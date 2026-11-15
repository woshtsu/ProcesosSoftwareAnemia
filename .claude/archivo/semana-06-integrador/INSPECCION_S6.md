# Inspección S6, versión 2 (reinspección): cumplimiento de la consigna integradora

- **Fecha:** 2026-10-01
- **Inspector:** inspector-guia (tarea S6-06, reinspección tras S6-13 a S6-20)
- **Rama y commit:** `feature/s6-integrador-final`, `fdc50c5` (árbol limpio; verificado con `git status`). Sin push.
- **Tag:** `v1.0-PMV` -> 9ce90c3 en origin; no es alcanzable desde la rama (`git merge-base --is-ancestor` falla; C-01).
- **Objetos inspeccionados:**
  - informe (680 líneas) y checklist;
  - `Presentacion_Integrador.md`, `GUION_EXPOSICION.md` y `generar_presentacion.py`;
  - PPTX (python-pptx **y renderizado con PowerPoint COM sobre una copia en el scratchpad**: se vieron las 7 diapositivas como imagen);
  - PNG `50` a `68`, **leídos como imagen uno por uno**;
  - README raíz y `.github/workflows/ci.yml`;
  - `exportados/semana-06/*.pdf` y `*.docx` (aparecieron durante la inspección: ver §6).
- **Leyenda:** CUMPLE / PARCIAL / NO CUMPLE / MANUAL (el único hueco es un dato o una acción de una persona; ver `PASOS_MANUALES.md`).
- **Verificaciones automáticas:**
  - 35 imágenes del informe, 14 de la presentación y 27 enlaces del README: 0 rotos;
  - 35 figuras y 31 tablas en el informe;
  - resumen de 285 palabras (límite 300);
  - 0 ocurrencias de `CARGA_CIERRE`, `[PENDIENTE`, `tag pendiente` y `pendiente -->` en informe, presentación, guion y PDF;
  - 17 líneas con `[COMPLETAR]` en el informe (datos humanos), 3 en el guion y 1 en las notas de la diapositiva 5;
  - PPTX: 7 diapositivas, 40/29/34/38/38/34/39 palabras visibles (todas <= 40), 7 con notas (156 a 254 palabras) y 14 imágenes.

## 0. Veredicto

**NO LISTO PARA ENTREGAR**, pero la situación cambió mucho: ya no hay ningún NO CUMPLE, los 12 errores de cifras E-01 a E-12 están resueltos y el informe es coherente con DATOS §17. Lo que bloquea ahora es:

1. **Datos humanos** (17 `[COMPLETAR]` visibles también en el PDF y el DOCX): códigos, docente, fecha, acta/Product Owner, horas, captura de CI, SonarCloud, staging, duración del video (PASOS_MANUALES 1 a 11).
2. **Legibilidad de las figuras en las diapositivas** (hallazgo N-01, nuevo y corregible por agentes): en D1, D3, D4, D5 y D7 las figuras ocupan cerca de 40 % de la diapositiva y su texto equivale a 3 a 6 pt; el PDF de las diapositivas hereda el defecto.
3. Ejecución real pendiente: CI en verde en GitHub, staging con Docker, E2E, ensayo de 7 minutos y defensa individual.

## 1. Antes y después (v1 -> v2)

Cada celda es `CUMPLE / total` y entre paréntesis el % ponderado (CUMPLE = 1; PARCIAL = 0,5; NO CUMPLE y MANUAL = 0).

| Bloque | Total | v1: CUMPLE (pond.) | v2: CUMPLE (pond.) | v2 PARCIAL | v2 NO CUMPLE | v2 MANUAL |
| --- | --- | --- | --- | --- | --- | --- |
| A. Modalidad y entregables | 5 | 2 = 40 % (50 %) | 3 = 60 % (70 %) | 1 | 0 | 1 |
| B. Portada | 4 | 2 = 50 % (50 %) | 2 = 50 % (50 %) | 0 | 0 | 2 |
| C. Estructura del informe | 30 | 16 = 53 % (70 %) | 25 = 83 % (85 %) | 1 | 0 | 4 |
| D. Siete diapositivas | 36 | 18 = 50 % (64 %) | 25 = 69 % (82 %) | 9 | 0 | 2 |
| E. Repositorio | 5 | 2 = 40 % (70 %) | 3 = 60 % (60 %) | 0 | 0 | 2 |
| F. Rúbrica | 8 | 0 = 0 % (25 %) | 1 = 12,5 % (37,5 %) | 4 | 0 | 3 |
| G. Puntaje y exposición | 3 | 2 = 67 % (67 %) | 2 = 67 % (67 %) | 0 | 0 | 1 |
| **Global** | **91** | **42 = 46,2 % (61,5 %)** | **61 = 67,0 % (75,3 %)** | **15** | **0** | **15** |

- v1 tenía 42 CUMPLE, 28 PARCIAL, 12 NO CUMPLE y 9 MANUAL. v2 tiene 61 CUMPLE, 15 PARCIAL, 0 NO CUMPLE y 15 MANUAL.
- Algunos PARCIAL de v1 pasaron a MANUAL porque su único hueco restante es un dato humano (R-20, R-21, R-32, R-34, R-78, R-80).
- Excluyendo los 15 MANUAL (lo que solo pueden hacer personas), el cumplimiento automático es 61/76 = **80,3 %** (ponderado 90,1 %). El hueco restante de los agentes son los 15 PARCIAL, casi todos por una sola causa (legibilidad en diapositivas, N-01).
- Criterio más estricto en v2: se marcó PARCIAL toda diapositiva cuyo esquema visual obligatorio queda ilegible al proyectarlo (R-40, R-45, R-50, R-55, R-60, R-62, R-70), aunque el contenido sea correcto.

## 2. Estado de E-01 a E-12

Se leyeron los PNG regenerados como imagen y se contrastaron con DATOS §9 y §17 y con las Tablas 5, 7, 9, 14, 15 y 16 del informe.

| N.° | Figura | Estado | Verificación en v2 |
| --- | --- | --- | --- |
| E-01 | 59, 64 | **RESUELTO** | Sin «77/77 en verde». 59: 62 + 11 + 4 = 77 declaradas, 62 + 11 = 73 reproducidas, 4 E2E sin reproducir, carga en recuadro aparte «no cuenta en el total». 64: «77 declaradas (62+11+4); 73 reproducidas el 01/10/2026» |
| E-02 | 62 | **RESUELTO** | Seis barras 5, 5, 3, 3, 2, 3 = 21 SP; tarjeta 21/21; cuadro «77 declaradas; 73 reproducidas» |
| E-03 | 63 | **RESUELTO** | Completado acumulado 5-10-13-16-18-21, termina en 21. Reserva: las dos series son idénticas (el «completado» se deriva del tag, no se midió): la figura es honesta pero poco informativa |
| E-04 | 63 | **RESUELTO** | Sin «01-28 Sep»; pie «entrega 30/09 frente al hito H1 del 28/09 (+2 días)»; informe l.386-390 y notas D6 alineados |
| E-05 | 67 | **RESUELTO** | Cinco factores en Alto con los textos de la Tabla 7 |
| E-06 | 51 | **RESUELTO** | Alt. 1 4,75; Alt. 2 3,85 (Kanban + DevOps + DataOps); Alt. 3 2,95 (Incremental + Espiral); Cascada 8/30 y Scrum 27/30 con la escala de la Tabla 8. Residuo: la nota de fuente cita `pmv_fastapi/.github/workflows/ci.yml` (ruta de referencia, no el CI efectivo; N-05) |
| E-07 | 50 | **RESUELTO** | M1 a M6 con INC-1, 2, 4, 3, 5 y 3/6 = Tabla 5; sin banner ni glifos |
| E-08 | 68 | **RESUELTO** | INC-2 agenda y alertas (Sprint 3); INC-3 sin conexión (S4); INC-4 mensajería (S5); INC-5 datos y modelo; INC-6 tablero (S7-S8); fechas = Tabla 16 |
| E-09 | 55 | **RESUELTO** | `v_ultimo_control`: «vista simple, no materializada; DISTINCT ON» |
| E-10 | 66 | **RESUELTO** | ADR-002 «PWA con borrador local (el registro requiere conexión)»; cabecera sin solape |
| E-11 | 61 | **RESUELTO** | Coma decimal (2 170 -> 2 336; 36,74 -> 39,56); anotación «Reporte: 2 200 ms a 74 ms (97 % menos...)» sin solape; +7,6 %, -81,3 % y +7,7 % recalculados y correctos |
| E-12 | 50-58, 64, 68 | **RESUELTO** (con un residuo) | Sin banner de PlantUML ni glifos vacíos (comprobado a ojo en las 19 figuras). La 58 ahora es compacta (3443x933, 15 pt), pero en una página A4 equivale a unos 5,5 pt y en la diapositiva a unos 6 pt (N-02) |

## 3. Errores nuevos o residuales (corregibles por agentes), priorizados

| Prio. | ID | Dónde | Problema | Acción y responsable |
| --- | --- | --- | --- | --- |
| 1 | N-01 | `presentacion/Presentacion_Integrador.md` l.37, 57, 77, 97, 118, 161 y `generar_presentacion.py` (l.119-135) | Con las diapositivas renderizadas en PowerPoint, las figuras miden entre 3 y 6 pt equivalentes: D1 (fig. 50 vertical, 3 x 4,5 pulgadas en el centro), D3 (53 y 66 a media anchura), D4 (tres figuras de 4 pulgadas), D5 (collage 65 y despliegue 58) y D7 (64 y 68, esta última vertical). Hay franjas vacías enormes. D2 y D6 son aceptables | disenador-diapositivas con recursos-visuales: una figura dominante por diapositiva a >= 80 % del ancho útil; D1 con una versión horizontal de la 50; D4 solo 59 + 61 (la 60 queda en el informe); D5 solo el collage 65; D7 con la 64 grande y la 68 sustituida por una línea de texto o una versión horizontal; fuente mínima equivalente de 10 pt. Regenerar PPTX y PDF |
| 2 | N-02 | `diagramas/src/58_s6_despliegue_docker_ci.puml` | Aun compacta, la fig. 58 es de 3,7:1: unos 5,5 pt en A4 | recursos-visuales: dos filas (CI arriba, staging abajo) a unos 2:1 |
| 3 | N-03 | `Presentacion_Integrador.md` l.122 (D5) | «pendiente de acta (ver anexo)»: no existe ningún anexo del acta (`entregables/semana-06-integrador/anexos/` solo tiene dos archivos viejos del 25/09) | disenador-diapositivas: «Aceptación del usuario: pendiente (verificado técnicamente)» |
| 4 | N-04 | `GUION_EXPOSICION.md` l.13 y l.15; `Presentacion_Integrador.md` l.84 | «Ingeniero de Desarrollo y Prototipado» para Tania; el informe y el README dicen «Ingeniera» (el PASOS_MANUALES 2 ya lo exigía) | disenador-diapositivas: «Ingeniera» (regenerar PPTX/PDF) |
| 5 | N-05 | `diagramas/src/51_*.puml` l.2 y nota; `52`, `53`, `55`, `58`, `64` | Notas de fuente con rutas internas (`coordinacion/s6/DATOS_PMV_FASTAPI.md`, `CONTEXTO_PROCESOS...`) y el CI de referencia `pmv_fastapi/.github/...` dentro de figuras que se entregan | recursos-visuales: citar el informe (Tabla o sección) y `.github/workflows/ci.yml` |
| 6 | N-06 | fig. 64 (`diagramas/src/64_*.puml`) | R-71: no muestra la matriz de 8 columnas ni una fila ejemplo; layout en escalera con texto de 5 pt; nota «Unidad III (INC-1 entregada)» confusa; la rama de futuro habla de «Reducción tiempos / Mejoría clínica / IRC/IA» sin rotular que no están medidos | recursos-visuales: una fila ejemplo B1 -> M1 -> híbrido -> ADR -> CP -> HU-01 a HU-05 -> 3 -> 1 en horizontal; la rama futura rotulada «no medido» |
| 7 | N-07 | fig. 60 (`60_s6_cobertura.py`) | El título dice «548 sentencias reproducidas el 01/10/2026 (641 declaradas)», pero las barras por módulo son las del tag (641) | recursos-visuales: título «641 sentencias declaradas en el tag; reproducción del 01/10: 548 y 99,07 %» y subtítulo «porcentajes por módulo: tag» |
| 8 | N-08 | Informe l.510 (Tabla 24, fila Unitarias) | El resultado es «Reproducido el 01/10/2026: 62 pasan», pero la evidencia cita README y mensaje del tag | redactor-informe-integrador: evidencia `verificacion_s6_2026-10-01.md` |
| 9 | N-09 | `GUION_EXPOSICION.md` l.54 (D6); notas D6 de `Presentacion_Integrador.md` l.154 | «el hito H1 se cumplió con dos días de retraso» es contradictorio (se incumplió); la «Nota (C-10)» interna se queda en las notas del orador | disenador-diapositivas: «se entregó 2 días después del hito H1»; borrar la nota C-10 |
| 10 | N-10 | fig. 52 (`52_*.puml`) | Actores y sistemas de INC-3/INC-4/futuro con trazo continuo igual que lo entregado (E-12, mitad pendiente) | recursos-visuales: línea discontinua para lo no entregado |
| 11 | N-11 | `entregables/semana-06-integrador/anexos/*.md` | Dos archivos de la revisión del 25/09 (menciones a Flask, 266, `PENDIENTE`) siguen en la carpeta de entrega | sincronizador: archivarlos con `git mv` en `archivo/` (o confirmar que no se suben) |
| 12 | N-12 | `exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf` | Metadatos `Title = Informe_Integrador_Anemia_Junin_temp`; formato Letter y no A4; tablas de portada y Tabla 1 muy estrechas | conversor-entregas: regenerar con título, A4 y tablas ajustadas, **después** de los pasos manuales (así se reexporta una sola vez) |
| 13 | N-13 | `herramientas/conversion/exportar_s6.py` | Reexportación (cuando se cierren los datos humanos) | conversor-entregas: ejecutar el script otra vez; sin otra acción hoy |
| 14 | N-14 | `exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf` pp. 43-44 | La captura 07 (vista móvil, 780x1688) se imprime dos veces: p. 43 (página casi vacía, sin rótulo) y p. 44 (con el rótulo de la Figura 32). Es un salto de página mal resuelto de la imagen alta | conversor-entregas: limitar la altura de las capturas (por ejemplo a 9 cm) o `page-break-inside: avoid` y reexportar. Además comprobar que el informe de S6-05 no repita «12 figuras» |

## 4. Lo que está al 100 % automatizable y hecho

- Estructura del informe (portada, 6 secciones, 31 tablas, 35 figuras, resumen de 285 palabras, matriz de trazabilidad de 8 columnas en orden, 3 conclusiones, 3 lecciones, siguiente incremento INC-2).
- Coherencia de cifras entre informe, diapositivas, notas, guion y figuras: ver §5.
- 7 diapositivas (PPTX y PDF de 7 páginas), cada una con <= 40 palabras visibles, imágenes y notas del orador; guion de 7:00 exactos (1:05 + 1:05 + 1:05 + 1:05 + 1:25 + 0:40 + 0:35).
- 19 figuras 50 a 68 corregidas, sin banner ni glifos vacíos.
- Repositorio: código, `db/`, `tests/`, README raíz y de `pmv_fastapi`, CI en `.github/workflows/ci.yml` (raíz, confirmado en `fdc50c5`), 0 enlaces rotos, 0 marcadores prohibidos.
- Exportación del informe a PDF (50 páginas, 35 figuras embebidas más 1 duplicada, 0 marcadores prohibidos) y DOCX (35 imágenes, 32 tablas), pendiente de reexportar al cerrar los `[COMPLETAR]`.

## 5. Coherencia cruzada de cifras y nombres

Contrastado informe, diapositivas, notas, guion y figuras con DATOS §17 y las tablas del informe. **Sin discrepancias de cifras.**

| Cifra o nombre | Valor | Dónde coincide |
| --- | --- | --- |
| Pruebas | 77 declaradas (62 + 11 + 4); 73 reproducidas el 01/10; carga aparte y fuera del total | resumen y Tablas 23-24, D4 y notas, guion, figs. 59, 62 y 64 |
| Cobertura | 99 % (641 sentencias, 2 sin cubrir; reproducida 99,07 % con 548) | Tabla 25, D4, guion, figs. 60 y 62 (el título de la 60 mezcla: N-07) |
| Carga | 310 -> 58 ms agregado; 2 200 -> 74 ms reporte; 39,6 req/s; 0 fallos; siempre rotulados por separado | Tabla 26, D4, D3, guion, figs. 59, 61, 62 y 66 |
| SP y calendario | 21 SP (13 + 8), 113 h-p, hito H1 28/09 frente a entrega 30/09 (+2 días) | Tablas 14 y 16, D6, guion, figs. 62, 63 y 68 |
| Modelo | 4,75 / 3,85 / 2,95; Cascada 8/30; Scrum 27/30 | Tablas 8-9, D2, guion, fig. 51 |
| Defectos | 2 (DEF-01, DEF-02), 1,02 KLOC = 2,0/KLOC, 0 abiertos | Tabla 27, D6, guion, fig. 62 |
| Indicador de valor | 3 -> 1 registros (sintético) | resumen, Tabla 6, D1, D6, D7, figs. 50, 62 y 64 |
| Nombres y roles | Porras V. (Ingeniero de Proceso), Auqui H. (**Ingeniera**), Huamani R. | Informe, README y figuras coherentes; el guion y la nota D3 dicen «Ingeniero» (N-04) |
| Siguiente incremento | INC-2, agenda y alertas, Sprint 3 | l.656 del informe, D7, guion, fig. 68 |

## 6. Exportados (S6-05)

Aparecieron durante la inspección. Revisados con pypdf y zipfile; S6-05 ya figura HECHO con su informe (`informes/2026-10-01_conversor-entregas_s6-05.md`); se tratan como **provisionales** porque el informe conserva 18 `[COMPLETAR]`.

| Archivo | Resultado |
| --- | --- |
| `Informe_Integrador_Anemia_Junin.pdf` (7,5 MB) | 50 páginas (Letter), 36 imágenes, índice y las 6 secciones, portada y Tabla 31. 0 `CARGA_CIERRE`, 0 `[PENDIENTE`, 0 `tag pendiente`, 0 cifras Flask. **18 apariciones de `COMPLETAR`** (esperado: datos humanos). **Figuras: se verificaron una por una (pypdf, hash de cada XObject y rótulos): están embebidas las 35 figuras (rótulos «Figura 1» a «Figura 35» todos presentes), no 12; el informe del conversor que dice «12 figuras embebidas» es incorrecto.** Hay 36 imágenes porque la captura 07 (Figura 32) aparece duplicada: el mismo objeto `X145` en la página 43 (sin rótulo ni texto) y en la 44 (N-14). Defectos de formato: N-12 y N-14 |
| `Informe_Integrador_Anemia_Junin.docx` (6,0 MB) | 35 imágenes, 32 tablas, 18 `COMPLETAR`, 0 marcadores prohibidos. No se pudo renderizar (sin Word); revisar a mano |
| `Presentacion_Integrador_Anemia_Junin.pdf` (1,8 MB) | 7 páginas de 960x540, creado con PowerPoint; 0 `COMPLETAR`, 0 `PENDIENTE`, 0 `77/77`. Hereda la ilegibilidad de las figuras (N-01) |
| `Presentacion_Integrador_Anemia_Junin.pptx` | 7 diapositivas, ver §0 y N-01 |

## 7. Matriz R-01 a R-91 (estado v2)

Leyenda de causa: **L** = legibilidad de la figura en la diapositiva (N-01). Rutas relativas a la raíz.

### A. Modalidad y entregables

| ID | Requisito | v1 | v2 | Evidencia | Acción | Responsable |
| --- | --- | --- | --- | --- | --- | --- |
| R-01 | Informe en PDF con formato oficial | NO CUMPLE | **PARCIAL** | `exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf`: 50 p., 18 `COMPLETAR`, defectos N-12 | Cerrar PASOS_MANUALES 1-7 y reexportar | personas + conversor-entregas |
| R-02 | 7 diapositivas en PDF/PPTX | PARCIAL | **CUMPLE** | PPTX y PDF con 7 páginas | Ninguna (legibilidad en R-75) | — |
| R-03 | Enlace al repo | CUMPLE | **CUMPLE** | Informe l.666, Tabla 31 | Ninguna | — |
| R-04 | 7 min + 5 min individuales | MANUAL | **MANUAL** | Guion §1 y §3 | PASOS 17-18 | personas |
| R-05 | Propósito integrador | CUMPLE | **CUMPLE** | Secciones 2.1 a 3.4 y Tabla 30 | Ninguna | — |

### B. Portada

| ID | Requisito | v1 | v2 | Evidencia | Acción | Responsable |
| --- | --- | --- | --- | --- | --- | --- |
| R-06 | Título y subtítulo | CUMPLE | **CUMPLE** | Informe l.1-3 | Ninguna | — |
| R-07 | Carrera, asignatura y proyecto | CUMPLE | **CUMPLE** | l.7-9 | Ninguna | — |
| R-08 | Integrantes con código, rol y mapeo | MANUAL | **MANUAL** | l.20-22 y l.35 `COMPLETAR`; el rol «Ingeniera» ya es coherente en informe y README; no en el guion (N-04) | PASOS 1-2; corregir N-04 | personas / disenador-diapositivas |
| R-09 | Fecha y docente | MANUAL | **MANUAL** | l.10-11 `COMPLETAR` | PASO 1 | personas |

### C. Estructura del informe

| ID | Requisito | v1 | v2 | Evidencia | Acción | Responsable |
| --- | --- | --- | --- | --- | --- | --- |
| R-10 | Resumen <= 300 palabras | CUMPLE | **CUMPLE** | `sed -n 57,65p` + `wc -w` = 285 | Ninguna | — |
| R-11 | Diagnóstico y matriz de actores | CUMPLE | **CUMPLE** | l.73-88, Tabla 3 | Ninguna | — |
| R-12 | AS-IS y >= 5 brechas | CUMPLE | **CUMPLE** | l.92-111, Tabla 4 (6 brechas) | Ninguna | — |
| R-13 | TO-BE y matriz de intervención | PARCIAL | **CUMPLE** | Fig. 1 (50) alineada con la Tabla 5, sin banner (E-07) | Ninguna | — |
| R-14 | Cadena de valor e indicadores | CUMPLE | **CUMPLE** | l.134-150, Tabla 6 | Ninguna | — |
| R-15 | Matriz de factores | NO CUMPLE | **CUMPLE** | Fig. 5 (67) con 5 niveles Alto = Tabla 7 | Ninguna | — |
| R-16 | Comparación de 5 modelos | CUMPLE | **CUMPLE** | Tabla 8 (7 enfoques) | Ninguna | — |
| R-17 | Justificación y tailoring | CUMPLE | **CUMPLE** | Tabla 9 | Ninguna | — |
| R-18 | Gráfico del modelo aplicado | NO CUMPLE | **CUMPLE** | Fig. 6 (51) = Tablas 8-9 (E-06); residuo N-05 | Opcional N-05 | recursos-visuales |
| R-19 | Matriz de actividades | CUMPLE | **CUMPLE** | Tabla 10, Fig. 8 | Ninguna | — |
| R-20 | Matriz RAE | PARCIAL | **MANUAL** | Tabla 11 completa; l.263 `COMPLETAR` (Product Owner) | PASO 5 | personas |
| R-21 | DoD por actividad | PARCIAL | **MANUAL** | Tabla 12; l.277 y l.280 `COMPLETAR` | PASOS 3 y 5 | personas |
| R-22 | WBS | CUMPLE | **CUMPLE** | Fig. 9, Tabla 13 | Ninguna | — |
| R-23 | Estimación, priorización y plan | CUMPLE | **CUMPLE** | Tablas 14-16; l.323 `COMPLETAR` de horas (opcional, PASO 4) | Ninguna | — |
| R-24 | Seguimiento y desviaciones | NO CUMPLE | **CUMPLE** | l.386-392 corregidas; Figs. 13 (63) y 14 (62) correctas (E-02 a E-04) | Ninguna | — |
| R-25 | Clasificación de procesos | CUMPLE | **CUMPLE** | Tabla 19 | Ninguna | — |
| R-26 | Matriz de tailoring | CUMPLE | **CUMPLE** | Tabla 20 (l.424 `COMPLETAR`: PASO 6) | PASO 6 | personas |
| R-27 | ADR con NFR | PARCIAL | **CUMPLE** | Tabla 21; Fig. 15 (66) corregida (E-10) | Ninguna | — |
| R-28 | C4 niveles 1, 2 y 3 | PARCIAL | **CUMPLE** | Figs. 16-18 sin banner; residuo N-10 | Opcional N-10 | recursos-visuales |
| R-29 | Modelo de datos y API | PARCIAL | **CUMPLE** | Fig. 21 (55) «vista simple»; Tabla 22; `openapi.json` | Ninguna | — |
| R-30 | Pirámide de 4 niveles con casos | NO CUMPLE | **CUMPLE** | Tabla 23; Fig. 22 (59) sin «77/77» (E-01) | Ninguna | — |
| R-31 | Registro de ejecución y cobertura | PARCIAL | **CUMPLE** | Tabla 24 (l.512-514 «según el tag; no reproducido»), Tabla 25, Fig. 23; residuos N-07 y N-08 | N-07, N-08 | recursos-visuales / redactor |
| R-32 | Análisis estático y defectos | PARCIAL | **MANUAL** | Ruff y Tabla 27 completos; l.551 `COMPLETAR` (SonarCloud) | PASO 7 | personas |
| R-33 | Arquitectura del despliegue | PARCIAL | **PARCIAL** | Fig. 25 (58) compacta pero de unos 5,5 pt en A4 (N-02); staging no ejecutado (l.583) | N-02; PASOS 8-9 | recursos-visuales / personas |
| R-34 | Evidencia del incremento operativo | PARCIAL | **MANUAL** | 8 capturas y video, enlaces válidos; l.615 y l.617 `COMPLETAR` | PASOS 5 y 10 | personas |
| R-35 | Matriz de 8 columnas | CUMPLE | **CUMPLE** | Tabla 30, cabecera correcta | Ninguna | — |
| R-36 | Tres conclusiones | CUMPLE | **CUMPLE** | l.644-646 | Ninguna | — |
| R-37 | Tres lecciones | CUMPLE | **CUMPLE** | l.650-652 (l.652 `COMPLETAR`: PASO 6) | PASO 6 | personas |
| R-38 | Tag `v1.0-PMV` | CUMPLE | **CUMPLE** | `git ls-remote --tags origin`: 9ce90c3; l.667 y l.678 | Ninguna | — |
| R-39 | README de despliegue | CUMPLE | **CUMPLE** | `pmv_fastapi/README.md` | Ninguna | — |

### D. Siete diapositivas

| ID | Requisito | v1 | v2 | Evidencia | Acción | Responsable |
| --- | --- | --- | --- | --- | --- | --- |
| R-40 | D1: comparativo AS-IS vs TO-BE | PARCIAL | **PARCIAL** | Contenido correcto (fig. 50 = Tabla 5); en la diapositiva es una figura vertical de 3 x 4,5 pulgadas con texto de ~4 pt (L) | N-01 | disenador-diapositivas / recursos-visuales |
| R-41 | D1: problema y brechas | CUMPLE | **CUMPLE** | Texto visible «Brechas B1-B6» y notas | Ninguna | — |
| R-42 | D1: cadena de valor | CUMPLE | **CUMPLE** | «Datos -> Software -> Decisión -> Impacto» | Ninguna | — |
| R-43 | D1: indicador de valor | CUMPLE | **CUMPLE** | «3 registros -> 1» | Ninguna | — |
| R-44 | Pitch D1 | CUMPLE | **CUMPLE** | Notas y guion 1:05 | Ninguna | — |
| R-45 | D2: factores + ciclo adaptado | NO CUMPLE | **PARCIAL** | Datos correctos (E-05, E-06); la matriz se lee, el ciclo (51) a ~5 pt no (L) | N-01 | disenador-diapositivas |
| R-46 | D2: factores determinantes | NO CUMPLE | **CUMPLE** | Fig. 67 legible en la diapositiva y coherente con las notas | Ninguna | — |
| R-47 | D2: híbrido | CUMPLE | **CUMPLE** | Texto de D2 | Ninguna | — |
| R-48 | D2: rechazo de Cascada y Scrum puro | PARCIAL | **CUMPLE** | Texto «Cascada pura (8/30) y Scrum puro»; fig. 51 con 8/30 y 27/30 | Ninguna | — |
| R-49 | Pitch D2 | CUMPLE | **CUMPLE** | Notas y guion | Ninguna | — |
| R-50 | D3: C4 N2 + cuadro ADR | PARCIAL | **PARCIAL** | Figuras 53 y 66 correctas, a ~4 y ~3 pt (L) | N-01 | disenador-diapositivas |
| R-51 | D3: estructura y por qué no gateway ni caché | CUMPLE | **CUMPLE** | Texto de D3 | Ninguna | — |
| R-52 | D3: ADR críticos | PARCIAL | **CUMPLE** | Texto «ADR-003 integridad · ADR-006 latencia · ADR-002 disponibilidad»; fig. 66 corregida | Ninguna | — |
| R-53 | D3: protocolos | CUMPLE | **CUMPLE** | «REST/JSON + OpenAPI 3.1: sin WebSockets ni gRPC» | Ninguna | — |
| R-54 | Pitch D3 | CUMPLE | **CUMPLE** | Notas y guion | Ninguna | — |
| R-55 | D4: pirámide + cobertura + carga | NO CUMPLE | **PARCIAL** | Figuras 59, 60 y 61 correctas y sin «77/77», pero tres figuras de 4 pulgadas con ~3 pt (L) | N-01 | disenador-diapositivas |
| R-56 | D4: cobertura | CUMPLE | **CUMPLE** | «Cobertura 99 %» | Ninguna | — |
| R-57 | D4: p95 y throughput | CUMPLE | **CUMPLE** | «p95 310 -> 58 ms»; req/s en la figura 61 y las notas | Ninguna | — |
| R-58 | D4: DoD | CUMPLE | **CUMPLE** | «DoD cumplida: >= 80 %, Ruff 0» | Ninguna | — |
| R-59 | Pitch D4 | PARCIAL | **CUMPLE** | «62+11+4 = 77 declaradas, 73 reproducidas; la carga no cuenta» en slide, notas y guion | Ninguna | — |
| R-60 | D5: capturas + video o demo | PARCIAL | **PARCIAL** | Collage 65 con 5 paneles (HU-04 añadido) pero a ~3 pt (L); duración del video sin medir (`COMPLETAR` en notas y guion) | N-01; PASO 10 | disenador-diapositivas / personas |
| R-61 | D5: HU-01 a HU-03 | CUMPLE | **CUMPLE** | «HU-01 a HU-05 entregadas» | Ninguna | — |
| R-62 | D5: entorno de despliegue | PARCIAL | **PARCIAL** | Texto correcto; fig. 58 a ~6 pt (L, N-02); staging no ejecutado | N-01, N-02; PASOS 8-9 | disenador-diapositivas / personas |
| R-63 | D5: validación con el usuario | MANUAL | **MANUAL** | Texto visible «pendiente de acta (ver anexo)»: el anexo no existe (N-03) | N-03; PASO 5 | disenador-diapositivas / personas |
| R-64 | Pitch D5 (demo) | MANUAL | **MANUAL** | Guion de demo; depende de staging o del video | PASOS 8-10 y 18 | personas |
| R-65 | D6: dashboard integrado | NO CUMPLE | **CUMPLE** | Fig. 62 correcta y legible en la diapositiva | Ninguna | — |
| R-66 | D6: planificado vs completado | NO CUMPLE | **CUMPLE** | Fig. 63 (21 SP, entrega +2 días); notas sin burnup real; reserva: series idénticas | N-09 | disenador-diapositivas |
| R-67 | D6: defectos y cobertura | CUMPLE | **CUMPLE** | «2,0 defectos/KLOC … 99 %» | Ninguna | — |
| R-68 | D6: impacto medido | CUMPLE | **CUMPLE** | «3 -> 1 (sintético)» | Ninguna | — |
| R-69 | Pitch D6 | CUMPLE | **CUMPLE** | Notas; ver N-09 | N-09 | disenador-diapositivas |
| R-70 | D7: flujo de trazabilidad | NO CUMPLE | **PARCIAL** | Fig. 64 sin errores de cifra, pero ~5 pt y layout confuso (L, N-06) | N-01, N-06 | recursos-visuales |
| R-71 | D7: matriz de trazabilidad | PARCIAL | **PARCIAL** | Ni la figura ni el texto muestran la matriz de 8 columnas ni una fila ejemplo | N-06 | recursos-visuales |
| R-72 | D7: conclusiones | CUMPLE | **CUMPLE** | 3 conclusiones visibles | Ninguna | — |
| R-73 | D7: siguiente incremento | PARCIAL | **CUMPLE** | Texto «Siguiente: INC-2 …»; fig. 68 alineada con las Tablas 15-16 (E-08) | Ninguna | — |
| R-74 | Pitch D7 | CUMPLE | **CUMPLE** | Notas y guion 0:35 | Ninguna | — |
| R-75 | 7 diapositivas, alto impacto, sin bloques de texto | PARCIAL | **PARCIAL** | 7 diapositivas y <= 40 palabras (40/29/34/38/38/34/39) OK; figuras ilegibles y áreas vacías | N-01 | disenador-diapositivas |

### E. Repositorio

| ID | Requisito | v1 | v2 | Evidencia | Acción | Responsable |
| --- | --- | --- | --- | --- | --- | --- |
| R-76 | Código fuente | CUMPLE | **CUMPLE** | `pmv_fastapi/app/` | Ninguna | — |
| R-77 | Scripts de BD | CUMPLE | **CUMPLE** | `pmv_fastapi/db/`, `scripts/` | Ninguna | — |
| R-78 | Pruebas automatizadas y CI | PARCIAL | **MANUAL** | Tests (77 declaradas) y `.github/workflows/ci.yml` en `fdc50c5`; sin push no hay ejecución en verde | PASO 3 | personas |
| R-79 | README de despliegue | PARCIAL | **CUMPLE** | README l.38 y l.47 con el CI en la raíz | Ninguna | — |
| R-80 | Tag `v1.0-PMV` | PARCIAL | **MANUAL** | Existe (9ce90c3), no alcanzable desde la rama; documentado en l.678 | PASO 14 | personas |

### F. Rúbrica

| ID | Criterio | v1 | v2 | Evidencia | Acción | Responsable |
| --- | --- | --- | --- | --- | --- | --- |
| R-81 | C1 | PARCIAL | **PARCIAL** | Figs. 1, 5 y 6 corregidas; faltan fecha, docente y códigos (portada) | PASO 1 | personas |
| R-82 | C2 | PARCIAL | **PARCIAL** | Figs. 12-14 correctas; faltan acta, Product Owner y horas | PASOS 4-5 | personas |
| R-83 | C3 | PARCIAL | **PARCIAL** | Figs. 15-25 correctas; Sonar, staging y E2E sin ejecutar; fig. 58 pequeña | PASOS 7-9 y 11; N-02 | personas / recursos-visuales |
| R-84 | C4 | NO CUMPLE | **CUMPLE** | Matriz de 8 columnas y tablero 62/63 correctos | Ninguna | — |
| R-85 | C5 | PARCIAL | **PARCIAL** | Cifras correctas; legibilidad de figuras (N-01) | N-01 | disenador-diapositivas |
| R-86 | C6 | MANUAL | **MANUAL** | Sin staging ni aceptación ni CI en verde | PASOS 3, 5, 8-10 | personas |
| R-87 | C7 | MANUAL | **MANUAL** | Guion listo | PASO 17 | personas |
| R-88 | C8 | MANUAL | **MANUAL** | Preguntas listas | PASO 18 | personas |

### G. Puntaje y exposición

| ID | Requisito | v1 | v2 | Evidencia | Acción | Responsable |
| --- | --- | --- | --- | --- | --- | --- |
| R-89 | 8 + 12 = 20 | CUMPLE | **CUMPLE** | Informativo | Ninguna | — |
| R-90 | Guion de 7 min | CUMPLE | **CUMPLE** | Guion §1: 7:00; sumas verificadas | PASO 17 (ensayo) | personas |
| R-91 | Demo en vivo o video | MANUAL | **MANUAL** | `demo_pmv.mp4` existe; staging no ejecutado | PASOS 8-10 | personas |

## 8. Lo que es MANUAL (15 requisitos), con su paso

| Requisitos | Qué falta | Paso (`PASOS_MANUALES.md`) |
| --- | --- | --- |
| R-08, R-09, R-81 | Códigos, docente, fecha y confirmación del mapeo de roles | 1 y 2 |
| R-20, R-21, R-34, R-63, R-82 | Acta o declaración de aceptación; Product Owner | 5 |
| R-23 (opcional) | Horas reales | 4 |
| R-26, R-37 | Confirmar el motivo del cambio Flask -> FastAPI | 6 |
| R-32 | Activar SonarCloud o declarar que no se usa | 7 |
| R-21, R-78, R-86 | Push y captura de Actions en verde | 3 |
| R-33, R-62, R-64, R-86, R-91 | Levantar el staging y capturar `/api/salud` | 8 y 9 |
| R-34, R-60, R-91 | Duración del video | 10 |
| R-31, R-83 | E2E con Chromium (convierte «según el tag» en «reproducido») | 11 |
| R-80 | Decidir sobre el tag | 14 |
| R-04, R-87, R-88, R-90 | Ensayo de 7 minutos y defensa individual | 17 y 18 |
| R-01 | Reexportar el PDF y el DOCX al cerrar los `[COMPLETAR]` | 13 |

## 9. Estimación de la nota (orientativa; no es la nota oficial)

Rúbrica de la consigna: C1 a C4 valen 2,0 puntos cada uno y C5 a C8 valen 3,0.

| Criterio | Estado actual | Con las correcciones de agentes | Con además los pasos manuales |
| --- | --- | --- | --- |
| C1 (2,0) | 1,75 (contenido completo, figuras correctas, portada con `[COMPLETAR]`) | 1,75 | 2,0 |
| C2 (2,0) | 1,5 a 1,75 (sin acta ni horas) | 1,5 a 1,75 | 1,75 a 2,0 |
| C3 (2,0) | 1,5 a 1,75 (Sonar, staging y E2E sin ejecutar) | 1,75 | 1,75 a 2,0 |
| C4 (2,0) | 1,75 a 2,0 | 2,0 | 2,0 |
| **Informe /8** | **6,5 a 7,25 (central 6,9)** | 7,0 a 7,5 | **7,5 a 8,0 (central 7,7)** |
| C5 (3,0) | 2,25 (7 diapositivas, cifras correctas, figuras ilegibles) | 3,0 | 3,0 |
| C6 (3,0) | 1,5 (capturas y video; sin staging ni aceptación; nivel Básico) | 1,5 | 2,25 a 3,0 (demo en vivo en staging) |
| C7 (3,0) | depende del ensayo (supuesto Bueno: 2,25) | 2,25 | 2,25 a 3,0 |
| C8 (3,0) | depende de cada integrante (supuesto 2,25) | 2,25 | 2,25 a 3,0 |
| **Total /20** | **~15 (14 a 16)** | **~16** | **~18 (17 a 19,5)** |

El informe /8 tal como está: **6,9 (rango 6,5 a 7,25)**. Proyección si se completan los pasos manuales: informe 7,7 y total de unos **18 sobre 20** (el 60 % oral depende de la demo en staging y del ensayo).

## 10. Declaración final

**NO LISTO PARA ENTREGAR.** Bloqueantes:

1. Pasos manuales 1 a 7, 9 y 10 (17 `[COMPLETAR]` visibles también en el PDF y el DOCX).
2. N-01: figuras ilegibles en D1, D3, D4, D5 y D7 y por tanto en el PDF de las diapositivas (corregible por agentes).
3. CI sin ejecución en verde (paso 3), staging sin ejecutar (pasos 8-9), ensayo y defensa (17-18).

Para pasar a LISTO: corregir N-01 a N-06 y N-09 (agentes), cerrar los pasos manuales, reexportar el PDF y el DOCX (N-12) y repetir esta inspección una vez más (S6-06, v3).
