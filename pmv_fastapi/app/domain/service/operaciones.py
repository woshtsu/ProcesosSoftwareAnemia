"""Normalización de las operaciones que llegan del dispositivo (HIST-3.2). Servicio de dominio puro.

El dispositivo envía JSON: las fechas llegan como texto ISO (AAAA-MM-DD) y los números pueden venir mal tipados.
Aquí se convierten a los tipos del dominio y se señala, por campo, lo que no se pudo convertir. Las reglas clínicas y
de negocio NO se repiten aquí: las aplican los mismos servicios de validación del registro en línea.
"""

from datetime import date, datetime

from app.domain.model.errores import ErrorCampo
from app.domain.model.sincronizacion import TipoOperacion
from app.domain.model.tiempo import ZONA_PERU

_NINO = {
    "dni": "texto",
    "nombres": "texto",
    "apellidos": "texto",
    "sexo": "texto",
    "fecha_nacimiento": "fecha",
    "establecimiento": "texto",
    "distrito": "texto",
    "comunidad": "texto",
    "altitud_m": "numero",
    "tutor_nombre": "texto",
    "tutor_celular": "texto",
}
_EVALUACION = {"fecha": "fecha", "hemoglobina_observada": "numero", "peso_kg": "numero", "talla_cm": "numero"}
_ASISTENCIA = {
    "codigo": "texto",
    "fecha_programada": "fecha",
    "estado": "texto",
    "motivo": "texto",
    "evaluacion_id": "texto",
}
_VISITA = {"fecha": "fecha", "resultado": "texto", "consume_suplemento": "texto", "observaciones": "texto"}
_BARRERA = {"tipo": "texto", "detalle": "texto", "fuente": "texto", "fecha": "fecha"}

_MENSAJE = {
    "fecha": "Fecha inválida (use AAAA-MM-DD).",
    "numero": "Debe ser un número.",
    "texto": "Debe ser texto.",
}


def normalizar_fecha_local(momento: datetime) -> datetime:
    """Fecha y hora local del dispositivo con zona horaria; sin zona se interpreta como hora de Perú."""
    return momento if momento.tzinfo else momento.replace(tzinfo=ZONA_PERU)


def _convertir(valor, tipo: str):
    """Valor convertido al tipo del dominio; lanza ValueError si no corresponde."""
    if valor is None:
        return None
    if tipo == "fecha":
        if isinstance(valor, str):
            return date.fromisoformat(valor)
        raise ValueError(valor)
    if tipo == "numero":
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(valor)
        return float(valor)
    if not isinstance(valor, str):
        raise ValueError(valor)
    return valor


def _convertir_objeto(objeto, esquema: dict[str, str], errores: list[ErrorCampo]) -> dict:
    if not isinstance(objeto, dict):
        errores.append(ErrorCampo("datos", "Debe ser un objeto."))
        return {}
    convertido = {}
    for campo, tipo in esquema.items():
        try:
            convertido[campo] = _convertir(objeto.get(campo), tipo)
        except ValueError:
            errores.append(ErrorCampo(campo, _MENSAJE[tipo]))
    return convertido


def normalizar_datos(tipo: str, datos: dict) -> tuple[dict, list[ErrorCampo]]:
    """Datos de la operación con los tipos del dominio y los errores de formato (lista vacía si todo está bien).

    Resultado según el tipo: REGISTRAR_NINO -> ``{"nino": {...}, "evaluacion": {...}}``; REGISTRAR_EVALUACION,
    REGISTRAR_ASISTENCIA, REGISTRAR_VISITA y REGISTRAR_BARRERA -> el diccionario plano de campos.
    """
    errores: list[ErrorCampo] = []
    if tipo == TipoOperacion.REGISTRAR_NINO:
        nino = _convertir_objeto(datos.get("nino"), _NINO, errores)
        evaluacion = _convertir_objeto(datos.get("evaluacion_inicial"), _EVALUACION, errores)
        return {"nino": nino, "evaluacion": evaluacion}, errores
    esquema = {
        TipoOperacion.REGISTRAR_EVALUACION: _EVALUACION,
        TipoOperacion.REGISTRAR_ASISTENCIA: _ASISTENCIA,
        TipoOperacion.REGISTRAR_VISITA: _VISITA,
        TipoOperacion.REGISTRAR_BARRERA: _BARRERA,
    }.get(tipo)
    if esquema is None:
        return {}, [ErrorCampo("tipo", "Tipo de operación desconocido.")]
    return _convertir_objeto(datos, esquema, errores), errores
