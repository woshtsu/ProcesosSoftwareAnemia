# Índice de evidencias visuales (Actividad 5, guía S9)

Capturas reales del software en ejecución (Chromium headless / Playwright, viewport 1366x900) con **datos 100 % sintéticos**. Cada captura incluye un pie de «Evidencia S9» inyectado por el script (RF, paso, URL, versión, fecha-hora de Perú); no altera la funcionalidad. Script reproducible: `capturar_evidencias.py`.

> **Organización por RF.** Tras la ejecución del script, las capturas se reorganizaron en carpetas por requerimiento (`RF-01/` … `RF-07/`), como pide la guía S9 (anexo «carpeta de capturas organizadas por RF»). El nombre de cada archivo conserva el incremento (`inc1`, `inc2`) o la regresión (`v15_regresion`). Las capturas de la estructura de carpetas están en `arquitectura/`.

## Incremento 1 · v1.0-PMV (RF-01 a RF-05)

Versión: `v1.0-PMV` · generado: 16/10/2026 14:17:24

### Criterio de aceptación y tiempo de respuesta

| RF | Criterio (Dado-Cuando-Entonces) | Cumple | Observación | Tiempos medidos (ms) |
|---|---|---|---|---|
| RF-01 | Dado un formulario con datos válidos, cuando se pulsa «Guardar registro», entonces el sistema almacena el registro, muestra confirmación y abre el expediente en < 2 s. | Sí | GET /api/ninos/dni/72000001 → 200 con 1 evaluación; confirmación en 188 ms. Verificación adicional: DNI repetido → HTTP 409. | clic en «Guardar registro» → confirmación visible + expediente: **188** |
| RF-02 | Dado un expediente existente, cuando se consulta y se actualizan campos permitidos y se agrega un nuevo control, entonces persisten los cambios, el historial anterior se conserva y hay confirmación en < 2 s. | Sí | Consulta 98 ms; PATCH 107 ms (comunidad/celular persistidos: True); nuevo control 97 ms (evaluaciones 2→3). | consulta: clic en «Abrir» → expediente visible: **98**; actualización (PATCH): clic en «Guardar cambios» → confirmación + datos nuevos: **107**; nuevo control (POST): clic en «Guardar control» → confirmación + fila nueva: **97** |
| RF-03 | Dado un formulario con datos clínicos, cuando se digita la Hb, entonces la vista previa muestra Hb ajustada y clasificación; y cuando los datos son inválidos, entonces se rechaza con mensaje comprensible por campo. | Sí | Vista previa «Anemia moderada» en 830 ms (incl. 350 ms de antirrebote); rechazo en 55 ms con 2 campos marcados; POST /api/validaciones/evaluacion con Hb 25 → HTTP 422. | vista previa: digitar Hb → clasificación visible (incluye antirrebote de 350 ms): **830**; rechazo: clic en «Guardar» con datos inválidos → mensajes por campo: **55** |
| RF-04 | Dado un conjunto de niños en seguimiento, cuando se filtra por clasificación o se busca por comunidad, entonces el listado respeta el filtro y muestra el estado de control de cada niño en < 2 s. | Sí | Filtro LEVE 7/7 filas en 32 ms; búsqueda Palmayoc 4/4 filas en 288 ms. | filtro por clasificación «Anemia leve» → tabla filtrada: **32**; búsqueda «Palmayoc» → tabla filtrada (incluye antirrebote de 250 ms): **288** |
| RF-05 | Dado un periodo válido, cuando se pulsa «Generar», entonces se muestran los indicadores del periodo (JSON) y se puede descargar el mismo conjunto como CSV, en < 2 s. | Sí | Reporte en pantalla 82 ms (KPI 15 = API 15); CSV 80 ms con 15 filas = evaluaciones_realizadas 15; Content-Type text/csv; charset=utf-8. | clic en «Generar» → reporte visible: **82**; clic en «Descargar CSV» → archivo descargado: **80** |

### Capturas

| Archivo | RF | Incremento | Paso | Descripción | Fecha-hora (Perú) | URL | Resultado observado |
|---|---|---|---|---|---|---|---|
| `RF-01/RF01_inc1_paso1_entrada.png` | RF-01 | Inc. 1 (v1.0-PMV) | Paso 1 · ENTRADA | Formulario «Registrar niño y evaluación inicial» lleno con datos sintéticos (DNI 72000001, Hb obs. 11,6 g/dL, 3 720 m s. n. m.) antes de pulsar «Guardar registro»; la vista previa clínica ya muestra la clasificación. | 16/10/2026 14:17:05 | http://127.0.0.1:8101/ | Formulario completo y vista previa «Anemia moderada»; aún no se ha guardado. |
| `RF-01/RF01_inc1_paso2_resultado.png` | RF-01 | Inc. 1 (v1.0-PMV) | Paso 2 · RESULTADO | Confirmación «Registro guardado: Rosa Elvira Ccente Poma» y expediente del niño recién creado con su evaluación inicial. | 16/10/2026 14:17:06 | http://127.0.0.1:8101/ | Notificación de éxito y expediente abierto; confirmación en 188 ms. |
| `RF-02/RF02_inc1_paso1_entrada.png` | RF-02 | Inc. 1 (v1.0-PMV) | Paso 1 · ENTRADA | Pestaña «Expediente» con el DNI sintético 71000001 digitado en «Buscar expediente por DNI», antes de pulsar «Abrir». | 16/10/2026 14:17:07 | http://127.0.0.1:8101/ | Campo de búsqueda con el DNI; expediente aún sin abrir. |
| `RF-02/RF02_inc1_paso2_resultado.png` | RF-02 | Inc. 1 (v1.0-PMV) | Paso 2 · RESULTADO (consulta) | Expediente digital de Luz Mery Quispe Rojas: datos del niño, historial de evaluaciones, gráfico de Hb ajustada y formularios de edición/nuevo control. | 16/10/2026 14:17:07 | http://127.0.0.1:8101/ | Expediente con 2 evaluaciones previas y todos los datos; carga en 98 ms. |
| `RF-02/RF02_inc1_paso3_entrada_actualizacion.png` | RF-02 | Inc. 1 (v1.0-PMV) | Paso 3 · ENTRADA (actualización) | Formulario «Editar datos» abierto con cambios de comunidad (Chongos Alto → Llacuas) y celular del tutor (987654322). | 16/10/2026 14:17:08 | http://127.0.0.1:8101/ | Formulario de edición con los nuevos valores, aún sin guardar. |
| `RF-02/RF02_inc1_paso4_resultado_actualizacion.png` | RF-02 | Inc. 1 (v1.0-PMV) | Paso 4 · RESULTADO (actualización) | Confirmación «Expediente actualizado»; el expediente ahora muestra comunidad Llacuas y celular 987654322. | 16/10/2026 14:17:08 | http://127.0.0.1:8101/ | Datos actualizados y persistidos; confirmación en 107 ms. |
| `RF-02/RF02_inc1_paso5_entrada_nuevo_control.png` | RF-02 | Inc. 1 (v1.0-PMV) | Paso 5 · ENTRADA (nuevo control) | Formulario «Registrar nuevo control» con fecha de hoy, Hb 11,5 g/dL, peso 8,2 kg y talla 69 cm. | 16/10/2026 14:17:12 | http://127.0.0.1:8101/ | Formulario de control completo, aún sin guardar. |
| `RF-02/RF02_inc1_paso6_resultado_nuevo_control.png` | RF-02 | Inc. 1 (v1.0-PMV) | Paso 6 · RESULTADO (nuevo control) | Confirmación «Control registrado»; el historial pasa de 2 a 3 evaluaciones, con el historial anterior intacto. | 16/10/2026 14:17:12 | http://127.0.0.1:8101/ | Nueva fila en el historial y gráfico actualizado; confirmación en 97 ms. |
| `RF-03/RF03_inc1_paso1_entrada.png` | RF-03 | Inc. 1 (v1.0-PMV) | Paso 1 · ENTRADA | Formulario con fecha de nacimiento, altitud (3 720 m) y demás datos, pero sin hemoglobina: la vista previa aún no puede validar. | 16/10/2026 14:17:14 | http://127.0.0.1:8101/ | Vista previa vacía: «Complete fecha de nacimiento, altitud y hemoglobina…». |
| `RF-03/RF03_inc1_paso2_resultado.png` | RF-03 | Inc. 1 (v1.0-PMV) | Paso 2 · RESULTADO (vista previa) | Vista previa de validación clínica: edad al control, ajuste por altitud, Hb ajustada y clasificación calculadas por el servidor. | 16/10/2026 14:17:15 | http://127.0.0.1:8101/ | «Validación clínica (vista previa) Edad al control 1 a 1 m Ajuste por altitud (3720 m) −2.5 g/dL Hemoglobina ajustada 9.1 g/dL Clasificación Anemia moderada» (Hb ajustada 9.1 g/dL). |
| `RF-03/RF03_inc1_paso3_rechazo.png` | RF-03 | Inc. 1 (v1.0-PMV) | Paso 3 · RECHAZO | Datos inválidos (DNI «123», Hb 25 g/dL) al guardar: el sistema rechaza (HTTP 422) y marca cada campo con su mensaje. | 16/10/2026 14:17:17 | http://127.0.0.1:8101/ | 2 campo(s) marcado(s); mensajes visibles: DNI «exactamente 8 dígitos», Hb «rango clínico válido». |
| `RF-04/RF04_inc1_paso1_entrada.png` | RF-04 | Inc. 1 (v1.0-PMV) | Paso 1 · ENTRADA | Pestaña «Seguimiento» sin filtros: listado completo de niños con seguimiento activo, antes de aplicar un filtro. | 16/10/2026 14:17:17 | http://127.0.0.1:8101/ | 15 niños en seguimiento, con último control, Hb ajustada y clasificación. |
| `RF-04/RF04_inc1_paso2_resultado.png` | RF-04 | Inc. 1 (v1.0-PMV) | Paso 2 · RESULTADO (filtro por clasificación) | Filtro «Anemia leve» aplicado: solo aparecen niños cuya última clasificación es leve, con fecha y antigüedad del último control. | 16/10/2026 14:17:18 | http://127.0.0.1:8101/ | 7 fila(s), todas «Anemia leve»; coincide con GET /api/ninos?clasificacion=LEVE (7). |
| `RF-04/RF04_inc1_paso3_busqueda_comunidad.png` | RF-04 | Inc. 1 (v1.0-PMV) | Paso 3 · RESULTADO (búsqueda por comunidad) | Búsqueda por comunidad «Palmayoc»: el listado se reduce a los niños de esa comunidad. | 16/10/2026 14:17:19 | http://127.0.0.1:8101/ | 4 fila(s), todas de Palmayoc. |
| `RF-05/RF05_inc1_paso1_entrada.png` | RF-05 | Inc. 1 (v1.0-PMV) | Paso 1 · ENTRADA | Pestaña «Reporte» con el periodo 2026-09-01 a 2026-10-16 elegido, antes de pulsar «Generar». | 16/10/2026 14:17:19 | http://127.0.0.1:8101/ | Periodo definido; el reporte aún no se ha generado. |
| `RF-05/RF05_inc1_paso2_resultado.png` | RF-05 | Inc. 1 (v1.0-PMV) | Paso 2 · RESULTADO (reporte en pantalla) | Reporte del periodo: indicadores (niños registrados, evaluaciones, evaluados, % con anemia), barras por clasificación y tabla por comunidad. | 16/10/2026 14:17:20 | http://127.0.0.1:8101/ | 15 niños registrados en el periodo; reporte generado en 82 ms. |
| `RF-05/RF05_inc1_paso3_json.png` | RF-05 | Inc. 1 (v1.0-PMV) | Paso 3 · RESULTADO (JSON) | Respuesta JSON del servicio GET /api/reportes/periodo abierta en el navegador. | 16/10/2026 14:17:23 | http://127.0.0.1:8101/api/reportes/periodo?desde=2026-09-01&hasta=2026-10-16 | HTTP 200, application/json; ninos_registrados=15, evaluaciones_realizadas=15. |
| `RF-05/RF05_inc1_paso4_csv.png` | RF-05 | Inc. 1 (v1.0-PMV) | Paso 4 · RESULTADO (CSV descargado) | Contenido del archivo CSV generado y descargado desde el botón «Descargar CSV», renderizado en una página simple. | 16/10/2026 14:17:23 | archivo descargado: reporte_anemia_2026-09-01_2026-10-16.csv (origen /api/reportes/periodo?desde=2026-09-01&hasta=2026-10-16&formato=csv) | Archivo «reporte_anemia_2026-09-01_2026-10-16.csv» con 15 fila(s) y cabecera de 12 columnas. |

## Incremento 2 · v1.5.0-inc2-avance (RF-06 y RF-07)

Versión: `v1.5.0-inc2-avance` · generado: 16/10/2026 14:16:12

### Criterio de aceptación y tiempo de respuesta

| RF | Criterio (Dado-Cuando-Entonces) | Cumple | Observación | Tiempos medidos (ms) |
|---|---|---|---|---|
| RF-06 | Dado un niño con anemia en tratamiento, cuando se abre su expediente, entonces el sistema muestra la agenda normativa de controles con el estado de cada uno (cumplido/pendiente/próximo/vencido) en < 2 s. | Sí | DNI 71000022: 13 controles, estados {'CUMPLIDO': 2, 'PENDIENTE': 9, 'VENCIDO': 2} (UI = API: True); DNI 71000003 (anemia moderada) con 1 próximo(s); ningún niño sintético reúne los 4 estados a la vez, por eso se usan 2 niños; agenda en 119 ms. | clic en el niño → expediente con agenda calculada: **119** |
| RF-07 | Dado un conjunto de niños con controles, cuando se abre la pestaña «Alertas» y se filtra por prioridad o comunidad, entonces se listan los controles vencidos priorizados con su resumen, en < 2 s. | Sí | Resumen UI = API (9 vencidos); filtro ALTA 7 filas en 69 ms; comunidad Huaycha 1/1 filas en 70 ms; pestaña en 176 ms. | clic en pestaña «Alertas» → resumen + tabla: **176**; filtro prioridad «Alta» → tabla filtrada: **69**; filtro comunidad «Huaycha» → tabla filtrada: **70** |

### Capturas

| Archivo | RF | Incremento | Paso | Descripción | Fecha-hora (Perú) | URL | Resultado observado |
|---|---|---|---|---|---|---|---|
| `RF-06/RF06_inc2_paso1_entrada.png` | RF-06 | Inc. 2 (v1.5) | Paso 1 · ENTRADA | Pestaña «Seguimiento» con el niño sintético DNI 71000022 (anemia leve en tratamiento) localizado; se abrirá su expediente. | 16/10/2026 14:16:07 | http://127.0.0.1:8102/ | Fila del niño visible con su clasificación y la marca de controles vencidos. |
| `RF-06/RF06_inc2_paso2_resultado.png` | RF-06 | Inc. 2 (v1.5) | Paso 2 · RESULTADO (agenda del expediente) | Sección «Agenda de controles» del expediente: lista de controles por edad y de tratamiento con fecha programada, ventana de cumplimiento y estado (cumplido, pendiente, próximo a vencer, vencido). | 16/10/2026 14:16:08 | http://127.0.0.1:8102/ | 13 controles; estados {'CUMPLIDO': 2, 'PENDIENTE': 9, 'VENCIDO': 2}. Resumen: 13 controles · 2 cumplidos · 9 pendientes · 0 por vencer · 2 vencidos · Próximo control: DHc1 el 03/11/2026 |
| `RF-06/RF06_inc2_paso3_proximo_a_vencer.png` | RF-06 | Inc. 2 (v1.5) | Paso 3 · RESULTADO (control próximo a vencer) | Agenda de otro niño sintético con anemia moderada (DNI 71000003) con un control en estado «Próximo a vencer» (los datos de prueba no traen un niño con los cuatro estados a la vez). | 16/10/2026 14:16:09 | http://127.0.0.1:8102/ | 1 control(es) en estado «Próximo a vencer»; resumen «1 por vencer». |
| `RF-07/RF07_inc2_paso1_entrada.png` | RF-07 | Inc. 2 (v1.5) | Paso 1 · ENTRADA (alertas sin filtro) | Pestaña «Alertas» con el resumen (vencidos, niños, prioridad alta/media/baja, por vencer en 7 días) y la tabla completa, antes de aplicar filtros; la insignia de la cabecera muestra el total de vencidos. | 16/10/2026 14:16:11 | http://127.0.0.1:8102/ | 9 controles vencidos, 9 alertas ordenadas por prioridad; carga en 176 ms. |
| `RF-07/RF07_inc2_paso2_resultado_filtro_prioridad.png` | RF-07 | Inc. 2 (v1.5) | Paso 2 · RESULTADO (filtro por prioridad ALTA) | Filtro «Prioridad: Alta» aplicado: la tabla muestra solo alertas de prioridad alta (control de tratamiento vencido, clasificación moderada/severa o más de 30 días de atraso). | 16/10/2026 14:16:11 | http://127.0.0.1:8102/ | 7 alerta(s) ALTA de 9; coincide con la API. |
| `RF-07/RF07_inc2_paso3_resultado_filtro_comunidad.png` | RF-07 | Inc. 2 (v1.5) | Paso 3 · RESULTADO (filtro por comunidad) | Filtro «Comunidad: Huaycha» aplicado: solo las alertas de esa comunidad. | 16/10/2026 14:16:12 | http://127.0.0.1:8102/ | 1 alerta(s), todas de Huaycha. |

## Regresión visual · RF-01 a RF-05 ejecutados en v1.5.0-inc2-avance

Versión: `v1.5.0-inc2-avance` · generado: 16/10/2026 14:17:00

### Criterio de aceptación y tiempo de respuesta

| RF | Criterio (Dado-Cuando-Entonces) | Cumple | Observación | Tiempos medidos (ms) |
|---|---|---|---|---|
| RF-01 | Dado un formulario con datos válidos, cuando se pulsa «Guardar registro», entonces el sistema almacena el registro, muestra confirmación y abre el expediente en < 2 s. | Sí | GET /api/ninos/dni/72000001 → 200 con 1 evaluación; confirmación en 294 ms. Verificación adicional: DNI repetido → HTTP 409. | clic en «Guardar registro» → confirmación visible + expediente: **294** |
| RF-02 | Dado un expediente existente, cuando se consulta y se actualizan campos permitidos y se agrega un nuevo control, entonces persisten los cambios, el historial anterior se conserva y hay confirmación en < 2 s. | Sí | Consulta 163 ms; PATCH 190 ms (comunidad/celular persistidos: True); nuevo control 184 ms (evaluaciones 2→3). | consulta: clic en «Abrir» → expediente visible: **163**; actualización (PATCH): clic en «Guardar cambios» → confirmación + datos nuevos: **190**; nuevo control (POST): clic en «Guardar control» → confirmación + fila nueva: **184** |
| RF-03 | Dado un formulario con datos clínicos, cuando se digita la Hb, entonces la vista previa muestra Hb ajustada y clasificación; y cuando los datos son inválidos, entonces se rechaza con mensaje comprensible por campo. | Sí | Vista previa «Anemia moderada» en 863 ms (incl. 350 ms de antirrebote); rechazo en 80 ms con 2 campos marcados; POST /api/validaciones/evaluacion con Hb 25 → HTTP 422. | vista previa: digitar Hb → clasificación visible (incluye antirrebote de 350 ms): **863**; rechazo: clic en «Guardar» con datos inválidos → mensajes por campo: **80** |
| RF-04 | Dado un conjunto de niños en seguimiento, cuando se filtra por clasificación o se busca por comunidad, entonces el listado respeta el filtro y muestra el estado de control de cada niño en < 2 s. | Sí | Filtro LEVE 9/9 filas en 51 ms; búsqueda Palmayoc 8/8 filas en 308 ms. | filtro por clasificación «Anemia leve» → tabla filtrada: **51**; búsqueda «Palmayoc» → tabla filtrada (incluye antirrebote de 250 ms): **308** |
| RF-05 | Dado un periodo válido, cuando se pulsa «Generar», entonces se muestran los indicadores del periodo (JSON) y se puede descargar el mismo conjunto como CSV, en < 2 s. | Sí | Reporte en pantalla 102 ms (KPI 28 = API 28); CSV 116 ms con 18 filas = evaluaciones_realizadas 18; Content-Type text/csv; charset=utf-8. | clic en «Generar» → reporte visible: **102**; clic en «Descargar CSV» → archivo descargado: **116** |

### Capturas

| Archivo | RF | Incremento | Paso | Descripción | Fecha-hora (Perú) | URL | Resultado observado |
|---|---|---|---|---|---|---|---|
| `RF-01/RF01_v15_regresion.png` | RF-01 | Regresión Inc. 1 en v1.5 | Paso 2 · RESULTADO | Confirmación «Registro guardado: Rosa Elvira Ccente Poma» y expediente del niño recién creado con su evaluación inicial. | 16/10/2026 14:16:46 | http://127.0.0.1:8102/ | Notificación de éxito y expediente abierto; confirmación en 294 ms. |
| `RF-02/RF02_v15_regresion.png` | RF-02 | Regresión Inc. 1 en v1.5 | Paso 6 · RESULTADO (nuevo control) | Confirmación «Control registrado»; el historial pasa de 2 a 3 evaluaciones, con el historial anterior intacto. | 16/10/2026 14:16:51 | http://127.0.0.1:8102/ | Nueva fila en el historial y gráfico actualizado; confirmación en 184 ms. |
| `RF-03/RF03_v15_regresion.png` | RF-03 | Regresión Inc. 1 en v1.5 | Paso 2 · RESULTADO (vista previa) | Vista previa de validación clínica: edad al control, ajuste por altitud, Hb ajustada y clasificación calculadas por el servidor. | 16/10/2026 14:16:54 | http://127.0.0.1:8102/ | «Validación clínica (vista previa) Edad al control 1 a 1 m Ajuste por altitud (3720 m) −2.5 g/dL Hemoglobina ajustada 9.1 g/dL Clasificación Anemia moderada» (Hb ajustada 9.1 g/dL). |
| `RF-04/RF04_v15_regresion.png` | RF-04 | Regresión Inc. 1 en v1.5 | Paso 2 · RESULTADO (filtro por clasificación) | Filtro «Anemia leve» aplicado: solo aparecen niños cuya última clasificación es leve, con fecha y antigüedad del último control. | 16/10/2026 14:16:56 | http://127.0.0.1:8102/ | 9 fila(s), todas «Anemia leve»; coincide con GET /api/ninos?clasificacion=LEVE (9). |
| `RF-05/RF05_v15_regresion.png` | RF-05 | Regresión Inc. 1 en v1.5 | Paso 2 · RESULTADO (reporte en pantalla) | Reporte del periodo: indicadores (niños registrados, evaluaciones, evaluados, % con anemia), barras por clasificación y tabla por comunidad. | 16/10/2026 14:16:58 | http://127.0.0.1:8102/ | 28 niños registrados en el periodo; reporte generado en 102 ms. |

## Arquitectura · árboles de app/

Versión: `-` · generado: 16/10/2026 18:46:43

### Capturas

| Archivo | RF | Incremento | Paso | Descripción | Fecha-hora (Perú) | URL | Resultado observado |
|---|---|---|---|---|---|---|---|
| `arquitectura/arbol_v1.0.png` | Arquitectura | Arquitectura | Árbol de carpetas app/ (v1.0-PMV) | Árbol de app/ en v1.0-PMV | 16/10/2026 18:46:42 | app/ (tag v1.0-PMV) | Árbol de app/ (tag v1.0-PMV) |
| `arquitectura/arbol_v1.5.png` | Arquitectura | Arquitectura | Árbol de carpetas app/ (v1.5.0-inc2-avance) | Árbol de app/ en v1.5.0-inc2-avance (rama de trabajo local) | 16/10/2026 18:46:43 | pmv_fastapi/app/ | Árbol de pmv_fastapi/app/ |

## Intento de captura en GitHub (opcional)

- URL: https://github.com/woshtsu/ProcesosSoftwareAnemia/tree/v1.0-PMV/app
- Éxito: no
- Detalle: HTTP 403 · {"message":"GitHub access to this repository is not enabled for this session. Use add_repo to request access. If add_repo answers that read access is already av
