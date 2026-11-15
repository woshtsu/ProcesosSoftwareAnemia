#!/usr/bin/env python
"""Oráculo independiente de controles vencidos (GQM M3.2 / V3).

Implementación PROPIA y autónoma de la regla documentada de la agenda (README y ADR-007 de v1.5, esquema AGENDA-V1).
NO importa nada de la aplicación: solo biblioteca estándar. Se escribió a partir del texto de la regla:

  * Controles por edad (tamizaje): 6, 9, 12, 15, 18, 21, 24, 30, 36, 39, 48 y 51 meses de edad.
    Fecha programada = nacimiento + N meses calendario (si el día no existe, último día del mes).
  * Controles de tratamiento: tras una evaluación con anemia (LEVE, MODERADA o SEVERA) se programan C1M, C3M y C6M a
    +1, +3 y +6 meses de esa evaluación. Un episodio empieza con la primera evaluación con anemia; las posteriores con
    anemia dentro del episodio no reinician el calendario. Se abre un episodio nuevo con una anemia posterior a una
    evaluación SIN_ANEMIA o posterior al fin de la ventana del C6M.
  * Ventana de cumplimiento: de programada - 15 días a programada + 30 días (ambos extremos incluidos).
  * La agenda empieza cuando el niño entra al sistema: solo se programan controles por edad con fecha programada
    >= fecha de la primera evaluación - 15 días.
  * Población: solo niños ACTIVO y solo controles con el niño de menos de 60 meses en la fecha programada.
  * Cada evaluación cumple como máximo un control y cada control usa una sola evaluación; se asignan primero los pares
    más cercanos (empate: control más antiguo; a igual fecha, el de tratamiento).
  * VENCIDO = no cumplido y hoy > programada + 30 días. Si una evaluación posterior al diagnóstico es SIN_ANEMIA, los
    controles de tratamiento de ese episodio que aún no habían vencido en la fecha de esa evaluación y no se cumplieron
    pasan a CERRADO_RECUPERADO (no cuentan como vencidos); los ya vencidos antes de la recuperación siguen vencidos.

La clasificación de anemia de cada evaluación se calcula aquí mismo con la guía OMS 2024 citada en la documentación de
reglas clínicas (ADR-004): ajuste por altitud = (0,0056384*alt + 0,0000003*alt^2)/10 g/dL redondeado a 1 decimal;
Hb ajustada = Hb observada - ajuste (1 decimal); puntos de corte 6-23 meses: <10,5 anemia, >=9,5 leve, >=7,0 moderada,
<7,0 severa; 24-59 meses: <11,0 anemia, >=10,0 leve, >=7,0 moderada, <7,0 severa; menores de 6 meses: no aplica.

Uso como biblioteca:  from oraculo_agenda import controles_vencidos
Uso como CLI:         python oraculo_agenda.py dataset.json [--hoy AAAA-MM-DD] [--salida etiquetas.json]
"""

from __future__ import annotations

import argparse
import calendar
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

EDADES_TAMIZAJE = (6, 9, 12, 15, 18, 21, 24, 30, 36, 39, 48, 51)
TRATAMIENTO = ((1, "C1M"), (3, "C3M"), (6, "C6M"))
VENTANA_ANTES, VENTANA_DESPUES = 15, 30
EDAD_MAX = 60


def hoy_peru() -> date:
    return datetime.now(timezone(timedelta(hours=-5))).date()


def sumar_meses(d: date, n: int) -> date:
    m = d.month - 1 + n
    anio, mes = d.year + m // 12, m % 12 + 1
    return date(anio, mes, min(d.day, calendar.monthrange(anio, mes)[1]))


def edad_meses(nac: date, ref: date) -> int:
    m = (ref.year - nac.year) * 12 + ref.month - nac.month
    return m - 1 if ref.day < nac.day else m


def ajuste_altitud(alt: float) -> float:
    if alt <= 0:
        return 0.0
    return round((0.0056384 * alt + 0.0000003 * alt**2) / 10, 1)


def clasificar(edad: int, hb_obs: float, alt: float) -> str:
    hb = round(hb_obs - ajuste_altitud(alt), 1)
    if edad < 6 or edad > 59:
        return "NO_APLICA"
    anemia, leve = (10.5, 9.5) if edad <= 23 else (11.0, 10.0)
    if hb >= anemia:
        return "SIN_ANEMIA"
    if hb >= leve:
        return "LEVE"
    if hb >= 7.0:
        return "MODERADA"
    return "SEVERA"


def _controles(nino: dict, evals: list[dict]) -> list[dict]:
    nac = nino["nacimiento"]
    primera = evals[0]["fecha"]
    controles = []
    for n in EDADES_TAMIZAJE:
        prog = sumar_meses(nac, n)
        if prog >= primera - timedelta(days=15) and edad_meses(nac, prog) < EDAD_MAX:
            controles.append({"tipo": "TAMIZAJE_EDAD", "codigo": f"EDAD{n}", "prog": prog, "episodio": None})
    # episodios de anemia
    episodios: list[dict] = []
    actual = None
    for ev in evals:
        if ev["clasif"] in ("LEVE", "MODERADA", "SEVERA"):
            fin_c6m = sumar_meses(actual["inicio"], 6) + timedelta(days=VENTANA_DESPUES) if actual else None
            if actual is None or actual["recuperado"] is not None or ev["fecha"] > fin_c6m:
                actual = {"inicio": ev["fecha"], "recuperado": None}
                episodios.append(actual)
        elif ev["clasif"] == "SIN_ANEMIA" and actual is not None and actual["recuperado"] is None:
            actual["recuperado"] = ev["fecha"]
    for k, ep in enumerate(episodios):
        for meses, cod in TRATAMIENTO:
            prog = sumar_meses(ep["inicio"], meses)
            if edad_meses(nac, prog) < EDAD_MAX:
                controles.append({"tipo": "CONTROL_TRATAMIENTO", "codigo": cod, "prog": prog, "episodio": k})
    return controles, episodios


def controles_vencidos(nino: dict, hoy: date) -> list[dict]:
    """Controles vencidos hoy de un niño. ``nino`` = {nacimiento: date, estado, altitud, evaluaciones: [{fecha, hb_obs}]}."""
    if nino["estado"] != "ACTIVO" or not nino["evaluaciones"]:
        return []
    nac = nino["nacimiento"]
    evals = sorted(
        (
            {"fecha": e["fecha"], "clasif": clasificar(edad_meses(nac, e["fecha"]), e["hb_obs"], nino["altitud"])}
            for e in nino["evaluaciones"]
        ),
        key=lambda e: e["fecha"],
    )
    controles, episodios = _controles(nino, evals)
    # asignación 1:1 de evaluaciones a controles (pares más cercanos primero)
    pares = []
    for i, c in enumerate(controles):
        ini, fin = c["prog"] - timedelta(days=VENTANA_ANTES), c["prog"] + timedelta(days=VENTANA_DESPUES)
        for j, e in enumerate(evals):
            if ini <= e["fecha"] <= fin:
                prioridad_tipo = 0 if c["tipo"] == "CONTROL_TRATAMIENTO" else 1
                pares.append((abs((e["fecha"] - c["prog"]).days), c["prog"], prioridad_tipo, e["fecha"], i, j))
    usados_c, usados_e = set(), set()
    for _, _, _, _, i, j in sorted(pares):
        if i not in usados_c and j not in usados_e:
            usados_c.add(i)
            usados_e.add(j)
    vencidos = []
    for i, c in enumerate(controles):
        if i in usados_c:
            continue
        limite = c["prog"] + timedelta(days=VENTANA_DESPUES)
        if hoy <= limite:
            continue  # pendiente
        if c["tipo"] == "CONTROL_TRATAMIENTO":
            rec = episodios[c["episodio"]]["recuperado"]
            if rec is not None and rec <= limite:
                continue  # CERRADO_RECUPERADO
        vencidos.append(
            {"tipo": c["tipo"], "codigo": c["codigo"], "programada": c["prog"].isoformat(),
             "limite": limite.isoformat(), "dias_vencido": (hoy - limite).days}
        )
    return vencidos


def cargar_dataset(ruta: str | Path) -> dict:
    d = json.loads(Path(ruta).read_text(encoding="utf-8"))
    for n in d["ninos"]:
        n["nacimiento"] = date.fromisoformat(n["nacimiento"])
        for e in n["evaluaciones"]:
            e["fecha"] = date.fromisoformat(e["fecha"])
    return d


def etiquetar(dataset: dict, hoy: date) -> dict:
    etiquetas = {}
    for n in dataset["ninos"]:
        v = controles_vencidos(n, hoy)
        etiquetas[n["dni"]] = {"vencido": bool(v), "n_vencidos": len(v), "controles": v}
    return etiquetas


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset")
    ap.add_argument("--hoy", default=None, help="AAAA-MM-DD (por defecto, fecha de hoy en Perú)")
    ap.add_argument("--salida", default=None)
    a = ap.parse_args()
    hoy = date.fromisoformat(a.hoy) if a.hoy else hoy_peru()
    ds = cargar_dataset(a.dataset)
    et = etiquetar(ds, hoy)
    pos = sum(1 for e in et.values() if e["vencido"])
    print(f"Oráculo: {len(et)} niños, hoy={hoy}, con >=1 control vencido: {pos}, sin vencidos: {len(et) - pos}")
    if a.salida:
        Path(a.salida).write_text(json.dumps({"hoy": hoy.isoformat(), "etiquetas": et}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
