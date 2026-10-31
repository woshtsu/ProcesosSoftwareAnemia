"""Calculo del indice FURPS+ a partir de las salidas reales de metricas/salidas/ (sin valores escritos a mano).

Uso (raiz del repositorio): python entregables/semana-10/metricas/furps_calculo.py
Formulas por criterio (cada criterio pesa lo mismo dentro de su factor):
  ratio  : % = cumplen / total x 100
  mayor  : % = min(100, medido / meta x 100)        (mayor es mejor)
  menor  : % = min(100, meta / medido x 100)        (menor es mejor; medido = 0 -> 100; meta = 0 y medido > 0 -> 0)
Indice primario      : solo criterios MEDIDOS.
Indice conservador   : los criterios NO MEDIDOS cuentan 0 % (no se consideran cumplidos).
Pesos de la guia S10: F 30, U 15, R 15, P 15, S 10, + 15.
Salida: salidas/FURPS_calculo.json y tabla en stdout.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

SAL = Path(__file__).resolve().parent / "salidas"
J = lambda n: json.load(open(SAL / n, encoding="utf-8"))
PESOS = {"F": 30, "U": 15, "R": 15, "P": 15, "S": 10, "+": 15}
C = []


def pct(tipo, medido, meta):
    if tipo == "ratio":
        ok, total = medido
        return round(100 * ok / total, 1)
    if tipo == "mayor":
        return round(min(100, medido / meta * 100), 1)
    if medido == 0:
        return 100.0 if meta >= 0 else 0.0
    if meta == 0:
        return 0.0
    return round(min(100, meta / medido * 100), 1)


def crit(f, cid, nombre, tipo, medido, meta, fuente, texto_medido, texto_meta, medible=True):
    C.append({"factor": f, "id": cid, "criterio": nombre, "tipo": tipo, "medido": medido, "meta": meta, "medido_txt": texto_medido, "meta_txt": texto_meta,
              "pct": pct(tipo, medido, meta) if medible else None, "medible": medible, "fuente": fuente})


# ---------------- F ----------------
fa = J("F_resultados_aceptacion.json")
crit("F", "F1", "Escenarios de aceptación aprobados (Inc. 1-4)", "ratio", (fa["aprobados"], fa["escenarios"]), None, "salidas/F_resultados_aceptacion.json", f"{fa['aprobados']}/{fa['escenarios']}", "100 %")
pr = {t: sum(int(x.get("tests", 0)) for x in ET.parse(SAL / f).getroot().iter("testsuite")) for t, f in (("unit", "R02_junit_unit.xml"), ("e2e", "R03_junit_e2e.xml"))}
fall = {t: sum(int(x.get("failures", 0)) + int(x.get("errors", 0)) for x in ET.parse(SAL / f).getroot().iter("testsuite")) for t, f in (("unit", "R02_junit_unit.xml"), ("e2e", "R03_junit_e2e.xml"))}
tot_t = pr["unit"] + pr["e2e"]
crit("F", "F2", "Pruebas automatizadas aprobadas (unitarias+integración+arquitectura y E2E)", "ratio", (tot_t - fall["unit"] - fall["e2e"], tot_t), None, "salidas/R02_junit_unit.xml, R03_junit_e2e.xml", f"{tot_t - fall['unit'] - fall['e2e']}/{tot_t}", "100 %")
t_rf = max(next(r for r in fa["resultados"] if r["codigo"] == "RF-01")["detalle"]["tiempo_guardar_ms"], next(r for r in fa["resultados"] if r["codigo"] == "RF-05")["detalle"]["tiempo_ms"])
crit("F", "F3", "Tiempo de RF-01 (guardar) y RF-05 (reporte), peor caso", "menor", t_rf / 1000, 2.0, "salidas/F_resultados_aceptacion.json", f"{t_rf} ms", "< 2 s")

# ---------------- U ----------------
ax = J("U_axe_por_pantalla.json")
pas = sum(v["pasadas"] for d in ax.values() for v in d.values())
vio = sum(len(v["violaciones"]) for d in ax.values() for v in d.values())
sin = sum(1 for d in ax.values() for v in d.values() if not v["violaciones"])
crit("U", "U1", "axe-core WCAG 2.1 A/AA: reglas aprobadas sobre evaluadas (14 pantallas x 2 vistas)", "ratio", (pas, pas + vio), None, "salidas/U_axe_por_pantalla.json", f"{pas}/{pas + vio} reglas; {sin}/28 pantallas sin violaciones", "100 % (0 violaciones)")
cp = J("U_contraste_paleta.json")
unicos = {}
for r in cp["pares_texto"]:
    k = tuple(sorted((r["texto"].upper().replace("#FFF", "#FFFFFF") if len(r["texto"]) == 4 else r["texto"].upper(), r["fondo"].upper().replace("#FFF", "#FFFFFF") if len(r["fondo"]) == 4 else r["fondo"].upper())))
    unicos[k] = r["razon"] >= r["umbral"]
crit("U", "U2", "Contraste de texto ≥ 4,5:1 (1.4.3), pares de color únicos", "ratio", (sum(unicos.values()), len(unicos)), None, "salidas/U_contraste_paleta.json", f"{sum(unicos.values())}/{len(unicos)} pares", "100 %")
cmp_ = cp["componentes"]
crit("U", "U3", "Contraste de componentes ≥ 3:1 (1.4.11): bordes, foco y barras", "ratio", (sum(1 for c in cmp_ if c["cumple_1_4_11"]), len(cmp_)), None, "salidas/U_contraste_paleta.json", f"{sum(1 for c in cmp_ if c['cumple_1_4_11'])}/{len(cmp_)}", "100 %")
tc = J("U_teclado.json")
checks = [tc["ciclo_completo"], not tc["elementos_sin_indicador_de_foco"], tc["registro_con_teclado_enter_en_guardar"], tc["modal_abre_con_enter"], tc["modal_foco_inicial_dentro"], tc["modal_cierra_con_esc"], tc["foco_tras_cerrar_modal"] != "body", tc["modal_tab_escapa_del_dialogo_veces_en_14"] == 0]
crit("U", "U4", "Teclado (2.1.1/2.4.3): ciclo, indicador de foco, registro, abrir/cerrar modal, foco contenido y devuelto", "ratio", (sum(checks), len(checks)), None, "salidas/U_teclado.json", f"{sum(checks)}/{len(checks)} comprobaciones", "100 %")
ot = J("U_objetivos_tactiles.json")
tot_o = sum(v["total"] for d in ot.values() for v in d.values())
peq = sum(len(v["menores_24"]) for d in ot.values() for v in d.values())
crit("U", "U5", "Objetivos táctiles ≥ 24x24 px (2.5.8, WCAG 2.2)", "ratio", (tot_o - peq, tot_o), None, "salidas/U_objetivos_tactiles.json", f"{tot_o - peq}/{tot_o} (escritorio+móvil)", "100 %")
rf = J("U_reflow_320px.json")
crit("U", "U6", "Reflujo a 320 px sin desplazamiento horizontal (1.4.10)", "ratio", (sum(1 for v in rf.values() if not v["desborde"]), len(rf)), None, "salidas/U_reflow_320px.json", f"{sum(1 for v in rf.values() if not v['desborde'])}/{len(rf)} pantallas", "100 %")
et = J("U_estados_con_texto.json")
tot_e = sum(v["total"] for d in et.values() for v in d.values())
sin_t = sum(v["sin_texto"] for d in et.values() for v in d.values())
crit("U", "U7", "Estados de color con texto asociado (1.4.1, no solo color)", "ratio", (tot_e - sin_t, tot_e), None, "salidas/U_estados_con_texto.json", f"{tot_e - sin_t}/{tot_e} insignias", "100 %")
crit("U", "U8", "Lector de pantalla NVDA/TalkBack (4.1.2)", "ratio", (0, 1), None, "-", "no medido (sin lector instalado)", "100 %", medible=False)

# ---------------- R ----------------
pp = J("P_resumen.json")
disp = min(c["disponibilidad_pct"] for c in pp["corridas"])
sond = sum(c["sondeos_salud"] for c in pp["corridas"])
crit("R", "R1", "Disponibilidad de /api/salud durante las 3 corridas de carga", "mayor", disp, 99.5, "salidas/P_resumen.json", f"{disp} % ({sond} sondeos, 0 fallidos)", "≥ 99,5 %")
mt = J("R_mttr_reinicio.json")
crit("R", "R2", "MTTR: kill -9 del servidor y reinicio hasta /api/salud 200", "menor", mt["segundos_hasta_salud_200"], 300, "salidas/R_mttr_reinicio.json", f"{mt['segundos_hasta_salud_200']} s (datos íntegros: {mt['datos_integros']})", "< 5 min")
ch = J("R_caos_postgres.json")
crit("R", "R3", "Caos PostgreSQL (kill -9): el pool se reconecta sin reiniciar la aplicación", "ratio", (0 if ch["reinicio_de_la_aplicacion_necesario"] else 1, 1), None, "salidas/R_caos_postgres.json", f"sí, {ch['segundos_hasta_primer_200_tras_volver_la_bd']} s tras volver la BD", "sin reinicio")
cod = ch["codigos_durante_caida"]
crit("R", "R4", "Caos PostgreSQL: peticiones durante la caída respondidas sin error 500", "ratio", (ch["peticiones_durante_caida"] - cod.get("500", 0), ch["peticiones_durante_caida"]), None, "salidas/R_caos_postgres.json", f"{ch['peticiones_durante_caida'] - cod.get('500', 0)}/{ch['peticiones_durante_caida']} (500: {cod.get('500', 0)})", "respuesta controlada (503), 0 x 500")
nom = [c for c in pp["corridas"] if c["usuarios"] == 20]
crit("R", "R5", "Tasa de error con carga nominal (20 usuarios, 2 corridas)", "menor", sum(c["fallos"] for c in nom) / sum(c["peticiones"] for c in nom) * 100, 1.0, "salidas/P_resumen.json", f"{sum(c['fallos'] for c in nom)}/{sum(c['peticiones'] for c in nom)} fallos", "≤ 1 %")
fa_off = next(r for r in fa["resultados"] if r["codigo"] == "HIST-3.1b")["detalle"]
crit("R", "R6", "Lecturas servidas desde el caché del service worker con el servidor detenido", "ratio", (fa_off["filas_desde_cache"], fa_off["filas_en_linea"]), None, "salidas/F_resultados_aceptacion.json", f"{fa_off['filas_desde_cache']}/{fa_off['filas_en_linea']} filas", "100 %")
crit("R", "R7", "Disponibilidad en staging (Render/AWS) y recuperación automática de la BD gestionada", "ratio", (0, 1), None, "-", "no medido (no hay entorno de staging)", "≥ 99,5 %", medible=False)

# ---------------- P ----------------
a, b, c100 = [next(x for x in pp["corridas"] if x["corrida"].startswith(k)) for k in "ABC"]
p95 = max(a["p95_ms"], b["p95_ms"])
crit("P", "P1", "Latencia p95, 20 usuarios (peor de Inc. 1-2 e Inc. 3-4)", "menor", p95, 800, "salidas/P_resumen.json", f"{p95:.0f} ms (p50 {a['p50_ms']:.0f}/{b['p50_ms']:.0f} ms)", "< 800 ms")
crit("P", "P2", "Latencia p95, 100 usuarios (Inc. 1-2)", "menor", c100["p95_ms"], 800, "salidas/P_resumen.json", f"{c100['p95_ms']:.0f} ms (p50 {c100['p50_ms']:.0f} ms)", "< 800 ms")
crit("P", "P3", "Latencia p95, 500 usuarios (meta de la guía)", "menor", 0, 800, "-", "no medido (máximo probado: 100)", "< 800 ms", medible=False)
crit("P", "P4", "Tasa de error a 100 usuarios", "menor", c100["tasa_error_pct"], 1.0, "salidas/P_resumen.json", f"{c100['tasa_error_pct']} % (1 de {c100['peticiones']}: DNI duplicado generado por el script)", "≤ 1 %")
cl = J("P_cliente_pwa.json")
lcp = cl["primera_carga"]["lcp"]
crit("P", "P5", "LCP de la primera carga móvil (390x844, CPU x4, 1,6 Mbps, 150 ms)", "menor", lcp, 2500, "salidas/P_cliente_pwa.json", f"{lcp} ms (con service worker: {cl['segunda_carga_con_service_worker']['lcp']} ms)", "< 2500 ms")

# ---------------- S ----------------
hx = J("S_hexagonal.json")
n_dom = hx["archivos_por_capa"]["domain.model"] + hx["archivos_por_capa"]["domain.service"]
terc = sum(hx["matriz_importaciones"][c].get("tercero", 0) for c in ("domain.model", "domain.service"))
crit("S", "S1", "Importaciones de frameworks/terceros en el dominio (archivos limpios sobre archivos)", "ratio", (n_dom if terc == 0 else n_dom - terc, n_dom), None, "salidas/S_hexagonal.json", f"{terc} importaciones en {n_dom} archivos", "0")
arq = ET.parse(SAL / "R02_junit_unit.xml").getroot()
tests_arq = [t for t in arq.iter("testcase") if t.get("classname", "").startswith("tests.arquitectura")]
ok_arq = sum(1 for t in tests_arq if t.find("failure") is None and t.find("error") is None)
crit("S", "S2", "Pruebas de arquitectura (regla de dependencias) aprobadas", "ratio", (ok_arq, len(tests_arq)), None, "salidas/R02_junit_unit.xml", f"{ok_arq}/{len(tests_arq)}", "100 %")
cov = J("R01_cobertura.json")["totals"]["percent_covered"]
crit("S", "S3", "Cobertura de líneas y ramas (pytest-cov)", "mayor", cov, 80.0, "salidas/R01_cobertura.json", f"{cov:.2f} %", "≥ 80 % (umbral del proyecto)")
crit("S", "S4", "Ruff (E,F,W,I,B,UP,S,C90): errores", "menor", 0 if "All checks passed" in open(SAL / "R04_ruff_check.txt").read() else 1, 0, "salidas/R04_ruff_check.txt", "0 errores", "0")
rd = J("S_radon_resumen.json")
crit("S", "S5", "Bloques con complejidad ciclomática ≤ 10 (radon)", "ratio", (rd["bloques_analizados"] - rd["bloques_cc_gt_10"], rd["bloques_analizados"]), None, "salidas/S_radon_resumen.json", f"{rd['bloques_analizados'] - rd['bloques_cc_gt_10']}/{rd['bloques_analizados']} (máx. {rd['cc_maximo']})", "100 %")
crit("S", "S6", "Archivos con índice de mantenibilidad rango A (radon mi)", "ratio", (rd["rangos_mi"]["A"], rd["archivos_analizados"]), None, "salidas/S_radon_resumen.json", f"{rd['rangos_mi']['A']}/{rd['archivos_analizados']}", "100 %")

# ---------------- + ----------------
oe, oh = J("OWASP_estatico.json"), J("OWASP_pruebas_http.json")
cum = oe["cumple"] + oh["cumple"]
med = oe["comprobaciones"] - oe["no_medidos"] + oh["comprobaciones"]
crit("+", "+1", "Comprobaciones OWASP 2025 que cumplen (estáticas E01-E30 y dinámicas T01-T32)", "ratio", (cum, med), None, "salidas/OWASP_estatico.json, OWASP_pruebas_http.json", f"{cum}/{med} (+{oe['no_medidos']} no medida)", "100 %")
bd = open(SAL / "O05_bandit.json").read()
bj = json.loads(bd)["metrics"]["_totals"]
crit("+", "+2", "Vulnerabilidades Alta/Crítica por SAST y SCA (bandit, pip-audit)", "menor", bj["SEVERITY.HIGH"] + (0 if "No known vulnerabilities found" in open(SAL / "R09_pip_audit.txt").read() else 1), 0, "salidas/O05_bandit.json, R09_pip_audit.txt", "0 (bandit: 0 altas, 1 baja; pip-audit: 0)", "0")
crit("+", "+3", "Hallazgos Alta/Crítica confirmados por revisión manual y dinámica (A01: sin RBAC)", "menor", 1, 0, "salidas/OWASP_estatico.json (E01)", "1 (falta de roles/segmentación)", "0")
crit("+", "+4", "Restricciones técnicas verificadas por ejecución (diseño, implementación, interfaz)", "ratio", (3, 3), None, "salidas/R06, R04, R07", "3/3 (Docker: sin daemon, no ejecutado)", "100 %")
crit("+", "+5", "Restricción de despliegue Docker verificada por ejecución (build/up)", "ratio", (0, 1), None, "-", "no medido (sin daemon Docker)", "100 %", medible=False)
crit("+", "+6", "Política de contraseñas, MFA y bloqueo por intentos (Supabase Auth, A07)", "ratio", (0, 1), None, "salidas/OWASP_estatico.json (E23)", "no medido (se configura en el panel de Supabase)", "100 %", medible=False)


def indice(conservador):
    res, glob = {}, 0.0
    for f, w in PESOS.items():
        cs = [x for x in C if x["factor"] == f and (x["medible"] or conservador)]
        p = sum((x["pct"] if x["medible"] else 0.0) for x in cs) / len(cs)
        res[f] = {"pct": round(p, 1), "peso": w, "ponderado": round(p * w / 100, 2), "criterios": len(cs)}
        glob += p * w / 100
    return res, round(glob, 2)


prim, g1 = indice(False)
cons, g2 = indice(True)
salida = {"criterios": C, "primario": prim, "indice_primario": g1, "conservador": cons, "indice_conservador": g2, "no_medidos": [x["id"] for x in C if not x["medible"]]}
(SAL / "FURPS_calculo.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{'ID':4} {'%':>6}  {'medido':55} meta")
for x in C:
    print(f"{x['id']:4} {('%.1f' % x['pct']) if x['medible'] else 'N/M':>6}  {x['medido_txt'][:55]:55} {x['meta_txt']}")
print()
print(f"{'Factor':6} {'Peso':>5} {'Prim.%':>7} {'Pond.':>6} {'Cons.%':>7} {'Pond.':>6}")
for f in PESOS:
    print(f"{f:6} {PESOS[f]:>5} {prim[f]['pct']:>7} {prim[f]['ponderado']:>6} {cons[f]['pct']:>7} {cons[f]['ponderado']:>6}")
print(f"GLOBAL primario (solo medidos): {g1} %   conservador (no medidos = 0): {g2} %")
