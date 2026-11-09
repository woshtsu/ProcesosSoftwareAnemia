"""Casos de uso HIST-4.1 y HIST-4.2: recordatorios de control por mensajería y respuesta del tutor (ADR-014).

Una sola carga por lotes de niños activos y de recordatorios existentes; la selección y la redacción las hace el
dominio (``domain/service/notificaciones.py``). El envío sale por el puerto ``Notificador``: simulado por defecto,
WhatsApp Cloud con respaldo por SMS cuando está configurado.
"""

import json
import threading
import uuid
from datetime import date

from app.domain.model.errores import (
    ConflictoBarrera,
    ConflictoRecordatorio,
    ConflictoRespuesta,
    ErrorCampo,
    ErrorValidacion,
    FirmaInvalida,
    NoEncontrado,
    WebhookNoConfigurado,
)
from app.domain.model.notificacion import (
    ConfiguracionWebhook,
    EstadoRecordatorio,
    EventosWebhook,
    MensajeSaliente,
    MetricasRecordatorios,
    OrigenRespuesta,
    Recordatorio,
    RespuestaTutor,
    ResultadoGeneracion,
    ResultadoRespuesta,
    ResumenWebhook,
    VistaRecordatorio,
)
from app.domain.model.tiempo import ahora
from app.domain.service.agenda import generar_agenda
from app.domain.service.barreras import validar_datos_barrera
from app.domain.service.notificaciones import (
    PLANTILLA_WHATSAPP,
    avanzar_estado,
    calcular_metricas,
    extraer_eventos,
    firma_valida,
    interpretar_respuesta,
    parametros_mensaje,
    redactar_mensaje,
    seleccionar_controles,
    tiene_contacto,
    validar_respuesta,
    verificacion_valida,
)
from app.domain.service.validaciones import exigir
from app.ports.inbound.barreras import GestionarBarreras
from app.ports.inbound.notificaciones import (
    ConsultarRecordatorios,
    GenerarRecordatorios,
    ProcesarNotificacionesWhatsApp,
    RegistrarRespuestaRecordatorio,
)
from app.ports.outbound.cache_agendas import ProveedorAgendasActivos
from app.ports.outbound.notificador import Notificador
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos
from app.ports.outbound.repositorio_recordatorios import RepositorioRecordatorios

LIMITE_MAXIMO = 1000


def _vista(r: Recordatorio, nino) -> VistaRecordatorio:
    return VistaRecordatorio(r, nino.nombre_completo, nino.codigo_origen, nino.comunidad, nino.establecimiento)


class ServicioRecordatorios(
    GenerarRecordatorios, ConsultarRecordatorios, RegistrarRespuestaRecordatorio, ProcesarNotificacionesWhatsApp
):
    def __init__(
        self,
        repo: RepositorioNinos,
        recordatorios: RepositorioRecordatorios,
        notificador: Notificador,
        reloj: Reloj,
        barreras: GestionarBarreras,
        webhook: ConfiguracionWebhook = ConfiguracionWebhook(),
        cache_agendas: ProveedorAgendasActivos | None = None,
    ):
        self.repo = repo
        self.recordatorios = recordatorios
        self.notificador = notificador
        self.reloj = reloj
        self.barreras = barreras
        self.webhook = webhook
        self.cache_agendas = cache_agendas
        # Una generación, respuesta o aviso de entrega a la vez en este proceso: dos generaciones simultáneas no envían
        # dos veces el mismo mensaje (la restricción UNIQUE solo evita la segunda fila, no el segundo envío) y dos
        # respuestas simultáneas no se pisan (ADR-014).
        self._cerrojo = threading.Lock()

    # HIST-4.1 -----------------------------------------------------------------------------------------------------
    def generar_recordatorios(self, usuario: str, establecimiento: str | None = None) -> ResultadoGeneracion:
        with self._cerrojo:
            return self._generar(usuario, establecimiento)

    def _generar(self, usuario: str, establecimiento: str | None) -> ResultadoGeneracion:
        hoy = self.reloj.hoy()
        filtro = (establecimiento or "").strip().casefold()
        existentes = {r.clave: r for r in self.recordatorios.listar_recordatorios()}
        candidatos = enviados = fallidos = sin_contacto = ya_enviados = 0
        generados: list[VistaRecordatorio] = []
        agendas = (
            self.cache_agendas.obtener_agendas()
            if self.cache_agendas is not None
            else [(n, generar_agenda(n, hoy)) for n in self.repo.listar(estado="ACTIVO")]
        )
        for nino, agenda in agendas:
            if filtro and nino.establecimiento.strip().casefold() != filtro:
                continue
            for control, tipo in seleccionar_controles(agenda, hoy):
                candidatos += 1
                clave = (nino.id, control.codigo, control.fecha_programada, tipo.value)
                previo = existentes.get(clave)
                if previo and previo.estado != EstadoRecordatorio.FALLIDO:
                    ya_enviados += 1
                elif not tiene_contacto(nino):
                    sin_contacto += 1
                else:
                    parametros = parametros_mensaje(nino, control, tipo, hoy)
                    recordatorio = self._enviar(previo, nino.id, control, tipo, parametros, nino.tutor_celular, usuario)
                    if recordatorio is None:  # otra generación simultánea ya lo creó
                        ya_enviados += 1
                        continue
                    generados.append(_vista(recordatorio, nino))
                    if recordatorio.estado == EstadoRecordatorio.FALLIDO:
                        fallidos += 1
                    else:
                        enviados += 1
        return ResultadoGeneracion(hoy, candidatos, enviados, fallidos, sin_contacto, ya_enviados, tuple(generados))

    def _enviar(self, previo, nino_id, control, tipo, parametros, celular, usuario) -> Recordatorio | None:
        texto = redactar_mensaje(parametros)
        referencia = previo.id if previo else str(uuid.uuid4())
        resultado = self.notificador.enviar(MensajeSaliente(celular, texto, PLANTILLA_WHATSAPP, parametros, referencia))
        momento = ahora()
        recordatorio = previo or Recordatorio(
            id=referencia,
            nino_id=nino_id,
            codigo_control=control.codigo,
            fecha_programada=control.fecha_programada,
            tipo=tipo,
            canal=resultado.canal,
            estado=resultado.estado,
            destino=celular,
            mensaje=texto,
            generado_por=usuario,
        )
        if previo:  # reintento de un envío fallido
            previo.intentos += 1
            previo.canal, previo.estado, previo.mensaje, previo.generado_por = (
                resultado.canal,
                resultado.estado,
                texto,
                usuario,
            )
        recordatorio.id_externo = resultado.id_externo
        recordatorio.detalle = resultado.error
        recordatorio.enviado_en = momento if resultado.exito else None
        recordatorio.actualizado_en = momento
        if previo:
            return self.recordatorios.actualizar_recordatorio(recordatorio)
        try:
            return self.recordatorios.agregar_recordatorio(recordatorio)
        except ConflictoRecordatorio:
            return None

    def listar_recordatorios(
        self, estado: str | None = None, desde: date | None = None, nino_id: str | None = None, limite: int = 200
    ) -> list[VistaRecordatorio]:
        errores = []
        if estado and estado not in {e.value for e in EstadoRecordatorio}:
            errores.append(ErrorCampo("estado", "Estado de recordatorio inválido."))
        if not (1 <= limite <= LIMITE_MAXIMO):
            errores.append(ErrorCampo("limite", f"El límite debe estar entre 1 y {LIMITE_MAXIMO}."))
        exigir(errores)
        lista = self.recordatorios.listar_recordatorios(estado=estado, desde=desde, nino_id=nino_id, limite=limite)
        ninos = self.repo.obtener_varios({r.nino_id for r in lista})
        return [_vista(r, ninos[r.nino_id]) for r in lista]

    def metricas_recordatorios(self, desde: date | None = None, hasta: date | None = None) -> MetricasRecordatorios:
        if desde and hasta and desde > hasta:
            raise ErrorValidacion([ErrorCampo("desde", "La fecha inicial debe ser anterior o igual a la final.")])
        return calcular_metricas(self.recordatorios.listar_recordatorios(desde=desde, hasta=hasta))

    # HIST-4.2 -----------------------------------------------------------------------------------------------------
    def registrar_respuesta(self, recordatorio_id: str, datos: dict, usuario: str) -> ResultadoRespuesta:
        with self._cerrojo:
            return self._responder(recordatorio_id, datos, usuario)

    def _responder(self, recordatorio_id: str, datos: dict, usuario: str) -> ResultadoRespuesta:
        recordatorio = self.recordatorios.obtener_recordatorio(recordatorio_id)
        if not recordatorio:
            raise NoEncontrado("No existe el recordatorio solicitado.")
        hoy = self.reloj.hoy()
        exigir(validar_respuesta(datos, hoy))
        if recordatorio.respuesta:
            raise ConflictoRespuesta("El recordatorio ya tiene una respuesta registrada.")
        nino = self.repo.obtener(recordatorio.nino_id)
        barrera = datos.get("barrera")
        if barrera:  # se valida antes de guardar la respuesta: o se registra todo o nada
            datos_barrera = {
                **barrera,
                "fuente": "RESPUESTA_RECORDATORIO",
                "fecha": hoy,
                "recordatorio_id": recordatorio.id,
            }
            exigir(validar_datos_barrera(datos_barrera, nino.fecha_nacimiento, hoy))
        self._aplicar_respuesta(
            recordatorio, datos["respuesta"], datos.get("fecha_reprogramada"), OrigenRespuesta.PERSONAL, usuario
        )
        barrera_id = None
        if barrera:
            try:
                barrera_id = self.barreras.registrar_barrera(recordatorio.nino_id, datos_barrera, usuario).id
            except ConflictoBarrera as e:  # el niño ya tenía esa barrera registrada hoy por la misma fuente
                barrera_id = e.id_existente
        sugerida = recordatorio.respuesta == RespuestaTutor.NO_PUEDE and barrera_id is None
        return ResultadoRespuesta(_vista(recordatorio, nino), barrera_id, sugerida)

    def _aplicar_respuesta(
        self, r: Recordatorio, respuesta, fecha: date | None, origen: OrigenRespuesta, quien: str
    ) -> None:
        r.respuesta = RespuestaTutor(respuesta)
        r.fecha_reprogramada = fecha if r.respuesta == RespuestaTutor.REPROGRAMAR else None
        r.respondido_en = r.actualizado_en = ahora()
        r.respondido_por, r.origen_respuesta = quien, origen
        self.recordatorios.actualizar_recordatorio(r)

    # Webhook de WhatsApp ------------------------------------------------------------------------------------------
    def verificar_suscripcion(self, modo: str | None, token: str | None) -> bool:
        return verificacion_valida(modo, token, self.webhook.verify_token)

    def procesar_webhook(self, cuerpo: bytes, firma: str | None) -> ResumenWebhook:
        # Falla cerrado: sin secreto no hay forma de comprobar quién llama y el endpoint es público.
        if not self.webhook.app_secret:
            raise WebhookNoConfigurado("El webhook está deshabilitado: falta configurar WHATSAPP_APP_SECRET.")
        if not firma_valida(cuerpo, firma, self.webhook.app_secret):
            raise FirmaInvalida("La firma de la notificación no es válida.")
        try:
            payload = json.loads(cuerpo)
        except ValueError:
            raise ErrorValidacion([ErrorCampo("cuerpo", "La notificación debe ser un JSON.")]) from None
        return self.procesar_eventos(extraer_eventos(payload))

    def procesar_eventos(self, eventos: EventosWebhook) -> ResumenWebhook:
        with self._cerrojo:
            return self._aplicar_eventos(eventos)

    def _aplicar_eventos(self, eventos: EventosWebhook) -> ResumenWebhook:
        hoy = self.reloj.hoy()
        aplicados = registradas = ignorados = 0
        for evento in eventos.estados:
            r = self.recordatorios.obtener_por_id_externo(evento.id_externo)
            nuevo = avanzar_estado(r.estado, evento.estado) if r else None
            if r is None or nuevo == r.estado:
                ignorados += 1
                continue
            r.estado, r.actualizado_en = nuevo, ahora()
            if nuevo == EstadoRecordatorio.FALLIDO:
                r.detalle = evento.error
            self.recordatorios.actualizar_recordatorio(r)
            aplicados += 1
        for mensaje in eventos.mensajes:
            respuesta, fecha = interpretar_respuesta(mensaje.texto)
            r = self.recordatorios.buscar_para_respuesta(mensaje.id_contexto, mensaje.telefono) if respuesta else None
            if r is None or r.respuesta is not None:
                ignorados += 1
                continue
            if validar_respuesta({"respuesta": respuesta, "fecha_reprogramada": fecha}, hoy, exigir_fecha=False):
                fecha = None  # una fecha fuera de rango no se acepta; el personal la confirma con el tutor
            self._aplicar_respuesta(r, respuesta, fecha, OrigenRespuesta.WHATSAPP, "whatsapp")
            registradas += 1
        return ResumenWebhook(aplicados, registradas, ignorados)
