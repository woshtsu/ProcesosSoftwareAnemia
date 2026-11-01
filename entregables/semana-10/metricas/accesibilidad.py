"""Factor U: accesibilidad WCAG 2.1 AA medida (axe-core por pantalla, teclado, objetivos tactiles, reflow) y contraste de la paleta.

Uso (raiz del repositorio):
    PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers AXE_JS=/ruta/node_modules/axe-core/axe.min.js python entregables/semana-10/metricas/accesibilidad.py
(axe-core se instala con `npm i axe-core`; la version usada queda en el JSON.) Servidor demo en 127.0.0.1:8765 + login con servidor
supabase simulado en el mismo puerto (al final). Salidas: metricas/salidas/U_axe_por_pantalla.json, U_teclado.json, U_objetivos_tactiles.json,
U_reflow.json y U_contraste_paleta.json (este ultimo lo genera paleta_colores.py).
"""

import json
import os
import re
import sys
import threading
import socket
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capturar_software as cs  # noqa: E402
from playwright.sync_api import expect, sync_playwright  # noqa: E402

AXE = Path(os.environ.get("AXE_JS", "/tmp/axe/node_modules/axe-core/axe.min.js"))
SAL = cs.BASE / "metricas" / "salidas"
IMGU = cs.BASE / "evidencias" / "usabilidad"
ETIQUETAS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]


def correr_axe(pg):
    pg.add_script_tag(content=AXE.read_text(encoding="utf-8")) if not pg.evaluate("typeof axe !== 'undefined'") else None
    return pg.evaluate(
        """async (tags) => {
          const r = await axe.run(document, {runOnly: {type: 'tag', values: tags}});
          const bp = await axe.run(document, {runOnly: {type: 'tag', values: ['best-practice']}});
          const f = (v) => v.map(x => ({id: x.id, impacto: x.impact, ayuda: x.help, wcag: x.tags.filter(t => /^wcag\\d+$/.test(t) || /^wcag\\d{3,}$/.test(t)), nodos: x.nodes.length, ejemplo: x.nodes.slice(0,3).map(n => ({selector: n.target.join(' '), html: n.html.slice(0,140), detalle: (n.any[0]||n.all[0]||n.none[0]||{}).message}))}));
          return {version: axe.version, violaciones: f(r.violations), pasadas: r.passes.length, inaplicables: r.inapplicable.length, incompletas: f(r.incomplete), buenas_practicas: f(bp.violations)};
        }""",
        ETIQUETAS,
    )


def preparar_pantallas(pg):
    """Genera (nombre, funcion que deja la pantalla lista)."""
    def reg():
        pg.get_by_test_id("tab-registro").click()

    def seg():
        pg.get_by_test_id("tab-seguimiento").click()
        pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length > 3")

    def exp():
        cs.abrir_por_dni(pg, "71000022")
        pg.get_by_test_id("agenda-tabla").wait_for()

    def agenda():
        pg.get_by_test_id("tab-agenda").click()
        pg.wait_for_function("document.querySelectorAll('[data-testid=agenda-personal-dia]').length === 7")

    def visitas():
        pg.get_by_test_id("tab-visitas").click()
        pg.get_by_test_id("visita-priorizada").first.wait_for()

    def recordatorios():
        pg.get_by_test_id("tab-recordatorios").click()
        pg.get_by_test_id("recordatorios-generar").click()
        pg.get_by_test_id("recordatorio").first.wait_for()

    def alertas():
        pg.get_by_test_id("tab-alertas").click()
        pg.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")

    def sync():
        pg.get_by_test_id("tab-sincronizacion").click()

    def reporte():
        pg.get_by_test_id("tab-reporte").click()
        pg.get_by_test_id("generar-reporte").click()
        pg.get_by_test_id("kpi-registrados").wait_for()

    def m_asistencia():
        cs.abrir_por_dni(pg, "71000022")
        pg.locator("[data-testid=agenda-tabla] tr[data-estado=VENCIDO] [data-testid=btn-no-asistio]").first.click()
        pg.get_by_test_id("modal-asistencia").wait_for()

    def m_visita():
        pg.get_by_test_id("tab-visitas").click()
        pg.get_by_test_id("visita-priorizada").first.get_by_test_id("btn-visitar").click()
        pg.get_by_test_id("modal-visita").wait_for()

    def m_respuesta():
        pg.get_by_test_id("tab-recordatorios").click()
        pg.locator("[data-testid=recordatorio]:has([data-testid=btn-responder]) [data-testid=btn-responder]").first.click()
        pg.get_by_test_id("modal-respuesta").wait_for()

    def m_barrera():
        cs.abrir_por_dni(pg, "71000022")
        pg.get_by_test_id("btn-barrera-nino").click()
        pg.get_by_test_id("modal-barrera").wait_for()

    return [("Registrar niño", reg), ("Seguimiento", seg), ("Expediente", exp), ("Agenda", agenda), ("Visitas", visitas), ("Recordatorios", recordatorios), ("Alertas", alertas), ("Sincronización", sync), ("Reporte", reporte), ("Modal asistencia", m_asistencia), ("Modal visita", m_visita), ("Modal respuesta del tutor", m_respuesta), ("Modal barrera", m_barrera)]


def cerrar_modales(pg):
    pg.keyboard.press("Escape")
    pg.evaluate("document.querySelectorAll('.modal').forEach(m => m.hidden = true)")


def objetivos(pg):
    return pg.evaluate(
        """() => [...document.querySelectorAll('button, a[href], input:not([type=hidden]), select, textarea, [role=button], summary')]
          .filter(e => e.offsetParent !== null && !e.closest('[hidden]'))
          .map(e => {const r = e.getBoundingClientRect(); return {t: e.tagName.toLowerCase() + (e.id ? '#' + e.id : (e.dataset.testid ? '[' + e.dataset.testid + ']' : '')), w: Math.round(r.width), h: Math.round(r.height)};})"""
    )


def estados(pg):
    """Elementos de estado (badge, ctrl, chip, prioridad) y cuantos carecen de texto: el color no es el unico canal (1.4.1)."""
    return pg.evaluate(
        """() => { const e = [...document.querySelectorAll('.badge, .ctrl, .chip, .insignia, .sync-indicador')].filter(x => x.offsetParent !== null);
        return {total: e.length, sin_texto: e.filter(x => !x.textContent.trim()).length}; }"""
    )


def main():
    IMGU.mkdir(parents=True, exist_ok=True)
    proc = cs.levantar({})
    axe_res, tact_res, reflow = {"escritorio": {}, "movil": {}}, {"escritorio": {}, "movil": {}}, {}
    teclado = {}
    est_res = {}
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch()
            kw = dict(locale="es-PE", timezone_id="America/Lima")
            for nombre, vp, extra in (("escritorio", cs.ESC, {}), ("movil", cs.MOV, {"is_mobile": True, "has_touch": True, "device_scale_factor": 2})):
                ctx = nav.new_context(viewport=vp, **kw, **extra)
                pg = ctx.new_page()
                pg.goto(cs.URL)
                pg.get_by_test_id("tab-registro").wait_for()
                for pant, prep in preparar_pantallas(pg):
                    cerrar_modales(pg)
                    prep()
                    pg.wait_for_timeout(300)
                    axe_res[nombre][pant] = correr_axe(pg)
                    est_res.setdefault(nombre, {})[pant] = estados(pg)
                    ob = objetivos(pg)
                    tact_res[nombre][pant] = {"total": len(ob), "menores_24": [o for o in ob if o["w"] < 24 or o["h"] < 24], "menores_44": sum(1 for o in ob if o["w"] < 44 or o["h"] < 44)}
                    v = axe_res[nombre][pant]["violaciones"]
                    print(f"{nombre:<11}{pant:<28} violaciones WCAG 2.1 A/AA: {sum(x['nodos'] for x in v):>3} nodos en {len(v)} reglas; objetivos<24px: {len(tact_res[nombre][pant]['menores_24'])}/{len(ob)}")
                ctx.close()
            # reflow a 320 px (1.4.10): sin desplazamiento horizontal de la pagina
            ctx = nav.new_context(viewport={"width": 320, "height": 640}, **kw)
            pg = ctx.new_page()
            pg.goto(cs.URL)
            pg.get_by_test_id("tab-registro").wait_for()
            for pant, prep in preparar_pantallas(pg):
                cerrar_modales(pg)
                prep()
                pg.wait_for_timeout(250)
                reflow[pant] = pg.evaluate("({ancho: document.documentElement.scrollWidth, ventana: innerWidth})")
                reflow[pant]["desborde"] = reflow[pant]["ancho"] > reflow[pant]["ventana"]
            ctx.close()
            # teclado
            ctx = nav.new_context(viewport=cs.ESC, **kw)
            pg = ctx.new_page()
            pg.goto(cs.URL)
            pg.get_by_test_id("tab-registro").wait_for()
            paradas, sin_foco = [], []
            for i in range(60):
                pg.keyboard.press("Tab")
                pg.wait_for_timeout(40)
                info = pg.evaluate(
                    """() => {const e = document.activeElement; if (!e || e === document.body) return null;
                    const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
                    return {t: e.tagName.toLowerCase() + (e.id ? '#' + e.id : (e.dataset.testid ? '[' + e.dataset.testid + ']' : '')), outline: cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor, sombra: cs.boxShadow, visible: r.width > 0 && r.height > 0, foco: e.matches(':focus')}}"""
                )
                if info and info["foco"]:  # si el foco esta en una parte interna del control (p. ej. el icono del calendario) no se evalua el contorno del <input>
                    paradas.append(info)
                    if (info["outline"].startswith("none") or info["outline"].split()[1] == "0px") and info["sombra"] == "none":
                        sin_foco.append(info["t"])
            unicos = list(dict.fromkeys(x["t"] for x in paradas))
            teclado["paradas_tab_en_60_pulsaciones"] = len(paradas)
            teclado["elementos_distintos"] = len(unicos)
            teclado["ciclo_completo"] = len(unicos) < 60 and unicos[0] in [x["t"] for x in paradas[len(unicos):]]
            teclado["elementos_sin_indicador_de_foco"] = sin_foco
            teclado["indicadores"] = list({x["outline"] for x in paradas})
            # captura de foco visible en un boton de pestana y en un campo
            pg.focus("[data-testid=tab-seguimiento]")
            pg.keyboard.press("Shift+Tab")
            pg.keyboard.press("Tab")
            pg.screenshot(path=str(IMGU / "U_teclado_foco_pestana.png"), clip={"x": 0, "y": 0, "width": 1280, "height": 140})
            pg.focus("#dni")
            pg.screenshot(path=str(IMGU / "U_teclado_foco_campo.png"), clip={"x": 0, "y": 110, "width": 1280, "height": 330})
            # recorrido por teclado: campos llenados y envio con Enter en el boton Guardar (sin usar el raton)
            pg.get_by_test_id("tab-registro").click()
            cs.llenar(pg, "72555001")
            pg.get_by_test_id("guardar").focus()
            pg.keyboard.press("Enter")
            try:
                pg.get_by_test_id("tabla-evaluaciones").wait_for(timeout=5000)
                teclado["registro_con_teclado_enter_en_guardar"] = True
            except Exception:  # noqa: BLE001
                teclado["registro_con_teclado_enter_en_guardar"] = False
            # modal: Esc cierra y que el foco quede dentro
            cs.abrir_por_dni(pg, "71000022")
            btn = pg.locator("[data-testid=agenda-tabla] tr[data-estado=VENCIDO] [data-testid=btn-no-asistio]").first
            btn.focus()
            pg.keyboard.press("Enter")
            pg.get_by_test_id("modal-asistencia").wait_for()
            foco_en_modal = pg.evaluate("!!document.activeElement.closest('#modal-asistencia')")
            pg.keyboard.press("Escape")
            cerrado = pg.get_by_test_id("modal-asistencia").is_hidden()
            foco_vuelve = pg.evaluate("document.activeElement.tagName === 'BODY' ? 'body' : document.activeElement.tagName.toLowerCase() + (document.activeElement.dataset.testid ? '[' + document.activeElement.dataset.testid + ']' : '')")
            teclado["modal_abre_con_enter"] = True
            teclado["modal_foco_inicial_dentro"] = foco_en_modal
            teclado["modal_cierra_con_esc"] = cerrado
            teclado["foco_tras_cerrar_modal"] = foco_vuelve
            # atrapa el foco el modal? (Tab 12 veces dentro del modal)
            btn.focus()
            pg.keyboard.press("Enter")
            pg.get_by_test_id("modal-asistencia").wait_for()
            fuera = 0
            for _ in range(14):
                pg.keyboard.press("Tab")
                if not pg.evaluate("!!document.activeElement.closest('#modal-asistencia')"):
                    fuera += 1
            teclado["modal_tab_escapa_del_dialogo_veces_en_14"] = fuera
            ctx.close()
            nav.close()
    finally:
        proc.terminate()
        proc.wait()
    # login (servidor supabase simulado)
    login = login_axe()
    axe_res["escritorio"]["Inicio de sesión"] = login["escritorio"]
    axe_res["movil"]["Inicio de sesión"] = login["movil"]
    print("Inicio de sesion: violaciones", [(k, sum(x["nodos"] for x in v["violaciones"])) for k, v in login.items()])
    (SAL / "U_axe_por_pantalla.json").write_text(json.dumps(axe_res, ensure_ascii=False, indent=2), encoding="utf-8")
    (SAL / "U_objetivos_tactiles.json").write_text(json.dumps(tact_res, ensure_ascii=False, indent=2), encoding="utf-8")
    (SAL / "U_estados_con_texto.json").write_text(json.dumps(est_res, ensure_ascii=False, indent=2), encoding="utf-8")
    (SAL / "U_reflow_320px.json").write_text(json.dumps(reflow, ensure_ascii=False, indent=2), encoding="utf-8")
    (SAL / "U_teclado.json").write_text(json.dumps(teclado, ensure_ascii=False, indent=2), encoding="utf-8")
    resumen = {}
    for vp, pant in axe_res.items():
        resumen[vp] = {"pantallas": len(pant), "reglas_axe_aprobadas_total": sum(v["pasadas"] for v in pant.values()), "violaciones_nodos": sum(sum(x["nodos"] for x in v["violaciones"]) for v in pant.values()), "pantallas_sin_violaciones": sum(1 for v in pant.values() if not v["violaciones"]), "buenas_practicas_nodos": sum(sum(x["nodos"] for x in v["buenas_practicas"]) for v in pant.values())}
    print(json.dumps(resumen, ensure_ascii=False))
    print("reflow 320px con desborde:", [k for k, v in reflow.items() if v["desborde"]])
    print("teclado:", json.dumps(teclado, ensure_ascii=False))
    (SAL / "U_resumen.json").write_text(json.dumps({"axe": resumen, "reflow_pantallas": len(reflow), "reflow_con_desborde": [k for k, v in reflow.items() if v["desborde"]], "axe_version": next(iter(axe_res["escritorio"].values()))["version"]}, ensure_ascii=False, indent=2), encoding="utf-8")


def login_axe():
    sys.path.insert(0, str(cs.PMV))
    from app.adapters.outbound.supabase_auth import SupabaseAuth
    from app.application.servicio_sesion import ServicioSesion
    from app.main import crear_app
    import tempfile
    import uvicorn

    app = crear_app(f"sqlite:///{tempfile.mkdtemp()}/l.db", auth_mode="supabase")
    app.state.auth_configurado = True
    app.state.sesiones = ServicioSesion(SupabaseAuth("https://example.test", "publica", transport=httpx.MockTransport(lambda r: httpx.Response(401))))
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", cs.PUERTO))
    server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
    th = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    th.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    out = {}
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch()
            for nombre, vp, extra in (("escritorio", cs.ESC, {}), ("movil", cs.MOV, {"is_mobile": True, "device_scale_factor": 2})):
                ctx = nav.new_context(viewport=vp, locale="es-PE", **extra)
                pg = ctx.new_page()
                pg.goto(cs.URL)
                pg.wait_for_function("document.getElementById('login-enviar') && !document.getElementById('login-enviar').disabled || document.getElementById('login-estado').textContent.length > 0")
                pg.fill("#login-email", "enfermeria@example.test")
                pg.fill("#login-password", "mala")
                out[nombre] = correr_axe(pg)
                if nombre == "escritorio":
                    pg.screenshot(path=str(IMGU / "U_login_escritorio.png"))
                else:
                    pg.screenshot(path=str(IMGU / "U_login_movil.png"))
                ctx.close()
            nav.close()
    finally:
        server.should_exit = True
        th.join(timeout=10)
        sock.close()
        app.state.repositorio.engine.dispose()
    return out


if __name__ == "__main__":
    main()
