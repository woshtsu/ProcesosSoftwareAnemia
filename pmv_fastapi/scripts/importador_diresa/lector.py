"""Lectura y limpieza del CSV de la DIRESA Junín: cada fila válida se convierte en un ``RegistroImportado``.

No se altera ninguna fecha ni ninguna hemoglobina del archivo; lo que no se puede leer se trata como ausente y se
cuenta con su motivo. ``num_doc`` (notación científica, deformado y no único) y ``seguro`` se ignoran a propósito: no
sirven como identificador y no se intenta reidentificar a nadie.
"""

import csv
import math
from collections import Counter
from collections.abc import Iterator
from datetime import date, datetime
from pathlib import Path

from app.domain.model.importacion import EvaluacionImportada, RegistroImportado, TipoEvaluacionImportada
from scripts.importador_diresa import config as cfg

DESCARTE_SIN_NACIMIENTO = "fila_sin_fecha_de_nacimiento_valida"
DESCARTE_SIN_PROVINCIA = "fila_con_provincia_sin_altitud"
DESCARTE_SIN_ESTABLECIMIENTO = "fila_sin_establecimiento_o_distrito"


def leer_filas(ruta: Path) -> Iterator[tuple[int, dict[str, str]]]:
    """Filas de datos con su número (1 = primera fila después del encabezado)."""
    with open(ruta, encoding=cfg.CODIFICACION, newline="") as archivo:
        for numero, fila in enumerate(csv.DictReader(archivo, delimiter=cfg.SEPARADOR), start=1):
            yield numero, {k.strip(): (v or "").strip() for k, v in fila.items() if k}


def _fecha(texto: str, problemas: list[str]) -> date | None:
    if texto in ("", cfg.VALOR_NULO):
        return None
    try:
        return datetime.strptime(texto, cfg.FORMATO_FECHA).date()
    except ValueError:
        problemas.append("fecha_ilegible")
        return None


def _hemoglobina(texto: str, problemas: list[str]) -> float | None:
    if texto in ("", cfg.VALOR_NULO):
        return None
    try:
        valor = float(texto.replace(",", "."))
    except ValueError:
        valor = math.nan
    if not math.isfinite(valor):
        problemas.append("hemoglobina_ilegible")
        return None
    return valor


def codigo_de(numero: int) -> str:
    return f"{cfg.PREFIJO_CODIGO}{numero:05d}"


def severidad_his(fila: dict[str, str]) -> str | None:
    valor = fila.get("valor_lab_dx", cfg.VALOR_NULO)
    return valor if valor in cfg.SEVERIDAD_HIS_A_CLASIFICACION else None


def _evaluaciones(fila: dict[str, str], problemas: list[str]) -> list[EvaluacionImportada]:
    evaluaciones = []
    # Diagnóstico: fecha del dosaje del diagnóstico o, si falta, la fecha del diagnóstico.
    fecha_dx = _fecha(fila["fecha_dosaje_dx"], problemas) or _fecha(fila["fecha_dx"], problemas)
    hb_dx = _hemoglobina(fila["hb_dx"], problemas)
    if fecha_dx and hb_dx is not None:
        evaluaciones.append(
            EvaluacionImportada(TipoEvaluacionImportada.DIAGNOSTICO, fecha_dx, hb_dx, severidad_his(fila))
        )
    else:
        problemas.append("diagnostico_sin_hemoglobina" if hb_dx is None else "diagnostico_sin_fecha")
    for tipo, col_fecha, col_hb, etiqueta in cfg.CONTROLES:
        fecha_control = _fecha(fila[col_fecha], problemas)
        hb = _hemoglobina(fila[col_hb], problemas)
        if fecha_control and hb is not None:
            evaluaciones.append(EvaluacionImportada(tipo, fecha_control, hb))
        elif fecha_control or hb is not None:  # un dato sin el otro: no se inventa el que falta
            problemas.append(f"{etiqueta}_sin_hemoglobina" if hb is None else f"{etiqueta}_sin_fecha")
    return evaluaciones


def fila_a_registro(numero: int, fila: dict[str, str]) -> tuple[RegistroImportado | None, list[str]]:
    """Registro del dominio de una fila, o ``None`` si la fila no se puede usar; más los motivos de descarte."""
    problemas: list[str] = []
    nacimiento = _fecha(fila["fecha_nac"], problemas)
    if nacimiento is None:
        return None, [*problemas, DESCARTE_SIN_NACIMIENTO]
    provincia = fila["Provincia"].upper()
    if provincia not in cfg.ALTITUD_CAPITAL_PROVINCIA:
        return None, [*problemas, DESCARTE_SIN_PROVINCIA]
    if not fila["Nombre_Establecimiento"] or not fila["Distrito"]:
        return None, [*problemas, DESCARTE_SIN_ESTABLECIMIENTO]
    registro = RegistroImportado(
        codigo_origen=codigo_de(numero),
        fecha_nacimiento=nacimiento,
        establecimiento=fila["Nombre_Establecimiento"],
        distrito=fila["Distrito"],
        comunidad=fila["Distrito"],  # comunidad = distrito (decisión del equipo)
        altitud_m=float(cfg.ALTITUD_CAPITAL_PROVINCIA[provincia]),
        red=fila["Red"] or None,
        microred=fila["MicroRed"] or None,
        provincia=provincia,
        evaluaciones=tuple(_evaluaciones(fila, problemas)),
    )
    return registro, problemas


def leer_registros(ruta: Path) -> tuple[list[RegistroImportado], Counter[str], int]:
    """Todos los registros utilizables del CSV, los motivos de descarte de lectura y el total de filas leídas.

    Los motivos de las filas que sí se importan viajan dentro de cada registro (``descartes_lectura``) y los cuenta el
    caso de uso; aquí solo se cuentan los de las filas que no se pudieron convertir en registro.
    """
    registros: list[RegistroImportado] = []
    descartes_de_fila: Counter[str] = Counter()
    filas = 0
    for numero, fila in leer_filas(ruta):
        filas += 1
        registro, problemas = fila_a_registro(numero, fila)
        if registro is None:
            descartes_de_fila.update(problemas)
            continue
        registros.append(_con_descartes(registro, problemas))
    return registros, descartes_de_fila, filas


def _con_descartes(registro: RegistroImportado, problemas: list[str]) -> RegistroImportado:
    return RegistroImportado(**{**registro.__dict__, "descartes_lectura": tuple(problemas)})
