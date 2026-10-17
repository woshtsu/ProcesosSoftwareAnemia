#!/usr/bin/env python
"""Captura de evidencias visuales (Actividad 5, guía S9) con Chromium headless (Playwright).

Ejecuta el software REAL (servidor uvicorn + base SQLite propia + datos sintéticos) y fotografía cada paso de los
requerimientos funcionales. Es reproducible y se parametriza por versión, puerto y rutas.

Modos (--modo):
  inc1          RF-01..RF-05 sobre la v1.0-PMV                -> evidencias_capturas/inc1/
  inc2          RF-06 y RF-07 sobre la v1.5                    -> evidencias_capturas/inc2/
  regresion     RF-01..RF-05 sobre la v1.5 (una captura por RF) -> evidencias_capturas/regresion_v1.5/
  arquitectura  árbol de app/ de ambas versiones (HTML monoespaciado -> PNG) -> evidencias_capturas/arquitectura/
  indice        genera INDICE.md a partir de los resultados_*.json

Uso (desde cualquier carpeta; el intérprete debe tener playwright instalado):
  python capturar_evidencias.py --modo inc1   (si hace falta, PLAYWRIGHT_BROWSERS_PATH apunta a los navegadores de Playwright)
  ... --modo inc2 ; --modo regresion ; --modo arquitectura ; --modo indice
Parámetros: --app-dir, --puerto, --db, --version-etiqueta, --salida, --sin-servidor (usa un servidor ya levantado).

MARCA DE EVIDENCIA: antes de cada captura se inyecta en la página un pie fijo (position:fixed) con RF, paso, URL,
versión, fecha-hora de Perú y la leyenda «datos sintéticos». No altera la funcionalidad; se declara en el informe.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[3]  # raíz del repositorio
# v1.0: copia del tag (git worktree add ../inc1_v1.0_PMV v1.0-PMV); configurable con GQM_RAIZ_V10
APP_V10 = Path(os.getenv("GQM_RAIZ_V10", str(REPO.parent / "inc1_v1.0_PMV")))
APP_V15 = REPO / "pmv_fastapi"
SALIDA = Path(__file__).resolve().parent
LIMA = ZoneInfo("America/Lima")
VIEWPORT = {"width": 1366, "height": 900}
UMBRAL_MS = 2000  # criterio modelo de la guía: confirmación en < 2 s


def ahora() -> str:
    return datetime.now(LIMA).strftime("%d/%m/%Y %H:%M:%S")


# --------------------------------------------------------------------------------------------------------------------
# Servidor
# --------------------------------------------------------------------------------------------------------------------
class Servidor:
    """Levanta la base propia, carga los datos sintéticos de la versión y arranca uvicorn."""

    def __init__(self, app_dir: Path, db: Path, puerto: int, reiniciar_flag: bool):
        self.app_dir, self.db, self.puerto, self.reiniciar_flag = app_dir, db, puerto, reiniciar_flag
        self.proc: subprocess.Popen | None = None
        self.url = f"http://127.0.0.1:{puerto}"

    def __enter__(self):
        self.db.parent.mkdir(parents=True, exist_ok=True)
        for sufijo in ("", "-wal", "-shm", "-journal"):
            Path(str(self.db) + sufijo).unlink(missing_ok=True)
        entorno = {**os.environ, "DATABASE_URL": f"sqlite:///{self.db}"}
        orden = [sys.executable, "-m", "scripts.cargar_datos_prueba"] + (["--reiniciar"] if self.reiniciar_flag else [])
        carga = subprocess.run(orden, cwd=self.app_dir, env=entorno, capture_output=True, text=True, check=True)
        self.salida_carga = carga.stdout.strip()
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:crear_app", "--factory", "--port", str(self.puerto)],
            cwd=self.app_dir, env=entorno, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for _ in range(100):
            try:
                if httpx.get(self.url + "/api/salud", timeout=1).status_code == 200:
                    return self
            except httpx.HTTPError:
                time.sleep(0.2)
        raise RuntimeError("El servidor no respondió en /api/salud")

    def __exit__(self, *exc):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()


# --------------------------------------------------------------------------------------------------------------------
# Registro de resultados
# --------------------------------------------------------------------------------------------------------------------
class Evidencias:
    def __init__(self, modo, version, carpeta: Path, solo_principales: bool):
        self.modo, self.version, self.carpeta, self.solo_principales = modo, version, carpeta, solo_principales
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self.capturas: list[dict] = []
        self.tiempos: list[dict] = []
        self.criterios: dict[str, dict] = {}
        self.hallazgos: list[str] = []

    def marca(self, pg, rf, paso, url_texto=None):
        texto = (f"Evidencia S9 · {rf} · {paso} · {url_texto or pg.url} · {self.version} · "
                 f"{ahora()} · datos sintéticos")
        pg.evaluate(
            """(t) => {
              let e = document.getElementById('s9-marca');
              if (!e) { e = document.createElement('div'); e.id = 's9-marca';
                e.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:2147483647;background:rgba(0,0,0,.78);'
                  + 'color:#fff;font:11px/1.4 monospace;padding:4px 8px;pointer-events:none;';
                document.body.appendChild(e); }
              e.textContent = t;
              document.body.style.paddingBottom = (e.offsetHeight + 6) + 'px';
            }""",
            texto,
        )
        return texto

    def foto(self, pg, rf, paso, nombre, descripcion, observado, principal=True, full=True, url_texto=None):
        """Guarda una captura. En modo regresión solo se guardan las marcadas como principales."""
        if self.solo_principales and not principal:
            return
        if self.solo_principales:  # regresión: una captura de resultado por RF -> RFxx_v15_regresion.png
            nombre = f"{rf.replace('-', '')}_v15_regresion.png"
        pg.wait_for_timeout(150)
        self.marca(pg, rf, paso, url_texto)
        ruta = self.carpeta / nombre
        if full:
            # Página completa con el pie realmente fijo al final: se agranda el viewport a la altura del documento
            # (así position:fixed;bottom:0 queda al pie de la imagen y no tapa contenido).
            ancho = pg.viewport_size["width"]
            alto0 = pg.viewport_size["height"]
            alto = max(alto0, pg.evaluate("document.documentElement.scrollHeight"))
            pg.set_viewport_size({"width": ancho, "height": alto})
            pg.wait_for_timeout(200)
            alto2 = max(alto0, pg.evaluate("document.documentElement.scrollHeight"))
            if alto2 != alto:
                pg.set_viewport_size({"width": ancho, "height": alto2})
                pg.wait_for_timeout(200)
            pg.screenshot(path=str(ruta))
            pg.set_viewport_size({"width": ancho, "height": alto0})
        else:
            pg.screenshot(path=str(ruta))
        self.capturas.append({
            "archivo": f"{self.carpeta.name}/{nombre}", "rf": rf, "incremento": self.modo, "paso": paso,
            "descripcion": descripcion, "fecha_hora": ahora(), "url": url_texto or pg.url,
            "resultado_observado": observado, "version": self.version,
        })
        print(f"  [captura] {nombre}")

    def tiempo(self, rf, accion, ms, umbral=True):
        self.tiempos.append({"rf": rf, "accion": accion, "ms": round(ms), "umbral_2s": umbral and ms < UMBRAL_MS})
        print(f"  [tiempo] {rf} · {accion}: {ms:.0f} ms")

    def criterio(self, rf, dado_cuando_entonces, cumple, detalle):
        self.criterios[rf] = {"gwt": dado_cuando_entonces, "cumple": bool(cumple), "detalle": detalle}
        print(f"  [criterio] {rf}: {'SÍ' if cumple else 'NO'} · {detalle}")

    def hallazgo(self, texto):
        self.hallazgos.append(texto)
        print(f"  [HALLAZGO] {texto}")

    def guardar_json(self):
        datos = {"modo": self.modo, "version": self.version, "capturas": self.capturas, "tiempos": self.tiempos,
                 "criterios": self.criterios, "hallazgos": self.hallazgos, "generado": ahora()}
        (SALIDA / f"resultados_{self.modo}.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), "utf-8")


def cronometrar(fn):
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000


# --------------------------------------------------------------------------------------------------------------------
# Flujos RF-01 .. RF-05 (iguales en v1.0 y v1.5)
# --------------------------------------------------------------------------------------------------------------------
def llenar_registro(pg, dni, hb="11.6", fecha_nac="2025-09-10", altitud="3720", completar_hb=True):
    pg.fill("#dni", dni)
    pg.fill("#nombres", "Rosa Elvira")
    pg.fill("#apellidos", "Ccente Poma")
    pg.select_option("#sexo", "F")
    pg.fill("#fecha_nacimiento", fecha_nac)
    pg.fill("#comunidad", "Palmayoc")
    pg.fill("#altitud_m", altitud)
    pg.fill("#tutor_nombre", "Elena Poma Rojas")
    pg.fill("#peso_kg", "8.4")
    pg.fill("#talla_cm", "71")
    if completar_hb:
        pg.fill("#hemoglobina_observada", hb)


def rf01(pg, ev: Evidencias, base: str, tag: str):
    rf, n = "RF-01", "RF01"
    pre = f"{n}_{tag}"
    DNI = "72000001"
    pg.goto(base)
    pg.get_by_test_id("tab-registro").click()
    llenar_registro(pg, DNI)
    pg.get_by_test_id("clasificacion-previa").wait_for()
    ev.foto(pg, rf, "Paso 1 · ENTRADA", f"{pre}_paso1_entrada.png",
            "Formulario «Registrar niño y evaluación inicial» lleno con datos sintéticos (DNI 72000001, Hb obs. 11,6 g/dL, "
            "3 720 m s. n. m.) antes de pulsar «Guardar registro»; la vista previa clínica ya muestra la clasificación.",
            "Formulario completo y vista previa «Anemia moderada»; aún no se ha guardado.", principal=False)

    def accion():
        pg.get_by_test_id("guardar").click()
        pg.get_by_test_id("tabla-evaluaciones").wait_for()
        pg.wait_for_function("document.querySelector('#toast') && !document.querySelector('#toast').hidden "
                             "&& document.querySelector('#toast').textContent.includes('Registro guardado')")
    ms = cronometrar(accion)
    ev.tiempo(rf, "clic en «Guardar registro» → confirmación visible + expediente", ms)
    ev.foto(pg, rf, "Paso 2 · RESULTADO", f"{pre}_paso2_resultado.png",
            "Confirmación «Registro guardado: Rosa Elvira Ccente Poma» y expediente del niño recién creado con su evaluación inicial.",
            f"Notificación de éxito y expediente abierto; confirmación en {ms:.0f} ms.")
    r = httpx.get(f"{base}/api/ninos/dni/{DNI}")
    persiste = r.status_code == 200 and len(r.json().get("evaluaciones", [])) == 1
    ok_ui = "Rosa Elvira Ccente Poma" in pg.get_by_test_id("expediente").inner_text()
    ev.criterio(rf, "Dado un formulario con datos válidos, cuando se pulsa «Guardar registro», entonces el sistema almacena "
                    "el registro, muestra confirmación y abre el expediente en < 2 s.",
                persiste and ok_ui and ms < UMBRAL_MS,
                f"GET /api/ninos/dni/{DNI} → {r.status_code} con 1 evaluación; confirmación en {ms:.0f} ms.")
    # Duplicado (409) como verificación adicional, sin captura
    d = httpx.post(f"{base}/api/ninos", json={"nino": {"dni": DNI, "nombres": "Rosa Elvira", "apellidos": "Ccente Poma", "sexo": "F",
                   "fecha_nacimiento": "2025-09-10", "establecimiento": "P. S. Chongos Alto", "distrito": "Chongos Alto",
                   "comunidad": "Palmayoc", "altitud_m": 3720, "tutor_nombre": "Elena Poma Rojas", "tutor_celular": None},
                   "evaluacion_inicial": {"fecha": datetime.now(LIMA).strftime("%Y-%m-%d"), "hemoglobina_observada": 11.6,
                                          "peso_kg": 8.4, "talla_cm": 71}})
    print(f"  [verif] DNI duplicado → HTTP {d.status_code}")
    ev.criterios[rf]["detalle"] += f" Verificación adicional: DNI repetido → HTTP {d.status_code}."


def rf02(pg, ev: Evidencias, base: str, tag: str):
    rf, n = "RF-02", "RF02"
    pre = f"{n}_{tag}"
    DNI = "71000001"
    hoy = datetime.now(LIMA).strftime("%Y-%m-%d")
    pg.goto(base)
    pg.get_by_test_id("tab-expediente").click()
    pg.get_by_test_id("buscar-dni").fill(DNI)
    ev.foto(pg, rf, "Paso 1 · ENTRADA", f"{pre}_paso1_entrada.png",
            "Pestaña «Expediente» con el DNI sintético 71000001 digitado en «Buscar expediente por DNI», antes de pulsar «Abrir».",
            "Campo de búsqueda con el DNI; expediente aún sin abrir.", principal=False, full=False)
    ms_consulta = cronometrar(lambda: (pg.click("#btn-buscar-dni"), pg.get_by_test_id("tabla-evaluaciones").wait_for()))
    ev.tiempo(rf, "consulta: clic en «Abrir» → expediente visible", ms_consulta)
    n_antes = pg.locator("[data-testid=tabla-evaluaciones] tbody tr").count()
    ev.foto(pg, rf, "Paso 2 · RESULTADO (consulta)", f"{pre}_paso2_resultado.png",
            "Expediente digital de Luz Mery Quispe Rojas: datos del niño, historial de evaluaciones, gráfico de Hb ajustada y formularios de edición/nuevo control.",
            f"Expediente con {n_antes} evaluaciones previas y todos los datos; carga en {ms_consulta:.0f} ms.", principal=False)
    # actualización de datos permitidos
    pg.click("#btn-editar")
    f = pg.locator("#form-editar")
    f.locator('[name="comunidad"]').fill("Llacuas")
    f.locator('[name="tutor_celular"]').fill("987654322")
    ev.foto(pg, rf, "Paso 3 · ENTRADA (actualización)", f"{pre}_paso3_entrada_actualizacion.png",
            "Formulario «Editar datos» abierto con cambios de comunidad (Chongos Alto → Llacuas) y celular del tutor (987654322).",
            "Formulario de edición con los nuevos valores, aún sin guardar.", principal=False)

    def guardar_edicion():
        f.locator("button.primario").click()
        pg.wait_for_function("document.querySelector('#toast') && !document.querySelector('#toast').hidden "
                             "&& document.querySelector('#toast').textContent.includes('Expediente actualizado')")
        pg.wait_for_function("document.querySelector('[data-testid=expediente]').innerText.includes('Llacuas')")
    ms_edit = cronometrar(guardar_edicion)
    ev.tiempo(rf, "actualización (PATCH): clic en «Guardar cambios» → confirmación + datos nuevos", ms_edit)
    ev.foto(pg, rf, "Paso 4 · RESULTADO (actualización)", f"{pre}_paso4_resultado_actualizacion.png",
            "Confirmación «Expediente actualizado»; el expediente ahora muestra comunidad Llacuas y celular 987654322.",
            f"Datos actualizados y persistidos; confirmación en {ms_edit:.0f} ms.", principal=False)
    pg.wait_for_function("document.querySelector('#toast').hidden")  # que no quede la confirmación anterior en la siguiente captura
    api = httpx.get(f"{base}/api/ninos/dni/{DNI}").json()
    edit_ok = api["comunidad"] == "Llacuas" and api["tutor_celular"] == "987654322"
    # nuevo control
    c = pg.locator("#form-control")
    c.locator('[name="fecha"]').fill(hoy)
    c.locator('[name="hemoglobina_observada"]').fill("11.5")
    c.locator('[name="peso_kg"]').fill("8.2")
    c.locator('[name="talla_cm"]').fill("69")
    ev.foto(pg, rf, "Paso 5 · ENTRADA (nuevo control)", f"{pre}_paso5_entrada_nuevo_control.png",
            "Formulario «Registrar nuevo control» con fecha de hoy, Hb 11,5 g/dL, peso 8,2 kg y talla 69 cm.",
            "Formulario de control completo, aún sin guardar.", principal=False)

    def guardar_control():
        c.locator("[data-testid=guardar-control]").click()
        pg.wait_for_function("document.querySelector('#toast') && !document.querySelector('#toast').hidden "
                             "&& document.querySelector('#toast').textContent.includes('Control registrado')")
        pg.wait_for_function(f"document.querySelectorAll('[data-testid=tabla-evaluaciones] tbody tr').length === {n_antes + 1}")
    ms_ctrl = cronometrar(guardar_control)
    ev.tiempo(rf, "nuevo control (POST): clic en «Guardar control» → confirmación + fila nueva", ms_ctrl)
    ev.foto(pg, rf, "Paso 6 · RESULTADO (nuevo control)", f"{pre}_paso6_resultado_nuevo_control.png",
            f"Confirmación «Control registrado»; el historial pasa de {n_antes} a {n_antes + 1} evaluaciones, con el historial anterior intacto.",
            f"Nueva fila en el historial y gráfico actualizado; confirmación en {ms_ctrl:.0f} ms.", principal=True)
    api = httpx.get(f"{base}/api/ninos/dni/{DNI}").json()
    ctrl_ok = len(api["evaluaciones"]) == n_antes + 1
    ev.criterio(rf, "Dado un expediente existente, cuando se consulta y se actualizan campos permitidos y se agrega un nuevo "
                    "control, entonces persisten los cambios, el historial anterior se conserva y hay confirmación en < 2 s.",
                edit_ok and ctrl_ok and max(ms_consulta, ms_edit, ms_ctrl) < UMBRAL_MS,
                f"Consulta {ms_consulta:.0f} ms; PATCH {ms_edit:.0f} ms (comunidad/celular persistidos: {edit_ok}); "
                f"nuevo control {ms_ctrl:.0f} ms (evaluaciones {n_antes}→{len(api['evaluaciones'])}).")


def rf03(pg, ev: Evidencias, base: str, tag: str):
    rf, n = "RF-03", "RF03"
    pre = f"{n}_{tag}"
    pg.goto(base)
    pg.evaluate("localStorage.clear()")
    pg.reload()
    pg.get_by_test_id("tab-registro").click()
    llenar_registro(pg, "72000003", completar_hb=False)
    pg.wait_for_timeout(700)
    ev.foto(pg, rf, "Paso 1 · ENTRADA", f"{pre}_paso1_entrada.png",
            "Formulario con fecha de nacimiento, altitud (3 720 m) y demás datos, pero sin hemoglobina: la vista previa aún no puede validar.",
            "Vista previa vacía: «Complete fecha de nacimiento, altitud y hemoglobina…».", principal=False)

    def accion():
        pg.fill("#hemoglobina_observada", "11.6")
        pg.get_by_test_id("clasificacion-previa").wait_for()
    ms = cronometrar(accion)
    ev.tiempo(rf, "vista previa: digitar Hb → clasificación visible (incluye antirrebote de 350 ms)", ms)
    previa = pg.get_by_test_id("vista-previa").inner_text().replace("\n", " ")
    ajust = pg.get_by_test_id("hb-ajustada").inner_text()
    ev.foto(pg, rf, "Paso 2 · RESULTADO (vista previa)", f"{pre}_paso2_resultado.png",
            "Vista previa de validación clínica: edad al control, ajuste por altitud, Hb ajustada y clasificación calculadas por el servidor.",
            f"«{previa}» (Hb ajustada {ajust}).", principal=True)
    prev_ok = "Anemia moderada" in previa
    # rechazo
    pg.fill("#dni", "123")
    pg.fill("#hemoglobina_observada", "25")
    pg.wait_for_timeout(600)

    def rechazo():
        pg.get_by_test_id("guardar").click()
        pg.wait_for_selector(".campo.invalido")
    ms_rech = cronometrar(rechazo)
    ev.tiempo(rf, "rechazo: clic en «Guardar» con datos inválidos → mensajes por campo", ms_rech)
    texto = pg.inner_text("#form-registro")
    n_inv = pg.locator(".campo.invalido").count()
    ev.foto(pg, rf, "Paso 3 · RECHAZO", f"{pre}_paso3_rechazo.png",
            "Datos inválidos (DNI «123», Hb 25 g/dL) al guardar: el sistema rechaza (HTTP 422) y marca cada campo con su mensaje.",
            f"{n_inv} campo(s) marcado(s); mensajes visibles: DNI «exactamente 8 dígitos», Hb «rango clínico válido».", principal=False)
    rej = httpx.post(f"{base}/api/validaciones/evaluacion", json={
        "fecha_nacimiento": "2025-09-10", "altitud_m": 3720,
        "evaluacion": {"fecha": datetime.now(LIMA).strftime("%Y-%m-%d"), "hemoglobina_observada": 25, "peso_kg": 8.4, "talla_cm": 71}})
    rech_ok = "exactamente 8 dígitos" in texto and "rango clínico válido" in texto
    ev.criterio(rf, "Dado un formulario con datos clínicos, cuando se digita la Hb, entonces la vista previa muestra Hb ajustada y "
                    "clasificación; y cuando los datos son inválidos, entonces se rechaza con mensaje comprensible por campo.",
                prev_ok and rech_ok and ms_rech < UMBRAL_MS and rej.status_code == 422,
                f"Vista previa «Anemia moderada» en {ms:.0f} ms (incl. 350 ms de antirrebote); rechazo en {ms_rech:.0f} ms con "
                f"{n_inv} campos marcados; POST /api/validaciones/evaluacion con Hb 25 → HTTP {rej.status_code}.")


def rf04(pg, ev: Evidencias, base: str, tag: str):
    rf, n = "RF-04", "RF04"
    pre = f"{n}_{tag}"
    pg.goto(base)
    pg.get_by_test_id("tab-seguimiento").click()
    pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length > 1")
    total = pg.locator("#cuerpo-seguimiento tr").count()
    ev.foto(pg, rf, "Paso 1 · ENTRADA", f"{pre}_paso1_entrada.png",
            "Pestaña «Seguimiento» sin filtros: listado completo de niños con seguimiento activo, antes de aplicar un filtro.",
            f"{total} niños en seguimiento, con último control, Hb ajustada y clasificación.", principal=False)
    esperado = httpx.get(f"{base}/api/ninos", params={"estado": "ACTIVO", "clasificacion": "LEVE"}).json()

    def filtrar():
        pg.select_option("#filtro-clasificacion", "LEVE")
        pg.wait_for_function(f"document.querySelectorAll('#cuerpo-seguimiento tr').length === {len(esperado)}")
    ms_f = cronometrar(filtrar)
    ev.tiempo(rf, "filtro por clasificación «Anemia leve» → tabla filtrada", ms_f)
    badges = pg.locator("#cuerpo-seguimiento .badge").all_inner_texts()
    ev.foto(pg, rf, "Paso 2 · RESULTADO (filtro por clasificación)", f"{pre}_paso2_resultado.png",
            "Filtro «Anemia leve» aplicado: solo aparecen niños cuya última clasificación es leve, con fecha y antigüedad del último control.",
            f"{len(badges)} fila(s), todas «Anemia leve»; coincide con GET /api/ninos?clasificacion=LEVE ({len(esperado)}).", principal=True)
    filtro_ok = len(badges) == len(esperado) and all(b == "Anemia leve" for b in badges)
    # búsqueda por comunidad
    pg.select_option("#filtro-clasificacion", "")
    esperado2 = httpx.get(f"{base}/api/ninos", params={"estado": "ACTIVO", "q": "Palmayoc"}).json()

    def buscar():
        pg.get_by_test_id("buscar").fill("Palmayoc")
        pg.wait_for_function(f"document.querySelectorAll('#cuerpo-seguimiento tr').length === {len(esperado2)}")
    ms_b = cronometrar(buscar)
    ev.tiempo(rf, "búsqueda «Palmayoc» → tabla filtrada (incluye antirrebote de 250 ms)", ms_b)
    com = pg.locator("#cuerpo-seguimiento tr td:nth-child(4)").all_inner_texts()
    ev.foto(pg, rf, "Paso 3 · RESULTADO (búsqueda por comunidad)", f"{pre}_paso3_busqueda_comunidad.png",
            "Búsqueda por comunidad «Palmayoc»: el listado se reduce a los niños de esa comunidad.",
            f"{len(com)} fila(s), todas de Palmayoc.", principal=False)
    busq_ok = len(com) == len(esperado2) and all(c == "Palmayoc" for c in com)
    ev.criterio(rf, "Dado un conjunto de niños en seguimiento, cuando se filtra por clasificación o se busca por comunidad, "
                    "entonces el listado respeta el filtro y muestra el estado de control de cada niño en < 2 s.",
                filtro_ok and busq_ok and max(ms_f, ms_b) < UMBRAL_MS,
                f"Filtro LEVE {len(badges)}/{len(esperado)} filas en {ms_f:.0f} ms; búsqueda Palmayoc {len(com)}/{len(esperado2)} filas en {ms_b:.0f} ms.")


def rf05(pg, ev: Evidencias, base: str, tag: str, carpeta: Path):
    rf, n = "RF-05", "RF05"
    pre = f"{n}_{tag}"
    hoy = datetime.now(LIMA)
    desde, hasta = "2026-09-01", hoy.strftime("%Y-%m-%d")
    pg.goto(base)
    pg.get_by_test_id("tab-reporte").click()
    pg.fill("#desde", desde)
    pg.fill("#hasta", hasta)
    ev.foto(pg, rf, "Paso 1 · ENTRADA", f"{pre}_paso1_entrada.png",
            f"Pestaña «Reporte» con el periodo {desde} a {hasta} elegido, antes de pulsar «Generar».",
            "Periodo definido; el reporte aún no se ha generado.", principal=False, full=False)

    def generar():
        pg.get_by_test_id("generar-reporte").click()
        pg.get_by_test_id("kpi-registrados").wait_for()
    ms = cronometrar(generar)
    ev.tiempo(rf, "clic en «Generar» → reporte visible", ms)
    kpi = pg.get_by_test_id("kpi-registrados").inner_text()
    ev.foto(pg, rf, "Paso 2 · RESULTADO (reporte en pantalla)", f"{pre}_paso2_resultado.png",
            "Reporte del periodo: indicadores (niños registrados, evaluaciones, evaluados, % con anemia), barras por clasificación y tabla por comunidad.",
            f"{kpi} niños registrados en el periodo; reporte generado en {ms:.0f} ms.", principal=True)
    api_url = f"/api/reportes/periodo?desde={desde}&hasta={hasta}"
    jr = httpx.get(base + api_url)
    datos = jr.json()
    ui_ok = int(kpi) == datos["ninos_registrados"]
    # JSON en el navegador
    pg.goto(base + api_url)
    pg.wait_for_load_state()
    ev.foto(pg, rf, "Paso 3 · RESULTADO (JSON)", f"{pre}_paso3_json.png",
            "Respuesta JSON del servicio GET /api/reportes/periodo abierta en el navegador.",
            f"HTTP {jr.status_code}, application/json; ninos_registrados={datos['ninos_registrados']}, "
            f"evaluaciones_realizadas={datos['evaluaciones_realizadas']}.", principal=False, full=True)
    # CSV: descarga real desde la interfaz
    pg.goto(base)
    pg.get_by_test_id("tab-reporte").click()
    pg.fill("#desde", desde)
    pg.fill("#hasta", hasta)
    pg.get_by_test_id("generar-reporte").click()
    pg.get_by_test_id("kpi-registrados").wait_for()
    t0 = time.perf_counter()
    with pg.expect_download() as dl:
        pg.get_by_test_id("descargar-csv").click()
    descarga = dl.value
    destino = carpeta / f"{pre}_reporte_descargado.csv"
    descarga.save_as(str(destino))
    ms_csv = (time.perf_counter() - t0) * 1000
    ev.tiempo(rf, "clic en «Descargar CSV» → archivo descargado", ms_csv)
    contenido = destino.read_text("utf-8-sig")
    filas = list(csv.reader(io.StringIO(contenido)))
    cab = "".join(f"<th>{html.escape(c)}</th>" for c in filas[0])
    cuerpo = "".join("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in f) + "</tr>" for f in filas[1:])
    pg.set_content(f"""<!doctype html><meta charset=utf-8><title>CSV descargado</title>
      <body style="font:13px system-ui;margin:16px 16px 40px">
      <h2 style="margin:0 0 4px">Archivo CSV descargado desde «Descargar CSV» (renderizado)</h2>
      <p style="margin:0 0 10px;color:#444">Nombre sugerido por el servidor: <b>{html.escape(descarga.suggested_filename)}</b> ·
      {len(filas) - 1} fila(s) de datos · {len(contenido.encode())} bytes · tiempo hasta completar la descarga: {ms_csv:.0f} ms</p>
      <table border=1 cellspacing=0 cellpadding=4 style="border-collapse:collapse;font:12px monospace"><thead style="background:#e8eef5">
      <tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table></body>""")
    ev.foto(pg, rf, "Paso 4 · RESULTADO (CSV descargado)", f"{pre}_paso4_csv.png",
            "Contenido del archivo CSV generado y descargado desde el botón «Descargar CSV», renderizado en una página simple.",
            f"Archivo «{descarga.suggested_filename}» con {len(filas) - 1} fila(s) y cabecera de {len(filas[0])} columnas.",
            principal=False, url_texto=f"archivo descargado: {descarga.suggested_filename} (origen {api_url}&formato=csv)")
    cabeceras = httpx.get(base + api_url + "&formato=csv").headers
    csv_ok = len(filas) - 1 == datos["evaluaciones_realizadas"] and "csv" in cabeceras.get("content-type", "")
    ev.criterio(rf, "Dado un periodo válido, cuando se pulsa «Generar», entonces se muestran los indicadores del periodo "
                    "(JSON) y se puede descargar el mismo conjunto como CSV, en < 2 s.",
                ui_ok and csv_ok and max(ms, ms_csv) < UMBRAL_MS,
                f"Reporte en pantalla {ms:.0f} ms (KPI {kpi} = API {datos['ninos_registrados']}); CSV {ms_csv:.0f} ms con "
                f"{len(filas) - 1} filas = evaluaciones_realizadas {datos['evaluaciones_realizadas']}; "
                f"Content-Type {cabeceras.get('content-type')}.")


# --------------------------------------------------------------------------------------------------------------------
# Flujos RF-06 y RF-07 (solo v1.5)
# --------------------------------------------------------------------------------------------------------------------
def abrir_por_dni(pg, dni):
    pg.get_by_test_id("tab-seguimiento").click()
    pg.get_by_test_id("buscar").fill(dni)
    pg.wait_for_function(  # la fila debe ser la del DNI buscado (no la del filtro anterior, hay antirrebote de 250 ms)
        "(d) => { const f = document.querySelectorAll('#cuerpo-seguimiento tr'); return f.length === 1 && f[0].innerText.includes(d); }",
        arg=dni)


def esperar_agenda(pg, dni):
    """Espera la agenda DEL niño pedido (evita leer la tabla del expediente anterior, que sigue en el DOM)."""
    pg.wait_for_function(
        "(d) => document.querySelector('[data-testid=expediente]').innerText.includes(d) "
        "&& document.querySelector('[data-testid=agenda-tabla]')", arg=dni)


def rf06(pg, ev: Evidencias, base: str, tag: str):
    rf, n = "RF-06", "RF06"
    pre = f"{n}_{tag}"
    DNI = "71000022"  # Ethan: anemia leve; C1M cumplido, C3M y DHx vencidos, C6M pendiente
    pg.goto(base)
    abrir_por_dni(pg, DNI)
    ev.foto(pg, rf, "Paso 1 · ENTRADA", f"{pre}_paso1_entrada.png",
            f"Pestaña «Seguimiento» con el niño sintético DNI {DNI} (anemia leve en tratamiento) localizado; se abrirá su expediente.",
            "Fila del niño visible con su clasificación y la marca de controles vencidos.", principal=False, full=False)

    def abrir():
        pg.locator("#cuerpo-seguimiento tr").first.click()
        esperar_agenda(pg, DNI)
    ms = cronometrar(abrir)
    ev.tiempo(rf, "clic en el niño → expediente con agenda calculada", ms)
    pg.get_by_test_id("agenda-seccion").scroll_into_view_if_needed()
    estados = pg.locator("[data-testid=agenda-tabla] tbody tr").evaluate_all("rs => rs.map(r => r.dataset.estado)")
    resumen = pg.get_by_test_id("agenda-resumen").inner_text().replace("\n", " · ")
    conteo = {e: estados.count(e) for e in sorted(set(estados))}
    ev.foto(pg, rf, "Paso 2 · RESULTADO (agenda del expediente)", f"{pre}_paso2_resultado.png",
            "Sección «Agenda de controles» del expediente: lista de controles por edad y de tratamiento con fecha programada, "
            "ventana de cumplimiento y estado (cumplido, pendiente, próximo a vencer, vencido).",
            f"{len(estados)} controles; estados {conteo}. Resumen: {resumen}", principal=True)
    api = httpx.get(f"{base}/api/ninos/dni/{DNI}").json()
    ag = httpx.get(f"{base}/api/ninos/{api['id']}/agenda").json()
    api_estados = [("PROXIMO" if c["estado"] == "PENDIENTE" and c.get("proximo") else c["estado"]) for c in ag["controles"]]
    coincide = api_estados == estados
    hay = {"CUMPLIDO", "PENDIENTE", "VENCIDO"} <= set(estados)
    # Caso adicional: próximo a vencer
    abrir_por_dni(pg, "71000003")
    pg.locator("#cuerpo-seguimiento tr").first.click()
    esperar_agenda(pg, "71000003")
    pg.get_by_test_id("agenda-seccion").scroll_into_view_if_needed()
    prox = pg.locator("[data-testid=agenda-tabla] tr[data-estado=PROXIMO]").count()
    ev.foto(pg, rf, "Paso 3 · RESULTADO (control próximo a vencer)", f"{pre}_paso3_proximo_a_vencer.png",
            "Agenda de otro niño sintético con anemia moderada (DNI 71000003) con un control en estado «Próximo a vencer» (los datos de prueba no traen un niño con los cuatro estados a la vez).",
            f"{prox} control(es) en estado «Próximo a vencer»; resumen «{pg.get_by_test_id('agenda-proximos').inner_text()}».",
            principal=False)
    ev.criterio(rf, "Dado un niño con anemia en tratamiento, cuando se abre su expediente, entonces el sistema muestra la agenda "
                    "normativa de controles con el estado de cada uno (cumplido/pendiente/próximo/vencido) en < 2 s.",
                coincide and hay and prox >= 1 and ms < UMBRAL_MS,
                f"DNI {DNI}: {len(estados)} controles, estados {conteo} (UI = API: {coincide}); DNI 71000003 (anemia moderada) con {prox} próximo(s); ningún niño sintético reúne los 4 estados a la vez, por eso se usan 2 niños; "
                f"agenda en {ms:.0f} ms.")


def rf07(pg, ev: Evidencias, base: str, tag: str):
    rf, n = "RF-07", "RF07"
    pre = f"{n}_{tag}"
    pg.goto(base)

    def abrir():
        pg.get_by_test_id("tab-alertas").click()
        pg.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
    ms = cronometrar(abrir)
    ev.tiempo(rf, "clic en pestaña «Alertas» → resumen + tabla", ms)
    resumen = httpx.get(f"{base}/api/alertas/resumen").json()
    todas = httpx.get(f"{base}/api/alertas/controles-vencidos").json()
    kv = pg.get_by_test_id("kpi-vencidos").inner_text()
    ev.foto(pg, rf, "Paso 1 · ENTRADA (alertas sin filtro)", f"{pre}_paso1_entrada.png",
            "Pestaña «Alertas» con el resumen (vencidos, niños, prioridad alta/media/baja, por vencer en 7 días) y la tabla completa, "
            "antes de aplicar filtros; la insignia de la cabecera muestra el total de vencidos.",
            f"{kv} controles vencidos, {len(todas)} alertas ordenadas por prioridad; carga en {ms:.0f} ms.", principal=False)
    # filtro prioridad
    esperado = [a for a in todas if a["prioridad"] == "ALTA"]

    def filtrar_prio():
        pg.get_by_test_id("filtro-alerta-prioridad").select_option("ALTA")
        pg.wait_for_function("([p, n]) => { const f = [...document.querySelectorAll('[data-testid=alertas-tabla] tbody tr')];"
                             " return f.length === n && f.every((x) => x.dataset.prioridad === p); }", arg=["ALTA", len(esperado)])
    ms_p = cronometrar(filtrar_prio)
    ev.tiempo(rf, "filtro prioridad «Alta» → tabla filtrada", ms_p)
    ev.foto(pg, rf, "Paso 2 · RESULTADO (filtro por prioridad ALTA)", f"{pre}_paso2_resultado_filtro_prioridad.png",
            "Filtro «Prioridad: Alta» aplicado: la tabla muestra solo alertas de prioridad alta (control de tratamiento vencido, clasificación moderada/severa o más de 30 días de atraso).",
            f"{len(esperado)} alerta(s) ALTA de {len(todas)}; coincide con la API.", principal=True)
    # filtro comunidad
    pg.get_by_test_id("filtro-alerta-prioridad").select_option("")
    pg.wait_for_function(f"document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length === {len(todas)}")
    com = "Huaycha"
    esp_c = [a for a in todas if a["nino"]["comunidad"] == com]

    def filtrar_com():
        pg.get_by_test_id("filtro-alerta-comunidad").select_option(com)
        pg.wait_for_function(f"document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length === {len(esp_c)}")
    ms_c = cronometrar(filtrar_com)
    ev.tiempo(rf, "filtro comunidad «Huaycha» → tabla filtrada", ms_c)
    comunidades = pg.locator("[data-testid=alertas-tabla] tbody tr td:nth-child(6)").all_inner_texts()
    ev.foto(pg, rf, "Paso 3 · RESULTADO (filtro por comunidad)", f"{pre}_paso3_resultado_filtro_comunidad.png",
            f"Filtro «Comunidad: {com}» aplicado: solo las alertas de esa comunidad.",
            f"{len(comunidades)} alerta(s), todas de {com}.", principal=False)
    ok_resumen = (kv == str(resumen["total_vencidos"]) and pg.evaluate("document.querySelector('[data-testid=insignia-alertas]').textContent")
                  == str(resumen["total_vencidos"]))
    ok = (ok_resumen and len(comunidades) == len(esp_c) and all(c == com for c in comunidades)
          and max(ms, ms_p, ms_c) < UMBRAL_MS)
    ev.criterio(rf, "Dado un conjunto de niños con controles, cuando se abre la pestaña «Alertas» y se filtra por prioridad o "
                    "comunidad, entonces se listan los controles vencidos priorizados con su resumen, en < 2 s.",
                ok, f"Resumen UI = API ({kv} vencidos); filtro ALTA {len(esperado)} filas en {ms_p:.0f} ms; comunidad {com} "
                    f"{len(comunidades)}/{len(esp_c)} filas en {ms_c:.0f} ms; pestaña en {ms:.0f} ms.")


# --------------------------------------------------------------------------------------------------------------------
# Árboles de carpetas y regresión
# --------------------------------------------------------------------------------------------------------------------
def arbol_texto(raiz: Path) -> str:
    lineas = [f"{raiz.name}/"]

    def rec(d: Path, prefijo: str):
        hijos = sorted([p for p in d.iterdir() if p.name != "__pycache__" and not p.name.endswith(".pyc")],
                       key=lambda p: (p.is_file(), p.name.lower()))
        for i, p in enumerate(hijos):
            ultimo = i == len(hijos) - 1
            lineas.append(f"{prefijo}{'└── ' if ultimo else '├── '}{p.name}{'/' if p.is_dir() else ''}")
            if p.is_dir():
                rec(p, prefijo + ("    " if ultimo else "│   "))
    rec(raiz, "")
    return "\n".join(lineas)


def modo_arquitectura(args):
    carpeta = SALIDA / "arquitectura"
    carpeta.mkdir(exist_ok=True)
    trabajos = [
        ("arbol_v1.0.png", "Árbol de app/ en v1.0-PMV", APP_V10 / "app", "v1.0-PMV",
         "contenido idéntico al tag v1.0-PMV (domain / application / adapters/entrada|salida)"),
        ("arbol_v1.5.png", "Árbol de app/ en v1.5.0-inc2-avance (rama de trabajo local)", APP_V15 / "app", "v1.5.0-inc2-avance",
         "árbol de trabajo local, por publicar en la rama feature/inc2-agenda-alertas (domain/model|service, ports/inbound|outbound, adapters/inbound|outbound)"),
    ]
    # rutas relativas al repositorio (no se imprimen rutas del contenedor)
    rutas_rel = {"v1.0-PMV": "app/ (tag v1.0-PMV)", "v1.5.0-inc2-avance": "pmv_fastapi/app/"}
    res = []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for archivo, titulo, raiz, version, nota in trabajos:
            pg = nav.new_page(viewport={"width": 1000, "height": 700})
            texto = arbol_texto(raiz)
            pg.set_content(f"""<!doctype html><meta charset=utf-8><title>{html.escape(titulo)}</title>
              <body style="margin:0;padding:24px 28px 56px;background:#fff;color:#111;font-family:system-ui">
              <h1 style="font-size:22px;margin:0 0 4px;color:#1F4E79">{html.escape(titulo)}</h1>
              <p style="margin:0 0 14px;color:#555;font-size:13px">Ruta relativa: {html.escape(rutas_rel[version])} · {html.escape(nota)} · se excluye __pycache__</p>
              <pre style="font:13px/1.45 'DejaVu Sans Mono',monospace;background:#f4f6f9;border:1px solid #cfd8e3;border-radius:6px;padding:14px 18px;margin:0">{html.escape(texto)}</pre></body>""")
            ev_tmp = Evidencias("arquitectura", version, carpeta, False)
            ev_tmp.foto(pg, "Arquitectura", f"Árbol de carpetas app/ ({version})", archivo, titulo,
                        f"Árbol de {rutas_rel[version]}", url_texto=rutas_rel[version])
            res.extend(ev_tmp.capturas)
            pg.close()
        nav.close()
    ev = Evidencias("arquitectura", "-", carpeta, False)
    ev.capturas = res
    ev.guardar_json()


def intentar_github(args):
    """Intento no bloqueante de capturar la estructura del tag v1.0-PMV en GitHub."""
    url = "https://github.com/woshtsu/ProcesosSoftwareAnemia/tree/v1.0-PMV/app"
    carpeta = SALIDA / "arquitectura"
    carpeta.mkdir(exist_ok=True)
    resultado = {"url": url, "exito": False, "detalle": ""}
    try:
        ca = os.environ.get('SSL_CERT_FILE') or ('/root/.ccr/ca-bundle.crt' if Path('/root/.ccr/ca-bundle.crt').exists() else True)
        r = httpx.get(url, timeout=20, follow_redirects=True, verify=ca)
        resultado["detalle"] = f"HTTP {r.status_code}" + (f" · {r.text[:160]}" if r.status_code != 200 else "")
        if r.status_code == 200:
            with sync_playwright() as p:
                nav = p.chromium.launch()
                pg = nav.new_page(viewport=VIEWPORT)
                pg.goto(url, timeout=30000)
                pg.wait_for_load_state("networkidle", timeout=30000)
                Evidencias("arquitectura", "v1.0-PMV", carpeta, False).foto(
                    pg, "Arquitectura", "GitHub tag v1.0-PMV", "github_v1.0-PMV_app.png", "GitHub", "estructura app/", full=False)
                nav.close()
            resultado["exito"] = True
    except Exception as e:  # noqa: BLE001
        resultado["detalle"] = f"{type(e).__name__}: {str(e)[:200]}"
    (SALIDA / "resultados_github.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), "utf-8")
    print("[github]", resultado)


# --------------------------------------------------------------------------------------------------------------------
# Ejecución por modo
# --------------------------------------------------------------------------------------------------------------------
def ejecutar_flujos(args, modo, flujos, version, tag, carpeta, solo_principales, viewport=VIEWPORT):
    app_dir = Path(args.app_dir)
    db = Path(args.db) if args.db else app_dir / "datos" / "s9_capturas.db"
    ev = Evidencias(modo, version, carpeta, solo_principales)
    srv = None if args.sin_servidor else Servidor(app_dir, db, args.puerto, reiniciar_flag=(modo != "inc1"))
    contexto = srv if srv else _Nulo(f"http://127.0.0.1:{args.puerto}")
    with contexto as s, sync_playwright() as p:
        print(f"== {modo} · {version} · {s.url}")
        nav = p.chromium.launch()
        for nombre, fn in flujos:
            ctx = nav.new_context(viewport=viewport, locale="es-PE", timezone_id="America/Lima", accept_downloads=True)
            pg = ctx.new_page()
            errores = []
            pg.on("pageerror", lambda e: errores.append(str(e)))
            # los 422 son respuestas esperadas de las pruebas de rechazo (RF-03), no defectos
            pg.on("console", lambda m: errores.append(m.text) if m.type == "error" and "422" not in m.text else None)
            print(f"-- {nombre}")
            try:
                if fn is rf05:
                    fn(pg, ev, s.url, tag, carpeta)
                else:
                    fn(pg, ev, s.url, tag)
            except Exception as e:  # noqa: BLE001
                ev.hallazgo(f"{nombre.upper()}: la ejecución del flujo falló: {type(e).__name__}: {str(e)[:300]}")
                ev.criterios.setdefault(nombre.upper().replace("RF", "RF-"), {"gwt": "(flujo interrumpido)", "cumple": False, "detalle": str(e)[:300]})
            if errores:
                ev.hallazgo(f"{nombre.upper()}: errores de consola/JS durante el flujo: {errores[:3]}")
            ctx.close()
        nav.close()
    ev.guardar_json()
    return ev


class _Nulo:
    def __init__(self, url):
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


ETIQ_INC = {"inc1": "Inc. 1 (v1.0-PMV)", "inc2": "Inc. 2 (v1.5)", "regresion": "Regresión Inc. 1 en v1.5", "arquitectura": "Arquitectura"}


def modo_indice(args):
    archivos = ["inc1", "inc2", "regresion", "arquitectura"]
    datos = {m: json.loads((SALIDA / f"resultados_{m}.json").read_text("utf-8")) for m in archivos if (SALIDA / f"resultados_{m}.json").exists()}
    L = ["# Índice de evidencias visuales (Actividad 5, guía S9)", "",
         "Capturas reales del software en ejecución (Chromium headless / Playwright, viewport 1366x900) con **datos 100 % sintéticos**. "
         "Cada captura incluye un pie de «Evidencia S9» inyectado por el script (RF, paso, URL, versión, fecha-hora de Perú); "
         "no altera la funcionalidad. Script reproducible: `capturar_evidencias.py`.", ""]
    nombres = {"inc1": "Incremento 1 · v1.0-PMV (RF-01 a RF-05)", "inc2": "Incremento 2 · v1.5.0-inc2-avance (RF-06 y RF-07)",
               "regresion": "Regresión visual · RF-01 a RF-05 ejecutados en v1.5.0-inc2-avance", "arquitectura": "Arquitectura · árboles de app/"}
    for m, d in datos.items():
        L += [f"## {nombres[m]}", "", f"Versión: `{d['version']}` · generado: {d['generado']}", ""]
        if d.get("criterios"):
            L += ["### Criterio de aceptación y tiempo de respuesta", "",
                  "| RF | Criterio (Dado-Cuando-Entonces) | Cumple | Observación | Tiempos medidos (ms) |", "|---|---|---|---|---|"]
            for rf, c in d["criterios"].items():
                t = "; ".join(f"{x['accion']}: **{x['ms']}**" for x in d["tiempos"] if x["rf"] == rf)
                L.append(f"| {rf} | {c['gwt']} | {'Sí' if c['cumple'] else '**No**'} | {c['detalle']} | {t} |")
            L.append("")
        L += ["### Capturas", "", "| Archivo | RF | Incremento | Paso | Descripción | Fecha-hora (Perú) | URL | Resultado observado |", "|---|---|---|---|---|---|---|---|"]
        for c in d["capturas"]:
            L.append(f"| `{c['archivo']}` | {c['rf']} | {ETIQ_INC.get(c['incremento'], c['incremento'])} | {c['paso']} | {c['descripcion']} | {c['fecha_hora']} | {c['url']} | {c['resultado_observado']} |")
        L.append("")
        if d.get("hallazgos"):
            L += ["### Hallazgos durante la captura", ""] + [f"- {h}" for h in d["hallazgos"]] + [""]
    gh = SALIDA / "resultados_github.json"
    if gh.exists():
        g = json.loads(gh.read_text("utf-8"))
        L += ["## Intento de captura en GitHub (opcional)", "", f"- URL: {g['url']}", f"- Éxito: {'sí' if g['exito'] else 'no'}", f"- Detalle: {g['detalle']}", ""]
    (SALIDA / "INDICE.md").write_text("\n".join(L), "utf-8")
    print("INDICE.md generado")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modo", required=True, choices=["inc1", "inc2", "regresion", "arquitectura", "indice", "github"])
    ap.add_argument("--app-dir", help="carpeta raíz de la app (por defecto según el modo)")
    ap.add_argument("--puerto", type=int, help="puerto (por defecto 8101 para inc1, 8102 para inc2/regresion)")
    ap.add_argument("--db", help="ruta de la base SQLite (por defecto <app-dir>/datos/s9_capturas.db)")
    ap.add_argument("--version-etiqueta", help="etiqueta de versión para el pie de evidencia")
    ap.add_argument("--sin-servidor", action="store_true", help="no levantar servidor: usar uno ya activo en --puerto")
    args = ap.parse_args()

    if args.modo == "arquitectura":
        return modo_arquitectura(args)
    if args.modo == "github":
        return intentar_github(args)
    if args.modo == "indice":
        return modo_indice(args)
    if args.modo == "inc1":
        args.app_dir = args.app_dir or str(APP_V10)
        args.puerto = args.puerto or 8101
        ejecutar_flujos(args, "inc1", [("rf01", rf01), ("rf02", rf02), ("rf03", rf03), ("rf04", rf04), ("rf05", rf05)],
                        args.version_etiqueta or "v1.0-PMV", "inc1", SALIDA / "inc1", False)
    elif args.modo == "inc2":
        args.app_dir = args.app_dir or str(APP_V15)
        args.puerto = args.puerto or 8102
        ejecutar_flujos(args, "inc2", [("rf06", rf06), ("rf07", rf07)],
                        args.version_etiqueta or "v1.5.0-inc2-avance", "inc2", SALIDA / "inc2", False)
    elif args.modo == "regresion":
        args.app_dir = args.app_dir or str(APP_V15)
        args.puerto = args.puerto or 8102
        ejecutar_flujos(args, "regresion", [("rf01", rf01), ("rf02", rf02), ("rf03", rf03), ("rf04", rf04), ("rf05", rf05)],
                        args.version_etiqueta or "v1.5.0-inc2-avance", "v15_regresion", SALIDA / "regresion_v1.5", True)


if __name__ == "__main__":
    main()
