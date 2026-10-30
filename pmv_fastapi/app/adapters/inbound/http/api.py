"""Adaptador de entrada HTTP (FastAPI). Traduce peticiones REST a casos de uso."""

import csv
import io
from collections import Counter
from datetime import date

from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse

from app.adapters.inbound.http import esquemas as s
from app.domain.model.agenda import ControlProgramado
from app.domain.model.agenda_personal import AgendaPersonal, ItemAgendaPersonal
from app.domain.model.alertas import AlertaControl
from app.domain.model.asistencia import AsistenciaControl
from app.domain.model.barrera import AlertaBarrera, Barrera
from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.errores import (
    ConflictoAsistencia,
    ConflictoBarrera,
    ConflictoRespuesta,
    ConflictoVisita,
    ConflictoYaResuelto,
    ErrorValidacion,
    FirmaInvalida,
    NoEncontrado,
    RegistroDuplicado,
    WebhookNoConfigurado,
)
from app.domain.model.notificacion import VistaRecordatorio
from app.domain.model.sincronizacion import (
    ConflictoSincronizacion,
    OperacionEntrante,
    ResultadoOperacion,
    ResultadoSincronizacion,
)
from app.domain.model.tiempo import edad_en_meses
from app.domain.model.visita import LIMITE_PREDETERMINADO, NinoPriorizado, VisitaDomiciliaria
from app.ports.inbound.agenda import GenerarAgenda
from app.ports.inbound.agenda_personal import ConsultarAgendaPersonal
from app.ports.inbound.alertas import ConsultarControlesVencidos
from app.ports.inbound.asistencia import RegistrarAsistencia
from app.ports.inbound.barreras import ConsultarAlertasBarreras, GestionarBarreras
from app.ports.inbound.contexto import ConsultarContexto
from app.ports.inbound.expediente import GestionarExpediente
from app.ports.inbound.notificaciones import (
    ConsultarRecordatorios,
    GenerarRecordatorios,
    ProcesarNotificacionesWhatsApp,
    RegistrarRespuestaRecordatorio,
)
from app.ports.inbound.reportes import GenerarReporte
from app.ports.inbound.seguimiento import ConsultarSeguimiento
from app.ports.inbound.sincronizacion import GestionarConflictos, SincronizarOperaciones
from app.ports.inbound.visitas import ConsultarVisitasPriorizadas, GestionarVisitas

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


def agenda_personal_uc(request: Request) -> ConsultarAgendaPersonal:
    return request.app.state.agenda_personal


def asistencia_uc(request: Request) -> RegistrarAsistencia:
    return request.app.state.asistencia


def contexto_uc(request: Request) -> ConsultarContexto:
    return request.app.state.contexto


def visitas_uc(request: Request) -> GestionarVisitas:
    return request.app.state.visitas


def priorizadas_uc(request: Request) -> ConsultarVisitasPriorizadas:
    return request.app.state.visitas


def sincronizacion_uc(request: Request) -> SincronizarOperaciones:
    return request.app.state.sincronizacion


def conflictos_uc(request: Request) -> GestionarConflictos:
    return request.app.state.sincronizacion


def barreras_uc(request: Request) -> GestionarBarreras:
    return request.app.state.barreras


def alertas_barreras_uc(request: Request) -> ConsultarAlertasBarreras:
    return request.app.state.barreras


def generar_recordatorios_uc(request: Request) -> GenerarRecordatorios:
    return request.app.state.recordatorios


def recordatorios_uc(request: Request) -> ConsultarRecordatorios:
    return request.app.state.recordatorios


def respuesta_uc(request: Request) -> RegistrarRespuestaRecordatorio:
    return request.app.state.recordatorios


def webhook_uc(request: Request) -> ProcesarNotificacionesWhatsApp:
    return request.app.state.recordatorios


def usuario_actual(request: Request, x_usuario: str | None = Header(default=None, alias="X-Usuario")) -> str:
    if request.app.state.auth_mode == "supabase":
        return request.state.usuario.id
    # Solo en el modo demo explícito se admite el selector de identidad sintética.
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
        clasificacion_origen=e.clasificacion_origen,
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
        nombre_completo=n.nombre_completo,
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
        origen=n.origen.value,
        codigo_origen=n.codigo_origen,
        red=n.red,
        microred=n.microred,
        provincia=n.provincia,
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
        inasistencia_registrada=c.inasistencia_registrada,
        motivo_inasistencia=c.motivo_inasistencia,
        cumplido_por_asistencia=c.cumplido_por_asistencia,
    )


def _alerta(a: AlertaControl) -> s.AlertaSalida:
    return s.AlertaSalida(
        nino=s.AlertaNino(
            id=a.nino_id,
            dni=a.dni,
            codigo_origen=a.codigo_origen,
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
    "string_pattern_mismatch": "Formato inválido.",
    "too_long": "Supera el largo o la cantidad máxima permitida.",
    "too_short": "No alcanza el largo o la cantidad mínima requerida.",
}


async def _webhook_rechazado(_, exc: Exception):
    """Webhook de WhatsApp: 403 si la firma falta o es inválida; 503 (falla cerrado) si no hay secreto configurado."""
    estado = 503 if isinstance(exc, WebhookNoConfigurado) else 403
    return JSONResponse(status_code=estado, content={"mensaje": str(exc), "errores": []})


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

    @app.exception_handler(ConflictoAsistencia)
    async def _conflicto_asistencia(_, exc: ConflictoAsistencia):
        return JSONResponse(
            status_code=409, content={"mensaje": str(exc), "errores": [{"campo": "codigo", "mensaje": str(exc)}]}
        )

    @app.exception_handler(ConflictoVisita)
    async def _conflicto_visita(_, exc: ConflictoVisita):
        return JSONResponse(
            status_code=409, content={"mensaje": str(exc), "errores": [{"campo": "fecha", "mensaje": str(exc)}]}
        )

    @app.exception_handler(ConflictoYaResuelto)
    async def _conflicto_resuelto(_, exc: ConflictoYaResuelto):
        return JSONResponse(
            status_code=409, content={"mensaje": str(exc), "errores": [{"campo": "estado", "mensaje": str(exc)}]}
        )

    @app.exception_handler(ConflictoBarrera)
    async def _conflicto_barrera(_, exc: ConflictoBarrera):
        return JSONResponse(
            status_code=409, content={"mensaje": str(exc), "errores": [{"campo": "tipo", "mensaje": str(exc)}]}
        )

    @app.exception_handler(ConflictoRespuesta)
    async def _conflicto_respuesta(_, exc: ConflictoRespuesta):
        return JSONResponse(
            status_code=409, content={"mensaje": str(exc), "errores": [{"campo": "respuesta", "mensaje": str(exc)}]}
        )

    app.add_exception_handler(FirmaInvalida, _webhook_rechazado)
    app.add_exception_handler(WebhookNoConfigurado, _webhook_rechazado)

    @app.exception_handler(NoEncontrado)
    async def _no_encontrado(_, exc: NoEncontrado):
        return JSONResponse(status_code=404, content={"mensaje": str(exc), "errores": []})


@router.get("/salud", response_model=s.SaludSalida, tags=["Operación"])
def salud(svc: ConsultarContexto = Depends(contexto_uc)):
    """Estado del servicio y fecha de hoy; ``fecha_referencia`` solo si se fijó FECHA_REFERENCIA (demo con dataset)."""
    c = svc.contexto()
    return s.SaludSalida(estado="ok", fecha_hoy=c.fecha_hoy, fecha_referencia=c.fecha_referencia)


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
            codigo_origen=f["nino"].codigo_origen,
            origen=f["nino"].origen.value,
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
            inasistencias=r.inasistencias,
            proximo_control=_control(r.proximo_control) if r.proximo_control else None,
        ),
        controles=[_control(c) for c in ag.controles],
    )


def _asistencia(a: AsistenciaControl) -> s.AsistenciaSalida:
    return s.AsistenciaSalida(
        id=a.id,
        nino_id=a.nino_id,
        codigo_control=a.codigo_control,
        fecha_programada=a.fecha_programada,
        estado=a.estado.value,
        motivo=a.motivo,
        evaluacion_id=a.evaluacion_id,
        registrado_por=a.registrado_por,
        creado_en=a.creado_en,
    )


@router.post(
    "/ninos/{nino_id}/controles/{codigo}/asistencia",
    status_code=201,
    response_model=s.AsistenciaSalida,
    tags=["HIST-2.4 Asistencia"],
    responses={404: {"model": s.RespuestaError}, 409: {"model": s.RespuestaError}, 422: {"model": s.RespuestaError}},
)
def registrar_asistencia(
    nino_id: str,
    codigo: str,
    datos: s.AsistenciaEntrada,
    svc: RegistrarAsistencia = Depends(asistencia_uc),
    usuario: str = Depends(usuario_actual),
):
    """Registra que el niño asistió (con la evaluación del día, opcional) o no asistió (con motivo) a un control.

    409 si el control ya tiene una asistencia o ya está cumplido; 422 si la fecha programada es futura o faltan datos.
    """
    return _asistencia(svc.registrar_asistencia(nino_id, codigo, datos.model_dump(), usuario))


@router.get(
    "/ninos/{nino_id}/asistencias",
    response_model=list[s.AsistenciaSalida],
    tags=["HIST-2.4 Asistencia"],
    responses={404: {"model": s.RespuestaError}},
)
def asistencias(nino_id: str, svc: RegistrarAsistencia = Depends(asistencia_uc)):
    """Asistencias e inasistencias registradas para los controles del niño, por fecha programada."""
    return [_asistencia(a) for a in svc.listar_asistencias(nino_id)]


def _visita(v: VisitaDomiciliaria) -> s.VisitaSalida:
    return s.VisitaSalida(
        id=v.id,
        nino_id=v.nino_id,
        fecha=v.fecha,
        resultado=v.resultado.value,
        consume_suplemento=v.consume_suplemento.value,
        observaciones=v.observaciones,
        registrado_por=v.registrado_por,
        creado_en=v.creado_en,
    )


@router.post(
    "/ninos/{nino_id}/visitas",
    status_code=201,
    response_model=s.VisitaSalida,
    tags=["VIS-3.5 Visitas"],
    responses={404: {"model": s.RespuestaError}, 409: {"model": s.RespuestaError}, 422: {"model": s.RespuestaError}},
)
def registrar_visita(
    nino_id: str,
    datos: s.VisitaEntrada,
    svc: GestionarVisitas = Depends(visitas_uc),
    usuario: str = Depends(usuario_actual),
):
    """Registra una visita domiciliaria (una por niño y por día; ``registrado_por`` sale de la sesión).

    409 si el niño ya tiene una visita ese día; 422 si la fecha es futura, el resultado o el consumo del suplemento
    son inválidos (solo una visita REALIZADA puede indicar SI o NO) o las observaciones superan 500 caracteres.
    """
    return _visita(svc.registrar_visita(nino_id, datos.model_dump(), usuario))


@router.get(
    "/ninos/{nino_id}/visitas",
    response_model=list[s.VisitaSalida],
    tags=["VIS-3.5 Visitas"],
    responses={404: {"model": s.RespuestaError}},
)
def visitas_del_nino(nino_id: str, svc: GestionarVisitas = Depends(visitas_uc)):
    """Visitas domiciliarias del niño, la más reciente primero."""
    return [_visita(v) for v in svc.listar_visitas(nino_id)]


def _priorizado(posicion: int, p: NinoPriorizado) -> s.VisitaPriorizadaSalida:
    return s.VisitaPriorizadaSalida(
        posicion=posicion,
        nino=s.NinoVisitaSalida(
            id=p.nino_id,
            dni=p.dni,
            codigo_origen=p.codigo_origen,
            nombre_completo=p.nombre_completo,
            comunidad=p.comunidad,
        ),
        establecimiento=p.establecimiento,
        ultima_clasificacion=p.ultima_clasificacion.value,
        dias_control_vencido=p.dias_control_vencido,
        inasistencias_recientes=p.inasistencias_recientes,
        ultima_visita=p.ultima_visita,
        dias_desde_ultima_visita=p.dias_desde_ultima_visita,
        puntaje=p.puntaje,
        componentes=[s.ComponentePuntajeSalida(**vars(c)) for c in p.componentes],
    )


@router.get(
    "/visitas/priorizadas",
    response_model=list[s.VisitaPriorizadaSalida],
    tags=["VIS-3.5 Visitas"],
    responses={422: {"model": s.RespuestaError}},
)
def visitas_priorizadas(
    establecimiento: str | None = None,
    limite: int = Query(LIMITE_PREDETERMINADO, description="De 1 a 200"),
    svc: ConsultarVisitasPriorizadas = Depends(priorizadas_uc),
):
    """Niños en tratamiento ordenados por un puntaje explicable (0 a 100) para planificar las visitas domiciliarias.

    Componentes: severidad de la última evaluación, días del control más vencido, inasistencias de los últimos 90 días
    y días desde la última visita; los niños con barreras críticas (HIST-4.4) suman además el componente
    BARRERA_CRITICA (hasta 15 puntos). Los pesos son una propuesta del equipo (ADR-013), no una norma del MINSA.
    """
    return [_priorizado(i, p) for i, p in enumerate(svc.visitas_priorizadas(establecimiento, limite), start=1)]


def _resultado_operacion(r: ResultadoSincronizacion) -> s.ResultadoOperacionSalida:
    return s.ResultadoOperacionSalida(
        id_operacion=r.id_operacion,
        tipo=r.tipo,
        resultado=r.resultado.value,
        id_recurso=r.id_recurso,
        id_cliente=r.id_cliente,
        id_conflicto=r.id_conflicto,
        mensaje=r.mensaje,
        errores=[s.ErrorDetalle(campo=e.campo, mensaje=e.mensaje) for e in r.errores],
        resultado_original=r.resultado_original.value if r.resultado_original else None,
    )


@router.post(
    "/sincronizacion",
    response_model=s.SincronizacionSalida,
    tags=["HIST-3.2 Sincronización"],
    responses={422: {"model": s.RespuestaError}},
)
def sincronizar(
    lote: s.LoteSincronizacionEntrada,
    svc: SincronizarOperaciones = Depends(sincronizacion_uc),
    usuario: str = Depends(usuario_actual),
):
    """Aplica un lote (1 a 200) de operaciones registradas sin conexión, ordenadas por fecha local.

    Devuelve un resultado por operación, en el orden recibido: APLICADA (con el id del servidor y el mapeo
    id_cliente -> id), DUPLICADA (el ``id_operacion`` ya se procesó o el servidor ya tiene el mismo dato), CONFLICTO (el
    servidor tiene un dato distinto; queda pendiente de resolver) o RECHAZADA (error de validación del dominio, sin
    efecto). Reenviar el mismo lote no crea nada nuevo.
    """
    operaciones = [
        OperacionEntrante(
            id_operacion=o.id_operacion,
            tipo=o.tipo,
            id_dispositivo=o.id_dispositivo,
            fecha_local=o.fecha_local,
            datos=o.datos,
            id_cliente=o.id_cliente,
            nino_id=o.nino_ref.id if o.nino_ref else None,
            nino_id_cliente=o.nino_ref.id_cliente if o.nino_ref else None,
        )
        for o in lote.operaciones
    ]
    resultados = svc.sincronizar(operaciones, usuario)
    cuenta = Counter(r.resultado for r in resultados)
    return s.SincronizacionSalida(
        resumen=s.ResumenSincronizacionSalida(
            aplicadas=cuenta[ResultadoOperacion.APLICADA],
            duplicadas=cuenta[ResultadoOperacion.DUPLICADA],
            conflictos=cuenta[ResultadoOperacion.CONFLICTO],
            rechazadas=cuenta[ResultadoOperacion.RECHAZADA],
        ),
        resultados=[_resultado_operacion(r) for r in resultados],
    )


def _conflicto(c: ConflictoSincronizacion) -> s.ConflictoSalida:
    return s.ConflictoSalida(**{**vars(c), "estado": c.estado.value, "resolucion": c.resolucion and c.resolucion.value})


@router.get(
    "/sincronizacion/conflictos",
    response_model=list[s.ConflictoSalida],
    tags=["HIST-3.3 Conflictos"],
    responses={422: {"model": s.RespuestaError}},
)
def conflictos(estado: str | None = None, svc: GestionarConflictos = Depends(conflictos_uc)):
    """Conflictos de sincronización (el más antiguo primero); ``estado`` = PENDIENTE o RESUELTO."""
    return [_conflicto(c) for c in svc.listar_conflictos(estado)]


@router.post(
    "/sincronizacion/conflictos/{conflicto_id}/resolver",
    response_model=s.ConflictoSalida,
    tags=["HIST-3.3 Conflictos"],
    responses={404: {"model": s.RespuestaError}, 409: {"model": s.RespuestaError}, 422: {"model": s.RespuestaError}},
)
def resolver_conflicto(
    conflicto_id: str,
    datos: s.ResolucionEntrada,
    svc: GestionarConflictos = Depends(conflictos_uc),
    usuario: str = Depends(usuario_actual),
):
    """Resuelve un conflicto. CONSERVAR_SERVIDOR: el dato del servidor gana (solo se agrega lo que no existía).
    APLICAR_CLIENTE: el dato del dispositivo reemplaza al del servidor solo donde el dominio lo permite (campos
    editables del niño, la hemoglobina de una evaluación, una visita o una asistencia sin evaluación que la respalde;
    nunca los datos de identidad del niño: 422). DESCARTAR: se ignora la operación. 409 si ya estaba resuelto."""
    return _conflicto(svc.resolver_conflicto(conflicto_id, datos.resolucion, usuario))


def _item_personal(i: ItemAgendaPersonal) -> s.ItemAgendaPersonalSalida:
    return s.ItemAgendaPersonalSalida(
        nino=s.ItemAgendaNino(
            id=i.nino_id,
            codigo_origen=i.codigo_origen,
            dni=i.dni,
            nombre_completo=i.nombre_completo,
            establecimiento=i.establecimiento,
            comunidad=i.comunidad,
        ),
        control=_control(i.control),
        prioridad=i.prioridad.value if i.prioridad else None,
    )


def _agenda_personal(a: AgendaPersonal) -> s.AgendaPersonalSalida:
    return s.AgendaPersonalSalida(
        desde=a.desde,
        hasta=a.hasta,
        fecha_referencia=a.fecha_referencia,
        establecimiento=a.establecimiento,
        comunidad=a.comunidad,
        resumen=s.ResumenAgendaPersonalSalida(**vars(a.resumen)),
        dias=[
            s.DiaAgendaSalida(
                fecha=d.fecha,
                total=d.total,
                cumplidos=d.cumplidos,
                pendientes=d.pendientes,
                vencidos=d.vencidos,
                con_inasistencia=d.con_inasistencia,
                items=[_item_personal(i) for i in d.items],
            )
            for d in a.dias
        ],
        establecimientos_disponibles=a.establecimientos_disponibles,
        comunidades_disponibles=a.comunidades_disponibles,
    )


@router.get(
    "/agenda",
    response_model=s.AgendaPersonalSalida,
    tags=["HIST-2.3 Agenda del personal"],
    responses={422: {"model": s.RespuestaError}},
)
def agenda_del_personal(
    desde: date | None = None,
    hasta: date | None = None,
    establecimiento: str | None = None,
    comunidad: str | None = None,
    svc: ConsultarAgendaPersonal = Depends(agenda_personal_uc),
):
    """Controles programados por día en un rango de hasta 31 días (por defecto, la semana de la fecha de referencia).

    Incluye cumplidos, pendientes y vencidos (con su prioridad); filtrable por establecimiento y comunidad.
    """
    return _agenda_personal(svc.agenda_personal(desde, hasta, establecimiento, comunidad))


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


# --- INC-4: barreras (HIST-4.3 y HIST-4.4) --------------------------------------------------------------------------


def _barrera(b: Barrera) -> s.BarreraSalida:
    return s.BarreraSalida(
        id=b.id,
        nino_id=b.nino_id,
        tipo=b.tipo.value,
        detalle=b.detalle,
        fuente=b.fuente.value,
        fecha=b.fecha,
        recordatorio_id=b.recordatorio_id,
        registrado_por=b.registrado_por,
        creado_en=b.creado_en,
    )


@router.post(
    "/ninos/{nino_id}/barreras",
    status_code=201,
    response_model=s.BarreraSalida,
    tags=["HIST-4.3 Barreras"],
    responses={404: {"model": s.RespuestaError}, 409: {"model": s.RespuestaError}, 422: {"model": s.RespuestaError}},
)
def registrar_barrera(
    nino_id: str,
    datos: s.BarreraEntrada,
    svc: GestionarBarreras = Depends(barreras_uc),
    usuario: str = Depends(usuario_actual),
):
    """Registra una barrera de acceso al tratamiento (catálogo de 8 tipos; con OTRA el detalle es obligatorio).

    La fuente indica de dónde sale: PERSONAL, RESPUESTA_RECORDATORIO, INASISTENCIA o VISITA. 409 si el niño ya tiene
    esa barrera (mismo tipo, fecha y fuente); 422 si el tipo o la fuente son inválidos, falta el detalle o la fecha es
    futura.
    """
    return _barrera(svc.registrar_barrera(nino_id, datos.model_dump(), usuario))


@router.get(
    "/ninos/{nino_id}/barreras",
    response_model=list[s.BarreraSalida],
    tags=["HIST-4.3 Barreras"],
    responses={404: {"model": s.RespuestaError}},
)
def barreras_del_nino(nino_id: str, svc: GestionarBarreras = Depends(barreras_uc)):
    """Barreras registradas del niño, la más reciente primero (se muestran en su expediente)."""
    return [_barrera(b) for b in svc.listar_barreras(nino_id)]


def _alerta_barrera(a: AlertaBarrera) -> s.AlertaBarreraSalida:
    return s.AlertaBarreraSalida(
        nino=s.AlertaBarreraNino(
            id=a.nino_id,
            dni=a.dni,
            codigo_origen=a.codigo_origen,
            nombre_completo=a.nombre_completo,
            comunidad=a.comunidad,
            establecimiento=a.establecimiento,
            tutor_celular=a.tutor_celular,
        ),
        prioridad=a.prioridad.value,
        razones=[s.RazonBarreraSalida(codigo=r.codigo.value, descripcion=r.descripcion) for r in a.razones],
        ultima_clasificacion=a.ultima_clasificacion.value if a.ultima_clasificacion else None,
        dias_control_vencido=a.dias_control_vencido,
        barreras=[_barrera(b) for b in a.barreras],
    )


@router.get(
    "/alertas/barreras",
    response_model=list[s.AlertaBarreraSalida],
    tags=["HIST-4.4 Alertas de barreras"],
    responses={422: {"model": s.RespuestaError}},
)
def alertas_de_barreras(
    comunidad: str | None = None,
    prioridad: str | None = None,
    svc: ConsultarAlertasBarreras = Depends(alertas_barreras_uc),
):
    """Niños con barreras críticas, por prioridad, con la razón de cada alerta.

    Es crítica una barrera de RECHAZO_TRATAMIENTO o EFECTOS_ADVERSOS_SUPLEMENTO; o dos o más barreras distintas en
    60 días; o cualquier barrera vigente (90 días) con anemia moderada o severa y un control vencido.
    """
    return [_alerta_barrera(a) for a in svc.alertas_barreras(comunidad=comunidad, prioridad=prioridad)]


# --- INC-4: recordatorios y respuesta del tutor (HIST-4.1 y HIST-4.2) ------------------------------------------------


def _recordatorio(v: VistaRecordatorio) -> s.RecordatorioSalida:
    r = v.recordatorio
    return s.RecordatorioSalida(
        id=r.id,
        nino=s.RecordatorioNino(
            id=r.nino_id,
            nombre_completo=v.nombre_nino,
            codigo_origen=v.codigo_origen,
            comunidad=v.comunidad,
            establecimiento=v.establecimiento,
        ),
        codigo_control=r.codigo_control,
        fecha_programada=r.fecha_programada,
        tipo=r.tipo.value,
        canal=r.canal.value,
        simulado=r.simulado,
        estado=r.estado.value,
        destino=f"*****{r.destino[-4:]}",
        mensaje=r.mensaje,
        detalle=r.detalle,
        intentos=r.intentos,
        creado_en=r.creado_en,
        enviado_en=r.enviado_en,
        respuesta=r.respuesta.value if r.respuesta else None,
        fecha_reprogramada=r.fecha_reprogramada,
        respondido_en=r.respondido_en,
        respondido_por=r.respondido_por,
        origen_respuesta=r.origen_respuesta.value if r.origen_respuesta else None,
    )


@router.post(
    "/recordatorios/generar",
    response_model=s.GeneracionSalida,
    tags=["HIST-4.1 Recordatorios"],
)
def generar_recordatorios(
    datos: s.GenerarRecordatoriosEntrada | None = None,
    svc: GenerarRecordatorios = Depends(generar_recordatorios_uc),
    usuario: str = Depends(usuario_actual),
):
    """Genera y envía el lote de recordatorios del día (controles próximos, de hoy y vencidos).

    Es idempotente: un recordatorio es único por niño, control y tipo, así que repetir la generación no repite
    mensajes. Devuelve enviados, fallidos y omitidos («sin contacto» y «ya enviado»). Los niños del dataset no tienen
    celular y se cuentan como «sin contacto». Con el notificador simulado (por defecto) no sale ningún mensaje real.
    """
    r = svc.generar_recordatorios(usuario, datos.establecimiento if datos else None)
    return s.GeneracionSalida(
        fecha=r.fecha,
        candidatos=r.candidatos,
        enviados=r.enviados,
        fallidos=r.fallidos,
        omitidos_sin_contacto=r.omitidos_sin_contacto,
        omitidos_ya_enviado=r.omitidos_ya_enviado,
        recordatorios=[_recordatorio(v) for v in r.recordatorios],
    )


@router.get(
    "/recordatorios",
    response_model=list[s.RecordatorioSalida],
    tags=["HIST-4.1 Recordatorios"],
    responses={422: {"model": s.RespuestaError}},
)
def listar_recordatorios(
    estado: str | None = None,
    desde: date | None = None,
    nino_id: str | None = None,
    limite: int = Query(200, description="De 1 a 1000"),
    svc: ConsultarRecordatorios = Depends(recordatorios_uc),
):
    """Recordatorios generados (el más reciente primero); filtrables por estado, por fecha de generación y por niño."""
    return [
        _recordatorio(v) for v in svc.listar_recordatorios(estado=estado, desde=desde, nino_id=nino_id, limite=limite)
    ]


@router.get(
    "/recordatorios/metricas",
    response_model=s.MetricasRecordatoriosSalida,
    tags=["HIST-4.1 Recordatorios"],
    responses={422: {"model": s.RespuestaError}},
)
def metricas_recordatorios(
    desde: date | None = None, hasta: date | None = None, svc: ConsultarRecordatorios = Depends(recordatorios_uc)
):
    """Métricas de entrega de mensajes (hito H4): tasas de envío, entrega y confirmación, en total y por canal.

    Las tasas son proporciones de 0 a 1. La tasa de entrega usa solo los envíos reales: los simulados no se entregan.
    """
    m = svc.metricas_recordatorios(desde, hasta)
    return s.MetricasRecordatoriosSalida(
        **{**vars(m), "por_canal": [s.MetricasCanalSalida(**vars(c)) for c in m.por_canal]}
    )


@router.post(
    "/recordatorios/{recordatorio_id}/respuesta",
    response_model=s.RespuestaSalida,
    tags=["HIST-4.2 Respuestas"],
    responses={404: {"model": s.RespuestaError}, 409: {"model": s.RespuestaError}, 422: {"model": s.RespuestaError}},
)
def responder_recordatorio(
    recordatorio_id: str,
    datos: s.RespuestaEntrada,
    svc: RegistrarRespuestaRecordatorio = Depends(respuesta_uc),
    usuario: str = Depends(usuario_actual),
):
    """El personal registra la respuesta del tutor: CONFIRMA, NO_PUEDE o REPROGRAMAR (con fecha, hasta 90 días).

    Con NO_PUEDE puede indicar la barrera (tipo y detalle): se registra con la fuente RESPUESTA_RECORDATORIO; si no la
    indica, ``barrera_sugerida`` es verdadero. 409 si el recordatorio ya tiene respuesta; 422 si los datos no son
    válidos.
    """
    r = svc.registrar_respuesta(recordatorio_id, datos.model_dump(), usuario)
    return s.RespuestaSalida(
        recordatorio=_recordatorio(r.recordatorio), barrera_id=r.barrera_id, barrera_sugerida=r.barrera_sugerida
    )


@router.get("/notificaciones/whatsapp/webhook", tags=["HIST-4.2 Respuestas"], response_class=PlainTextResponse)
def verificar_webhook(
    modo: str | None = Query(None, alias="hub.mode"),
    token: str | None = Query(None, alias="hub.verify_token"),
    desafio: str | None = Query(None, alias="hub.challenge"),
    svc: ProcesarNotificacionesWhatsApp = Depends(webhook_uc),
):
    """Verificación del webhook que hace Meta al registrarlo: devuelve ``hub.challenge`` si el token es el configurado
    en ``WHATSAPP_VERIFY_TOKEN``; 403 en otro caso. Público: no usa la sesión del personal."""
    if desafio is None or not svc.verificar_suscripcion(modo, token):
        return JSONResponse(status_code=403, content={"mensaje": "Verificación rechazada.", "errores": []})
    return PlainTextResponse(desafio)


@router.post(
    "/notificaciones/whatsapp/webhook",
    response_model=s.ResumenWebhookSalida,
    tags=["HIST-4.2 Respuestas"],
    responses={403: {"model": s.RespuestaError}, 422: {"model": s.RespuestaError}, 503: {"model": s.RespuestaError}},
)
async def recibir_webhook(request: Request, svc: ProcesarNotificacionesWhatsApp = Depends(webhook_uc)):
    """Recibe los estados de entrega (enviado, entregado, leído, fallido) y las respuestas del tutor desde WhatsApp.

    Público (sin sesión) pero protegido por la firma ``X-Hub-Signature-256``, que siempre se exige (403 si falta o es
    inválida). Falla cerrado: si no se configuró ``WHATSAPP_APP_SECRET`` responde 503 y no procesa nada. La respuesta
    se asocia al recordatorio por el mensaje al que responde o, si no, por el número del tutor. Lo que no se reconoce
    se ignora y se cuenta.
    """
    cuerpo = await request.body()
    resumen = await run_in_threadpool(svc.procesar_webhook, cuerpo, request.headers.get("X-Hub-Signature-256"))
    return s.ResumenWebhookSalida(**vars(resumen))
