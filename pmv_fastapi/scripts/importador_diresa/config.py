"""Configuración del importador del dataset de la DIRESA Junín.

Todo lo que es propio de esta fuente de datos vive aquí y no en el dominio: el nombre del archivo, su formato, las
columnas y la tabla de altitudes por provincia.

Altitud por provincia
---------------------
El dataset no trae la altitud de la residencia ni del establecimiento. Se asigna a cada niño la altitud de la CAPITAL
de su provincia, tomada de:

    INEI, «Perú: Compendio Estadístico 2014», cuadro 1.12 «Superficie, población, densidad poblacional y altitud de la
    capital, según departamento y provincia, 2013», pp. 32-33.
    https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1173/cap01/cap01.pdf

Es una APROXIMACIÓN: la altitud real del establecimiento o de la vivienda puede diferir en cientos de metros dentro de
una misma provincia (p. ej. Chanchamayo o Satipo tienen zonas de selva alta y de selva baja). Como la hemoglobina se
ajusta por altitud (OMS 2024), esta aproximación afecta la clasificación calculada por el sistema.
"""

from datetime import date
from pathlib import Path

from app.domain.model.importacion import TipoEvaluacionImportada

# Fecha de corte del dataset: última fecha de diagnóstico registrada es 21/06/2024; se usa 30/06/2024 como «hoy».
FECHA_CORTE = date(2024, 6, 30)

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
CSV_POR_DEFECTO = (
    RAIZ_PROYECTO / "datos" / "Niños_menores_de_36_meses_con_dx_de_anemia_en_la_Región_ Junín.csv"
)
CODIFICACION = "latin-1"
SEPARADOR = ";"
VALOR_NULO = "NULL"
FORMATO_FECHA = "%d/%m/%Y"
PREFIJO_CODIGO = "DJ-"  # DJ-00001 = fila 1 de datos del CSV (sin contar el encabezado)

# Provincia (como figura en el CSV) -> altitud (m s. n. m.) de su capital.
ALTITUD_CAPITAL_PROVINCIA = {
    "HUANCAYO": 3245,  # Huancayo
    "CONCEPCION": 3286,  # Concepción
    "CHANCHAMAYO": 775,  # La Merced
    "JAUJA": 3389,  # Jauja
    "JUNIN": 4113,  # Junín
    "SATIPO": 628,  # Satipo
    "TARMA": 3059,  # Tarma
    "YAULI": 3725,  # La Oroya
    "CHUPACA": 3281,  # Chupaca
}

# Severidad que registra el HIS (valor_lab_dx) -> clasificación equivalente del sistema.
SEVERIDAD_HIS_A_CLASIFICACION = {"LEV": "LEVE", "MOD": "MODERADA", "SEV": "SEVERA"}

# Evaluaciones de control: (tipo, columna de fecha, columna de hemoglobina, etiqueta para los descartes).
CONTROLES = (
    (TipoEvaluacionImportada.CONTROL_1_MES, "fecha_dosaje_mes", "hb", "control_1_mes"),
    (TipoEvaluacionImportada.CONTROL_3_MESES, "fecha_dosaje_3_meses", "hb_tresmeses", "control_3_meses"),
    (TipoEvaluacionImportada.CONTROL_6_MESES, "fecha_dosaje_6_meses", "hb_seismeses", "control_6_meses"),
)
