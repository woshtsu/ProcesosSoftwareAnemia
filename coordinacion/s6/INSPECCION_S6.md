# Inspección S6: cumplimiento de la consigna integradora

- **Fecha:** 2026-10-01
- **Inspector:** inspector-guia (tarea S6-06)
- **Rama:** `feature/s6-integrador-final`; **commit base:** `807d3dc`. El trabajo inspeccionado no está confirmado: el informe aparece modificado y la presentación, las figuras y `.github/` como archivos sin seguimiento en `git status`.
- **Tag:** `v1.0-PMV` -> 9ce90c3 en origin (verificado con `git ls-remote --tags origin`).
- **Objetos inspeccionados:** informe y checklist; `Presentacion_Integrador.md`; `GUION_EXPOSICION.md`; PPTX (python-pptx); PNG `50` a `68`; README raíz y de `pmv_fastapi`; `.github/workflows/ci.yml`.
- **Leyenda:** CUMPLE / PARCIAL / NO CUMPLE / MANUAL (depende de una persona; ver `PASOS_MANUALES.md`).
- **Verificaciones automáticas:** 35 enlaces e imágenes locales del informe y 14 de la presentación resueltos sin roturas (los 5 «rotos» del README raíz son falsos positivos por URL con `%20`; los archivos existen); 0 ocurrencias de `CARGA_CIERRE`, `[PENDIENTE`, `tag pendiente` y `VIS-… pendiente`; 17 líneas con `[COMPLETAR]` en el informe, 1 en la presentación y 1 en el guion; resumen de 285 palabras; 35 figuras y 31 tablas.

## 0. Veredicto

**NO LISTO PARA ENTREGAR.**

Bloqueantes:

- No existen el PDF ni el DOCX del informe (R-01) ni el PDF de las diapositivas (R-02).
- Doce hallazgos en figuras (sección 3): cifras o contenido que no coinciden con la fuente, y defectos de renderizado; varias figuras están incrustadas en las diapositivas 1, 2, 3, 4, 6 y 7.
- Datos de portada y 17 líneas con `[COMPLETAR]` visibles en el informe, más uno en la diapositiva 5 (aceptación del usuario).
- `.github/workflows/ci.yml` sin commit ni push: no hay evidencia de CI en verde.
- Staging con Docker Compose y E2E sin ejecutar; SonarCloud sin activar.

## 1. Resumen de cumplimiento

Se muestra el porcentaje de CUMPLE sobre el total de cada bloque y el cumplimiento ponderado (CUMPLE = 1, PARCIAL = 0,5; NO CUMPLE y MANUAL = 0). Los MANUAL no son fallas del contenido: dependen de personas.

| Bloque | Requisitos | CUMPLE | PARCIAL | NO CUMPLE | MANUAL | % CUMPLE | % ponderado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A. Modalidad y entregables | 5 | 2 | 1 | 1 | 1 | 40 % | 50 % |
| B. Portada | 4 | 2 | 0 | 0 | 2 | 50 % | 50 % |
| C. Estructura del informe | 30 | 16 | 10 | 4 | 0 | 53 % | 70 % |
| D. Siete diapositivas | 36 | 18 | 10 | 6 | 2 | 50 % | 64 % |
| E. Repositorio | 5 | 2 | 3 | 0 | 0 | 40 % | 70 % |
| F. Rúbrica | 8 | 0 | 4 | 1 | 3 | 0 % | 25 % |
| G. Puntaje y exposición | 3 | 2 | 0 | 0 | 1 | 67 % | 67 % |
| **Global** | **91** | **42** | **28** | **12** | **9** | **46.2 %** | **61.5 %** |

Excluyendo los 9 MANUAL, el cumplimiento automático es 51.2 % de CUMPLE (68.3 % ponderado). Con las correcciones de la sección 4 aplicadas y los pasos manuales hechos, el objetivo es 91/91.

Estimación orientativa de puntaje por criterio (no es la nota oficial), con el estado actual: C1 1,5 a 1,75; C2 1,5 a 1,75; C3 1,5; C4 1,25 a 1,5; C5 1,5 a 2,25; C6 1,5 (demo solo con capturas y video, sin staging ejecutado: nivel Básico); C7 y C8 dependen del ensayo. Con las correcciones aplicadas, C1 a C5 podrían alcanzar el nivel Excelente.

## 2. Matriz R-01 a R-91


### A. Modalidad y entregables

| ID | Requisito | Estado | Evidencia | Acción correctiva | Responsable |
| --- | --- | --- | --- | --- | --- |
| R-01 | Informe en PDF con el formato oficial | **NO CUMPLE** | `exportados/semana-06/` solo contiene el PPTX; no existe `Informe_Integrador_Anemia_Junin.pdf` ni `.docx`; el .md aún tiene 17 líneas con `[COMPLETAR]` (entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md) | Corregir las figuras (sección 3), cerrar los `[COMPLETAR]` (PASOS_MANUALES 1-9) y recién entonces ejecutar S6-05 (PDF/DOCX) | conversor-entregas (tras redactor y personas) |
| R-02 | PPTX/PDF con exactamente 7 diapositivas | **PARCIAL** | python-pptx: 7 diapositivas y 7 separadores Marp (`entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md`); falta el PDF; el archivo se llama `Presentacion_Integrador_Anemia_Junin.pptx`, pero PROTOCOLO_S6 §2 y RUTAS.md l.77 esperan `Presentacion_Integrador.{pptx,pdf}` | Generar el PDF (PASOS_MANUALES 12); unificar el nombre (renombrar o actualizar PROTOCOLO_S6 y RUTAS.md); regenerar el PPTX tras corregir figuras | disenador-diapositivas / sincronizador |
| R-03 | Enlace al repositorio con código, scripts BD, pruebas y README | **CUMPLE** | `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` l.665 (Tabla 31) y README raíz; existen `pmv_fastapi/app`, `db/`, `tests/` y `README.md` | Ninguna. Verificar tras el push que la rama o el PR sea visible (PASOS_MANUALES 3) | — |
| R-04 | 7 min grupal + 5 min individual por integrante | **MANUAL** | `entregables/semana-06-integrador/presentacion/GUION_EXPOSICION.md` §1 (7:00) y §3 (preguntas); falta el ensayo real | Ensayo cronometrado (PASOS_MANUALES 17-18) | personas |
| R-05 | Propósito integrador problema -> TO-BE -> tailoring -> arquitectura -> pruebas -> demo | **CUMPLE** | Secciones 2.1 a 3.4 del informe y matriz l.622-633 | Ninguna | — |

### B. Portada

| ID | Requisito | Estado | Evidencia | Acción correctiva | Responsable |
| --- | --- | --- | --- | --- | --- |
| R-06 | Título y subtítulo textuales | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.1-3 | Ninguna | — |
| R-07 | Carrera, asignatura y proyecto | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.7-9 | Ninguna | — |
| R-08 | Integrantes con apellidos, nombres, código y rol; mapeo 4 roles a 3 personas | **MANUAL** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.20-22 (código `[COMPLETAR]`) y l.35 (confirmar mapeo); README raíz l.23 dice «Ingeniera» y el informe l.21 «Ingeniero» | Personas: códigos y confirmación (PASOS_MANUALES 1-2). Unificar el género del rol en README raíz l.23 y en el informe l.21 | personas / sincronizador |
| R-09 | Fecha de entrega (DD/MM/AAAA) y docente | **MANUAL** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.10-11 `[COMPLETAR]` | PASOS_MANUALES 1 | personas |

### C. Estructura del informe

| ID | Requisito | Estado | Evidencia | Acción correctiva | Responsable |
| --- | --- | --- | --- | --- | --- |
| R-10 | Resumen <= 300 palabras con los 5 elementos | **CUMPLE** | `sed -n 57,65p` + `wc -w` = 285 palabras; cubre problema, solución, modelo, arquitectura y resultados (l.57-65) | Ninguna. Si se corrigen cifras, volver a contar (<= 300) | — |
| R-11 | Diagnóstico y matriz de actores y necesidades | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.73-88, Tabla 3 | Ninguna | — |
| R-12 | AS-IS y >= 5 brechas | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.92-111 (Fig. 2 = `10_s1_proceso_as_is.svg`; Tabla 4 con 6 brechas) | Ninguna | — |
| R-13 | TO-BE y matriz de intervención | **PARCIAL** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.115-130: la Tabla 5 es correcta, pero la Fig. 1 (l.94, `50_s6_as_is_vs_to_be`) asigna incrementos distintos (M2-M3 INC-2; M4-M5 INC-3/4; M6 INC-5/6) a los de la Tabla 5 (M3 INC-4, M4 INC-3, M5 INC-5, M6 INC-3 e INC-6); muestra el banner «Please use CSS style…» y un glifo vacío en «v1.0 ▯» | Regenerar la figura 50 alineada con la Tabla 5, sin banner (skinparam) y con el glifo corregido (E-07, E-12) | recursos-visuales |
| R-14 | Cadena de valor e indicadores de los 4 tipos | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.134-150, Tabla 6 (Proceso, Producto, Resultado, Valor) | Ninguna | — |
| R-15 | Matriz de factores con los 5 nombres | **NO CUMPLE** | La Tabla 7 (l.160-166) dice «Alto» en los cinco; la Fig. 5 (l.170, `67_s6_matriz_factores`) muestra Complejidad = Medio, Integración = Medio y Datos/IA = Bajo; la presentación l.66 dice «cinco factores en nivel alto» | Regenerar la figura 67 con los cinco niveles «Alto» y los textos de la Tabla 7 (E-05) | recursos-visuales |
| R-16 | Comparación de Cascada, Incremental, Scrum, DevOps y MLOps | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.176-188, Tabla 8 (7 enfoques) | Ninguna | — |
| R-17 | Justificación técnica y tailoring híbrido | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.190-210, Tabla 9 (4,75 / 3,85 / 2,95) | Ninguna | — |
| R-18 | Representación gráfica del modelo aplicado | **NO CUMPLE** | La Fig. 6 (l.216, `51_s6_ciclo_vida_tailoring`) rotula Alt. 2 = «Cascada + Testing» y Alt. 3 = «Scrum sin DevOps», pero la Tabla 9 dice Alt. 2 = Kanban + DevOps + DataOps y Alt. 3 = Incremental + Espiral sin automatización; rotula «Scrum Puro 3/5 en S2» (Tabla 8: Scrum = 27/30); lleva el banner de PlantUML | Regenerar la figura 51 con las alternativas de la Tabla 9, quitar «3/5» (usar 27/30 o no cifrar) y el banner (E-06) | recursos-visuales |
| R-19 | Matriz de actividades (entradas, artefactos, salidas) | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.226-242, Tabla 10, Fig. 8 | Ninguna (el acta es un `[COMPLETAR]` aparte) | — |
| R-20 | Matriz RAE | **PARCIAL** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.248-263 (Tabla 11 completa); l.263 `[COMPLETAR]` nombre del Product Owner | PASOS_MANUALES 5 (nombrar al PO o declarar «rol previsto, sin designar») | personas |
| R-21 | DoD por actividad | **PARCIAL** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.267-283 (Tabla 12); l.277 y l.280 `[COMPLETAR]` (captura de CI en verde y acta) | PASOS_MANUALES 3 y 5 | personas |
| R-22 | WBS épicas -> HU -> tareas | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.287-303 (Fig. 9, Tabla 13) | Ninguna | — |
| R-23 | Estimación, priorización valor/riesgo y plan | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.307-357 (Tablas 14-16, Figs. 10-11). Las horas reales (l.323) no forman parte del requisito | Ninguna; opcional PASOS_MANUALES 4 | — |
| R-24 | Seguimiento, control de desviaciones e indicadores | **NO CUMPLE** | Las Figs. 13 (l.390) y 14 (l.392) tienen cifras erróneas: el burnup termina en 16 y no en 21, y declara «01-28 Sep» cuando `git log 9ce90c3` muestra todos los commits del 2026-09-30; el tablero muestra 21/21 SP con barras que suman 16; l.386 afirma «avance real reconstruido del historial git» | Reconstruir la figura 63 (E-03, E-04), corregir la 62 (E-02) y reescribir l.386 y el pie de la Fig. 13, o retirarla | recursos-visuales + redactor |
| R-25 | Clasificación principales, soporte y organizacionales | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.402-408, Tabla 19 | Ninguna | — |
| R-26 | Matriz de tailoring | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.412-424, Tabla 20 | Ninguna (l.424 `[COMPLETAR]` justificación Flask -> FastAPI: PASOS_MANUALES 6) | personas |
| R-27 | ADR con NFR | **PARCIAL** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.430-441: la Tabla 21 es correcta; la Fig. 15 (`66_s6_adr_nfr`) tiene los encabezados superpuestos al título y rotula ADR-002 como «PWA (offline)» (el registro definitivo requiere conexión según ADR-002) | Regenerar la figura 66: separar cabecera y título, rotular «PWA con borrador local» (E-10) | recursos-visuales |
| R-28 | C4 niveles 1, 2 y 3 | **PARCIAL** | Figs. 16-18 (l.447-451) existen y son de FastAPI; las tres muestran el banner «Please use CSS style instead of skinparam padding»; la Fig. 16 dibuja al agente comunitario y a WhatsApp con el mismo trazo que los actores del PMV | Regenerar 52, 53 y 54 sin banner; marcar con línea discontinua lo no entregado en INC-1 (E-12) | recursos-visuales |
| R-29 | Modelo de datos y contrato API | **PARCIAL** | La Fig. 21 (l.468) rotula `v_ultimo_control` como «vista materializada», pero es una vista (l.465; DATOS §5); banner; la Tabla 22 y `openapi.json` son correctos | Corregir el texto de la figura 55 (E-09) y quitar el banner | recursos-visuales |
| R-30 | Pirámide de pruebas con 4 niveles y casos | **NO CUMPLE** | Fig. 22 (l.502, `59_s6_piramide_pruebas`): título «Total: 77/77 en verde»; solo se reprodujeron 73 (DATOS §17); además la carga aparece como cuarto nivel bajo ese total | Retitular «77 automatizadas declaradas (62+11+4); 73 reproducidas el 01/10; carga: 1 escenario, no cuenta» (E-01) | recursos-visuales |
| R-31 | Registro de ejecución y cobertura | **PARCIAL** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.506-513 (Tabla 24) marca «En verde» E2E, PostgreSQL y carga sin haberlas reproducido; l.515 lo aclara. La Tabla 25 y la Fig. 23 son correctas (641 declarado frente a 548 reproducido, explicado) | Cambiar el Resultado de las filas E2E, PostgreSQL y carga a «En verde según el tag; no reproducido el 01/10» (l.511-513); tras PASOS_MANUALES 11 pasar a «Reproducido» | redactor / personas |
| R-32 | Análisis estático y gestión de defectos | **PARCIAL** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.548-561: Ruff y defectos completos; l.550 SonarCloud sin análisis (`[COMPLETAR]`) | PASOS_MANUALES 7 (activar SonarCloud) o decidir no usarlo y eliminar el `[COMPLETAR]` | personas |
| R-33 | Arquitectura del entorno de despliegue | **PARCIAL** | Fig. 25 (l.580): imagen de 2749x1130 con texto diminuto (ilegible en A4 y en diapositiva), banner y la nota interna «C-02» visible; el staging no se ejecutó (l.582 `[COMPLETAR]`) | Rehacer la figura 58 en formato compacto (vertical, fuente >= 10 pt), sin banner ni referencias a C-02; ejecutar staging (PASOS_MANUALES 8-9) | recursos-visuales / personas |
| R-34 | Evidencia del incremento operativo | **PARCIAL** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.598-616: ocho capturas y video; todos los enlaces existen; falta la duración del video y el acta (l.614, l.616) | PASOS_MANUALES 10 y 5 | personas |
| R-35 | Matriz de trazabilidad de 8 columnas en orden | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.624 (cabecera: Problema Org., Proceso TO-BE, Modelo Adaptado, Categoría/Actividad, Decisión Arquitectura, Caso Prueba, PMV Entregado, Indicador Valor) | Ninguna | — |
| R-36 | Tres conclusiones técnicas | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.643-645 (exactamente 3) | Ninguna | — |
| R-37 | Tres lecciones aprendidas | **CUMPLE** | entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.649-651 (exactamente 3); l.651 `[COMPLETAR]` justificación del cambio de pila | PASOS_MANUALES 6 | personas |
| R-38 | Enlace al repositorio con tag `v1.0-PMV` | **CUMPLE** | `git ls-remote --tags origin`: refs/tags/v1.0-PMV -> 9ce90c3; entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md l.666 y nota l.677 | Ninguna. El tag no es alcanzable desde main (decisión en PASOS_MANUALES 14) | — |
| R-39 | README con compilación, despliegue y BD | **CUMPLE** | `pmv_fastapi/README.md` l.31-90 (local, Docker, BD, pruebas) | Ninguna | — |

### D. Siete diapositivas

| ID | Requisito | Estado | Evidencia | Acción correctiva | Responsable |
| --- | --- | --- | --- | --- | --- |
| R-40 | Diap. 1: comparativo AS-IS vs TO-BE | **PARCIAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.37 usa `50_s6_as_is_vs_to_be.png` (inconsistente con la Tabla 5, con banner y glifo vacío) | Regenerar la figura 50 (ver R-13) y re-exportar el PPTX | recursos-visuales + disenador-diapositivas |
| R-41 | Diap. 1: problema central y brechas | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.39 (B1-B6) y figura; detalle en las notas l.46 | Ninguna | — |
| R-42 | Diap. 1: cadena Datos -> Software -> Decisión -> Impacto | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.39 y figura 50 | Ninguna | — |
| R-43 | Diap. 1: indicador de valor objetivo | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.40: 3 registros -> 1 (sin inventar tiempos) | Ninguna | — |
| R-44 | Pitch diap. 1 | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.43-51 (1:05, reducido de 1,5 min); entregables/semana-06-integrador/presentacion/GUION_EXPOSICION.md l.25 | Ninguna | — |
| R-45 | Diap. 2: matriz de factores + ciclo adaptado | **NO CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.57 incrusta las figuras 51 y 67, ambas con errores (E-05, E-06) | Regenerar 51 y 67 y re-exportar | recursos-visuales + disenador-diapositivas |
| R-46 | Diap. 2: factores determinantes | **NO CUMPLE** | La figura 67 contradice las notas l.66 («cinco factores en nivel alto») | Igual que R-45 | recursos-visuales |
| R-47 | Diap. 2: justificación del híbrido | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.59-60 y notas l.67 | Ninguna | — |
| R-48 | Diap. 2: rechazo de Cascada y Scrum puro | **PARCIAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.61 es correcto («Cascada pura (8/30)»), pero la figura 51 rotula «Scrum Puro 3/5 en S2», escala distinta e incoherente con 27/30 | Corregir la figura 51 (E-06) | recursos-visuales |
| R-49 | Pitch diap. 2 | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.63-71; entregables/semana-06-integrador/presentacion/GUION_EXPOSICION.md l.29 | Ninguna | — |
| R-50 | Diap. 3: C4 N2 + cuadro de ADR | **PARCIAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.77: la figura 53 lleva banner; el cuadro 66 tiene la cabecera superpuesta | Regenerar 53 y 66; revisar la legibilidad en el PPTX | recursos-visuales |
| R-51 | Diap. 3: estructura tecnológica y por qué no gateway, microservicios ni caché | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.80 y notas l.87 | Ninguna | — |
| R-52 | Diap. 3: ADR críticos (concurrencia, latencia, disponibilidad) | **PARCIAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.81 es correcto; la figura 66 rotula ADR-002 «PWA (offline)», lo que contradice la nota «el registro definitivo exige conexión» (l.88) | Corregir la figura 66 (E-10) | recursos-visuales |
| R-53 | Diap. 3: protocolos REST, WebSockets, gRPC | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.79 | Ninguna | — |
| R-54 | Pitch diap. 3 | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.83-91 | Ninguna | — |
| R-55 | Diap. 4: pirámide + cobertura + carga | **NO CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.97: la figura 59 trae «77/77 en verde» (E-01); tres imágenes de h:240 (la pirámide mide 3,2 pulgadas de ancho en el PPTX: texto ilegible) | Corregir la 59; en la diapositiva usar dos figuras más grandes o recortar rótulos; re-exportar | recursos-visuales + disenador-diapositivas |
| R-56 | Diap. 4: cobertura | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.100: 99 %; la figura 60 coincide con DATOS §7 | Ninguna | — |
| R-57 | Diap. 4: p95 y throughput | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.100: p95 310 -> 58 ms, 39,6 req/s, 0 % errores; la figura 61 coincide con DATOS §9 (usa punto decimal: 2,170 y 36.74; ver E-11) | Opcional: coma decimal en la figura 61 | recursos-visuales |
| R-58 | Diap. 4: cumplimiento de la DoD | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.101 | Ninguna | — |
| R-59 | Pitch diap. 4 | **PARCIAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.106 y entregables/semana-06-integrador/presentacion/GUION_EXPOSICION.md l.37: la frase «62 …, 11 …, 4 E2E … y un escenario de carga: 77 automatizadas» puede leerse como 78 o como carga contada entre las pruebas | Reescribir: «62 + 11 + 4 = 77 pruebas automatizadas; además 1 escenario de carga, que no cuenta en el total» | disenador-diapositivas |
| R-60 | Diap. 5: capturas + video o demo | **PARCIAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.117: el collage 65 tiene solo 4 paneles (falta HU-04, Seguimiento); video sin duración medida (l.125 `[COMPLETAR]`) | Agregar el panel de la captura 04 al collage 65; medir el video (PASOS_MANUALES 10) | recursos-visuales / personas |
| R-61 | Diap. 5: HU-01 a HU-03 operativas | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.119 (HU-01 a HU-05) | Ninguna | — |
| R-62 | Diap. 5: entorno de despliegue | **PARCIAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.120; la figura 58 (2749x1130 a h:240) es ilegible en la diapositiva; staging no ejecutado | Ver R-33; PASOS_MANUALES 8-9 | recursos-visuales / personas |
| R-63 | Diap. 5: validación con el usuario final | **MANUAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.121 `[COMPLETAR] (sin acta)` visible en la diapositiva | PASOS_MANUALES 5. Si no hay acta, reemplazar el `[COMPLETAR]` visible por «Pendiente de aceptación del usuario final» | personas + disenador-diapositivas |
| R-64 | Pitch diap. 5 (demo) | **MANUAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.123-134; la demo depende de staging o del video | PASOS_MANUALES 8-10 y 18 | personas |
| R-65 | Diap. 6: dashboard integrado | **NO CUMPLE** | Figura 62: la tarjeta «21/21 SP» y las barras HU-01..05 (5+3+3+2+3) suman 16 (falta EP-1.T = 5); el cuadro «✓ 77 pruebas automatizadas» no distingue declaradas de reproducidas (E-02) | Regenerar la figura 62 con las seis barras de la Tabla 14 (EP-1.T 5, HU-01 5, HU-03 3, HU-02 3, HU-04 2, HU-05 3 = 21) | recursos-visuales |
| R-66 | Diap. 6: historias planificadas vs completadas | **NO CUMPLE** | Figura 63 (E-03, E-04): completadas acumuladas 5-8-11-13-16 con rótulo «21 SP entregados»; período «01-28 Sep» incompatible con `git log` (todos los commits del 30/09); no es una serie temporal; las notas l.149 afirman que se reconstruyó del historial git | Rehacer con 2 sprints (planificado 13 y 8 SP; completado 21 el 30/09) o rotular «avance por historia» sin pretender una serie temporal; corregir las notas l.149 y entregables/semana-06-integrador/presentacion/GUION_EXPOSICION.md l.72 | recursos-visuales + disenador-diapositivas |
| R-67 | Diap. 6: densidad de defectos y cobertura | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.143: 2,0 defectos/KLOC y 99 % | Ninguna | — |
| R-68 | Diap. 6: impacto medido | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.144: 3 -> 1 sintético, sin atribuir impacto | Ninguna | — |
| R-69 | Pitch diap. 6 | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.146-154 | Ninguna | — |
| R-70 | Diap. 7: flujo de trazabilidad | **NO CUMPLE** | Figura 64: «77/77 automatizadas», glifos vacíos en cinco rótulos y en «✓», banner y texto pequeño (E-01, E-12) | Regenerar la 64 sin 77/77, sin glifos vacíos y sin banner | recursos-visuales |
| R-71 | Diap. 7: matriz de trazabilidad | **PARCIAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.160 muestra solo el flujo (figura 64) y no la matriz sintética; las notas l.170 la resumen | Incluir en la figura 64 las 8 columnas condensadas o una fila ejemplo B1 -> … -> 3→1 | recursos-visuales |
| R-72 | Diap. 7: conclusiones principales | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.162-164 | Ninguna | — |
| R-73 | Diap. 7: siguiente incremento (Unidad III) | **PARCIAL** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.165 es correcto; la figura 68 asigna INC-3 «Integración HIS», INC-4 «WhatsApp» e INC-6 «Evolución», contra las Tablas 5, 15 y 16 (INC-3 sin conexión, INC-4 mensajería, INC-6 tablero), y pone «Integración parcial con HIS» en INC-2 (E-08) | Regenerar la figura 68 con la Tabla 16 (Sprint 3 INC-2 y backlog técnico; S4 INC-3; S5 INC-4; S6-S7 INC-5; S7-S8 INC-6) | recursos-visuales |
| R-74 | Pitch diap. 7 | **CUMPLE** | entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md l.167-174 | Ninguna | — |
| R-75 | Exactamente 7 diapositivas, alto impacto visual, sin bloques de texto | **PARCIAL** | 7 diapositivas (OK). Palabras visibles (python-pptx, con título y paginador): D1 45, D2 31, D3 36, D4 54, D5 39, D6 42, D7 46; D1, D4, D6 y D7 superan las 40 recomendadas; figuras con banner de PlantUML y texto ilegible (D3, D4, D5) | Recortar D4 a <= 40 palabras, regenerar figuras (R-13, R-33, R-55) y revisar el PPTX en pantalla completa (PASOS_MANUALES 12) | disenador-diapositivas |

### E. Repositorio

| ID | Requisito | Estado | Evidencia | Acción correctiva | Responsable |
| --- | --- | --- | --- | --- | --- |
| R-76 | Código fuente del PMV | **CUMPLE** | `pmv_fastapi/app/` | Ninguna | — |
| R-77 | Scripts de BD | **CUMPLE** | `pmv_fastapi/db/01_esquema_postgresql.sql`, `pmv_fastapi/scripts/cargar_datos_prueba.py` | Ninguna | — |
| R-78 | Pruebas automatizadas | **PARCIAL** | `pmv_fastapi/tests/` (77). `.github/workflows/ci.yml` está en la raíz pero sin commit (`git status`: `?? .github/`) ni ejecución en verde | Commit, push y captura de Actions (PASOS_MANUALES 3) | sincronizador / personas |
| R-79 | README de despliegue | **PARCIAL** | `pmv_fastapi/README.md` correcto; el README raíz l.38 y l.47 sigue diciendo que el CI está en `pmv_fastapi/.github/workflows/ci.yml` y que copiarlo es la tarea S6-08 (ya HECHA) | Actualizar README.md l.38 y l.47: «CI en `.github/workflows/ci.yml` (raíz)» | sincronizador |
| R-80 | Tag `v1.0-PMV` | **PARCIAL** | Existe en origin (9ce90c3) pero no es alcanzable desde main (`git merge-base --is-ancestor v1.0-PMV main` falla; C-01) | Decisión del equipo (PASOS_MANUALES 14); si se mantiene, el informe l.677 ya lo documenta | personas |

### F. Rúbrica

| ID | Requisito | Estado | Evidencia | Acción correctiva | Responsable |
| --- | --- | --- | --- | --- | --- |
| R-81 | C1 Fundamentación y modelo | **PARCIAL** | Contenido completo, pero Figs. 1, 5 y 6 con errores (R-13, R-15, R-18) y portada con `[COMPLETAR]` | Resolver R-13, R-15 y R-18 | recursos-visuales |
| R-82 | C2 Operatividad y planificación | **PARCIAL** | Tablas 10-18 completas; Figs. 12-14 con errores (R-24); acta y horas `[COMPLETAR]` | Resolver R-24; PASOS_MANUALES 4-5 | recursos-visuales / personas |
| R-83 | C3 Categorización, arquitectura y pruebas | **PARCIAL** | Figs. 15, 16-18, 21, 22 y 25 con errores o defectos (R-27 a R-33); Sonar y staging sin ejecutar | Resolver R-27 a R-33 | recursos-visuales / personas |
| R-84 | C4 Trazabilidad y tablero de valor | **NO CUMPLE** | La matriz es correcta (R-35), pero el tablero que la sustenta (Figs. 13-14 y 62-63) tiene cifras incorrectas (R-24, R-65, R-66) | Regenerar 62 y 63 (E-02 a E-04) | recursos-visuales |
| R-85 | C5 Estructura visual de las diapositivas | **PARCIAL** | 7 diapositivas; errores de cifras en D2, D4, D6 y D7; legibilidad (R-75) | Resolver R-45, R-55, R-65, R-66, R-70 y R-75 | recursos-visuales + disenador-diapositivas |
| R-86 | C6 Demo operativa y despliegue | **MANUAL** | Staging no ejecutado; aceptación ausente; CI sin evidencia | PASOS_MANUALES 3, 8-10 | personas |
| R-87 | C7 Sustentación oral | **MANUAL** | Guion y preguntas listos (entregables/semana-06-integrador/presentacion/GUION_EXPOSICION.md) | PASOS_MANUALES 17-18 | personas |
| R-88 | C8 Defensa individual | **MANUAL** | Tablas de preguntas listas (entregables/semana-06-integrador/presentacion/GUION_EXPOSICION.md §3) | PASOS_MANUALES 18 | personas |

### G. Puntaje y exposición

| ID | Requisito | Estado | Evidencia | Acción correctiva | Responsable |
| --- | --- | --- | --- | --- | --- |
| R-89 | Distribución 8 + 12 = 20 puntos | **CUMPLE** | Estructura informativa; sin acción propia | Ninguna | — |
| R-90 | Guion de 7 minutos | **CUMPLE** | entregables/semana-06-integrador/presentacion/GUION_EXPOSICION.md §1: 1:05+1:05+1:05+1:05+1:25+0:40+0:35 = 7:00 (suma verificada) | Validar con el ensayo (PASOS_MANUALES 17) | personas |
| R-91 | PMV demostrable en vivo o en video | **MANUAL** | `pmv_fastapi/docs/evidencias/demo_pmv.mp4` existe (1,6 MB, duración no medida); no hay staging ejecutado | PASOS_MANUALES 8-10 | personas |

## 3. Errores de cifras detectados

Toda cifra de una figura o del texto que no coincide con la fuente es NO CUMPLE. Las fuentes son `coordinacion/s6/DATOS_PMV_FASTAPI.md` (DATOS), `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` (S3-4), el informe y `git log`. Se leyeron los PNG; para E-01 se confirmó con `grep` que los SVG de las figuras 59 y 64 contienen el mismo texto.

| N.° | Figura (archivo) | Dónde se usa | Valor mostrado | Valor correcto | Fuente |
| --- | --- | --- | --- | --- | --- |
| E-01 | `59_s6_piramide_pruebas` (título) y `64_s6_flujo_trazabilidad` (cuadro PRUEBAS) | Informe Fig. 22 (l.502) y Fig. 34 (l.635); diapositivas 4 y 7 | «Total: 77/77 en verde» y «77/77 automatizadas» | 77 pruebas declaradas en el tag (62 + 11 + 4). El 01/10 solo se reprodujeron 73 (62 + 11); las 4 E2E no se ejecutaron (falta `chromium_headless_shell-1194`) y la integración en PostgreSQL tampoco. Además la figura 59 pone la carga como cuarto nivel dentro del «Total», lo que sugiere 78: el escenario Locust no cuenta como prueba | DATOS §6 y §17; `pmv_fastapi/docs/evidencias/verificacion_s6_2026-10-01.md` |
| E-02 | `62_s6_tablero_metricas` | Informe Fig. 14 (l.392); diapositiva 6 | Tarjeta «5/5 HU, 21/21 Story Points» junto a un gráfico «SP Planificados vs Entregados» cuyas barras suman 16 (5, 3, 3, 2, 3); cuadro «✓ 77 pruebas automatizadas» | Las barras deben sumar 21: falta EP-1.T (5 SP). Tabla 14 del informe: EP-1.T 5, HU-01 5, HU-03 3, HU-02 3, HU-04 2, HU-05 3 = 21. El cuadro debe decir «77 declaradas; 73 reproducidas el 01/10» | S3-4 §10 y Tablas 19-20; informe Tabla 14; DATOS C-10 |
| E-03 | `63_s6_burnup_inc1` (valores) | Informe Fig. 13 (l.390); diapositiva 6 | Serie completada acumulada 5, 8, 11, 13, 16 con la anotación «✓ 21 SP entregados»; serie ideal 0, 5,25, 10,5, 15,75 y 21 | La serie completada debe terminar en 21 (incluye los 5 SP de EP-1.T). La serie «ideal» arranca en 0 para HU-01 sin motivo | Informe Tabla 14 |
| E-04 | `63_s6_burnup_inc1` (título y pie) | Informe l.386 y l.390; notas de la diapositiva 6 l.149; guion l.72 | «Burnup Real del Incremento 1, Planificado vs Completado (01-28 Sep 2026)», «Fuente: git log del tag v1.0-PMV» | `git log 9ce90c3` muestra que todos los commits y merges son del 2026-09-30: no existe una serie temporal del 01 al 28 de septiembre, y el eje X es por historia y no por fecha. El hecho verificable es «entrega el 30/09 frente al hito H1 del 28/09 (+2 días)» | `git log 9ce90c3 --format='%h %ad'` |
| E-05 | `67_s6_matriz_factores` | Informe Fig. 5 (l.170); diapositiva 2 | Incertidumbre Alto; Complejidad Medio; Riesgo Alto; Integración Medio; Datos/IA Bajo (con «Datos sintéticos») | Los cinco factores en nivel Alto con los textos de la Tabla 7 (Complejidad: modelo predictivo, API de mensajería, sincronización; Integración: HIS, mensajería, artefacto del modelo; Datos/IA: datos históricos de calidad variable, MLOps desde INC-5) | Informe Tabla 7 (l.160-166); S2 §1-2 |
| E-06 | `51_s6_ciclo_vida_tailoring` | Informe Fig. 6 (l.216); diapositiva 2 | Alt. 3 «Scrum sin DevOps» 2,95; Alt. 2 «Cascada + Testing» 3,85; «Scrum Puro 3/5 en S2» y «Cascada Pura 8/30» | Alt. 2 = Kanban + DevOps + DataOps (3,85); Alt. 3 = Incremental + Espiral sin automatización (2,95). Scrum puro suma 27/30 en la comparación de modelos (Tabla 8): «3/5» corresponde a un solo criterio (automatización) y mezcla escalas con «8/30» | Informe Tablas 8 y 9; S2 Tablas 3 y 6 |
| E-07 | `50_s6_as_is_vs_to_be` | Informe Fig. 1 (l.94); diapositiva 1 | M2-M3 «Alertas & Seguimiento (INC-2)»; M4-M5 «Integración HIS & WhatsApp (INC-3/4)»; M6 «Monitoreo Clínico (INC-5/6)» | M2 agenda INC-2; M3 recordatorios INC-4; M4 visita priorizada INC-3; M5 riesgo explicable INC-5; M6 captura sin conexión e indicadores INC-3 e INC-6 | Informe Tabla 5 (l.121-128) |
| E-08 | `68_s6_roadmap_incrementos` | Informe Fig. 35 (l.657); diapositiva 7 | INC-2 con «Integración parcial con HIS»; INC-3 «Integración HIS»; INC-4 «WhatsApp Business API»; INC-5 «MLOps (Piloto)»; INC-6 «Evolución, optimizaciones, documentación, capacitación»; H3/H4 en el Sprint 5 | INC-2 agenda y alertas; INC-3 sin conexión y sincronización (Sprint 4, H3); INC-4 mensajería y barreras (Sprint 5, H4); INC-5 datos y modelo; INC-6 tablero territorial (Sprints 7-8) | Informe Tablas 15 y 16 (l.329-353) |
| E-09 | `55_s6_modelo_datos_postgresql` | Informe Fig. 21 (l.468) | `v_ultimo_control` con «(nota: vista materializada para HU-04)» | Es una vista simple con `DISTINCT ON`, no una vista materializada | DATOS §5; `pmv_fastapi/db/01_esquema_postgresql.sql` |
| E-10 | `66_s6_adr_nfr` | Informe Fig. 15 (l.441); diapositiva 3 | ADR-002 «PWA (offline)» y encabezados de columna superpuestos al título | «PWA con borrador local»: el registro definitivo requiere conexión y la cola sin conexión es INC-3 | DATOS §13, ADR-002 |
| E-11 | `61_s6_carga_p95` | Informe Fig. 24 (l.542); diapositiva 4 | «2,170 → 2,336», «36.74 → 39.56 req/s» (punto decimal); anotaciones («+7,6 % más capacidad», «-81,3 % latencia») pisadas por los recuadros | Las cifras coinciden con DATOS §9 (2 170 → 2 336; 36,74 → 39,56; 310 → 58 ms; 2 200 → 74 ms). Solo es formato y legibilidad | DATOS §9 |
| E-12 | `50`, `51`, `52`, `53`, `54`, `55`, `58`, `64`, `68` | Informe Figs. 1, 6, 16-18, 21, 25, 34 y 35; diapositivas 1, 2, 3, 5 y 7 | Banner amarillo «Please use CSS style instead of skinparam padding» incrustado en la imagen; glifos vacíos «▯▯▯» y «✓ ▯» en las figuras 50, 64 y 68; la figura 58 mide 2749x1130 con texto diminuto | Sin banner (quitar `skinparam padding` del `.puml` o actualizar PlantUML), con fuentes que incluyan los glifos o reemplazar «✓» por texto, y la figura 58 en formato compacto con fuente >= 10 pt | `diagramas/src/*.puml` |

**Comprobaciones pedidas en la tarea.**

- **(a) «77/77 en verde»:** confirmado en la figura 59 (título) y en la 64. En el informe, el resumen (l.63), la Tabla 24 y l.515 hablan de 77 pruebas «declaradas» y explican que se reprodujeron 73, salvo que la Tabla 24 marca «En verde» las E2E y PostgreSQL (ver R-31). En el guion y en la diapositiva 4 se explicita «73 pasan el 01/10».
- **(b) Mezcla de «p95 310 → 58 ms» con «reporte 2 200 → 74 ms»:** no se detectó en el texto del informe ni de las diapositivas: en cada lugar los dos pares aparecen con su etiqueta (agregado frente a reporte): resumen l.63, Tabla 21 l.439, Tabla 26, conclusión 2 l.644, Tabla 30 l.630, diapositivas 3 y 4. En la figura 61 las cifras también están separadas por endpoint y «Agregado». El riesgo es la anotación «97 % mejora» sobre la barra del reporte, que no indica «2 200 → 74 ms»: conviene rotularla (E-11).
- **«1 prueba de carga» contada como prueba:** el informe nunca la suma (Tabla 23: «1 escenario», total 62 + 11 + 4 = 77). Sí se induce en la figura 59 (E-01) y en la frase del pitch de la diapositiva 4 y del guion l.37 (R-59).
- **Otros valores contrastados y correctos:** cobertura 99 % (641 sentencias, 2 sin cubrir; 98 ramas, 4 parciales) y porcentajes por módulo en la figura 60; 2,0 defectos/KLOC; 3 → 1 registros; p95 por endpoint 250 → 75, 56 → 30 y 100 → 36 ms; 21 SP y 113 h-p; 4,75 / 3,85 / 2,95; 285 palabras de resumen; suma de tiempos del guion = 7:00. Nota: la reproducción del 01/10 dio 548 sentencias (Python 3.14) frente a 641; el informe lo explica en l.515 y la figura 60 muestra el valor declarado.

## 4. Lista priorizada de correcciones automáticas (agentes)

| Prioridad | Responsable | Archivo y línea | Qué cambiar |
| --- | --- | --- | --- |
| 1 | recursos-visuales | `diagramas/src/62_*`, `63_*` y sus PNG/SVG | Regenerar con 6 barras (EP-1.T 5 SP) y completado = 21; eliminar «01-28 Sep» y el pretendido burnup real (E-02 a E-04). Tarea S6-13 |
| 2 | recursos-visuales | `diagramas/src/59_*`, `64_*` | Quitar «77/77 en verde»; mostrar «77 declaradas; 73 reproducidas»; sacar la carga del total (E-01). Tarea S6-14 |
| 3 | recursos-visuales | `diagramas/src/67_*`, `51_*` | Cinco factores en «Alto» con los textos de la Tabla 7; alternativas de la Tabla 9 y Scrum 27/30 (E-05, E-06). Tarea S6-15 |
| 4 | recursos-visuales | `diagramas/src/50_*`, `68_*` | Alinear los incrementos con las Tablas 5, 15 y 16 (E-07, E-08). Tarea S6-16 |
| 5 | recursos-visuales | `diagramas/src/52_*` a `58_*`, `66_*`, `61_*`, `65_*` | Quitar el banner de PlantUML y los glifos vacíos; «vista», «PWA con borrador local»; figura 58 compacta; añadir HU-04 al collage 65; coma decimal en la 61 (E-09 a E-12). Tarea S6-17 |
| 6 | redactor-informe-integrador | `Informe_Integrador_Anemia_Junin.md` l.386, l.390 | Reescribir el texto y el pie de la Fig. 13 tras la nueva figura 63 (sin «historial git» como serie temporal). Tarea S6-18 |
| 7 | redactor-informe-integrador | mismo archivo, l.511-513 | Cambiar «En verde» por «En verde según el tag; no reproducido el 01/10/2026» en las filas E2E, PostgreSQL y carga (R-31) |
| 8 | redactor-informe-integrador | mismo archivo, l.21 | Unificar el género del rol con README raíz l.23 |
| 9 | disenador-diapositivas | `Presentacion_Integrador.md` l.97-101 | Reducir a <= 40 palabras visibles; dos figuras grandes en lugar de tres de h:240 (R-55, R-75). Tarea S6-19 |
| 10 | disenador-diapositivas | `Presentacion_Integrador.md` l.121; l.149; l.106; `GUION_EXPOSICION.md` l.37, l.72 | Sustituir `[COMPLETAR]` visible por «Pendiente de aceptación del usuario final»; corregir la afirmación del burnup (E-04); frase «62 + 11 + 4 = 77; la carga no cuenta» (R-59) |
| 11 | disenador-diapositivas | `generar_presentacion.py` y `exportados/semana-06/` | Regenerar el PPTX con las figuras nuevas; renombrar a `Presentacion_Integrador.pptx` o fijar el nombre en PROTOCOLO_S6 y RUTAS.md |
| 12 | sincronizador | `README.md` l.23, l.38, l.47 | CI en la raíz (tarea S6-08 hecha); «Ingeniero» de Desarrollo; RUTAS.md l.33 y l.126-129 alinear `GUION_EXPOSICION.md` y las rutas reales |
| 13 | sincronizador | `.github/`, `exportados/`, informe, presentación y figuras | Confirmar los cambios en la rama (git add y commit). Hoy no están confirmados |
| 14 | conversor-entregas | `exportados/semana-06/Informe_Integrador_Anemia_Junin.{pdf,docx}` | Ejecutar S6-05 solo cuando 1 a 8 y los `[COMPLETAR]` estén resueltos |
| 15 | inspector-guia | `INSPECCION_S6.md` | Repetir esta inspección tras las correcciones |

## 5. Declaración final

**NO LISTO PARA ENTREGAR.** Prerrequisitos para pasar a LISTO: (1) correcciones 1 a 11 de la sección 4; (2) PASOS_MANUALES 1 a 12 resueltos; (3) PDF del informe y de las diapositivas generados; (4) nueva inspección sin NO CUMPLE.
