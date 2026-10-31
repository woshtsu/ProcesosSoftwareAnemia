"""Graba el video demostrativo (~5 min) del sistema «Anemia Junín» v4.0.0-inc4 con datos SINTÉTICOS.

Qué hace, de principio a fin:
  1. Crea una base SQLite temporal y la llena con ``scripts/cargar_datos_prueba.py`` (27 niños sintéticos).
  2. Levanta la aplicación en el puerto 8770 con ``AUTH_MODE=supabase`` y un proveedor de identidad SIMULADO
     (el mismo montaje de ``tests/e2e/test_login.py``: nunca se contacta a Supabase ni se usan cuentas reales).
  3. Recorre la interfaz con Playwright (Chromium, 1280x720) grabando con ``record_video_dir``. Sobre cada paso
     inyecta un rótulo fijo con la sección (PMV, Incremento 1 a 4) y un cursor visible.
  4. Genera con Pillow la portada y las diapositivas finales (capturas reales de GitHub de ``semana-10`` y ``semana-11``).
  5. Une todo con ffmpeg en ``demo_anemia_junin_v4.mp4`` (H.264, 1280x720, sin audio).

Uso (desde cualquier carpeta; Chromium debe estar instalado, no se ejecuta ``playwright install``):

    PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python entregables/semana-12/video/grabar_demo.py

Al terminar borra la base, los temporales y detiene el servidor. No toca producción.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import date, timedelta
from pathlib import Path

import httpx
import uvicorn
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import expect, sync_playwright

AQUI = Path(__file__).resolve().parent
RAIZ_REPO = AQUI.parents[2]
APP = RAIZ_REPO / "pmv_fastapi"
SALIDA = AQUI / "demo_anemia_junin_v4.mp4"
PUERTO = 8770
URL = f"http://127.0.0.1:{PUERTO}"
GH10 = RAIZ_REPO / "entregables/semana-10/evidencias/github"
GH11 = RAIZ_REPO / "entregables/semana-11/evidencias/github"
FUENTES = Path("/usr/share/fonts/opentype/inter")
W, H = 1280, 720

COLORES = {"PMV": "#2563eb", "INC2": "#0d9488", "INC3": "#d97706", "INC4": "#9333ea", "AUTH": "#2563eb"}

# --------------------------------------------------------------------------------------------------------------
# Rótulo, cursor y resaltado inyectados en la página (sobreviven a recargas mediante sessionStorage)
# --------------------------------------------------------------------------------------------------------------
INIT_JS = r"""
(() => {
  const K = '__rotulo_demo', KC = '__cursor_demo';
  function css() {
    if (document.getElementById('demo-estilos')) return;
    const s = document.createElement('style'); s.id = 'demo-estilos';
    s.textContent = `
      #rotulo-demo{position:fixed;top:7px;left:196px;z-index:2147483647;display:flex;align-items:center;gap:10px;
        background:rgba(15,23,42,.88);color:#fff;font:600 20px/1.15 Inter,system-ui,sans-serif;padding:7px 14px 7px 8px;
        border-radius:10px;max-width:640px;pointer-events:none;box-shadow:0 2px 10px rgba(0,0,0,.35)}
      #rotulo-demo b{font-weight:800;padding:3px 10px;border-radius:7px;color:#fff;white-space:nowrap}
      #rotulo-demo span{white-space:nowrap}
      #cursor-demo{position:fixed;z-index:2147483646;width:26px;height:26px;pointer-events:none;display:none;
        filter:drop-shadow(1px 2px 2px rgba(0,0,0,.5))}
      .clic-demo{position:fixed;z-index:2147483645;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;
        border:3px solid #f59e0b;pointer-events:none;animation:clic-demo .55s ease-out forwards}
      @keyframes clic-demo{to{transform:scale(3.2);opacity:0}}
      .resaltado-demo{outline:4px solid #f59e0b !important;outline-offset:3px !important;border-radius:6px}`;
    document.documentElement.appendChild(s);
  }
  function pintar() {
    if (!document.documentElement) return;
    css();
    let d = document.getElementById('rotulo-demo');
    const r = JSON.parse(sessionStorage.getItem(K) || 'null');
    if (!r) { if (d) d.remove(); }
    else {
      if (!d) { d = document.createElement('div'); d.id = 'rotulo-demo'; document.documentElement.appendChild(d); }
      const h = `<b style="background:${r.color}">${r.etiqueta}</b><span>${r.texto}</span>`;
      if (d.dataset.h !== h) { d.innerHTML = h; d.dataset.h = h; }
    }
    let c = document.getElementById('cursor-demo');
    if (!c) {
      c = document.createElement('div'); c.id = 'cursor-demo';
      c.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M3 2l7 18 2.6-7.4L20 10z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>';
      document.documentElement.appendChild(c);
      const p = JSON.parse(sessionStorage.getItem(KC) || 'null');
      if (p) { c.style.left = p.x + 'px'; c.style.top = p.y + 'px'; c.style.display = 'block'; }
    }
  }
  window.__rotular = (etiqueta, texto, color) => { sessionStorage.setItem(K, JSON.stringify({etiqueta, texto, color})); pintar(); };
  window.__sinRotulo = () => { sessionStorage.removeItem(K); pintar(); };
  document.addEventListener('mousemove', (e) => {
    const c = document.getElementById('cursor-demo'); if (!c) return;
    c.style.display = 'block'; c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px';
    sessionStorage.setItem(KC, JSON.stringify({x: e.clientX, y: e.clientY}));
  }, true);
  document.addEventListener('mousedown', (e) => {
    const o = document.createElement('div'); o.className = 'clic-demo'; o.style.left = e.clientX + 'px'; o.style.top = e.clientY + 'px';
    document.documentElement.appendChild(o); setTimeout(() => o.remove(), 700);
  }, true);
  document.addEventListener('DOMContentLoaded', pintar);
  setInterval(pintar, 400);
})();
"""


# --------------------------------------------------------------------------------------------------------------
# Servidor local (base temporal sintética + Supabase simulado)
# --------------------------------------------------------------------------------------------------------------
class Servidor:
    def __init__(self, carpeta: Path):
        self.db = carpeta / "demo_s12.db"
        self.server = None
        self.hilo = None
        self.app = None

    def iniciar(self):
        entorno = {**os.environ, "DATABASE_URL": f"sqlite:///{self.db}", "AUTH_MODE": "demo"}
        entorno.pop("FECHA_REFERENCIA", None)
        subprocess.run(
            [sys.executable, "-m", "scripts.cargar_datos_prueba"],
            cwd=APP,
            env=entorno,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        sys.path.insert(0, str(APP))
        os.chdir(APP)
        os.environ["AUTH_COOKIE_SECURE"] = "false"
        from app.adapters.outbound.supabase_auth import SupabaseAuth
        from app.application.servicio_sesion import ServicioSesion
        from app.main import crear_app

        usuario = {"id": "usuario-prueba", "email": "enfermeria@example.test", "email_confirmed_at": "2026-10-23"}

        def responder(req):
            if req.url.path.endswith("/token"):
                if json.loads(req.content).get("password") != "correcta":
                    return httpx.Response(400)
                return httpx.Response(
                    200,
                    json={"access_token": "access-demo", "refresh_token": "refresh-demo", "expires_in": 3600, "user": usuario},
                )
            if req.url.path.endswith("/logout"):
                return httpx.Response(204)
            return httpx.Response(200, json=usuario)

        self.app = crear_app(f"sqlite:///{self.db}", auth_mode="supabase")
        self.app.state.auth_configurado = True
        self.app.state.sesiones = ServicioSesion(
            SupabaseAuth("https://example.test", "publica", transport=httpx.MockTransport(responder))
        )
        self.server = uvicorn.Server(uvicorn.Config(self.app, host="127.0.0.1", port=PUERTO, log_level="error"))
        self.hilo = threading.Thread(target=self.server.run, daemon=True)
        self.hilo.start()
        for _ in range(100):
            if self.server.started:
                break
            time.sleep(0.1)
        assert self.server.started, "el servidor no arrancó"
        salud = httpx.get(URL + "/api/salud").json()
        print("Salud:", salud)

    def detener(self):
        if self.server:
            self.server.should_exit = True
            self.hilo.join(timeout=10)
        if self.app is not None:
            self.app.state.repositorio.engine.dispose()


# --------------------------------------------------------------------------------------------------------------
# Piloto de la interfaz
# --------------------------------------------------------------------------------------------------------------
class Piloto:
    def __init__(self, ctx, pg):
        self.ctx, self.pg = ctx, pg
        self.pos = (640.0, 360.0)
        self.t0 = time.monotonic()  # instante de creación de la página = inicio del webm
        self.marcas: list[tuple[str, float]] = []

    # tiempo
    def ahora(self) -> float:
        return time.monotonic() - self.t0

    def marca(self, nombre: str):
        self.marcas.append((nombre, self.ahora()))
        pass

    def pausa(self, s: float):
        time.sleep(s)

    # rótulo
    def rotulo(self, clave: str, etiqueta: str, texto: str):
        self.marcas.append(("· " + texto, self.ahora()))
        self.pg.evaluate("([e, t, c]) => window.__rotular(e, t, c)", [etiqueta, texto, COLORES[clave]])
        derecha = self.pg.evaluate("document.getElementById('rotulo-demo').getBoundingClientRect().right")
        if derecha > 830:
            print(f"AVISO: rótulo demasiado ancho ({derecha:.0f}px): {texto}")

    # cursor y resaltado
    def mover(self, x: float, y: float, pasos: int = 22):
        x0, y0 = self.pos
        for i in range(1, pasos + 1):
            k = i / pasos
            k = k * k * (3 - 2 * k)  # suavizado
            self.pg.mouse.move(x0 + (x - x0) * k, y0 + (y - y0) * k)
            time.sleep(0.018)
        self.pos = (x, y)

    def _centro(self, loc):
        try:
            caja = None
            for _ in range(5):
                loc.scroll_into_view_if_needed(timeout=8000)
                time.sleep(0.15)
                caja = loc.bounding_box(timeout=8000)
                if caja:
                    break
                time.sleep(0.3)
        except Exception:
            if os.getenv("DEPURAR"):
                self.pg.screenshot(path=os.getenv("DEPURAR"))
            raise
        return caja["x"] + caja["width"] / 2, caja["y"] + caja["height"] / 2

    def resaltar(self, loc, on: bool = True):
        try:
            loc.evaluate("(e, on) => e.classList.toggle('resaltado-demo', on)", on, timeout=1200)
        except Exception:
            pass

    def clic(self, loc, espera: float = 0.55):
        x, y = self._centro(loc)
        self.mover(x, y)
        self.resaltar(loc)
        time.sleep(espera)
        loc.click()
        time.sleep(0.15)
        self.resaltar(loc, False)

    def escribir(self, loc, texto: str, retardo: int = 28):
        x, y = self._centro(loc)
        self.mover(x, y, 14)
        self.resaltar(loc)
        loc.click()
        loc.fill("")
        loc.press_sequentially(texto, delay=retardo)
        self.resaltar(loc, False)

    def rapido(self, loc, texto: str):
        """Cursor breve y relleno directo (para formularios ya mostrados antes)."""
        x, y = self._centro(loc)
        self.mover(x, y, 7)
        loc.fill(texto)

    def fecha(self, loc, iso: str):
        x, y = self._centro(loc)
        self.mover(x, y, 14)
        self.resaltar(loc)
        loc.fill(iso)
        time.sleep(0.2)
        self.resaltar(loc, False)

    def elegir(self, loc, valor: str):
        x, y = self._centro(loc)
        self.mover(x, y, 14)
        self.resaltar(loc)
        time.sleep(0.5)
        loc.select_option(valor)
        time.sleep(0.3)
        self.resaltar(loc, False)

    def mostrar(self, loc, segundos: float):
        """Resalta un elemento (sin clic) para que se lea."""
        x, y = self._centro(loc)
        self.mover(x, y, 16)
        self.resaltar(loc)
        time.sleep(segundos)
        self.resaltar(loc, False)

    def t(self, id_):
        return self.pg.get_by_test_id(id_)

    def pendientes(self, n: int):
        expect(self.t("indicador-sync")).to_have_attribute("data-pendientes", str(n), timeout=20000)


def abrir_controlada(pg):
    """Espera a que el service worker controle la página (así sus lecturas quedan en caché para el modo sin red)."""
    pg.evaluate("navigator.serviceWorker.ready.then(() => true)")
    pg.reload()
    pg.wait_for_function("navigator.serviceWorker.controller !== null")
    expect(pg.get_by_test_id("tab-registro")).to_be_visible()


def llenar_registro(p: Piloto, dni, nombres, apellidos, tutor, hb, peso, talla, nacimiento="2025-09-10", fecha_control=None, rapido=False):
    pg = p.pg
    if rapido:
        campos = [("#fecha", fecha_control), ("#dni", dni), ("#nombres", nombres), ("#apellidos", apellidos),
                  ("#fecha_nacimiento", nacimiento), ("#comunidad", "Palmayoc"), ("#altitud_m", "3720"),
                  ("#tutor_nombre", tutor), ("#hemoglobina_observada", hb), ("#peso_kg", peso), ("#talla_cm", talla)]
        for sel, valor in campos:
            if valor:
                p.rapido(pg.locator(sel), valor)
        pg.locator("#sexo").select_option("F")
        return
    if fecha_control:
        p.fecha(pg.locator("#fecha"), fecha_control)
    p.escribir(pg.locator("#dni"), dni)
    p.escribir(pg.locator("#nombres"), nombres)
    p.escribir(pg.locator("#apellidos"), apellidos)
    p.elegir(pg.locator("#sexo"), "F")
    p.fecha(pg.locator("#fecha_nacimiento"), nacimiento)
    p.escribir(pg.locator("#comunidad"), "Palmayoc")
    p.fecha(pg.locator("#altitud_m"), "3720")
    p.escribir(pg.locator("#tutor_nombre"), tutor)
    p.escribir(pg.locator("#hemoglobina_observada"), hb)
    p.escribir(pg.locator("#peso_kg"), peso)
    p.escribir(pg.locator("#talla_cm"), talla)


def abrir_expediente_por_dni(p: Piloto, dni: str):
    pg = p.pg
    p.clic(p.t("tab-seguimiento"))
    p.elegir(pg.locator("#filtro-clasificacion"), "")
    p.escribir(p.t("buscar"), dni, 40)
    pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length === 1")
    time.sleep(0.8)
    p.clic(pg.locator("#cuerpo-seguimiento tr").first)
    p.t("tabla-evaluaciones").wait_for()


# --------------------------------------------------------------------------------------------------------------
# Guion de la grabación
# --------------------------------------------------------------------------------------------------------------
def grabar(dir_video: Path, srv: Servidor) -> tuple[Path, float, list[tuple[str, float]]]:
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(
            viewport={"width": W, "height": H},
            locale="es-PE",
            timezone_id="America/Lima",
            record_video_dir=str(dir_video),
            record_video_size={"width": W, "height": H},
        )
        ctx.add_init_script(INIT_JS)
        pg = ctx.new_page()
        p = Piloto(ctx, pg)
        pg.goto(URL)
        expect(pg.locator("#login-enviar")).to_be_enabled()

        # ---------------- PMV · Incremento 1 ----------------
        p.rotulo("PMV", "PMV · Incremento 1", "AUTH Inicio de sesión")
        time.sleep(1.2)
        inicio = p.ahora()
        p.marca("pmv")
        time.sleep(2.0)
        p.escribir(pg.locator("#login-email"), "enfermeria@example.test", 40)
        p.escribir(pg.locator("#login-password"), "correcta", 60)
        time.sleep(0.5)
        p.clic(pg.locator("#login-enviar"))
        expect(pg.locator("#aplicacion")).to_be_visible()
        time.sleep(1.5)
        abrir_controlada(pg)
        time.sleep(1.5)

        p.rotulo("PMV", "PMV · Incremento 1", "RF-03 Validación de datos inválidos")
        time.sleep(1.2)
        p.escribir(pg.locator("#dni"), "123")
        p.escribir(pg.locator("#hemoglobina_observada"), "25")
        p.clic(p.t("guardar"))
        pg.wait_for_selector(".campo.invalido")
        time.sleep(2.5)
        p.clic(pg.get_by_role("button", name="Limpiar"))
        time.sleep(0.8)
        p.rotulo("PMV", "PMV · Incremento 1", "RF-01 Registro nominal del niño")
        time.sleep(1.0)
        llenar_registro(p, "72000001", "Lucía", "Quispe Rojas", "Elena Quispe Rojas", "11.6", "8.4", "71")
        p.rotulo("PMV", "PMV · Incremento 1", "RF-03 Hb ajustada y clasificación")
        previa = p.t("clasificacion-previa")
        previa.wait_for()
        p.mostrar(previa, 3.5)
        p.rotulo("PMV", "PMV · Incremento 1", "RF-01 Guardar el registro")
        p.clic(p.t("guardar"))
        p.t("tabla-evaluaciones").wait_for()
        p.rotulo("PMV", "PMV · Incremento 1", "RF-02 Expediente digital del niño")
        time.sleep(3.0)
        p.mostrar(p.t("tabla-evaluaciones"), 2.5)

        p.rotulo("PMV", "PMV · Incremento 1", "RF-04 Seguimiento de niños y filtros")
        p.clic(p.t("tab-seguimiento"))
        pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length > 5")
        time.sleep(2.2)
        p.elegir(pg.locator("#filtro-clasificacion"), "MODERADA")
        time.sleep(2.5)

        p.rotulo("PMV", "PMV · Incremento 1", "RF-05 Reporte del período")
        p.clic(p.t("tab-reporte"))
        time.sleep(1.0)
        p.clic(p.t("generar-reporte"))
        p.t("kpi-registrados").wait_for()
        time.sleep(3.0)

        # ---------------- Incremento 2 ----------------
        p.marca("inc2")
        p.rotulo("INC2", "Incremento 2", "RF-06 Agenda normativa de controles")
        time.sleep(0.5)
        abrir_expediente_por_dni(p, "71000022")
        agenda = p.t("agenda-tabla")
        agenda.wait_for()
        time.sleep(1.0)
        p.mostrar(p.t("agenda-resumen"), 2.0)
        p.mostrar(agenda.locator("tr[data-codigo='C3M']").first, 3.0)

        p.rotulo("INC2", "Incremento 2", "RF-07 Alertas de controles vencidos")
        p.clic(p.t("tab-alertas"))
        pg.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 3")
        time.sleep(2.5)
        p.elegir(p.t("filtro-alerta-prioridad"), "ALTA")
        time.sleep(3.0)

        p.rotulo("INC2", "Incremento 2", "RF-08 Agenda del personal por rango")
        p.clic(p.t("tab-agenda"))
        p.t("agenda-personal-tabla").wait_for()
        time.sleep(2.5)
        hoy = date.fromisoformat(httpx.get(URL + "/api/salud").json()["fecha_hoy"])
        p.fecha(p.t("agenda-desde"), (hoy - timedelta(days=30)).isoformat())
        p.fecha(p.t("agenda-hasta"), hoy.isoformat())
        p.clic(p.t("agenda-consultar"))
        pg.wait_for_function(
            "() => document.querySelector('[data-testid=agenda-personal-resumen]')?.textContent.includes('fecha de referencia')"
        )
        time.sleep(3.5)
        # vuelve a la semana actual para registrar la asistencia sobre controles pendientes
        lunes = hoy - timedelta(days=hoy.weekday())
        p.fecha(p.t("agenda-desde"), lunes.isoformat())
        p.fecha(p.t("agenda-hasta"), (lunes + timedelta(days=6)).isoformat())
        p.clic(p.t("agenda-consultar"))
        time.sleep(1.8)

        p.rotulo("INC2", "Incremento 2", "RF-09 Registro de asistencia a un control")
        time.sleep(0.8)
        p.clic(pg.locator("#cuerpo-agenda-personal [data-testid=btn-asistio]").first)
        pg.locator("#asistencia-confirmar").wait_for()
        time.sleep(1.8)
        p.clic(pg.locator("#asistencia-confirmar"))
        expect(p.t("modal-asistencia")).to_be_hidden()
        time.sleep(2.0)
        p.rotulo("INC2", "Incremento 2", "RF-09 Registro de inasistencia y motivo")
        p.clic(pg.locator("#cuerpo-agenda-personal [data-testid=btn-no-asistio]").first)
        p.elegir(p.t("asistencia-motivo"), "Olvido de la cita")
        time.sleep(1.0)
        p.clic(p.t("asistencia-confirmar"))
        expect(p.t("modal-asistencia")).to_be_hidden()
        time.sleep(2.8)

        # ---------------- Incremento 3 ----------------
        p.marca("inc3")
        p.rotulo("INC3", "Incremento 3", "HIST-3.1 Registro sin conexión: se corta la red")
        p.clic(p.t("tab-registro"))
        time.sleep(0.8)
        p.clic(pg.get_by_role("button", name="Limpiar"))
        time.sleep(1.2)
        ctx.set_offline(True)
        expect(pg.locator("#red.fuera")).to_have_count(1)
        p.mostrar(pg.locator("#red"), 2.5)
        llenar_registro(
            p, "72300001", "Mía Alejandra", "Huamán Zevallos", "Elena Zevallos Rojas", "9.4", "8.4", "71",
            fecha_control=(hoy - timedelta(days=20)).isoformat(), rapido=True,
        )
        p.clic(p.t("guardar"))
        expect(p.t("expediente-pendiente")).to_be_visible()
        p.pendientes(1)
        time.sleep(2.0)
        p.rotulo("INC3", "Incremento 3", "HIST-3.1 Nuevo control, también sin conexión")
        p.rapido(pg.locator("#form-control input[name=hemoglobina_observada]"), "10.1")
        p.rapido(pg.locator("#form-control input[name=peso_kg]"), "8.6")
        p.rapido(pg.locator("#form-control input[name=talla_cm]"), "72")
        p.clic(p.t("guardar-control"))
        p.pendientes(2)
        p.rotulo("INC3", "Incremento 3", "HIST-3.4 Indicador «2 pendientes»")
        p.mostrar(p.t("indicador-sync"), 2.5)
        p.clic(p.t("tab-sincronizacion"))
        expect(p.t("pendiente")).to_have_count(2)
        time.sleep(3.0)

        p.rotulo("INC3", "Incremento 3", "HIST-3.2 Se reconecta la red: sincroniza")
        time.sleep(1.0)
        ctx.set_offline(False)
        p.pendientes(0)
        expect(p.t("indicador-sync")).to_have_text("Al día")
        p.mostrar(p.t("indicador-sync"), 2.5)
        p.rotulo("INC3", "Incremento 3", "HIST-3.2 Sin duplicados: un solo niño")
        p.clic(p.t("tab-seguimiento"))
        p.elegir(pg.locator("#filtro-clasificacion"), "")
        p.escribir(p.t("buscar"), "72300001", 40)
        expect(pg.locator("#cuerpo-seguimiento tr")).to_have_count(1)
        p.mostrar(pg.locator("#cuerpo-seguimiento tr").first, 3.0)

        # Prepara (sin mostrarlo) un niño ya existente con evaluación de hoy: el control sin conexión chocará con él.
        cuerpo = {
            "nino": {
                "dni": "72300003", "nombres": "Ana Lucía", "apellidos": "Ccora Ñaupa", "sexo": "F",
                "fecha_nacimiento": "2025-09-10", "establecimiento": "P. S. Chongos Alto", "distrito": "Chongos Alto",
                "comunidad": "Palmayoc", "altitud_m": 3720, "tutor_nombre": "Rosa Ñaupa", "tutor_celular": None,
            },
            "evaluacion_inicial": {"fecha": hoy.isoformat(), "hemoglobina_observada": 9.8, "peso_kg": 8.4, "talla_cm": 71},
        }
        r = ctx.request.post(URL + "/api/ninos", data=cuerpo, headers={"X-CSRF-Protection": "1"})
        assert r.status == 201, r.text()
        p.rotulo("INC3", "Incremento 3", "HIST-3.3 Conflicto con el servidor")
        abrir_expediente_por_dni(p, "72300003")
        pg.locator("#form-control input[name=hemoglobina_observada]").wait_for()
        time.sleep(1.0)
        ctx.set_offline(True)
        expect(pg.locator("#red.fuera")).to_have_count(1)
        p.rapido(pg.locator("#form-control input[name=hemoglobina_observada]"), "11.2")
        p.rapido(pg.locator("#form-control input[name=peso_kg]"), "8.4")
        p.rapido(pg.locator("#form-control input[name=talla_cm]"), "71")
        p.clic(p.t("guardar-control"))
        p.pendientes(1)
        time.sleep(1.5)
        ctx.set_offline(False)
        p.pendientes(0)
        p.clic(p.t("tab-sincronizacion"))
        conflicto = p.t("conflicto")
        expect(conflicto).to_have_count(1)
        p.rotulo("INC3", "Incremento 3", "HIST-3.3 Resolución del conflicto")
        p.mostrar(conflicto, 3.5)
        p.clic(p.t("conflicto-conservar"))
        expect(p.t("sin-conflictos")).to_be_visible()
        expect(p.t("indicador-sync")).to_have_text("Al día")
        time.sleep(2.5)

        p.rotulo("INC3", "Incremento 3", "VIS-3.5 Visitas domiciliarias priorizadas")
        p.clic(p.t("tab-visitas"))
        filas = p.t("visita-priorizada")
        expect(filas.first).to_be_visible()
        time.sleep(2.5)
        p.clic(filas.first.get_by_test_id("puntaje"))
        expect(p.t("desglose").first).to_be_visible()
        p.rotulo("INC3", "Incremento 3", "VIS-3.5 Puntaje con su desglose")
        time.sleep(3.5)
        p.clic(filas.first.get_by_test_id("btn-visitar"))
        p.elegir(p.t("visita-resultado"), "REALIZADA")
        p.elegir(p.t("visita-suplemento"), "SI")
        p.escribir(p.t("visita-observaciones"), "Familia receptiva", 40)
        time.sleep(1.0)
        p.clic(p.t("visita-confirmar"))
        expect(p.t("modal-visita")).to_be_hidden()
        time.sleep(2.5)

        # ---------------- Incremento 4 ----------------
        p.marca("inc4")
        p.rotulo("INC4", "Incremento 4", "HIST-4.1 Recordatorios SIMULADOS")
        p.clic(p.t("tab-recordatorios"))
        time.sleep(1.2)
        p.clic(p.t("recordatorios-generar"))
        expect(p.t("recordatorios-resultado")).to_contain_text("Modo simulado")
        expect(p.t("marca-simulado").first).to_be_visible()
        p.mostrar(p.t("recordatorios-resultado"), 2.5)
        p.mostrar(p.t("marca-simulado").first, 3.0)
        p.rotulo("INC4", "Incremento 4", "HIST-4.1 Métricas de los recordatorios")
        p.mostrar(p.t("recordatorios-metricas"), 3.0)

        p.rotulo("INC4", "Incremento 4", "HIST-4.2 Respuesta del tutor: «No puede»")
        fila = pg.locator("[data-testid=recordatorio]:has([data-testid=btn-responder])").first
        nino_id = fila.locator(".enlace-nino").get_attribute("data-nino")
        p.clic(fila.get_by_test_id("btn-responder"))
        p.elegir(p.t("respuesta-opcion"), "NO_PUEDE")
        p.rotulo("INC4", "Incremento 4", "HIST-4.3 Registro de la barrera de acceso")
        p.elegir(p.t("respuesta-barrera"), "RECHAZO_TRATAMIENTO")
        time.sleep(1.5)
        p.clic(p.t("respuesta-confirmar"))
        expect(p.t("modal-respuesta")).to_be_hidden()
        time.sleep(1.0)
        p.mostrar(pg.locator("[data-testid=recordatorio]", has_text="No puede asistir").first, 3.0)

        p.rotulo("INC4", "Incremento 4", "HIST-4.3 Barrera desde el expediente")
        p.clic(pg.locator(f"[data-testid=recordatorio] .enlace-nino[data-nino='{nino_id}']").first)
        p.t("btn-barrera-nino").wait_for()
        time.sleep(1.5)
        p.clic(p.t("btn-barrera-nino"))
        p.elegir(p.t("barrera-tipo"), "TRANSPORTE")
        time.sleep(1.0)
        p.clic(p.t("barrera-confirmar"))
        expect(p.t("modal-barrera")).to_be_hidden()
        expect(p.t("barrera-fila").first).to_be_visible()
        time.sleep(1.0)
        p.mostrar(p.t("barreras-nino-tabla"), 3.0)

        p.rotulo("INC4", "Incremento 4", "HIST-4.4 Alerta de barrera crítica")
        p.clic(p.t("tab-alertas"))
        alerta = p.t("alerta-barrera").first
        expect(alerta).to_be_visible()
        time.sleep(1.5)
        p.mostrar(alerta, 3.5)
        p.marca("fin")
        time.sleep(0.5)

        ruta = pg.video.path()
        ctx.close()
        nav.close()
        p.marcas.append(("cierre", p.ahora()))
        return Path(ruta), inicio, p.marcas


# --------------------------------------------------------------------------------------------------------------
# Portada y diapositivas (Pillow)
# --------------------------------------------------------------------------------------------------------------
def fuente(peso: str, tam: int):
    return ImageFont.truetype(str(FUENTES / f"Inter-{peso}.otf"), tam)


def fondo() -> Image.Image:
    im = Image.new("RGB", (W, H), "#1e4d7b")
    d = ImageDraw.Draw(im)
    for y in range(H):  # degradado vertical
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(24 + 10 * k), int(61 - 22 * k), int(105 - 40 * k)))
    return im


def texto_centrado(d, y, txt, f, color="#ffffff"):
    ancho = d.textlength(txt, font=f)
    d.text(((W - ancho) / 2, y), txt, font=f, fill=color)


def portada(ruta: Path):
    im = fondo()
    d = ImageDraw.Draw(im)
    # gota con cruz (logotipo simplificado)
    cx, cy = W // 2, 150
    d.polygon([(cx, cy - 70), (cx - 46, cy + 10), (cx + 46, cy + 10)], fill="#e24b3b")
    d.ellipse([cx - 46, cy - 20, cx + 46, cy + 72], fill="#e24b3b")
    d.rectangle([cx - 5, cy + 4, cx + 5, cy + 52], fill="#ffffff")
    d.rectangle([cx - 24, cy + 23, cx + 24, cy + 33], fill="#ffffff")
    texto_centrado(d, 255, "Sistema de Detección Temprana", fuente("Bold", 54))
    texto_centrado(d, 322, "de Anemia Infantil — Junín", fuente("Bold", 54))
    texto_centrado(d, 410, "v4.0.0-inc4", fuente("SemiBold", 40), "#fbbf24")
    texto_centrado(d, 470, "Procesos de Software 2026-20", fuente("Medium", 32), "#dbeafe")
    # tira de secciones
    etiquetas = [("PMV · Inc. 1", COLORES["PMV"]), ("Incremento 2", COLORES["INC2"]), ("Incremento 3", COLORES["INC3"]), ("Incremento 4", COLORES["INC4"])]
    f = fuente("Bold", 24)
    ancho_total = sum(d.textlength(t, font=f) + 44 for t, _ in etiquetas) + 18 * (len(etiquetas) - 1)
    x = (W - ancho_total) / 2
    for t, c in etiquetas:
        a = d.textlength(t, font=f) + 44
        d.rounded_rectangle([x, 580, x + a, 628], radius=12, fill=c)
        d.text((x + 22, 590), t, font=f, fill="#ffffff")
        x += a + 18
    texto_centrado(d, 662, "Demostración con datos sintéticos · ejecución local", fuente("Regular", 20), "#bfdbfe")
    im.save(ruta)


def diapositiva(ruta: Path, titulo: str, subtitulo: str, imagen: Path | None, pie: str, escala: float = 0.9):
    im = Image.new("RGB", (W, H), "#0f172a")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 78], fill="#1e4d7b")
    d.text((36, 12), titulo, font=fuente("Bold", 34), fill="#ffffff")
    d.text((38, 52), subtitulo, font=fuente("Regular", 17), fill="#bfdbfe")
    if imagen:
        cap = Image.open(imagen).convert("RGB")
        alto_max = H - 78 - 80
        k = min(alto_max / cap.height, (W - 60) / cap.width) * (escala / 0.9)
        k = min(k, alto_max / cap.height)
        cap = cap.resize((int(cap.width * k), int(cap.height * k)), Image.LANCZOS)
        x = (W - cap.width) // 2
        y = 78 + 12
        d.rectangle([x - 3, y - 3, x + cap.width + 3, y + cap.height + 3], fill="#38bdf8")
        im.paste(cap, (x, y))
    d.rectangle([0, H - 62, W, H], fill="#1e293b")
    d.text((36, H - 49), pie, font=fuente("SemiBold", 24), fill="#fde68a")
    im.save(ruta)


def cierre(ruta: Path):
    im = fondo()
    d = ImageDraw.Draw(im)
    texto_centrado(d, 50, "Resumen de la demostración", fuente("Bold", 46))
    filas = [
        ("PMV · Incremento 1", "Registro nominal, expediente, clasificación, seguimiento y reporte", COLORES["PMV"]),
        ("Incremento 2", "Agenda normativa, alertas de vencidos, agenda del personal y asistencia", COLORES["INC2"]),
        ("Incremento 3", "Trabajo sin conexión, sincronización idempotente, conflictos y visitas", COLORES["INC3"]),
        ("Incremento 4", "Recordatorios simulados, respuesta del tutor, barreras y alerta crítica", COLORES["INC4"]),
    ]
    y = 140
    for t, s, c in filas:
        d.rounded_rectangle([90, y, 1190, y + 84], radius=14, fill="#0f172a")
        d.rounded_rectangle([90, y, 104, y + 84], radius=6, fill=c)
        d.text((130, y + 10), t, font=fuente("Bold", 28), fill="#ffffff")
        d.text((130, y + 48), s, font=fuente("Regular", 22), fill="#cbd5e1")
        y += 100
    texto_centrado(d, 556, "Limitaciones declaradas: envío real de mensajes no probado · proveedor de identidad simulado", fuente("Regular", 21), "#fde68a")
    texto_centrado(d, 590, "rendimiento p95 ≈ 1,1 s a vigilar · hallazgos OWASP abiertos", fuente("Regular", 21), "#fde68a")
    texto_centrado(d, 650, "Gracias · Procesos de Software 2026-20 · v4.0.0-inc4", fuente("SemiBold", 26), "#dbeafe")
    im.save(ruta)


def generar_slides(carpeta: Path) -> list[tuple[Path, float]]:
    s = []
    p0 = carpeta / "00_portada.png"
    portada(p0)
    s.append((p0, 15.0))
    p1 = carpeta / "90_hexagonal.png"
    diapositiva(p1, "Calidad y arquitectura · estructura hexagonal", "Repositorio · etiqueta v4.0-Inc4 · pmv_fastapi/app", GH10 / "GH_arbol_app.png",
                "domain · ports · application · adapters · web — dependencias hacia el dominio")
    s.append((p1, 7.0))
    p2 = carpeta / "91_arquitectura_pruebas.png"
    diapositiva(p2, "Calidad y arquitectura · pruebas de dependencias", "pmv_fastapi/tests/arquitectura/test_dependencias.py", GH10 / "GH_pruebas_arquitectura.png",
                "El dominio no importa frameworks ni adaptadores: lo verifica una prueba automática")
    s.append((p2, 5.0))
    p3 = carpeta / "92_actions.png"
    diapositiva(p3, "Calidad y arquitectura · integración continua", "GitHub Actions · CI y producción — PMV Anemia Junín", GH10 / "GH_actions_ejecucion_verde.png",
                "Ejecución en verde: calidad-y-pruebas e imagen aprobadas en cada push")
    s.append((p3, 7.0))
    p4 = carpeta / "93_etiquetas.png"
    diapositiva(p4, "Calidad y arquitectura · etiquetas por incremento", "GitHub · Tags", GH10 / "GH_etiquetas.png",
                "v1.0-PMV · v1.5.0-inc2-avance · v2.0-Inc2 · v3.0-Inc3 · v4.0-Inc4")
    s.append((p4, 5.0))
    p5 = carpeta / "94_cierre.png"
    cierre(p5)
    s.append((p5, 8.0))
    return s


# --------------------------------------------------------------------------------------------------------------
# Montaje con ffmpeg
# --------------------------------------------------------------------------------------------------------------
def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


COMUN = ["-an", "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30", "-vf", f"scale={W}:{H},setsar=1"]


def montar(tmp: Path, webm: Path, inicio: float, fin: float, slides: list[tuple[Path, float]], desfase: float):
    partes: list[Path] = []
    portada_p, dur = slides[0]
    pt = tmp / "p_portada.mp4"
    ff("-loop", 1, "-t", dur, "-i", portada_p, *COMUN, "-crf", 22, pt)
    partes.append(pt)
    pv = tmp / "p_software.mp4"
    ff("-ss", f"{inicio + desfase:.2f}", "-i", webm, "-t", f"{fin - inicio:.2f}", *COMUN, "-crf", 26, pv)
    partes.append(pv)
    for i, (img, dur) in enumerate(slides[1:]):
        ps = tmp / f"p_slide{i}.mp4"
        ff("-loop", 1, "-t", dur, "-i", img, *COMUN, "-crf", 22, ps)
        partes.append(ps)
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes), encoding="utf-8")
    ff("-f", "concat", "-safe", 0, "-i", lista, "-c", "copy", "-movflags", "+faststart", SALIDA)


def duracion(ruta: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def main():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    desfase = float(os.getenv("DESFASE_VIDEO", "0.0"))  # ajuste fino entre el reloj del guion y el webm
    tmp = Path(tempfile.mkdtemp(prefix="demo_anemia_"))
    srv = Servidor(tmp)
    try:
        srv.iniciar()
        slides = generar_slides(tmp)
        print("Grabando…")
        webm, inicio, marcas = grabar(tmp / "video", srv)
        marcas_d = dict(marcas)
        # El webm de Playwright dura algo más que el reloj del guion (≈ 7 %): se escala cada marca por D / t_cierre.
        k = duracion(webm) / marcas_d["cierre"]
        print(f"Factor webm/reloj: {k:.3f} (webm {duracion(webm):.1f} s, reloj {marcas_d['cierre']:.1f} s)")
        marcas = [(n, t * k) for n, t in marcas]
        marcas_d = dict(marcas)
        inicio *= k
        fin = marcas_d["fin"] + 0.5 * k
        if os.getenv("PERFIL"):
            for n, t in marcas:
                print(f"PERFIL {t:7.1f} {n}")
        print("Montando…")
        montar(tmp, webm, inicio, fin, slides, desfase)
        total = duracion(SALIDA)
        t_portada = slides[0][1]
        print(f"\nVideo: {SALIDA} ({SALIDA.stat().st_size / 1e6:.1f} MB, {total:.1f} s)")
        orden = [("PMV · Incremento 1", "pmv", "inc2"), ("Incremento 2", "inc2", "inc3"), ("Incremento 3", "inc3", "inc4"), ("Incremento 4", "inc4", "fin")]
        print(f"  Portada: 0.0 – {t_portada:.1f} s")
        for nombre, a, b in orden:
            ini = t_portada + (marcas_d[a] - inicio)
            fn = t_portada + ((marcas_d[b] + 0.5 * k) if b == "fin" else marcas_d[b]) - inicio
            print(f"  {nombre}: {ini:.1f} – {fn:.1f} s ({fn - ini:.1f} s)")
        t_sw = t_portada + fin - inicio
        print(f"  Calidad y arquitectura + cierre: {t_sw:.1f} – {total:.1f} s ({total - t_sw:.1f} s)")
        if os.getenv("CONSERVAR_WEBM"):
            shutil.copy(webm, AQUI / "demo_anemia_junin_v4_software.webm")
    finally:
        srv.detener()
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
