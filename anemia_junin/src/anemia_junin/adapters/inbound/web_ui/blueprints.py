"""
Blueprints Web UI — PMV Anemia Junín.

Rutas HTML con POST/Redirect/GET (303). Usan los mismos casos de uso que la API.
Sin CORS. Escape automático por Jinja2. Datos de formulario preservados en errores.
"""

from __future__ import annotations

from datetime import date

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)

from anemia_junin.application.casos_de_uso.actualizar_nino import ActualizacionVaciaError
from anemia_junin.application.casos_de_uso.consultar_expediente import NinoNoEncontradoError
from anemia_junin.application.casos_de_uso.registrar_nino import DniDuplicadoError
from anemia_junin.application.dto import (
    ActualizarNinoDTO,
    CrearDosajeDTO,
    CrearNinoDTO,
    DosajeInicialDTO,
    FiltroListaDTO,
    PeriodoReporteDTO,
)
from anemia_junin.domain.validators import (
    ErrorValidacion,
    validar_hb_gdl,
    validar_peso_kg,
)

web_bp = Blueprint("web", __name__)


def _cu(nombre: str):
    return current_app.config["CASOS_DE_USO"][nombre]


# ─── Raíz ────────────────────────────────────────────────────────────────────

@web_bp.get("/")
def raiz():
    return redirect(url_for("web.lista_ninos"), 303)


# ─── Lista de niños ───────────────────────────────────────────────────────────

@web_bp.get("/ninos")
def lista_ninos():
    try:
        pagina = int(request.args.get("pagina", 1))
        tamano = int(request.args.get("tamano", 20))
    except ValueError:
        pagina, tamano = 1, 20

    dto = FiltroListaDTO(
        q=request.args.get("q") or None,
        distrito=request.args.get("distrito") or None,
        clasificacion=request.args.get("clasificacion") or None,
        pagina=pagina,
        tamano=tamano,
    )
    resultado = _cu("listar_ninos").ejecutar(dto)
    return render_template(
        "ninos/lista.html",
        ninos=resultado.items,
        meta={"pagina": resultado.pagina, "tamano": resultado.tamano, "total": resultado.total},
        filtros=dto,
    )


# ─── Registro de nuevo niño ───────────────────────────────────────────────────

@web_bp.get("/ninos/nuevo")
def nuevo_nino_form():
    return render_template("ninos/nuevo.html", errores={}, datos={})


def _fecha_o_none(valor: str | None) -> date | None:
    try:
        return date.fromisoformat(valor or "")
    except ValueError:
        return None


def _entero_o_none(valor: str | None) -> int | None:
    try:
        return int((valor or "").strip())
    except ValueError:
        return None


@web_bp.post("/ninos/nuevo")
def nuevo_nino_post():
    f = request.form
    errores_entrada: dict[str, list[str]] = {}

    # Peso (kg → gramos)
    err_peso, peso_g = validar_peso_kg(f.get("peso_kg", ""))
    errores_entrada["peso_kg"] = err_peso

    # Fecha de nacimiento: nunca se sustituye por "hoy" si viene mal formada
    fecha_nac = _fecha_o_none(f.get("fecha_nacimiento"))
    if fecha_nac is None:
        errores_entrada["fecha_nacimiento"] = ["Ingrese una fecha válida (AAAA-MM-DD)"]

    # Dosaje inicial opcional
    dosaje_inicial = None
    if f.get("tiene_dosaje_inicial") == "1":
        err_hb, hb_ddl = validar_hb_gdl(f.get("hb_observada", ""))
        errores_entrada["dosaje_inicial.hb_observada"] = err_hb
        fecha_d = _fecha_o_none(f.get("fecha_dosaje"))
        if fecha_d is None:
            errores_entrada["dosaje_inicial.fecha_dosaje"] = ["Ingrese una fecha válida"]
        dosaje_inicial = DosajeInicialDTO(
            fecha_dosaje=fecha_d,
            hb_observada_ddl=hb_ddl if not err_hb else 0,
        )

    altitud_raw = f.get("altitud_msnm", "")
    dto = CrearNinoDTO(
        dni=f.get("dni", "").strip(),
        nombres=f.get("nombres", ""),
        apellidos=f.get("apellidos", ""),
        fecha_nacimiento=fecha_nac,
        sexo=f.get("sexo") or None,
        tipo_nacimiento=f.get("tipo_nacimiento") or None,
        peso_g=peso_g if not err_peso else None,
        distrito=f.get("distrito", ""),
        altitud_msnm=altitud_raw if altitud_raw != "" else None,
        cuidador=f.get("cuidador", ""),
        telefono=(f.get("telefono") or "").strip() or None,
        dosaje_inicial=dosaje_inicial,
    )

    try:
        nino_dto, _ = _cu("registrar_nino").ejecutar(dto, errores_entrada=errores_entrada)
        return redirect(url_for("web.expediente", dni=nino_dto.dni), 303)
    except ErrorValidacion as exc:
        return render_template("ninos/nuevo.html", errores=exc.errores, datos=f), 422
    except DniDuplicadoError:
        errores = {"dni": ["Este DNI ya está registrado"]}
        return render_template("ninos/nuevo.html", errores=errores, datos=f), 409


# ─── Expediente ───────────────────────────────────────────────────────────────

@web_bp.get("/ninos/<string:dni>")
def expediente(dni: str):
    try:
        exp = _cu("consultar_expediente").ejecutar(dni)
    except NinoNoEncontradoError:
        return render_template("errors/404.html", dni=dni), 404
    return render_template("ninos/expediente.html", expediente=exp)


# ─── Edición ─────────────────────────────────────────────────────────────────

@web_bp.get("/ninos/<string:dni>/editar")
def editar_form(dni: str):
    try:
        exp = _cu("consultar_expediente").ejecutar(dni)
    except NinoNoEncontradoError:
        return render_template("errors/404.html", dni=dni), 404
    return render_template("ninos/editar.html", nino=exp.nino, errores={}, datos={})


@web_bp.post("/ninos/<string:dni>/editar")
def editar_post(dni: str):
    f = request.form

    err_peso, peso_g = validar_peso_kg(f.get("peso_kg", "")) if f.get("peso_kg") else ([], None)
    if err_peso:
        try:
            exp = _cu("consultar_expediente").ejecutar(dni)
        except NinoNoEncontradoError:
            return render_template("errors/404.html", dni=dni), 404
        return render_template(
            "ninos/editar.html", nino=exp.nino, errores={"peso_kg": err_peso}, datos=f
        ), 422

    dto = ActualizarNinoDTO(
        peso_g=peso_g if f.get("peso_kg") else None,
        distrito=f.get("distrito") or None,
        altitud_msnm=f.get("altitud_msnm") or None,
        cuidador=f.get("cuidador") or None,
        telefono=f.get("telefono") or None,
    )

    try:
        _cu("actualizar_nino").ejecutar(dni, dto)
        return redirect(url_for("web.expediente", dni=dni), 303)
    except ErrorValidacion as exc:
        try:
            exp = _cu("consultar_expediente").ejecutar(dni)
        except NinoNoEncontradoError:
            return render_template("errors/404.html", dni=dni), 404
        return render_template(
            "ninos/editar.html", nino=exp.nino, errores=exc.errores, datos=f
        ), 422
    except ActualizacionVaciaError:
        try:
            exp = _cu("consultar_expediente").ejecutar(dni)
        except NinoNoEncontradoError:
            return render_template("errors/404.html", dni=dni), 404
        return render_template(
            "ninos/editar.html", nino=exp.nino,
            errores={"_general": ["Ingrese al menos un campo para actualizar"]}, datos=f
        ), 422
    except NinoNoEncontradoError:
        return render_template("errors/404.html", dni=dni), 404


# ─── Nuevo dosaje ─────────────────────────────────────────────────────────────

@web_bp.get("/ninos/<string:dni>/dosajes/nuevo")
def nuevo_dosaje_form(dni: str):
    try:
        exp = _cu("consultar_expediente").ejecutar(dni)
    except NinoNoEncontradoError:
        return render_template("errors/404.html", dni=dni), 404
    return render_template(
        "dosajes/nuevo.html", nino=exp.nino, errores={}, datos={},
        altitud_precargada=exp.nino.altitud_msnm,
    )


@web_bp.post("/ninos/<string:dni>/dosajes/nuevo")
def nuevo_dosaje_post(dni: str):
    f = request.form

    err_hb, hb_ddl = validar_hb_gdl(f.get("hb_observada", ""))
    fecha_d = _fecha_o_none(f.get("fecha_dosaje"))
    altitud = _entero_o_none(f.get("altitud_msnm"))

    errores_entrada: dict[str, list[str]] = {}
    if err_hb:
        errores_entrada["hb_observada"] = err_hb
    if fecha_d is None:
        errores_entrada["fecha_dosaje"] = ["Ingrese una fecha válida"]
    if altitud is None:
        errores_entrada["altitud_msnm"] = ["Debe ser un número entero"]

    try:
        if errores_entrada:
            raise ErrorValidacion(errores_entrada)
        dto = CrearDosajeDTO(fecha_dosaje=fecha_d, hb_observada_ddl=hb_ddl, altitud_msnm=altitud)
        _cu("agregar_dosaje").ejecutar(dni, dto)
        return redirect(url_for("web.expediente", dni=dni), 303)
    except ErrorValidacion as exc:
        errores = exc.errores
        try:
            exp = _cu("consultar_expediente").ejecutar(dni)
        except NinoNoEncontradoError:
            return render_template("errors/404.html", dni=dni), 404
        return render_template(
            "dosajes/nuevo.html", nino=exp.nino, errores=errores, datos=f,
            altitud_precargada=exp.nino.altitud_msnm,
        ), 422
    except NinoNoEncontradoError:
        return render_template("errors/404.html", dni=dni), 404


# ─── Reporte ──────────────────────────────────────────────────────────────────

@web_bp.get("/reportes/registros")
def reporte_registros():
    desde_str = request.args.get("desde", "")
    hasta_str = request.args.get("hasta", "")
    reporte = None
    errores: dict[str, list[str]] = {}

    if desde_str or hasta_str:
        try:
            desde = date.fromisoformat(desde_str)
        except ValueError:
            errores["desde"] = ["Fecha inválida"]
            desde = None
        try:
            hasta = date.fromisoformat(hasta_str)
        except ValueError:
            errores["hasta"] = ["Fecha inválida"]
            hasta = None

        if not errores:
            try:
                reporte = _cu("consultar_reporte").ejecutar(
                    PeriodoReporteDTO(desde=desde, hasta=hasta)
                )
            except ErrorValidacion as exc:
                errores = exc.errores

    return render_template(
        "reportes/registros.html",
        reporte=reporte, errores=errores,
        desde=desde_str, hasta=hasta_str,
    )
