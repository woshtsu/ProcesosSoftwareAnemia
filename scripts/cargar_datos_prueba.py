"""Carga datos SINTÉTICOS de prueba (nombres y DNI ficticios) para el entorno de staging/demo.

Uso:  python -m scripts.cargar_datos_prueba            (usa DATABASE_URL o SQLite local)
"""

import os
from datetime import date, timedelta

from app.adapters.salida.persistencia.sqlalchemy_repo import RepositorioSQLAlchemy
from app.application.casos_uso import RelojSistema, ServicioExpediente
from app.domain.errores import RegistroDuplicado

HOY = date.today()

# dni, nombres, apellidos, sexo, meses de edad, comunidad, altitud, tutor, celular, controles [(dias_atras, hb_obs, peso, talla)]
NINOS = [
    (
        "71000001",
        "Luz Mery",
        "Quispe Rojas",
        "F",
        8,
        "Chongos Alto",
        3550,
        "Rosa Rojas Pérez",
        "987654321",
        [(62, 11.6, 7.6, 67.0), (20, 11.9, 8.0, 68.5)],
    ),
    (
        "71000002",
        "Jhon Kevin",
        "Huamán Poma",
        "M",
        14,
        "Palmayoc",
        3720,
        "Elsa Poma Ccente",
        "912345678",
        [(75, 11.4, 9.1, 74.0), (34, 11.8, 9.4, 75.5)],
    ),
    (
        "71000003",
        "Yeny",
        "Condori Huaylla",
        "F",
        10,
        "Chongos Alto",
        3550,
        "Marta Huaylla Vila",
        None,
        [(48, 10.9, 8.2, 70.0), (10, 11.2, 8.6, 71.8)],
    ),
    (
        "71000004",
        "Brayan",
        "Ccanto Samaniego",
        "M",
        30,
        "Llacuas",
        3890,
        "Nelly Samaniego Arzapalo",
        "956789012",
        [(66, 12.8, 12.6, 88.0), (40, 13.1, 12.9, 89.0)],
    ),
    (
        "71000005",
        "Mayra",
        "Taipe Orihuela",
        "F",
        18,
        "Palmayoc",
        3720,
        "Gladys Orihuela Ramos",
        "923456789",
        [(55, 12.4, 10.1, 79.0)],
    ),
    (
        "71000006",
        "Luis Ángel",
        "Rivera Chuquillanqui",
        "M",
        7,
        "Chongos Alto",
        3550,
        "Karina Chuquillanqui Solís",
        "934567890",
        [(15, 12.9, 7.9, 68.0)],
    ),
    (
        "71000007",
        "Nayeli",
        "Pomalaza Cerrón",
        "F",
        40,
        "Llacuas",
        3890,
        "Ruth Cerrón Baquerizo",
        None,
        [(70, 12.9, 13.8, 95.0), (28, 13.4, 14.1, 96.0)],
    ),
    (
        "71000008",
        "Dilan",
        "Suárez Meza",
        "M",
        22,
        "Huaycha",
        3950,
        "Olga Meza Inga",
        "945678901",
        [(80, 13.7, 11.0, 83.0), (45, 13.9, 11.3, 84.0)],
    ),
    (
        "71000009",
        "Kiara",
        "Inga Lazo",
        "F",
        12,
        "Huaycha",
        3950,
        "Doris Lazo Pari",
        "956780123",
        [(38, 12.2, 8.9, 73.0)],
    ),
    (
        "71000010",
        "Fabián",
        "Lazo Ccanto",
        "M",
        50,
        "Chongos Alto",
        3550,
        "Irma Ccanto Huari",
        "967890123",
        [(58, 13.3, 15.6, 101.0)],
    ),
    (
        "71000011",
        "Sheyla",
        "Huari Pari",
        "F",
        9,
        "Llacuas",
        3890,
        "Lidia Pari Poma",
        "978901234",
        [(25, 13.0, 8.0, 69.0)],
    ),
    (
        "71000012",
        "Thiago",
        "Arzapalo Vila",
        "M",
        16,
        "Palmayoc",
        3720,
        "Yolanda Vila Taipe",
        None,
        [(42, 13.3, 9.9, 77.0), (5, 13.6, 10.2, 78.2)],
    ),
    (
        "71000013",
        "Ariana",
        "Solís Rojas",
        "F",
        26,
        "Huaycha",
        3950,
        "Sonia Rojas Cerrón",
        "989012345",
        [(33, 13.6, 11.7, 86.0)],
    ),
    (
        "71000014",
        "Josué",
        "Pari Condori",
        "M",
        11,
        "Chongos Alto",
        3550,
        "Maribel Condori Taipe",
        "990123456",
        [(18, 10.4, 8.3, 72.0)],
    ),
]


def restar_meses(d: date, meses: int) -> date:
    y, m = divmod(d.month - 1 - meses, 12)
    return date(d.year + y, m + 1, min(d.day, 28))


def main() -> None:
    repo = RepositorioSQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///./datos/anemia.db"))
    repo.crear_esquema()
    svc = ServicioExpediente(repo, RelojSistema())
    creados = 0
    for dni, nom, ape, sexo, meses, com, alt, tutor, cel, controles in NINOS:
        primero, *resto = sorted(controles, key=lambda c: -c[0])
        datos = dict(
            dni=dni,
            nombres=nom,
            apellidos=ape,
            sexo=sexo,
            fecha_nacimiento=restar_meses(HOY, meses),
            establecimiento="P. S. Chongos Alto",
            distrito="Chongos Alto",
            comunidad=com,
            altitud_m=alt,
            tutor_nombre=tutor,
            tutor_celular=cel,
        )
        ev = lambda c: dict(fecha=HOY - timedelta(days=c[0]), hemoglobina_observada=c[1], peso_kg=c[2], talla_cm=c[3])  # noqa: E731
        try:
            nino = svc.registrar_nino(datos, ev(primero), "carga.datos.prueba")
        except RegistroDuplicado:
            continue
        for c in resto:
            svc.registrar_evaluacion(nino.id, ev(c), "carga.datos.prueba")
        creados += 1
    print(f"Datos sintéticos cargados: {creados} niños.")


if __name__ == "__main__":
    main()
