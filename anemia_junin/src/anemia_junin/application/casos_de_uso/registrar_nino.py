from __future__ import annotations

from datetime import datetime

from anemia_junin.application.conversores import dosaje_a_dto, nino_a_dto
from anemia_junin.application.dto import CrearNinoDTO, DosajeSalidaDTO, NinoSalidaDTO
from anemia_junin.domain.clasificador import ClasificadorHemoglobina
from anemia_junin.domain.entities import (
    Dosaje,
    IntentoRegistro,
    Nino,
    Sexo,
    TipoNacimiento,
)
from anemia_junin.domain.ports import Reloj
from anemia_junin.domain.validators import (
    ErrorValidacion,
    normalizar_distrito,
    normalizar_nombre,
    validar_altitud,
    validar_distrito,
    validar_dni,
    validar_fecha_dosaje,
    validar_fecha_nacimiento,
    validar_nombre,
    validar_peso_kg,
    validar_sexo,
    validar_telefono,
    validar_tipo_nacimiento,
)


class DniDuplicadoError(Exception):
    """DNI ya existe en el sistema."""


def _valor_enum(valor: object) -> object:
    """Devuelve el valor crudo de un Enum (o el objeto tal cual si no lo es)."""
    return getattr(valor, "value", valor)


class RegistrarNino:
    def __init__(
        self,
        uow_factory,
        clasificador: ClasificadorHemoglobina,
        reloj: Reloj,
    ) -> None:
        self._uow_factory = uow_factory
        self._clasificador = clasificador
        self._reloj = reloj

    def ejecutar(
        self,
        dto: CrearNinoDTO,
        errores_entrada: dict[str, list[str]] | None = None,
    ) -> tuple[NinoSalidaDTO, DosajeSalidaDTO | None]:
        """
        Registra un niño (y opcionalmente su dosaje inicial) de forma atómica.

        ``errores_entrada`` son los errores de conversión detectados por el adaptador
        de entrada (p. ej. una fecha mal formada o un peso no numérico). Se combinan
        con las validaciones de dominio para que el intento rechazado quede siempre
        registrado en la traza de calidad (HIST-1.5) y nunca se guarde un registro
        con valores sustituidos por defecto.
        """
        ahora = self._reloj.ahora_utc()
        hoy = self._reloj.hoy()
        entrada = {k: v for k, v in (errores_entrada or {}).items() if v}

        # ── Validar datos del niño ──
        errores: dict[str, list[str]] = {}
        errores["dni"] = validar_dni(dto.dni)
        errores["nombres"] = validar_nombre(dto.nombres)
        errores["apellidos"] = validar_nombre(dto.apellidos)
        errores["fecha_nacimiento"] = validar_fecha_nacimiento(dto.fecha_nacimiento, hoy)
        errores["sexo"] = validar_sexo(_valor_enum(dto.sexo))
        errores["tipo_nacimiento"] = validar_tipo_nacimiento(_valor_enum(dto.tipo_nacimiento))
        errores["distrito"] = validar_distrito(dto.distrito)
        errores["altitud_msnm"] = validar_altitud(dto.altitud_msnm)
        errores["cuidador"] = validar_nombre(dto.cuidador)
        errores["telefono"] = validar_telefono(dto.telefono)

        if dto.peso_g is None:
            errores["peso_kg"] = ["Debe ser un número válido"]
        else:
            err_peso, _ = validar_peso_kg(dto.peso_g / 1000)  # dto ya tiene gramos
            errores["peso_kg"] = err_peso

        # Los errores de conversión del adaptador prevalecen (son más específicos)
        for campo, mensajes in entrada.items():
            errores[campo] = mensajes

        # Validar dosaje inicial si viene
        dosaje_err: dict[str, list[str]] = {}
        edad_meses_dosaje = 0
        if dto.dosaje_inicial is not None:
            d = dto.dosaje_inicial
            # Solo se valida la fecha del dosaje si la fecha de nacimiento es válida
            if not errores.get("fecha_nacimiento") and not entrada.get(
                "dosaje_inicial.fecha_dosaje"
            ):
                err_fecha_d, edad_meses_dosaje = validar_fecha_dosaje(
                    d.fecha_dosaje, dto.fecha_nacimiento, hoy
                )
                dosaje_err["dosaje_inicial.fecha_dosaje"] = err_fecha_d
            # hb ya viene en ddl (convertido por el adaptador)
            # Verificar rango en ddl: 20–250
            if not (20 <= d.hb_observada_ddl <= 250):
                dosaje_err["dosaje_inicial.hb_observada"] = ["Fuera de rango permitido"]

        todos_errores = {**errores, **dosaje_err}
        for campo, mensajes in entrada.items():
            todos_errores[campo] = mensajes
        hay_errores = any(v for v in todos_errores.values())

        if hay_errores:
            self._registrar_intento_rechazado(todos_errores, ahora)
            ErrorValidacion.si_hay_errores(todos_errores)

        # ── Normalizar ──
        nombres = normalizar_nombre(dto.nombres)
        apellidos = normalizar_nombre(dto.apellidos)
        distrito = normalizar_distrito(dto.distrito)

        # ── Construir entidades ──
        nino = Nino.nuevo(
            dni=dto.dni,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=dto.fecha_nacimiento,
            sexo=Sexo(_valor_enum(dto.sexo)),
            tipo_nacimiento=TipoNacimiento(_valor_enum(dto.tipo_nacimiento)),
            peso_g=dto.peso_g,
            distrito=distrito,
            altitud_msnm=int(dto.altitud_msnm),
            cuidador=normalizar_nombre(dto.cuidador),
            telefono=dto.telefono if dto.telefono else None,
            ahora=ahora,
        )

        dosaje = None
        if dto.dosaje_inicial is not None:
            resultado_clas = self._clasificador.clasificar(
                hb_observada_ddl=dto.dosaje_inicial.hb_observada_ddl,
                altitud_msnm=int(dto.altitud_msnm),
                edad_meses=edad_meses_dosaje,
            )
            dosaje = Dosaje.nuevo(
                nino_id=nino.id,
                fecha_dosaje=dto.dosaje_inicial.fecha_dosaje,
                hb_observada_ddl=dto.dosaje_inicial.hb_observada_ddl,
                altitud_msnm=int(dto.altitud_msnm),
                ajuste_ddl=resultado_clas.ajuste_ddl,
                hb_ajustada_ddl=resultado_clas.hb_ajustada_ddl,
                edad_meses=edad_meses_dosaje,
                clasificacion=resultado_clas.clasificacion,
                version_normativa=resultado_clas.version_normativa,
                advertencias=resultado_clas.advertencias,
                ahora=ahora,
            )

        # ── Persistir (transacción atómica) ──
        try:
            with self._uow_factory() as uow:
                uow.ninos.guardar(nino)
                if dosaje:
                    uow.dosajes.guardar(dosaje)
                # Registrar intento ACEPTADO dentro de la misma transacción
                intento = IntentoRegistro.nuevo(
                    operacion="CREAR_NINO",
                    resultado="ACEPTADO",
                    codigos_error=[],
                    ahora=ahora,
                )
                uow.intentos.guardar(intento)
        except Exception as exc:
            # IntegrityError de SQLite → DNI duplicado (detectado por nombre de tipo)
            if type(exc).__name__ == "IntegrityError":
                self._registrar_intento_rechazado({"dni": ["DNI ya registrado"]}, ahora)
                raise DniDuplicadoError(f"El DNI {dto.dni} ya existe") from exc
            raise

        dosaje_dto = dosaje_a_dto(dosaje) if dosaje else None
        return nino_a_dto(nino), dosaje_dto

    def _registrar_intento_rechazado(
        self, errores: dict[str, list[str]], ahora: datetime
    ) -> None:
        codigos = [k for k, v in errores.items() if v]
        intento = IntentoRegistro.nuevo(
            operacion="CREAR_NINO",
            resultado="RECHAZADO",
            codigos_error=codigos,
            ahora=ahora,
        )
        try:
            with self._uow_factory() as uow:
                uow.intentos.guardar(intento)
        except Exception:
            pass  # el registro de auditoría no debe bloquear la respuesta de error
