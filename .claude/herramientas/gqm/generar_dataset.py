#!/usr/bin/env python
"""Generador de conjuntos sintéticos etiquetables (100 % ficticios, semilla fija) para V2, V3, V4 y V6.

Cada niño trae sus datos y su historial de evaluaciones con FECHAS ABSOLUTAS calculadas respecto de ``hoy`` (Perú).
Mezcla (a) niños aleatorios con historiales de distinto tipo (cumplidores, con omisiones, con anemia y seguimiento,
con abandono, recién nacidos, cercanos a los 60 meses, con alta) y (b) casos de FRONTERA diseñados: fecha límite
igual a hoy, límite = hoy - 1, ventana -16/-15/+30/+31 días, fin de mes (29-31), recuperación antes y después del
vencimiento. NO usa la aplicación ni el oráculo: solo produce datos; las etiquetas las calcula oraculo_agenda.py.

Uso:  python generar_dataset.py --n 150 --semilla 20261016 --salida datos/dataset_B150.json [--sin-fronteras]
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

import oraculo_agenda as o  # solo para sumar_meses/edad/clasificar (el oráculo no depende de la app)

NOMBRES = ["Luz Mery", "Jhon", "Yeny", "Brayan", "Mayra", "Ángel", "Nayeli", "Dilan", "Kiara", "Yuri", "Thiago",
           "Camila", "Milagros", "Anthony", "Fabiola", "Joel", "Rosa", "Erick", "Alexa", "Ñusta", "Wilmer", "Sayuri"]
APELLIDOS = ["Quispe", "Huamán", "Condori", "Ccanto", "Taipe", "Rivera", "Pomalaza", "Suárez", "Inga", "Lazo",
             "Poma", "Ccente", "Orihuela", "Samaniego", "Chuquillanqui", "Cerrón", "Baquerizo", "Meza", "Pari",
             "Rojas", "Ñahui", "Yauri", "Ayala", "Mayta"]
COMUNIDADES = ["Palmayoc", "Chongos Alto", "Llacuas", "Huaycha", "Yanacancha", "Ñahuimpuquio", "Ahuac", "Chicche"]
ALTITUDES = [0, 1500, 2800, 3200, 3550, 3720, 3890, 3950, 4300]
HB_AJUSTADA = {"SIN_ANEMIA": (11.2, 13.4), "LEVE": (9.6, 10.4), "MODERADA": (7.2, 9.4), "SEVERA": (5.0, 6.8)}


def pesos_talla(meses: int) -> tuple[float, float]:
    return round(min(3.4 + 0.22 * meses, 24.0), 1), round(min(50.0 + 1.1 * meses, 118.0), 1)


class Gen:
    def __init__(self, hoy: date, semilla: int, prefijo_dni: str):
        self.hoy = hoy
        self.r = random.Random(semilla)
        self.prefijo = prefijo_dni
        self.ninos: list[dict] = []

    # --- piezas ---------------------------------------------------------------------------------------------
    def evaluacion(self, nac: date, alt: float, fecha: date, clase: str | None = None) -> dict:
        meses = o.edad_meses(nac, fecha)
        if clase is None:
            clase = self.r.choices(["SIN_ANEMIA", "LEVE", "MODERADA", "SEVERA"], [58, 22, 15, 5])[0]
        lo, hi = HB_AJUSTADA[clase]
        if clase == "LEVE" and meses >= 24:
            lo, hi = 10.0, 10.9  # el rango leve depende de la edad (24-59: 10,0-10,9)
        if clase == "SIN_ANEMIA":
            lo, hi = (10.6, 13.4) if meses < 24 else (11.1, 13.4)
        hb_ajustada = round(self.r.uniform(lo, hi), 1)
        hb_obs = round(hb_ajustada + o.ajuste_altitud(alt), 1)
        peso, talla = pesos_talla(max(meses, 0))
        return {"fecha": fecha.isoformat(), "hb_obs": hb_obs, "peso_kg": peso, "talla_cm": talla}

    def agregar(self, escenario: str, nac: date, evals_fechas: list[tuple[date, str | None]], alta=False, alt=None,
                comunidad=None):
        r = self.r
        idx = len(self.ninos) + 1
        alt = r.choice(ALTITUDES[1:]) if alt is None else alt
        evals = []
        usados = set()
        for f, clase in sorted(evals_fechas, key=lambda x: x[0]):
            if f in usados or f < nac or f > self.hoy:
                continue
            usados.add(f)
            evals.append(self.evaluacion(nac, alt, f, clase))
        if not evals:
            return
        com = comunidad or r.choice(COMUNIDADES)
        self.ninos.append(
            {
                "dni": f"{self.prefijo}{idx:07d}",
                "nombres": r.choice(NOMBRES),
                "apellidos": f"{r.choice(APELLIDOS)} {r.choice(APELLIDOS)}",
                "sexo": r.choice(["F", "M"]),
                "nacimiento": nac.isoformat(),
                "comunidad": com,
                "distrito": "Chongos Alto",
                "establecimiento": "P. S. Chongos Alto",
                "altitud": alt,
                "tutor": f"{r.choice(NOMBRES)} {r.choice(APELLIDOS)}",
                "celular": r.choice([None, f"9{r.randint(10000000, 99999999)}"]),
                "estado": "ALTA" if alta else "ACTIVO",
                "escenario": escenario,
                "evaluaciones": evals,
            }
        )

    # --- niños aleatorios -------------------------------------------------------------------------------------
    def aleatorio(self):
        r, hoy = self.r, self.hoy
        edad_hoy = r.choice([r.randint(0, 5)] * 2 + [r.randint(6, 59) for _ in range(10)])
        nac = hoy - timedelta(days=int(edad_hoy * 30.4375 + r.randint(0, 29)))
        if o.edad_meses(nac, hoy) > 59:
            nac = hoy - timedelta(days=int(59 * 30.4375))
        tipo = r.choices(["cumplidor", "omisiones", "anemia", "abandono", "tardio", "unico_reciente", "alta"],
                         [22, 22, 20, 12, 10, 8, 6])[0]
        alta = tipo == "alta"
        base = tipo if not alta else "omisiones"
        fechas: list[tuple[date, str | None]] = []
        primera = nac + timedelta(days=r.randint(0, max(1, min(200, (hoy - nac).days))))
        if base in ("tardio", "unico_reciente"):
            primera = hoy - timedelta(days=r.randint(0, 60 if base == "unico_reciente" else 400))
            primera = max(primera, nac)
            fechas.append((primera, None))
            if base == "tardio" and r.random() < 0.5:
                fechas.append((min(hoy, primera + timedelta(days=r.randint(25, 200))), None))
        else:
            fecha = primera
            prob_visita = {"cumplidor": 0.95, "omisiones": 0.65, "anemia": 0.8, "abandono": 0.9}[base]
            corte = hoy - timedelta(days=r.randint(45, 300)) if base == "abandono" else hoy
            clase_prev = None
            while fecha <= corte:
                clase = None
                if base == "anemia":
                    if clase_prev in (None, "SIN_ANEMIA") and r.random() < 0.3:
                        clase = r.choice(["LEVE", "MODERADA", "SEVERA"])
                    elif clase_prev in ("LEVE", "MODERADA", "SEVERA"):
                        clase = r.choice(["SIN_ANEMIA", "LEVE", "LEVE", "MODERADA"])
                    else:
                        clase = "SIN_ANEMIA"
                fechas.append((fecha, clase))
                clase_prev = clase
                # siguiente visita: el próximo hito normativo cercano (+jitter) o una brecha aleatoria
                if r.random() < prob_visita:
                    fecha = fecha + timedelta(days=r.choice([r.randint(28, 45), r.randint(60, 100), r.randint(85, 130)]))
                else:
                    fecha = fecha + timedelta(days=r.randint(70, 260))
        self.agregar(tipo, nac, fechas, alta=alta)

    # --- casos de frontera diseñados ----------------------------------------------------------------------------
    def nac_para(self, prog: date, n: int) -> date | None:
        for dia in (prog.day, 28, 27, 26):
            try:
                base = date(prog.year, prog.month, min(dia, 28 if dia > 28 else dia))
            except ValueError:
                continue
            total = base.year * 12 + base.month - 1 - n
            cand = date(total // 12, total % 12 + 1, min(dia, 28) if dia <= 28 else dia)
            if o.sumar_meses(cand, n) == prog:
                return cand
        return None

    def frontera_tamizaje(self):
        hoy = self.hoy
        for n in (6, 12, 24, 36):
            for limite_offset, nombre in ((0, "limite_hoy"), (-1, "limite_ayer"), (-2, "limite_anteayer")):
                prog = hoy - timedelta(days=30) + timedelta(days=limite_offset)  # límite = prog + 30 = hoy + offset
                nac = self.nac_para(prog, n)
                if not nac or o.edad_meses(nac, hoy) > 59:
                    continue
                primera = prog - timedelta(days=40)
                self.agregar(f"frontera_{nombre}_N{n}", nac, [(max(primera, nac), "SIN_ANEMIA")])
        for n in (9, 18, 30):
            for delta in (-16, -15, 29, 30, 31):
                prog = hoy - timedelta(days=50)
                nac = self.nac_para(prog, n)
                if not nac:
                    continue
                self.agregar(f"frontera_ventana_N{n}_d{delta:+d}", nac,
                             [(max(prog - timedelta(days=45), nac), "SIN_ANEMIA"), (prog + timedelta(days=delta), "SIN_ANEMIA")])

    def frontera_fin_de_mes(self):
        hoy = self.hoy
        for dia in (29, 30, 31):
            for n in (6, 12, 24):
                # nacimiento un día 29/30/31 de un mes con ese día, con programada aproximadamente 40-70 días atrás
                intento = hoy - timedelta(days=n * 30 + 45)
                for retro in range(0, 60):
                    f = intento - timedelta(days=retro)
                    try:
                        nac = date(f.year, f.month, dia)
                    except ValueError:
                        continue
                    prog = o.sumar_meses(nac, n)
                    if 20 <= (hoy - prog).days <= 90 and o.edad_meses(nac, hoy) <= 59:
                        self.agregar(f"fin_de_mes_{dia}_N{n}", nac, [(max(prog - timedelta(days=60), nac), "SIN_ANEMIA")])
                        break

    def frontera_tratamiento(self):
        hoy = self.hoy
        edad = 20  # meses
        nac = hoy - timedelta(days=int(edad * 30.4375) + 40)
        for desfase, nombre in ((0, "c1m_limite_hoy"), (-1, "c1m_vence_ayer"), (-20, "c1m_vencido_hace_20")):
            # diagnóstico tal que C1M.prog + 30 = hoy + desfase
            diag = o.sumar_meses(hoy - timedelta(days=30) + timedelta(days=desfase), -1)
            if diag < nac or o.sumar_meses(diag, 1) != hoy - timedelta(days=30) + timedelta(days=desfase):
                diag = diag + timedelta(days=1)
            self.agregar(f"trat_{nombre}", nac, [(diag, "MODERADA")])
        # recuperación ANTES del vencimiento del C1M (queda CERRADO) y DESPUÉS (sigue VENCIDO)
        base = hoy - timedelta(days=100)
        for k, rec_dias in enumerate((20, 50, 75)):
            self.agregar(f"trat_recupera_dia{rec_dias}", nac, [(base, "LEVE"), (base + timedelta(days=rec_dias), "SIN_ANEMIA")])
        # anemia sostenida sin reiniciar calendario; episodio nuevo tras recuperar
        self.agregar("trat_sostenida", nac, [(base, "LEVE"), (base + timedelta(days=33), "MODERADA"), (base + timedelta(days=62), "LEVE")])
        self.agregar("trat_nuevo_episodio", nac, [(base - timedelta(days=60), "LEVE"), (base - timedelta(days=30), "SIN_ANEMIA"), (base, "MODERADA")])
        self.agregar("trat_cumplido_c1m_en_borde", nac, [(base, "LEVE"), (o.sumar_meses(base, 1) + timedelta(days=30), "LEVE")])
        self.agregar("trat_cumplido_c1m_fuera_borde", nac, [(base, "LEVE"), (o.sumar_meses(base, 1) + timedelta(days=31), "LEVE")])

    def frontera_edades(self):
        hoy = self.hoy
        # recién nacidos y menores de 6 meses
        for dias in (0, 15, 100, 170):
            nac = hoy - timedelta(days=dias)
            self.agregar(f"recien_nacido_{dias}d", nac, [(nac, "SIN_ANEMIA")])
        # cerca de los 60 meses
        for meses_extra in (0, 15, 28):
            nac = o.sumar_meses(hoy, -59) - timedelta(days=meses_extra)
            if o.edad_meses(nac, hoy) <= 59:
                self.agregar(f"cerca_60m_{meses_extra}", nac, [(hoy - timedelta(days=200 + meses_extra), "SIN_ANEMIA"),
                                                              (hoy - timedelta(days=60 + meses_extra), "SIN_ANEMIA")])
        nac = o.sumar_meses(hoy, -58) - timedelta(days=5)
        self.agregar("cerca_60m_tratamiento", nac, [(hoy - timedelta(days=120), "MODERADA")])
        # alta con controles vencidos
        nac = hoy - timedelta(days=500)
        self.agregar("alta_con_vencidos", nac, [(hoy - timedelta(days=400), "SIN_ANEMIA")], alta=True)


def generar(n: int, semilla: int, hoy: date, prefijo: str, fronteras: bool = True) -> dict:
    g = Gen(hoy, semilla, prefijo)
    if fronteras:
        g.frontera_tamizaje()
        g.frontera_fin_de_mes()
        g.frontera_tratamiento()
        g.frontera_edades()
    fijos = len(g.ninos)
    while len(g.ninos) < n:
        g.aleatorio()
    g.ninos = g.ninos[:n] if len(g.ninos) > n else g.ninos
    return {"hoy": hoy.isoformat(), "semilla": semilla, "n": len(g.ninos), "n_fronteras": fijos, "ninos": g.ninos}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--semilla", type=int, default=20261016)
    ap.add_argument("--hoy", default=None)
    ap.add_argument("--prefijo-dni", default="6")
    ap.add_argument("--sin-fronteras", action="store_true")
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    hoy = date.fromisoformat(a.hoy) if a.hoy else o.hoy_peru()
    ds = generar(a.n, a.semilla, hoy, a.prefijo_dni, not a.sin_fronteras)
    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.salida).write_text(json.dumps(ds, ensure_ascii=False, indent=1), encoding="utf-8")
    escenarios: dict[str, int] = {}
    for x in ds["ninos"]:
        escenarios[x["escenario"].split("_N")[0]] = escenarios.get(x["escenario"].split("_N")[0], 0) + 1
    print(f"{ds['n']} niños (fronteras diseñadas: {ds['n_fronteras']}), hoy={hoy}, semilla={a.semilla} -> {a.salida}")
    print(escenarios)


if __name__ == "__main__":
    main()
