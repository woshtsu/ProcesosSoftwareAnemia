"""CP-143 a CP-145: orden y totales de la agenda del personal (HIST-2.3). Dominio puro, sin repositorio."""

from datetime import date

from app.domain.model.agenda import EstadoControl
from app.domain.model.alertas import Prioridad
from app.domain.service.agenda import generar_agenda
from app.domain.service.agenda_personal import construir_agenda_personal
from tests.conftest import nino_de

DIA = date(2026, 9, 10)  # DHx de 6 meses de los niños nacidos el 10-mar-2026 y C1M de la anemia del 10-ago-2026
HOY = date(2026, 10, 25)  # 45 días después: los controles del 10-sep llevan 15 días vencidos (ventana de 30 días)


def agendas(*ninos, hoy=HOY):
    return [(n, generar_agenda(n, hoy)) for n in ninos]


def escenario():
    cumplido = nino_de(
        date(2026, 3, 10), [(date(2026, 3, 12), "NO_APLICA"), (date(2026, 9, 12), "SIN_ANEMIA")], nombres="Zoila"
    )
    vencido_medio = nino_de(date(2026, 3, 10), [(date(2026, 3, 12), "NO_APLICA")], nombres="Beto")
    tratamiento = nino_de(date(2025, 1, 1), [(date(2026, 8, 10), "LEVE")], nombres="Ana", dni="71234560")
    return cumplido, vencido_medio, tratamiento


def test_cp143_dentro_del_dia_primero_los_vencidos_por_prioridad_y_al_final_los_cumplidos():
    cumplido, vencido_medio, tratamiento = escenario()
    ag = construir_agenda_personal(agendas(cumplido, vencido_medio, tratamiento), DIA, DIA, HOY)
    (dia,) = ag.dias
    assert [(i.nombre_completo.split()[0], i.control.codigo, i.control.estado, i.prioridad) for i in dia.items] == [
        ("Ana", "C1M", EstadoControl.VENCIDO, Prioridad.ALTA),  # tratamiento: prioridad alta
        ("Beto", "DHx", EstadoControl.VENCIDO, Prioridad.MEDIA),  # 15 días de atraso
        ("Zoila", "DHx", EstadoControl.CUMPLIDO, None),  # cumplidos al final y sin prioridad
    ]
    assert (dia.total, dia.vencidos, dia.pendientes, dia.cumplidos, dia.con_inasistencia) == (3, 2, 0, 1, 0)
    assert (ag.resumen.total, ag.resumen.ninos) == (3, 3)


def test_cp144_los_controles_cerrados_por_recuperacion_no_se_listan_pero_si_los_pendientes():
    # Anemia leve el 10-jun-2026 y recuperación el 10-jul: el C3M (10-sep) y el C6M (10-dic) aún no vencían y se cierran.
    recuperado = nino_de(date(2025, 3, 10), [(date(2026, 6, 10), "LEVE"), (date(2026, 7, 10), "SIN_ANEMIA")])
    hoy = date(2026, 9, 1)
    ag_nino = generar_agenda(recuperado, hoy)
    assert {c.estado for c in ag_nino.controles if c.codigo in ("C3M", "C6M")} == {EstadoControl.CERRADO_RECUPERADO}
    ag = construir_agenda_personal([(recuperado, ag_nino)], date(2026, 9, 1), date(2026, 12, 31), hoy)
    listados = {i.control.codigo for d in ag.dias for i in d.items}
    assert "C3M" not in listados and "C6M" not in listados
    assert ag.resumen.total == sum(d.total for d in ag.dias)


def test_cp145_los_dias_sin_controles_figuran_con_totales_en_cero_y_solo_cuentan_los_del_rango():
    cumplido, _, _ = escenario()
    ag = construir_agenda_personal(agendas(cumplido), date(2026, 9, 8), date(2026, 9, 12), HOY, comunidad="Palmayoc")
    assert [d.fecha.day for d in ag.dias] == [8, 9, 10, 11, 12]
    assert [d.total for d in ag.dias] == [0, 0, 1, 0, 0]
    assert ag.comunidad == "Palmayoc" and ag.establecimiento is None and ag.resumen.total == 1
    vacio = construir_agenda_personal([], date(2026, 9, 8), date(2026, 9, 8), HOY)
    assert vacio.resumen.total == 0 and vacio.dias[0].items == [] and vacio.comunidades_disponibles == []
