"""Muestra estratificada, proporcional y reproducible de los registros del dataset."""

import random
from collections import defaultdict
from collections.abc import Sequence

from app.domain.model.importacion import RegistroImportado


def estrato(registro: RegistroImportado) -> tuple[str, str]:
    """Estrato = provincia × severidad registrada por el HIS en el diagnóstico (o «NULL» si no hay dato)."""
    diagnostico = next((e for e in registro.evaluaciones if e.tipo.value == "DIAGNOSTICO"), None)
    severidad = (diagnostico.clasificacion_origen if diagnostico else None) or "NULL"
    return registro.provincia or "SIN_DATO", severidad


def asignar_cupos(tamanos: dict[tuple[str, str], int], n: int) -> dict[tuple[str, str], int]:
    """Reparto proporcional de ``n`` por el método del mayor resto (la suma es exactamente ``n``)."""
    total = sum(tamanos.values())
    if n >= total:
        return dict(tamanos)
    exactos = {k: n * v / total for k, v in tamanos.items()}
    cupos = {k: int(x) for k, x in exactos.items()}
    faltan = n - sum(cupos.values())
    por_resto = sorted(exactos, key=lambda k: (-(exactos[k] - cupos[k]), k))
    for k in por_resto[:faltan]:
        cupos[k] += 1
    return cupos


def muestra_estratificada(registros: Sequence[RegistroImportado], n: int, semilla: int) -> list[RegistroImportado]:
    """``n`` registros distribuidos entre los estratos en proporción a su tamaño; misma semilla, misma muestra.

    Dentro de cada estrato los registros se ordenan por código antes de sortear, de modo que el resultado no depende
    del orden de lectura. El resultado se devuelve ordenado por código.
    """
    por_estrato: dict[tuple[str, str], list[RegistroImportado]] = defaultdict(list)
    for r in sorted(registros, key=lambda r: r.codigo_origen):
        por_estrato[estrato(r)].append(r)
    cupos = asignar_cupos({k: len(v) for k, v in por_estrato.items()}, n)
    azar = random.Random(semilla)  # noqa: S311 - muestreo reproducible, no criptográfico
    elegidos: list[RegistroImportado] = []
    for clave in sorted(por_estrato):
        elegidos += azar.sample(por_estrato[clave], cupos[clave])
    return sorted(elegidos, key=lambda r: r.codigo_origen)
