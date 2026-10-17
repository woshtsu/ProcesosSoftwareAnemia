"""Adaptador de entrada HTTP (FastAPI). Traduce peticiones REST a casos de uso."""

import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse

from app.adapters.inbound.http import esquemas as s
from app.domain.model.agenda import ControlProgramado
from app.domain.model.alertas import AlertaControl
from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.errores import ErrorValidacion, NoEncontrado, RegistroDuplicado
from app.domain.model.tiempo import edad_en_meses
from app.ports.inbound.agenda import GenerarAgenda
from app.ports.inbound.alertas import ConsultarControlesVencidos
from app.ports.inbound.expediente import GestionarExpediente
from app.ports.inbound.reportes import GenerarReporte
from app.ports.inbound.seguimiento import ConsultarSeguimiento

router = APIRouter(prefix="/api")


# Las dependencias se tipan contra los puertos de entrada; main.py inyecta las implementaciones (ADR-008).
def expediente_uc(request: Request) -> GestionarExpediente:
    return request.app.state.expediente


def seguimiento_uc(request: Request) -> ConsultarSeguimiento:
    return request.app.state.seguimiento


def reporte_uc(request: Request) -> GenerarReporte:
    return request.app.state.reporte


def agenda_uc(request: Request) -> GenerarAgenda:
    return request.app.state.agenda


def alertas_uc(request: Request) -> ConsultarControlesVencidos:
    return request.app.state.alertas


def usuario_actual(x_usuario: str | None = Header(default=None, alias="X-Usuario")) -> str:
    # Autenticación real (roles por establecimiento) se incorpora en un incremento posterior.
    return (x_usuario or "personal.posta").strip()[:60]


def _eval(e: Evaluacion) -> s.EvaluacionSalida:
    return s.EvaluacionSalida(
        id=e.id,
        fecha=e.fecha,
        edad_meses=e.edad_meses,
        hemoglobina_observada=e.hemoglobina_observada,
        altitud_m=e.altitud_m,
        hemoglobina_ajustada=e.hemoglobina_ajustada,
        clasificacion=e.clasificacion.value,
        peso_kg=e.peso_kg,
        talla_cm=e.talla_cm,
        registrado_por=e.registrado_por,
    )


def _expediente(n: Nino, hoy: date) -> s.ExpedienteSalida:
    evaluaciones = sorted(n.evaluaciones, key=lambda e: (e.fecha, e.creado_en), reverse=True)
    return s.ExpedienteSalida(
        id=n.id,
        dni=n.dni,
        nombres=n.nombres,
        apellidos=n.apellidos,
        sexo=n.sexo,
        fecha_nacimiento=n.fecha_nacimiento,
        edad_meses=edad_en_meses(n.fecha_nacimiento, hoy),
        establecimiento=n.establecimiento,
        distrito=n.distrito,
        comunidad=n.comunidad,
        altitud_m=n.altitud_m,
        tutor_nombre=n.tutor_nombre,
        tutor_celular=n.tutor_celular,
        estado=n.estado,
        registrado_por=n.registrado_por,
        creado_en=n.creado_en,
        actualizado_en=n.actualizado_en,
        evaluaciones=[_eval(e) for e in evaluaciones],
    )


def _control(c: ControlProgramado) -> s.ControlSalida:
    return s.ControlSalida(
        codigo=c.codigo,
        tipo=c.tipo.value,
        descripcion=c.descripcion,
        fecha_programada=c.fecha_programada,
        fecha_inicio_ventana=c.fecha_inicio_ventana,
        fecha_limite=c.fecha_limite,
        estado=c.estado.value,
        proximo=c.proximo,
        dias_vencido=c.dias_vencido,
        evaluacion_id=c.evaluacion_id,
        edad_meses_programada=c.edad_meses_programada,
    )


def _alerta(a: AlertaControl) -> s.AlertaSalida:
    return s.AlertaSalida(
        nino=s.AlertaNino(
            id=a.nino_id,
            dni=a.dni,
            nombre_completo=a.nombre_completo,
            comunidad=a.comunidad,
            tutor_celular=a.tutor_celular,
        ),
        control=_control(a.control),
        ultima_clasificacion=a.ultima_clasificacion.value if a.ultima_clasificacion else None,
        prioridad=a.prioridad.value,
    )


MENSAJES_TIPO = {
    "missing": "Es obligatorio.",
    "float_parsing": "Debe ser un número.",
    "float_type": "Debe ser un número.",
    "int_parsing": "Debe ser un número entero.",
    "date_from_datetime_parsing": "Fecha inválida (use AAAA-MM-DD).",
    "date_parsing": "Fecha inválida (use AAAA-MM-DD).",
    "date_type": "Fecha inválida (use AAAA-MM-DD).",
    "string_type": "Debe ser texto.",
}


def registrar_manejadores(app) -> None:
    @app.exception_handler(RequestValidationError)
    async def _formato(_, exc: RequestValidationError):
        errores = []
        for err in exc.errors():
            ubicacion = [str(x) for x in err.get("loc", []) if x not in ("body", "query", "path")]
            campo = ubicacion[-1] if ubicacion else "solicitud"
            errores.append({"campo": campo, "mensaje": MENSAJES_TIPO.get(err.get("type"), "Valor inválido.")})
        return JSONResponse(status_code=422, content={"mensaje": "Revise los datos marcados.", "errores": errores})

    @app.exception_handler(ErrorValidacion)
    async def _validacion(_, exc: ErrorValidacion):
        return JSONResponse(
            status_code=422,
            content={
                "mensaje": "Revise los datos marcados.",
                "errores": [{"campo": e.campo, "mensaje": e.mensaje} for e in exc.errores],
            },
        )

    @app.exception_handler(RegistroDuplicado)
    async def _duplicado(_, exc: RegistroDuplicado):
        return JSONResponse(
            status_code=409, content={"mensaje": str(exc), "errores": [{"campo": "dni", "mensaje": str(exc)}]}
        )

    @app.exception_handler(NoEncontrado)
    async def _no_encontrado(_, exc: NoEncontrado):
        return JSONResponse(status_code=404, content={"mensaje": str(exc), "errores": []})


@router.get("/salud", tags=["Operación"])
def salud():
    return {"estado": "ok"}


@router.post(
    "/validaciones/evaluacion",
    response_model=s.EvaluacionSalida,
    tags=["HU-03 Validación"],
    responses={422: {"model": s.RespuestaError}},
)
def vista_previa(datos: s.VistaPreviaEntrada, svc: GestionarExpediente = Depends(expediente_uc)):
    """Calcula la Hb ajustada por altitud y la clasificación antes de guardar."""
    e = svc.previsualizar_evaluacion(datos.fecha_nacimiento, datos.altitud_m, datos.evaluacion.model_dump())
    return _eval(e)


@router.post(
    "/ninos",
    status_code=201,
    response_model=s.ExpedienteSalida,
    tags=["HU-01 Registro"],
    responses={409: {"model": s.RespuestaError}, 422: {"model": s.RespuestaError}},
)
def registrar(
    datos: s.RegistroNinoEntrada,
    svc: GestionarExpediente = Depends(expediente_uc),
    usuario: str = Depends(usuario_actual),
):
    nino = svc.registrar_nino(datos.nino.model_dump(), datos.evaluacion_inicial.model_dump(), usuario)
    return _expediente(nino, svc.fecha_actual())


@router.get("/ninos", response_model=list[s.FilaSeguimiento], tags=["HU-04 Seguimiento"])
def listar(
    estado: str | None = Query("ACTIVO"),
    q: str | None = None,
    clasificacion: str | None = None,
    svc: ConsultarSeguimiento = Depends(seguimiento_uc),
):
    filas = svc.listar_seguimiento(estado=estado or None, texto=q, clasificacion=clasificacion)
    return [
        s.FilaSeguimiento(
            id=f["nino"].id,
            dni=f["nino"].dni,
            nombre_completo=f["nino"].nombre_completo,
            edad_meses=f["edad_meses"],
            comunidad=f["nino"].comunidad,
            estado=f["nino"].estado,
            ultima_fecha_control=f["ultima_evaluacion"].fecha if f["ultima_evaluacion"] else None,
            ultima_hb_ajustada=f["ultima_evaluacion"].hemoglobina_ajustada if f["ultima_evaluacion"] else None,
            ultima_clasificacion=f["ultima_evaluacion"].clasificacion.value if f["ultima_evaluacion"] else None,
            dias_desde_ultimo_control=f["dias_desde_ultimo_control"],
            control_atrasado=f["control_atrasado"],
            controles_vencidos=f["controles_vencidos"],
        )
        for f in filas
    ]


@router.get("/ninos/dni/{dni}", response_model=s.ExpedienteSalida, tags=["HU-02 Expediente"])
def por_dni(dni: str, svc: GestionarExpediente = Depends(expediente_uc)):
    return _expediente(svc.consultar_por_dni(dni), svc.fecha_actual())


@router.get(
    "/ninos/{nino_id}",
    response_model=s.ExpedienteSalida,
    tags=["HU-02 Expediente"],
    responses={404: {"model": s.RespuestaError}},
)
def expediente(nino_id: str, svc: GestionarExpediente = Depends(expediente_uc)):
    return _expediente(svc.consultar(nino_id), svc.fecha_actual())


@router.patch("/ninos/{nino_id}", response_model=s.ExpedienteSalida, tags=["HU-02 Expediente"])
def actualizar(
    nino_id: str,
    cambios: s.ActualizacionNino,
    svc: GestionarExpediente = Depends(expediente_uc),
    usuario: str = Depends(usuario_actual),
):
    nino = svc.actualizar_datos(nino_id, cambios.model_dump(exclude_unset=True), usuario)
    return _expediente(nino, svc.fecha_actual())


@router.post(
    "/ninos/{nino_id}/evaluaciones", status_code=201, response_model=s.ExpedienteSalida, tags=["HU-02 Expediente"]
)
def nueva_evaluacion(
    nino_id: str,
    datos: s.EvaluacionEntrada,
    svc: GestionarExpediente = Depends(expediente_uc),
    usuario: str = Depends(usuario_actual),
):
    nino = svc.registrar_evaluacion(nino_id, datos.model_dump(), usuario)
    return _expediente(nino, svc.fecha_actual())


@router.get(
    "/ninos/{nino_id}/agenda",
    response_model=s.AgendaSalida,
    tags=["HIST-2.1 Agenda"],
    responses={404: {"model": s.RespuestaError}},
)
def agenda(nino_id: str, svc: GenerarAgenda = Depends(agenda_uc)):
    """Agenda de controles del niño según el esquema normativo (calculada en línea, sin tabla propia)."""
    ag = svc.generar_agenda(nino_id)
    r = ag.resumen
    return s.AgendaSalida(
        nino_id=ag.nino_id,
        version_esquema=ag.version_esquema,
        fecha_referencia=ag.fecha_referencia,
        aplica=ag.aplica,
        motivo=ag.motivo,
        resumen=s.ResumenAgendaSalida(
            total=r.total,
            cumplidos=r.cumplidos,
            pendientes=r.pendientes,
            vencidos=r.vencidos,
            cerrados=r.cerrados,
            proximos=r.proximos,
            proximo_control=_control(r.proximo_control) if r.proximo_control else None,
        ),
        controles=[_control(c) for c in ag.controles],
    )


@router.get(
    "/alertas/controles-vencidos",
    response_model=list[s.AlertaSalida],
    tags=["HIST-2.2 Alertas"],
    responses={422: {"model": s.RespuestaError}},
)
def controles_vencidos(
    comunidad: str | None = None, prioridad: str | None = None, svc: ConsultarControlesVencidos = Depends(alertas_uc)
):
    """Controles vencidos de niños activos, ordenados por prioridad y días de atraso."""
    return [_alerta(a) for a in svc.listar_controles_vencidos(comunidad=comunidad, prioridad=prioridad)]


@router.get("/alertas/resumen", response_model=s.ResumenAlertasSalida, tags=["HIST-2.2 Alertas"])
def resumen_alertas(svc: ConsultarControlesVencidos = Depends(alertas_uc)):
    r = svc.resumen_alertas()
    return s.ResumenAlertasSalida(
        total_vencidos=r.total_vencidos,
        por_prioridad=r.por_prioridad,
        ninos_con_vencidos=r.ninos_con_vencidos,
        proximos_7_dias=r.proximos_7_dias,
    )


@router.get("/reportes/periodo", response_model=s.ReportePeriodo, tags=["HU-05 Reporte"])
def reporte(desde: date, hasta: date, formato: str = "json", svc: GenerarReporte = Depends(reporte_uc)):
    datos = svc.reporte_periodo(desde, hasta)
    if formato == "csv":
        buffer = io.StringIO()
        w = csv.writer(buffer)
        w.writerow(
            [
                "fecha",
                "dni",
                "nino",
                "comunidad",
                "edad_meses",
                "hb_observada",
                "altitud_m",
                "hb_ajustada",
                "clasificacion",
                "peso_kg",
                "talla_cm",
                "registrado_por",
            ]
        )
        for e in datos["evaluaciones"]:
            n = datos["ninos"][e.nino_id]
            w.writerow(
                [
                    e.fecha,
                    n.dni,
                    n.nombre_completo,
                    n.comunidad,
                    e.edad_meses,
                    e.hemoglobina_observada,
                    e.altitud_m,
                    e.hemoglobina_ajustada,
                    e.clasificacion.value,
                    e.peso_kg,
                    e.talla_cm,
                    e.registrado_por,
                ]
            )
        nombre = f"reporte_anemia_{desde}_{hasta}.csv"
        return StreamingResponse(
            iter(["﻿" + buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
        )
    return s.ReportePeriodo(**{k: v for k, v in datos.items() if k not in ("evaluaciones", "ninos")})
