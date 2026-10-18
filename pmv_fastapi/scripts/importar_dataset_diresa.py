"""Importa el dataset de niños menores de 36 meses con diagnóstico de anemia de la DIRESA Junín (HIS) a la base.

Cada fila del CSV pasa a ser un niño de origen DATASET_DIRESA_JUNIN con un código seudónimo estable (DJ-00001 = fila 1
de datos), SIN DNI, nombres, celular ni tutor, y con sus evaluaciones: el diagnóstico (hb_dx) y los controles al mes,
a los 3 y a los 6 meses que tengan fecha y hemoglobina. Peso y talla no vienen en el dataset y no se inventan. La
altitud es la de la capital de la provincia (INEI, ver scripts/importador_diresa/config.py). Las evaluaciones con edad
de 60 meses o más o fuera de los rangos del dominio se descartan y se cuentan. No se altera ninguna fecha.

Uso (la base se toma de DATABASE_URL; sin ella, SQLite en ./datos/anemia.db):
    python -m scripts.importar_dataset_diresa --muestra 500 --semilla 2026 --reiniciar
    python -m scripts.importar_dataset_diresa --completo --reiniciar --reporte docs/evidencias/inc2/importacion_completa.json

Demo con dataset (luego se arranca la API con FECHA_REFERENCIA=2024-06-30):
    DATABASE_URL=sqlite:///./datos/demo_dataset.db python -m scripts.importar_dataset_diresa --muestra 500 --reiniciar \\
        --con-registros-sistema 5
"""

import argparse
import json
import os
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from app.adapters.outbound.persistence.sqlalchemy_repo import RepositorioSQLAlchemy
from app.adapters.outbound.reloj_fijo import RelojFijo
from app.application.servicio_expediente import ServicioExpediente
from app.application.servicio_importacion import ServicioImportacion
from app.domain.model.errores import RegistroDuplicado
from app.domain.service.agenda import agregar_meses
from app.domain.service.reglas_clinicas import ajuste_por_altitud
from app.main import VERSION
from scripts.cargar_datos_prueba import HB_AJUSTADA, antropometria
from scripts.importador_diresa import config as cfg
from scripts.importador_diresa.lector import leer_registros
from scripts.importador_diresa.muestreo import muestra_estratificada
from scripts.importador_diresa.reporte import armar_reporte

USUARIO_REGISTROS_SISTEMA = "demo.registros-sistema"
SEMILLA_POR_DEFECTO = 2026
MUESTRA_POR_DEFECTO = 500


def crear_registros_sistema(servicio: ServicioExpediente, cantidad: int, hoy: date) -> int:
    """Niños registrados «desde el sistema» (origen SISTEMA, todos los campos), rotulados como de prueba.

    Sirven en la demo para mostrar la diferencia con los registros del dataset. Son ficticios; se omiten los que ya
    existen (mismo DNI).
    """
    creados = 0
    patron = [(8, "SIN_ANEMIA"), (14, "LEVE"), (20, "MODERADA"), (26, "SIN_ANEMIA"), (11, "LEVE"), (17, "SIN_ANEMIA")]
    for i in range(1, cantidad + 1):
        meses, clasificacion = patron[(i - 1) % len(patron)]
        nacimiento = agregar_meses(hoy, -meses)
        fecha_control = hoy - timedelta(days=7 + 3 * i)
        peso, talla = antropometria(meses)
        datos = dict(
            dni=f"7900{i:04d}",
            nombres="PRUEBA DEL SISTEMA",
            apellidos=f"Registro {i:02d}",
            sexo="F" if i % 2 else "M",
            fecha_nacimiento=nacimiento,
            establecimiento="ESTABLECIMIENTO DE PRUEBA (SISTEMA)",
            distrito="HUANCAYO",
            comunidad="HUANCAYO",
            altitud_m=cfg.ALTITUD_CAPITAL_PROVINCIA["HUANCAYO"],
            tutor_nombre="Tutor de prueba (sistema)",
            tutor_celular=f"9000000{i:02d}",
        )
        hb = round(HB_AJUSTADA[clasificacion] + ajuste_por_altitud(datos["altitud_m"]), 1)
        evaluacion = dict(fecha=max(fecha_control, nacimiento), hemoglobina_observada=hb, peso_kg=peso, talla_cm=talla)
        try:
            servicio.registrar_nino(datos, evaluacion, USUARIO_REGISTROS_SISTEMA)
        except RegistroDuplicado:
            continue
        creados += 1
    return creados


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--csv", type=Path, default=cfg.CSV_POR_DEFECTO, help="ruta del CSV (latin-1, separador «;»)")
    modo = ap.add_mutually_exclusive_group()
    modo.add_argument(
        "--muestra", type=int, metavar="N", help=f"muestra estratificada de N niños (por defecto {MUESTRA_POR_DEFECTO})"
    )
    modo.add_argument("--completo", action="store_true", help="importa todas las filas utilizables del CSV")
    ap.add_argument("--semilla", type=int, default=SEMILLA_POR_DEFECTO, help="semilla del muestreo (reproducible)")
    ap.add_argument("--reiniciar", action="store_true", help="borra antes los niños ya importados del dataset")
    ap.add_argument("--reporte", type=Path, help="escribe el reporte de la importación en este archivo JSON")
    ap.add_argument("--fecha-referencia", help="AAAA-MM-DD; por defecto FECHA_REFERENCIA o el corte 2024-06-30")
    ap.add_argument(
        "--con-registros-sistema",
        type=int,
        default=0,
        metavar="N",
        help="agrega N registros completos de prueba (origen SISTEMA)",
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _argumentos(argv)
    texto_fecha = args.fecha_referencia or os.getenv("FECHA_REFERENCIA") or cfg.FECHA_CORTE.isoformat()
    reloj = RelojFijo.desde_texto(texto_fecha)
    repo = RepositorioSQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///./datos/anemia.db"))
    repo.crear_esquema()
    importacion = ServicioImportacion(repo, reloj)
    if args.reiniciar:
        print(f"Niños del dataset eliminados antes de importar: {importacion.eliminar_importados()}.")
    elif importacion.contar_importados():
        print("La base ya tiene niños importados del dataset: use --reiniciar para volver a importar.", file=sys.stderr)
        repo.engine.dispose()
        return 2

    registros, descartes_de_fila, filas_leidas = leer_registros(args.csv)
    problemas_archivo = Counter(descartes_de_fila)
    for r in registros:
        problemas_archivo.update(r.descartes_lectura)
    elegibles = [r for r in registros if r.evaluaciones]
    completo = args.completo
    n_muestra = None if completo else (args.muestra or MUESTRA_POR_DEFECTO)
    a_importar = registros if completo else muestra_estratificada(elegibles, n_muestra, args.semilla)

    resultado = importacion.importar(a_importar)
    creados_sistema = 0
    if args.con_registros_sistema:
        creados_sistema = crear_registros_sistema(
            ServicioExpediente(repo, reloj), args.con_registros_sistema, reloj.hoy()
        )

    reporte = armar_reporte(
        modo="completo" if completo else "muestra",
        semilla=None if completo else args.semilla,
        muestra=n_muestra,
        fecha_referencia=reloj.hoy(),
        archivo=args.csv.name,
        filas_leidas=filas_leidas,
        descartes_de_fila=dict(descartes_de_fila),
        problemas_del_archivo=dict(problemas_archivo),
        filas_elegibles=len(elegibles),
        filas_enviadas=len(a_importar),
        resultado=resultado,
        registros_sistema=creados_sistema,
        version=VERSION,
    )
    if args.reporte:
        args.reporte.parent.mkdir(parents=True, exist_ok=True)
        args.reporte.write_text(json.dumps(reporte, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    c = reporte["concordancia_his_vs_sistema"]
    print(f"Filas leídas: {filas_leidas} · con evaluación utilizable: {len(elegibles)} · enviadas: {len(a_importar)}")
    print(f"Niños importados: {resultado.ninos_importados} (con alta por edad: {resultado.ninos_con_alta_por_edad})")
    print(f"Evaluaciones importadas: {reporte['evaluaciones_importadas']['por_tipo']}")
    print(
        f"Concordancia de severidad HIS vs sistema: {c['porcentaje_acuerdo']} % de {c['diagnosticos_con_severidad_his']}"
    )
    if creados_sistema:
        print(f"Registros de prueba del sistema creados: {creados_sistema}.")
    if args.reporte:
        print(f"Reporte escrito en {args.reporte}")
    repo.engine.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
