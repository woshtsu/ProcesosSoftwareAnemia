"""CP-73 a CP-82: casos de uso del Incremento 2 (agenda y alertas) con el repositorio en memoria.

Escenario común (hoy = 28-sep-2026, Hb 13.5 g/dL a 3 720 m = sin anemia salvo donde se indica):
  * V (Palmayoc): primera evaluación el 12-sep-2025 a los 6 meses; no volvió. DHc1 (9 m), DHc2 (12 m) y DHx (15 m)
    vencidos hace 262, 172 y 80 días.
  * T (Llacuas): anemia moderada el 1-jul-2026; el C1M venció el 31-ago (28 días); su DHc2 vence en 3 días.
  * M (Chongos Alto): DHx de 15 meses vencido hace 8 días (prioridad media).
  * B (Huaycha): DHx de 15 meses vencido hace 7 días (prioridad baja).
  * A (Palmayoc): como V pero con alta: no genera alertas.
"""

from datetime import date

import pytest

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.application.servicio_agenda import ServicioAgenda
from app.application.servicio_alertas import ServicioAlertas
from app.application.servicio_expediente import ServicioExpediente
from app.domain.model.agenda import EstadoControl
from app.domain.model.errores import ErrorValidacion, NoEncontrado
from tests.conftest import RelojFijo, datos_eval, datos_nino


def registrar(servicio, dni, nacimiento, fecha_eval, comunidad, hb=13.5):
    return servicio.registrar_nino(
        datos_nino(dni=dni, fecha_nacimiento=nacimiento, comunidad=comunidad),
        datos_eval(fecha=fecha_eval, hemoglobina_observada=hb),
        "a",
    )


@pytest.fixture
def escenario(servicio):
    ninos = {
        "V": registrar(servicio, "70000001", date(2025, 3, 10), date(2025, 9, 12), "Palmayoc"),
        "T": registrar(servicio, "70000002", date(2025, 9, 1), date(2026, 7, 1), "Llacuas", hb=11.0),
        "M": registrar(servicio, "70000003", date(2025, 5, 21), date(2026, 8, 1), "Chongos Alto"),
        "B": registrar(servicio, "70000004", date(2025, 5, 22), date(2026, 8, 1), "Huaycha"),
        "A": registrar(servicio, "70000005", date(2025, 3, 10), date(2025, 9, 12), "Palmayoc"),
    }
    servicio.actualizar_datos(ninos["A"].id, {"estado": "ALTA"}, "a")
    return servicio, ninos


@pytest.fixture
def alertas(escenario, reloj):
    return ServicioAlertas(escenario[0].repo, reloj)


def test_cp73_agenda_de_un_nino_desde_su_expediente(escenario, reloj):
    servicio, ninos = escenario
    agenda = ServicioAgenda(servicio.repo, reloj).generar_agenda(ninos["V"].id)
    assert agenda.nino_id == ninos["V"].id and agenda.fecha_referencia == date(2026, 9, 28)
    assert (agenda.resumen.cumplidos, agenda.resumen.vencidos) == (1, 3)
    vencidos = [(c.codigo, c.dias_vencido) for c in agenda.controles if c.estado == EstadoControl.VENCIDO]
    assert vencidos == [("DHc1", 262), ("DHc2", 172), ("DHx", 80)]


def test_cp74_agenda_de_un_nino_inexistente_es_no_encontrado(escenario, reloj):
    with pytest.raises(NoEncontrado):
        ServicioAgenda(escenario[0].repo, reloj).generar_agenda("no-existe")


def test_cp75_agenda_usa_el_reloj_inyectado(escenario):
    servicio, ninos = escenario
    antes = ServicioAgenda(servicio.repo, RelojFijo(date(2026, 1, 8))).generar_agenda(ninos["V"].id)
    assert antes.resumen.vencidos == 0  # el DHc1 de 9 meses vence el 9-ene-2026


def test_cp76_controles_vencidos_ordenados_por_prioridad_y_atraso(alertas):
    lista = alertas.listar_controles_vencidos()
    assert [(a.dni, a.control.codigo, a.control.dias_vencido, a.prioridad.value) for a in lista] == [
        ("70000001", "DHc1", 262, "ALTA"),
        ("70000001", "DHc2", 172, "ALTA"),
        ("70000001", "DHx", 80, "ALTA"),
        ("70000002", "C1M", 28, "ALTA"),  # tratamiento: siempre alta
        ("70000003", "DHx", 8, "MEDIA"),
        ("70000004", "DHx", 7, "BAJA"),
    ]
    assert lista[3].ultima_clasificacion.value == "MODERADA"


def test_cp77_los_ninos_con_alta_no_generan_alertas(alertas):
    assert "70000005" not in {a.dni for a in alertas.listar_controles_vencidos()}


@pytest.mark.parametrize(
    "comunidad, esperados",
    [
        ("Huaycha", {"70000004"}),
        ("  llacuas ", {"70000002"}),  # sin distinguir mayúsculas ni espacios
        ("CHONGOS ALTO", {"70000003"}),
        ("Inexistente", set()),
    ],
)
def test_cp78_filtro_por_comunidad(alertas, comunidad, esperados):
    assert {a.dni for a in alertas.listar_controles_vencidos(comunidad=comunidad)} == esperados


def test_cp79_filtro_por_prioridad_y_combinado(alertas):
    assert [a.dni for a in alertas.listar_controles_vencidos(prioridad="MEDIA")] == ["70000003"]
    assert [a.dni for a in alertas.listar_controles_vencidos(prioridad="BAJA")] == ["70000004"]
    assert len(alertas.listar_controles_vencidos(prioridad="ALTA")) == 4
    assert alertas.listar_controles_vencidos(comunidad="Palmayoc", prioridad="BAJA") == []
    assert len(alertas.listar_controles_vencidos(comunidad="palmayoc", prioridad="ALTA")) == 3
    with pytest.raises(ErrorValidacion) as e:
        alertas.listar_controles_vencidos(prioridad="URGENTE")
    assert e.value.errores[0].campo == "prioridad"


def test_cp80_resumen_de_alertas(alertas):
    r = alertas.resumen_alertas()
    assert r.total_vencidos == 6 and r.ninos_con_vencidos == 4
    assert r.por_prioridad == {"ALTA": 4, "MEDIA": 1, "BAJA": 1}
    assert r.proximos_7_dias == 1  # el DHc2 de T vence el 1-oct (3 días)


class RepositorioContador(RepositorioEnMemoria):
    """Cuenta las consultas al repositorio para demostrar que no hay patrón N+1."""

    def __init__(self):
        super().__init__()
        self.llamadas = {"listar": 0, "obtener": 0, "obtener_por_dni": 0, "obtener_varios": 0}

    def listar(self, estado=None, texto=None):
        self.llamadas["listar"] += 1
        return super().listar(estado, texto)

    def obtener(self, nino_id):
        self.llamadas["obtener"] += 1
        return super().obtener(nino_id)

    def obtener_por_dni(self, dni):
        self.llamadas["obtener_por_dni"] += 1
        return super().obtener_por_dni(dni)

    def obtener_varios(self, ids):
        self.llamadas["obtener_varios"] += 1
        return super().obtener_varios(ids)


def test_cp81_las_alertas_se_calculan_con_una_sola_consulta_por_lotes(reloj):
    repo = RepositorioContador()
    servicio = ServicioExpediente(repo, reloj)
    for i in range(20):
        registrar(servicio, f"7100{i:04d}", date(2025, 3, 10), date(2025, 9, 12), "Palmayoc")
    repo.llamadas = dict.fromkeys(repo.llamadas, 0)
    alertas = ServicioAlertas(repo, reloj)
    assert len(alertas.listar_controles_vencidos()) == 60
    assert alertas.resumen_alertas().ninos_con_vencidos == 20
    assert repo.llamadas == {"listar": 2, "obtener": 0, "obtener_por_dni": 0, "obtener_varios": 0}  # 1 por operación
    repo.llamadas = dict.fromkeys(repo.llamadas, 0)
    servicio.listar_seguimiento()
    assert repo.llamadas["listar"] == 1 and repo.llamadas["obtener"] == 0


def test_cp82_seguimiento_marca_atrasado_solo_con_controles_vencidos(escenario):
    servicio, _ = escenario
    filas = {f["nino"].dni: f for f in servicio.listar_seguimiento()}
    assert "70000005" not in filas  # con alta: no aparece en el listado de activos
    assert (filas["70000001"]["control_atrasado"], filas["70000001"]["controles_vencidos"]) == (True, 3)
    assert (filas["70000002"]["control_atrasado"], filas["70000002"]["controles_vencidos"]) == (True, 1)
    # Un niño evaluado hace 80 días ya no es «atrasado» por la heurística de 30 días: depende de la agenda normativa.
    al_dia = registrar(servicio, "70000006", date(2026, 3, 28), date(2026, 7, 10), "Palmayoc")
    fila = {f["nino"].id: f for f in servicio.listar_seguimiento()}[al_dia.id]
    assert fila["dias_desde_ultimo_control"] == 80
    assert (fila["control_atrasado"], fila["controles_vencidos"]) == (False, 0)
