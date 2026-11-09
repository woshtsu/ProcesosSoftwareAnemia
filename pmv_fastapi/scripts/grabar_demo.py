"""Graba la demo del PMV contra PRODUCCIÓN capturando el escritorio completo con ffmpeg (gdigrab).

Qué hace:
  1. Abre Microsoft Edge visible y maximizado (perfil temporal, sin el aviso «controlado por software
     automatizado») en la URL indicada.
  2. Espera, sin límite de tiempo, a que el usuario inicie sesión a mano. El script nunca ve la contraseña.
  3. Realiza un calentamiento previo de los endpoints clave de la API en Render antes de iniciar la grabación
     para evitar que el arranque en frío aparezca en el video.
  4. Lanza ffmpeg (``gdigrab -i desktop``: barra de tareas, navegador, fecha y hora visibles), consulta la
     fecha de referencia fijada en el servidor (/api/salud), recorre el guion con datos sintéticos marcados
     «DEMO», verifica paso a paso cada respuesta HTTP y detiene ffmpeg.
  5. Genera el SQL de limpieza de los datos DEMO en un archivo temporal para ejecutarlo en el editor SQL de Supabase.

Uso (desde pmv_fastapi/, con el entorno virtual activado):
    python -m scripts.grabar_demo --prueba 10          # prueba corta: 10 s de escritorio, sin crear datos
    python -m scripts.grabar_demo --ensayo             # recorrido completo sin ffmpeg para validar contra producción
    python -m scripts.grabar_demo                      # recorrido completo con grabación (~5 min)

Opciones: --url, --salida (mp4), --ffmpeg (ruta), --prueba, --ensayo, --solo-limpiar.
Antes de generar recordatorios se verifica contra /api/recordatorios/metricas que el modo sea SIMULADO.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
import time
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

URL_PROD = "https://softwareanemia-virginia.onrender.com"
RAIZ = Path(__file__).resolve().parents[2]
SALIDA_POR_DEFECTO = RAIZ / "entregables" / "semana-12" / "video" / "demo_anemia_junin_v4.mp4"

# DNI sintéticos del rango 7999xxxx; nombres con prefijo DEMO para reconocerlos y borrarlos.
# Cada ejecución usa DNI distintos (7999 + 4 dígitos) para encadenar ensayos sin limpiar entre ellos;
# el SQL de limpieza borra todos los 7999xxxx con nombre «DEMO …».
_BASE_DNI = (int(time.time()) // 60 % 2400) * 4 + 100
NINOS_DEMO = {
    "inc1": (f"7999{_BASE_DNI:04d}", "DEMO Lucía", "Prueba Quispe"),
    "offline": (f"7999{_BASE_DNI + 1:04d}", "DEMO Mía", "Prueba Huamán"),
    "rec": (f"7999{_BASE_DNI + 2:04d}", "DEMO Gael", "Prueba Flores"),
    "vencido": (f"7999{_BASE_DNI + 3:04d}", "DEMO Samanta", "Prueba Rojas"),
}
DNI_INVALIDO = "123"
COMUNIDAD_DEMO = "DEMO Comunidad"

ROTULO_JS = """(t) => {
  let d = document.getElementById('rotulo-demo');
  const pestanas = document.querySelector('[data-testid="tab-registro"]')?.closest('.pestanas')
    || document.querySelector('.pestanas')
    || document.querySelector('[data-testid="tab-registro"]')?.parentElement;

  if (pestanas) {
    if (!d || d.parentElement !== pestanas.parentElement || d.previousElementSibling !== pestanas) {
      if (d) d.remove();
      d = document.createElement('div');
      d.id = 'rotulo-demo';
      d.style.cssText = 'background:#1F4E79;color:#fff;font:700 18px Segoe UI,sans-serif;' +
        'padding:8px 18px;text-align:center;box-shadow:0 3px 10px rgba(0,0,0,.3);width:100%;box-sizing:border-box;';
      pestanas.insertAdjacentElement('afterend', d);
    }
  } else {
    if (!d) {
      d = document.createElement('div');
      d.id = 'rotulo-demo';
      d.style.cssText = 'position:fixed;left:0;right:0;top:0;z-index:2147483646;background:#1F4E79;color:#fff;' +
        'font:700 18px Segoe UI,sans-serif;padding:8px 18px;text-align:center;box-shadow:0 3px 10px rgba(0,0,0,.3);';
      document.body.appendChild(d);
    }
  }
  d.textContent = t;
}"""

LEYENDA_JS = """(t) => {
  let d = document.getElementById('leyenda-demo');
  if (!d) { d = document.createElement('div'); d.id = 'leyenda-demo';
    d.style.cssText = 'position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:2147483646;' +
      'background:rgba(20,45,75,.94);color:#fff;padding:10px 22px;border-radius:12px;font:600 17px Segoe UI,sans-serif;' +
      'box-shadow:0 6px 20px rgba(0,0,0,.25);max-width:88%;text-align:center';
    document.body.appendChild(d); }
  d.innerHTML = t;
}"""

PORTADA = """<html><head><title>Anemia Junín · v4.0-Inc4</title></head>
<body style="margin:0;height:100vh;display:flex;align-items:center;justify-content:center;
background:linear-gradient(135deg,#1F4E79,#2E5C8A);font-family:Segoe UI,sans-serif;color:#fff;text-align:center">
<div><div style="font-size:22px;opacity:.85">Procesos de Software 2026-20 · Demostración en producción</div>
<h1 style="font-size:46px;margin:16px 0 10px">Anemia Junín · v4.0-Inc4</h1>
<div style="font-size:24px">{texto}</div>
<div style="margin-top:26px;font-size:18px;opacity:.9">Datos sintéticos marcados «DEMO»; se eliminan al terminar.</div>
</div></body></html>"""


# ---------------------------------------------------------------------------------------------------------
# ffmpeg
# ---------------------------------------------------------------------------------------------------------
def localizar_ffmpeg(explicita: str | None) -> str:
    if explicita:
        return explicita
    encontrada = shutil.which("ffmpeg")
    if encontrada:
        return encontrada
    paquetes = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    for exe in paquetes.glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"):
        return str(exe)
    raise SystemExit("No se encontró ffmpeg. Instálalo con: winget install --id Gyan.FFmpeg -e")


class Grabadora:
    """Graba el escritorio completo; se detiene enviando «q» para que el MP4 quede bien cerrado."""

    def __init__(self, ffmpeg: str, salida: Path):
        self.ffmpeg, self.salida, self.proc = ffmpeg, salida, None

    def iniciar(self) -> None:
        self.salida.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            self.ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "gdigrab",
            "-framerate",
            "30",
            "-draw_mouse",
            "1",
            "-i",
            "desktop",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-movflags",
            "+faststart",
            str(self.salida),
        ]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)  # noqa: S603 - comando fijo
        time.sleep(1.5)
        if self.proc.poll() is not None:
            raise SystemExit("ffmpeg terminó al arrancar; revisa el mensaje anterior.")
        print("[REC] Grabando escritorio →", self.salida)

    def detener(self) -> None:
        if not self.proc or self.proc.poll() is not None:
            return
        try:
            self.proc.stdin.write(b"q")
            self.proc.stdin.flush()
            self.proc.wait(timeout=30)
        except Exception:
            self.proc.kill()
        print("[STOP] Grabación detenida")


# ---------------------------------------------------------------------------------------------------------
# Navegador
# ---------------------------------------------------------------------------------------------------------
def abrir_edge(p, perfil: Path):
    ctx = p.chromium.launch_persistent_context(
        str(perfil),
        channel="msedge",
        headless=False,
        no_viewport=True,
        args=[
            "--start-maximized",
            "--lang=es-PE",
            "--no-first-run",
            "--no-default-browser-check",
            # Se añade Translate a disable-features para eliminar el popup de traducción de Edge en GitHub.
            "--disable-features=msEdgeSidebarV2,msShowCopilotButton,Translate",
        ],
        ignore_default_args=[
            "--enable-automation",
            "--no-sandbox",
        ],  # quita la barra «controlado por software automatizado»
        locale="es-PE",
        timezone_id="America/Lima",
    )
    # Oculta el correo del usuario autenticado en la cabecera: no debe verse en el video.
    ctx.add_init_script(
        "document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style');"
        " s.textContent = '#usuario-autenticado{visibility:hidden !important}'; document.head.appendChild(s); });"
    )
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    return ctx, pg


def esperar_login(pg, url: str) -> None:
    pg.goto(url)
    print("Inicia sesión en la ventana de Edge; el script espera sin límite de tiempo…")
    pg.wait_for_selector("#aplicacion", state="visible", timeout=0)
    pg.wait_for_selector('[data-testid="tab-registro"]', state="visible", timeout=0)
    print("Sesión detectada.")
    time.sleep(1.5)


def obtener_fecha_referencia(pg, url: str) -> date:
    """Lee fecha_referencia de GET {url}/api/salud con la sesión del navegador. Falla si no viene fijada."""
    url_salud = f"{url.rstrip('/')}/api/salud"
    try:
        resp = pg.request.get(url_salud, timeout=90_000)
        if not resp.ok:
            raise RuntimeError(f"HTTP {resp.status}: {resp.text()}")
        datos = resp.json()
    except Exception as e:
        raise SystemExit(f"Error consultando {url_salud}: {e}") from e

    ref_str = datos.get("fecha_referencia")
    if not ref_str:
        raise SystemExit(
            f"El endpoint {url_salud} no devolvió 'fecha_referencia'. "
            f"Respuesta recibida: {datos}. Se requiere que el servidor tenga configurada FECHA_REFERENCIA."
        )
    try:
        return date.fromisoformat(ref_str)
    except Exception as e:
        raise SystemExit(f"Fecha de referencia inválida ('{ref_str}'): {e}") from e


def verificar_modo_simulado(pg, url: str) -> bool:
    """Comprueba en GET {url}/api/recordatorios/metricas que el modo sea SIMULADO."""
    url_metricas = f"{url.rstrip('/')}/api/recordatorios/metricas"
    try:
        resp = pg.request.get(url_metricas, timeout=90_000)
        if not resp.ok:
            raise RuntimeError(f"HTTP {resp.status}: {resp.text()}")
        m = resp.json()
    except Exception as e:
        raise SystemExit(f"Error consultando {url_metricas}: {e}") from e

    # Si hay canales reales con envíos o registros
    por_canal = m.get("por_canal", [])
    canales_reales = [c.get("canal") for c in por_canal if c.get("canal") != "SIMULADO" and c.get("total", 0) > 0]
    if canales_reales:
        return False

    enviados = m.get("enviados", 0)
    simulados = m.get("simulados", 0)
    if enviados > simulados:
        return False

    return True


# ---------------------------------------------------------------------------------------------------------
# Calentamiento de endpoints (evita cold start en el video)
# ---------------------------------------------------------------------------------------------------------
def calentar_servidor(pg, url: str, fecha_ref: date) -> None:
    """Realiza peticiones GET a /api/salud y rutas de pestañas hasta que respondan para calentar Render."""
    base = url.rstrip("/")
    primer_dia = fecha_ref.replace(day=1).isoformat()
    rutas = [
        "/api/salud",
        "/api/ninos?estado=ACTIVO&limite=200",
        "/api/ninos?estado=ACTIVO&limite=200&q=DEMO",
        "/api/agenda",
        "/api/visitas/priorizadas?limite=10",
        "/api/recordatorios?limite=10",
        "/api/recordatorios/metricas",
        "/api/alertas/resumen",
        "/api/alertas/controles-vencidos?limite=10",
        "/api/alertas/barreras",
        "/api/sincronizacion/conflictos?estado=PENDIENTE",
        f"/api/reportes/periodo?desde={primer_dia}&hasta={fecha_ref.isoformat()}",
    ]
    print("\n[CALENTAMIENTO] Calentando endpoints de producción antes de grabar...")
    for ruta in rutas:
        url_completa = f"{base}{ruta}"
        t0 = time.monotonic()
        intentos = 0
        while True:
            intentos += 1
            try:
                resp = pg.request.get(url_completa, timeout=90_000)
                if resp.ok:
                    dur = time.monotonic() - t0
                    print(f"  OK {resp.status} en {dur:4.1f} s → {ruta}")
                    break
                print(f"  Reintentando (HTTP {resp.status}) → {ruta}")
            except Exception as e:
                print(f"  Esperando respuesta ({e}) → {ruta}")
            if intentos >= 3:
                print(f"  Aviso: {ruta} no respondió 200 tras {intentos} intentos; continuando.")
                break
            time.sleep(2)
    print("[CALENTAMIENTO] Endpoints listos.\n")


# ---------------------------------------------------------------------------------------------------------
# Estructuras de pasos y piloto
# ---------------------------------------------------------------------------------------------------------
class PasoResultado:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.inicio = time.monotonic()
        self.duracion = 0.0
        self.estado = "PENDIENTE"
        self.detalle = ""
        self.ultima_respuesta = None

    def terminar_ok(self, detalle: str = "") -> None:
        self.duracion = time.monotonic() - self.inicio
        self.estado = "OK"
        self.detalle = detalle

    def terminar_fallo(self, detalle: str = "") -> None:
        self.duracion = time.monotonic() - self.inicio
        self.estado = "FALLO"
        self.detalle = detalle


class Piloto:
    def __init__(self, pg, grabadora: Grabadora | None = None):
        self.pg = pg
        self.grabadora = grabadora
        self.pasos: list[PasoResultado] = []
        self.paso_actual: PasoResultado | None = None
        self._captura_guardada = False

    def guardar_captura(self, prefijo: str = "error") -> Path | None:
        """Guarda captura de pantalla completa en el directorio TEMP del sistema e imprime su ruta."""
        captura = Path(tempfile.gettempdir()) / f"{prefijo}_{int(time.time())}.png"
        try:
            self.pg.screenshot(path=str(captura), full_page=True)
            self._captura_guardada = True
            print(f"  [CAPTURA ERROR] Pantalla completa guardada en: {captura}")
            return captura
        except Exception as e:
            print(f"  [AVISO] No se pudo guardar captura ({e})")
            return None

    def t(self, testid: str):
        return self.pg.get_by_test_id(testid)

    def rotulo(self, texto: str) -> None:
        self.pg.evaluate(ROTULO_JS, texto)

    def leyenda(self, texto: str, pausa: float = 0) -> None:
        self.pg.evaluate(LEYENDA_JS, texto)
        if pausa > 0:
            time.sleep(pausa)

    def clic(self, loc, espera: float = 0.6) -> None:
        loc.scroll_into_view_if_needed()
        loc.hover()
        time.sleep(0.25)
        loc.click()
        if espera > 0:
            time.sleep(espera)

    def escribir(self, loc, texto: str, retardo: int = 35) -> None:
        loc.scroll_into_view_if_needed()
        loc.click()
        loc.fill("")
        loc.type(texto, delay=retardo)

    def elegir(self, loc, valor: str) -> None:
        loc.scroll_into_view_if_needed()
        loc.select_option(valor)
        time.sleep(0.4)

    def reponer_rotulo(self, texto: str) -> None:
        """Tras una recarga o navegación el DOM inyectado desaparece."""
        self.rotulo(texto)

    @contextmanager
    def paso(self, nombre: str):
        p = PasoResultado(nombre)
        self.paso_actual = p
        self.pasos.append(p)
        self._captura_guardada = False
        print(f"\n[PASO] {nombre}...")
        try:
            yield p
            p.terminar_ok()
            print(f"  → OK ({p.duracion:4.1f} s)")
        except Exception as exc:
            if not getattr(self, "_captura_guardada", False):
                self.guardar_captura("error_paso")
            p.terminar_fallo(str(exc))
            print(f"  → FALLO ({p.duracion:4.1f} s): {exc}")
            if self.grabadora:
                self.grabadora.detener()
            raise
        finally:
            self.paso_actual = None

    @contextmanager
    def esperar_red(
        self,
        url_substring: str,
        metodo: str = "POST",
        status_esperado: int | tuple[int, ...] = (200, 201),
        timeout_ms: int = 90_000,
    ):
        """Espera una respuesta HTTP del servidor Render y valida su código de estado."""
        esperados = (status_esperado,) if isinstance(status_esperado, int) else status_esperado

        def _pred(r):
            return url_substring in r.url and r.request.method.upper() == metodo.upper()

        with self.pg.expect_response(_pred, timeout=timeout_ms) as info:
            yield
        resp = info.value
        cuerpo = ""
        try:
            cuerpo = resp.text()
        except Exception:  # noqa: S110
            pass

        if resp.status not in esperados:
            captura = self.guardar_captura(f"error_http_{resp.status}")
            if self.grabadora:
                self.grabadora.detener()
            nombre = self.paso_actual.nombre if self.paso_actual else "Acción de red"
            msg = (
                f"\n[ERROR EN PASO] {nombre}\n"
                f"  URL: {resp.url}\n"
                f"  Método: {metodo}\n"
                f"  Status real: {resp.status} (esperado: {esperados})\n"
                f"  Cuerpo recibido: {cuerpo[:500]}\n"
                f"  Captura guardada en: {captura}"
            )
            print(msg)
            raise RuntimeError(msg)

        if self.paso_actual:
            self.paso_actual.ultima_respuesta = resp


def seleccionar_comunidad_demo(
    p: Piloto,
    testid_select: str,
    comunidad: str = COMUNIDAD_DEMO,
    timeout_s: float = 30.0,
    obligatorio: bool = True,
) -> bool:
    """Espera a que exista la opción de comunidad DEMO y la selecciona.

    Si obligatorio es False y la opción no aparece en el plazo, continúa sin abortar.
    """
    sel = p.t(testid_select)
    opcion = sel.locator(f'option[value="{comunidad}"]')
    try:
        opcion.wait_for(state="attached", timeout=int(timeout_s * 1000))
        sel.select_option(comunidad)
        sel.dispatch_event("change")
        time.sleep(0.8)
        return True
    except Exception as e:
        if not obligatorio:
            print(
                f"  [AVISO] La opción '{comunidad}' no apareció en {testid_select}; continuando sin filtrar por select."
            )
            return False
        captura = p.guardar_captura(f"error_comunidad_{testid_select}")
        if p.grabadora:
            p.grabadora.detener()
        msg = f"La opción '{comunidad}' no apareció en {testid_select} en {timeout_s} s."
        print(f"[ERROR] {msg} Captura: {captura}")
        raise RuntimeError(msg) from e


def llenar_registro(
    p: Piloto,
    dni: str,
    nombres: str,
    apellidos: str,
    hb: str,
    fecha_ref: date,
    fecha_control: date | None = None,
    fecha_nac: date | None = None,
) -> None:
    """Rellena el formulario de registro con datos válidos o de prueba clínica."""
    pg = p.pg
    f_ctrl = fecha_control or fecha_ref
    f_nac = fecha_nac or (fecha_ref - timedelta(days=150))
    pg.locator("#fecha").fill(f_ctrl.isoformat())
    p.escribir(pg.locator("#dni"), dni)
    p.escribir(pg.locator("#nombres"), nombres)
    p.escribir(pg.locator("#apellidos"), apellidos)
    p.elegir(pg.locator("#sexo"), "F")
    pg.locator("#fecha_nacimiento").fill(f_nac.isoformat())
    p.escribir(pg.locator("#comunidad"), COMUNIDAD_DEMO)
    p.escribir(pg.locator("#altitud_m"), "3720")
    p.escribir(pg.locator("#tutor_nombre"), "DEMO Tutor")
    p.escribir(pg.locator("#tutor_celular"), "999000001")
    p.escribir(pg.locator("#hemoglobina_observada"), hb)
    p.escribir(pg.locator("#peso_kg"), "6.8")
    p.escribir(pg.locator("#talla_cm"), "62")


def abrir_expediente(p: Piloto, dni: str) -> None:
    """Abre un expediente buscando por DNI y esperando confirmación de red y que el DOM muestre el DNI."""
    p.clic(p.t("tab-expediente"))
    p.escribir(p.t("buscar-dni"), dni)
    with p.esperar_red(f"/api/ninos/dni/{dni}", metodo="GET", status_esperado=200):
        p.clic(p.pg.locator("#btn-buscar-dni"))
    # Espera explícita a que el expediente cargado contenga el DNI buscado antes de seguir
    p.pg.locator("#expediente").get_by_text(dni).first.wait_for(state="visible", timeout=90_000)
    p.t("tabla-evaluaciones").wait_for(state="visible", timeout=90_000)


def portada(ctx, texto: str, segundos: float) -> None:
    tarjeta = ctx.new_page()
    tarjeta.set_content(PORTADA.format(texto=texto))
    tarjeta.bring_to_front()
    time.sleep(segundos)
    tarjeta.close()


# ---------------------------------------------------------------------------------------------------------
# Guion de recorrido verificado
# ---------------------------------------------------------------------------------------------------------
def recorrido(ctx, pg, url: str, fecha_ref: date, grabadora: Grabadora | None = None) -> list[PasoResultado]:
    p = Piloto(pg, grabadora)

    with p.paso("Portada inicial"):
        portada(ctx, "PMV · Incremento 1 · Incremento 2 · Incremento 3 · Incremento 4", 16)
        pg.bring_to_front()

    # ---------- Escena 1 · PMV · Incremento 1 ----------
    r1 = "PMV · Incremento 1 (v1.0-PMV)"
    p.rotulo(r1)
    p.clic(p.t("tab-registro"))
    dni, nom, ape = NINOS_DEMO["inc1"]

    with p.paso("RF-03 · Validación clínica: rechazo de datos fuera de rango (422)"):
        p.leyenda("RF-03 · Validación: el sistema rechaza datos fuera de rango", 7)
        llenar_registro(p, DNI_INVALIDO, nom, ape, "25", fecha_ref)
        with p.esperar_red("/api/ninos", metodo="POST", status_esperado=422):
            p.clic(p.t("guardar"))
        pg.locator("#alerta-registro").wait_for(state="visible", timeout=90_000)
        time.sleep(2)

    id_nino1 = None
    with p.paso("RF-01 · Registro de niño y evaluación inicial"):
        p.leyenda("RF-01 · Registro con Hb ajustada por altitud y clasificación automática", 8)
        # Se fijan fechas para que tenga al menos un control VENCIDO a fecha_ref:
        # Nacimiento hace 270 días (~9 m) y evaluación inicial con anemia moderada hace 75 días (~2.5 m).
        # La evaluación inicial (6 m de edad) cumple DHx (6 m) y abre episodio de tratamiento.
        # El control de tratamiento C1M (+1 m, hace 45 días) venció hace 15 días (ventana de 30 días):
        # queda VENCIDO a fecha_ref, produciendo alerta crítica, recordatorio y prioridad de visita.
        f_nac_demo1 = fecha_ref - timedelta(days=270)
        f_eval_inicial = fecha_ref - timedelta(days=75)
        pg.locator("#fecha").fill(f_eval_inicial.isoformat())
        pg.locator("#fecha_nacimiento").fill(f_nac_demo1.isoformat())
        p.escribir(pg.locator("#dni"), dni)
        p.escribir(pg.locator("#hemoglobina_observada"), "11.6")
        p.t("clasificacion-previa").wait_for(state="visible", timeout=90_000)
        time.sleep(2)
        with p.esperar_red("/api/ninos", metodo="POST", status_esperado=201):
            p.clic(p.t("guardar"))
        resp_exp = p.paso_actual.ultima_respuesta.json()
        id_nino1 = resp_exp["id"]
        p.t("tabla-evaluaciones").wait_for(state="visible", timeout=90_000)

    with p.paso("RF-02 · Expediente digital único y nuevo control"):
        p.leyenda("RF-02 · Expediente digital único; el sistema clasifica, no diagnostica", 8)
        form = pg.locator("#form-control")
        form.locator("[name=fecha]").fill(fecha_ref.isoformat())
        p.escribir(form.locator("[name=hemoglobina_observada]"), "11.5")
        p.escribir(form.locator("[name=peso_kg]"), "8.2")
        p.escribir(form.locator("[name=talla_cm]"), "69")
        with p.esperar_red(f"/api/ninos/{id_nino1}/evaluaciones", metodo="POST", status_esperado=201):
            p.clic(p.t("guardar-control"))
        pg.locator('[data-testid="tabla-evaluaciones"] tbody tr').nth(1).wait_for(state="visible", timeout=90_000)
        time.sleep(2)

    with p.paso("RF-04 · Seguimiento filtrado a registros DEMO"):
        p.leyenda("RF-04 · Seguimiento (filtrado a los registros DEMO)")
        with p.esperar_red("/api/ninos", metodo="GET", status_esperado=200):
            p.clic(p.t("tab-seguimiento"))
        with p.esperar_red("q=DEMO", metodo="GET", status_esperado=200):
            p.escribir(p.t("buscar"), "DEMO")
        pg.locator('[data-testid="tabla-seguimiento"] tbody tr:has-text("DEMO")').first.wait_for(
            state="visible", timeout=90_000
        )
        time.sleep(4)

    with p.paso("RF-05 · Reporte del periodo exportable a CSV"):
        p.clic(p.t("tab-reporte"))
        with p.esperar_red("/api/reportes/periodo", metodo="GET", status_esperado=200):
            p.clic(p.t("generar-reporte"))
        p.t("kpi-registrados").wait_for(state="visible", timeout=90_000)
        p.leyenda("RF-05 · Reporte del periodo, exportable a CSV", 8)
        time.sleep(2)

    # ---------- Escena 2 · Incremento 2 ----------
    p.rotulo("Incremento 2 (v2.0-Inc2)")
    with p.paso("RF-06 · Agenda de controles del niño"):
        abrir_expediente(p, dni)
        p.leyenda("RF-06 · Agenda de controles del niño (esquema por edad)", 8)
        p.t("agenda-tabla").wait_for(state="visible", timeout=90_000)

    with p.paso("RF-09 · Inasistencia a control vencido"):
        p.leyenda("RF-09 · Inasistencia: registro de motivo de control vencido", 8)
        fila_vencida = pg.locator('[data-testid="agenda-tabla"] tr[data-estado="VENCIDO"]').first
        fila_vencida.wait_for(state="visible", timeout=90_000)
        btn_no_asistio = fila_vencida.locator('[data-testid="btn-no-asistio"]')
        btn_no_asistio.wait_for(state="visible", timeout=90_000)
        p.clic(btn_no_asistio)
        p.t("modal-asistencia").wait_for(state="visible", timeout=90_000)
        p.elegir(p.t("asistencia-motivo"), "Enfermedad del niño")
        p.escribir(p.t("asistencia-detalle"), "DEMO fiebre")
        with p.esperar_red("/asistencia", metodo="POST", status_esperado=201):
            p.clic(p.t("asistencia-confirmar"))
        p.t("marca-inasistencia").first.wait_for(state="visible", timeout=90_000)
        time.sleep(2)

    with p.paso("RF-08 · Agenda del personal y validación de rango"):
        with p.esperar_red("/api/agenda", metodo="GET", status_esperado=200):
            p.clic(p.t("tab-agenda"))
        pg.get_by_test_id("agenda-desde").fill(fecha_ref.isoformat())
        pg.get_by_test_id("agenda-hasta").fill((fecha_ref + timedelta(days=30)).isoformat())
        seleccionar_comunidad_demo(p, "filtro-agenda-comunidad", COMUNIDAD_DEMO, timeout_s=30.0, obligatorio=False)
        with p.esperar_red("/api/agenda", metodo="GET", status_esperado=200):
            p.clic(p.t("agenda-consultar"))
        pg.locator('[data-testid="agenda-personal-tabla"]').wait_for(state="visible", timeout=90_000)
        p.leyenda("RF-08 · Agenda del personal: controles por día (rango máximo 31 días)", 8)

        # Validación del límite de 31 días (rechaza con 422)
        pg.get_by_test_id("agenda-hasta").fill((fecha_ref + timedelta(days=40)).isoformat())
        with p.esperar_red("/api/agenda", metodo="GET", status_esperado=422):
            p.clic(p.t("agenda-consultar"))
        p.t("agenda-error").wait_for(state="visible", timeout=90_000)
        time.sleep(3)

    # ---------- Escena 3 · Incremento 3 ----------
    r3 = "Incremento 3 (v3.0-Inc3)"
    pg.evaluate("navigator.serviceWorker.ready.then(() => true)")
    pg.reload()
    pg.wait_for_function("navigator.serviceWorker.controller !== null", timeout=90_000)
    p.rotulo(r3)

    with p.paso("HIST-3.1 · Registro sin conexión en cola IndexedDB"):
        p.leyenda("HIST-3.1 · Sin conexión: el registro queda en la cola local (IndexedDB)", 8)
        ctx.set_offline(True)
        p.clic(p.t("tab-registro"))
        dni2, nom2, ape2 = NINOS_DEMO["offline"]
        llenar_registro(
            p,
            dni2,
            nom2,
            ape2,
            "9.4",
            fecha_ref,
            fecha_control=fecha_ref,
            fecha_nac=fecha_ref - timedelta(days=180),
        )
        p.clic(p.t("guardar"))
        p.t("tabla-evaluaciones").wait_for(state="visible", timeout=90_000)
        pg.locator('[data-testid="expediente-pendiente"]').wait_for(state="visible", timeout=90_000)
        time.sleep(2)

    with p.paso("HIST-3.4 / HIST-3.2 · Reconexión y sincronización"):
        p.clic(p.t("tab-sincronizacion"))
        pg.locator('[data-testid="sync-tabla"] tbody tr').first.wait_for(state="visible", timeout=90_000)
        p.leyenda("HIST-3.4 · Pendientes y su antigüedad", 8)
        p.leyenda("HIST-3.2 · Al reconectar se sincroniza; el id de operación evita duplicados", 8)
        ctx.set_offline(False)
        # Se envía evento 'online' y se pulsa sync-ahora asegurando la petición de sincronización
        with p.esperar_red("/api/sincronizacion", metodo="POST", status_esperado=200):
            pg.evaluate("window.dispatchEvent(new Event('online'))")
            p.clic(p.t("sync-ahora"))
        # Espera hasta que el indicador confirme 0 pendientes
        pg.wait_for_function(
            "document.querySelector('[data-testid=indicador-sync]').dataset.pendientes === '0'", timeout=90_000
        )
        time.sleep(3)

    with p.paso("VIS-3.5 · Visitas domiciliarias priorizadas con desglose explicable"):
        with p.esperar_red("/api/visitas/priorizadas", metodo="GET", status_esperado=200):
            p.clic(p.t("tab-visitas"))
        pg.locator('[data-testid="visitas-tabla"] tbody tr[data-testid="visita-priorizada"]').first.wait_for(
            state="visible", timeout=90_000
        )
        p.leyenda("VIS-3.5 · Visitas domiciliarias priorizadas por puntaje con su desglose", 10)
        p.clic(pg.locator('[data-testid="visitas-tabla"] button[data-testid="puntaje"]').first)
        pg.locator('[data-testid="desglose"]').first.wait_for(state="visible", timeout=90_000)
        time.sleep(3)

    # ---------- Escena 4 · Incremento 4 ----------
    p.rotulo("Incremento 4 (v4.0-Inc4)")
    with p.paso("HIST-4.1 · Recordatorios al tutor (modo simulado)"):
        with p.esperar_red("/api/recordatorios", metodo="GET", status_esperado=200):
            p.clic(p.t("tab-recordatorios"))
        p.leyenda("HIST-4.1 · Recordatorios al tutor: en esta versión el envío es SIMULADO", 8)
        if not verificar_modo_simulado(pg, url):
            raise SystemExit("ABORTADO: El modo de recordatorios no es SIMULADO.")
        with p.esperar_red("/api/recordatorios/generar", metodo="POST", status_esperado=200):
            p.clic(p.t("recordatorios-generar"))
        pg.locator('[data-testid="recordatorios-tabla"] tbody tr[data-testid="recordatorio"]').first.wait_for(
            state="visible", timeout=90_000
        )
        p.t("recordatorios-resultado").wait_for(state="visible", timeout=90_000)
        time.sleep(3)

    with p.paso("HIST-4.2 · Respuesta del tutor a recordatorio"):
        fila_rec_demo = pg.locator(f'[data-testid="recordatorio"]:has-text("{nom}"):has([data-testid="btn-responder"])')
        # Solo se responde un recordatorio de un niño DEMO: nunca se modifican datos reales.
        fila_rec = fila_rec_demo.first
        fila_rec.wait_for(state="visible", timeout=90_000)
        rec_id = fila_rec.get_attribute("data-id")
        p.leyenda("HIST-4.2 · Respuesta del tutor: no puede asistir por rechazo al tratamiento", 8)
        p.clic(fila_rec.locator('[data-testid="btn-responder"]'))
        p.t("modal-respuesta").wait_for(state="visible", timeout=90_000)
        p.elegir(p.t("respuesta-opcion"), "NO_PUEDE")
        p.elegir(p.t("respuesta-barrera"), "RECHAZO_TRATAMIENTO")
        with p.esperar_red(f"/api/recordatorios/{rec_id}/respuesta", metodo="POST", status_esperado=200):
            p.clic(p.t("respuesta-confirmar"))
        p.t("modal-respuesta").wait_for(state="hidden", timeout=90_000)
        time.sleep(3)

    with p.paso("HIST-4.3 · Registro de barrera en expediente"):
        abrir_expediente(p, dni)
        p.clic(p.t("btn-barrera-nino"))
        p.t("modal-barrera").wait_for(state="visible", timeout=90_000)
        p.leyenda("HIST-4.3 · Registro de barreras por niño (también sin conexión)", 8)
        tipo = p.t("barrera-tipo")
        tipo.select_option(index=1)
        p.escribir(p.t("barrera-detalle"), "DEMO sin transporte a la posta")
        with p.esperar_red(f"/api/ninos/{id_nino1}/barreras", metodo="POST", status_esperado=201):
            p.clic(p.t("barrera-confirmar"))
        p.t("barreras-nino-tabla").wait_for(state="visible", timeout=90_000)
        time.sleep(3)

    with p.paso("HIST-4.4 · Alertas de barreras críticas"):
        with p.esperar_red("/api/alertas/barreras", metodo="GET", status_esperado=200):
            p.clic(p.t("tab-alertas"))
        p.leyenda("HIST-4.4 · Alertas de barreras críticas", 8)

        # Si el select de comunidad incluye la comunidad DEMO, se aplica el filtro por API;
        # si no (en producción app.js extrae las opciones solo de los primeros 200 controles vencidos
        # y el niño DEMO no entra en esa página), no se depende del select.
        sel_alerta = p.t("filtro-alerta-comunidad")
        if sel_alerta.locator(f'option[value="{COMUNIDAD_DEMO}"]').count() > 0:
            with p.esperar_red("/api/alertas/barreras", metodo="GET", status_esperado=200):
                sel_alerta.select_option(COMUNIDAD_DEMO)
                sel_alerta.dispatch_event("change")
            time.sleep(0.8)

        # Verificación de que la alerta de barrera crítica del niño DEMO existe
        fila_barrera = pg.locator('[data-testid="alerta-barrera"]:has-text("DEMO")').first
        fila_barrera.wait_for(state="visible", timeout=90_000)

        # Scroll a la sección de barreras críticas y resaltado visual para la grabación
        p.t("alertas-barreras-tabla").scroll_into_view_if_needed()
        fila_barrera.scroll_into_view_if_needed()
        fila_barrera.hover()
        fila_barrera.evaluate(
            """el => {
                el.style.transition = 'all 0.4s ease';
                el.style.backgroundColor = '#dbeafe';
                el.style.outline = '3px solid #1F4E79';
            }"""
        )
        time.sleep(5)

    # ---------- Escena 5 · Calidad y arquitectura ----------
    with p.paso("Escena 5 · Calidad y arquitectura"):
        repo = "https://github.com/woshtsu/ProcesosSoftwareAnemia"
        for ruta, texto, s in [
            ("/tree/v4.0-Inc4/pmv_fastapi/app", "Arquitectura hexagonal: domain, ports, adapters, application", 14),
            ("/actions", "Integración continua en GitHub Actions", 12),
            ("/tags", "Versiones: v1.0-PMV, v2.0-Inc2, v3.0-Inc3, v4.0-Inc4", 12),
        ]:
            pg.goto(repo + ruta, wait_until="domcontentloaded", timeout=90_000)
            p.rotulo("Calidad y arquitectura")
            p.leyenda(texto, s)
        portada(ctx, "Limitaciones: envío real no probado · validación en una posta pendiente", 10)

    return p.pasos


# ---------------------------------------------------------------------------------------------------------
# Limpieza de los datos DEMO (la API no expone DELETE)
# ---------------------------------------------------------------------------------------------------------
def sql_limpieza() -> str:
    dnis = ", ".join(f"'{d}'" for d, _, _ in NINOS_DEMO.values())
    filtro_nino = f"(dni IN ({dnis}) OR dni LIKE '7999%') AND nombres LIKE 'DEMO %'"
    ninos = f"SELECT id FROM nino WHERE {filtro_nino}"  # noqa: S608 - constantes del script
    evals = f"SELECT id FROM evaluacion_hemoglobina WHERE nino_id IN ({ninos})"  # noqa: S608
    asists = f"SELECT id FROM asistencia_control WHERE nino_id IN ({ninos})"  # noqa: S608
    visitas = f"SELECT id FROM visita_domiciliaria WHERE nino_id IN ({ninos})"  # noqa: S608
    recs = f"SELECT id FROM recordatorio WHERE nino_id IN ({ninos})"  # noqa: S608
    barreras = f"SELECT id FROM barrera WHERE nino_id IN ({ninos})"  # noqa: S608
    return (
        "BEGIN;\n"
        f"DELETE FROM conflicto_sincronizacion WHERE nino_id IN ({ninos});\n"
        f"DELETE FROM operacion_sincronizada WHERE id_recurso IN ({ninos})\n"
        f"   OR id_recurso IN ({evals})\n"
        f"   OR id_recurso IN ({asists})\n"
        f"   OR id_recurso IN ({visitas})\n"
        f"   OR id_recurso IN ({recs})\n"
        f"   OR id_recurso IN ({barreras});\n"
        f"DELETE FROM barrera WHERE nino_id IN ({ninos});\n"
        f"DELETE FROM recordatorio WHERE nino_id IN ({ninos});\n"
        f"DELETE FROM asistencia_control WHERE nino_id IN ({ninos});\n"
        f"DELETE FROM visita_domiciliaria WHERE nino_id IN ({ninos});\n"
        f"DELETE FROM evaluacion_hemoglobina WHERE nino_id IN ({ninos});\n"
        f"DELETE FROM nino WHERE {filtro_nino};\n"
        "COMMIT;\n"
    )


def limpiar() -> Path:
    sql = sql_limpieza()
    archivo = Path(tempfile.gettempdir()) / "limpieza_demo_anemia.sql"
    archivo.write_text(sql, encoding="utf-8")
    print("SQL de limpieza generado en:", archivo)
    return archivo


def imprimir_resumen_ensayo(pasos: list[PasoResultado], duracion_total_s: float) -> None:
    print("\n" + "=" * 80)
    print("RESUMEN DEL ENSAYO (MODO ENSAYO - VALIDACIÓN EN PRODUCCIÓN)")
    print("=" * 80)
    for i, p in enumerate(pasos, 1):
        estado_fmt = f"[{p.estado}]"
        print(f"Paso {i:02d}: {p.nombre:<54} {estado_fmt:>8} ({p.duracion:5.1f} s)")
    print("-" * 80)
    exitosos = sum(1 for p in pasos if p.estado == "OK")
    fallidos = sum(1 for p in pasos if p.estado == "FALLO")
    minutos = int(duracion_total_s // 60)
    segundos = int(duracion_total_s % 60)
    print(f"Total de pasos: {len(pasos)} | Exitosos: {exitosos} | Fallidos: {fallidos}")
    print(f"Duración total del recorrido: {minutos:02d}:{segundos:02d} ({duracion_total_s:.1f} s)")
    print("Duración objetivo estimada en video: 04:50 - 05:10 (290 s - 310 s)")
    if 290 <= duracion_total_s <= 310:
        print("Calibración de tiempo: DENTRO DEL RANGO OBJETIVO")
    elif duracion_total_s < 290:
        diff = 290 - duracion_total_s
        print(f"Calibración de tiempo: {diff:.1f} s por debajo del objetivo de 4:50")
    else:
        diff = duracion_total_s - 310
        print(f"Calibración de tiempo: {diff:.1f} s por encima del objetivo de 5:10")
    print("=" * 80 + "\n")


def main() -> None:
    import sys

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=URL_PROD)
    ap.add_argument("--salida", type=Path, default=SALIDA_POR_DEFECTO)
    ap.add_argument("--ffmpeg")
    ap.add_argument("--prueba", type=float, metavar="SEG", help="solo graba SEG segundos, sin crear datos")
    ap.add_argument(
        "--ensayo",
        action="store_true",
        help="ejecuta el recorrido completo sin ffmpeg (tras login) para validar contra producción e imprimir resumen",
    )
    ap.add_argument("--solo-limpiar", action="store_true")
    args = ap.parse_args()

    if args.solo_limpiar:
        limpiar()
        return

    usar_grabadora = not (args.ensayo or args.solo_limpiar)
    grabadora = None
    if usar_grabadora:
        salida = args.salida.with_name(args.salida.stem + "_prueba.mp4") if args.prueba else args.salida
        grabadora = Grabadora(localizar_ffmpeg(args.ffmpeg), salida)

    perfil = Path(tempfile.mkdtemp(prefix="edge_demo_"))
    try:
        with sync_playwright() as p:
            ctx, pg = abrir_edge(p, perfil)
            esperar_login(pg, args.url)
            fecha_ref = obtener_fecha_referencia(pg, args.url)
            print(f"Fecha de referencia obtenida de /api/salud: {fecha_ref}")

            # Calentamiento de endpoints antes de arrancar ffmpeg
            if not args.prueba:
                calentar_servidor(pg, args.url, fecha_ref)

            t_inicio = time.monotonic()
            pasos_ensayo: list[PasoResultado] = []
            try:
                if grabadora:
                    grabadora.iniciar()
                if args.prueba:
                    Piloto(pg).rotulo(f"Prueba de grabación · escritorio completo · fecha ref: {fecha_ref}")
                    time.sleep(args.prueba)
                else:
                    pasos_ensayo = recorrido(ctx, pg, args.url, fecha_ref, grabadora=grabadora)
            finally:
                if grabadora:
                    grabadora.detener()
                ctx.close()

            if args.ensayo and pasos_ensayo:
                dur_total = time.monotonic() - t_inicio
                imprimir_resumen_ensayo(pasos_ensayo, dur_total)
    finally:
        shutil.rmtree(perfil, ignore_errors=True)
        if not args.prueba:
            limpiar()

    if grabadora and grabadora.salida:
        print("Video:", grabadora.salida)


if __name__ == "__main__":
    main()
