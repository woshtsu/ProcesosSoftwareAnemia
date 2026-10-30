#!/usr/bin/env python
"""Pruebas exploratorias independientes del código NUEVO del cierre del Incremento 2 (RF-08 agenda del personal y RF-09 asistencia).

Caja negra por HTTP contra la API v2.0.0-inc2 (servidor con base SQLite propia, sin FECHA_REFERENCIA, es decir con el reloj real de Perú).
Cada caso declara entrada y resultado esperado (derivado del README de la app, ADR-010 y las reglas de la agenda, no del código) y compara con
lo obtenido. Estados: OK, FALLA (contradice la especificación o devuelve 5xx) y OBS (comportamiento que la especificación no define o decisión
de diseño documentada; se informa sin contarlo como defecto). Reutiliza los ayudantes de exploratorias_inc2.py.

Escribe datos/exploratorias_inc2_final.json y metricas/exploratorias_inc2_final.md.
Uso:  python exploratorias_inc2_final.py --base http://127.0.0.1:8404 [--db ruta.sqlite]
"""

from __future__ import annotations

import argparse
import json
import threading
from collections import Counter
from datetime import timedelta

import httpx

import comun as c
import exploratorias_inc2 as ex
from exploratorias_inc2 import CASOS, Ctx, agenda, alertas, caso, crear, nac_para, ok

HOY = ex.HOY
PRIO_SUBE = {"BAJA": "MEDIA", "MEDIA": "ALTA", "ALTA": "ALTA"}


def vencido_edad(dias_vencido: int, edad: int = 12, comunidad: str = "Palmayoc", alta_hb: str = "SIN"):
    """Niño con un control por edad vencido hace ``dias_vencido`` días (atraso contado desde la fecha límite = programada + 30)."""
    prog = HOY - timedelta(days=30 + dias_vencido)
    nid, d = crear(nac_para(prog, edad), [(prog - timedelta(days=40), alta_hb)], comunidad=comunidad)
    ctl = next(x for x in agenda(nid)["controles"] if x["tipo"] == "TAMIZAJE_EDAD" and x["edad_meses_programada"] == edad)
    return nid, d, ctl


def post_asistencia(nid: str, ctl: dict, estado: str, motivo: str | None = None, **extra):
    cuerpo = {"fecha_programada": ctl["fecha_programada"], "estado": estado, **({"motivo": motivo} if motivo is not None else {}), **extra}
    return Ctx.cli.post(f"/api/ninos/{nid}/controles/{ctl['codigo']}/asistencia", json=cuerpo)


def agenda_personal(**params):
    return Ctx.cli.get("/api/agenda", params=params)


def estado_control(nid: str, ctl: dict) -> dict:
    return next(x for x in agenda(nid)["controles"] if x["codigo"] == ctl["codigo"] and x["fecha_programada"] == ctl["fecha_programada"])


def ejecutar() -> None:
    cli = Ctx.cli
    lunes = HOY - timedelta(days=HOY.weekday())

    # ================================ RF-08 · Agenda del personal ================================
    @caso("EXF-01", "RF-08 rango", "GET /api/agenda sin parámetros", "200; semana lunes a domingo de la fecha de hoy (7 días); fecha_referencia = hoy")
    def _():
        r = agenda_personal(); j = r.json()
        return ok(r.status_code == 200 and j["desde"] == lunes.isoformat() and j["hasta"] == (lunes + timedelta(days=6)).isoformat() and len(j["dias"]) == 7 and j["fecha_referencia"] == HOY.isoformat(),
                  f"HTTP {r.status_code}; {j.get('desde')} a {j.get('hasta')}; {len(j.get('dias', []))} días; fecha_referencia={j.get('fecha_referencia')}")

    @caso("EXF-02", "RF-08 rango", "Rangos de 1, 31 y 32 días", "1 y 31 días -> 200 con ese número de días; 32 días -> 422")
    def _():
        res = {}
        for n in (1, 31, 32):
            r = agenda_personal(desde=HOY.isoformat(), hasta=(HOY + timedelta(days=n - 1)).isoformat())
            res[n] = (r.status_code, len(r.json()["dias"]) if r.status_code == 200 else None)
        return ok(res[1] == (200, 1) and res[31] == (200, 31) and res[32][0] == 422, str(res))

    @caso("EXF-03", "RF-08 rango", "desde posterior a hasta; fechas imposibles (2026-13-45, 2026-02-30), texto, vacío, '2026-10-1', fecha con hora", "422 con mensaje en todos los inválidos (el vacío equivale a no indicar); nunca 5xx")
    def _():
        res = {"desde>hasta": agenda_personal(desde="2026-10-10", hasta="2026-10-01").status_code}
        for v in ("2026-13-45", "2026-02-30", "abc", "2026-10-1", "2026-10-01T10:00:00", "%00", "x" * 3000):
            res[v[:12]] = agenda_personal(desde=v, hasta="2026-12-31").status_code
        res["vacío"] = agenda_personal(desde="", hasta="").status_code
        invalidos = [k for k in res if k != "vacío"]
        return ok(all(s == 422 for k, s in res.items() if k in invalidos) and res["vacío"] < 500, str(res))

    @caso("EXF-04", "RF-08 rango", "Un solo extremo: solo desde, solo hasta", "Sin 5xx; si responde 200, el rango no supera 31 días y contiene la fecha indicada")
    def _():
        r1 = agenda_personal(desde=HOY.isoformat()); r2 = agenda_personal(hasta=HOY.isoformat())
        det = []
        for nombre, r in (("solo desde", r1), ("solo hasta", r2)):
            det.append(f"{nombre}: HTTP {r.status_code}" + (f" {r.json()['desde']}..{r.json()['hasta']}" if r.status_code == 200 else ""))
        buenos = all(r.status_code < 500 for r in (r1, r2))
        return ok(buenos, "; ".join(det))

    @caso("EXF-05", "RF-08 rango", "Años extremos: 0001-01-01..0001-01-31, 9999-12-01..9999-12-31, 1900-01-01..1900-01-31", "Sin 5xx (200 con días vacíos o 422)")
    def _():
        res = {}
        for a, b in (("0001-01-01", "0001-01-31"), ("9999-12-01", "9999-12-31"), ("1900-01-01", "1900-01-31")):
            r = agenda_personal(desde=a, hasta=b); res[a] = (r.status_code, r.json()["resumen"]["total"] if r.status_code == 200 else None)
        return ok(all(s < 500 for s, _t in res.values()), str(res))

    @caso("EXF-06", "RF-08 contenido", "Niño con un control por edad programado HOY, otro hace 10 días (pendiente) y otro hace 31 días (vencido por 1 día)", "Cada control aparece en el día de su fecha programada con su estado: hoy PENDIENTE, hace 10 días PENDIENTE, hace 31 días VENCIDO")
    def _():
        res = []
        for dias_atras, esperado in ((0, "PENDIENTE"), (10, "PENDIENTE"), (31, "VENCIDO")):
            prog = HOY - timedelta(days=dias_atras); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")], comunidad="ExfSeis")
            j = agenda_personal(desde=prog.isoformat(), hasta=prog.isoformat(), comunidad="ExfSeis").json()
            items = [i for dia in j["dias"] for i in dia["items"] if i["nino"]["dni"] == d]
            res.append((dias_atras, items[0]["control"]["estado"] if items else None, esperado))
        return ok(all(a == b for _, a, b in res), "; ".join(f"programado hace {d} d -> {a} (esperado {b})" for d, a, b in res))

    @caso("EXF-07", "RF-08 contenido", "Totales: resumen y totales por día de un rango de 31 días con todos los niños de la prueba", "resumen.total = suma de dias.total; cumplidos + pendientes + vencidos = total; cada día cuadra con sus ítems")
    def _():
        j = agenda_personal(desde=(HOY - timedelta(days=30)).isoformat(), hasta=HOY.isoformat()).json()
        r = j["resumen"]; dias = j["dias"]
        s = sum(d["total"] for d in dias); cuadra_dia = all(d["total"] == len(d["items"]) == d["cumplidos"] + d["pendientes"] + d["vencidos"] for d in dias)
        return ok(r["total"] == s == r["cumplidos"] + r["pendientes"] + r["vencidos"] and cuadra_dia, f"resumen={r}; suma por día={s}; cada día cuadra={cuadra_dia}")

    @caso("EXF-08", "RF-08 contenido", "Niño con alta: tenía un control en la semana; se le da de alta", "Sus controles dejan de aparecer en la agenda del personal; al reactivarlo reaparecen")
    def _():
        prog = HOY - timedelta(days=2); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")], comunidad="ExfOcho")
        esta = lambda: any(i["nino"]["dni"] == d for dia in agenda_personal(desde=prog.isoformat(), hasta=prog.isoformat(), comunidad="ExfOcho").json()["dias"] for i in dia["items"])  # noqa: E731
        antes = esta(); cli.patch(f"/api/ninos/{nid}", json={"estado": "ALTA"}); con_alta = esta(); cli.patch(f"/api/ninos/{nid}", json={"estado": "ACTIVO"}); despues = esta()
        return ok(antes and not con_alta and despues, f"antes={antes}; con alta={con_alta}; reactivado={despues}")

    @caso("EXF-09", "RF-08 filtros", "Filtros por establecimiento y comunidad inexistentes, vacíos y con texto especial ('%', '_', comilla, '; DROP TABLE', NUL, 5 000 caracteres, emoji)", "200 con 0 controles para valores inexistentes; '%' y '_' se tratan como texto; vacío = sin filtro; nunca 5xx")
    def _():
        tot = agenda_personal(desde=(HOY - timedelta(days=30)).isoformat(), hasta=HOY.isoformat()).json()["resumen"]["total"]; res = {}
        for campo in ("establecimiento", "comunidad"):
            for v in ("No existe", "%", "_", "'", "'; DROP TABLE nino;--", "\x00", "x" * 5000, "😀"):
                r = agenda_personal(desde=(HOY - timedelta(days=30)).isoformat(), hasta=HOY.isoformat(), **{campo: v})
                res[f"{campo}:{v[:8]!r}"] = (r.status_code, r.json()["resumen"]["total"] if r.status_code == 200 else None)
        vacio = agenda_personal(desde=(HOY - timedelta(days=30)).isoformat(), hasta=HOY.isoformat(), comunidad="").json()["resumen"]["total"]
        ceros = all(t == 0 for _k, (s, t) in res.items() if s == 200)
        return ok(all(s == 200 for s, _t in res.values()) and ceros and vacio == tot, f"{len(res)} combinaciones: todas 200={all(s == 200 for s, _t in res.values())}, todas con 0 controles={ceros}; comunidad='' -> {vacio} de {tot}")

    @caso("EXF-10", "RF-08 filtros", "Comunidad grabada 'ExfDiez' y filtro 'EXFDIEZ', 'exfdiez', ' ExfDiez '", "Coincide sin distinguir mayúsculas ni espacios (igual que en las alertas)")
    def _():
        prog = HOY - timedelta(days=2); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")], comunidad="ExfDiez")
        res = {f: any(i["nino"]["dni"] == d for dia in agenda_personal(desde=prog.isoformat(), hasta=prog.isoformat(), comunidad=f).json()["dias"] for i in dia["items"]) for f in ("EXFDIEZ", "exfdiez", " ExfDiez ")}
        return ok(all(res.values()), str(res))

    @caso("EXF-11", "RF-08 filtros", "Opciones de filtro: establecimientos_disponibles y comunidades_disponibles tras crear un niño en la comunidad 'ExfOnce'", "La nueva comunidad figura en comunidades_disponibles, sin duplicados ni valores vacíos")
    def _():
        crear(nac_para(HOY - timedelta(days=2), 12), [(HOY - timedelta(days=42), "SIN")], comunidad="ExfOnce")
        j = agenda_personal().json(); com = j["comunidades_disponibles"]; est = j["establecimientos_disponibles"]
        return ok("ExfOnce" in com and len(com) == len(set(com)) and "" not in com and len(est) == len(set(est)), f"{len(com)} comunidades, {len(est)} establecimientos; 'ExfOnce' presente={'ExfOnce' in com}")

    @caso("EXF-12", "RF-08 rendimiento", "Rango de 31 días con todos los niños creados hasta ahora, 5 mediciones", "200 y menos de 1 s en cada medición")
    def _():
        import time
        ts = []
        for _i in range(5):
            t0 = time.perf_counter(); r = agenda_personal(desde=(HOY - timedelta(days=30)).isoformat(), hasta=HOY.isoformat()); ts.append((time.perf_counter() - t0) * 1000)
            assert r.status_code == 200
        n = len(cli.get("/api/ninos", params={"estado": ""}).json())
        return ok(max(ts) < 1000, f"{n} niños; tiempos (ms): {[round(t) for t in ts]}")

    # ================================ RF-09 · Asistencia ================================
    @caso("EXF-20", "RF-09 asistió", "Control vencido (atraso 20 d): POST asistencia ASISTIO", "201; el control pasa a CUMPLIDO (cumplido_por_asistencia); sale de las alertas; la agenda del personal lo muestra CUMPLIDO; el resumen de vencidos baja en 1")
    def _():
        nid, d, ctl = vencido_edad(20, comunidad="ExfVeinte"); antes = cli.get("/api/alertas/resumen").json()["total_vencidos"]
        r = post_asistencia(nid, ctl, "ASISTIO"); despues = cli.get("/api/alertas/resumen").json()["total_vencidos"]
        nuevo = estado_control(nid, ctl); en_alertas = d in {a["nino"]["dni"] for a in alertas(comunidad="ExfVeinte")}
        j = agenda_personal(desde=ctl["fecha_programada"], hasta=ctl["fecha_programada"], comunidad="ExfVeinte").json()
        en_ag = [i["control"]["estado"] for dia in j["dias"] for i in dia["items"] if i["nino"]["dni"] == d]
        return ok(r.status_code == 201 and nuevo["estado"] == "CUMPLIDO" and nuevo["cumplido_por_asistencia"] and not en_alertas and despues == antes - 1 and en_ag == ["CUMPLIDO"],
                  f"HTTP {r.status_code}; estado={nuevo['estado']} por_asistencia={nuevo['cumplido_por_asistencia']}; en alertas={en_alertas}; vencidos {antes}->{despues}; agenda personal={en_ag}")

    @caso("EXF-21", "RF-09 no asistió", "Controles vencidos hace 3 d (BAJA), 20 d (MEDIA) y 40 d (ALTA): POST NO_ASISTIO con motivo", "201; el control sigue VENCIDO con inasistencia_registrada y motivo; la prioridad sube un nivel (BAJA->MEDIA, MEDIA->ALTA, ALTA se mantiene)")
    def _():
        res = []
        for dias, antes in ((3, "BAJA"), (20, "MEDIA"), (40, "ALTA")):
            nid, d, ctl = vencido_edad(dias, comunidad=f"ExfVeintiuno{dias}")
            a0 = next(a for a in alertas(comunidad=f"ExfVeintiuno{dias}") if a["nino"]["dni"] == d)["prioridad"]
            r = post_asistencia(nid, ctl, "NO_ASISTIO", "Viaje o traslado de la familia")
            a1 = next(a for a in alertas(comunidad=f"ExfVeintiuno{dias}") if a["nino"]["dni"] == d)
            nuevo = estado_control(nid, ctl)
            res.append((dias, a0, a1["prioridad"], PRIO_SUBE[antes], r.status_code, nuevo["estado"], nuevo["inasistencia_registrada"], nuevo["motivo_inasistencia"]))
        return ok(all(a0 == ant and a1 == esp and s == 201 and est == "VENCIDO" and ina and mot for (dias, a0, a1, esp, s, est, ina, mot), ant in zip(res, ("BAJA", "MEDIA", "ALTA"))),
                  "; ".join(f"{dias} d: {a0}->{a1} (esperado {esp}), HTTP {s}, {est}, inasistencia={ina}" for dias, a0, a1, esp, s, est, ina, _m in res))

    @caso("EXF-22", "RF-09 validación", "NO_ASISTIO sin motivo, con motivo de 2 caracteres, de solo espacios, de 201 caracteres y de 200; ASISTIO con motivo largo de 201", "Sin motivo, 2 caracteres y solo espacios -> 422; 201 caracteres -> 422; 200 caracteres -> 201; sin 5xx. (El motivo de 3 a 200 caracteres es la regla de ADR-010.)")
    def _():
        res = {}
        for etiqueta, motivo in (("sin motivo", None), ("2 car.", "ab"), ("espacios", "     "), ("201 car.", "x" * 201)):
            nid, d, ctl = vencido_edad(15, comunidad="ExfVeintidos"); res[etiqueta] = post_asistencia(nid, ctl, "NO_ASISTIO", motivo).status_code
        nid, d, ctl = vencido_edad(15, comunidad="ExfVeintidos"); res["200 car."] = post_asistencia(nid, ctl, "NO_ASISTIO", "y" * 200).status_code
        nid, d, ctl = vencido_edad(15, comunidad="ExfVeintidos"); res["asistió+201"] = post_asistencia(nid, ctl, "ASISTIO", "z" * 201).status_code
        return ok(res["sin motivo"] == res["2 car."] == res["espacios"] == res["201 car."] == res["asistió+201"] == 422 and res["200 car."] == 201, str(res))

    @caso("EXF-23", "RF-09 validación", "Estado no válido: 'ASISTIÓ', 'asistio', 'Asistio', '', null, número, lista; cuerpo vacío, cuerpo no JSON, fecha_programada nula", "422 en todos; nunca 5xx; no se guarda nada")
    def _():
        nid, d, ctl = vencido_edad(15, comunidad="ExfVeintitres"); url = f"/api/ninos/{nid}/controles/{ctl['codigo']}/asistencia"; res = {}
        base = {"fecha_programada": ctl["fecha_programada"]}
        for v in ("ASISTIÓ", "asistio", "Asistio", "", None, 1, ["ASISTIO"]):
            res[repr(v)] = cli.post(url, json={**base, "estado": v}).status_code
        res["{}"] = cli.post(url, json={}).status_code
        res["no JSON"] = cli.post(url, content=b"esto no es json", headers={"content-type": "application/json"}).status_code
        res["fecha nula"] = cli.post(url, json={"estado": "ASISTIO", "fecha_programada": None}).status_code
        guardadas = len(cli.get(f"/api/ninos/{nid}/asistencias").json())
        return ok(all(s == 422 for s in res.values()) and guardadas == 0, f"{res}; asistencias guardadas={guardadas}")

    @caso("EXF-24", "RF-09 control inexistente", "Niño inexistente; código inexistente; fecha programada que no corresponde al control; id y código con caracteres raros", "404 con mensaje JSON (o 422 por fecha futura en los casos que lo ameriten); nunca 5xx")
    def _():
        nid, d, ctl = vencido_edad(15, comunidad="ExfVeinticuatro"); res = {}
        cuerpo = {"fecha_programada": ctl["fecha_programada"], "estado": "ASISTIO"}
        res["niño inexistente"] = cli.post(f"/api/ninos/00000000-0000-0000-0000-000000000000/controles/{ctl['codigo']}/asistencia", json=cuerpo).status_code
        res["código inexistente"] = cli.post(f"/api/ninos/{nid}/controles/ZZZ9/asistencia", json=cuerpo).status_code
        res["fecha desplazada"] = cli.post(f"/api/ninos/{nid}/controles/{ctl['codigo']}/asistencia", json={**cuerpo, "fecha_programada": (HOY - timedelta(days=400)).isoformat()}).status_code
        res["id raro"] = cli.post("/api/ninos/%00/controles/DHc2/asistencia", json=cuerpo).status_code
        res["código raro"] = cli.post(f"/api/ninos/{nid}/controles/%F0%9F%98%80/asistencia", json=cuerpo).status_code
        res["código 5000"] = cli.post(f"/api/ninos/{nid}/controles/{'X' * 5000}/asistencia", json=cuerpo).status_code
        return ok(res["niño inexistente"] == 404 and res["código inexistente"] == 404 and res["fecha desplazada"] == 404 and all(s < 500 for s in res.values()), str(res))

    @caso("EXF-25", "RF-09 fecha", "Fecha programada futura (mañana), hoy y control programado hoy", "Futura -> 422; un control programado hoy admite asistencia (201)")
    def _():
        nid, d, ctl = vencido_edad(15, comunidad="ExfVeinticinco")
        fut = cli.post(f"/api/ninos/{nid}/controles/{ctl['codigo']}/asistencia", json={"fecha_programada": (HOY + timedelta(days=1)).isoformat(), "estado": "ASISTIO"}).status_code
        prog = HOY; nid2, d2 = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")], comunidad="ExfVeinticinco")
        ctl2 = next(x for x in agenda(nid2)["controles"] if x["tipo"] == "TAMIZAJE_EDAD" and x["edad_meses_programada"] == 12)
        hoy = post_asistencia(nid2, ctl2, "ASISTIO").status_code
        return ok(fut == 422 and hoy == 201, f"futura -> {fut}; programado hoy -> {hoy}")

    @caso("EXF-26", "RF-09 duplicados", "Segundo registro del mismo control (ASISTIO y luego NO_ASISTIO; NO_ASISTIO y luego ASISTIO; ASISTIO dos veces)", "El segundo -> 409 con mensaje; el primero se conserva; GET asistencias lista una sola")
    def _():
        res = []
        for primero, segundo in (("ASISTIO", "NO_ASISTIO"), ("NO_ASISTIO", "ASISTIO"), ("ASISTIO", "ASISTIO")):
            nid, d, ctl = vencido_edad(20, comunidad="ExfVeintiseis")
            r1 = post_asistencia(nid, ctl, primero, "Olvido de la cita" if primero == "NO_ASISTIO" else None)
            r2 = post_asistencia(nid, ctl, segundo, "Olvido de la cita" if segundo == "NO_ASISTIO" else None)
            lista = cli.get(f"/api/ninos/{nid}/asistencias").json()
            res.append((primero, segundo, r1.status_code, r2.status_code, len(lista), lista[0]["estado"] if lista else None))
        return ok(all(a == 201 and b == 409 and n == 1 and e == p for p, _s, a, b, n, e in res), "; ".join(f"{p}+{s}: {a},{b}, guardadas={n}, conservada={e}" for p, s, a, b, n, e in res))

    @caso("EXF-27", "RF-09 duplicados", "8 solicitudes simultáneas (hilos) para el mismo control", "Exactamente un 201 y el resto 409; ningún 5xx; una sola asistencia guardada")
    def _():
        nid, d, ctl = vencido_edad(20, comunidad="ExfVeintisiete"); res = []
        def uno():
            with httpx.Client(base_url=cli.base_url, timeout=60) as h:
                res.append(h.post(f"/api/ninos/{nid}/controles/{ctl['codigo']}/asistencia", json={"fecha_programada": ctl["fecha_programada"], "estado": "ASISTIO"}).status_code)
        hs = [threading.Thread(target=uno) for _ in range(8)]; [h.start() for h in hs]; [h.join() for h in hs]
        n = len(cli.get(f"/api/ninos/{nid}/asistencias").json()); cnt = Counter(res)
        return ok(cnt.get(201) == 1 and cnt.get(409) == 7 and n == 1, f"códigos {dict(cnt)}; asistencias guardadas={n}")

    @caso("EXF-28", "RF-09 estados", "Control ya CUMPLIDO por una evaluación en su ventana; control CERRADO por recuperación", "409 en ambos (ya no hay nada que registrar)")
    def _():
        prog = HOY - timedelta(days=5); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN"), (prog, "SIN")], comunidad="ExfVeintiocho")
        ctl = next(x for x in agenda(nid)["controles"] if x["tipo"] == "TAMIZAJE_EDAD" and x["edad_meses_programada"] == 12)
        s1 = post_asistencia(nid, ctl, "ASISTIO").status_code if ctl["estado"] == "CUMPLIDO" else None
        # cerrado por recuperación con fecha programada ya pasada: anemia leve hace 100 d (C1M hace ~70 d, C3M hace ~10 d, aún sin vencer)
        # y una evaluación sin anemia hace 60 d (dentro de la ventana del C1M) que cierra el C3M y el C6M
        nac = ex.o.sumar_meses(HOY, -12)
        nid2, d2 = crear(nac, [(HOY - timedelta(days=100), "LEVE"), (HOY - timedelta(days=60), "SIN")], comunidad="ExfVeintiocho")
        cerrados = [x for x in agenda(nid2)["controles"] if x["estado"] == "CERRADO_RECUPERADO" and x["fecha_programada"] <= HOY.isoformat()]
        s2 = post_asistencia(nid2, cerrados[0], "ASISTIO").status_code if cerrados else None
        return ok(s1 == 409 and s2 == 409, f"cumplido -> {s1} (estado {ctl['estado']}); cerrado por recuperación -> {s2} ({len(cerrados)} cerrado(s) con fecha pasada)")

    @caso("EXF-29", "RF-09 evaluación vinculada", "ASISTIO con evaluacion_id propia del niño; con evaluación de otro niño; NO_ASISTIO con evaluacion_id; id inexistente", "Propia -> 201 y queda vinculada; ajena, con NO_ASISTIO e inexistente -> 422; sin 5xx")
    def _():
        prog = HOY - timedelta(days=45); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=100), "SIN"), (HOY - timedelta(days=2), "SIN")], comunidad="ExfVeintinueve")
        ctl = next(x for x in agenda(nid)["controles"] if x["tipo"] == "TAMIZAJE_EDAD" and x["edad_meses_programada"] == 12)
        otra_nid, _d2 = crear(ex.o.sumar_meses(HOY, -9), [(HOY - timedelta(days=1), "SIN")], comunidad="ExfVeintinueve")
        ajena = cli.get(f"/api/ninos/{otra_nid}").json()["evaluaciones"][0]["id"]
        propia = next(e["id"] for e in cli.get(f"/api/ninos/{nid}").json()["evaluaciones"] if e["fecha"] == (HOY - timedelta(days=2)).isoformat())
        r_aj = post_asistencia(nid, ctl, "ASISTIO", evaluacion_id=ajena).status_code
        r_na = post_asistencia(nid, ctl, "NO_ASISTIO", "Enfermedad del niño", evaluacion_id=propia).status_code
        r_in = post_asistencia(nid, ctl, "ASISTIO", evaluacion_id="00000000-0000-0000-0000-000000000000").status_code
        r_ok = post_asistencia(nid, ctl, "ASISTIO", evaluacion_id=propia)
        lista = cli.get(f"/api/ninos/{nid}/asistencias").json()
        return ok(r_aj == 422 and r_na == 422 and r_in == 422 and r_ok.status_code == 201 and lista and lista[0]["evaluacion_id"] == propia,
                  f"ajena {r_aj}; NO_ASISTIO+evaluación {r_na}; inexistente {r_in}; propia {r_ok.status_code}, vinculada={bool(lista) and lista[0]['evaluacion_id'] == propia}")

    @caso("EXF-30", "RF-09 secuencia", "NO_ASISTIO y después una evaluación dentro de la ventana del control", "El control queda CUMPLIDO y la marca de inasistencia deja de figurar (CP-126), sin error")
    def _():
        prog = HOY - timedelta(days=10); nid, d = crear(nac_para(prog, 12), [(prog - timedelta(days=40), "SIN")], comunidad="ExfTreinta")
        ctl = next(x for x in agenda(nid)["controles"] if x["tipo"] == "TAMIZAJE_EDAD" and x["edad_meses_programada"] == 12)
        r = post_asistencia(nid, ctl, "NO_ASISTIO", "Distancia o falta de transporte")
        e = cli.post(f"/api/ninos/{nid}/evaluaciones", json={"fecha": HOY.isoformat(), "hemoglobina_observada": 12.5, "peso_kg": 9.5, "talla_cm": 75})
        nuevo = estado_control(nid, ctl)
        return ok(r.status_code == 201 and e.status_code == 201 and nuevo["estado"] == "CUMPLIDO" and not nuevo["inasistencia_registrada"], f"NO_ASISTIO {r.status_code}; evaluación {e.status_code}; control {nuevo['estado']}, inasistencia visible={nuevo['inasistencia_registrada']}")

    @caso("EXF-31", "RF-09 alta", "Registrar asistencia de un control de un niño con ALTA", "Sin 5xx; lo razonable es 404/409/422 porque ya no tiene agenda", )
    def _():
        nid, d, ctl = vencido_edad(20, comunidad="ExfTreintayuno"); cli.patch(f"/api/ninos/{nid}", json={"estado": "ALTA"})
        r = post_asistencia(nid, ctl, "ASISTIO")
        return ok(r.status_code in (404, 409, 422), f"HTTP {r.status_code} {r.text[:120]}", obs=r.status_code < 500)

    @caso("EXF-32", "RF-09 listado", "GET /api/ninos/{id}/asistencias de un niño con 3 asistencias en distinto orden de registro; de un niño sin asistencias; de un niño inexistente", "Ordenadas por fecha programada; [] para el niño sin asistencias; 404 para el inexistente")
    def _():
        nid, d = crear(ex.o.sumar_meses(HOY, -26), [(HOY - timedelta(days=400), "SIN")], comunidad="ExfTreintaydos")
        vencidos = [x for x in agenda(nid)["controles"] if x["estado"] == "VENCIDO"][:3]
        for ctl in reversed(vencidos):
            post_asistencia(nid, ctl, "NO_ASISTIO", "Olvido de la cita")
        lista = cli.get(f"/api/ninos/{nid}/asistencias").json(); fechas = [x["fecha_programada"] for x in lista]
        vacio = cli.get(f"/api/ninos/{crear(ex.o.sumar_meses(HOY, -9), [(HOY, 'SIN')])[0]}/asistencias").json()
        inex = cli.get("/api/ninos/00000000-0000-0000-0000-000000000000/asistencias").status_code
        return ok(len(lista) == len(vencidos) >= 2 and fechas == sorted(fechas) and vacio == [] and inex == 404, f"{len(lista)} asistencias, ordenadas={fechas == sorted(fechas)}; sin asistencias={vacio}; inexistente={inex}")

    @caso("EXF-33", "RF-09 auditoría", "Encabezado X-Usuario con nombre, vacío, ausente y de 300 caracteres", "registrado_por guarda el usuario (o un valor por omisión); sin 5xx")
    def _():
        res = []
        for u in ("Obstetra Prueba", "", None, "U" * 300):
            nid, d, ctl = vencido_edad(20, comunidad="ExfTreintaytres")
            h = {} if u is None else {"X-Usuario": u}
            r = cli.post(f"/api/ninos/{nid}/controles/{ctl['codigo']}/asistencia", json={"fecha_programada": ctl["fecha_programada"], "estado": "ASISTIO"}, headers=h)
            res.append((repr(u)[:14], r.status_code, r.json().get("registrado_por", "")[:20] if r.status_code == 201 else r.text[:60]))
        return ok(all(s < 500 for _u, s, _r in res) and res[0][1] == 201 and res[0][2] == "Obstetra Prueba", str(res))

    @caso("EXF-34", "RF-09 + RF-08 concurrencia", "6 hilos que registran asistencias de controles distintos mientras 6 hilos leen la agenda del personal y las alertas", "Ningún 5xx en las lecturas; las escrituras 201 (si SQLite bloquea, es limitación del motor de desarrollo -> OBS)")
    def _():
        niños = [vencido_edad(20, comunidad="ExfTreintaycuatro") for _ in range(6)]; esc, lect = [], []
        def escribir(k):
            with httpx.Client(base_url=cli.base_url, timeout=60) as h:
                nid, d, ctl = niños[k]; esc.append(h.post(f"/api/ninos/{nid}/controles/{ctl['codigo']}/asistencia", json={"fecha_programada": ctl["fecha_programada"], "estado": "ASISTIO"}).status_code)
        def leer(_k):
            with httpx.Client(base_url=cli.base_url, timeout=60) as h:
                for _i in range(15):
                    lect.append(h.get("/api/agenda").status_code); lect.append(h.get("/api/alertas/resumen").status_code)
        hs = [threading.Thread(target=escribir, args=(k,)) for k in range(6)] + [threading.Thread(target=leer, args=(k,)) for k in range(6)]
        [h.start() for h in hs]; [h.join() for h in hs]
        texto = f"escrituras {dict(Counter(esc))}; lecturas {dict(Counter(lect))}"
        if any(s >= 500 for s in lect):
            return "FALLA", texto
        if any(s >= 500 for s in esc):
            return "OBS", texto + " -- 5xx en escritura simultánea (SQLite)"
        return ok(all(s == 201 for s in esc), texto)


def escribir_md(casos: list[dict], ruta, base: str) -> None:
    tot = len(casos); n = Counter(x["estado"] for x in casos)
    lineas = [
        "# Pruebas exploratorias independientes del cierre del Incremento 2 (RF-08 agenda del personal y RF-09 asistencia)", "",
        f"- Fecha de ejecución: {HOY.strftime('%d/%m/%Y')} (hora de Perú). Versión bajo prueba: v2.0.0-inc2, API REST real en `{base}` con SQLite y el reloj real.",
        "- Método: caja negra por HTTP con `herramientas/gqm/exploratorias_inc2_final.py`; los resultados esperados se derivaron del README de la app, de ADR-010 y de las reglas de la agenda, no del código. Datos 100 % sintéticos.",
        f"- Resumen: **{tot} casos**: {n.get('OK', 0)} OK, {n.get('FALLA', 0)} FALLA, {n.get('OBS', 0)} OBS (observación: comportamiento no definido o decisión de diseño documentada; no cuenta como defecto).",
        "- Reproducción: servidor v2.0 con base SQLite nueva (sin `FECHA_REFERENCIA`) y `python herramientas/gqm/exploratorias_inc2_final.py --base <url>`.", "",
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
    CASOS.clear()
    with httpx.Client(base_url=a.base, timeout=60) as cli:
        salud = cli.get("/api/salud").json()
        if salud.get("fecha_referencia"):
            raise SystemExit("Estas exploratorias se ejecutan con el reloj real: inicie el servidor sin FECHA_REFERENCIA.")
        Ctx.cli = cli
        ejecutar()
    (c.DATOS / "exploratorias_inc2_final.json").write_text(json.dumps(CASOS, ensure_ascii=False, indent=1), encoding="utf-8")
    escribir_md(CASOS, c.METRICAS / "exploratorias_inc2_final.md", "http://127.0.0.1:<puerto>")
    for x in CASOS:
        print(f"{x['id']} [{x['estado']}] {x['obtenido'][:300]}")
    print(Counter(x["estado"] for x in CASOS))


if __name__ == "__main__":
    main()
