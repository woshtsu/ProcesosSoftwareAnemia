"""Origen de los datos de un niño: registrado desde el sistema o importado de un dataset externo (ADR-009)."""

from enum import StrEnum


class OrigenDatos(StrEnum):
    SISTEMA = (
        "SISTEMA"  # registro nominal hecho por el personal desde la API o la interfaz: todos los campos obligatorios
    )
    DATASET_DIRESA_JUNIN = "DATASET_DIRESA_JUNIN"  # dataset anonimizado de la DIRESA Junín (HIS): sin datos personales
