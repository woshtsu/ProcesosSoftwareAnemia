"""Casos de uso HIST-3.2 y HIST-3.3: sincronizar operaciones registradas sin conexión y resolver conflictos (ADR-012).

El dispositivo guarda sus operaciones en una cola local con un ``id_operacion`` (UUID). Al reconectar las envía en un
lote; este servicio las procesa en orden de fecha local y es idempotente: una operación ya procesada se responde como
DUPLICADA sin tocar nada. Para crear los registros reutiliza los mismos casos de uso del registro en línea (expediente,
asistencia, visitas y barreras), de modo que las reglas clínicas y de negocio no se repiten. El servidor es la fuente
de verdad: cuando ya tiene un dato distinto no lo sobrescribe, abre un conflicto que una persona resuelve después.
"""

from app.domain.model.asistencia import EstadoAsistencia
from app.domain.model.errores import (
    ConflictoAsistencia,
    ConflictoBarrera,
    ConflictoVisita,
    ConflictoYaResuelto,
    ErrorCampo,
    ErrorValidacion,
    NoEncontrado,
    RegistroDuplicado,
)
from app.domain.model.sincronizacion import (
    ConflictoSincronizacion,
    EstadoConflicto,
    OperacionEntrante,
    OperacionSincronizada,
    ResolucionConflicto,
    ResultadoOperacion,
    ResultadoSincronizacion,
    TipoOperacion,
)
from app.domain.model.tiempo import ahora
from app.domain.model.visita import ConsumoSuplemento, ResultadoVisita
from app.domain.service import reglas_clinicas as rc
from app.domain.service.asistencia import validar_datos_asistencia
from app.domain.service.conflictos import (
    CAMPOS_EDITABLES,
    AccionSync,
    Decision,
    decidir_asistencia,
    decidir_evaluacion,
    decidir_nino,
    decidir_visita,
    diferencias_nino,
    instantanea_asistencia,
    motivo_no_aplicable,
)
from app.domain.service.operaciones import normalizar_datos, normalizar_fecha_local
from app.domain.service.validaciones import exigir, validar_datos_evaluacion, validar_datos_nino
from app.domain.service.visitas import validar_datos_visita
from app.ports.inbound.asistencia import RegistrarAsistencia
from app.ports.inbound.barreras import GestionarBarreras
from app.ports.inbound.expediente import GestionarExpediente
from app.ports.inbound.sincronizacion import GestionarConflictos, SincronizarOperaciones
from app.ports.inbound.visitas import GestionarVisitas
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos
from app.ports.outbound.repositorio_sincronizacion import RepositorioSincronizacion
from app.ports.outbound.repositorio_visitas import RepositorioVisitas

_DE_DOMINIO = (NoEncontrado, ConflictoAsistencia, ConflictoVisita, RegistroDuplicado)
_MAPEAN_NINO = (ResultadoOperacion.APLICADA, ResultadoOperacion.DUPLICADA, ResultadoOperacion.RESUELTA)


class ServicioSincronizacion(SincronizarOperaciones, GestionarConflictos):
    def __init__(
        self,
        repo: RepositorioNinos,
        visitas: RepositorioVisitas,
        sync: RepositorioSincronizacion,
        expediente: GestionarExpediente,
        asistencia: RegistrarAsistencia,
        gestion_visitas: GestionarVisitas,
        reloj: Reloj,
        gestion_barreras: GestionarBarreras,
    ):
        self.repo = repo
        self.visitas = visitas
        self.sync = sync
        self.expediente = expediente
        self.asistencia = asistencia
        self.gestion_visitas = gestion_visitas
        self.gestion_barreras = gestion_barreras
        self.reloj = reloj

    # HIST-3.2 -----------------------------------------------------------------------------------------------------
    def sincronizar(self, operaciones: list[OperacionEntrante], usuario: str) -> list[ResultadoSincronizacion]:
        orden = sorted(range(len(operaciones)), key=lambda i: (normalizar_fecha_local(operaciones[i].fecha_local), i))
        resultados = {i: self._procesar(operaciones[i], usuario) for i in orden}
        return [resultados[i] for i in range(len(operaciones))]

    def _procesar(self, op: OperacionEntrante, usuario: str) -> ResultadoSincronizacion:
        previa = self.sync.obtener_operacion(op.id_operacion)
        if previa:
            return self._reenvio(op, previa)
        try:
            return self._aplicar(op, usuario)
        except ErrorValidacion as e:
            return self._rechazada(op, e.errores)
        except _DE_DOMINIO as e:
            return self._rechazada(op, [ErrorCampo("operacion", str(e))])

    def _aplicar(self, op: OperacionEntrante, usuario: str) -> ResultadoSincronizacion:
        datos, errores = normalizar_datos(op.tipo, op.datos)
        exigir(errores)
        if op.tipo == TipoOperacion.REGISTRAR_NINO:
            return self._nino(op, datos, usuario)
        nino = self._nino_referenciado(op)
        hoy = self.reloj.hoy()
        if op.tipo == TipoOperacion.REGISTRAR_EVALUACION:
            exigir(validar_datos_evaluacion(datos, nino.fecha_nacimiento, hoy))
            return self._evaluacion(op, nino, datos, usuario)
        if op.tipo == TipoOperacion.REGISTRAR_ASISTENCIA:
            falta_codigo = [] if datos.get("codigo") else [ErrorCampo("codigo", "Es obligatorio.")]
            exigir(validar_datos_asistencia(datos, hoy) + falta_codigo)
            return self._asistencia(op, nino, datos, usuario)
        if op.tipo == TipoOperacion.REGISTRAR_BARRERA:
            return self._barrera(op, nino, datos, usuario)
        exigir(validar_datos_visita(datos, nino.fecha_nacimiento, hoy))
        return self._visita(op, nino, datos, usuario)

    def _nino_referenciado(self, op: OperacionEntrante):
        if op.nino_id:
            nino_id = op.nino_id
        elif op.nino_id_cliente:
            nino_id = self.sync.id_nino_de_cliente(op.id_dispositivo, op.nino_id_cliente)
            if not nino_id:
                raise NoEncontrado(
                    "El niño registrado en el dispositivo aún no está sincronizado o su conflicto sigue pendiente."
                )
        else:
            raise ErrorValidacion([ErrorCampo("nino_ref", "Indique el niño por su id o por su id_cliente.")])
        nino = self.repo.obtener(nino_id)
        if not nino:
            raise NoEncontrado("No existe el niño al que se refiere la operación.")
        return nino

    def _nino(self, op: OperacionEntrante, datos: dict, usuario: str) -> ResultadoSincronizacion:
        hoy = self.reloj.hoy()
        datos_nino, datos_eval = datos["nino"], datos["evaluacion"]
        errores = validar_datos_nino(datos_nino, hoy)
        nacimiento = None if any(e.campo == "fecha_nacimiento" for e in errores) else datos_nino["fecha_nacimiento"]
        exigir(errores + validar_datos_evaluacion(datos_eval, nacimiento, hoy))
        existente = self.repo.obtener_por_dni(datos_nino["dni"].strip())
        decision = decidir_nino(existente, datos_nino, datos_eval)
        if decision.accion == AccionSync.CREAR:
            nino = self.expediente.registrar_nino(datos_nino, datos_eval, usuario)
            return self._registrar(op, ResultadoOperacion.APLICADA, nino.id)
        if decision.accion == AccionSync.AGREGAR_EVALUACION:
            self.expediente.registrar_evaluacion(existente.id, datos_eval, usuario)
            return self._registrar(
                op, ResultadoOperacion.APLICADA, existente.id, "El niño ya existía: se agregó su evaluación."
            )
        if decision.accion == AccionSync.MAPEAR:
            return self._registrar(
                op, ResultadoOperacion.DUPLICADA, existente.id, "El servidor ya tiene a este niño con los mismos datos."
            )
        return self._conflicto(op, decision, existente.id, usuario)

    def _evaluacion(self, op, nino, datos: dict, usuario: str) -> ResultadoSincronizacion:
        decision = decidir_evaluacion(nino, datos)
        if decision.accion == AccionSync.CREAR:
            previas = {e.id for e in nino.evaluaciones}
            actualizado = self.expediente.registrar_evaluacion(nino.id, datos, usuario)
            nueva = next(e for e in actualizado.evaluaciones if e.id not in previas)
            return self._registrar(op, ResultadoOperacion.APLICADA, nueva.id)
        if decision.accion == AccionSync.MAPEAR:
            return self._registrar(
                op, ResultadoOperacion.DUPLICADA, decision.id_recurso, "El niño ya tiene esa evaluación."
            )
        return self._conflicto(op, decision, nino.id, usuario)

    def _asistencia(self, op, nino, datos: dict, usuario: str) -> ResultadoSincronizacion:
        decision = decidir_asistencia(nino, datos)
        if decision.accion == AccionSync.CREAR:
            asistencia = self.asistencia.registrar_asistencia(nino.id, datos["codigo"], datos, usuario)
            return self._registrar(op, ResultadoOperacion.APLICADA, asistencia.id)
        if decision.accion == AccionSync.MAPEAR:
            return self._registrar(
                op, ResultadoOperacion.DUPLICADA, decision.id_recurso, "El control ya tiene esa asistencia."
            )
        return self._conflicto(op, decision, nino.id, usuario)

    def _visita(self, op, nino, datos: dict, usuario: str) -> ResultadoSincronizacion:
        decision = decidir_visita(self.visitas.obtener_visita_del_dia(nino.id, datos["fecha"]), datos)
        if decision.accion == AccionSync.CREAR:
            visita = self.gestion_visitas.registrar_visita(nino.id, datos, usuario)
            return self._registrar(op, ResultadoOperacion.APLICADA, visita.id)
        if decision.accion == AccionSync.MAPEAR:
            return self._registrar(
                op, ResultadoOperacion.DUPLICADA, decision.id_recurso, "El niño ya tiene esa visita."
            )
        return self._conflicto(op, decision, nino.id, usuario)

    def _barrera(self, op, nino, datos: dict, usuario: str) -> ResultadoSincronizacion:
        """Una barrera es un hecho, no un valor que pueda chocar: si el niño ya la tiene se mapea a la existente."""
        try:
            barrera = self.gestion_barreras.registrar_barrera(nino.id, datos, usuario)
        except ConflictoBarrera as e:
            return self._registrar(op, ResultadoOperacion.DUPLICADA, e.id_existente, "El niño ya tiene esa barrera.")
        return self._registrar(op, ResultadoOperacion.APLICADA, barrera.id)

    # Registro del resultado ---------------------------------------------------------------------------------------
    def _registrar(
        self, op: OperacionEntrante, resultado: ResultadoOperacion, id_recurso: str, mensaje: str | None = None
    ) -> ResultadoSincronizacion:
        es_nino = op.tipo == TipoOperacion.REGISTRAR_NINO
        guardada = self.sync.registrar_operacion(
            OperacionSincronizada(
                op.id_operacion,
                op.tipo,
                op.id_dispositivo,
                resultado,
                id_recurso,
                op.id_cliente if es_nino else None,
                normalizar_fecha_local(op.fecha_local),
            )
        )
        if not guardada:  # otra solicitud simultánea ya procesó este id_operacion
            return self._reenvio(op, self.sync.obtener_operacion(op.id_operacion))
        return ResultadoSincronizacion(
            op.id_operacion,
            op.tipo,
            resultado,
            id_recurso,
            id_cliente=op.id_cliente if es_nino else None,
            mensaje=mensaje,
        )

    def _conflicto(
        self, op: OperacionEntrante, decision: Decision, nino_id: str, usuario: str
    ) -> ResultadoSincronizacion:
        resultado = self._registrar(op, ResultadoOperacion.CONFLICTO, decision.id_recurso)
        if resultado.resultado != ResultadoOperacion.CONFLICTO:  # carrera: ya la procesó otra solicitud
            return resultado
        conflicto = self.sync.guardar_conflicto(
            ConflictoSincronizacion(
                id_operacion=op.id_operacion,
                tipo=op.tipo,
                motivo=decision.motivo,
                nino_id=nino_id,
                id_recurso=decision.id_recurso,
                datos_cliente=op.datos,
                datos_servidor=decision.datos_servidor,
                registrado_por=usuario,
            )
        )
        return ResultadoSincronizacion(
            op.id_operacion,
            op.tipo,
            ResultadoOperacion.CONFLICTO,
            decision.id_recurso,
            id_conflicto=conflicto.id,
            mensaje=decision.motivo,
        )

    def _reenvio(self, op: OperacionEntrante, previa: OperacionSincronizada) -> ResultadoSincronizacion:
        conflicto = self.sync.obtener_conflicto_de_operacion(op.id_operacion)
        original = ResultadoOperacion.CONFLICTO if previa.resultado == ResultadoOperacion.RESUELTA else previa.resultado
        return ResultadoSincronizacion(
            op.id_operacion,
            op.tipo,
            ResultadoOperacion.DUPLICADA,
            previa.id_recurso,
            id_cliente=previa.id_cliente if previa.resultado in _MAPEAN_NINO else None,
            id_conflicto=conflicto.id if conflicto else None,
            mensaje="La operación ya se había procesado: no se aplicó de nuevo.",
            resultado_original=original,
        )

    @staticmethod
    def _rechazada(op: OperacionEntrante, errores: list[ErrorCampo]) -> ResultadoSincronizacion:
        return ResultadoSincronizacion(
            op.id_operacion,
            op.tipo,
            ResultadoOperacion.RECHAZADA,
            mensaje="; ".join(f"{e.campo}: {e.mensaje}" for e in errores),
            errores=tuple(errores),
        )

    # HIST-3.3 -----------------------------------------------------------------------------------------------------
    def listar_conflictos(self, estado: str | None = None) -> list[ConflictoSincronizacion]:
        if estado is not None and estado not in {e.value for e in EstadoConflicto}:
            raise ErrorValidacion([ErrorCampo("estado", "El estado debe ser PENDIENTE o RESUELTO.")])
        return self.sync.listar_conflictos(estado)

    def resolver_conflicto(self, conflicto_id: str, resolucion: str, usuario: str) -> ConflictoSincronizacion:
        conflicto = self.sync.obtener_conflicto(conflicto_id)
        if not conflicto:
            raise NoEncontrado("No existe el conflicto solicitado.")
        if resolucion not in {r.value for r in ResolucionConflicto}:
            raise ErrorValidacion(
                [ErrorCampo("resolucion", "La resolución debe ser CONSERVAR_SERVIDOR, APLICAR_CLIENTE o DESCARTAR.")]
            )
        if conflicto.estado == EstadoConflicto.RESUELTO:
            raise ConflictoYaResuelto("El conflicto ya fue resuelto.")
        if resolucion == ResolucionConflicto.APLICAR_CLIENTE:
            self._aplicar_cliente(conflicto, usuario)
        elif resolucion == ResolucionConflicto.CONSERVAR_SERVIDOR and conflicto.tipo == TipoOperacion.REGISTRAR_NINO:
            self._asegurar_evaluacion(conflicto, reemplazar=False)
        conflicto.estado = EstadoConflicto.RESUELTO
        conflicto.resolucion = ResolucionConflicto(resolucion)
        conflicto.resuelto_en = ahora()
        conflicto.resuelto_por = usuario
        if conflicto.tipo == TipoOperacion.REGISTRAR_NINO and resolucion != ResolucionConflicto.DESCARTAR:
            self.sync.marcar_operacion_resuelta(conflicto.id_operacion)
        return self.sync.actualizar_conflicto(conflicto)

    def _aplicar_cliente(self, conflicto: ConflictoSincronizacion, usuario: str) -> None:
        """El dato del dispositivo reemplaza al del servidor solo donde el dominio lo permite (ver conflictos.py)."""
        datos, _ = normalizar_datos(conflicto.tipo, conflicto.datos_cliente)
        nino = self.repo.obtener(conflicto.nino_id)
        if conflicto.tipo == TipoOperacion.REGISTRAR_NINO:
            diferencias = diferencias_nino(nino, datos["nino"])
            self._exigir_aplicable(conflicto.tipo, diferencias, {})
            cambios = {c: datos["nino"][c] for c in diferencias if c in CAMPOS_EDITABLES}
            if cambios:
                self.expediente.actualizar_datos(nino.id, cambios, usuario)
            self._asegurar_evaluacion(conflicto, reemplazar=True)
        elif conflicto.tipo == TipoOperacion.REGISTRAR_EVALUACION:
            self._asegurar_evaluacion(conflicto, reemplazar=True)
        elif conflicto.tipo == TipoOperacion.REGISTRAR_ASISTENCIA:
            previa = next(
                a
                for a in nino.asistencias
                if (a.codigo_control, a.fecha_programada) == (datos["codigo"], datos["fecha_programada"])
            )
            self._exigir_aplicable(conflicto.tipo, ("estado",), instantanea_asistencia(previa))
            previa.estado = EstadoAsistencia(datos["estado"])
            previa.motivo = (datos.get("motivo") or "").strip() or None
            previa.registrado_por = conflicto.registrado_por
            self.repo.actualizar_asistencia(previa)
        else:
            previa = self.visitas.obtener_visita_del_dia(nino.id, datos["fecha"])
            previa.resultado = ResultadoVisita(datos["resultado"])
            previa.consume_suplemento = ConsumoSuplemento(datos.get("consume_suplemento") or "DESCONOCIDO")
            previa.observaciones = (datos.get("observaciones") or "").strip() or None
            previa.registrado_por = conflicto.registrado_por
            self.visitas.actualizar_visita(previa)

    @staticmethod
    def _exigir_aplicable(tipo: str, diferencias: tuple[str, ...], datos_servidor: dict) -> None:
        motivo = motivo_no_aplicable(tipo, diferencias, datos_servidor)
        if motivo:
            raise ErrorValidacion([ErrorCampo("resolucion", motivo)])

    def _asegurar_evaluacion(self, conflicto: ConflictoSincronizacion, reemplazar: bool) -> None:
        """Agrega la evaluación del dispositivo si el servidor no tiene una ese día; con ``reemplazar`` y una
        hemoglobina distinta, el valor del dispositivo sustituye al del servidor (se recalculan las reglas clínicas)."""
        datos, _ = normalizar_datos(conflicto.tipo, conflicto.datos_cliente)
        evaluacion = datos["evaluacion"] if conflicto.tipo == TipoOperacion.REGISTRAR_NINO else datos
        nino = self.repo.obtener(conflicto.nino_id)
        decision = decidir_evaluacion(nino, evaluacion)
        if decision.accion == AccionSync.CREAR:
            self.expediente.registrar_evaluacion(nino.id, evaluacion, conflicto.registrado_por)
        elif decision.accion == AccionSync.CONFLICTO and reemplazar:
            actual = next(e for e in nino.evaluaciones if e.id == decision.id_recurso)
            actual.hemoglobina_observada = evaluacion["hemoglobina_observada"]
            actual.peso_kg, actual.talla_cm = evaluacion["peso_kg"], evaluacion["talla_cm"]
            actual.registrado_por = conflicto.registrado_por
            rc.aplicar_reglas_clinicas(actual)
            self.repo.actualizar_evaluacion(actual)
