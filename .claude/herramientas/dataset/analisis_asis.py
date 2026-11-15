#!/usr/bin/env python3
"""Línea base AS-IS del seguimiento de anemia a partir del dataset DIRESA Junín.

Lee el CSV completo (latin-1, separador ';', nulos "NULL", fechas dd/mm/aaaa) y
calcula perfil, calidad del dato e indicadores de proceso AS-IS. Escribe:

  entregables/semana-09/metricas/datos/asis_dataset_diresa.json
  entregables/semana-09/metricas/asis_dataset_diresa.md
  entregables/semana-09/metricas/graficos/g7_asis_cascada_seguimiento.(png|svg)
  entregables/semana-09/metricas/graficos/g8_asis_por_provincia.(png|svg)
  entregables/semana-09/metricas/graficos/g9_asis_suplementacion.(png|svg)

Uso (desde cualquier directorio; todas las rutas son relativas a la raíz del repo):

    python .claude/herramientas/dataset/analisis_asis.py [--sin-graficos]

Requisitos: pandas, matplotlib. No modifica ninguna fecha ni valor del dataset.
"""
from __future__ import annotations

import argparse
import glob
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[3]
CSV = next(iter(sorted(glob.glob(str(RAIZ / "pmv_fastapi" / "datos" / "Ni*menores_de_36_meses*.csv")))), None)
SALIDA = RAIZ / "entregables" / "semana-09" / "metricas"
JSON_OUT = SALIDA / "datos" / "asis_dataset_diresa.json"
MD_OUT = SALIDA / "asis_dataset_diresa.md"
GRAF = SALIDA / "graficos"

CORTE = pd.Timestamp(2024, 6, 30)  # fecha de corte del dataset (último dx: 21/06/2024)
PLAZOS = {"mes": 30, "3m": 90, "6m": 180}  # fecha esperada = fecha_dx + plazo (supuesto declarado)
HOLGURA = 30  # días de tolerancia de la ventana (el máximo observado es plazo + 29)
COL_FECHA = {"mes": "fecha_dosaje_mes", "3m": "fecha_dosaje_3_meses", "6m": "fecha_dosaje_6_meses"}
COL_HB = {"mes": "hb", "3m": "hb_tresmeses", "6m": "hb_seismeses"}
ETQ = {"mes": "al mes", "3m": "a los 3 meses", "6m": "a los 6 meses"}
FECHAS = ["fecha_nac", "fecha_dx", "fecha_dosaje_dx", "fecha_dosaje_mes", "fecha_dosaje_3_meses",
          "fecha_dosaje_6_meses", "fecha_recup"] + [f"fecha_supT{i}" for i in range(1, 7)] + ["fecha_ta"]
HB = ["hb_dx", "hb", "hb_tresmeses", "hb_seismeses"]
# Altitud de la capital provincial (m s. n. m.), INEI, Perú: Compendio Estadístico 2014, cuadro 1.12
ALTITUD = {"HUANCAYO": 3245, "CONCEPCION": 3286, "CHANCHAMAYO": 775, "JAUJA": 3389, "JUNIN": 4113,
           "SATIPO": 628, "TARMA": 3059, "YAULI": 3725, "CHUPACA": 3281}
# Ajuste de Hb por altitud, referencial (OMS 2011): se resta del valor observado. Solo análisis exploratorio.
AJUSTE_ALT = [(4500, 4.5), (4000, 3.5), (3500, 2.7), (3000, 1.9), (2500, 1.3), (2000, 0.8),
              (1500, 0.5), (1000, 0.2), (0, 0.0)]
FUENTE = ("Fuente: DIRESA Junín, HIS, dataset “Niños menores de 36 meses con dx de anemia en la Región Junín” "
          "(2022–2024); elaboración propia")


def mil(n):
    return f"{int(n):,}".replace(",", " ")


def pct(n, d):
    return round(100.0 * n / d, 1) if d else None


def ind(n, d, formula, **extra):
    r = {"n": int(n), "N": int(d), "pct": pct(n, d), "formula": formula}
    r.update(extra)
    return r


def cargar():
    if CSV is None:
        raise SystemExit("No se encontró el CSV en pmv_fastapi/datos/")
    d = pd.read_csv(CSV, sep=";", encoding="latin-1", dtype=str, keep_default_na=False)
    d = d.replace("NULL", np.nan)
    d = d.replace(r"^\s*$", np.nan, regex=True)
    for c in FECHAS:
        d[c] = pd.to_datetime(d[c], format="%d/%m/%Y", errors="coerce")
    for c in HB:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["recup"] = d["recup"].astype(int)
    d["sev"] = d["valor_lab_dx"].fillna("SIN DATO")
    d["edad_m"] = np.floor((d["fecha_dx"] - d["fecha_nac"]).dt.days / 30.4375)
    d["n_entregas"] = d[[f"fecha_supT{i}" for i in range(1, 7)]].notna().sum(axis=1)
    return d


def ajuste_altitud(prov):
    alt = ALTITUD.get(prov)
    if alt is None:
        return np.nan
    return next(a for lim, a in AJUSTE_ALT if alt >= lim)


# ----------------------------------------------------------------------------------------------
def perfil(d):
    n = len(d)
    vc = lambda s: {str(k): {"n": int(v), "pct": pct(v, n)} for k, v in s.value_counts(dropna=False).items()}
    edad = d["edad_m"]
    grupos = pd.cut(edad, [-1, 5, 11, 23, 35, 999], labels=["<6 m", "6–11 m", "12–23 m", "24–35 m", "≥36 m"])
    seguro_tokens = d["seguro"].str.replace(" ", "").str.strip(",").str.split(",")
    return {
        "filas": n,
        "rango_fecha_dx": [d.fecha_dx.min().strftime("%d/%m/%Y"), d.fecha_dx.max().strftime("%d/%m/%Y")],
        "rango_fecha_nac": [d.fecha_nac.min().strftime("%d/%m/%Y"), d.fecha_nac.max().strftime("%d/%m/%Y")],
        "fecha_corte_supuesta": CORTE.strftime("%d/%m/%Y"),
        "cobertura": {
            "provincias": int(d.Provincia.nunique()), "redes": int(d.Red.nunique()),
            "microredes": int(d.MicroRed.nunique()),
            "distritos_nombres_distintos": int(d.Distrito.nunique()),
            "distritos_pares_provincia_distrito": int(d[["Provincia", "Distrito"]].drop_duplicates().shape[0]),
            "establecimientos_nombres_distintos": int(d.Nombre_Establecimiento.nunique()),
            "establecimientos_combinacion_red_microred_nombre":
                int(d[["Red", "MicroRed", "Nombre_Establecimiento"]].drop_duplicates().shape[0]),
        },
        "por_provincia": vc(d.Provincia),
        "por_red": vc(d.Red),
        "edad_al_dx_meses": {
            "mediana": float(edad.median()), "p25": float(edad.quantile(.25)), "p75": float(edad.quantile(.75)),
            "min": float(edad.min()), "max": float(edad.max()),
            "grupos": {str(k): {"n": int(v), "pct": pct(v, n)} for k, v in grupos.value_counts(sort=False).items()},
        },
        "severidad_his": vc(d.sev),
        "seguro_valores_crudos": vc(d.seguro),
        "seguro_con_mas_de_un_codigo": ind((seguro_tokens.str.len() > 1).sum(), n, "filas con ≥2 códigos de seguro ÷ filas"),
    }


# ----------------------------------------------------------------------------------------------
def calidad(d):
    n = len(d)
    nulos = {c: {"n": int(d[c].isna().sum()), "pct": pct(d[c].isna().sum(), n)} for c in d.columns
             if c not in ("sev", "edad_m", "n_entregas")}
    nd = pd.read_csv(CSV, sep=";", encoding="latin-1", dtype=str, usecols=["num_doc"])["num_doc"]
    q = {"nulos_por_columna": nulos}
    q["num_doc"] = {
        "valores_distintos": int(nd.nunique()), "filas": n,
        "en_notacion_cientifica": ind(nd.str.contains(r"[Ee]\+?\d+$").sum(), n, "num_doc con 'E+nn' ÷ filas"),
        "filas_con_num_doc_repetido": ind(nd.duplicated(keep=False).sum(), n, "filas cuyo num_doc aparece ≥2 veces ÷ filas"),
        "maximo_filas_por_num_doc": int(nd.value_counts().max()),
        "pares_num_doc_fecha_nac_distintos": int(pd.concat([nd, d.fecha_nac], axis=1).drop_duplicates().shape[0]),
        "conclusion": "No utilizable como identificador ni como clave: está truncado a 6 cifras significativas "
                      "(notación científica) y colisiona entre niños distintos.",
    }
    cols_sin_sev = [c for c in d.columns if c not in ("sev", "edad_m", "n_entregas")]
    q["duplicados"] = {
        "filas_duplicadas_exactas_extra": int(d[cols_sin_sev].duplicated().sum()),
        "filas_involucradas_en_duplicados_exactos": int(d[cols_sin_sev].duplicated(keep=False).sum()),
        "filas_con_igual_num_doc_fecha_nac_fecha_dx": int(d.assign(nd=nd).duplicated(["nd", "fecha_nac", "fecha_dx"], keep=False).sum()),
        "nota": "Sin identificador fiable no se puede afirmar si son el mismo niño; son posibles duplicados.",
    }

    # Severidad vs hb_dx
    h = d["hb_dx"]
    crit = {}
    crit["criterio_A_sin_altitud"] = (
        "Criterio A (cribado simple, sin altitud): severidad LEV/MOD/SEV registrada con Hb observada ≥ 13,0 g/dL. "
        "Es una cota gruesa: en provincias de altura puede ser un falso positivo, porque la severidad se asigna con Hb ajustada.")
    selva = d.Provincia.map(ALTITUD) <= 1000
    crit["LEV_con_hb_dx_ge_13_en_provincias_hasta_1000_m"] = ind(
        ((h >= 13) & (d.valor_lab_dx == "LEV") & selva).sum(), ((d.valor_lab_dx == "LEV") & h.notna() & selva).sum(),
        "LEV con hb_dx≥13 en Satipo/Chanchamayo (capital < 1 000 m, ajuste ≈ 0) ÷ LEV con hb_dx en esas provincias")
    crit["hb_dx_ge_13_con_severidad"] = ind(((h >= 13) & d.valor_lab_dx.notna()).sum(), h.notna().sum(),
                                            "dx con severidad y hb_dx≥13 ÷ dx con hb_dx")
    crit["LEV_con_hb_dx_ge_13"] = ind(((h >= 13) & (d.valor_lab_dx == "LEV")).sum(), ((d.valor_lab_dx == "LEV") & h.notna()).sum(),
                                      "LEV con hb_dx≥13 ÷ LEV con hb_dx")
    crit["hb_dx_maxima_en_LEV"] = float(h[d.valor_lab_dx == "LEV"].max())
    crit["SEV_con_hb_dx_ge_11"] = ind(((h >= 11) & (d.valor_lab_dx == "SEV")).sum(), ((d.valor_lab_dx == "SEV") & h.notna()).sum(),
                                      "SEV con hb_dx≥11 ÷ SEV con hb_dx")
    crit["mediana_hb_dx_por_provincia_y_severidad"] = {
        p: {s: (round(float(v), 1) if pd.notna(v) else None) for s, v in g.groupby(d.loc[g.index, "valor_lab_dx"]).median().items()}
        for p, g in d.groupby("Provincia")["hb_dx"]}
    crit["lectura"] = ("La mediana de hb_dx de los casos LEV sube con la altitud (≈10,4 g/dL en Satipo/Chanchamayo frente a ≈13,6 "
                       "en Junín): la severidad del HIS se asigna con Hb AJUSTADA por altitud y hb_dx es la Hb OBSERVADA. "
                       "Por eso 'LEV con Hb ≥ 13' no es necesariamente un error, pero sí un valor que un usuario o un "
                       "sistema sin el ajuste interpretaría como no anémico.")
    # Criterio B exploratorio con ajuste de altitud (aprox.)
    aj = d.Provincia.map({p: ajuste_altitud(p) for p in ALTITUD})
    hadj = h - aj
    esp = pd.Series(np.where(hadj >= 11, "SIN ANEMIA", np.where(hadj >= 10, "LEV", np.where(hadj >= 7, "MOD", "SEV"))), index=d.index)
    con = h.notna() & d.valor_lab_dx.notna()
    conc = (esp[con] == d.valor_lab_dx[con])
    crit["criterio_B_exploratorio_con_altitud"] = {
        "descripcion": "Hb ajustada = hb_dx − ajuste OMS 2011 según altitud de la capital provincial (INEI 2014); "
                       "umbrales: SIN ANEMIA ≥ 11,0; LEV 10,0–10,9; MOD 7,0–9,9; SEV < 7,0. Es aproximado "
                       "(altitud de la capital, no del establecimiento; tabla de ajuste referencial a contrastar con la NTS vigente).",
        "concordancia": ind(conc.sum(), con.sum(), "severidad esperada = severidad HIS ÷ dx con severidad y hb_dx"),
        "esperado_sin_anemia_pero_con_severidad": ind((esp[con] == "SIN ANEMIA").sum(), con.sum(), "Hb ajustada ≥ 11 con severidad registrada ÷ idem"),
        "matriz_esperada_vs_HIS": {e: {s: int(v) for s, v in row.items()} for e, row in
                                    pd.crosstab(esp[con], d.valor_lab_dx[con]).iterrows()},
    }
    q["severidad_vs_hb_dx"] = crit

    # Fechas incoherentes
    dx = d.fecha_dx
    inc = {}
    inc["dosaje_dx_antes_del_dx"] = int((d.fecha_dosaje_dx < dx).sum())
    inc["dosaje_dx_despues_del_dx"] = int((d.fecha_dosaje_dx > dx).sum())
    inc["recuperacion_antes_del_dx"] = int((d.fecha_recup < dx).sum())
    inc["nacimiento_despues_del_dx"] = int((d.fecha_nac > dx).sum())
    inc["control_antes_del_dx"] = int(sum((d[c] < dx).sum() for c in COL_FECHA.values()))
    inc["suplementacion_antes_del_dx"] = int(sum((d[f"fecha_supT{i}"] < dx).sum() for i in range(1, 7)))
    inc["fin_tratamiento_antes_del_dx"] = int((d.fecha_ta < dx).sum())
    inc["cualquier_fecha_posterior_al_corte"] = int((d[FECHAS] > CORTE).any(axis=1).sum())
    inc["edad_al_dx_fuera_de_0_35_meses"] = int(((d.edad_m < 0) | (d.edad_m > 35)).sum())
    inc["entregas_no_monotonas"] = int((pd.concat([d[f"fecha_supT{i}"] for i in range(1, 7)], axis=1).diff(axis=1) < pd.Timedelta(0)).any(axis=1).sum())
    inc["recup1_sin_fecha_recup_o_viceversa"] = int(((d.recup == 1) != d.fecha_recup.notna()).sum())
    inc["fecha_ta_igual_fecha_dx"] = ind((d.fecha_ta == dx).sum(), d.fecha_ta.notna().sum(), "fecha_ta = fecha_dx ÷ filas con fecha_ta")
    inc["primera_entrega_igual_fecha_dx"] = ind((d.fecha_supT1 == dx).sum(), d.fecha_supT1.notna().sum(), "fecha_supT1 = fecha_dx ÷ filas con fecha_supT1")
    inc["dosaje_dx_igual_fecha_dx"] = ind((d.fecha_dosaje_dx == dx).sum(), d.fecha_dosaje_dx.notna().sum(), "fecha_dosaje_dx = fecha_dx ÷ filas con fecha_dosaje_dx")
    inc["rango_dias_dx_a_control"] = {
        k: [int((d[COL_FECHA[k]] - dx).dt.days.min()), int((d[COL_FECHA[k]] - dx).dt.days.max())] for k in COL_FECHA}
    q["fechas_incoherentes"] = inc

    # Hb fuera de rango y fecha sin Hb
    q["hb_fuera_de_rango_3_20"] = {c: {"menor_3": int((d[c] < 3).sum()), "mayor_20": int((d[c] > 20).sum())} for c in HB}
    q["hb_fuera_de_rango_total"] = int(sum(((d[c] < 3) | (d[c] > 20)).sum() for c in HB))
    q["fecha_dosaje_sin_hb"] = {
        "dx": ind((d.fecha_dosaje_dx.notna() & d.hb_dx.isna()).sum(), d.fecha_dosaje_dx.notna().sum(), "fecha_dosaje_dx sin hb_dx ÷ fecha_dosaje_dx"),
        **{k: ind((d[COL_FECHA[k]].notna() & d[COL_HB[k]].isna()).sum(), d[COL_FECHA[k]].notna().sum(),
                  f"fecha de dosaje {ETQ[k]} sin Hb ÷ con fecha") for k in COL_FECHA}}
    q["recup_documentada_con_hb_6m_menor_11"] = ind(
        ((d.recup == 1) & (d.hb_seismeses < 11)).sum(), ((d.recup == 1) & d.hb_seismeses.notna()).sum(),
        "recup=1 con hb_seismeses<11 (observada, antes de ajustar por altitud: ya sería anemia) ÷ recup=1 con hb_seismeses")
    return q


# ----------------------------------------------------------------------------------------------
def elegible(d, plazo, extra=0):
    """Tiene tiempo de seguimiento posible: fecha_dx + plazo + HOLGURA (+extra) <= corte."""
    return d.fecha_dx <= CORTE - pd.Timedelta(days=plazo + HOLGURA + extra)


def indicadores(d):
    """Indicadores sobre un subconjunto (global, provincia o severidad)."""
    n = len(d)
    r = {"diagnosticados": n}
    dx = d.fecha_dx
    for k, pz in PLAZOS.items():
        f = d[COL_FECHA[k]]
        hecho = f.notna()
        el = elegible(d, pz)
        el0 = d.fecha_dx <= CORTE - pd.Timedelta(days=pz)
        r[f"control_{k}"] = ind(hecho.sum(), n, f"fecha_dosaje {ETQ[k]} registrada ÷ diagnosticados")
        r[f"control_{k}_con_seguimiento_posible"] = ind(
            (hecho & el).sum(), el.sum(),
            f"control {ETQ[k]} ÷ diagnosticados con fecha_dx ≤ {(CORTE - pd.Timedelta(days=pz + HOLGURA)).strftime('%d/%m/%Y')} (plazo {pz} d + holgura {HOLGURA} d antes del corte)")
        r[f"control_{k}_sin_holgura"] = ind((hecho & el0).sum(), el0.sum(),
                                           f"idem con fecha_dx ≤ {(CORTE - pd.Timedelta(days=pz)).strftime('%d/%m/%Y')} (sin holgura; sensibilidad)")
        r[f"control_{k}_con_hb"] = ind((hecho & d[COL_HB[k]].notna()).sum(), n, f"control {ETQ[k]} con fecha y Hb ÷ diagnosticados")
        dem = (f - (dx + pd.Timedelta(days=pz))).dt.days.dropna()
        r[f"demora_{k}_dias"] = {
            "n": int(len(dem)), "mediana": float(dem.median()) if len(dem) else None,
            "p90": float(dem.quantile(.9)) if len(dem) else None,
            "min": float(dem.min()) if len(dem) else None, "max": float(dem.max()) if len(dem) else None,
            "pct_con_retraso_positivo": pct((dem > 0).sum(), len(dem)),
            "formula": f"fecha_dosaje {ETQ[k]} − (fecha_dx + {pz} d), solo controles realizados"}
    ncon = d[[COL_FECHA[k] for k in PLAZOS]].notna().sum(axis=1)
    r["sin_ningun_control"] = ind((ncon == 0).sum(), n, "sin dosaje a 1, 3 ni 6 meses ÷ diagnosticados")
    r["tres_controles"] = ind((ncon == 3).sum(), n, "con los 3 dosajes (mes, 3 m, 6 m) ÷ diagnosticados")
    e6 = elegible(d, PLAZOS["6m"])
    r["sin_ningun_control_con_seguimiento_posible"] = ind(((ncon == 0) & e6).sum(), e6.sum(), "sin ningún dosaje ÷ dx con seguimiento de 6 m posible")
    r["tres_controles_con_seguimiento_posible"] = ind(((ncon == 3) & e6).sum(), e6.sum(), "los 3 dosajes ÷ dx con seguimiento de 6 m posible")
    r["perdida_seguimiento_6m"] = ind((d.fecha_dosaje_6_meses.isna()).sum(), n, "sin dosaje a los 6 meses ÷ diagnosticados (= 100 − control 6 m)")
    r["perdida_seguimiento_6m_con_seguimiento_posible"] = ind(
        (d.fecha_dosaje_6_meses.isna() & e6).sum(), e6.sum(), "sin dosaje a 6 m ÷ dx con seguimiento de 6 m posible")
    # Recuperación
    rec = d.recup == 1
    r["recuperacion_documentada"] = ind(rec.sum(), n, "recup=1 (con fecha_recup) ÷ diagnosticados")
    r["recuperacion_con_seguimiento_6m"] = ind((rec & e6).sum(), e6.sum(), "recup=1 ÷ dx con fecha_dx ≤ " + (CORTE - pd.Timedelta(days=PLAZOS['6m'] + HOLGURA)).strftime('%d/%m/%Y'))
    e12 = d.fecha_dx <= CORTE - pd.Timedelta(days=365)
    r["recuperacion_con_seguimiento_12m"] = ind((rec & e12).sum(), e12.sum(), "recup=1 ÷ dx con fecha_dx ≤ " + (CORTE - pd.Timedelta(days=365)).strftime('%d/%m/%Y') + " (≥ 1 año de seguimiento)")
    c6 = d.fecha_dosaje_6_meses.notna()
    r["recuperados_sobre_control_cierre"] = ind((rec & c6).sum(), c6.sum(), "recup=1 con dosaje a 6 m ÷ con dosaje a 6 m (control de cierre; Tabla 8 de S1)")
    dr = (d.fecha_recup - dx).dt.days.dropna()
    r["dias_dx_a_recuperacion"] = {"n": int(len(dr)), "mediana": float(dr.median()) if len(dr) else None,
                                   "p90": float(dr.quantile(.9)) if len(dr) else None}
    # Suplementación
    ne = d.n_entregas
    r["suplementacion_distribucion"] = {str(i): ind((ne == i).sum(), n, f"{i} entregas ÷ diagnosticados") for i in range(7)}
    r["entregas_ge5"] = ind((ne >= 5).sum(), n, "≥5 fechas fecha_supT1..T6 registradas ÷ diagnosticados")
    r["entregas_0"] = ind((ne == 0).sum(), n, "0 entregas registradas ÷ diagnosticados")
    s5 = d.fecha_dx <= CORTE - pd.Timedelta(days=120 + HOLGURA)
    r["entregas_ge5_con_seguimiento_posible"] = ind(((ne >= 5) & s5).sum(), s5.sum(),
                                                   "≥5 entregas ÷ dx con fecha_dx ≤ " + (CORTE - pd.Timedelta(days=150)).strftime('%d/%m/%Y') + " (5.ª entrega esperada a ~120 d + holgura)")
    r["media_entregas"] = round(float(ne.mean()), 2)
    r["fin_tratamiento_registrado"] = ind(d.fecha_ta.notna().sum(), n, "fecha_ta registrada ÷ diagnosticados")
    r["fin_tratamiento_con_seguimiento_6m"] = ind((d.fecha_ta.notna() & e6).sum(), e6.sum(), "fecha_ta registrada ÷ dx con seguimiento de 6 m posible")
    d1 = (d.fecha_supT1 - dx).dt.days.dropna()
    r["dx_a_primera_suplementacion_dias"] = {
        "n": int(len(d1)), "mediana": float(d1.median()) if len(d1) else None, "p90": float(d1.quantile(.9)) if len(d1) else None,
        "pct_mismo_dia": pct((d1 == 0).sum(), len(d1)),
        "sin_primera_entrega": ind(d.fecha_supT1.isna().sum(), n, "sin fecha_supT1 ÷ diagnosticados"),
        "formula": "fecha_supT1 − fecha_dx (diagnosticados con entrega 1)"}
    r["sin_hb_dx"] = ind(d.hb_dx.isna().sum(), n, "sin hb_dx ÷ diagnosticados")
    return r


COLS_TABLA = [("control_mes", "Control 1 m"), ("control_3m", "Control 3 m"), ("control_6m", "Control 6 m"),
              ("control_6m_con_seguimiento_posible", "Control 6 m (seg. posible)"),
              ("recuperacion_documentada", "Recup."), ("recuperacion_con_seguimiento_6m", "Recup. (seg. 6 m)"),
              ("entregas_ge5", "≥5 entregas"), ("entregas_0", "0 entregas")]


def tabla_por(d, col, orden=None):
    out = {}
    claves = orden or sorted(d[col].unique(), key=lambda k: -(d[col] == k).sum())
    for k in claves:
        out[str(k)] = indicadores(d[d[col] == k])
    return out


def por_trimestre(d):
    out = {}
    for q, g in d.groupby(d.fecha_dx.dt.to_period("Q")):
        out[str(q)] = {"n": len(g), "control_mes_pct": pct(g.fecha_dosaje_mes.notna().sum(), len(g)),
                       "control_3m_pct": pct(g.fecha_dosaje_3_meses.notna().sum(), len(g)),
                       "control_6m_pct": pct(g.fecha_dosaje_6_meses.notna().sum(), len(g)),
                       "recup_pct": pct((g.recup == 1).sum(), len(g))}
    return out


# ----------------------------------------------------------------------------------------------
BRECHA = [
    ("Cobertura oportuna de medición/control (proceso)", "control_mes / control_3m / control_6m (global y con seguimiento posible)",
     "Línea base del indicador de valor V2/V3 «controles programados y vencidos visibles»: hoy no existe agenda normativa; "
     "el control depende de que el niño vuelva y alguien lo registre."),
    ("Demora de controles vencidos (proceso)", "demora_mes / demora_3m / demora_6m (mediana y p90 de días respecto de la fecha esperada)",
     "Solo mide los controles que SÍ se hicieron; los vencidos nunca atendidos no tienen demora observable "
     "(sesgo de supervivencia). El Inc. 2 muestra los vencidos con su demora actual."),
    ("Pérdida de seguimiento (valor)", "perdida_seguimiento_6m y sin_ningun_control (global y con seguimiento posible)",
     "Línea base del indicador de pérdida de seguimiento de S1 (y S3-4): niños sin cierre a 6 meses; "
     "el Inc. 2 la ataca con alertas y agenda del personal."),
    ("Recuperación documentada al año (resultado)", "recuperacion_documentada, recuperacion_con_seguimiento_6m/12m, recuperados_sobre_control_cierre",
     "Resultado clínico de referencia; no es atribuible solo al sistema, se usa como contexto."),
]

ADVERTENCIAS = [
    "El dataset solo contiene niños CON diagnóstico de anemia: no hay población total ni sanos, por lo que no se puede calcular prevalencia ni cobertura de tamizaje.",
    "Solo constan dosajes dentro de la ventana de cada control (1.º: 29–58 d; 3.º: 87–119 d; 6.º: 178–209 d desde el dx). Un control fuera de ventana, "
    "o no registrado en el HIS, aparece como «no realizado»: el indicador mide control registrado en ventana, no asistencia real.",
    "Censura por corte: los diagnósticos recientes (hasta 21/06/2024) no han tenido tiempo de cumplir los controles. Por eso se reportan "
    "dos lecturas: sobre todos los diagnosticados (cifra bruta, penalizada) y sobre quienes tenían seguimiento posible (cifra más justa).",
    "La fecha esperada de cada control (dx + 30/90/180 d) y la holgura de 30 d son supuestos operativos de este análisis, coherentes con el rango observado de las fechas; deben contrastarse con la norma técnica vigente.",
    "num_doc no es confiable (notación científica, no único): no hay identificación del niño; puede haber repeticiones del mismo niño en filas distintas (varios diagnósticos o duplicados). No se intentó reidentificar a nadie.",
    "La severidad del HIS parece asignarse con Hb ajustada por altitud, mientras hb_dx es la observada; la concordancia calculada con la altitud de la capital provincial es una aproximación.",
    "fecha_supT1 coincide con fecha_dx en el 100 % de los casos y fecha_ta coincide con fecha_dx en una parte de los registros: el tiempo dx→primera suplementación no mide demora real y fecha_ta debe usarse con cautela.",
    "Una entrega no registrada puede ser entrega no hecha o registro faltante; el dataset no distingue ambas cosas.",
    "El dataset no incluye adherencia real (consumo), visitas domiciliarias, referencias ni motivos de abandono.",
]


def construir():
    d = cargar()
    res = {
        "fuente": "pmv_fastapi/datos/Niños_menores_de_36_meses_con_dx_de_anemia_en_la_Región_ Junín.csv (DIRESA Junín, HIS)",
        "fecha_corte": CORTE.strftime("%d/%m/%Y"),
        "parametros": {"plazos_dias": PLAZOS, "holgura_dias": HOLGURA,
                       "regla_seguimiento_posible": "fecha_dx + plazo + holgura ≤ fecha de corte"},
        "perfil": perfil(d),
        "calidad": calidad(d),
        "indicadores_globales": indicadores(d),
        "por_provincia": tabla_por(d, "Provincia"),
        "por_severidad": tabla_por(d, "sev", [s for s in ["LEV", "MOD", "SEV", "SIN DATO"]]),
        "por_trimestre_dx": por_trimestre(d),
        "brecha_inc2": [{"indicador_S1_tabla8": a, "indicador_AS_IS": b, "relacion_con_inc2": c} for a, b, c in BRECHA],
        "advertencias": ADVERTENCIAS,
    }
    return d, res


# ----------------------------------------------------------------------------------------------
def f1(x):
    return "—" if x is None else f"{x:.1f}".replace(".", ",")


def celda(i):
    return f"{f1(i['pct'])} % ({mil(i['n'])}/{mil(i['N'])})" if i["N"] else "—"


def tabla_md(res, clave, titulo_col):
    filas = [f"| {titulo_col} | N | " + " | ".join(t for _, t in COLS_TABLA) + " |",
             "|---|---:|" + "---:|" * len(COLS_TABLA)]
    for k, r in res[clave].items():
        filas.append(f"| {k} | {mil(r['diagnosticados'])} | " +
                     " | ".join(f"{f1(r[c]['pct'])}" if r[c]["N"] else "—" for c, _ in COLS_TABLA) + " |")
    return "\n".join(filas)


def escribir_md(res):
    p, q, g = res["perfil"], res["calidad"], res["indicadores_globales"]
    L = []
    a = L.append
    a("# Línea base AS-IS del seguimiento de anemia (dataset DIRESA Junín)\n")
    a(f"Generado por `.claude/herramientas/dataset/analisis_asis.py` a partir de `pmv_fastapi/datos/Niños_menores_de_36_meses_con_dx_de_anemia_en_la_Región_ Junín.csv` "
      f"(HIS, diagnósticos del {p['rango_fecha_dx'][0]} al {p['rango_fecha_dx'][1]}). Fecha de corte usada: {res['fecha_corte']}. "
      "Datos completos y fórmulas en `datos/asis_dataset_diresa.json`. Los porcentajes llevan un decimal; entre paréntesis, numerador/denominador.\n")
    a("## 1. Perfil del dataset\n")
    c = p["cobertura"]
    a(f"- Filas: **{mil(p['filas'])}**. Nacimientos: {p['rango_fecha_nac'][0]} a {p['rango_fecha_nac'][1]}.")
    a(f"- Cobertura: {c['provincias']} provincias, {c['redes']} redes, {c['microredes']} microredes, "
      f"{c['distritos_nombres_distintos']} distritos (nombres distintos; {c['distritos_pares_provincia_distrito']} pares provincia–distrito), "
      f"{c['establecimientos_nombres_distintos']} establecimientos (nombres distintos; {c['establecimientos_combinacion_red_microred_nombre']} combinaciones red–microred–nombre).")
    e = p["edad_al_dx_meses"]
    a(f"- Edad al diagnóstico (meses cumplidos): mediana {f1(e['mediana'])}, cuartiles {f1(e['p25'])}–{f1(e['p75'])}.")
    a("- Grupos de edad: " + "; ".join(f"{k} {f1(v['pct'])} % ({v['n']})" for k, v in e["grupos"].items() if v["n"]) + ".")
    a("- Severidad HIS: " + "; ".join(f"{k} {f1(v['pct'])} % ({v['n']})" for k, v in p["severidad_his"].items()) + ".")
    a(f"- Seguro (código numérico sin tabla de códigos en el diccionario): " +
      "; ".join(f"`{k.strip()}` {f1(v['pct'])} %" for k, v in list(p["seguro_valores_crudos"].items())[:5]) +
      f"; con ≥2 códigos: {celda(p['seguro_con_mas_de_un_codigo'])}.\n")
    a("| Provincia | Diagnosticados | % |\n|---|---:|---:|")
    for k, v in p["por_provincia"].items():
        a(f"| {k} | {mil(v['n'])} | {f1(v['pct'])} |")
    a("\n| Red | Diagnosticados | % |\n|---|---:|---:|")
    for k, v in p["por_red"].items():
        a(f"| {k} | {mil(v['n'])} | {f1(v['pct'])} |")

    a("\n## 2. Calidad del dato\n")
    nd = q["num_doc"]
    a(f"- **num_doc no utilizable**: {mil(nd['valores_distintos'])} valores distintos para {mil(nd['filas'])} filas; en notación científica {celda(nd['en_notacion_cientifica'])}; "
      f"filas con num_doc repetido {celda(nd['filas_con_num_doc_repetido'])}; máximo {nd['maximo_filas_por_num_doc']} filas con el mismo valor.")
    dp = q["duplicados"]
    a(f"- Posibles duplicados: {dp['filas_duplicadas_exactas_extra']} filas idénticas en todas las columnas (excedentes sobre la primera aparición); "
      f"{dp['filas_con_igual_num_doc_fecha_nac_fecha_dx']} filas comparten num_doc, fecha de nacimiento y fecha de diagnóstico con otra.")
    a("- Nulos por columna (%): " + ", ".join(f"{k} {f1(v['pct'])}" for k, v in q["nulos_por_columna"].items() if k != "num_doc") + ".")
    s = q["severidad_vs_hb_dx"]
    a(f"- **Severidad vs hb_dx.** {s['criterio_A_sin_altitud']} Resultado: {celda(s['hb_dx_ge_13_con_severidad'])} con severidad y Hb ≥ 13; "
      f"en LEV {celda(s['LEV_con_hb_dx_ge_13'])} (máximo {f1(s['hb_dx_maxima_en_LEV'])} g/dL); en provincias bajas (Satipo, Chanchamayo), donde el ajuste es casi nulo, "
      f"LEV con Hb ≥ 13: {celda(s['LEV_con_hb_dx_ge_13_en_provincias_hasta_1000_m'])}; SEV con Hb ≥ 11: {celda(s['SEV_con_hb_dx_ge_11'])}. {s['lectura']}")
    b = s["criterio_B_exploratorio_con_altitud"]
    a(f"- Criterio B (exploratorio, con altitud): concordancia con la severidad esperada {celda(b['concordancia'])}; "
      f"Hb ajustada ≥ 11 pese a tener severidad: {celda(b['esperado_sin_anemia_pero_con_severidad'])}. {b['descripcion']}")
    i = q["fechas_incoherentes"]
    a(f"- Fechas incoherentes: dosaje del dx antes del dx {i['dosaje_dx_antes_del_dx']}; recuperación antes del dx {i['recuperacion_antes_del_dx']}; "
      f"nacimiento después del dx {i['nacimiento_despues_del_dx']}; controles antes del dx {i['control_antes_del_dx']}; "
      f"entregas antes del dx {i['suplementacion_antes_del_dx']}; fin de tratamiento antes del dx {i['fin_tratamiento_antes_del_dx']}; "
      f"fechas posteriores al corte {i['cualquier_fecha_posterior_al_corte']}; edad fuera de 0–35 m {i['edad_al_dx_fuera_de_0_35_meses']}; "
      f"entregas no monótonas {i['entregas_no_monotonas']}; recup/fecha_recup contradictorios {i['recup1_sin_fecha_recup_o_viceversa']}. "
      "Es decir, el orden temporal básico es consistente.")
    a(f"- Rasgos de registro: fecha_supT1 = fecha_dx en {celda(i['primera_entrega_igual_fecha_dx'])}; fecha_ta = fecha_dx en {celda(i['fecha_ta_igual_fecha_dx'])}; "
      f"fecha_dosaje_dx = fecha_dx en {celda(i['dosaje_dx_igual_fecha_dx'])}.")
    a(f"- Hb fuera de 3–20 g/dL: {q['hb_fuera_de_rango_total']} valores (" +
      ", ".join(f"{k}: <3 = {v['menor_3']}, >20 = {v['mayor_20']}" for k, v in q["hb_fuera_de_rango_3_20"].items()) + ").")
    fs = q["fecha_dosaje_sin_hb"]
    a("- Fecha de dosaje sin valor de Hb: dx " + celda(fs["dx"]) + "; mes " + celda(fs["mes"]) + "; 3 m " + celda(fs["3m"]) + "; 6 m " + celda(fs["6m"]) + ".")
    a(f"- Recuperación documentada con Hb a 6 m < 11 g/dL observada: {celda(q['recup_documentada_con_hb_6m_menor_11'])} (la Hb observada ya sería anemia aun sin ajustar).\n")

    a("## 3. Indicadores de proceso AS-IS (global)\n")
    a("«Seg. posible» = solo diagnosticados con `fecha_dx + plazo + 30 d ≤ 30/06/2024` (plazos: 30, 90 y 180 días).\n")
    a("| Indicador | Valor (n/N) | Fórmula |\n|---|---|---|")
    claves = [("control_mes", "Control de Hb al mes"), ("control_mes_con_seguimiento_posible", "Control al mes, seg. posible"),
              ("control_3m", "Control de Hb a los 3 meses"), ("control_3m_con_seguimiento_posible", "Control a los 3 meses, seg. posible"),
              ("control_6m", "Control de Hb a los 6 meses"), ("control_6m_con_seguimiento_posible", "Control a los 6 meses, seg. posible"),
              ("control_6m_sin_holgura", "Control a los 6 meses, sin holgura (sensibilidad)"),
              ("control_mes_con_hb", "Control al mes con Hb"), ("control_3m_con_hb", "Control a los 3 meses con Hb"), ("control_6m_con_hb", "Control a los 6 meses con Hb"),
              ("tres_controles", "Los tres controles"), ("tres_controles_con_seguimiento_posible", "Los tres controles, seg. posible"),
              ("sin_ningun_control", "Ningún control"), ("sin_ningun_control_con_seguimiento_posible", "Ningún control, seg. posible"),
              ("perdida_seguimiento_6m", "Pérdida de seguimiento a 6 meses"), ("perdida_seguimiento_6m_con_seguimiento_posible", "Pérdida de seguimiento a 6 meses, seg. posible"),
              ("recuperacion_documentada", "Recuperación documentada"), ("recuperacion_con_seguimiento_6m", "Recuperación, seg. 6 m posible"),
              ("recuperacion_con_seguimiento_12m", "Recuperación, ≥ 1 año de seguimiento"), ("recuperados_sobre_control_cierre", "Recuperados sobre control de cierre (6 m)"),
              ("entregas_ge5", "Suplementación ≥ 5 entregas"), ("entregas_ge5_con_seguimiento_posible", "≥ 5 entregas, seg. posible"),
              ("entregas_0", "Sin ninguna entrega"), ("fin_tratamiento_registrado", "Fin de tratamiento (fecha_ta) registrado"),
              ("fin_tratamiento_con_seguimiento_6m", "Fin de tratamiento registrado, seg. 6 m posible"), ("sin_hb_dx", "Sin Hb al diagnóstico")]
    for k, t in claves:
        a(f"| {t} | {celda(g[k])} | {g[k]['formula']} |")
    a("\n**Demora respecto de la fecha esperada (solo controles realizados; días, positivo = tarde):**\n")
    a("| Control | N | Mediana | P90 | Mín–máx | % con retraso > 0 |\n|---|---:|---:|---:|---|---:|")
    for k in PLAZOS:
        x = g[f"demora_{k}_dias"]
        a(f"| {ETQ[k].capitalize()} (esperado dx + {PLAZOS[k]} d) | {mil(x['n'])} | {f1(x['mediana'])} | {f1(x['p90'])} | {f1(x['min'])} a {f1(x['max'])} | {f1(x['pct_con_retraso_positivo'])} |")
    a("\nComo el dataset solo contiene dosajes dentro de ventana, la demora de los controles realizados es pequeña por construcción; "
      "la brecha real está en los controles que no constan, no en el retraso de los que sí constan.\n")
    r = g["dias_dx_a_recuperacion"]
    a(f"Recuperación: mediana {f1(r['mediana'])} días desde el diagnóstico (p90 {f1(r['p90'])}, n = {mil(r['n'])}).")
    d1 = g["dx_a_primera_suplementacion_dias"]
    a(f"Tiempo dx → primera suplementación: mediana {f1(d1['mediana'])} d, p90 {f1(d1['p90'])} d; el {f1(d1['pct_mismo_dia'])} % de las primeras entregas consta el mismo día del dx; "
      f"sin primera entrega: {celda(d1['sin_primera_entrega'])}.\n")
    a("**Distribución del n.º de entregas (fecha_supT1..T6):**\n")
    a("| Entregas | " + " | ".join(str(i) for i in range(7)) + " |\n|---|" + "---:|" * 7)
    a("| % | " + " | ".join(f1(g["suplementacion_distribucion"][str(i)]["pct"]) for i in range(7)) + " |")
    a(f"\nMedia: {f1(g['media_entregas'])} entregas por niño.\n")

    a("## 4. Desagregación\n")
    a("Valores en %. «seg. posible» y «seg. 6 m» usan la regla de seguimiento posible (columnas completas, con n/N, en el JSON).\n")
    a("### Por provincia\n")
    a(tabla_md(res, "por_provincia", "Provincia"))
    a("\n### Por severidad (HIS)\n")
    a(tabla_md(res, "por_severidad", "Severidad"))
    a("\n### Por trimestre de diagnóstico (efecto de la censura)\n")
    a("| Trimestre | N | Control 1 m | Control 3 m | Control 6 m | Recup. |\n|---|---:|---:|---:|---:|---:|")
    for k, v in res["por_trimestre_dx"].items():
        a(f"| {k} | {mil(v['n'])} | {f1(v['control_mes_pct'])} | {f1(v['control_3m_pct'])} | {f1(v['control_6m_pct'])} | {f1(v['recup_pct'])} |")
    a("\nLos dos o tres últimos trimestres tienen valores bajos en control a 6 meses y recuperación porque aún no habían cumplido el plazo: por eso la cifra bruta subestima el desempeño real y se reporta además la variante con seguimiento posible.\n")

    a("## 5. Brecha que ataca el Incremento 2\n")
    a("| Indicador de la Tabla 8 de S1 | Indicador AS-IS de este análisis | Relación con el Inc. 2 |\n|---|---|---|")
    for x in res["brecha_inc2"]:
        a(f"| {x['indicador_S1_tabla8']} | {x['indicador_AS_IS']} | {x['relacion_con_inc2']} |")
    a(f"\nLectura: sobre los diagnosticados con seguimiento posible, el control a los 6 meses consta en {celda(g['control_6m_con_seguimiento_posible'])} y {celda(g['sin_ningun_control_con_seguimiento_posible'])} no tiene ningún control; "
      "esa es la población de niños «vencidos» que el Inc. 2 busca hacer visible (agenda normativa, controles vencidos y alertas).\n")

    a("## 6. Advertencias metodológicas\n")
    for w in res["advertencias"]:
        a(f"- {w}")
    a("\n_" + FUENTE + "._\n")
    MD_OUT.write_text("\n".join(L), encoding="utf-8")


# ----------------------------------------------------------------------------------------------
def graficos(d, res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.edgecolor": "#8a8f98", "axes.labelcolor": "#33373d",
                         "xtick.color": "#4a4f57", "ytick.color": "#4a4f57"})
    AZUL, GRIS, TXT = "#2f5f8f", "#b4bac3", "#222831"
    GRAF.mkdir(parents=True, exist_ok=True)
    g = res["indicadores_globales"]

    def guardar(fig, nombre):
        fig.text(0.01, 0.01, FUENTE, fontsize=7.2, color="#5a6068", ha="left", va="bottom")
        for ext in ("png", "svg"):
            fig.savefig(GRAF / f"{nombre}.{ext}", dpi=150, facecolor="white")
        plt.close(fig)

    # g7 cascada
    etapas = [("Diagnosticados", g["diagnosticados"], g["diagnosticados"], g["diagnosticados"]), ]
    e = [("Control de Hb al mes", "control_mes"), ("Control a los 3 meses", "control_3m"), ("Control a los 6 meses", "control_6m")]
    nombres = ["Diagnosticados"] + [x[0] for x in e] + ["Recuperación documentada"]
    todos = [100.0] + [g[k]["pct"] for _, k in e] + [g["recuperacion_documentada"]["pct"]]
    con = [100.0] + [g[k + "_con_seguimiento_posible"]["pct"] for _, k in e] + [g["recuperacion_con_seguimiento_6m"]["pct"]]
    nt = [g["diagnosticados"]] + [g[k]["n"] for _, k in e] + [g["recuperacion_documentada"]["n"]]
    nc = [None] + [(g[k + "_con_seguimiento_posible"]["n"], g[k + "_con_seguimiento_posible"]["N"]) for _, k in e] + \
         [(g["recuperacion_con_seguimiento_6m"]["n"], g["recuperacion_con_seguimiento_6m"]["N"])]
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    y = np.arange(len(nombres))[::-1]
    h = 0.36
    ax.barh(y + h / 2, todos, h, color=AZUL, label="Sobre todos los diagnosticados", zorder=3)
    ax.barh(y - h / 2, con, h, color=GRIS, label="Solo con seguimiento posible (dx + plazo + 30 d ≤ 30/06/2024)", zorder=3)
    for yi, t, c, n_t, n_c in zip(y, todos, con, nt, nc):
        ax.text(t + 1, yi + h / 2, f"{f1(t)} %  ({mil(n_t)})", va="center", fontsize=8.6, color=TXT)
        if n_c:
            ax.text(c + 1, yi - h / 2, f"{f1(c)} %  ({mil(n_c[0])}/{mil(n_c[1])})", va="center", fontsize=8.6, color=TXT)
    ax.set_yticks(y)
    ax.set_yticklabels(nombres)
    ax.set_xlim(0, 125)
    ax.set_xlabel("% de niños")
    ax.xaxis.grid(True, color="#e3e6ea", zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.4, -0.12), ncol=1, frameon=False, fontsize=8.6)
    ax.set_title("Línea base AS-IS: del diagnóstico a la recuperación documentada (12 486 niños)", fontsize=11, loc="left", color=TXT, pad=12)
    fig.subplots_adjust(left=0.24, right=0.97, top=0.9, bottom=0.25)
    guardar(fig, "g7_asis_cascada_seguimiento")

    # g8 provincias
    pr = res["por_provincia"]
    prov = sorted(pr, key=lambda k: pr[k]["control_6m_con_seguimiento_posible"]["pct"] or 0)
    c6 = [pr[k]["control_6m_con_seguimiento_posible"]["pct"] for k in prov]
    rc = [pr[k]["recuperacion_con_seguimiento_6m"]["pct"] for k in prov]
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 5.2), sharey=True)
    yy = np.arange(len(prov))
    for ax, vals, tit, col, kk in ((axs[0], c6, "Control de Hb a los 6 meses", AZUL, "control_6m_con_seguimiento_posible"),
                                    (axs[1], rc, "Recuperación documentada", "#5b7f5f", "recuperacion_con_seguimiento_6m")):
        ax.barh(yy, vals, 0.6, color=col, zorder=3)
        for yi, v, k in zip(yy, vals, prov):
            ax.text(v + 1, yi, f"{f1(v)} %  (n={mil(pr[k][kk]['N'])})", va="center", fontsize=8.2, color=TXT)
        ax.set_xlim(0, 125)
        ax.set_xticks([0, 20, 40, 60, 80, 100])
        ax.set_title(tit, fontsize=10.5, loc="left", color=TXT)
        ax.set_xlabel("% de niños con seguimiento posible")
        ax.xaxis.grid(True, color="#e3e6ea", zorder=0)
        ax.set_axisbelow(True)
    axs[0].set_yticks(yy)
    axs[0].set_yticklabels([p.title() for p in prov])
    fig.suptitle("Línea base AS-IS por provincia (solo diagnosticados con seguimiento de 6 meses posible)", fontsize=11, x=0.01, ha="left", color=TXT)
    fig.subplots_adjust(left=0.13, right=0.98, top=0.86, bottom=0.14, wspace=0.08)
    guardar(fig, "g8_asis_por_provincia")

    # g9 suplementación
    dist = g["suplementacion_distribucion"]
    xs = list(range(7))
    ps = [dist[str(i)]["pct"] for i in xs]
    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    cols = [GRIS if i < 5 else AZUL for i in xs]
    ax.bar(xs, ps, 0.62, color=cols, zorder=3)
    for i, p_ in zip(xs, ps):
        ax.text(i, p_ + 0.6, f"{f1(p_)} %\n({mil(dist[str(i)]['n'])})", ha="center", fontsize=8.4, color=TXT)
    ax.set_xticks(xs)
    ax.set_xlabel("N.º de entregas de suplemento registradas por niño (fecha_supT1 a T6)")
    ax.set_ylabel("% de diagnosticados")
    ax.set_ylim(0, max(ps) + 8)
    ax.yaxis.grid(True, color="#e3e6ea", zorder=0)
    ax.set_axisbelow(True)
    ax.set_title(f"Suplementación AS-IS: {f1(g['entregas_ge5']['pct'])} % con ≥ 5 entregas y {f1(g['entregas_0']['pct'])} % sin ninguna", fontsize=11, loc="left", color=TXT, pad=10)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.89, bottom=0.2)
    guardar(fig, "g9_asis_suplementacion")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sin-graficos", action="store_true")
    a = ap.parse_args()
    d, res = construir()
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    escribir_md(res)
    if not a.sin_graficos:
        graficos(d, res)
    g = res["indicadores_globales"]
    for k in ("control_mes", "control_3m", "control_6m", "perdida_seguimiento_6m", "recuperacion_documentada", "entregas_ge5", "entregas_0"):
        print(f"{k}: {g[k]['pct']} % ({g[k]['n']}/{g[k]['N']})")


if __name__ == "__main__":
    main()
