"""Carga datos SINTÉTICOS de prueba (nombres y DNI ficticios) para el entorno de staging/demo.

Uso:
    python -m scripts.cargar_datos_prueba                # usa DATABASE_URL o SQLite local
    python -m scripts.cargar_datos_prueba --reiniciar    # borra antes los niños sintéticos ya cargados

El conjunto es determinista y se define respecto de la fecha de hoy (Perú): al cargarlo cualquier día produce los
mismos escenarios de agenda (controles cumplidos, pendientes, próximos a vencer y vencidos, de edad y de tratamiento).
Los 14 niños del Incremento 1 (71000001 a 71000014) se conservan; los 71000015 en adelante cubren la agenda del
Incremento 2.
"""

import argparse
import os
from dataclasses import dataclass, field
from datetime import date, timedelta

from app.adapters.outbound.persistence.sqlalchemy_repo import NinoORM, RepositorioSQLAlchemy
from app.adapters.outbound.reloj_sistema import RelojSistema
from app.application.servicio_expediente import ServicioExpediente
from app.domain.model.errores import RegistroDuplicado
from app.domain.service.agenda import agregar_meses
from app.domain.service.reglas_clinicas import ajuste_por_altitud

USUARIO_CARGA = "carga.datos.prueba"
ESTABLECIMIENTO = "P. S. Chongos Alto"

# Hemoglobina ajustada objetivo por clasificación (válida para 6 a 59 meses).
HB_AJUSTADA = {"SIN_ANEMIA": 12.0, "LEVE": 10.2, "MODERADA": 8.5, "SEVERA": 6.0}


@dataclass
class Caso:
    dni: str
    nombres: str
    apellidos: str
    sexo: str
    nacimiento: date
    comunidad: str
    altitud: float
    tutor: str
    celular: str | None
    controles: list[tuple[date, float, float, float]]  # fecha, Hb observada, peso (kg), talla (cm)
    alta: bool = False
    escenario: str = ""
    extra: dict = field(default_factory=dict)


# Incremento 1: dni, nombres, apellidos, sexo, meses de edad, comunidad, altitud, tutor, celular,
# controles [(días atrás, Hb observada, peso, talla)]
NINOS_INC1 = [
    ("71000001", "Luz Mery", "Quispe Rojas", "F", 8, "Chongos Alto", 3550, "Rosa Rojas Pérez", "987654321", [(62, 11.6, 7.6, 67.0), (20, 11.9, 8.0, 68.5)]),
    ("71000002", "Jhon Kevin", "Huamán Poma", "M", 14, "Palmayoc", 3720, "Elsa Poma Ccente", "912345678", [(75, 11.4, 9.1, 74.0), (34, 11.8, 9.4, 75.5)]),
    ("71000003", "Yeny", "Condori Huaylla", "F", 10, "Chongos Alto", 3550, "Marta Huaylla Vila", None, [(48, 10.9, 8.2, 70.0), (10, 11.2, 8.6, 71.8)]),
    ("71000004", "Brayan", "Ccanto Samaniego", "M", 30, "Llacuas", 3890, "Nelly Samaniego Arzapalo", "956789012", [(66, 12.8, 12.6, 88.0), (40, 13.1, 12.9, 89.0)]),
    ("71000005", "Mayra", "Taipe Orihuela", "F", 18, "Palmayoc", 3720, "Gladys Orihuela Ramos", "923456789", [(55, 12.4, 10.1, 79.0)]),
    ("71000006", "Luis Ángel", "Rivera Chuquillanqui", "M", 7, "Chongos Alto", 3550, "Karina Chuquillanqui Solís", "934567890", [(15, 12.9, 7.9, 68.0)]),
    ("71000007", "Nayeli", "Pomalaza Cerrón", "F", 40, "Llacuas", 3890, "Ruth Cerrón Baquerizo", None, [(70, 12.9, 13.8, 95.0), (28, 13.4, 14.1, 96.0)]),
    ("71000008", "Dilan", "Suárez Meza", "M", 22, "Huaycha", 3950, "Olga Meza Inga", "945678901", [(80, 13.7, 11.0, 83.0), (45, 13.9, 11.3, 84.0)]),
    ("71000009", "Kiara", "Inga Lazo", "F", 12, "Huaycha", 3950, "Doris Lazo Pari", "956780123", [(38, 12.2, 8.9, 73.0)]),
    ("71000010", "Fabián", "Lazo Ccanto", "M", 50, "Chongos Alto", 3550, "Irma Ccanto Huari", "967890123", [(58, 13.3, 15.6, 101.0)]),
    ("71000011", "Sheyla", "Huari Pari", "F", 9, "Llacuas", 3890, "Lidia Pari Poma", "978901234", [(25, 13.0, 8.0, 69.0)]),
    ("71000012", "Thiago", "Arzapalo Vila", "M", 16, "Palmayoc", 3720, "Yolanda Vila Taipe", None, [(42, 13.3, 9.9, 77.0), (5, 13.6, 10.2, 78.2)]),
    ("71000013", "Ariana", "Solís Rojas", "F", 26, "Huaycha", 3950, "Sonia Rojas Cerrón", "989012345", [(33, 13.6, 11.7, 86.0)]),
    ("71000014", "Josué", "Pari Condori", "M", 11, "Chongos Alto", 3550, "Maribel Condori Taipe", "990123456", [(18, 10.4, 8.3, 72.0)]),
]  # fmt: skip


def antropometria(meses: int) -> tuple[float, float]:
    """Peso y talla plausibles para una edad en meses (datos sintéticos)."""
    peso = 3.5 + 0.55 * min(meses, 12) + 0.22 * max(meses - 12, 0)
    talla = 50 + 1.9 * min(meses, 12) + 0.75 * max(meses - 12, 0)
    return round(peso, 1), round(talla, 1)


def _control(fecha: date, nacimiento: date, clasificacion: str, altitud: float) -> tuple[date, float, float, float]:
    meses = (fecha.year - nacimiento.year) * 12 + fecha.month - nacimiento.month - (fecha.day < nacimiento.day)
    peso, talla = antropometria(meses)
    hb = round(HB_AJUSTADA[clasificacion] + ajuste_por_altitud(altitud), 1)
    return fecha, hb, peso, talla


def _nacer_con_hito(hoy: date, meses: int, dias_hito: int) -> date:
    """Fecha de nacimiento tal que el control programado a ``meses`` de edad cae ``dias_hito`` días respecto de hoy."""
    return agregar_meses(hoy + timedelta(days=dias_hito), -meses)


def construir_casos(hoy: date) -> list[Caso]:
    """Conjunto sintético completo, calculado respecto de ``hoy`` (determinista)."""
    casos: list[Caso] = []
    for dni, nom, ape, sexo, meses, com, alt, tutor, cel, controles in NINOS_INC1:
        nacimiento = agregar_meses(hoy, -meses)
        evals = [(hoy - timedelta(days=d), hb, peso, talla) for d, hb, peso, talla in controles]
        casos.append(Caso(dni, nom, ape, sexo, nacimiento, com, alt, tutor, cel, evals, escenario="Incremento 1"))

    def agregar(dni, nom, ape, sexo, nacimiento, com, alt, tutor, cel, evals, escenario, alta=False):
        controles = [_control(f, nacimiento, c, alt) for f, c in evals]
        casos.append(Caso(dni, nom, ape, sexo, nacimiento, com, alt, tutor, cel, controles, alta, escenario))

    def hito(nac: date, meses: int, desfase: int = 0) -> date:
        return agregar_meses(nac, meses) + timedelta(days=desfase)

    # 15. Al día: tres dosajes cumplidos y el siguiente aún lejano.
    n = _nacer_con_hito(hoy, 18, 18)
    agregar("71000015", "Valeria", "Ccente Rojas", "F", n, "Palmayoc", 3720, "Mirian Rojas Taipe", "911223344",
            [(hito(n, 9, 2), "SIN_ANEMIA"), (hito(n, 12, -3), "SIN_ANEMIA"), (hito(n, 15, 4), "SIN_ANEMIA")],
            "Al día: DHc1, DHc2 y DHx cumplidos; DHc1 de 18 meses pendiente")  # fmt: skip
    # 16. Dos controles de edad vencidos (uno con más de 30 días de atraso).
    n = _nacer_con_hito(hoy, 21, 25)
    agregar("71000016", "Joel", "Poma Huaylla", "M", n, "Chongos Alto", 3550, "Dora Huaylla Pari", "922334455",
            [(hito(n, 12, 1), "SIN_ANEMIA")],
            "Edad vencida: DHx de 15 y DHc1 de 18 meses sin realizar")  # fmt: skip
    # 17. Próximo a vencer: la ventana del DHc1 de 18 meses cierra en 3 días.
    n = _nacer_con_hito(hoy, 18, -27)
    agregar("71000017", "Camila", "Arzapalo Vila", "F", n, "Huaycha", 3950, "Ines Vila Meza", "933445566",
            [(hito(n, 15, 0), "SIN_ANEMIA")],
            "Próximo a vencer: DHc1 de 18 meses vence en 3 días")  # fmt: skip
    # 18. Vencido con poco atraso (prioridad BAJA).
    n = _nacer_con_hito(hoy, 18, -34)
    agregar("71000018", "Rodrigo", "Cerrón Taipe", "M", n, "Llacuas", 3890, "Felipa Taipe Lazo", None,
            [(hito(n, 15, 1), "SIN_ANEMIA")],
            "Edad vencida con atraso corto: DHc1 de 18 meses (prioridad BAJA)")  # fmt: skip
    # 19. Vencido con atraso medio (prioridad MEDIA).
    n = _nacer_con_hito(hoy, 12, -55)
    agregar("71000019", "Alexandra", "Huari Condori", "F", n, "Palmayoc", 3720, "Luz Condori Ramos", "944556677",
            [(hito(n, 9, 0), "SIN_ANEMIA")],
            "Edad vencida con atraso medio: DHc2 de 12 meses (prioridad MEDIA)")  # fmt: skip
    # 20. Vencido con mucho atraso (prioridad ALTA por más de 30 días).
    n = _nacer_con_hito(hoy, 24, -90)
    agregar("71000020", "Piero", "Samaniego Lazo", "M", n, "Huaycha", 3950, "Rocío Lazo Inga", "955667788",
            [(hito(n, 18, 0), "SIN_ANEMIA"), (hito(n, 21, 3), "SIN_ANEMIA")],
            "Edad vencida con atraso largo: DHx de 24 meses (prioridad ALTA)")  # fmt: skip
    # 21. Tratamiento vencido: anemia moderada sin el control de 1 mes.
    n = _nacer_con_hito(hoy, 9, -80)
    agregar("71000021", "Dayana", "Orihuela Pari", "F", n, "Palmayoc", 3720, "Nancy Pari Solís", "966778899",
            [(hito(n, 9, 0), "MODERADA")],
            "Tratamiento vencido: anemia moderada, C1M sin realizar y C3M por llegar")  # fmt: skip
    # 22. Tratamiento en curso: C1M cumplido, C3M vencido (junto con el DHx de 15 meses) y C6M pendiente.
    n = _nacer_con_hito(hoy, 12, -166)
    agregar("71000022", "Ethan", "Chuquillanqui Ccanto", "M", n, "Llacuas", 3890, "Pilar Ccanto Vila", "977889900",
            [(hito(n, 12, 10), "LEVE"), (hito(n, 12, 10) + timedelta(days=33), "LEVE")],
            "Tratamiento en curso: C1M cumplido, C3M y DHx vencidos, C6M pendiente")  # fmt: skip
    # 23. Recuperado: anemia leve resuelta al mes; los controles restantes se cierran.
    n = _nacer_con_hito(hoy, 9, -120)
    agregar("71000023", "Milagros", "Inga Baquerizo", "F", n, "Chongos Alto", 3550, "Cecilia Baquerizo Rojas", None,
            [(hito(n, 9, 0), "LEVE"), (hito(n, 9, 0) + timedelta(days=34), "SIN_ANEMIA")],
            "Recuperado: C1M cumplido y C3M/C6M cerrados por recuperación")  # fmt: skip
    # 24. Con alta: sin agenda.
    n = agregar_meses(hoy, -30)
    agregar("71000024", "Santiago", "Rojas Meza", "M", n, "Huaycha", 3950, "Gloria Meza Cerrón", "988990011",
            [(hito(n, 24, 2), "SIN_ANEMIA"), (hito(n, 30, 0), "SIN_ANEMIA")],
            "Con alta: sin agenda de controles", alta=True)  # fmt: skip
    # 25. Cerca de los 60 meses: los controles de tratamiento posteriores a los 59 meses no se programan.
    n = agregar_meses(hoy, -56) - timedelta(days=5)
    agregar("71000025", "Lucero", "Pari Taipe", "F", n, "Chongos Alto", 3550, "Marisol Taipe Huari", "999001122",
            [(hoy - timedelta(days=20), "LEVE")],
            "Borde de edad: C1M y C3M se programan, C6M excede los 59 meses")  # fmt: skip
    # 26. Registrado hoy: sin controles vencidos.
    n = agregar_meses(hoy, -7)
    agregar("71000026", "Adriel", "Taipe Orihuela", "M", n, "Llacuas", 3890, "Beatriz Orihuela Pari", "910111213",
            [(hoy, "SIN_ANEMIA")],
            "Registrado hoy: la agenda empieza en el DHc1 de 9 meses")  # fmt: skip
    # 27. Dosaje de tamizaje cumplido por el último control, siguiente próximo a vencer (sin anemia).
    n = _nacer_con_hito(hoy, 15, -26)
    agregar("71000027", "Brenda", "Lazo Arzapalo", "F", n, "Palmayoc", 3720, "Teresa Arzapalo Poma", "921222324",
            [(hito(n, 12, -2), "SIN_ANEMIA")],
            "Próximo a vencer: DHx de 15 meses vence en 4 días")  # fmt: skip
    return casos


def cargar(servicio: ServicioExpediente, hoy: date) -> int:
    """Registra el conjunto sintético; omite los niños cuyo DNI ya existe. Devuelve cuántos creó."""
    creados = 0
    for caso in construir_casos(hoy):
        primero, *resto = sorted(caso.controles, key=lambda c: c[0])
        datos = dict(
            dni=caso.dni,
            nombres=caso.nombres,
            apellidos=caso.apellidos,
            sexo=caso.sexo,
            fecha_nacimiento=caso.nacimiento,
            establecimiento=ESTABLECIMIENTO,
            distrito="Chongos Alto",
            comunidad=caso.comunidad,
            altitud_m=caso.altitud,
            tutor_nombre=caso.tutor,
            tutor_celular=caso.celular,
        )

        def evaluacion(c):
            return dict(fecha=c[0], hemoglobina_observada=c[1], peso_kg=c[2], talla_cm=c[3])

        try:
            nino = servicio.registrar_nino(datos, evaluacion(primero), USUARIO_CARGA)
        except RegistroDuplicado:
            continue
        for c in resto:
            servicio.registrar_evaluacion(nino.id, evaluacion(c), USUARIO_CARGA)
        if caso.alta:
            servicio.actualizar_datos(nino.id, {"estado": "ALTA"}, USUARIO_CARGA)
        creados += 1
    return creados


def reiniciar(repo: RepositorioSQLAlchemy) -> int:
    """Elimina SOLO los niños cargados por este script (registrado_por = carga.datos.prueba)."""
    with repo.Sesion.begin() as s:
        filas = s.query(NinoORM).filter(NinoORM.registrado_por == USUARIO_CARGA).all()
        for fila in filas:
            s.delete(fila)
        return len(filas)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--reiniciar", action="store_true", help="borra antes los niños sintéticos ya cargados")
    args = ap.parse_args()
    repo = RepositorioSQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///./datos/anemia.db"))
    repo.crear_esquema()
    reloj = RelojSistema()
    if args.reiniciar:
        print(f"Niños sintéticos eliminados: {reiniciar(repo)}.")
    creados = cargar(ServicioExpediente(repo, reloj), reloj.hoy())
    print(f"Datos sintéticos cargados: {creados} niños.")


if __name__ == "__main__":
    main()
