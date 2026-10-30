"""Reporte de la importación: cifras del archivo, de lo importado y concordancia entre el HIS y el sistema."""

from datetime import date

from app.domain.model.importacion import ResultadoImportacion
from scripts.importador_diresa import config as cfg

CLASES_SISTEMA = ("SIN_ANEMIA", "LEVE", "MODERADA", "SEVERA", "NO_APLICA")
SEVERIDADES_HIS = ("LEV", "MOD", "SEV")


def _pct(parte: int, total: int) -> float | None:
    return round(100 * parte / total, 1) if total else None


def concordancia(matriz: dict[str, dict[str, int]]) -> dict:
    """Matriz HIS × sistema y porcentajes de acuerdo sobre los diagnósticos con severidad registrada por el HIS.

    * ``porcentaje_acuerdo``: la severidad del sistema (leve, moderada, severa) coincide con la del HIS.
    * ``porcentaje_sistema_sin_anemia``: el HIS diagnosticó anemia pero el sistema, tras ajustar por altitud y aplicar
      los puntos de corte, clasifica SIN_ANEMIA (o NO_APLICA por ser menor de 6 meses).
    * ``porcentaje_acuerdo_entre_anemicos``: acuerdo de severidad solo cuando el sistema también detecta anemia.
    """
    filas = {h: {c: matriz.get(h, {}).get(c, 0) for c in CLASES_SISTEMA} for h in (*SEVERIDADES_HIS, "SIN_DATO")}
    comparables = sum(sum(filas[h].values()) for h in SEVERIDADES_HIS)
    de_acuerdo = sum(filas[h][cfg.SEVERIDAD_HIS_A_CLASIFICACION[h]] for h in SEVERIDADES_HIS)
    sin_anemia = sum(filas[h]["SIN_ANEMIA"] + filas[h]["NO_APLICA"] for h in SEVERIDADES_HIS)
    anemicos = comparables - sin_anemia
    return {
        "matriz_his_vs_sistema": filas,
        "diagnosticos_con_severidad_his": comparables,
        "diagnosticos_sin_severidad_his": sum(filas["SIN_DATO"].values()),
        "de_acuerdo": de_acuerdo,
        "porcentaje_acuerdo": _pct(de_acuerdo, comparables),
        "sistema_sin_anemia": sin_anemia,
        "porcentaje_sistema_sin_anemia": _pct(sin_anemia, comparables),
        "porcentaje_acuerdo_entre_anemicos": _pct(de_acuerdo, anemicos),
        "nota": (
            "La severidad del HIS no coincide con el sistema cuando el HIS usa otra regla de ajuste por altitud o "
            "registra la hemoglobina sin ajustar; la altitud aquí es la de la capital de la provincia (aproximación)."
        ),
    }


def armar_reporte(
    *,
    modo: str,
    semilla: int | None,
    muestra: int | None,
    fecha_referencia: date,
    archivo: str,
    filas_leidas: int,
    descartes_de_fila: dict[str, int],
    problemas_del_archivo: dict[str, int],
    filas_elegibles: int,
    filas_enviadas: int,
    resultado: ResultadoImportacion,
    registros_sistema: int,
    version: str,
) -> dict:
    # En modo muestra las filas inutilizables nunca llegan a sortearse; en modo completo se cuentan como descartes.
    descartes = dict(resultado.descartes)
    if modo == "completo":
        for motivo, n in descartes_de_fila.items():
            descartes[motivo] = descartes.get(motivo, 0) + n
    return {
        "version": version,
        "archivo": archivo,
        "modo": modo,
        "semilla": semilla,
        "muestra_solicitada": muestra,
        "fecha_referencia": fecha_referencia.isoformat(),
        "filas_leidas": filas_leidas,
        "filas_con_evaluacion_utilizable": filas_elegibles,
        "filas_enviadas_a_importar": filas_enviadas,
        "ninos_importados": resultado.ninos_importados,
        "ninos_omitidos": resultado.ninos_omitidos,
        "ninos_con_alta_por_edad": resultado.ninos_con_alta_por_edad,
        "evaluaciones_importadas": {
            "total": sum(resultado.evaluaciones_importadas.values()),
            "por_tipo": dict(sorted(resultado.evaluaciones_importadas.items())),
        },
        "descartes_por_motivo": dict(sorted(descartes.items())),
        "calidad_del_archivo_completo": dict(sorted(problemas_del_archivo.items())),
        "concordancia_his_vs_sistema": concordancia(resultado.matriz_concordancia),
        "distribucion_por_provincia": dict(sorted(resultado.ninos_por_provincia.items())),
        "altitud_por_provincia_m": cfg.ALTITUD_CAPITAL_PROVINCIA,
        "registros_sistema_creados": registros_sistema,
    }
