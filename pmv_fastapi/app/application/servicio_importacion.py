"""Caso de uso: importar un dataset externo anonimizado como niños de origen DATASET_DIRESA_JUNIN (ADR-009).

Recibe registros ya leídos y limpiados (``RegistroImportado``), aplica las reglas del dominio a cada evaluación y
persiste por el puerto de salida, en lotes. No inventa datos: peso y talla quedan en ``None`` porque el dataset no los
trae, y una evaluación fuera de los rangos del dominio (o de una edad de 60 meses o más) se descarta y se cuenta.

Los identificadores se derivan del código seudónimo (UUID v5), de modo que importar dos veces el mismo registro produce
el mismo niño y la misma evaluación: la importación es reproducible.
"""

import uuid
from collections import Counter
from collections.abc import Iterable
from datetime import UTC, date, datetime, time

from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.importacion import RegistroImportado, ResultadoImportacion, TipoEvaluacionImportada
from app.domain.model.origen import OrigenDatos
from app.domain.model.tiempo import ZONA_PERU, edad_en_meses
from app.domain.service import reglas_clinicas as rc
from app.domain.service.validaciones import validar_datos_evaluacion, validar_datos_nino
from app.ports.inbound.importacion import ImportarDataset
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos

USUARIO_IMPORTACION = "importador.dataset-diresa"
NAMESPACE_IDS = uuid.UUID("5b0d6f4a-3c1e-4e7a-9d2b-8a1f0c6e2d11")
TAMANO_LOTE = 500

# Motivos de descarte de una evaluación o de un niño (claves del reporte).
DESCARTE_ANTES_DE_NACER = "evaluacion_anterior_al_nacimiento"
DESCARTE_FECHA_POSTERIOR = "evaluacion_posterior_a_la_fecha_de_referencia"
DESCARTE_EDAD = "evaluacion_con_edad_de_60_meses_o_mas"
DESCARTE_HEMOGLOBINA = "evaluacion_con_hemoglobina_fuera_de_rango"
DESCARTE_NINO_INVALIDO = "nino_con_datos_invalidos"
DESCARTE_SIN_EVALUACIONES = "nino_sin_evaluaciones_validas"


def _mediodia_utc(dia: date) -> datetime:
    """Instante (UTC) del mediodía en Perú de un día: marca de creación coherente con la fecha clínica."""
    return datetime.combine(dia, time(12, 0), tzinfo=ZONA_PERU).astimezone(UTC)


def _motivo_descarte(registro: RegistroImportado, fecha: date, hemoglobina: float, hoy: date) -> str | None:
    """Motivo por el que una evaluación no entra al dominio, o None si es válida (reglas de ``validaciones``)."""
    if fecha < registro.fecha_nacimiento:
        return DESCARTE_ANTES_DE_NACER
    if fecha > hoy:
        return DESCARTE_FECHA_POSTERIOR
    if edad_en_meses(registro.fecha_nacimiento, fecha) > rc.EDAD_MAX_MESES:
        return DESCARTE_EDAD
    datos = {"fecha": fecha, "hemoglobina_observada": hemoglobina, "peso_kg": None, "talla_cm": None}
    errores = validar_datos_evaluacion(datos, registro.fecha_nacimiento, hoy, antropometria_obligatoria=False)
    return DESCARTE_HEMOGLOBINA if errores else None


class ServicioImportacion(ImportarDataset):
    def __init__(self, repo: RepositorioNinos, reloj: Reloj, tamano_lote: int = TAMANO_LOTE):
        self.repo = repo
        self.reloj = reloj
        self.tamano_lote = tamano_lote

    def contar_importados(self) -> int:
        return self.repo.contar_por_origen(OrigenDatos.DATASET_DIRESA_JUNIN)

    def eliminar_importados(self) -> int:
        return self.repo.eliminar_por_origen(OrigenDatos.DATASET_DIRESA_JUNIN)

    def importar(self, registros: Iterable[RegistroImportado]) -> ResultadoImportacion:
        hoy = self.reloj.hoy()
        resultado = ResultadoImportacion()
        descartes: Counter[str] = Counter()
        por_tipo: Counter[str] = Counter()
        provincias: Counter[str] = Counter()
        matriz: dict[str, Counter[str]] = {}
        lote: list[Nino] = []
        for registro in registros:
            resultado.registros_recibidos += 1
            descartes.update(registro.descartes_lectura)
            nino = self._construir(registro, hoy, descartes)
            if nino is None:
                resultado.ninos_omitidos += 1
                continue
            lote.append(nino)
            resultado.ninos_con_alta_por_edad += 1 if nino.estado == "ALTA" else 0
            provincias[nino.provincia or "SIN_DATO"] += 1
            tipos = {_id_evaluacion(registro.codigo_origen, e.tipo): e.tipo for e in registro.evaluaciones}
            for ev in nino.evaluaciones:
                por_tipo[tipos[ev.id].value] += 1
                if tipos[ev.id] == TipoEvaluacionImportada.DIAGNOSTICO:
                    matriz.setdefault(ev.clasificacion_origen or "SIN_DATO", Counter())[ev.clasificacion.value] += 1
            if len(lote) >= self.tamano_lote:
                resultado.ninos_importados += self.repo.guardar_varios(lote)
                lote = []
        if lote:
            resultado.ninos_importados += self.repo.guardar_varios(lote)
        resultado.evaluaciones_importadas = dict(por_tipo)
        resultado.descartes = dict(descartes)
        resultado.matriz_concordancia = {k: dict(v) for k, v in matriz.items()}
        resultado.ninos_por_provincia = dict(provincias)
        return resultado

    def _construir(self, registro: RegistroImportado, hoy: date, descartes: Counter[str]) -> Nino | None:
        """Niño de dominio con sus evaluaciones válidas; None si el niño o todas sus evaluaciones se descartan."""
        datos = {
            "establecimiento": registro.establecimiento,
            "distrito": registro.distrito,
            "comunidad": registro.comunidad,
            "altitud_m": registro.altitud_m,
        }
        if registro.fecha_nacimiento > hoy or [
            e for e in validar_datos_nino(datos, hoy, OrigenDatos.DATASET_DIRESA_JUNIN) if e.campo != "fecha_nacimiento"
        ]:
            descartes[DESCARTE_NINO_INVALIDO] += 1
            return None
        evaluaciones = self._evaluaciones_validas(registro, hoy, descartes)
        if not evaluaciones:
            descartes[DESCARTE_SIN_EVALUACIONES] += 1
            return None
        primera = evaluaciones[0].fecha
        edad_hoy = edad_en_meses(registro.fecha_nacimiento, hoy)
        nino = Nino(
            id=str(uuid.uuid5(NAMESPACE_IDS, registro.codigo_origen)),
            dni=None,
            nombres=None,
            apellidos=None,
            sexo=None,
            fecha_nacimiento=registro.fecha_nacimiento,
            establecimiento=registro.establecimiento,
            distrito=registro.distrito,
            comunidad=registro.comunidad,
            altitud_m=registro.altitud_m,
            tutor_nombre=None,
            registrado_por=USUARIO_IMPORTACION,
            estado="ALTA" if edad_hoy > rc.EDAD_MAX_MESES else "ACTIVO",  # fuera de la población objetivo
            origen=OrigenDatos.DATASET_DIRESA_JUNIN,
            codigo_origen=registro.codigo_origen,
            red=registro.red,
            microred=registro.microred,
            provincia=registro.provincia,
            creado_en=_mediodia_utc(primera),
            actualizado_en=_mediodia_utc(primera),
        )
        for ev in evaluaciones:
            ev.nino_id = nino.id
        nino.evaluaciones = evaluaciones
        return nino

    def _evaluaciones_validas(
        self, registro: RegistroImportado, hoy: date, descartes: Counter[str]
    ) -> list[Evaluacion]:
        validas = []
        for origen in sorted(registro.evaluaciones, key=lambda e: e.fecha):
            motivo = _motivo_descarte(registro, origen.fecha, origen.hemoglobina_observada, hoy)
            if motivo:
                descartes[motivo] += 1
                continue
            ev = Evaluacion(
                id=_id_evaluacion(registro.codigo_origen, origen.tipo),
                fecha=origen.fecha,
                hemoglobina_observada=origen.hemoglobina_observada,
                peso_kg=None,  # el dataset no registra peso ni talla: no se inventan
                talla_cm=None,
                altitud_m=registro.altitud_m,
                edad_meses=edad_en_meses(registro.fecha_nacimiento, origen.fecha),
                registrado_por=USUARIO_IMPORTACION,
                creado_en=_mediodia_utc(origen.fecha),
                clasificacion_origen=origen.clasificacion_origen,
            )
            rc.aplicar_reglas_clinicas(ev)
            validas.append(ev)
        return validas


def _id_evaluacion(codigo: str, tipo: TipoEvaluacionImportada) -> str:
    return str(uuid.uuid5(NAMESPACE_IDS, f"{codigo}:{tipo.value}"))
