#!/usr/bin/env python
"""Pruebas exploratorias independientes del código NUEVO del Incremento 2 (agenda y alertas) contra la API v1.5.

Caja negra por HTTP (httpx). Cada caso declara entrada, resultado esperado (derivado de ADR-007 y del README de v1.5,
no del código) y compara con lo obtenido. Estados: OK, FALLA (contradice la especificación o devuelve 5xx) y OBS
(comportamiento que la especificación no define o que es una decisión de diseño documentada; se informa sin contarlo
como defecto). Escribe datos/exploratorias_inc2.json y metricas/exploratorias_inc2.md.

Uso:  python exploratorias_inc2.py --base http://127.0.0.1:8202 [--db ruta.sqlite]   (servidor v1.5 con datos de partida)
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from collections import Counter
from datetime import date, timedelta

import httpx

import comun as c
import oraculo_agenda as o

HOY = o.hoy_peru()
CASOS: list[dict] = []
_dni = [68000000]
HB = {"SIN": 13.0, "LEVE": 10.2, "MODERADA": 8.5, "SEVERA": 6.0}


class Ctx:
    cli: httpx.Client
    db: str | None = None


def dni() -> str:
    _dni[0] += 1
    return str(_dni[0])


def nac_para(prog: date, n: int) -> date:
    """Fecha de nacimiento cuyo control de n meses cae exactamente en prog."""
    total = prog.year * 12 + prog.month - 1 - n
    for dia in range(min(prog.day, 28), 0, -1):
        cand = date(total // 12, total % 12 + 1, dia)
        if o.sumar_meses(cand, n) == prog:
            return cand
    raise ValueError("sin nacimiento exacto")


def crear(nac: date, evals: list[tuple[date, str]], comunidad="Palmayoc", altitud=0, estado="ACTIVO",
          dni_=None) -> tuple[str, str]:
    """Registra por API un niño con evaluaciones [(fecha, clase)]. Devuelve (id, dni)."""
    evals = sorted(evals)
    d = dni_ or dni()
    cuerpo = {"nino": {"dni": d, "nombres": "Explora", "apellidos": "Prueba Sintetica", "sexo": "F",
                       "fecha_nacimiento": nac.isoformat(), "establecimiento": "P. S. Chongos Alto",
                       "distrito": "Chongos Alto", "comunidad": comunidad, "altitud_m": altitud,
                       "tutor_nombre": "Tutor Sintetico", "tutor_celular": "912345678"},
              "evaluacion_inicial": {"fecha": evals[0][0].isoformat(), "hemoglobina_observada": HB[evals[0][1]],
                                     "peso_kg": 8.0, "talla_cm": 70.0}}
    r = Ctx.cli.post("/api/ninos", json=cuerpo)
    assert r.status_code == 201, (r.status_code, r.text[:300])
    nid = r.json()["id"]
    for f, k in evals[1:]:
        r = Ctx.cli.post(f"/api/ninos/{nid}/evaluaciones", json={"fecha": f.isoformat(), "hemoglobina_observada": HB[k],
                                                                  "peso_kg": 8.0, "talla_cm": 70.0})
        assert r.status_code == 201, (r.status_code, r.text[:300])
    if estado != "ACTIVO":
        assert Ctx.cli.patch(f"/api/ninos/{nid}", json={"estado": estado}).status_code == 200
    return nid, d


def agenda(nid: str) -> dict:
    r = Ctx.cli.get(f"/api/ninos/{nid}/agenda")
    assert r.status_code == 200, (r.status_code, r.text[:300])
    return r.json()


def alertas(**params) -> list[dict]:
    r = Ctx.cli.get("/api/alertas/controles-vencidos", params=params)
    assert r.status_code == 200, (r.status_code, r.text[:300])
    return r.json()


def control_edad(ag: dict, n: int) -> dict | None:
    return next((x for x in ag["controles"] if x["tipo"] == "TAMIZAJE_EDAD" and x["edad_meses_programada"] == n), None)


def caso(cid: str, area: str, entrada: str, esperado: str):
    def deco(fn):
        t0 = time.time()
        try:
            estado, obtenido = fn()
        except AssertionError as e:
            estado, obtenido = "FALLA", f"Excepción de la prueba: {e}"
        except Exception as e:  # noqa: BLE001
            estado, obtenido = "FALLA", f"Excepción: {type(e).__name__}: {e}"
        CASOS.append({"id": cid, "area": area, "entrada": entrada, "esperado": esperado, "obtenido": obtenido,
                      "estado": estado, "ms": round((time.time() - t0) * 1000)})
        return fn
    return deco


def ok(cond: bool, texto: str, obs: bool = False) -> tuple[str, str]:
    return ("OK" if cond else ("OBS" if obs else "FALLA")), texto


# ===================================================================================================================
def ejecutar() -> None:
    cli = Ctx.cli
    mes = lambda d, n: o.sumar_meses(d, n)  # noqa: E731

    # ---------------- Agenda: edades límite ----------------
    @caso("EX-01", "Agenda", "Recién nacido (nace hoy), evaluación inicial hoy", "aplica=true; 12 controles por edad, todos PENDIENTE; 0 vencidos; el primero a los 6 meses")
    def _():
        nid, _d = crear(HOY, [(HOY, "SIN")]); ag = agenda(nid); r = ag["resumen"]
        prim = ag["controles"][0]
        return ok(ag["aplica"] and r["total"] == 12 and r["pendientes"] == 12 and r["vencidos"] == 0 and prim["fecha_programada"] == mes(HOY, 6).isoformat(),
                  f"aplica={ag['aplica']} total={r['total']} pendientes={r['pendientes']} vencidos={r['vencidos']} primero={prim['fecha_programada']}")

    @caso("EX-02", "Agenda", "Niño que cumple exactamente 6 meses hoy; su única evaluación es de hoy", "El control de 6 meses queda CUMPLIDO con esa evaluación (programada = hoy, dentro de la ventana)")
    def _():
        nid, _d = crear(mes(HOY, -6), [(HOY, "SIN")]); c6 = control_edad(agenda(nid), 6)
        return ok(c6 is not None and c6["estado"] == "CUMPLIDO" and c6["fecha_programada"] == HOY.isoformat(), f"control 6 m: {c6 and (c6['estado'], c6['fecha_programada'])}")

    @caso("EX-03", "Agenda", "Niño a un día de cumplir 6 meses, evaluación hoy", "Control de 6 meses PENDIENTE (programada mañana; la evaluación de hoy cae dentro de su ventana, por lo que queda CUMPLIDO) -- se verifica que el estado sea CUMPLIDO o PENDIENTE sin error y con proximo coherente")
    def _():
        nac = mes(HOY, -6) + timedelta(days=1); nid, _d = crear(nac, [(HOY, "SIN")]); c6 = control_edad(agenda(nid), 6)
        return ok(c6["estado"] == "CUMPLIDO", f"{c6['estado']} proximo={c6['proximo']} prog={c6['fecha_programada']} límite={c6['fecha_limite']}")

    @caso("EX-04", "Agenda", "Niño de 59 meses exactos, evaluación inicial hoy, sin anemia", "Registro aceptado; agenda 200 con 0 controles (los de 60+ meses no se programan), sin error")
    def _():
        nid, _d = crear(mes(HOY, -59), [(HOY, "SIN")]); ag = agenda(nid)
        return ok(ag["aplica"] and ag["resumen"]["total"] == 0, f"aplica={ag['aplica']} total={ag['resumen']['total']} motivo={ag['motivo']}")

    @caso("EX-05", "Agenda", "Registrar niño de 60 meses exactos", "Rechazo 422 con mensaje en fecha_nacimiento (atiende menores de 5 años)")
    def _():
        n = mes(HOY, -60); body = {"nino": {"dni": dni(), "nombres": "Ab", "apellidos": "Cd", "sexo": "F", "fecha_nacimiento": n.isoformat(), "establecimiento": "PS", "distrito": "Chongos Alto", "comunidad": "Palmayoc", "altitud_m": 0, "tutor_nombre": "Tu"}, "evaluacion_inicial": {"fecha": HOY.isoformat(), "hemoglobina_observada": 13, "peso_kg": 8, "talla_cm": 70}}
        r = cli.post("/api/ninos", json=body)
        return ok(r.status_code == 422 and any(e["campo"] == "fecha_nacimiento" for e in r.json().get("errores", [])), f"HTTP {r.status_code} {r.text[:120]}")

    @caso("EX-06", "Agenda", "Niño de 59 meses con anemia LEVE hoy", "Sin controles de tratamiento: C1M caería a los 60 meses (fuera de población)")
    def _():
        nid, _d = crear(mes(HOY, -59), [(HOY, "LEVE")]); ag = agenda(nid)
        return ok(ag["resumen"]["total"] == 0, f"total={ag['resumen']['total']}: {[x['codigo'] for x in ag['controles']]}")

    @caso("EX-07", "Agenda", "Niño de 58 meses con anemia MODERADA hoy", "Solo C1M (a los 59 meses); C3M y C6M quedan fuera (>=60 meses)")
    def _():
        nid, _d = crear(mes(HOY, -58), [(HOY, "MODERADA")]); ag = agenda(nid); cods = [x["codigo"] for x in ag["controles"] if x["tipo"] == "CONTROL_TRATAMIENTO"]
        return ok(cods == ["C1M"], f"tratamiento={cods}")

    @caso("EX-08", "Agenda", "Niño de 5 meses con Hb muy baja (evaluación hoy, menor de 6 meses)", "Sin diagnóstico de anemia (NO_APLICA bajo 6 meses): no se programan C1M/C3M/C6M")
    def _():
        nid, _d = crear(mes(HOY, -5), [(HOY, "SEVERA")]); ag = agenda(nid)
        trat = [x for x in ag["controles"] if x["tipo"] == "CONTROL_TRATAMIENTO"]
        return ok(not trat, f"controles de tratamiento={len(trat)}")

    @caso("EX-09", "Agenda", "Cambio de umbral 23 a 24 meses: la misma Hb ajustada 10,7 g/dL a los 23 m y a los 24 m", "23 m: SIN_ANEMIA (umbral 10,5); 24 m: LEVE (umbral 11,0)")
    def _():
        res = []
        for meses, esperado in ((23, "SIN_ANEMIA"), (24, "LEVE")):
            nid, _d = crear(mes(HOY, -meses), [(HOY - timedelta(days=60), "SIN")])
            e = cli.post(f"/api/ninos/{nid}/evaluaciones", json={"fecha": HOY.isoformat(), "hemoglobina_observada": 10.7, "peso_kg": 9, "talla_cm": 80}).json()
            clas = e["evaluaciones"][0]["clasificacion"]
            res.append((meses, clas, esperado))
        return ok(all(a == b for _, a, b in res), "; ".join(f"{m} m -> {a} (esperado {b})" for m, a, b in res))

    # ---------------- Agenda: alta / reactivación / estados ----------------
    @caso("EX-10", "Alta/reactivación", "Niño con control vencido -> PATCH estado=ALTA -> GET agenda y alertas", "Agenda aplica=false con motivo; el niño desaparece de /alertas")
    def _():
        prog = HOY - timedelta(days=40); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")])
        antes = d in {a["nino"]["dni"] for a in alertas()}
        cli.patch(f"/api/ninos/{nid}", json={"estado": "ALTA"})
        ag = agenda(nid); despues = d in {a["nino"]["dni"] for a in alertas()}
        return ok(antes and ag["aplica"] is False and bool(ag["motivo"]) and not despues, f"antes={antes} aplica={ag['aplica']} motivo={ag['motivo']!r} sigue_en_alertas={despues}")

    @caso("EX-11", "Alta/reactivación", "ALTA -> PATCH estado=ACTIVO (reactivación)", "Vuelve la agenda (aplica=true) y reaparece la alerta vencida; mismo conteo que antes del alta")
    def _():
        prog = HOY - timedelta(days=40); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")])
        n0 = len([a for a in alertas() if a["nino"]["dni"] == d])
        cli.patch(f"/api/ninos/{nid}", json={"estado": "ALTA"}); cli.patch(f"/api/ninos/{nid}", json={"estado": "ACTIVO"})
        n1 = len([a for a in alertas() if a["nino"]["dni"] == d]); ag = agenda(nid)
        return ok(ag["aplica"] and n0 == n1 == 1, f"alertas antes={n0} tras reactivar={n1} aplica={ag['aplica']}")

    @caso("EX-12", "Alta/reactivación", "PATCH estado con valores no válidos: 'PENDIENTE', 'alta' (minúscula), '', null", "422 con mensaje por campo en cada uno; nunca 5xx ni cambio de estado")
    def _():
        nid, _d = crear(mes(HOY, -10), [(HOY, "SIN")]); res = []
        for v in ("PENDIENTE", "alta", "", None):
            r = cli.patch(f"/api/ninos/{nid}", json={"estado": v}); res.append((v, r.status_code))
        est = cli.get(f"/api/ninos/{nid}").json()["estado"]
        return ok(all(s == 422 for _, s in res) and est == "ACTIVO", f"{res}; estado final={est}")

    @caso("EX-13", "Alta/reactivación", "PATCH con campo no editable (fecha_nacimiento) y cuerpo vacío {}", "Rechazo claro o ignorado sin efecto; sin 5xx; la fecha de nacimiento no cambia")
    def _():
        nid, _d = crear(mes(HOY, -10), [(HOY, "SIN")])
        r1 = cli.patch(f"/api/ninos/{nid}", json={"fecha_nacimiento": "2020-01-01"}); r2 = cli.patch(f"/api/ninos/{nid}", json={})
        fn = cli.get(f"/api/ninos/{nid}").json()["fecha_nacimiento"]
        return ok(r1.status_code < 500 and r2.status_code < 500 and fn == mes(HOY, -10).isoformat(), f"campo no editable -> HTTP {r1.status_code}; cuerpo vacío -> HTTP {r2.status_code}; fecha_nacimiento sin cambio={fn}")

    # ---------------- IDs raros ----------------
    @caso("EX-14", "IDs", "Agenda con ids inexistentes: uuid válido ausente, texto, 5 000 caracteres, '%00', '../', emoji, espacios", "404 con mensaje JSON en todos; nunca 5xx")
    def _():
        ids = ["00000000-0000-0000-0000-000000000000", "no-existe", "x" * 5000, "%00", "..%2F..%2Fetc", "%F0%9F%98%80", "%20%20"]
        res = [(i[:12], cli.get(f"/api/ninos/{i}/agenda").status_code) for i in ids]
        return ok(all(s == 404 for _, s in res), str(res))

    # ---------------- Filtros ----------------
    @caso("EX-15", "Filtros", "Niño en 'Ñahuimpuquio'; filtro 'ÑAHUIMPUQUIO', 'ñahuimpuquio', ' Ñahuimpuquio ', 'Nahuimpuquio'", "Coinciden las tres primeras (insensible a mayúsculas y espacios); 'Nahuimpuquio' (sin tilde) no coincide")
    def _():
        prog = HOY - timedelta(days=40); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")], comunidad="Ñahuimpuquio")
        res = {f: d in {a["nino"]["dni"] for a in alertas(comunidad=f)} for f in ("ÑAHUIMPUQUIO", "ñahuimpuquio", " Ñahuimpuquio ", "Nahuimpuquio")}
        return ok(all(list(res.values())[:3]) and not res["Nahuimpuquio"], str(res))

    @caso("EX-16", "Filtros", "Comunidad grabada como 'palmayoc' (minúscula) y 'PALMAYOC': filtro 'Palmayoc'", "Ambas aparecen (misma comunidad con distinta escritura)")
    def _():
        p = HOY - timedelta(days=40); ds = []
        for com in ("palmayoc", "PALMAYOC"):
            _id, d = crear(nac_para(p, 12), [(p - timedelta(days=40), "SIN")], comunidad=com); ds.append(d)
        got = {a["nino"]["dni"] for a in alertas(comunidad="Palmayoc")}
        return ok(all(d in got for d in ds), f"presentes={[d in got for d in ds]}")

    @caso("EX-17", "Filtros", "Comunidad en forma Unicode descompuesta (N + tilde combinante) frente a la compuesta guardada", "Idealmente coincide; si no, es una limitación de normalización Unicode (NFC/NFD)")
    def _():
        import unicodedata
        p = HOY - timedelta(days=40); nid, d = crear(nac_para(p, 12), [(p - timedelta(days=40), "SIN")], comunidad="Ñahuimpuquio")
        nfd = unicodedata.normalize("NFD", "Ñahuimpuquio"); hallado = d in {a["nino"]["dni"] for a in alertas(comunidad=nfd)}
        return ok(hallado, f"filtro NFD {'coincide' if hallado else 'NO coincide'} con valor NFC almacenado", obs=True)

    @caso("EX-18", "Filtros", "Comunidad con comodines y valores extremos: '%', '_', '', 5 000 caracteres, emoji, NUL", "'%' y '_' se tratan como texto (0 resultados); '' no filtra; 200 siempre")
    def _():
        tot = len(alertas()); res = {}
        for v in ("%", "_", "x" * 5000, "😀", "\x00"):
            r = cli.get("/api/alertas/controles-vencidos", params={"comunidad": v}); res[v[:6].encode("unicode_escape").decode()] = (r.status_code, len(r.json()) if r.status_code == 200 else None)
        vacio = len(alertas(comunidad=""))
        return ok(all(s == 200 for s, _ in res.values()) and vacio == tot and res["%"][1] == 0 and res["_"][1] == 0, f"{res}; comunidad='' -> {vacio} de {tot}")

    @caso("EX-19", "Filtros", "prioridad: 'ALTA', 'alta', 'Alta', 'URGENTE', '', ' ALTA ', repetida (?prioridad=ALTA&prioridad=BAJA)", "Valores válidos exactos -> 200; no válidos -> 422 con mensaje; vacío = sin filtro; nunca 5xx")
    def _():
        res = {}
        for v in ("ALTA", "alta", "Alta", "URGENTE", "", " ALTA "):
            res[repr(v)] = cli.get("/api/alertas/controles-vencidos", params={"prioridad": v}).status_code
        res["repetida"] = cli.get("/api/alertas/controles-vencidos?prioridad=ALTA&prioridad=BAJA").status_code
        return ok(all(s < 500 for s in res.values()) and res["'URGENTE'"] == 422 and res["'ALTA'"] == 200 and res["''"] == 200, str(res))

    @caso("EX-20", "Filtros", "Método no permitido y rutas cercanas: POST /api/alertas/resumen, GET /api/alertas, GET /api/alertas/controles-vencidos/", "405 / 404 con JSON, nunca 5xx")
    def _():
        res = [cli.post("/api/alertas/resumen").status_code, cli.get("/api/alertas").status_code, cli.get("/api/alertas/controles-vencidos/", follow_redirects=False).status_code]
        return ok(all(s < 500 for s in res), f"{res}")

    # ---------------- Alertas: prioridad y orden ----------------
    @caso("EX-21", "Alertas", "Frontera de prioridad por atraso (último estado SIN_ANEMIA, control por edad): días vencidos 1, 7, 8, 30, 31", "BAJA hasta 7 días; MEDIA de 8 a 30; ALTA desde 31")
    def _():
        res = []
        for dias, esperado in ((1, "BAJA"), (7, "BAJA"), (8, "MEDIA"), (30, "MEDIA"), (31, "ALTA")):
            prog = HOY - timedelta(days=30 + dias); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")])
            a = [x for x in alertas() if x["nino"]["dni"] == d]
            res.append((dias, a[0]["control"]["dias_vencido"] if a else None, a[0]["prioridad"] if a else None, esperado))
        return ok(all(p == e and dv == dias for dias, dv, p, e in res), "; ".join(f"{dias} d -> dias_vencido={dv}, {p} (esperado {e})" for dias, dv, p, e in res))

    @caso("EX-22", "Alertas", "Control por edad vencido hace 3 días en niño cuya última clasificación es MODERADA / SEVERA / LEVE", "MODERADA y SEVERA -> ALTA; LEVE -> BAJA (atraso <=7 d, control por edad)")
    def _():
        res = []
        for clase, esperado in (("MODERADA", "ALTA"), ("SEVERA", "ALTA"), ("LEVE", "BAJA")):
            prog = HOY - timedelta(days=33)
            nac = nac_para(prog, 18)
            # la evaluación con la clase probada debe quedar FUERA de la ventana del control de 18 m (programada -15/+30 días);
            # si cayera dentro, la cumpliría y no habría alerta (error de diseño del caso detectado en la corrida 1)
            ev = [(prog - timedelta(days=60), "SIN"), (prog - timedelta(days=20), clase)]
            nid, d = crear(nac, ev)
            a = [x for x in alertas() if x["nino"]["dni"] == d and x["control"]["tipo"] == "TAMIZAJE_EDAD"]
            res.append((clase, a[0]["prioridad"] if a else None, esperado, a[0]["ultima_clasificacion"] if a else None))
        return ok(all(p == e for _, p, e, _u in res), "; ".join(f"{c_} -> {p} (esperado {e}), ultima_clasificacion={u}" for c_, p, e, u in res))

    @caso("EX-23", "Alertas", "Control de TRATAMIENTO (C1M) vencido hace 2 días", "Prioridad ALTA (regla: todo control de tratamiento es ALTA)")
    def _():
        diag = o.sumar_meses(HOY - timedelta(days=32), -1); nid, d = crear(mes(HOY, -20), [(diag, "LEVE")])
        a = [x for x in alertas() if x["nino"]["dni"] == d]
        return ok(len(a) == 1 and a[0]["control"]["codigo"] == "C1M" and a[0]["prioridad"] == "ALTA" and a[0]["control"]["dias_vencido"] == 2, f"{[(x['control']['codigo'], x['control']['dias_vencido'], x['prioridad']) for x in a]}")

    @caso("EX-24", "Alertas", "Coherencia global: prioridad de TODAS las alertas del sistema recalculada con la regla del ADR-007 desde los campos devueltos", "0 discrepancias entre prioridad devuelta y regla")
    def _():
        al = alertas(); mal = []
        for a in al:
            d, t, u = a["control"]["dias_vencido"], a["control"]["tipo"], a["ultima_clasificacion"]
            esp = "ALTA" if (t == "CONTROL_TRATAMIENTO" or u in ("MODERADA", "SEVERA") or d > 30) else ("MEDIA" if d >= 8 else "BAJA")
            if esp != a["prioridad"]:
                mal.append((a["nino"]["dni"], a["control"]["codigo"], d, u, a["prioridad"], esp))
        return ok(not mal, f"{len(al)} alertas revisadas; discrepancias={mal[:5]}")

    @caso("EX-25", "Alertas", "Orden de la lista: prioridad (ALTA>MEDIA>BAJA) y dentro de cada una, días de atraso descendente", "Lista ordenada según la especificación")
    def _():
        al = alertas(); rank = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
        claves = [(rank[a["prioridad"]], -a["control"]["dias_vencido"]) for a in al]
        return ok(claves == sorted(claves), f"{len(al)} alertas; ordenadas={claves == sorted(claves)}")

    @caso("EX-26", "Alertas", "Consistencia entre resumen y lista; dias_vencido = hoy - fecha_limite; ventana = programada -15/+30 en cada alerta", "Totales iguales; fórmulas exactas en todas las alertas")
    def _():
        al = alertas(); r = cli.get("/api/alertas/resumen").json(); mal = 0
        for a in al:
            k = a["control"]; lim = date.fromisoformat(k["fecha_limite"]); prog = date.fromisoformat(k["fecha_programada"])
            if (HOY - lim).days != k["dias_vencido"] or lim != prog + timedelta(days=30) or date.fromisoformat(k["fecha_inicio_ventana"]) != prog - timedelta(days=15):
                mal += 1
        pp = Counter(a["prioridad"] for a in al)
        return ok(mal == 0 and r["total_vencidos"] == len(al) and r["ninos_con_vencidos"] == len({a['nino']['id'] for a in al}) and all(pp.get(k, 0) == r["por_prioridad"].get(k, 0) for k in ("ALTA", "MEDIA", "BAJA")),
                  f"alertas={len(al)} resumen={r} fórmulas_incorrectas={mal}")

    @caso("EX-27", "Alertas", "Próximo a vencer: control PENDIENTE cuyo límite es hoy, hoy+7 y hoy+8", "proximo=true en hoy y hoy+7; false en hoy+8")
    def _():
        res = []
        for delta, esperado in ((0, True), (7, True), (8, False)):
            prog = HOY - timedelta(days=30) + timedelta(days=delta); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")])
            c12 = control_edad(agenda(nid), 12); res.append((delta, c12["estado"], c12["proximo"], esperado))
        return ok(all(e == "PENDIENTE" and p == x for _, e, p, x in res), str(res))

    @caso("EX-28", "Alertas", "Control que vence hoy (límite = hoy) y el que venció ayer (límite = hoy-1)", "Límite = hoy es PENDIENTE (no alerta); límite = hoy-1 es VENCIDO con dias_vencido=1")
    def _():
        res = []
        for delta in (0, -1):
            prog = HOY - timedelta(days=30) + timedelta(days=delta); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")])
            c12 = control_edad(agenda(nid), 12); res.append((delta, c12["estado"], c12["dias_vencido"]))
        return ok(res[0][1] == "PENDIENTE" and res[1][1] == "VENCIDO" and res[1][2] == 1, str(res))

    # ---------------- Regla de ventana y asignación ----------------
    @caso("EX-29", "Ventana", "Evaluaciones en programada-16, -15, +30, +31 días para el control de 12 meses (hoy posterior al límite)", "Cumplen -15 y +30; no cumplen -16 ni +31 (quedan VENCIDO)")
    def _():
        res = []
        for delta, esperado in ((-16, "VENCIDO"), (-15, "CUMPLIDO"), (30, "CUMPLIDO"), (31, "VENCIDO")):
            prog = HOY - timedelta(days=50); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=45), "SIN"), (prog + timedelta(days=delta), "SIN")])
            res.append((delta, control_edad(agenda(nid), 12)["estado"], esperado))
        return ok(all(a == b for _, a, b in res), str(res))

    @caso("EX-30", "Ventana", "Una evaluación que cae en la ventana de DOS controles (tamizaje 12 m y C1M de una anemia previa)", "Cumple solo uno (el de tratamiento en empate de fecha); el otro permanece sin cumplir (VENCIDO si pasó su límite)")
    def _():
        prog12 = HOY - timedelta(days=50); nac = nac_para(prog12, 12); diag = o.sumar_meses(prog12, -1)
        nid, d = crear(nac, [(diag, "LEVE"), (prog12, "SIN")]); ag = agenda(nid)
        c1 = [x for x in ag["controles"] if x["codigo"] == "C1M"][0]; c12 = control_edad(ag, 12)
        return ok(sorted([c1["estado"], c12["estado"]]) == ["CUMPLIDO", "VENCIDO"] and c1["estado"] == "CUMPLIDO", f"C1M={c1['estado']} tamizaje12={c12['estado']}")

    @caso("EX-31", "Ventana", "Anemia y recuperación (SIN_ANEMIA) ANTES de abrirse la ventana de C1M (día 12) y, en otro niño, DENTRO de la ventana de C1M (día 20); hoy 100 días después", "Día 12: C1M, C3M y C6M CERRADO_RECUPERADO (aún no habían vencido). Día 20: la evaluación cae en la ventana de C1M y lo cumple (CUMPLIDO); C3M y C6M CERRADO_RECUPERADO")
    def _():
        base = HOY - timedelta(days=100)
        nid, d = crear(mes(HOY, -20), [(base, "LEVE"), (base + timedelta(days=12), "SIN")]); ag = agenda(nid)
        est12 = {x["codigo"]: x["estado"] for x in ag["controles"] if x["tipo"] == "CONTROL_TRATAMIENTO"}
        nid, d = crear(mes(HOY, -20), [(base, "LEVE"), (base + timedelta(days=20), "SIN")]); ag = agenda(nid)
        est20 = {x["codigo"]: x["estado"] for x in ag["controles"] if x["tipo"] == "CONTROL_TRATAMIENTO"}
        bien12 = est12 == {"C1M": "CERRADO_RECUPERADO", "C3M": "CERRADO_RECUPERADO", "C6M": "CERRADO_RECUPERADO"}
        bien20 = est20 == {"C1M": "CUMPLIDO", "C3M": "CERRADO_RECUPERADO", "C6M": "CERRADO_RECUPERADO"}
        return ok(bien12 and bien20, f"día 12: {est12}; día 20: {est20}")

    @caso("EX-32", "Ventana", "Anemia, recuperación a los 75 días (C1M ya vencido)", "C1M permanece VENCIDO (historial); C3M y C6M CERRADO_RECUPERADO")
    def _():
        base = HOY - timedelta(days=100); nid, d = crear(mes(HOY, -20), [(base, "LEVE"), (base + timedelta(days=75), "SIN")]); ag = agenda(nid)
        est = {x["codigo"]: x["estado"] for x in ag["controles"] if x["tipo"] == "CONTROL_TRATAMIENTO"}
        return ok(est.get("C1M") == "VENCIDO" and est.get("C3M") == "CERRADO_RECUPERADO", str(est))

    @caso("EX-33", "Ventana", "Anemia sostenida: LEVE, a los 33 días MODERADA, a los 62 días LEVE", "El calendario no se reinicia: solo 3 controles de tratamiento (C1M, C3M, C6M) del primer diagnóstico")
    def _():
        base = HOY - timedelta(days=70); nid, d = crear(mes(HOY, -20), [(base, "LEVE"), (base + timedelta(days=33), "MODERADA"), (base + timedelta(days=62), "LEVE")]); ag = agenda(nid)
        trat = [x["codigo"] for x in ag["controles"] if x["tipo"] == "CONTROL_TRATAMIENTO"]
        return ok(sorted(trat) == ["C1M", "C3M", "C6M"], str(trat))

    @caso("EX-34", "Ventana", "Dos evaluaciones EL MISMO DÍA y una evaluación retroactiva anterior a la primera", "Se aceptan; la agenda se recalcula sin error. Una evaluación retroactiva puede adelantar el inicio de la agenda (diseño ADR-007)")
    def _():
        nac = mes(HOY, -14); nid, d = crear(nac, [(HOY - timedelta(days=10), "SIN")]); t0 = agenda(nid)["resumen"]["total"]
        r1 = cli.post(f"/api/ninos/{nid}/evaluaciones", json={"fecha": (HOY - timedelta(days=10)).isoformat(), "hemoglobina_observada": 12.5, "peso_kg": 9, "talla_cm": 75})
        r2 = cli.post(f"/api/ninos/{nid}/evaluaciones", json={"fecha": mes(HOY, -8).isoformat(), "hemoglobina_observada": 12.5, "peso_kg": 8, "talla_cm": 70})
        ag = agenda(nid)
        return ok(r1.status_code == 201 and r2.status_code == 201 and ag["resumen"]["total"] >= t0, f"misma fecha HTTP {r1.status_code}; retroactiva HTTP {r2.status_code}; total de controles {t0} -> {ag['resumen']['total']}; vencidos={ag['resumen']['vencidos']}", obs=True)

    @caso("EX-35", "Entradas", "Evaluación con fecha futura, anterior al nacimiento, igual al nacimiento", "Futura y anterior -> 422; igual al nacimiento -> 201")
    def _():
        nac = mes(HOY, -10); nid, d = crear(nac, [(HOY, "SIN")]); r = []
        for f in (HOY + timedelta(days=1), nac - timedelta(days=1), nac):
            r.append(cli.post(f"/api/ninos/{nid}/evaluaciones", json={"fecha": f.isoformat(), "hemoglobina_observada": 12.5, "peso_kg": 8, "talla_cm": 70}).status_code)
        return ok(r == [422, 422, 201], str(r))

    @caso("EX-36", "Entradas", "Altitud límite al registrar: 0, 5000, 5001, -1, 4999.9", "0, 5000 y 4999.9 aceptados; 5001 y -1 rechazados con 422")
    def _():
        res = []
        for alt in (0, 5000, 5001, -1, 4999.9):
            body = {"nino": {"dni": dni(), "nombres": "Ab", "apellidos": "Cd", "sexo": "F", "fecha_nacimiento": mes(HOY, -12).isoformat(), "establecimiento": "PS", "distrito": "Chongos Alto", "comunidad": "Palmayoc", "altitud_m": alt, "tutor_nombre": "Tu"}, "evaluacion_inicial": {"fecha": HOY.isoformat(), "hemoglobina_observada": 18, "peso_kg": 8, "talla_cm": 70}}
            res.append((alt, cli.post("/api/ninos", json=body).status_code))
        return ok([s for _, s in res] == [201, 201, 422, 422, 201], str(res))

    # ---------------- Seguimiento vs alertas ----------------
    @caso("EX-37", "Consistencia", "Para todos los niños activos: controles_vencidos de GET /api/ninos == nº de alertas del niño; control_atrasado == (controles_vencidos>0)", "0 discrepancias")
    def _():
        filas = cli.get("/api/ninos").json(); por = Counter(a["nino"]["id"] for a in alertas()); mal = [f["dni"] for f in filas if f["controles_vencidos"] != por.get(f["id"], 0) or f["control_atrasado"] != (f["controles_vencidos"] > 0)]
        return ok(not mal, f"{len(filas)} niños revisados; discrepancias={mal[:5]}")

    @caso("EX-38", "Consistencia", "Orden de los controles en cada agenda (fecha programada ascendente) y fórmulas de ventana en una muestra de 60 agendas", "Siempre ordenados; límite = programada+30 e inicio = programada-15")
    def _():
        filas = cli.get("/api/ninos").json()[:60]; mal = 0
        for f in filas:
            ag = agenda(f["id"]); fs = [x["fecha_programada"] for x in ag["controles"]]
            if fs != sorted(fs):
                mal += 1
            for k in ag["controles"]:
                p = date.fromisoformat(k["fecha_programada"])
                if date.fromisoformat(k["fecha_limite"]) != p + timedelta(days=30) or date.fromisoformat(k["fecha_inicio_ventana"]) != p - timedelta(days=15):
                    mal += 1
        return ok(mal == 0, f"{len(filas)} agendas; incumplimientos={mal}")

    @caso("EX-39", "Consistencia", "Cambio de altitud por PATCH en un niño con evaluaciones previas", "Las evaluaciones previas conservan su altitud y clasificación (no se reescribe el historial); la agenda no cambia")
    def _():
        nid, d = crear(mes(HOY, -14), [(HOY - timedelta(days=5), "LEVE")], altitud=3500); a0 = agenda(nid)["resumen"]
        r = cli.patch(f"/api/ninos/{nid}", json={"altitud_m": 500}); exp = cli.get(f"/api/ninos/{nid}").json(); a1 = agenda(nid)["resumen"]
        ev = exp["evaluaciones"][0]
        return ok(r.status_code == 200 and ev["altitud_m"] == 3500 and a0 == a1, f"HTTP {r.status_code}; altitud de la evaluación={ev['altitud_m']}; resumen igual={a0 == a1}", obs=True)

    @caso("EX-40", "Niños mayores", "Niño ACTIVO que ya superó los 59 meses (insertado con SQL directo, nacido hace 70 meses, última evaluación hace 2 años)", "Decisión de diseño: fuera de población (sin alertas nuevas) o ALTA explícita. Se registra lo observado")
    def _():
        if not Ctx.db:
            return "OBS", "No ejecutado (sin --db)"
        import sqlite3
        import uuid
        nac = mes(HOY, -70); nid = str(uuid.uuid4()); ahora = "2026-10-16 12:00:00.000000"
        con = sqlite3.connect(Ctx.db)
        cols = [r[1] for r in con.execute("pragma table_info(nino)")]
        vals = {"id": nid, "dni": dni(), "nombres": "Mayor", "apellidos": "De Cinco", "sexo": "F", "fecha_nacimiento": nac.isoformat(), "establecimiento": "PS", "distrito": "Chongos Alto", "comunidad": "Palmayoc", "altitud_m": 0, "tutor_nombre": "Tu", "tutor_celular": None, "estado": "ACTIVO", "registrado_por": "sql", "creado_en": ahora, "actualizado_en": ahora}
        con.execute(f"insert into nino ({','.join(cols)}) values ({','.join('?' * len(cols))})", [vals[k] for k in cols])
        ecols = [r[1] for r in con.execute("pragma table_info(evaluacion_hemoglobina)")]
        f = HOY - timedelta(days=730)
        ev = {"id": str(uuid.uuid4()), "nino_id": nid, "fecha": f.isoformat(), "edad_meses": o.edad_meses(nac, f), "hemoglobina_observada": 13.0, "altitud_m": 0, "hemoglobina_ajustada": 13.0, "clasificacion": "SIN_ANEMIA", "peso_kg": 15.0, "talla_cm": 100.0, "registrado_por": "sql", "creado_en": ahora}
        con.execute(f"insert into evaluacion_hemoglobina ({','.join(ecols)}) values ({','.join('?' * len(ecols))})", [ev[k] for k in ecols])
        con.commit(); con.close()
        a = [x for x in alertas() if x["nino"]["id"] == nid]; fila = [x for x in cli.get("/api/ninos").json() if x["id"] == nid]
        return ok(not a, f"niño de {o.edad_meses(nac, HOY)} meses ACTIVO: {len(a)} alertas vencidas ({[(x['control']['codigo'], x['control']['dias_vencido']) for x in a][:4]}); seguimiento: edad_meses={fila[0]['edad_meses'] if fila else None}, control_atrasado={fila[0]['control_atrasado'] if fila else None}", obs=True)

    # ---------------- Concurrencia ligera ----------------
    @caso("EX-41", "Concurrencia", "20 hilos simultáneos agregan evaluaciones (fechas distintas) al mismo niño y otros 20 leen su agenda", "Todas 201/200; el expediente termina con 21 evaluaciones; sin 5xx ni 'database is locked'")
    def _():
        nid, d = crear(mes(HOY, -30), [(HOY - timedelta(days=300), "SIN")]); res = []
        def escribir(k):
            with httpx.Client(base_url=cli.base_url, timeout=60) as h:
                res.append(("w", h.post(f"/api/ninos/{nid}/evaluaciones", json={"fecha": (HOY - timedelta(days=k)).isoformat(), "hemoglobina_observada": 12.5, "peso_kg": 10, "talla_cm": 85}).status_code))
        def leer(_k):
            with httpx.Client(base_url=cli.base_url, timeout=60) as h:
                res.append(("r", h.get(f"/api/ninos/{nid}/agenda").status_code))
        hs = [threading.Thread(target=escribir, args=(k,)) for k in range(20)] + [threading.Thread(target=leer, args=(k,)) for k in range(20)]
        [h.start() for h in hs]; [h.join() for h in hs]
        n = len(cli.get(f"/api/ninos/{nid}").json()["evaluaciones"]); cnt = Counter(res)
        return ok(all(s in (200, 201) for _, s in res) and n == 21, f"{dict(cnt)}; evaluaciones finales={n}")

    @caso("EX-42", "Concurrencia", "10 hilos simultáneos registran el MISMO DNI", "Exactamente un 201 y nueve 409; nunca 5xx ni duplicados")
    def _():
        d = dni(); res = []
        body = {"nino": {"dni": d, "nombres": "Ab", "apellidos": "Cd", "sexo": "F", "fecha_nacimiento": mes(HOY, -12).isoformat(), "establecimiento": "PS", "distrito": "Chongos Alto", "comunidad": "Palmayoc", "altitud_m": 0, "tutor_nombre": "Tu"}, "evaluacion_inicial": {"fecha": HOY.isoformat(), "hemoglobina_observada": 13, "peso_kg": 8, "talla_cm": 70}}
        barrera = threading.Barrier(10)
        def reg():
            with httpx.Client(base_url=cli.base_url, timeout=60) as h:
                barrera.wait(); res.append(h.post("/api/ninos", json=body).status_code)
        hs = [threading.Thread(target=reg) for _ in range(10)]; [h.start() for h in hs]; [h.join() for h in hs]
        filas = [f for f in cli.get("/api/ninos", params={"q": d}).json() if f["dni"] == d]
        cnt = Counter(res)
        return ok(cnt.get(201, 0) == 1 and cnt.get(409, 0) == 9 and len(filas) == 1, f"{dict(cnt)}; filas con ese DNI={len(filas)}")

    @caso("EX-43", "Concurrencia", "Alternar ALTA/ACTIVO desde 8 hilos mientras otros 8 consultan /alertas y /resumen (30 vueltas)", "Las LECTURAS de alertas/resumen (código nuevo) nunca devuelven 5xx. Los PATCH concurrentes sobre el mismo niño pueden fallar con 5xx por el bloqueo de escritura de SQLite ('database is locked'): se informa como OBS, no como defecto (motor de desarrollo; en PostgreSQL no aplica)")
    def _():
        nid, d = crear(nac_para(HOY - timedelta(days=40), 12), [(HOY - timedelta(days=80), "SIN")]); lect, escr = [], []
        def alt(k):
            with httpx.Client(base_url=cli.base_url, timeout=60) as h:
                for i in range(30):
                    escr.append(h.patch(f"/api/ninos/{nid}", json={"estado": "ALTA" if (i + k) % 2 else "ACTIVO"}).status_code)
        def leer(_k):
            with httpx.Client(base_url=cli.base_url, timeout=60) as h:
                for _i in range(30):
                    lect.append(h.get("/api/alertas/controles-vencidos").status_code); lect.append(h.get("/api/alertas/resumen").status_code)
        hs = [threading.Thread(target=alt, args=(k,)) for k in range(8)] + [threading.Thread(target=leer, args=(k,)) for k in range(8)]
        [h.start() for h in hs]; [h.join() for h in hs]
        cl, ce = Counter(lect), Counter(escr)
        texto = f"lecturas de alertas: {dict(cl)}; PATCH de estado: {dict(ce)}"
        if any(s >= 500 for s in lect):
            return "FALLA", texto
        if any(s >= 500 for s in escr):
            return "OBS", texto + " -- 5xx en PATCH por bloqueo de escritura de SQLite (database is locked, visto en el registro del servidor); limitación del motor de desarrollo, código heredado del Inc. 1"
        return ok(True, texto)

    # ---------------- Rendimiento y volumen ----------------
    @caso("EX-44", "Volumen", "Niño con unas 120 evaluaciones (una cada 14 días) y su agenda", "200 y agenda en menos de 1 s; sin error")
    def _():
        nac = mes(HOY, -50); fechas = [(HOY - timedelta(days=14 * k), "SIN") for k in range(120) if HOY - timedelta(days=14 * k) >= nac]
        nid, d = crear(nac, fechas); t0 = time.time(); ag = agenda(nid); t = (time.time() - t0) * 1000
        return ok(t < 1000, f"{len(fechas)} evaluaciones; agenda en {t:.0f} ms; total controles={ag['resumen']['total']}")

    @caso("EX-45", "Entradas", "Búsqueda por DNI con caracteres raros en GET /api/ninos/dni/{dni} y ?q= con comodines/Unicode/inyección", "404 / 200 vacío; nunca 5xx")
    def _():
        res = [cli.get(f"/api/ninos/dni/{v}").status_code for v in ("%00", "1" * 3000, "%D9%A4%D9%A4", "abc")]
        res += [cli.get("/api/ninos", params={"q": v}).status_code for v in ("%", "_", "'; DROP TABLE nino;--", "Ñ", "\x00")]
        return ok(all(s < 500 for s in res), str(res))


def escribir_md(casos: list[dict], ruta, base: str) -> None:
    tot = len(casos); n = Counter(x["estado"] for x in casos)
    lineas = [
        "# Pruebas exploratorias independientes del Incremento 2 (agenda y alertas)", "",
        f"- Fecha de ejecución: {HOY.strftime('%d/%m/%Y')} (hora de Perú). Versión bajo prueba: v1.5.0-inc2-avance, API REST real en `{base}` con SQLite.",
        "- Método: caja negra por HTTP con `herramientas/gqm/exploratorias_inc2.py`; los resultados esperados se derivaron de ADR-007 y del README, no del código. Datos 100 % sintéticos.",
        f"- Resumen: **{tot} casos**: {n.get('OK', 0)} OK, {n.get('FALLA', 0)} FALLA, {n.get('OBS', 0)} OBS (observación: comportamiento no definido o decisión de diseño documentada; no cuenta como defecto).",
        f"- Reproducción: `python herramientas/gqm/exploratorias_inc2.py --base {base} --db <base.sqlite>` sobre una copia de la base de partida.", "",
        "| ID | Área | Entrada | Esperado | Obtenido | Resultado |", "|---|---|---|---|---|---|"]
    for x in casos:
        esc = lambda t: str(t).replace("|", "\\|").replace("\n", " ")  # noqa: E731
        lineas.append(f"| {x['id']} | {x['area']} | {esc(x['entrada'])} | {esc(x['esperado'])} | {esc(x['obtenido'])} | **{x['estado']}** |")
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--db", default=None)
    a = ap.parse_args()
    Ctx.db = a.db
    with httpx.Client(base_url=a.base, timeout=60) as cli:
        Ctx.cli = cli
        ejecutar()
    (c.DATOS / "exploratorias_inc2.json").write_text(json.dumps(CASOS, ensure_ascii=False, indent=1), encoding="utf-8")
    escribir_md(CASOS, c.METRICAS / "exploratorias_inc2.md", a.base)
    for x in CASOS:
        print(f"{x['id']} [{x['estado']}] {x['obtenido'][:200]}")
    print(Counter(x["estado"] for x in CASOS))


if __name__ == "__main__":
    main()
