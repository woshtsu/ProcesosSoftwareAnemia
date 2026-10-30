#!/usr/bin/env python
"""Captura de evidencias visuales (Actividad 5, guía S9) con Chromium headless (Playwright).

Ejecuta el software REAL (servidor uvicorn + base SQLite propia + datos sintéticos) y fotografía cada paso de los
requerimientos funcionales. Es reproducible y se parametriza por versión, puerto y rutas.

Modos (--modo):
  inc1          RF-01..RF-05 sobre la v1.0-PMV                -> evidencias_capturas/inc1/
  inc2          RF-06 y RF-07 sobre la v1.5                    -> evidencias_capturas/inc2/
  regresion     RF-01..RF-05 sobre la v1.5 (una captura por RF) -> evidencias_capturas/regresion_v1.5/
  inc2final     RF-08 y RF-09 sobre la v2.0.0-inc2 (cierre del Inc. 2) con la muestra de 500 niños de la DIRESA Junín
                (FECHA_REFERENCIA=2024-06-30) y registros de prueba de origen SISTEMA -> RF-08/, RF-09/ y datos_reales/
  arquitectura  árbol de app/ de ambas versiones (HTML monoespaciado -> PNG) -> evidencias_capturas/arquitectura/
  indice        genera INDICE.md a partir de los resultados_*.json

Uso (desde cualquier carpeta; el intérprete debe tener playwright instalado):
  python capturar_evidencias.py --modo inc1   (si hace falta, PLAYWRIGHT_BROWSERS_PATH apunta a los navegadores de Playwright)
  ... --modo inc2 ; --modo regresion ; --modo inc2final ; --modo arquitectura ; --modo indice
Parámetros: --app-dir, --puerto, --db, --version-etiqueta, --con-registros-sistema, --sin-servidor (usa un servidor ya levantado).

MARCA DE EVIDENCIA: antes de cada captura se inyecta en la página un pie fijo (position:fixed) con RF, paso, URL,
versión, fecha-hora de Perú y la leyenda de los datos («datos sintéticos»; en inc2final «datos: muestra DIRESA Junín + registros
de prueba»). No altera la funcionalidad; se declara en el informe.
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


class ServidorDataset(Servidor):
    """Base de demostración del cierre del Inc. 2: muestra estratificada de 500 niños del dataset de la DIRESA Junín
    (semilla 2026) + registros de prueba de origen SISTEMA, servida con FECHA_REFERENCIA=2024-06-30 (corte del dataset)."""

    FECHA_REFERENCIA = "2024-06-30"

    def __init__(self, app_dir: Path, db: Path, puerto: int, registros_sistema: int = 3, muestra: int = 500, semilla: int = 2026):
        super().__init__(app_dir, db, puerto, reiniciar_flag=True)
        self.registros_sistema, self.muestra, self.semilla = registros_sistema, muestra, semilla

    def __enter__(self):
        self.db.parent.mkdir(parents=True, exist_ok=True)
        for sufijo in ("", "-wal", "-shm", "-journal"):
            Path(str(self.db) + sufijo).unlink(missing_ok=True)
        entorno = {**os.environ, "DATABASE_URL": f"sqlite:///{self.db}", "FECHA_REFERENCIA": self.FECHA_REFERENCIA}
        orden = [sys.executable, "-m", "scripts.importar_dataset_diresa", "--muestra", str(self.muestra), "--semilla", str(self.semilla),
                 "--reiniciar", "--con-registros-sistema", str(self.registros_sistema)]
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


# --------------------------------------------------------------------------------------------------------------------
# Registro de resultados
# --------------------------------------------------------------------------------------------------------------------
class Evidencias:
    def __init__(self, modo, version, carpeta: Path, solo_principales: bool, leyenda="datos sintéticos", archivo_relativo=False):
        self.modo, self.version, self.carpeta, self.solo_principales = modo, version, carpeta, solo_principales
        self.leyenda = leyenda
        self.archivo_relativo = archivo_relativo  # True: `nombre` ya incluye la subcarpeta (RF-08/...) y se registra tal cual
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self.capturas: list[dict] = []
        self.tiempos: list[dict] = []
        self.criterios: dict[str, dict] = {}
        self.hallazgos: list[str] = []

    def marca(self, pg, rf, paso, url_texto=None):
        texto = (f"Evidencia S9 · {rf} · {paso} · {url_texto or pg.url} · {self.version} · "
                 f"{ahora()} · {self.leyenda}")
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
        ruta.parent.mkdir(parents=True, exist_ok=True)
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
            "archivo": nombre if self.archivo_relativo else f"{self.carpeta.name}/{nombre}", "rf": rf, "incremento": self.modo, "paso": paso,
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
# Flujos del cierre del Inc. 2 (v2.0.0-inc2): RF-08, RF-09 y datos reales (muestra DIRESA Junín, FECHA_REFERENCIA=2024-06-30)
# --------------------------------------------------------------------------------------------------------------------
FECHA_CORTE = "2024-06-30"
LEYENDA_INC2_FINAL = "datos: muestra DIRESA Junín + registros de prueba"
MOTIVO_NO_ASISTIO = "Enfermedad del niño"
DETALLE_NO_ASISTIO = "Fiebre desde hace 2 días"


def ir_a_expediente(pg, clave):
    """Abre el expediente desde la pestaña «Expediente» (por DNI o por código DJ-xxxxx) y espera su agenda."""
    pg.get_by_test_id("tab-expediente").click()
    pg.get_by_test_id("buscar-dni").fill(clave)
    pg.get_by_role("button", name="Abrir").click()
    pg.wait_for_function(
        "(c) => { const e = document.querySelector('[data-testid=expediente]');"
        " return e && e.innerText.toLowerCase().includes(c.toLowerCase()) && document.querySelector('[data-testid=agenda-tabla]'); }",
        arg=clave)


def clave_de(nino):
    return nino["dni"] or nino["codigo_origen"]


def fila_control(pg, codigo, programada):
    return pg.locator(f'[data-testid="agenda-tabla"] tr[data-codigo="{codigo}"][data-programada="{programada}"]')


def agenda_api(base, nino_id):
    return httpx.get(f"{base}/api/ninos/{nino_id}/agenda").json()


def consultar_rango(pg, desde, hasta):
    pg.get_by_test_id("agenda-desde").fill(desde)
    pg.get_by_test_id("agenda-hasta").fill(hasta)
    pg.get_by_test_id("agenda-consultar").click()
    pg.wait_for_function(
        "([d, h]) => document.querySelector('#agenda-desde').value === d && document.querySelector('#agenda-hasta').value === h"
        " && document.querySelector('[data-testid=agenda-personal-resumen]').textContent.includes('Del ' + d.split('-').reverse().join('/'))",
        arg=[desde, hasta])


def rf08(pg, ev: Evidencias, base: str, tag: str):
    rf, n = "RF-08", "RF08"
    pre = f"{n}_{tag}"
    carpeta = "RF-08"
    pg.goto(base)
    pg.get_by_test_id("tab-agenda").click()
    pg.get_by_test_id("agenda-personal-tabla").wait_for()
    pg.wait_for_function("document.querySelectorAll('[data-testid=agenda-personal-dia]').length === 7")
    desde, hasta = "2024-05-30", "2024-06-02"
    n_dias = 4
    # Paso 1: el personal escribe el rango (jueves a domingo) antes de pulsar «Consultar»; la tabla aún es la de la semana por defecto.
    pg.get_by_test_id("agenda-desde").fill(desde)
    pg.get_by_test_id("agenda-hasta").fill(hasta)
    ev.foto(pg, rf, "Paso 1 · ENTRADA (rango y filtros de la agenda)", f"{carpeta}/{pre}_paso1_entrada.png",
            f"Pestaña «Agenda» (aviso «Fecha de referencia: 30/06/2024 (corte del dataset)» en la cabecera) con el rango escrito {desde} a {hasta} "
            f"({n_dias} días; el máximo permitido es 31) y los filtros «Establecimiento» y «Comunidad» en «Todos/Todas», antes de pulsar «Consultar». "
            "Mientras no se consulta, la tabla inferior sigue mostrando la semana por defecto (24 al 30 de junio).",
            f"Campos Desde = {desde} y Hasta = {hasta}; botones «Consultar», «Anterior» y «Siguiente» visibles; filtros sin aplicar.",
            principal=False, full=False)

    def consultar():
        consultar_rango(pg, desde, hasta)
    ms = cronometrar(consultar)
    ev.tiempo(rf, f"clic en «Consultar» (rango {desde} a {hasta}) → agenda por día con totales", ms)
    api = httpx.get(f"{base}/api/agenda", params={"desde": desde, "hasta": hasta}).json()
    r = api["resumen"]
    filas = pg.locator("[data-testid=agenda-personal-tabla] tr[data-codigo]").count()
    dias_ui = pg.get_by_test_id("agenda-personal-dia").count()
    totales_ui = pg.get_by_test_id("agenda-personal-dia-total").all_inner_texts()
    totales_api = [f"{d['total']} control(es)" + (f" · {d['cumplidos']} cumplidos · {d['pendientes']} pendientes · {d['vencidos']} vencidos" if d["total"] else "")
                   for d in api["dias"]]
    resumen_ui = pg.get_by_test_id("agenda-personal-total").inner_text()
    pg.evaluate("window.scrollTo(0, 0)")
    alto = pg.evaluate("document.documentElement.scrollHeight")
    ev.foto(pg, rf, "Paso 2 · RESULTADO (agenda por día con totales)", f"{carpeta}/{pre}_paso2_resultado.png",
            f"Agenda del personal del {desde} al {hasta}: resumen del rango (programados, cumplidos, pendientes, vencidos, con inasistencia) y, "
            "por cada día, el total de controles y el desglose por estado, con la tabla de niños (código del registro, control, tipo, establecimiento, estado).",
            f"{r['total']} controles de {r['ninos']} niño(s) en {len(api['dias'])} días; {r['cumplidos']} cumplidos, {r['pendientes']} pendientes, {r['vencidos']} vencidos, "
            f"{r['con_inasistencia']} con inasistencia; UI: «{resumen_ui}», {filas} filas; consulta en {ms:.0f} ms.",
            principal=True, full=alto <= 4500)
    coincide_dias = totales_ui == totales_api and dias_ui == len(api["dias"])
    # Paso 3: filtro por establecimiento (el de más controles del rango)
    por_est = {}
    for d in api["dias"]:
        for i in d["items"]:
            por_est[i["nino"]["establecimiento"]] = por_est.get(i["nino"]["establecimiento"], 0) + 1
    est = max(sorted(por_est), key=lambda k: por_est[k])
    esperado = httpx.get(f"{base}/api/agenda", params={"desde": desde, "hasta": hasta, "establecimiento": est}).json()
    re_ = esperado["resumen"]

    def filtrar():
        pg.get_by_test_id("filtro-agenda-establecimiento").select_option(est)
        pg.wait_for_function(
            "(n) => document.querySelectorAll('[data-testid=agenda-personal-tabla] tr[data-codigo]').length === n"
            " && document.querySelector('#filtro-agenda-establecimiento').value !== ''", arg=re_["total"])
    ms_f = cronometrar(filtrar)
    ev.tiempo(rf, "filtro «Establecimiento» → agenda filtrada", ms_f)
    celdas = pg.locator("[data-testid=agenda-personal-tabla] tr[data-codigo] td:nth-child(4)").all_inner_texts()
    solo_est = bool(celdas) and all(est in c for c in celdas)
    pg.evaluate("window.scrollTo(0, 0)")
    alto = pg.evaluate("document.documentElement.scrollHeight")
    ev.foto(pg, rf, "Paso 3 · RESULTADO (filtro por establecimiento)", f"{carpeta}/{pre}_paso3_resultado_filtro_establecimiento.png",
            f"El mismo rango con el filtro «Establecimiento: {est}»: solo se listan los controles de ese establecimiento y los totales se recalculan.",
            f"{re_['total']} controles de {re_['ninos']} niño(s) (de {r['total']} del rango completo); todas las filas son de {est}: {solo_est}; filtro en {ms_f:.0f} ms.",
            principal=False, full=alto <= 4500)
    ev.criterio(rf, "Dado un conjunto de controles programados, cuando el personal consulta la agenda de un rango (máx. 31 días) y filtra por "
                    "establecimiento o comunidad, entonces se listan los controles por día con el total y el desglose por estado, coherentes con la API, en < 2 s.",
                coincide_dias and filas == r["total"] and resumen_ui == f"{r['total']} programados" and solo_est
                and len(celdas) == re_["total"] and max(ms, ms_f) < UMBRAL_MS,
                f"Rango {desde} a {hasta}: UI = API ({r['total']} controles, {len(api['dias'])} días, totales por día idénticos: {coincide_dias}); "
                f"filtro «{est}»: {re_['total']}/{r['total']} filas, todas del establecimiento; consulta {ms:.0f} ms y filtro {ms_f:.0f} ms.")


def elegir_objetivos_rf09(base):
    """Elige, con la API, los controles de la demostración de RF-09 (determinista: orden de la API). Los registros de prueba de
    origen SISTEMA solo tienen controles futuros (no se puede registrar asistencia), así que se usan registros del dataset.
    A: control PENDIENTE ya programado (fecha <= fecha de referencia) de un registro del dataset, para «Asistió».
    B: control vencido de prioridad BAJA (o MEDIA), para «No asistió» con motivo y subida de prioridad.
    C: otro control vencido de otro niño, para mostrar el 409 de un segundo registro."""
    semana = httpx.get(f"{base}/api/agenda", params={"desde": "2024-06-17", "hasta": FECHA_CORTE}).json()
    a = None
    for d in semana["dias"]:
        for i in d["items"]:
            c = i["control"]
            if c["estado"] == "PENDIENTE" and c["fecha_programada"] <= FECHA_CORTE and not c["inasistencia_registrada"] and i["nino"]["codigo_origen"]:
                a = (i["nino"], c)
                break
        if a:
            break
    alertas = httpx.get(f"{base}/api/alertas/controles-vencidos").json()
    libres = [x for x in alertas if not a or x["nino"]["id"] != a[0]["id"]]
    pref = [x for x in libres if x["prioridad"] == "BAJA"] or [x for x in libres if x["prioridad"] == "MEDIA"]
    b = pref[0] if pref else None
    c = next((x for x in pref[1:] if x["nino"]["id"] != b["nino"]["id"]), None) if b else None
    return a, b, c


def prioridad_actual(base, nino_id, codigo):
    for f in httpx.get(f"{base}/api/alertas/controles-vencidos").json():
        if f["nino"]["id"] == nino_id and f["control"]["codigo"] == codigo:
            return f["prioridad"]
    return None


def rf09(pg, ev: Evidencias, base: str, tag: str):
    rf, n = "RF-09", "RF09"
    pre = f"{n}_{tag}"
    carpeta = "RF-09"
    a, b, c = elegir_objetivos_rf09(base)
    if not (a and b and c):
        raise RuntimeError(f"No hay controles aptos para RF-09 (A={bool(a)}, B={bool(b)}, C={bool(c)})")
    nino_a, ctrl_a = a
    pg.goto(base)
    # ---- Paso 1: modal «Asistió» con datos ----
    ir_a_expediente(pg, clave_de(nino_a))
    fila = fila_control(pg, ctrl_a["codigo"], ctrl_a["fecha_programada"])
    fila.wait_for()
    fila.get_by_test_id("btn-asistio").scroll_into_view_if_needed()
    estado_antes = fila.get_by_test_id("estado-control").get_attribute("data-estado")
    fila.get_by_test_id("btn-asistio").click()
    modal = pg.get_by_test_id("modal-asistencia")
    modal.wait_for()
    pg.wait_for_function("document.querySelectorAll('#asistencia-evaluacion option').length >= 2")
    detalle = pg.locator("#modal-detalle").inner_text()
    n_opciones = pg.locator("#asistencia-evaluacion option").count() - 1
    vinculada = pg.get_by_test_id("asistencia-evaluacion").locator("option:checked").inner_text()  # por defecto: sin evaluación vinculada
    ev.foto(pg, rf, "Paso 1 · ENTRADA (registrar asistencia)", f"{carpeta}/{pre}_paso1_entrada.png",
            "Cuadro «Registrar asistencia» abierto desde la agenda del expediente de un registro del dataset anonimizado de la DIRESA Junín: muestra el niño, el control y la fecha "
            f"programada, y permite vincular una evaluación (opcional, {n_opciones} disponible(s)) antes de confirmar.",
            f"Detalle: «{detalle}»; evaluación vinculada: «{vinculada}»; estado del control antes: {estado_antes}.", principal=False, full=True)

    def registrar_asistio():
        pg.get_by_test_id("asistencia-confirmar").click()
        pg.wait_for_function(
            "([c, p]) => { const f = document.querySelector(`[data-testid=agenda-tabla] tr[data-codigo='${c}'][data-programada='${p}']`);"
            " return f && f.dataset.estado === 'CUMPLIDO'; }", arg=[ctrl_a["codigo"], ctrl_a["fecha_programada"]])
    ms_a = cronometrar(registrar_asistio)
    ev.tiempo(rf, "«Asistió» → confirmar → control «Cumplido» en la agenda", ms_a)
    fila = fila_control(pg, ctrl_a["codigo"], ctrl_a["fecha_programada"])
    texto_fila = fila.inner_text().replace("\n", " ")
    fila.scroll_into_view_if_needed()
    ev.foto(pg, rf, "Paso 2 · RESULTADO («Asistió»)", f"{carpeta}/{pre}_paso2_asistio.png",
            "Tras confirmar, el control pasa a «Cumplido (asistió)», deja de ofrecer los botones de asistencia y el resumen de la agenda se actualiza; aparece el aviso «Asistencia registrada».",
            f"Fila: «{texto_fila}». Estado antes: {estado_antes}; ahora CUMPLIDO; confirmación en {ms_a:.0f} ms.", principal=True, full=True)
    asist_a = httpx.get(f"{base}/api/ninos/{nino_a['id']}/asistencias").json()
    ok_a = any(x["codigo_control"] == ctrl_a["codigo"] and x["estado"] == "ASISTIO" for x in asist_a)
    ag_a = next(x for x in agenda_api(base, nino_a["id"])["controles"] if x["codigo"] == ctrl_a["codigo"] and x["fecha_programada"] == ctrl_a["fecha_programada"])
    cumplido_a = ag_a["estado"] == "CUMPLIDO" and ag_a.get("cumplido_por_asistencia") is True
    sin_alerta_a = prioridad_actual(base, nino_a["id"], ctrl_a["codigo"]) is None

    # ---- Paso 3: «No asistió» con motivo ----
    nino_b, ctrl_b = b["nino"], b["control"]
    prio_antes = b["prioridad"]
    pg.goto(base)
    ir_a_expediente(pg, clave_de(nino_b))
    fb = fila_control(pg, ctrl_b["codigo"], ctrl_b["fecha_programada"])
    fb.wait_for()
    fb.get_by_test_id("btn-no-asistio").click()
    pg.get_by_test_id("modal-asistencia").wait_for()
    pg.get_by_test_id("asistencia-motivo").select_option(MOTIVO_NO_ASISTIO)
    pg.get_by_test_id("asistencia-detalle").fill(DETALLE_NO_ASISTIO)

    def registrar_no_asistio():
        pg.get_by_test_id("asistencia-confirmar").click()
        pg.wait_for_function(
            "([c, p]) => { const f = document.querySelector(`[data-testid=agenda-tabla] tr[data-codigo='${c}'][data-programada='${p}']`);"
            " return f && f.querySelector('[data-testid=marca-inasistencia]'); }", arg=[ctrl_b["codigo"], ctrl_b["fecha_programada"]])
    ms_b = cronometrar(registrar_no_asistio)
    ev.tiempo(rf, "«No asistió» + motivo → confirmar → marca de inasistencia en la agenda", ms_b)
    fb = fila_control(pg, ctrl_b["codigo"], ctrl_b["fecha_programada"])
    marca = fb.get_by_test_id("marca-inasistencia").get_attribute("title")
    sigue_vencido = fb.get_by_test_id("estado-control").get_attribute("data-estado") == "VENCIDO"
    fb.scroll_into_view_if_needed()
    prio_despues = prioridad_actual(base, nino_b["id"], ctrl_b["codigo"])
    ev.foto(pg, rf, "Paso 3 · RESULTADO («No asistió» con motivo)", f"{carpeta}/{pre}_paso3_no_asistio.png",
            f"Control vencido de un registro del dataset marcado como «No asistió» con el motivo «{MOTIVO_NO_ASISTIO}: {DETALLE_NO_ASISTIO}»: la fila muestra la marca "
            "«Inasistencia registrada» (el motivo se ve al pasar el cursor) y el control sigue «Vencido» (no se da por cumplido).",
            f"Marca con motivo «{marca}»; el control sigue vencido: {sigue_vencido}; prioridad de la alerta {prio_antes} → {prio_despues}; registro en {ms_b:.0f} ms.",
            principal=True, full=True)
    # alerta de prioridad elevada
    pg.get_by_test_id("tab-alertas").click()
    pg.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
    pg.get_by_test_id("filtro-alerta-prioridad").select_option(prio_despues)
    pg.wait_for_function("(p) => { const f = [...document.querySelectorAll('[data-testid=alertas-tabla] tbody tr')]; return f.length > 0 && f.every((x) => x.dataset.prioridad === p); }", arg=prio_despues)
    comunidad_b = b["nino"]["comunidad"]  # se acota por comunidad para que la tabla quepa completa en la captura
    pg.get_by_test_id("filtro-alerta-comunidad").select_option(comunidad_b)
    pg.wait_for_function("(c) => { const f = [...document.querySelectorAll('[data-testid=alertas-tabla] tbody tr')]; return f.length > 0 && f.every((x) => x.cells[5].textContent.trim() === c); }", arg=comunidad_b)
    fila_alerta = pg.locator(f'[data-testid=alertas-tabla] tbody tr[data-id="{nino_b["id"]}"][data-codigo="{ctrl_b["codigo"]}"]')
    en_alertas = fila_alerta.count() == 1
    n_filas_alerta = pg.locator("[data-testid=alertas-tabla] tbody tr").count()
    marca_alerta = en_alertas and fila_alerta.get_by_test_id("marca-inasistencia").count() == 1
    ev.foto(pg, rf, "Paso 3b · RESULTADO (alerta con prioridad elevada)", f"{carpeta}/{pre}_paso3b_alerta_prioridad_elevada.png",
            f"Pestaña «Alertas» filtrada por prioridad {prio_despues} y comunidad {comunidad_b}: la alerta del control marcado como inasistencia aparece con la marca «Inasistencia registrada» y "
            f"con la prioridad subida un nivel ({prio_antes} → {prio_despues}).",
            f"Alerta presente: {en_alertas}; con marca de inasistencia: {marca_alerta}; prioridad {prio_antes} → {prio_despues}; {n_filas_alerta} alerta(s) con el filtro.", principal=False, full=True)

    # ---- Paso 4: segundo registro del mismo control -> 409 ----
    nino_c, ctrl_c = c["nino"], c["control"]
    pg.goto(base)
    ir_a_expediente(pg, clave_de(nino_c))
    fc = fila_control(pg, ctrl_c["codigo"], ctrl_c["fecha_programada"])
    fc.wait_for()
    fc.get_by_test_id("btn-no-asistio").click()
    pg.get_by_test_id("modal-asistencia").wait_for()
    pg.get_by_test_id("asistencia-motivo").select_option("Olvido de la cita")
    pg.get_by_test_id("asistencia-detalle").fill("Segundo registro de prueba")
    # Otra persona del personal (segunda sesión) registra primero la inasistencia de ese mismo control.
    primero = httpx.post(f"{base}/api/ninos/{nino_c['id']}/controles/{ctrl_c['codigo']}/asistencia",
                         json={"fecha_programada": ctrl_c["fecha_programada"], "estado": "NO_ASISTIO", "motivo": "Registrada antes por otra persona del personal"})
    t0 = time.perf_counter()
    pg.get_by_test_id("asistencia-confirmar").click()
    pg.wait_for_function("document.querySelector('[data-testid=asistencia-error]').textContent.trim().length > 0")
    ms_409 = (time.perf_counter() - t0) * 1000
    ev.tiempo(rf, "segundo registro del mismo control → mensaje 409", ms_409)
    mensaje = pg.get_by_test_id("asistencia-error").inner_text().strip()
    modal_abierto = pg.get_by_test_id("modal-asistencia").is_visible()
    pg.get_by_test_id("asistencia-error").scroll_into_view_if_needed()
    ev.foto(pg, rf, "Paso 4 · RESULTADO (409 en un segundo registro)", f"{carpeta}/{pre}_paso4_409_segundo_registro.png",
            "Dos personas del personal registran el mismo control: la segunda (esta pantalla) recibe el rechazo 409 con un mensaje claro dentro del cuadro, que sigue abierto; "
            "no se duplica el registro.",
            f"Primer registro (otra sesión): HTTP {primero.status_code}; mensaje visible en el cuadro: «{mensaje}»; respuesta en {ms_409:.0f} ms.", principal=True, full=True)
    cuenta_c = [x for x in httpx.get(f"{base}/api/ninos/{nino_c['id']}/asistencias").json() if x["codigo_control"] == ctrl_c["codigo"]]
    directo = httpx.post(f"{base}/api/ninos/{nino_c['id']}/controles/{ctrl_c['codigo']}/asistencia",
                         json={"fecha_programada": ctrl_c["fecha_programada"], "estado": "ASISTIO"})
    ok_a_todo = ok_a and cumplido_a and sin_alerta_a
    ev.criterio(rf, "Dado un control programado (fecha <= hoy) sin registro, cuando el personal registra «Asistió» o «No asistió» con motivo, entonces el control queda "
                    "cumplido o marcado como inasistencia (con la alerta elevada un nivel) y un segundo registro del mismo control se rechaza con 409 y un mensaje claro, en < 2 s.",
                ok_a_todo and marca == f"{MOTIVO_NO_ASISTIO}: {DETALLE_NO_ASISTIO}" and sigue_vencido and marca_alerta
                and primero.status_code == 201 and len(cuenta_c) == 1 and directo.status_code == 409 and bool(mensaje) and modal_abierto
                and max(ms_a, ms_b, ms_409) < UMBRAL_MS
                and {"BAJA": "MEDIA", "MEDIA": "ALTA"}.get(prio_antes) == prio_despues,
                f"«Asistió»: estado {estado_antes} → CUMPLIDO por asistencia ({ms_a:.0f} ms; asistencia registrada en la API: {ok_a}; sin alerta: {sin_alerta_a}); "
                f"«No asistió» con motivo: marca visible, control sigue vencido, prioridad {prio_antes} → {prio_despues} ({ms_b:.0f} ms); "
                f"segundo registro: 409 (mensaje «{mensaje}», {ms_409:.0f} ms), un solo registro en la API ({len(cuenta_c)}); POST directo repetido: HTTP {directo.status_code}.")


def datos_reales(pg, ev: Evidencias, base: str, tag: str):
    rf, n = "Datos reales", "DJ"
    carpeta = "datos_reales"
    ninos = httpx.get(f"{base}/api/ninos", params={"estado": ""}).json()
    dataset = [x for x in ninos if x["origen"] == "DATASET_DIRESA_JUNIN"]
    elegido = None
    for nino in dataset:  # primer registro con discrepancia HIS vs sistema y agenda con >= 2 estados distintos
        exp = httpx.get(f"{base}/api/ninos/{nino['id']}").json()
        dif = [e for e in exp["evaluaciones"] if e.get("clasificacion_origen") and e["clasificacion_origen"] != e["clasificacion"]]
        ag = agenda_api(base, nino["id"])
        estados = {c["estado"] for c in ag.get("controles", [])}
        if dif and ag.get("aplica") and len(estados) >= 2 and "VENCIDO" in estados and len(exp["evaluaciones"]) >= 2:
            elegido = (nino, exp, ag)
            break
    if not elegido:
        raise RuntimeError("No se encontró un registro del dataset con discrepancia HIS/sistema y agenda con varios estados")
    nino, exp, ag = elegido
    pg.goto(base)
    aviso = pg.get_by_test_id("aviso-fecha-referencia").inner_text().strip()

    def abrir():
        ir_a_expediente(pg, nino["codigo_origen"])
    ms = cronometrar(abrir)
    ev.tiempo(rf, f"búsqueda por código {nino['codigo_origen']} → expediente con agenda", ms)
    nombre = pg.get_by_test_id("expediente-nombre").inner_text()
    origen = pg.get_by_test_id("expediente-origen").inner_text().replace("\n", " ")
    codigo = pg.get_by_test_id("expediente-codigo").inner_text()
    his = pg.get_by_test_id("clasificacion-his").all_inner_texts()
    estados_ui = pg.locator("[data-testid=agenda-tabla] tbody tr").evaluate_all("rs => rs.map(r => r.dataset.estado)")
    cuerpo = pg.get_by_test_id("expediente").inner_text()
    pg.get_by_test_id("agenda-seccion").scroll_into_view_if_needed()
    his_txt = " | ".join(f"{x}" for x in his).replace("\n", " ")
    ev.foto(pg, rf, f"Expediente de un registro del dataset ({nino['codigo_origen']})", f"{carpeta}/{n}_expediente_{nino['codigo_origen']}.png",
            f"Expediente del registro {nino['codigo_origen']} de la muestra real de la DIRESA Junín: se presenta como «{nombre}» (sin DNI, nombres ni tutor), con el origen "
            "«Dataset DIRESA Junín (anonimizado)», su código seudónimo, cada evaluación con la clasificación calculada por el sistema y, debajo, la severidad del HIS; "
            "la agenda de controles se calcula con la fecha de referencia 30/06/2024 y muestra los estados.",
            f"Origen: «{origen}»; código {codigo}; clasificación HIS por evaluación: {his_txt}; estados de la agenda: {sorted(set(estados_ui))} ({len(estados_ui)} controles); "
            f"aviso de cabecera: «{aviso}»; expediente en {ms:.0f} ms.", principal=True, full=True)
    limpio = "undefined" not in cuerpo and "null" not in cuerpo
    # pestaña de alertas con la muestra real
    resumen = httpx.get(f"{base}/api/alertas/resumen").json()

    def abrir_alertas():
        pg.get_by_test_id("tab-alertas").click()
        pg.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
    ms_al = cronometrar(abrir_alertas)
    ev.tiempo(rf, "clic en pestaña «Alertas» → resumen + tabla con la muestra real", ms_al)
    kv = pg.get_by_test_id("kpi-vencidos").inner_text()
    filas = pg.locator("[data-testid=alertas-tabla] tbody tr").count()
    primeras = pg.locator("[data-testid=alertas-tabla] tbody tr td:nth-child(2)").all_inner_texts()[:3]
    pg.evaluate("window.scrollTo(0, 0)")
    ev.foto(pg, rf, "Pestaña Alertas con la muestra real", f"{carpeta}/{n}_alertas_muestra_real.png",
            "Pestaña «Alertas» sobre la muestra de 500 niños de la DIRESA Junín con fecha de referencia 30/06/2024: el resumen (vencidos, niños, prioridad alta/media/baja, por vencer en 7 días) y las primeras alertas "
            "ordenadas por prioridad; los registros del dataset aparecen por su código «Registro DJ-xxxxx (dataset anonimizado)». Se muestra la parte superior de la tabla (la lista completa es larga).",
            f"{kv} controles vencidos ({resumen['ninos_con_vencidos']} niños; ALTA {resumen['por_prioridad']['ALTA']}, MEDIA {resumen['por_prioridad']['MEDIA']}, BAJA {resumen['por_prioridad']['BAJA']}); "
            f"{filas} filas en la tabla; primeras: {primeras}; carga en {ms_al:.0f} ms.", principal=True, full=False)
    # contraste: registro de prueba de origen SISTEMA (con DNI, nombres y tutor ficticios, rotulado como de prueba)
    sis = next((x for x in ninos if x["origen"] == "SISTEMA"), None)
    if sis:
        ir_a_expediente(pg, sis["dni"])
        nombre_s = pg.get_by_test_id("expediente-nombre").inner_text()
        pg.get_by_test_id("agenda-seccion").scroll_into_view_if_needed()
        ev.foto(pg, rf, f"Expediente de un registro de prueba SISTEMA (DNI {sis['dni']})", f"{carpeta}/SISTEMA_expediente_{sis['dni']}.png",
                f"Contraste con el registro del dataset: expediente de un registro de prueba creado «desde el sistema» (origen SISTEMA), con DNI y nombre ficticios «{nombre_s}»; "
                "no tiene la severidad del HIS y su agenda solo tiene controles futuros respecto de la fecha de referencia.",
                f"Nombre «{nombre_s}»; DNI {sis['dni']}; sin etiqueta de dataset anonimizado.", principal=False, full=True)
    ev.criterio(rf, "Dado el dataset anonimizado de la DIRESA Junín importado (muestra de 500 niños) y la fecha de referencia del corte, cuando el personal abre un registro o la pestaña «Alertas», "
                    "entonces ve el registro sin datos personales, con la severidad del HIS junto a la clasificación del sistema, su agenda con estados y los controles vencidos de la muestra, en < 2 s.",
                nombre.startswith("Registro DJ-") and "anonimizado" in origen.lower() + nombre.lower() and codigo == nino["codigo_origen"] and bool(his) and len(set(estados_ui)) >= 2
                and limpio and kv == str(resumen["total_vencidos"]) and filas == resumen["total_vencidos"] and max(ms, ms_al) < UMBRAL_MS,
                f"{nino['codigo_origen']}: {len(exp['evaluaciones'])} evaluaciones, HIS ≠ sistema en {sum(1 for e in exp['evaluaciones'] if e.get('clasificacion_origen') and e['clasificacion_origen'] != e['clasificacion'])}; "
                f"agenda {sorted(set(estados_ui))}; alertas UI = API ({kv} vencidos, {filas} filas); expediente {ms:.0f} ms y alertas {ms_al:.0f} ms.")


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
def ejecutar_flujos(args, modo, flujos, version, tag, carpeta, solo_principales, viewport=VIEWPORT, ev=None, servidor=None):
    app_dir = Path(args.app_dir)
    db = Path(args.db) if args.db else app_dir / "datos" / "s9_capturas.db"
    ev = ev or Evidencias(modo, version, carpeta, solo_principales)
    srv = servidor if servidor else (None if args.sin_servidor else Servidor(app_dir, db, args.puerto, reiniciar_flag=(modo != "inc1")))
    contexto = srv if srv else _Nulo(f"http://127.0.0.1:{args.puerto}")
    with contexto as s, sync_playwright() as p:
        print(f"== {modo} · {version} · {s.url}")
        nav = p.chromium.launch()
        for nombre, fn in flujos:
            ctx = nav.new_context(viewport=viewport, locale="es-PE", timezone_id="America/Lima", accept_downloads=True)
            pg = ctx.new_page()
            errores = []
            pg.on("pageerror", lambda e: errores.append(str(e)))
            # los 422 (RF-03) y los 409 (segundo registro de RF-09) son respuestas esperadas de pruebas de rechazo, no defectos
            pg.on("console", lambda m: errores.append(m.text) if m.type == "error" and "422" not in m.text and "409" not in m.text else None)
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


ETIQ_INC = {"inc1": "Inc. 1 (v1.0-PMV)", "inc2": "Inc. 2 (v1.5)", "regresion": "Regresión Inc. 1 en v1.5",
            "inc2final": "Inc. 2 cierre (v2.0.0-inc2)", "arquitectura": "Arquitectura"}


def modo_inc2final(args):
    """RF-08 y RF-09 (y los registros reales de la muestra DIRESA) sobre la v2.0.0-inc2, con capturas directamente en RF-08/, RF-09/ y datos_reales/."""
    args.app_dir = args.app_dir or str(APP_V15)
    args.puerto = args.puerto or 8103
    version = args.version_etiqueta or "v2.0.0-inc2"
    db = Path(args.db) if args.db else Path(args.app_dir) / "datos" / "s9_capturas_inc2final.db"
    ev = Evidencias("inc2final", version, SALIDA, False, leyenda=LEYENDA_INC2_FINAL, archivo_relativo=True)
    srv = None if args.sin_servidor else ServidorDataset(Path(args.app_dir), db, args.puerto, registros_sistema=args.con_registros_sistema)
    # el orden importa: las capturas de datos reales se toman antes de que RF-09 modifique alertas de la muestra
    ejecutar_flujos(args, "inc2final", [("rf08", rf08), ("datos_reales", datos_reales), ("rf09", rf09)], version, "inc2final", SALIDA, False,
                    ev=ev, servidor=srv)


def modo_indice(args):
    archivos = ["inc1", "inc2", "regresion", "inc2final", "arquitectura"]
    datos = {m: json.loads((SALIDA / f"resultados_{m}.json").read_text("utf-8")) for m in archivos if (SALIDA / f"resultados_{m}.json").exists()}
    L = ["# Índice de evidencias visuales (Actividad 5, guía S9)", "",
         "Capturas reales del software en ejecución (Chromium headless / Playwright, viewport 1366x900, idioma es-PE, zona horaria America/Lima). "
         "Las de RF-01 a RF-07 usan **datos 100 % sintéticos**; las del cierre del Incremento 2 (RF-08, RF-09 y `datos_reales/`) usan la **muestra de 500 niños del dataset "
         "anonimizado de la DIRESA Junín** más registros de prueba de origen SISTEMA. "
         "Cada captura incluye un pie de «Evidencia S9» inyectado por el script (RF, paso, URL, versión, fecha-hora de Perú y la leyenda de los datos); "
         "no altera la funcionalidad. Script reproducible: `capturar_evidencias.py`.", "",
         "> **Organización por RF.** Las capturas están en carpetas por requerimiento (`RF-01/` … `RF-09/`), como pide la guía S9 (anexo «carpeta de capturas organizadas por RF»). "
         "El nombre de cada archivo conserva el incremento (`inc1`, `inc2`, `inc2final`) o la regresión (`v15_regresion`). Las capturas de los registros reales del dataset están en `datos_reales/` "
         "y las de la estructura de carpetas en `arquitectura/`.", ""]
    nombres = {"inc1": "Incremento 1 · v1.0-PMV (RF-01 a RF-05)", "inc2": "Incremento 2 · v1.5.0-inc2-avance (RF-06 y RF-07)",
               "regresion": "Regresión visual · RF-01 a RF-05 ejecutados en v1.5.0-inc2-avance",
               "inc2final": "Incremento 2 · cierre v2.0.0-inc2 (RF-08 y RF-09)", "arquitectura": "Arquitectura · árboles de app/"}
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
    ap.add_argument("--modo", required=True, choices=["inc1", "inc2", "regresion", "inc2final", "arquitectura", "indice", "github"])
    ap.add_argument("--app-dir", help="carpeta raíz de la app (por defecto según el modo)")
    ap.add_argument("--puerto", type=int, help="puerto (por defecto 8101 para inc1, 8102 para inc2/regresion)")
    ap.add_argument("--db", help="ruta de la base SQLite (por defecto <app-dir>/datos/s9_capturas.db)")
    ap.add_argument("--version-etiqueta", help="etiqueta de versión para el pie de evidencia")
    ap.add_argument("--sin-servidor", action="store_true", help="no levantar servidor: usar uno ya activo en --puerto")
    ap.add_argument("--con-registros-sistema", type=int, default=3, help="inc2final: cantidad de registros de prueba de origen SISTEMA (por defecto 3)")
    args = ap.parse_args()

    if args.modo == "arquitectura":
        return modo_arquitectura(args)
    if args.modo == "github":
        return intentar_github(args)
    if args.modo == "indice":
        return modo_indice(args)
    if args.modo == "inc2final":
        return modo_inc2final(args)
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
