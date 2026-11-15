#!/usr/bin/env python
"""Cobertura de RF por pruebas automatizadas y criterios de aceptación Dado-Cuando-Entonces verificados (G-02, V7 proxy).

Complementa a M2.1 (que usa capturas): aquí se calcula, por RF y por versión,
  * qué pruebas automatizadas (archivo::prueba) lo verifican (mapa curado por QA, validado contra el código por AST);
  * % de RF con >= 1 prueba automatizada y con >= 1 prueba E2E;
  * % de criterios de aceptación Dado-Cuando-Entonces (DCE) cuyas pruebas están TODAS en verde, EJECUTANDO las pruebas
    de cada versión con pytest (JUnit XML) y leyendo el resultado real.
  * como verificación cruzada, las pruebas que "mencionan" los endpoints del RF según búsqueda por patrón (grep).

Los criterios DCE los redactó QA a partir de la descripción de cada RF (spec S9), de las historias HIST-1.x del
entregable S5 y de ADR-007; la guía S5 no trae criterios DCE para el PMV FastAPI. Pueden sustituirse por los de las fichas
de prueba sin cambiar el método.

Uso:  python m21_cobertura_rf.py [--version v1.0|v1.5|v2.0|todas] [--sin-ejecutar]   (se conservan en el JSON las versiones no recalculadas)
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import comun as c

PY = os.getenv("PY", sys.executable)
A = "tests/integracion/test_api.py"
Z = "tests/integracion/test_zona_horaria.py"
UE = "tests/unitarias/test_entidades.py"
UR = "tests/unitarias/test_reglas_clinicas.py"
UC = "tests/unitarias/test_casos_uso.py"
E = "tests/e2e/test_interfaz.py"
A2 = "tests/integracion/test_api_inc2.py"
UA = "tests/unitarias/test_agenda.py"
UAL = "tests/unitarias/test_alertas.py"
UC2 = "tests/unitarias/test_casos_uso_inc2.py"
UR2 = "tests/unitarias/test_regresion_inc2.py"
A3 = "tests/integracion/test_api_inc2_final.py"
UAP = "tests/unitarias/test_agenda_personal.py"
UAS = "tests/unitarias/test_asistencia.py"
UC3 = "tests/unitarias/test_casos_uso_inc2_final.py"
E3 = "tests/e2e/test_interfaz_inc2_final.py"
UOD = "tests/unitarias/test_origen_dataset.py"


def t(archivo: str, *nombres: str) -> list[str]:
    return [f"{archivo}::{n}" for n in nombres]


# Criterios DCE por RF. Cada criterio: (id, texto Dado-Cuando-Entonces, [pruebas])
COMUN = {
    "RF-01": [
        ("RF-01-C1", "Dado un niño con datos válidos y su evaluación inicial, cuando se registra (POST /api/ninos), entonces responde 201 con un único expediente y la evaluación clasificada.",
         t(A, "test_registro_exitoso_devuelve_expediente") + t(UC, "test_registrar_nino_crea_expediente_con_evaluacion_clasificada")),
        ("RF-01-C2", "Dado un DNI ya registrado, cuando se intenta registrar de nuevo, entonces responde 409 y no se duplica el expediente.",
         t(A, "test_registro_duplicado_devuelve_409") + t(UC, "test_registro_duplicado_por_dni_se_rechaza")),
        ("RF-01-C3", "Dado un dato inválido o ausente, cuando se registra, entonces responde 422 con un mensaje por campo y no se guarda nada.",
         t(A, "test_datos_fuera_de_rango_devuelven_422_con_mensajes_en_espanol", "test_formato_invalido_devuelve_422_en_espanol")
         + t(UC, "test_registro_invalido_acumula_errores_de_nino_y_evaluacion") + t(UE, "test_dni_debe_tener_8_digitos", "test_campos_obligatorios_vacios")),
        ("RF-01-C4", "Dado el formulario de registro con datos válidos, cuando el personal pulsa Guardar, entonces la interfaz muestra el expediente creado.",
         t(E, "test_hu01_hu03_registro_con_vista_previa_y_expediente")),
    ],
    "RF-02": [
        ("RF-02-C1", "Dado un niño registrado, cuando se consulta su expediente por id o por DNI, entonces se muestran sus datos y evaluaciones; un id inexistente responde 404.",
         t(A, "test_consultar_expediente_por_id_y_dni") + t(UC, "test_consultar_y_buscar_por_dni")),
        ("RF-02-C2", "Dado un expediente, cuando se actualizan campos editables, entonces se guardan; un cambio inválido se rechaza con mensaje por campo.",
         t(A, "test_actualizar_expediente_y_registrar_control") + t(UC, "test_actualizar_datos_editables", "test_actualizar_rechaza_cambios_invalidos")),
        ("RF-02-C3", "Dado un expediente, cuando se registra un nuevo control, entonces se agrega a la evolución sin perder los anteriores.",
         t(A, "test_actualizar_expediente_y_registrar_control") + t(UC, "test_registrar_nuevo_control")),
        ("RF-02-C4", "Dado el listado de seguimiento, cuando el personal abre un niño, entonces la interfaz muestra la tabla de evaluaciones del expediente.",
         t(E, "test_hu04_seguimiento_y_busqueda")),
    ],
    "RF-03": [
        ("RF-03-C1", "Dado un control sin guardar, cuando se solicita la vista previa, entonces se devuelven la Hb ajustada por altitud y la clasificación, sin persistir nada.",
         t(A, "test_vista_previa_de_validacion") + t(UC, "test_vista_previa_no_guarda") + t(UR, "test_ajuste_por_altitud_segun_ecuacion", "test_hemoglobina_ajustada_resta_el_ajuste")),
        ("RF-03-C2", "Dado un valor de Hb en los límites de los puntos de corte por edad, cuando se clasifica, entonces el resultado respeta los umbrales (SIN_ANEMIA, LEVE, MODERADA, SEVERA, NO_APLICA).",
         t(UR, "test_clasificacion_en_limites_de_los_puntos_de_corte", "test_fuera_de_rango_de_edad_no_aplica") + t(UE, "test_evaluacion_calcula_ajuste_y_clasificacion")),
        ("RF-03-C3", "Dado un valor fuera del rango clínico, cuando se valida, entonces se rechaza con un mensaje comprensible por campo (422).",
         t(UE, "test_evaluacion_fuera_de_rango", "test_mensaje_de_hemoglobina_es_comprensible") + t(A, "test_datos_fuera_de_rango_devuelven_422_con_mensajes_en_espanol")),
        ("RF-03-C4", "Dado un formulario con datos inválidos, cuando se intenta guardar, entonces la interfaz marca los campos y explica el error.",
         t(E, "test_hu03_datos_invalidos_muestran_mensaje_comprensible")),
    ],
    "RF-04": [
        ("RF-04-C1", "Dados niños activos, cuando se lista el seguimiento, entonces se muestran con su última clasificación, ordenados por severidad, con filtros.",
         t(A, "test_listado_de_seguimiento_con_filtros") + t(UC, "test_listar_seguimiento_prioriza_casos_graves_y_filtra")),
        ("RF-04-C2", "Dado el listado, cuando el personal busca por DNI o nombre, entonces la interfaz filtra y permite abrir el expediente.",
         t(E, "test_hu04_seguimiento_y_busqueda")),
    ],
    "RF-05": [
        ("RF-05-C1", "Dado un periodo válido, cuando se solicita el reporte, entonces se entregan conteos por clasificación y comunidad en JSON y en CSV.",
         t(A, "test_reporte_json_y_csv") + t(UC, "test_reporte_del_periodo")),
        ("RF-05-C2", "Dado un registro hecho de noche (hora de Perú), cuando se genera el reporte del día, entonces se cuenta en el día local correcto.",
         t(Z, "test_registro_nocturno_cuenta_en_el_dia_local") + t(UC, "test_reporte_cuenta_registros_nocturnos_en_el_dia_local") + t(UE, "test_fecha_local_usa_hora_de_peru")),
        ("RF-05-C3", "Dado el módulo de reporte, cuando el personal genera el reporte, entonces la interfaz muestra los indicadores del periodo.",
         t(E, "test_hu05_reporte_del_periodo")),
    ],
}
INC2 = {
    "RF-01": [("RF-01-C5", "Dado un DNI o celular con dígitos no ASCII o salto de línea final, cuando se registra o se actualiza, entonces se rechaza (regresión DEF-04).",
               t(A2, "test_cp103_def04_dni_y_celular_solo_digitos_ascii_y_coincidencia_completa") + t(UR2, "test_cp85_def04_dni_solo_acepta_digitos_ascii", "test_cp86_def04_celular_exige_coincidencia_completa_y_digitos_ascii"))],
    "RF-03": [("RF-03-C5", "Dada una vista previa con altitud NaN/absurda o fecha de nacimiento absurda, cuando se solicita, entonces se rechaza con 422 (regresión DEF-05).",
               t(A2, "test_cp104_def05_vista_previa_rechaza_altitudes_invalidas", "test_cp107_nan_o_infinito_en_la_evaluacion_se_rechazan_con_mensaje_claro") + t(UR2, "test_cp87_def05_la_vista_previa_valida_la_altitud"))],
    "RF-04": [("RF-04-C3", "Dado el seguimiento, cuando un niño tiene al menos un control vencido de la agenda normativa, entonces control_atrasado es verdadero y se informa controles_vencidos.",
               t(A2, "test_cp100_listado_de_seguimiento_usa_los_controles_vencidos") + t(UC2, "test_cp82_seguimiento_marca_atrasado_solo_con_controles_vencidos")),
              ("RF-04-C4", "Dada una búsqueda con % o _, cuando se lista, entonces se tratan como texto y no como comodines (regresión DEF-07).",
               t(A2, "test_cp106_def07_la_busqueda_trata_los_comodines_como_texto"))],
    "RF-05": [("RF-05-C4", "Dado un periodo con fechas extremas, cuando se solicita el reporte, entonces responde 422 y no 500 (regresión DEF-03).",
               t(A2, "test_cp102_def03_reporte_con_fechas_extremas_devuelve_422_y_no_500") + t(UR2, "test_cp84_def03_el_servicio_rechaza_el_periodo_extremo"))],
    "RF-06": [
        ("RF-06-C1", "Dado un niño activo, cuando se consulta su agenda, entonces se devuelven los 12 dosajes por edad y los controles de tratamiento con fecha programada y ventana -15/+30 días.",
         t(A2, "test_cp89_agenda_de_un_nino", "test_cp90_campos_de_cada_control") + t(UA, "test_cp46_recien_nacido_tiene_los_12_dosajes_por_edad_pendientes", "test_cp47_fechas_programadas_con_nacimiento_en_fin_de_mes", "test_cp49_ventana_de_cumplimiento_valores_frontera")),
        ("RF-06-C2", "Dada una evaluación con anemia, cuando se genera la agenda, entonces se programan C1M, C3M y C6M, sin reiniciar el calendario y con cierre por recuperación.",
         t(A2, "test_cp91_agenda_de_tratamiento_y_proximo_a_vencer") + t(UA, "test_cp53_anemia_programa_c1m_c3m_c6m_con_suma_segura_de_meses", "test_cp56_episodio_con_recuperacion_cierra_los_controles_pendientes", "test_cp57_controles_ya_vencidos_antes_de_la_recuperacion_siguen_vencidos", "test_cp58_evaluaciones_con_anemia_dentro_del_episodio_no_reinician_el_calendario", "test_cp59_nuevo_episodio_tras_vencer_el_c6m_o_tras_una_recuperacion")),
        ("RF-06-C3", "Dados controles en la frontera de la ventana, cuando se calcula el estado, entonces se distinguen CUMPLIDO, PENDIENTE (con próximo a 7 días) y VENCIDO; no se programan controles de 60 meses o más.",
         t(UA, "test_cp48_la_agenda_empieza_cuando_el_nino_entra_al_sistema", "test_cp50_estados_pendiente_proximo_y_vencido_en_la_frontera", "test_cp61_los_controles_de_tratamiento_no_pasan_de_los_59_meses", "test_cp62_un_dosaje_por_edad_de_60_meses_o_mas_no_se_programa")),
        ("RF-06-C4", "Dado un id inexistente o un niño con alta, cuando se consulta la agenda, entonces responde 404 o aplica=false, respectivamente.",
         t(A2, "test_cp92_agenda_de_nino_inexistente_devuelve_404", "test_cp93_nino_con_alta_no_tiene_agenda") + t(UA, "test_cp63_nino_con_alta_no_tiene_agenda") + t(UC2, "test_cp74_agenda_de_un_nino_inexistente_es_no_encontrado")),
        ("RF-06-C5", "Dado un control pendiente vigente, cuando se registra una evaluación en su ventana, entonces lo cumple (una evaluación cumple a lo sumo un control).",
         t(A2, "test_cp94_registrar_un_control_cumple_el_pendiente_vigente_pero_no_rescata_los_vencidos") + t(UA, "test_cp51_una_evaluacion_cumple_a_lo_sumo_un_control")),
        ("RF-06-C6", "Dado el expediente de un niño, cuando el personal lo abre, entonces la interfaz muestra la sección Agenda de controles (casos especiales incluidos).",
         t(E, "test_cp109_hist21_agenda_de_controles_en_el_expediente", "test_cp110_hist21_agenda_casos_especiales")),
    ],
    "RF-07": [
        ("RF-07-C1", "Dados niños con controles vencidos, cuando se consultan las alertas, entonces se listan ordenadas por prioridad (ALTA, MEDIA, BAJA) y por mayor atraso, con datos para contactar a la familia.",
         t(A2, "test_cp95_controles_vencidos_ordenados_con_los_datos_del_nino") + t(UAL, "test_cp67_prioridad_valores_frontera", "test_cp68_una_alerta_por_control_vencido_con_los_datos_para_contactar_a_la_familia", "test_cp70_orden_por_prioridad_y_luego_por_mayor_atraso") + t(UC2, "test_cp76_controles_vencidos_ordenados_por_prioridad_y_atraso")),
        ("RF-07-C2", "Dados filtros por comunidad y prioridad, cuando se consultan las alertas, entonces se filtran; una prioridad inválida responde 422.",
         t(A2, "test_cp96_filtros_por_comunidad_y_prioridad", "test_cp97_prioridad_invalida_devuelve_422") + t(UC2, "test_cp78_filtro_por_comunidad", "test_cp79_filtro_por_prioridad_y_combinado")),
        ("RF-07-C3", "Dadas las alertas, cuando se pide el resumen, entonces se informan total, por prioridad, niños distintos y próximos a vencer; sin niños, todo en cero.",
         t(A2, "test_cp98_resumen_de_alertas", "test_cp99_sin_ninos_las_alertas_estan_vacias") + t(UAL, "test_cp71_resumen_cuenta_por_prioridad_y_ninos_distintos", "test_cp72_resumen_vacio_incluye_todas_las_prioridades_en_cero") + t(UC2, "test_cp80_resumen_de_alertas")),
        ("RF-07-C4", "Dado un niño con alta, cuando se consultan las alertas, entonces no genera alertas.",
         t(UC2, "test_cp77_los_ninos_con_alta_no_generan_alertas")),
        ("RF-07-C5", "Dada la pestaña Alertas, cuando el personal la abre y filtra, entonces se muestran el resumen, la tabla filtrable y la navegación al expediente; la vista móvil no desborda.",
         t(E, "test_cp111_hist22_pestana_de_alertas_resumen_filtros_y_navegacion", "test_cp112_hist22_vista_movil_sin_desborde_horizontal")),
    ],
}


# Incremento 2 al 100 % (v2.0.0-inc2): RF-08 y RF-09 y complementos de los RF anteriores. Los criterios los redactó QA a partir de
# la descripción de HIST-2.3 y HIST-2.4 (README de pmv_fastapi, sección Interfaz y API) y de los casos de prueba CP-123 a CP-186.
INC2_FINAL = {
    "RF-01": [("RF-01-C6", "Dado el registro desde la aplicación, cuando faltan datos personales o se intenta enviar un origen distinto, entonces el sistema sigue exigiendo todos los campos y fija el origen SISTEMA (los campos opcionales son solo para el dataset DIRESA, ADR-009).",
               t(UOD, "test_cp117_el_registro_desde_el_sistema_sigue_exigiendo_todos_los_campos", "test_cp120_el_registro_desde_el_sistema_es_siempre_origen_sistema") + t(A3, "test_cp172_el_cliente_no_puede_elegir_el_origen_y_el_sistema_sigue_exigiendo_todo", "test_cp173_la_base_exige_los_datos_personales_solo_para_el_origen_sistema"))],
    "RF-04": [("RF-04-C5", "Dado un registro del dataset DIRESA (sin DNI ni nombres), cuando se lista, se busca por su código (DJ-xxxxx) o se abre su expediente, entonces se muestra como «Registro DJ-xxxxx (dataset anonimizado)» con su origen y la severidad del HIS.",
               t(A3, "test_cp170_listado_busqueda_y_expediente_de_un_registro_del_dataset") + t(UOD, "test_cp116_nombre_legible_de_un_registro_del_dataset", "test_cp122_listar_y_buscar_por_codigo_en_memoria") + t(E3, "test_cp185_dataset_aviso_de_fecha_de_referencia_y_registro_sin_nombre"))],
    "RF-06": [("RF-06-C7", "Dado el servidor iniciado con FECHA_REFERENCIA, cuando se calcula la agenda, las alertas, el reporte o el CSV, entonces se usa esa fecha como «hoy» (y /api/salud la informa); sin ella se usa el reloj real de Perú.",
               t(A3, "test_cp161_salud_expone_la_fecha_de_hoy_y_la_de_referencia_si_esta_fijada", "test_cp161_sin_fecha_de_referencia_se_usa_el_reloj_real_y_una_fecha_mal_escrita_se_rechaza", "test_cp171_agenda_alertas_reporte_y_csv_con_registros_del_dataset") + t(UC3, "test_cp142_contexto_con_y_sin_fecha_de_referencia") + t(E3, "test_cp186_dataset_agenda_y_alertas_usan_la_fecha_de_referencia"))],
    "RF-08": [
        ("RF-08-C1", "Dado el personal de salud, cuando consulta la agenda sin indicar fechas, entonces recibe la semana (lunes a domingo) de la fecha de referencia, con totales por día y del rango (cumplidos, pendientes, vencidos).",
         t(A3, "test_cp162_agenda_del_personal_por_defecto_es_la_semana_de_la_fecha_de_referencia", "test_cp163_agenda_del_personal_campos_totales_y_orden_de_un_rango") + t(UC3, "test_cp137_rango_por_defecto_y_validacion", "test_cp138_agenda_por_dia_con_totales_estado_y_prioridad")),
        ("RF-08-C2", "Dado un rango de fechas, cuando se consulta, entonces cada día lista sus controles (vencidos por prioridad primero, cumplidos al final), los días sin controles figuran en cero y no aparecen controles cerrados por recuperación ni niños con alta.",
         t(UAP, "test_cp143_dentro_del_dia_primero_los_vencidos_por_prioridad_y_al_final_los_cumplidos", "test_cp144_los_controles_cerrados_por_recuperacion_no_se_listan_pero_si_los_pendientes", "test_cp145_los_dias_sin_controles_figuran_con_totales_en_cero_y_solo_cuentan_los_del_rango") + t(UC3, "test_cp139_incluye_pendientes_y_cumplidos_ordenados_y_excluye_cerrados_y_altas")),
        ("RF-08-C3", "Dados filtros por establecimiento y/o comunidad, cuando se consulta, entonces solo se listan los controles de esos niños y se devuelven las opciones de filtro disponibles.",
         t(A3, "test_cp164_agenda_del_personal_filtros_y_un_solo_extremo") + t(UC3, "test_cp139_filtros_por_establecimiento_y_comunidad_con_opciones_disponibles")),
        ("RF-08-C4", "Dado un rango inválido (desde posterior a hasta, formato incorrecto o más de 31 días), cuando se consulta, entonces responde 422 con un mensaje claro.",
         t(A3, "test_cp165_agenda_del_personal_rango_invalido_devuelve_422") + t(UC3, "test_cp137_rango_por_defecto_y_validacion")),
        ("RF-08-C5", "Dada la agenda de un rango extenso, cuando se calcula, entonces se hace con una sola carga por lotes (sin patrón N+1).",
         t(UC3, "test_cp141_la_agenda_del_personal_se_calcula_con_una_sola_consulta_por_lotes")),
        ("RF-08-C6", "Dada la pestaña Agenda, cuando el personal elige el rango y los filtros, navega por semanas o escribe un rango inválido, entonces la interfaz muestra el resumen y la tabla por día, el mensaje de error y no desborda en vista móvil.",
         t(E3, "test_cp180_rf08_pestana_agenda_semana_de_la_fecha_de_referencia_resumen_y_filtros", "test_cp181_rf08_rango_invalido_navegacion_por_semanas_y_fecha_de_hoy", "test_cp184_rf08_vista_movil_de_la_agenda_sin_desborde_horizontal")),
    ],
    "RF-09": [
        ("RF-09-C1", "Dado un control pendiente o vencido, cuando se registra «Asistió» (POST .../asistencia), entonces responde 201, el control queda CUMPLIDO y deja de figurar en las alertas.",
         t(UAS, "test_cp123_asistio_cumple_el_control_aunque_no_haya_evaluacion", "test_cp124_asistio_cumple_un_control_vencido_y_la_evaluacion_vinculada_se_le_asigna_a_el") + t(UC3, "test_cp131_registrar_asistio_guarda_usuario_y_fecha_y_cumple_el_control", "test_cp140_la_asistencia_se_refleja_en_la_agenda_del_personal") + t(A3, "test_cp166_registrar_asistencia_y_su_efecto_en_la_agenda_y_las_alertas")),
        ("RF-09-C2", "Dado un control, cuando se registra «No asistió» con su motivo, entonces el control sigue pendiente o vencido con la marca «Inasistencia registrada» y la prioridad de su alerta sube un nivel.",
         t(UAS, "test_cp125_no_asistio_no_cambia_el_estado_solo_lo_marca", "test_cp126_si_despues_una_evaluacion_cumple_el_control_deja_de_figurar_la_inasistencia", "test_cp128_la_inasistencia_registrada_sube_la_prioridad_un_nivel", "test_cp128_la_alerta_de_un_control_con_inasistencia_sube_de_prioridad") + t(UC3, "test_cp132_no_asistio_deja_el_control_vencido_con_marca_y_sube_la_prioridad_de_la_alerta")),
        ("RF-09-C3", "Dado un control con asistencia ya registrada, cumplido o cerrado por recuperación, cuando se intenta registrar de nuevo (también en solicitudes simultáneas), entonces responde 409 y no se duplica.",
         t(UC3, "test_cp133_no_se_registra_dos_veces_el_mismo_control") + t(UAS, "test_cp130_localizar_el_control_registrable_y_sus_conflictos", "test_cp130_un_control_cerrado_por_recuperacion_no_admite_asistencia", "test_cp189_el_repositorio_en_memoria_rechaza_una_asistencia_repetida_como_la_base") + t(A3, "test_cp167_no_se_registra_dos_veces_ni_con_fecha_futura_ni_con_datos_invalidos", "test_cp169_dos_registros_simultaneos_del_mismo_control_dan_un_201_y_el_resto_409", "test_cp174_restricciones_de_la_asistencia_y_borrado_en_cascada")),
        ("RF-09-C4", "Dados datos inválidos (fecha programada futura, «No asistió» sin motivo) o un niño o control inexistente, cuando se registra, entonces responde 422 o 404 con mensaje claro y no se guarda nada.",
         t(UAS, "test_cp127_una_asistencia_que_no_corresponde_a_ningun_control_se_ignora", "test_cp129_validacion_de_los_datos_de_la_asistencia", "test_cp129_la_fecha_programada_de_hoy_se_acepta") + t(UC3, "test_cp134_errores_de_registro_404_409_y_422")),
        ("RF-09-C5", "Dado un «Asistió» con la evaluación del día vinculada, cuando se registra, entonces la evaluación queda asociada al control y GET .../asistencias lista las asistencias del niño por fecha programada.",
         t(UC3, "test_cp135_asistio_con_la_evaluacion_del_dia_vinculada", "test_cp136_listar_asistencias_ordenadas_por_fecha_programada") + t(A3, "test_cp168_asistio_con_la_evaluacion_vinculada_y_listado_de_asistencias")),
        ("RF-09-C6", "Dado el expediente o la agenda del personal, cuando el personal pulsa «Asistió» o «No asistió» y confirma la ventana, entonces la interfaz actualiza el control (cumplido, o marca de inasistencia con la alerta elevada) y la insignia de vencidos.",
         t(E3, "test_cp182_rf09_no_asistio_desde_el_expediente_marca_el_control_y_sube_la_prioridad", "test_cp183_rf09_asistio_desde_la_agenda_del_personal_cumple_el_control_y_lo_quita_de_las_alertas")),
    ],
}

# Patrones para la verificación cruzada por búsqueda (grep) sobre el código fuente de cada prueba.
PATRONES = {
    "RF-01": r'registrar_nino\(|cuerpo_registro|\.post\(\s*"/api/ninos"|validar_datos_nino|llenar_registro',
    "RF-02": r'consultar\(|consultar_por_dni|actualizar_datos|registrar_evaluacion\(|/evaluaciones|\.patch\(|/api/ninos/dni',
    "RF-03": r'previsualizar_evaluacion|/api/validaciones/evaluacion|clasificar_anemia|hemoglobina_ajustada|validar_datos_evaluacion',
    "RF-04": r'listar_seguimiento|get\(\s*"/api/ninos"|control_atrasado|tab-seguimiento',
    "RF-05": r'reporte_periodo|/api/reportes/periodo|tab-reporte',
    "RF-06": r'generar_agenda|/agenda|ServicioAgenda|escenario\.agenda',
    "RF-07": r'/api/alertas|ServicioAlertas|alertas_de_nino|listar_controles_vencidos|resumen_alertas|tab-alertas',
    "RF-08": r'/api/agenda|agenda_personal|AgendaPersonal|ServicioAgendaPersonal|tab-agenda',
    "RF-09": r'/asistencia|asistencias|RegistrarAsistencia|ServicioAsistencia|btn-asistio|btn-no-asistio',
}


def criterios(version: str) -> dict:
    cr = {rf: list(v) for rf, v in COMUN.items()}
    fuentes = {"v1.0": [], "v1.5": [INC2], "v2.0": [INC2, INC2_FINAL]}[version]
    for fuente in fuentes:
        for rf, extra in fuente.items():
            cr.setdefault(rf, [])
            cr[rf] += extra
    return cr


def funciones_de_prueba(raiz: Path) -> dict[str, str]:
    """{archivo::nombre: código fuente} de todas las pruebas (def test_*) de la versión."""
    res = {}
    for p in sorted((raiz / "tests").rglob("test_*.py")):
        src = p.read_text(encoding="utf-8")
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"):
                res[f"{p.relative_to(raiz)}::{n.name}"] = ast.get_source_segment(src, n) or ""
    return res


def ejecutar(raiz: Path, ids: list[str], salida_xml: Path) -> dict[str, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "COVERAGE_FILE": str(salida_xml.with_suffix(".cov"))}
    cmd = [PY, "-m", "pytest", *ids, "--no-cov", "-p", "no:cacheprovider", "-q", f"--junitxml={salida_xml}"]
    proc = subprocess.run(cmd, cwd=raiz, env=env, capture_output=True, text=True)
    salida_xml.with_suffix(".txt").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    est: dict[str, list[str]] = {}
    for tc in ET.parse(salida_xml).getroot().iter("testcase"):
        archivo = tc.get("classname", "").replace(".", "/")
        # classname = tests.unitarias.test_agenda -> tests/unitarias/test_agenda.py
        nombre = tc.get("name", "").split("[")[0]
        clave = f"{archivo}.py::{nombre}"
        r = "passed"
        if tc.find("failure") is not None or tc.find("error") is not None:
            r = "failed"
        elif tc.find("skipped") is not None:
            r = "skipped"
        est.setdefault(clave, []).append(r)
    return {k: ("passed" if all(x == "passed" for x in v) else ("skipped" if "skipped" in v else "failed")) for k, v in est.items()}


def evaluar(version: str, ejecutar_pruebas: bool) -> dict:
    raiz = c.RAICES[version]
    funcs = funciones_de_prueba(raiz)
    cr = criterios(version)
    ids = sorted({x for lst in cr.values() for (_i, _t, p) in lst for x in p})
    inexistentes = [i for i in ids if i not in funcs]
    ids_ok = [i for i in ids if i in funcs]
    estado: dict[str, str] = {}
    if ejecutar_pruebas:
        xml = c.SALIDAS / version / "m21_criterios_dce.xml"
        estado = ejecutar(raiz, ids_ok, xml)
    por_rf = {}
    for rf, lst in sorted(cr.items()):
        pruebas = sorted({x for (_i, _t, p) in lst for x in p if x in funcs})
        crit = []
        for cid, texto, p in lst:
            res = [estado.get(x, "no_ejecutada" if ejecutar_pruebas else "sin_ejecutar") for x in p if x in funcs]
            ok = bool(res) and all(r == "passed" for r in res)
            crit.append({"id": cid, "criterio": texto, "pruebas": p, "estados": res, "verificado_en_verde": ok})
        grep = sorted(k for k, src in funcs.items() if re.search(PATRONES[rf], src))
        por_rf[rf] = {
            "pruebas_curadas": pruebas, "n_pruebas": len(pruebas),
            "n_e2e": sum(1 for x in pruebas if "/e2e/" in x),
            "n_integracion": sum(1 for x in pruebas if "/integracion/" in x),
            "n_unitarias": sum(1 for x in pruebas if "/unitarias/" in x),
            "criterios": crit,
            "pct_criterios_verificados": round(sum(1 for k in crit if k["verificado_en_verde"]) / len(crit) * 100, 1),
            "menciones_grep": len(grep), "menciones_grep_pruebas": grep,
        }
    rfs = sorted(por_rf)
    return {
        "version": version, "rfs_evaluados": rfs, "pruebas_inexistentes_en_codigo": inexistentes,
        "n_rf": len(rfs),
        "rf_con_prueba_automatizada": sum(1 for r in rfs if por_rf[r]["n_pruebas"] >= 1),
        "rf_con_e2e": sum(1 for r in rfs if por_rf[r]["n_e2e"] >= 1),
        "pct_rf_con_prueba": round(sum(1 for r in rfs if por_rf[r]["n_pruebas"] >= 1) / len(rfs) * 100, 1),
        "pct_rf_con_e2e": round(sum(1 for r in rfs if por_rf[r]["n_e2e"] >= 1) / len(rfs) * 100, 1),
        "criterios_total": sum(len(por_rf[r]["criterios"]) for r in rfs),
        "criterios_verificados": sum(sum(1 for k in por_rf[r]["criterios"] if k["verificado_en_verde"]) for r in rfs),
        "pct_criterios_verificados": round(
            sum(sum(1 for k in por_rf[r]["criterios"] if k["verificado_en_verde"]) for r in rfs)
            / sum(len(por_rf[r]["criterios"]) for r in rfs) * 100, 1),
        "por_rf": por_rf,
        "ejecutadas": ejecutar_pruebas,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="todas", choices=["v1.0", "v1.5", "v2.0", "todas"])
    ap.add_argument("--sin-ejecutar", action="store_true")
    ap.add_argument("--json", default=str(c.DATOS / "m21_cobertura_rf.json"))
    a = ap.parse_args()
    vs = c.VERSIONES if a.version == "todas" else [a.version]
    out = {v: evaluar(v, not a.sin_ejecutar) for v in vs}
    for v in vs:
        r = out[v]
        print(f"\n=== {c.ETIQUETA[v]}: RF con prueba {r['rf_con_prueba_automatizada']}/{r['n_rf']}, con E2E {r['rf_con_e2e']}/{r['n_rf']}, "
              f"criterios DCE verificados {r['criterios_verificados']}/{r['criterios_total']} ({r['pct_criterios_verificados']} %)")
        if r["pruebas_inexistentes_en_codigo"]:
            print("  PRUEBAS INEXISTENTES:", r["pruebas_inexistentes_en_codigo"])
        for rf, d in r["por_rf"].items():
            print(f"  {rf}: {d['n_pruebas']} pruebas (u={d['n_unitarias']} i={d['n_integracion']} e2e={d['n_e2e']}), "
                  f"criterios {d['pct_criterios_verificados']} %, menciones grep={d['menciones_grep']}")
    c.fusionar_json(Path(a.json), out)
    print("->", a.json)


if __name__ == "__main__":
    main()
