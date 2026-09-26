"""
Blueprints API REST — PMV Anemia Junín.

Endpoints JSON /api/v1/. Invocan los mismos casos de uso que el frontend HTML.
Sin CORS habilitado. Sin trazas internas en respuestas de error.
"""

from __future__ import annotations

import traceback
from datetime import date

from flask import Blueprint, current_app, jsonify, request

from anemia_junin.application.casos_de_uso.actualizar_nino import (
    ActualizacionVaciaError,
)
from anemia_junin.application.casos_de_uso.consultar_expediente import (
    NinoNoEncontradoError,
)
from anemia_junin.application.casos_de_uso.registrar_nino import DniDuplicadoError
from anemia_junin.application.dto import (
    ActualizarNinoDTO,
    CrearDosajeDTO,
    CrearNinoDTO,
    DosajeInicialDTO,
    FiltroListaDTO,
    PeriodoReporteDTO,
)
from anemia_junin.domain.entities import Sexo, TipoNacimiento
from anemia_junin.domain.validators import ErrorValidacion

api_bp = Blueprint("api", __name__)

_CAMPOS_NINO_PERMITIDOS = {
    "dni", "nombres", "apellidos", "fecha_nacimiento", "sexo",
    "tipo_nacimiento", "peso_kg", "distrito", "altitud_msnm",
    "cuidador", "telefono", "dosaje_inicial",
}
_CAMPOS_ACTUALIZACION_PERMITIDOS = {
    "peso_kg", "distrito", "altitud_msnm", "cuidador", "telefono"
}
_CAMPOS_DOSAJE_PERMITIDOS = {"fecha_dosaje", "hb_observada", "altitud_msnm"}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _cu(nombre: str):
    return current_app.config["CASOS_DE_USO"][nombre]


def _error(code: str, message: str, fields: dict | None = None, status: int = 400):
    body = {"error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = fields
    return jsonify(body), status


def _error_media_type():
    return _error(
        "UNSUPPORTED_MEDIA_TYPE", "Content-Type debe ser application/json", status=415
    )


def _parse_fecha(valor: object, campo: str) -> tuple[date | None, list[str]]:
    if not isinstance(valor, str):
        return None, [f"'{campo}' debe ser texto en formato YYYY-MM-DD"]
    try:
        return date.fromisoformat(valor), []
    except ValueError:
        return None, [f"'{campo}' debe ser una fecha válida (YYYY-MM-DD)"]


def _parse_hb(valor: object, campo: str = "hb_observada") -> tuple[int, list[str]]:
    """Parsea Hb en g/dL y devuelve décimas."""
    from anemia_junin.domain.validators import validar_hb_gdl
    errores, ddl = validar_hb_gdl(valor)
    return ddl, errores


def _serializar_nino(dto) -> dict:
    return {
        "id": str(dto.id),
        "dni": dto.dni,
        "nombres": dto.nombres,
        "apellidos": dto.apellidos,
        "fecha_nacimiento": dto.fecha_nacimiento.isoformat(),
        "sexo": dto.sexo.value,
        "tipo_nacimiento": dto.tipo_nacimiento.value,
        "peso_kg": dto.peso_kg,
        "distrito": dto.distrito,
        "altitud_msnm": dto.altitud_msnm,
        "cuidador": dto.cuidador,
        "telefono": dto.telefono,
        "created_at": dto.created_at.isoformat() + "Z",
        "updated_at": dto.updated_at.isoformat() + "Z",
    }


def _serializar_dosaje(dto) -> dict:
    return {
        "id": str(dto.id),
        "nino_id": str(dto.nino_id),
        "fecha_dosaje": dto.fecha_dosaje.isoformat(),
        "hb_observada": dto.hb_observada,
        "altitud_msnm": dto.altitud_msnm,
        "ajuste_gdl": dto.ajuste_gdl,
        "hb_ajustada": dto.hb_ajustada,
        "edad_meses": dto.edad_meses,
        "clasificacion": dto.clasificacion.value,
        "version_normativa": dto.version_normativa,
        "advertencias": dto.advertencias,
        "created_at": dto.created_at.isoformat() + "Z",
    }


# ─── GET /salud ───────────────────────────────────────────────────────────────

@api_bp.get("/salud")
def get_salud():
    # La verificación la inyecta bootstrap (adaptador de salida SQLite):
    # el adaptador de entrada no conoce la tecnología de persistencia.
    verificar_bd = current_app.config["VERIFICAR_BD"]
    bd_estado = "conectada" if verificar_bd() else "error"

    return jsonify({
        "data": {
            "estado": "ok",
            "version": "1.0.0",
            "base_datos": bd_estado,
        }
    })


# ─── POST /ninos ──────────────────────────────────────────────────────────────

@api_bp.post("/ninos")
def crear_nino():
    if not request.is_json:
        return _error_media_type()

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error("INVALID_JSON", "El cuerpo debe ser un objeto JSON válido")

    # Rechazar campos desconocidos
    campos_extra = set(data.keys()) - _CAMPOS_NINO_PERMITIDOS
    if campos_extra:
        return _error("VALIDATION_ERROR", "Campos no permitidos",
                      {"_extra": [f"Campo(s) no permitido(s): {', '.join(sorted(campos_extra))}"]})

    errores: dict[str, list[str]] = {}

    # Parsear fecha_nacimiento
    fecha_nac, err = _parse_fecha(data.get("fecha_nacimiento"), "fecha_nacimiento")
    errores["fecha_nacimiento"] = err

    # Parsear peso
    from anemia_junin.domain.validators import validar_peso_kg
    err_peso, peso_g = validar_peso_kg(data.get("peso_kg"))
    errores["peso_kg"] = err_peso

    # Parsear sexo y tipo de nacimiento (sin valores por defecto silenciosos)
    sexo_raw = data.get("sexo")
    try:
        sexo = Sexo(sexo_raw)
    except ValueError:
        sexo = None
        errores["sexo"] = ["Debe ser 'F' o 'M'"]

    tipo_raw = data.get("tipo_nacimiento")
    try:
        tipo_nac = TipoNacimiento(tipo_raw)
    except ValueError:
        tipo_nac = None
        errores["tipo_nacimiento"] = ["Debe ser 'TERMINO' o 'PREMATURO'"]

    # Parsear dosaje_inicial
    dosaje_inicial = None
    dosaje_data = data.get("dosaje_inicial")
    if dosaje_data is not None:
        if not isinstance(dosaje_data, dict):
            return _error("VALIDATION_ERROR", "Revise los datos ingresados",
                          {"dosaje_inicial": ["Debe ser un objeto"]})
        campos_extra_d = set(dosaje_data.keys()) - {"fecha_dosaje", "hb_observada"}
        if campos_extra_d:
            # Error estructural: se rechaza sin llegar al caso de uso
            return _error("VALIDATION_ERROR", "Revise los datos ingresados", {
                "dosaje_inicial": [
                    "Campos no permitidos en dosaje_inicial: "
                    + ", ".join(sorted(campos_extra_d))
                ]
            })
        fecha_d, err_fd = _parse_fecha(
            dosaje_data.get("fecha_dosaje"), "dosaje_inicial.fecha_dosaje"
        )
        errores["dosaje_inicial.fecha_dosaje"] = err_fd
        hb_ddl, err_hb = _parse_hb(dosaje_data.get("hb_observada"))
        errores["dosaje_inicial.hb_observada"] = err_hb
        dosaje_inicial = DosajeInicialDTO(
            fecha_dosaje=fecha_d,
            hb_observada_ddl=hb_ddl if not err_hb else 0,
        )

    dto = CrearNinoDTO(
        dni=data.get("dni", ""),
        nombres=data.get("nombres", ""),
        apellidos=data.get("apellidos", ""),
        fecha_nacimiento=fecha_nac,
        sexo=sexo,
        tipo_nacimiento=tipo_nac,
        peso_g=peso_g if not err_peso else None,
        distrito=data.get("distrito", ""),
        altitud_msnm=data.get("altitud_msnm"),
        cuidador=data.get("cuidador", ""),
        telefono=data.get("telefono") or None,
        dosaje_inicial=dosaje_inicial,
    )

    try:
        # Los errores de conversión se pasan al caso de uso, que decide y registra
        # el intento rechazado (traza de calidad HIST-1.5).
        nino_dto, dosaje_dto = _cu("registrar_nino").ejecutar(dto, errores_entrada=errores)
    except ErrorValidacion as exc:
        return _error("VALIDATION_ERROR", "Revise los datos ingresados", exc.errores)
    except DniDuplicadoError:
        return _error("CONFLICT", "El DNI ya está registrado en el sistema", status=409)
    except Exception:
        current_app.logger.error(traceback.format_exc())
        return _error("INTERNAL_ERROR", "Error interno del servidor", status=500)

    respuesta = {"data": _serializar_nino(nino_dto)}
    if dosaje_dto:
        respuesta["data"]["dosaje_inicial"] = _serializar_dosaje(dosaje_dto)

    return jsonify(respuesta), 201


# ─── GET /ninos ───────────────────────────────────────────────────────────────

@api_bp.get("/ninos")
def listar_ninos():
    try:
        pagina = int(request.args.get("pagina", 1))
        tamano = int(request.args.get("tamano", 20))
    except ValueError:
        return _error("VALIDATION_ERROR", "Los parámetros de paginación deben ser enteros")

    dto = FiltroListaDTO(
        q=request.args.get("q") or None,
        distrito=request.args.get("distrito") or None,
        clasificacion=request.args.get("clasificacion") or None,
        pagina=pagina,
        tamano=tamano,
    )

    pagina_dto = _cu("listar_ninos").ejecutar(dto)

    items = [
        {
            "dni": n.dni,
            "nombres": n.nombres,
            "apellidos": n.apellidos,
            "fecha_nacimiento": n.fecha_nacimiento.isoformat(),
            "sexo": n.sexo.value,
            "distrito": n.distrito,
            "clasificacion_ultimo_dosaje": n.clasificacion_ultimo_dosaje.value,
        }
        for n in pagina_dto.items
    ]

    return jsonify({
        "data": items,
        "meta": {
            "pagina": pagina_dto.pagina,
            "tamano": pagina_dto.tamano,
            "total": pagina_dto.total,
        }
    })


# ─── GET /ninos/<dni> ─────────────────────────────────────────────────────────

@api_bp.get("/ninos/<string:dni>")
def get_expediente(dni: str):
    try:
        expediente = _cu("consultar_expediente").ejecutar(dni)
    except NinoNoEncontradoError:
        return _error("NOT_FOUND", f"Niño con DNI {dni} no encontrado", status=404)

    return jsonify({
        "data": {
            "nino": _serializar_nino(expediente.nino),
            "clasificacion_actual": expediente.clasificacion_actual.value,
            "historial_dosajes": [_serializar_dosaje(d) for d in expediente.historial_dosajes],
        }
    })


# ─── PATCH /ninos/<dni> ───────────────────────────────────────────────────────

@api_bp.patch("/ninos/<string:dni>")
def actualizar_nino(dni: str):
    if not request.is_json:
        return _error_media_type()

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error("INVALID_JSON", "El cuerpo debe ser un objeto JSON válido")

    campos_extra = set(data.keys()) - _CAMPOS_ACTUALIZACION_PERMITIDOS
    if campos_extra:
        return _error("VALIDATION_ERROR", "Campos no permitidos o no editables",
                      {"_extra": [f"No se puede modificar: {', '.join(sorted(campos_extra))}"]})

    if not data:
        return _error("VALIDATION_ERROR", "Se requiere al menos un campo para actualizar")

    # Parsear peso si viene
    peso_g = None
    errores: dict[str, list[str]] = {}
    if "peso_kg" in data:
        from anemia_junin.domain.validators import validar_peso_kg
        err_peso, peso_g = validar_peso_kg(data["peso_kg"])
        errores["peso_kg"] = err_peso

    dto = ActualizarNinoDTO(
        peso_g=peso_g if "peso_kg" in data else None,
        distrito=data.get("distrito"),
        altitud_msnm=data.get("altitud_msnm"),
        cuidador=data.get("cuidador"),
        telefono=data.get("telefono"),
    )

    try:
        nino_dto = _cu("actualizar_nino").ejecutar(dni, dto)
    except ErrorValidacion as exc:
        merged = {**errores, **exc.errores}
        return _error("VALIDATION_ERROR", "Revise los datos ingresados", merged)
    except NinoNoEncontradoError:
        return _error("NOT_FOUND", f"Niño con DNI {dni} no encontrado", status=404)
    except ActualizacionVaciaError:
        return _error("VALIDATION_ERROR", "Se requiere al menos un campo para actualizar")

    return jsonify({"data": _serializar_nino(nino_dto)})


# ─── POST /ninos/<dni>/dosajes ────────────────────────────────────────────────

@api_bp.post("/ninos/<string:dni>/dosajes")
def agregar_dosaje(dni: str):
    if not request.is_json:
        return _error_media_type()

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error("INVALID_JSON", "El cuerpo debe ser un objeto JSON válido")

    campos_extra = set(data.keys()) - _CAMPOS_DOSAJE_PERMITIDOS
    if campos_extra:
        return _error("VALIDATION_ERROR", "Campos no permitidos",
                      {"_extra": [f"Campo(s) no permitido(s): {', '.join(sorted(campos_extra))}"]})

    errores: dict[str, list[str]] = {}
    fecha_d, err_f = _parse_fecha(data.get("fecha_dosaje"), "fecha_dosaje")
    errores["fecha_dosaje"] = err_f
    hb_ddl, err_hb = _parse_hb(data.get("hb_observada"))
    errores["hb_observada"] = err_hb

    alt = data.get("altitud_msnm")
    from anemia_junin.domain.validators import validar_altitud
    errores["altitud_msnm"] = validar_altitud(alt) if alt is not None else ["Campo requerido"]

    hay_errores = any(v for v in errores.values())
    if hay_errores:
        return _error("VALIDATION_ERROR", "Revise los datos ingresados", errores)

    dto = CrearDosajeDTO(
        fecha_dosaje=fecha_d,
        hb_observada_ddl=hb_ddl,
        altitud_msnm=int(alt),
    )

    try:
        dosaje_dto = _cu("agregar_dosaje").ejecutar(dni, dto)
    except ErrorValidacion as exc:
        return _error("VALIDATION_ERROR", "Revise los datos ingresados", exc.errores)
    except NinoNoEncontradoError:
        return _error("NOT_FOUND", f"Niño con DNI {dni} no encontrado", status=404)

    return jsonify({"data": _serializar_dosaje(dosaje_dto)}), 201


# ─── GET /reportes/registros ──────────────────────────────────────────────────

@api_bp.get("/reportes/registros")
def get_reporte():
    desde_str = request.args.get("desde")
    hasta_str = request.args.get("hasta")

    errores: dict[str, list[str]] = {}
    if not desde_str:
        errores["desde"] = ["Parámetro requerido"]
    if not hasta_str:
        errores["hasta"] = ["Parámetro requerido"]

    if errores:
        return _error("VALIDATION_ERROR", "Parámetros requeridos faltantes", errores)

    desde_date, err1 = _parse_fecha(desde_str, "desde")
    hasta_date, err2 = _parse_fecha(hasta_str, "hasta")
    if err1:
        errores["desde"] = err1
    if err2:
        errores["hasta"] = err2
    if errores:
        return _error("VALIDATION_ERROR", "Fechas inválidas", errores)

    dto = PeriodoReporteDTO(desde=desde_date, hasta=hasta_date)

    try:
        reporte = _cu("consultar_reporte").ejecutar(dto)
    except ErrorValidacion as exc:
        return _error("VALIDATION_ERROR", "Revise los parámetros", exc.errores)

    return jsonify({
        "data": {
            "periodo": {
                "desde": reporte.periodo_desde.isoformat(),
                "hasta": reporte.periodo_hasta.isoformat(),
            },
            "ninos_registrados": reporte.ninos_registrados,
            "dosajes_registrados": reporte.dosajes_registrados,
            "distribucion_clasificacion": reporte.distribucion_clasificacion,
            "distribucion_distrito": reporte.distribucion_distrito,
            "calidad_registro": {
                "intentos_aceptados": reporte.calidad_registro.intentos_aceptados,
                "intentos_rechazados": reporte.calidad_registro.intentos_rechazados,
                "tasa_aceptacion_pct": reporte.calidad_registro.tasa_aceptacion_pct,
            }
        }
    })
