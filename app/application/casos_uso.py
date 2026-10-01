"""Casos de uso del Incremento 1 (PMV).

HU-01 Registrar niño con evaluación inicial
HU-02 Consultar y actualizar expediente (incluye registrar nuevos controles)
HU-03 Validar datos según reglas clínicas (vista previa)
HU-04 Listar niños en seguimiento con estado de control
HU-05 Reporte del periodo
"""

from collections import Counter
from dataclasses import dataclass
from datetime import date

from app.application.puertos import Reloj, RepositorioNinos
from app.domain import reglas_clinicas as rc
from app.domain.entidades import (
    Evaluacion,
    Nino,
    ahora,
    edad_en_meses,
    exigir,
    validar_datos_evaluacion,
    validar_datos_nino,
)
from app.domain.errores import ErrorCampo, ErrorValidacion, NoEncontrado, RegistroDuplicado

CAMPOS_EDITABLES = ("comunidad", "distrito", "establecimiento", "altitud_m", "tutor_nombre", "tutor_celular", "estado")
DIAS_SIN_CONTROL_ALERTA = 30  # referencia visual del PMV; la agenda normativa llega en INC-2


class ServicioExpediente:
    def __init__(self, repo: RepositorioNinos, reloj: Reloj):
        self.repo = repo
        self.reloj = reloj

    # HU-03 -------------------------------------------------------------
    def previsualizar_evaluacion(self, fecha_nacimiento: date, altitud_m: float, datos_eval: dict) -> Evaluacion:
        hoy = self.reloj.hoy()
        exigir(validar_datos_evaluacion(datos_eval, fecha_nacimiento, hoy))
        evaluacion = Evaluacion(
            fecha=datos_eval["fecha"],
            hemoglobina_observada=datos_eval["hemoglobina_observada"],
            peso_kg=datos_eval["peso_kg"],
            talla_cm=datos_eval["talla_cm"],
            altitud_m=altitud_m,
            edad_meses=edad_en_meses(fecha_nacimiento, datos_eval["fecha"]),
            registrado_por="vista-previa",
        )
        evaluacion.calcular()
        return evaluacion

    # HU-01 -------------------------------------------------------------
    def registrar_nino(self, datos_nino: dict, datos_eval: dict, usuario: str) -> Nino:
        hoy = self.reloj.hoy()
        errores = validar_datos_nino(datos_nino, hoy)
        fn = datos_nino.get("fecha_nacimiento") if not any(e.campo == "fecha_nacimiento" for e in errores) else None
        errores += validar_datos_evaluacion(datos_eval, fn, hoy)
        exigir(errores)
        if self.repo.obtener_por_dni(datos_nino["dni"].strip()):
            raise RegistroDuplicado(f"Ya existe un niño registrado con DNI {datos_nino['dni']}.")

        nino = Nino(
            dni=datos_nino["dni"].strip(),
            nombres=datos_nino["nombres"].strip(),
            apellidos=datos_nino["apellidos"].strip(),
            sexo=datos_nino["sexo"],
            fecha_nacimiento=datos_nino["fecha_nacimiento"],
            establecimiento=datos_nino["establecimiento"].strip(),
            distrito=datos_nino["distrito"].strip(),
            comunidad=datos_nino["comunidad"].strip(),
            altitud_m=datos_nino["altitud_m"],
            tutor_nombre=datos_nino["tutor_nombre"].strip(),
            tutor_celular=(datos_nino.get("tutor_celular") or None),
            registrado_por=usuario,
        )
        self.repo.guardar(nino)
        self._crear_evaluacion(nino, datos_eval, usuario)
        return self.repo.obtener(nino.id)

    # HU-02 -------------------------------------------------------------
    def consultar(self, nino_id: str) -> Nino:
        nino = self.repo.obtener(nino_id)
        if not nino:
            raise NoEncontrado("No existe el expediente solicitado.")
        return nino

    def consultar_por_dni(self, dni: str) -> Nino:
        nino = self.repo.obtener_por_dni(dni)
        if not nino:
            raise NoEncontrado(f"No existe un niño registrado con DNI {dni}.")
        return nino

    def actualizar_datos(self, nino_id: str, cambios: dict, usuario: str) -> Nino:
        nino = self.consultar(nino_id)
        desconocidos = [c for c in cambios if c not in CAMPOS_EDITABLES]
        if desconocidos:
            raise ErrorValidacion([ErrorCampo(c, "Campo no editable en el expediente.") for c in desconocidos])
        propuesta = {
            "dni": nino.dni,
            "nombres": nino.nombres,
            "apellidos": nino.apellidos,
            "sexo": nino.sexo,
            "fecha_nacimiento": nino.fecha_nacimiento,
            "establecimiento": nino.establecimiento,
            "distrito": nino.distrito,
            "comunidad": nino.comunidad,
            "altitud_m": nino.altitud_m,
            "tutor_nombre": nino.tutor_nombre,
            "tutor_celular": nino.tutor_celular,
        }
        propuesta.update({k: v for k, v in cambios.items() if k != "estado"})
        errores = [e for e in validar_datos_nino(propuesta, self.reloj.hoy()) if e.campo != "fecha_nacimiento"]
        if "estado" in cambios and cambios["estado"] not in ("ACTIVO", "ALTA"):
            errores.append(ErrorCampo("estado", "El estado debe ser ACTIVO o ALTA."))
        exigir(errores)
        for campo, valor in cambios.items():
            if campo == "tutor_celular":
                valor = valor or None
            setattr(nino, campo, valor)
        nino.actualizado_en = ahora()
        self.repo.actualizar(nino)
        return self.repo.obtener(nino.id)

    def registrar_evaluacion(self, nino_id: str, datos_eval: dict, usuario: str) -> Nino:
        nino = self.consultar(nino_id)
        exigir(validar_datos_evaluacion(datos_eval, nino.fecha_nacimiento, self.reloj.hoy()))
        self._crear_evaluacion(nino, datos_eval, usuario)
        return self.repo.obtener(nino.id)

    # HU-04 -------------------------------------------------------------
    def listar_seguimiento(
        self, estado: str | None = "ACTIVO", texto: str | None = None, clasificacion: str | None = None
    ) -> list[dict]:
        hoy = self.reloj.hoy()
        filas = []
        for nino in self.repo.listar(estado=estado, texto=texto):
            ultima = nino.ultima_evaluacion
            dias = (hoy - ultima.fecha).days if ultima else None
            fila = {
                "nino": nino,
                "ultima_evaluacion": ultima,
                "dias_desde_ultimo_control": dias,
                "control_atrasado": dias is not None and dias > DIAS_SIN_CONTROL_ALERTA,
                "edad_meses": edad_en_meses(nino.fecha_nacimiento, hoy),
            }
            if clasificacion and (not ultima or ultima.clasificacion.value != clasificacion):
                continue
            filas.append(fila)
        orden = {rc.Clasificacion.SEVERA: 0, rc.Clasificacion.MODERADA: 1, rc.Clasificacion.LEVE: 2}
        filas.sort(
            key=lambda f: (
                orden.get(f["ultima_evaluacion"].clasificacion, 3) if f["ultima_evaluacion"] else 4,
                -(f["dias_desde_ultimo_control"] or 0),
            )
        )
        return filas

    # HU-05 -------------------------------------------------------------
    def reporte_periodo(self, desde: date, hasta: date) -> dict:
        if desde > hasta:
            raise ErrorValidacion([ErrorCampo("desde", "La fecha inicial debe ser anterior o igual a la final.")])
        evaluaciones = self.repo.evaluaciones_en_periodo(desde, hasta)
        nuevos = self.repo.ninos_registrados_en_periodo(desde, hasta)
        por_clasificacion = Counter(e.clasificacion.value for e in evaluaciones)
        ninos_evaluados = {e.nino_id for e in evaluaciones}
        con_anemia = {e.nino_id for e in evaluaciones if e.tiene_anemia}
        por_comunidad: dict[str, dict] = {}
        for e in evaluaciones:
            nino = self.repo.obtener(e.nino_id)
            fila = por_comunidad.setdefault(
                nino.comunidad, {"comunidad": nino.comunidad, "evaluaciones": 0, "con_anemia": 0}
            )
            fila["evaluaciones"] += 1
            fila["con_anemia"] += 1 if e.tiene_anemia else 0
        return {
            "desde": desde,
            "hasta": hasta,
            "ninos_registrados": len(nuevos),
            "evaluaciones_realizadas": len(evaluaciones),
            "ninos_evaluados": len(ninos_evaluados),
            "ninos_con_anemia": len(con_anemia),
            "por_clasificacion": {c.value: por_clasificacion.get(c.value, 0) for c in rc.Clasificacion},
            "por_comunidad": sorted(por_comunidad.values(), key=lambda f: f["comunidad"]),
            "evaluaciones": evaluaciones,
        }

    # ---------------------------------------------------------------------
    def _crear_evaluacion(self, nino: Nino, datos_eval: dict, usuario: str) -> Evaluacion:
        evaluacion = Evaluacion(
            nino_id=nino.id,
            fecha=datos_eval["fecha"],
            hemoglobina_observada=datos_eval["hemoglobina_observada"],
            peso_kg=datos_eval["peso_kg"],
            talla_cm=datos_eval["talla_cm"],
            altitud_m=nino.altitud_m,
            edad_meses=edad_en_meses(nino.fecha_nacimiento, datos_eval["fecha"]),
            registrado_por=usuario,
        )
        evaluacion.calcular()
        return self.repo.agregar_evaluacion(evaluacion)


@dataclass
class RelojSistema:
    def hoy(self) -> date:
        return date.today()
