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
from anemia_junin.domain.entities import Sexo, TipoNacimiento
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


@web_bp.post("/ninos/nuevo")
def nuevo_nino_post():
    f = request.form

    # Parsear peso
    err_peso, peso_g = validar_peso_kg(f.get("peso_kg", ""))
    # Parsear dosaje inicial
    dosaje_inicial = None
    errores_dosaje: dict[str, list[str]] = {}
    if f.get("tiene_dosaje_inicial") == "1":
        err_hb, hb_ddl = validar_hb_gdl(f.get("hb_observada", "")), 0
        if isinstance(err_hb, list):
            errores_dosaje["hb_observada"] = err_hb
        else:
            hb_ddl = err_hb
        try:
            fecha_d = date.fromisoformat(f.get("fecha_dosaje", ""))
        except ValueError:
            errores_dosaje["fecha_dosaje"] = ["Fecha inválida"]
            fecha_d = date.today()
        if not errores_dosaje:
            dosaje_inicial = DosajeInicialDTO(
                fecha_dosaje=fecha_d,
                hb_observada_ddl=hb_ddl,
            )

    try:
        sexo = Sexo(f.get("sexo", ""))
    except ValueError:
        sexo = Sexo.F

    try:
        tipo_nac = TipoNacimiento(f.get("tipo_nacimiento", ""))
    except ValueError:
        tipo_nac = TipoNacimiento.TERMINO

    try:
        fecha_nac = date.fromisoformat(f.get("fecha_nacimiento", ""))
    except ValueError:
        fecha_nac = date.today()

    dto = CrearNinoDTO(
        dni=f.get("dni", ""),
        nombres=f.get("nombres", ""),
        apellidos=f.get("apellidos", ""),
        fecha_nacimiento=fecha_nac,
        sexo=sexo,
        tipo_nacimiento=tipo_nac,
        peso_g=peso_g,
        distrito=f.get("distrito", ""),
        altitud_msnm=int(f.get("altitud_msnm", 0) or 0),
        cuidador=f.get("cuidador", ""),
        telefono=f.get("telefono") or None,
        dosaje_inicial=dosaje_inicial,
    )

    try:
        nino_dto, _ = _cu("registrar_nino").ejecutar(dto)
        return redirect(url_for("web.expediente", dni=nino_dto.dni), 303)
    except ErrorValidacion as exc:
        errores = {**exc.errores, **errores_dosaje}
        return render_template("ninos/nuevo.html", errores=errores, datos=f), 422
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

    dto = ActualizarNinoDTO(
        peso_g=peso_g if f.get("peso_kg") else None,
        distrito=f.get("distrito") or None,
        altitud_msnm=int(f.get("altitud_msnm")) if f.get("altitud_msnm") else None,
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
        return render_template("ninos/editar.html", nino=exp.nino, errores=exc.errores, datos=f), 422
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

    try:
        fecha_d = date.fromisoformat(f.get("fecha_dosaje", ""))
    except ValueError:
        fecha_d = date.today()

    dto = CrearDosajeDTO(
        fecha_dosaje=fecha_d,
        hb_observada_ddl=hb_ddl,
        altitud_msnm=int(f.get("altitud_msnm", 0) or 0),
    )

    try:
        _cu("agregar_dosaje").ejecutar(dni, dto)
        return redirect(url_for("web.expediente", dni=dni), 303)
    except ErrorValidacion as exc:
        errores = exc.errores
        if err_hb:
            errores["hb_observada"] = err_hb
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
            desde = date.today()
        try:
            hasta = date.fromisoformat(hasta_str)
        except ValueError:
            errores["hasta"] = ["Fecha inválida"]
            hasta = date.today()

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
