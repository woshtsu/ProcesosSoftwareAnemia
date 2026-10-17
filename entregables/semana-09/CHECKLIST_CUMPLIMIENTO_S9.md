# Checklist de cumplimiento — Semana 9 (evaluación GQM) — estado final tras la segunda pasada

- **Guía:** `guias/S9-PSW-GUÍA DE TRABAJO.md` (7 actividades con sus matrices, estructura III de 8 secciones, rúbrica IV de 5 criterios × 4 puntos) y las 6 aclaraciones del cliente
- **Entregable revisado:** `entregables/semana-09/Entregable_Semana9_Anemia_Junin.md` (1 268 líneas; 40 figuras; 48 tablas; Anexos A a G). Las tablas y figuras se citan con la **numeración nueva**; el Anexo G movió detalle del cuerpo.
- **Evidencias contrastadas (solo lectura):** `entregables/semana-09/evidencias_capturas/`, `entregables/semana-09/metricas/` (datos, salidas, gráficos), `pmv_fastapi/` (v1.5), copia v1.0 en `../inc1_v1.0_PMV` (idéntica al tag salvo fin de línea), tag `v1.0-PMV`, entregables S1, S3-4 y S6 (`temp-s6`), `ArchivosComplementarios/Semana09_S1.pdf`
- **Revisor:** revisor documental y auditor de cumplimiento independiente (no participó en la redacción) · **Primera revisión y segunda pasada:** 16/10/2026
- **Verificaciones del auditor (repetidas en la segunda pasada):** `pytest -q -p no:cacheprovider` en `pmv_fastapi` = **228 passed**; `pytest tests/e2e` = **8 passed**; `ruff check .` = **All checks passed**; `ruff format --check .` = **64 archivos correctos**; script de enlaces y anclas (43 enlaces locales y 43 anclas del índice, **0 rotos**); script de numeración (**48 tablas y 40 figuras consecutivas, todas citadas, 0 referencias a números inexistentes**); encabezados de las 6 matrices de la guía comparados uno a uno (**idénticos**); Tabla 38 igual al contenido real de `evidencias_capturas/`; `git ls-remote --tags origin` (solo `v1.0-PMV`); apertura con Read de 20 PNG y 4 gráficos o diagramas.
- **Resultado (actualizado 17/10/2026):** 69 requisitos (guía + aclaraciones): 67 CUMPLE, 1 CUMPLE PARCIAL, 1 NO CUMPLE. **Cumplimiento estricto ponderado (CUMPLE = 1; PARCIAL = 0,5; NO = 0): 97,8 %** (segunda pasada: 97,1 %; primera revisión: 95,7 %). Solo contra la guía (63 requisitos): **97,6 %**.
- **Hallazgos de la primera revisión (22):** 17 resueltos, 4 parciales, 1 abierto. **Hallazgos nuevos de la segunda pasada:** 4 menores y 4 de estilo. **Ninguno crítico.** De los tres mayores, H-02 y H-03 quedaron resueltos; H-01 depende de publicar en GitHub.

> Convención: CUMPLE = el requisito está presente y verificado; CUMPLE PARCIAL = presente con una carencia concreta; NO CUMPLE = ausente. «Ubicación en guía» es la actividad, matriz o sección de la guía; la «Sección del entregable» es la del informe revisado (numeración nueva).

## Parte A. Checklist ítem por ítem de la guía

### A.1 Actividades 1 a 7 (matrices, preguntas y métricas)

| ID | Requisito de la guía | Ubicación en guía | Sección del entregable | Estado | Evidencia / observación |
| --- | --- | --- | --- | --- | --- |
| A1-01 | 3 objetivos GQM (G-01, G-02, G-03) | Act. 1 | §3.1, Tabla 8 | **CUMPLE** | Los tres goals coinciden con la Matriz 1.1 de la guía. |
| A1-02 | Cada objetivo con la estructura formal de 5 elementos (Objeto, Propósito, Enfoque de Calidad, Punto de Vista, Contexto) | Act. 1; rúbrica 1 | §3.1.1 a 3.1.3 | **CUMPLE** | Redactados con la plantilla de la sesión S9 («Analizar / con el propósito de / con respecto a / desde el punto de vista de / en el contexto de»), verificada contra las láminas 15-16 de `Semana09_S1.pdf`. |
| A1-03 | Matriz 1.1 con las 7 columnas exactas (Código Goal, Dimensión Evaluada, Objeto a Evaluar, Propósito de Medición, Enfoque de Calidad / Atributo, Punto de Vista, Contexto de Aplicación) | Matriz 1.1 | Tabla 8 | **CUMPLE** | Encabezados idénticos; solo se precisan objeto y contexto con las versiones y carpetas reales. |
| A1-04 | G-01 Producto (Arquitectura): estructura de código en GitHub, evaluar desacoplamiento, mantenibilidad, Arquitecto de Software | Matriz 1.1 | Tabla 8, §3.1.1 | **CUMPLE** |  |
| A1-05 | G-02 Producto (Pruebas): Inc. 1 e Inc. 2, estabilidad funcional, cobertura y tasa de fallas, QA/Testers | Matriz 1.1 | Tabla 8, §3.1.2 | **CUMPLE** |  |
| A1-06 | G-03 Proceso y Producto (Valor): proceso y entregables, efectividad, valor e impacto, Usuario Final / Product Owner | Matriz 1.1 | Tabla 8, §3.1.3 | **CUMPLE** | Declara que el punto de vista del PO es simulado y que no hubo piloto. |
| A2-01 | Q1.1 (dominio aislado de frameworks) | Act. 2 | Tabla 9 | **CUMPLE** | Texto literal de la guía + «por qué importa» + métrica que la responde. |
| A2-02 | Q1.2 (puertos y adaptadores en módulos independientes) | Act. 2 | Tabla 9 | **CUMPLE** |  |
| A2-03 | Q2.1 (% de RF con evidencias fotográficas aprobadas) | Act. 2 | Tabla 10 | **CUMPLE** |  |
| A2-04 | Q2.2 (densidad de defectos entre PMV e Inc. 2) | Act. 2 | Tabla 10 | **CUMPLE** | La lectura alternativa 6/7 = 0,86 Def/RF se muestra junto al 0,0 por atribución (Tablas 7, 29 y 36; §5.5). H-02 resuelto. |
| A2-05 | Q3.1 (reducción de brechas AS-IS) | Act. 2 | Tabla 11 | **CUMPLE** |  |
| A2-06 | Q3.2 (tiempos de respuesta, disponibilidad y satisfacción por incremento) | Act. 2 | Tabla 11 | **CUMPLE** | El índice M3.2 incluye solo V1 a V3 y la salvedad figura en Tablas 7 y 12 y §6.4; V4 a V6 se informan aparte (Tabla 31). H-03 resuelto. |
| A2-07 | Árbol de preguntas Goal-Question-Metric visible | Act. 2; sesión S9 | Figura 2 (diagrama 71) | **CUMPLE** | Q1.3 y M1.3 se rotulan como complementarias (línea discontinua). |
| A3-01 | Matriz 3.1 con las 8 columnas exactas (Cód. Goal, Cód. Preg., Cód. Mét., Nombre de la Métrica, Fórmula / Método de Extracción, Fuente de Datos, Valor Meta Inc. 1, Valor Meta Inc. 2) | Matriz 3.1 | Tabla 12 | **CUMPLE** | Encabezados idénticos a la Matriz 3.1. Se agrega una fila (M1.3) rotulada «compl.»: la guía tiene 6 filas y el informe 7. |
| A3-02 | M1.1 Índice de Contaminación del Dominio, metas 0,0 % / 0,0 % | Matriz 3.1 | Tabla 12; §4.3 | **CUMPLE** | Fórmula operacionalizada con AST (`m11_contaminacion.py`); la diferencia con la fórmula de la guía se explica. |
| A3-03 | M1.2 Cohesión de Módulos Hexagonales, metas 100 % / 100 % | Matriz 3.1 | Tabla 12; §4.2 | **CUMPLE** | Se convierte «Conforme / No conforme» en % de 5 componentes (criterio estricto y laxo). |
| A3-04 | M2.1 Cobertura Funcional con Capturas, metas 100 % / 100 % | Matriz 3.1 | Tabla 12; §5.5 | **CUMPLE** | Informa además el 50,0 % sobre el alcance total del Inc. 2. |
| A3-05 | M2.2 Tasa de Defectos Funcionales, metas ≤ 1,0 / ≤ 0,2 Def/RF | Matriz 3.1 | Tabla 12; Tabla 29 | **CUMPLE** | La fuente declarada (registros DEF en lugar de GitHub Issues) está justificada. |
| A3-06 | M3.1 Cobertura de Brechas Resueltas, metas ≥ 60 % / ≥ 90 % | Matriz 3.1 | Tabla 12; Tablas 32-33; Tabla 36 | **CUMPLE** | Se agregó la lectura estricta (solo brechas con puntaje 1,0): 16,7 % en ambas versiones, variación 0,0 % (Tabla 33, fila «Estricta»; Tabla 36, fila «M3.1 estricta»; §6.3). Además se mantienen la lectura principal con crédito parcial, la complementaria y la sensibilidad. H-15 resuelto. |
| A3-07 | M3.2 Índice de Impacto en Valor, metas mejora ≥ 50 % / ≥ 80 % | Matriz 3.1 | Tabla 12; Tabla 48; §6.4 | **CUMPLE** | Definido con V1 a V3; la fórmula de la Tabla 12 y la Tabla 7 advierten que no incluye tiempo de respuesta, disponibilidad ni satisfacción, y que V4 empeora (175 → 610 ms). H-03 resuelto. |
| A3-08 | Fórmula, método de extracción y fuente de datos reales y trazables a un script y a un JSON | Act. 3; aclaración 4 | Tabla 12 | **CUMPLE** | Cada fila cita script y archivo `datos/*.json`; todos existen. |
| A3-09 | Metas no cumplidas analizadas (M1.2 Inc. 1, M2.2 Inc. 1, M3.1 ambos) | Act. 3, 7 | §4.5, §5.5, §6.3 | **CUMPLE** | Cada incumplimiento tiene causa raíz y acción; la propuesta de ajustar M3.1 se rotula «no aprobada». |
| A4-01 | Estructura hexagonal descrita y equivalencia `/src` de la guía con `app/` (Python/FastAPI) | Act. 4 | §4.1, Tabla 13; árboles | **CUMPLE** | Árboles de v1.0 y v1.5 correctos frente al código (verificados con `ls` y `git ls-tree`); versión en texto en el Anexo G.2. |
| A4-02 | Matriz 4.1 con las 4 columnas exactas (Componente Hexagonal, Ruta en Repositorio GitHub, Estado, Evidencia de Desacoplamiento / Hallazgo) | Matriz 4.1 | Tablas 14 y 15 | **CUMPLE** | Una matriz por versión; encabezados idénticos. |
| A4-03 | Fila Núcleo de Dominio | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | 0 importaciones externas (JSON m11 verificado). |
| A4-04 | Fila Puertos de Entrada | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | No Conforme en Inc. 1 (no existen); Conforme en Inc. 2 con archivo y línea. |
| A4-05 | Fila Puertos de Salida | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | Líneas citadas verificadas contra el código. |
| A4-06 | Fila Adaptadores de Entrada | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | `api.py:12` (v1.0) y `api.py:17-21` (v1.5) verificados. |
| A4-07 | Fila Adaptadores de Salida | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | `sqlalchemy_repo.py:149` y `:159` verificados. |
| A4-08 | Reporte de desacoplamiento del dominio (cero contaminación) con evidencia cuantitativa | Act. 4; Sec. III-4 | §4.3, Tablas 16-17 | **CUMPLE** | M1.1 y M1.3 con cifras reproducibles; 14 pruebas de arquitectura vigilan la regla. |
| A4-09 | Auditoría evidenciada en la carpeta y el repositorio GitHub (no solo en el árbol local) | Act. 4; rúbrica 2 | §4.1 «Evidencia en GitHub»; Figuras 3-4; Tabla 15; Anexo B | **CUMPLE** | Actualización 17/10/2026: rama `feature/inc2-agenda-alertas` y tag `v1.5.0-inc2-avance` (commit `416dfbc`) publicados; las Figuras 3 y 4 son capturas de la interfaz de GitHub de `v1.0-PMV/app` y `v1.5.0-inc2-avance/pmv_fastapi/app`. |
| A5-01 | Ficha 5.1 por RF del Incremento 1 (RF-01 a RF-05) | Act. 5; Ficha modelo | Tablas 19-23 | **CUMPLE** | 5 fichas. |
| A5-02 | Ficha 5.1 por RF del Incremento 2 entregado (RF-06 y RF-07) | Act. 5 | Tablas 24-25 | **CUMPLE** | 2 fichas. |
| A5-03 | Campos de la ficha: proyecto, incremento, código RF/HU, nombre, criterio Dado-Cuando-Entonces, ID caso de prueba, tipo, resultado esperado, evidencias, evaluación, fecha, evaluador | Ficha 5.1 | Tablas 19-25 | **CUMPLE** | Todos presentes; se agregan tiempos medidos, resultado observado y rótulos literales de la guía en la primera y la última captura de cada ficha; las pruebas que respaldan cada RF pasaron al Anexo G.6 (Tabla 43). |
| A5-04 | Capturas de entrada y de resultado del software en ejecución por RF (mínimo 2) | Ficha 5.1; rúbrica 3 | Figuras 7-30 | **CUMPLE** | 24 capturas de fichas (RF-01: 2; RF-02: 6; RF-03: 3; RF-04: 3; RF-05: 4; RF-06: 3; RF-07: 3). Abiertas 20 con Read: muestran la PWA real con pie «Evidencia S9» y coinciden con la descripción. |
| A5-05 | Archivo de imagen indicado en cada captura | Ficha 5.1 | Cada «Captura N» | **CUMPLE** | Ruta `evidencias_capturas/RF-0X/...png`; las 43 rutas locales de imágenes y enlaces y las 43 anclas del índice del documento resuelven. |
| A5-06 | Evaluación [APROBADO] | fecha | evaluador (QA Lead) | Ficha 5.1 | Tablas 19-25 | **CUMPLE** | Evaluador nominado con «firma pendiente» y aclaración de que APROBADO es resultado automatizado, no aceptación de usuario. |
| A5-07 | Matriz 5.2 con las 6 columnas exactas (Código RF, Descripción, Incremento, ID Caso Prueba, Archivo de Captura, Estado) | Matriz 5.2 | Tabla 27 | **CUMPLE** | Encabezados idénticos. |
| A5-08 | Matriz 5.2 cubre todos los RF de los Incrementos 1 y 2 | Matriz 5.2; rúbrica 3 | Tabla 27; §5.1.1; Tabla 26 | **CUMPLE** | La Matriz 5.2 cubre los nueve RF: RF-01 a RF-07 aprobados y RF-08 y RF-09 «Planificada, no ejecutada; fuera del avance del 50 %», con ficha planificada (Tabla 26) y casos reservados CP-RF08-01 y CP-RF09-01. No simula evidencia. H-16 resuelto (la captura de RF-08 y RF-09 sigue pendiente; ver E-05). |
| A5-09 | Capturas claras y legibles que permiten verificar la ejecución | Rúbrica 3 | Figuras 7-35 | **CUMPLE** | 1366 px de ancho, texto legible. Observaciones residuales: formato mm/dd en los campos de fecha (declarado en §5.0, nota 1; no regenerado) y capturas JSON y CSV poco informativas (H-08 y H-19, ver Parte E). |
| A5-10 | Q2.1 y Q2.2 respondidas con la métrica | Act. 2 | §5.5 | **CUMPLE** |  |
| A6-01 | Matriz 6.1 con las 5 columnas exactas (Problema Organizacional AS-IS, Brecha Resuelta, Incremento/Funcionalidad, Indicador de Proceso/Producto, Valor Organizacional) | Matriz 6.1 | Tabla 30 | **CUMPLE** | Encabezados idénticos. |
| A6-02 | Trazabilidad por brecha B1 a B6 (resueltas y no resueltas) | Act. 6; rúbrica 4 | Tabla 30, Tabla 32 | **CUMPLE** | 6 filas; B3, B4, B5 se declaran «no resueltas aún». |
| A6-03 | Indicadores cuantitativos de valor con línea base AS-IS y fuente | Act. 6; Q3.2 | Tablas 31, 48; §6.4 | **CUMPLE** | V1 a V6 con fuente en JSON. |
| A6-04 | Q3.1 y Q3.2 respondidas | Act. 2 | §6.7 | **CUMPLE** |  |
| A6-05 | Distinción entre valor medido (datos sintéticos) y valor que exige piloto | Act. 6; aclaración 3 | Tabla 35 | **CUMPLE** | Muy explícito; evita afirmar aceptación del usuario. |
| A7-01 | Matriz 7.1 con las 5 columnas exactas (Métrica GQM Evaluada, Inc. 1 Real, Inc. 2 Real, Variación %, Causa Raíz / Acción de Mejora) | Matriz 7.1 | Tabla 36 | **CUMPLE** | Encabezados idénticos. |
| A7-02 | Filas M1.1, M2.2 y M3.1 de la guía con valor real, variación, causa raíz y acción | Matriz 7.1 | Tabla 36 | **CUMPLE** | Se agregan M1.2, M1.3, M2.1, M3.1 compl., M3.2, V4 y V5. |
| A7-03 | Variaciones porcentuales correctas | Matriz 7.1 | Tabla 36 | **CUMPLE** | Recalculadas: +150,0 %, −100,0 %, +33,3 %, −25,0 %, +73,5 %, +248,6 %. |
| A7-04 | Plan de mejora continua PDCA | Act. 7 | §7.3, Tabla 37 | **CUMPLE** | 9 acciones con Plan, Do, Check, Act, responsable y fecha. La acción 1 pasó a «nueva medición: 26/10/2026 (cierre del Sprint 4)» y es coherente con el Anexo E. H-06 resuelto. |
| A7-05 | Diagnóstico comparativo (evolución del proceso) por pilar | Act. 7; rúbrica 5 | §7.2.1 a 7.2.3, §7.4 | **CUMPLE** |  |

### A.2 Estructura III del entregable (8 secciones) y anexos

| ID | Requisito de la guía | Ubicación en guía | Sección del entregable | Estado | Evidencia / observación |
| --- | --- | --- | --- | --- | --- |
| E-01 | Sección 1. Carátula e integrantes del equipo (Noveno Ciclo) | Sec. III | §1, Tablas 1-3 | **CUMPLE** | Incluye mapa de exposición por pilares (Tabla 3). |
| E-02 | Sección 2. Resumen ejecutivo y objetivos de evaluación GQM | Sec. III | §2, Tablas 4-7 | **CUMPLE** | La conclusión 1 de §2.2 incluye ahora la reserva sobre la evidencia de v1.5 en GitHub y las conclusiones 2 a 4 incluyen las salvedades de M2.2 y M3.2. |
| E-03 | Sección 3. Matriz de objetivos, preguntas y métricas (Actividades 1, 2, 3) | Sec. III | §3, Tablas 8-12 | **CUMPLE** |  |
| E-04 | Sección 4. Auditoría de arquitectura hexagonal en GitHub, con estructura de carpetas y reporte de desacoplamiento | Sec. III | §4.1 a 4.5 | **CUMPLE** |  |
| E-05 | Sección 5. Fichas de pruebas con capturas (registro de pruebas e imágenes para cada RF de Inc. 1 y 2) | Sec. III | §5.1 a 5.5 | **CUMPLE PARCIAL** | Todos los RF entregados tienen ficha, captura y pruebas. RF-08 y RF-09 tienen ficha planificada (Tabla 26) pero ninguna ejecución ni captura, por estar fuera del avance del 50 % pactado. |
| E-06 | Sección 6. Evaluación de entrega de valor al usuario final | Sec. III | §6.1 a 6.7 | **CUMPLE** |  |
| E-07 | Sección 7. Comparativa GQM y plan de mejora continua (Inc. 1 vs. Inc. 2) | Sec. III | §7.1 a 7.4 | **CUMPLE** |  |
| E-08 | Sección 8. Anexos | Sec. III | §8, Anexos A-G | **CUMPLE** | Los dos anexos exigidos más C a F y el Anexo G de detalle. |
| E-09 | Numeración y títulos de las 8 secciones en el orden de la guía | Sec. III | Encabezados `##` | **CUMPLE** | Idénticos a la guía; subtítulos por pilar añadidos. |
| E-10 | Anexo: carpeta `/evidencias_capturas/` organizada por RF | Sec. III-8 | Anexo A, Tabla 38; `evidencias_capturas/` | **CUMPLE** | RF-01 a RF-07 + `arquitectura/`; INDICE.md; la Tabla 38 coincide exactamente con el contenido real (31 PNG, 2 CSV, 5 JSON, script e índice). |
| E-11 | Anexo: enlace al repositorio GitHub con la etiqueta `v1.0-PMV` | Sec. III-8 | Anexo B | **CUMPLE** | Tag verificado en `origin` con `git ls-remote` (`refs/tags/v1.0-PMV`). |
| E-12 | Anexo: enlace al repositorio con la etiqueta `v2.0-Inc2` | Sec. III-8 | Anexo B (etiqueta «reservada») | **NO CUMPLE** | La etiqueta no existe y el informe lo declara como «reservada» y por crear al cerrar el Inc. 2 (Tablas 4 y 6, §4.1, Anexo B con los comandos). Coherente con un Inc. 2 al 50 %, pero la guía la exige; hay que acordarlo con el docente (H-01). |

**Matrices de la guía con columnas exactas (comprobado encabezado por encabezado en la segunda pasada):** Matriz 1.1 = Tabla 8 (7 columnas), Matriz 3.1 = Tabla 12 (8), Matriz 4.1 = Tablas 14 y 15 (4), Matriz 5.2 = Tabla 27 (6), Matriz 6.1 = Tabla 30 (5) y Matriz 7.1 = Tabla 36 (5): **ninguna alterada** tras la edición. Cambia solo el número de filas: la Tabla 12 agrega M1.3 (rotulada complementaria), la Tabla 36 agrega M1.2, M1.3, M2.1, M3.1 complementaria y estricta, M2.2 alternativa, M3.2, V4 y V5, y la Tabla 27 agrega RF-06 a RF-09. Es una ampliación legítima.

**Metas por métrica (Inc. 1 / Inc. 2) frente a lo medido:**

| Métrica | Meta guía Inc. 1 / Inc. 2 | Medido Inc. 1 / Inc. 2 | ¿Cumple Inc. 1 / Inc. 2? | Análisis de la meta no cumplida |
| --- | --- | --- | --- | --- |
| M1.1 | 0,0 % / 0,0 % | 0,0 % / 0,0 % | Sí / Sí | — |
| M1.2 | 100 % / 100 % | 40,0 % / 100,0 % | No / Sí | §4.5 y Tabla 36: faltaban puertos de entrada, el puerto de salida estaba dentro de `application` y el adaptador HTTP importaba una clase concreta; acción ADR-008. |
| M2.1 | 100 % / 100 % | 100,0 % / 100,0 % (50,0 % del alcance total) | Sí / Sí sobre lo entregado | §5.5 y Tabla 36: RF-08 y RF-09 pendientes. |
| M2.2 | ≤ 1,0 / ≤ 0,2 Def/RF | 1,4 / 0,0 (0,86 por hallazgo) | No / Sí por atribución; No por hallazgo (Tabla 7) | §5.5: 6 de 7 defectos escaparon por falta de pruebas de entradas límite; ahora ambas lecturas son visibles. |
| M3.1 | ≥ 60 % / ≥ 90 % | 25,0 % / 33,3 % (estricta 16,7 % / 16,7 %) | No / No | §6.3: la guía supone cierre casi total en dos incrementos y el plan reparte 6 brechas en 6 incrementos; propuesta de metas acumuladas (no aprobada). |
| M3.2 | mejora ≥ 50 % / ≥ 80 % | 57,6 % / 100,0 % (solo V1 a V3) | Sí / Sí | §6.4: el índice no incluye V4 (175 → 610 ms, empeora), V5 ni V6; la salvedad figura en Tablas 7 y 12. |

## Parte B. Verificación de las 6 aclaraciones del cliente

| ID | Aclaración | Dónde se verifica | Estado | Evidencia del auditor |
| --- | --- | --- | --- | --- |
| B-01 | Separación clara de los 3 pilares técnicos (arquitectura hexagonal / pruebas Inc. 1 y 2 / entrega de valor) | Tabla 3; etiquetas «[Pilar N]» en §3.1.x, 3.2.x, 3.3.x, §4, §5, §6, §7.2.x; Tabla 37 con columna Pilar | **CUMPLE** | Cada pilar tiene su goal, preguntas, métricas, sección, diagnóstico y acciones. Los resúmenes de §2 y la Matriz 7.1 son transversales por diseño. Observación: el cuerpo (§1 a §7) sigue siendo largo (≈ 17 200 palabras; H-17), aunque el detalle de apoyo pasó al Anexo G. |
| B-02 | Actividad 5 con capturas REALES del software ejecutado para cada RF | Figuras 7-35; `evidencias_capturas/`; `capturar_evidencias.py` | **CUMPLE** | 20 PNG abiertos (18 de RF-01 a RF-07 y 2 de arquitectura, estos últimos regenerados a las 18:46): muestran la PWA real en Chromium con datos sintéticos; las cifras de la ficha (Hb 11,6, 3 720 m, DNI 72000001, 7 filas LEVE, 15 niños, 13 controles en la agenda, 9 vencidos, 7 ALTA) coinciden con lo que se ve. Excepciones declaradas: la captura JSON es la vista del navegador y la del CSV es una página que renderiza el archivo descargado; los árboles de carpetas son locales. Los 31 PNG listados en la Tabla 38 existen. |
| B-03 | Avance del 50 % del Inc. 2 antes del informe, con trazabilidad a entregables previos | §2.1, Tablas 5-6; Tabla 4 (clase «Heredada») | **CUMPLE** | Verificado en código: `GET /api/ninos/{id}/agenda`, `GET /api/alertas/controles-vencidos` y `GET /api/alertas/resumen` existen (12 rutas frente a 9). Reejecutado en la segunda pasada: `pytest` = 228 passed, E2E = 8 passed, `ruff check` = All checks passed. Trazabilidad a S1 (Tablas A.3-A.4, B1-B6), S3-4 (HIST-2.1 a 2.4, 18 SP, Sprint 3) y S6 (Tablas 4-5, DEF-01/02) verificada. |
| B-04 | Métricas con cálculo REAL, cada valor rastreable a JSON o salida | Tablas 7, 12, 29, 31-34, 36; `metricas/datos/`, `salidas/` | **CUMPLE** | Rastreo en la Parte D: 66 filas de cifras (más de 130 valores individuales) contra su JSON, salida o archivo; 23 filas recalculadas a mano. Sin discrepancias numéricas con las fuentes; la única discrepancia de la segunda pasada es la hora de las capturas de los árboles (N-01). |
| B-05 | El documento se puede exponer dividido en los 3 pilares (mapa y guion) | Tabla 3; Anexo E, Tabla 39 | **CUMPLE** | Mapa con goal, preguntas, métricas, secciones, figuras y mensaje por pilar; las referencias de figuras ahora son concretas (Figuras 7 a 30 y 31; 32 a 34). Guion de ~5 min con figuras y pregunta probable del docente; el sujeto de la primera frase del Anexo E ya es «El equipo». H-04 y H-20 resueltos. |
| B-06 | Uso coherente del material complementario (sesión GQM: plantilla Analizar / con el propósito de / con respecto a / desde el punto de vista de / en el contexto de) | §3.1.1-3.1.3; Figura 2; Anexo F | **CUMPLE** | La plantilla coincide con las láminas 15-16 de `Semana09_S1.pdf`; el formato Goal / Questions / Metrics de la lámina 21 se cubre con el árbol y las Tablas 9-11. El Anexo F ya cita Basili et al. (2010), Sánchez-Seco et al. (2015), Hernández et al. (2015), IEEE SWEBOK (2014), Sommerville y Pressman, tal como figuran en las láminas. H-11 resuelto. |

## Parte C. Autoevaluación con la rúbrica (20 puntos)

| Criterio | Puntaje probable | Justificación | Qué falta para el máximo |
| --- | --- | --- | --- |
| Formulación del Modelo GQM (Act. 1, 2 y 3) | **4 / 4** | Tres goals con los 5 elementos de Basili en la plantilla de la sesión, 6 preguntas literales de la guía (+ Q1.3 complementaria), 6 métricas con fórmula, script, fuente y metas Inc. 1 / Inc. 2, diferenciando producto (G-01, G-02) y proceso/valor (G-03). Las salvedades de M2.2, M3.1 y M3.2 ya aparecen en la Tabla 7 y en la Tabla 12. | Nada obligatorio. |
| Auditoría de Arquitectura Hexagonal en GitHub (Act. 4) | **4 / 4** | Actualización 17/10/2026: con la rama y el tag publicados y las capturas de GitHub (Figuras 3 y 4), la estructura y el aislamiento del dominio se demuestran en el repositorio; Matriz 4.1 por versión con archivo y línea, M1.1 = 0,0 %, M1.3 y 14 pruebas de arquitectura. |
| Pruebas Funcionales con Capturas por RF (Act. 5) | **3 / 4** (4 / 4 si el docente acepta el alcance del 50 % pactado) | 7 fichas completas, 24 capturas de fichas y 5 de regresión, reales, legibles y coherentes; Matriz 5.2 con columnas exactas y los 9 RF; fichas planificadas de RF-08 y RF-09 sin simular evidencia; 228 + 8 pruebas, cobertura 100 %. La rúbrica dice «TODOS los RF de los Incrementos 1 y 2» y RF-08 y RF-09 no tienen ejecución ni captura. | Acordar por escrito el alcance, o completar HIST-2.3 y HIST-2.4 con sus capturas (acción 3 del PDCA); opcional: regenerar capturas con configuración regional es-PE. |
| Evaluación de Entrega de Valor al Usuario (Act. 6) | **4 / 4** | Matriz 6.1 con las 6 brechas, indicadores cuantitativos reales V1 a V6 con línea base, M3.1 con cuatro lecturas (principal, complementaria, sensibilidad y estricta), M3.2 con salvedad explícita y Tabla 35 que separa lo medido de lo que exige piloto; no sobredeclara. | Nada obligatorio. |
| Comparativa GQM y Mejora Continua (Act. 7) | **4 / 4** | Matriz 7.1 con variaciones recalculadas y correctas (+150,0 %, −100,0 %, −38,8 %, +33,3 %, −25,0 %, +73,5 %, +248,6 %), causa raíz y acción por métrica, diagnóstico por pilar, 9 acciones PDCA coherentes con el Anexo E y 5 lecciones. | Nada obligatorio. |

**Total probable: 19 / 20** (actualización del 17/10/2026: el criterio 2 sube a 4/4 con la evidencia en GitHub). El punto restante depende de que el docente acepte el alcance del 50 % del Inc. 2 en el criterio 3 o de completar RF-08 y RF-09.

## Parte D. Auditoría de veracidad: cifras verificadas

Clave: **V** = verificada contra la fuente; **R** = además recalculada a mano por el auditor. Los números de tabla son los de la numeración nueva.

| N.º | Cifra en el informe | Ubicación | Fuente | Valor en la fuente | ¿Coincide? | Tipo |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | M1.1 = 0,0 % (0/8 clases) en v1.0 | Tabla 7, §4.3 | `datos/m11_contaminacion.json` | 0 externas / 8 clases | Sí | V |
| 2 | M1.1 = 0,0 % (0/19 clases) en v1.5 | Tabla 7, §4.3 | ídem | 0 externas / 19 clases | Sí | V |
| 3 | Importaciones del dominio v1.0: 9 (7 estándar, 2 internas) | Tabla 14, 16 | ídem | 9 / 7 / 2 | Sí | V |
| 4 | Importaciones del dominio v1.5: 35 (17 estándar, 18 internas) | Tabla 15, 16 | ídem | 35 / 17 / 18 | Sí | V |
| 5 | Capas v1.0: puertos 2 clases/3 imp; aplicación 2 clases/7 imp | Tabla 16 | ídem | 2/3 (2+1); 2/7 (3+4) | Sí | V |
| 6 | Capas v1.5: puertos de entrada 5/10, de salida 2/5, aplicación 3/30; archivos 12, 6, 3, 4 | Tabla 16 | ídem | 5/10 (7+3); 2/5 (4+1); 3/30 (3+27); 12, 6, 3, 4 archivos | Sí | V |
| 7 | M1.2 = 40,0 % (2/5); laxo 60,0 %; ultra estricto 20,0 % | Tabla 7, §4.2 | `datos/m12_conformidad.json` | 2/5; 60,0; 40,0; 20,0 | Sí | R |
| 8 | M1.2 = 100,0 % (5/5) en v1.5 | Tabla 15 | ídem | 5/5; 100/100/100 | Sí | V |
| 9 | Variación M1.2 = +150,0 % (+60 puntos) | Tabla 36 | `resumen_gqm.json` | (100−40)/40 = 150,0; diferencia 60 | Sí | R |
| 10 | Inestabilidad I por capa v1.0 (0,00; 0,50; 0,67; 1,00; 1,00) | Tabla 17 | `datos/m13_acoplamiento.json` | 0,0; 0,5; 0,67; 1,0; 1,0 | Sí | V |
| 11 | Inestabilidad I por capa v1.5 (0,00; 0,33; 0,33; 1,00; 1,00; 1,00) | Tabla 17 | ídem | 0,0; 0,33; 0,33; 1,0; 1,0; 1,0 (1/3 = 0,33) | Sí | R |
| 12 | Violaciones de la regla de dependencia 1 (`api.py:12`) → 0 | Tabla 17, 36 | ídem; código v1.0 | n_violaciones 1 → 0; línea 12 confirmada en el árbol | Sí | V |
| 13 | Líneas citadas: `casos_uso.py:207`, `puertos.py:13` y `:33`, `memoria.py:9`, `sqlalchemy_repo.py:149` (v1.0) | Tabla 14 | Árbol `../inc1_v1.0_PMV` (idéntico al tag salvo fin de línea CRLF) | Coinciden con `grep -n` | Sí | V |
| 14 | Líneas citadas v1.5: `api.py:17-21`, `memoria.py:11`, `sqlalchemy_repo.py:159`, puertos `:6-13` | Tabla 15 | `pmv_fastapi/app/` | Coinciden con `grep -n` | Sí | V |
| 15 | 14 pruebas de arquitectura | §4.3, Tabla 18 | `pytest --collect-only tests/arquitectura` | 14 recolectadas (7 CP + 7 del verificador) | Sí (redacción confusa, H-14) | V |
| 16 | v1.0: 62 + 11 = 73 pruebas; 1,97 s | Tabla 18, 41 | `salidas/v1.0/pytest_por_carpeta.txt`, `pytest_cov.txt` | 62; 11; «73 passed in 1.97s» | Sí | V |
| 17 | v1.5: 174 + 40 + 14 = 228 pruebas; 5,01 s | Tabla 18, 41 | `salidas/v1.5/*`; reejecución del auditor | 228 passed (5,01 s con cobertura; 2,52 s sin cobertura en la reejecución) | Sí | V |
| 18 | E2E: 4 (9,56 s) y 8 (11,08 s); total 77 y 236 | Tabla 18, 41 | `pytest_e2e.txt`; reejecución del auditor | 4 passed; 8 passed (11,08 s también en la reejecución) | Sí | V |
| 19 | Cobertura v1.0: 99,19 % (641 sentencias, 2 sin cubrir; 98 ramas, 4 parciales) | Tabla 18, 41 | `pytest_cov.txt` | TOTAL 641 / 2 / 98 / 4; 99,19 % | Sí | V |
| 20 | Cobertura v1.5: 100 % (1 046 sentencias, 158 ramas) | Tabla 18, 41 | ídem | 1046 / 0 / 158 / 0; 100,00 % | Sí | V |
| 21 | ruff: 0 hallazgos; 33 y 64 archivos con formato | Tabla 18, 41 | `ruff_check.txt`, `ruff_format.txt`; reejecución del auditor | All checks passed; 33 y 64 archivos | Sí | V |
| 22 | Criterios Dado-Cuando-Entonces 17/17 (5 RF) y 33/33 (7 RF) | Tablas 41, 31 | `datos/m21_cobertura_rf.json` | 17/17; 33/33; por RF 4,4,4,2,3 y 5,4,5,4,4,6,5 | Sí | R |
| 23 | Pruebas por RF (RF-01: 10 y 13; RF-02: 7 y 7; RF-03: 11 y 14; RF-04: 3 y 6; RF-05: 6 y 8; RF-06: 23; RF-07: 17) con su desglose unit/integración/E2E | Tablas 19-25 | ídem | Coinciden en las 7 fichas | Sí | V |
| 24 | Exploratorias: 45 casos, 43 OK, 2 OBS, 0 FALLA; 39 sobre código nuevo (37 OK, 2 OBS) y 6 heredado | Tabla 41, §5.4 | `datos/exploratorias_inc2.json`, `exploratorias_inc2_resultado.txt` | 43 OK / 2 OBS; áreas suman 45 (9, 8, 6, 6, 4, 3, 3, 3, 1, 1, 1) | Sí | V |
| 25 | M2.2 = 1,4 Def/RF (7/5) en Inc. 1; 0,0 (0/2) en Inc. 2 | Tabla 7, 29 | `datos/m22_defectos.json` | 7/5 = 1,4; 0/2 | Sí | R |
| 26 | Variantes de M2.2: 0,2 (1/5); 1,2 (6/5); 1,6 (8/5) | Tabla 29 | ídem | 0,2; 1,2; 1,6 | Sí | R |
| 27 | Densidad por KLOC: 6,85; 0,98; 7,83; KLOC 1,022 y 1,688; neto 0,666 | Tabla 29 | ídem | 7/1,022 = 6,85; 1/1,022 = 0,98; 8/1,022 = 7,83; 1,688−1,022 = 0,666 | Sí | R |
| 28 | 6/7 = 0,86 Def/RF (cálculo propio) | §5.5 | Cálculo del auditor | 6/7 = 0,857 | Sí | R |
| 29 | M2.1 = 100 % (5/5); 100 % (2/2); 50,0 % (2/4); 77,8 % (7/9) | Tabla 7, §5.5 | `resumen_gqm.json`; cálculo | 5/5; 2/2; 2/4; 7/9 = 77,8 | Sí | R |
| 30 | M3.1 = 25,0 % (1,5/6) y 33,3 % (2,0/6); suma de puntos 1,5 y 2,0 | Tablas 32-33 | `datos/m31_brechas.json` | 25,0; 33,3333; 1,5; 2,0 | Sí | R |
| 31 | M3.1 complementaria 100,0 % (1,0/1) y 75,0 % (1,5/2); sensibilidad B6=0: 16,7 % y 25,0 % | Tabla 33 | ídem | 100; 75; 16,7; 25,0 | Sí | R |
| 32 | Metas acumuladas propuestas 16,7; 33,3; 50,0; 66,7; 83,3; 100 % | §6.3 | Cálculo (n/6) | 1/6 … 6/6 | Sí | R |
| 33 | M3.2 = 57,6 % (57,6389) y 100,0 %; +42,36 puntos; +73,5 % | Tablas 7, 36; §6.4 | `datos/m32_indice_valor.json` | (100+0+72,9167)/3 = 57,639; (100−57,639)/57,639 = 73,49 % | Sí | R |
| 34 | V1: 3 → 1 registros; 150→151 niños y 826→827 evaluaciones | Tabla 30, 31 | `datos/m32_v1.5_B150.json` | filas_bd 150/826 → 151/827 | Sí | V |
| 35 | V2: 0 % (0/140; 404 en 140/140) y 100 % (140/140; 135/140 = 96,4 %) | Tabla 31 | `m32_v1.0_B150.json`, `m32_v1.5_B150.json` | 0/140 con 404; 140/140; 135 → 96,4 | Sí | R |
| 36 | V3 v1.0: F1 72,9 %, precisión 70,7 %, sensibilidad 75,3 %; TP 70, FP 29, FN 23, TN 18 | Tabla 31 | `m32_v1.0_B150.json` | 70/29/23/18; P = 70/99; S = 70/93; F1 = 0,7292 | Sí | R |
| 37 | V3 v1.5: F1 100 %; TP 93, FP 0, FN 0, TN 47; 476/476 controles | Tabla 31; Tabla 30 | `m32_v1.5_B150.json` | 93/0/0/47; 476 coinciden | Sí | V |
| 38 | Resumen de alertas B150: 476 vencidos, 450 ALTA, 17 MEDIA, 9 BAJA, 93 niños, 10 próximos en 7 días | Tabla 30 | ídem | 450+17+9 = 476; 93; 10 | Sí | R |
| 39 | p95 por endpoint de la Tabla 34 (24 celdas) | Tabla 34 | `datos/m32_carga.json` (promedios de 2 corridas) | Las 24 coinciden (p. ej. 270; 59,5; 31; 120; 175 / 745; 320; 71,5; 830; 680 / 925; 460; 80,5; 1 095; 875; 520; 780; 1 015) | Sí | V |
| 40 | p95 agregado 175 (190 y 160), 610 (660 y 560), 750 (760 y 740) | Tabla 31, 34 | ídem | 175; 610; 750 con las corridas indicadas | Sí | V |
| 41 | Mediana / p99 agregados 21/345, 74,5/1 100, 105,5/1 300; rps 38,88 / 35,23 / 33,9 | Tabla 34 | ídem | Coinciden; (33,6+34,2)/2 = 33,9 | Sí | R |
| 42 | Variación del p95 = +248,6 % (+435 ms) | Tabla 36 | `m32_carga.json` | (610−175)/175 = 248,57 | Sí | R |
| 43 | Disponibilidad 728/728 y 856/856; 128 sondas por escenario; 600 sin carga; latencias 2,0-2,3 y 7,5-10,8 ms | Tabla 31; §6.4 | `datos/m32_disponibilidad.json` | 128+600 = 728; 128+128+600 = 856; medianas 2,0/2,3 y 7,5/10,7/10,8/10,2 | Sí | R |
| 44 | p95 de alertas con 1 usuario 68,4 ms; 185 ms con 1 000 niños (ADR-007) | §4.4 | `m32_v1.5_B150.json` (V6); `ADR-007` | 68,4; 185 ms | Sí | V |
| 45 | Defectos DEF-01 a DEF-08: tipo, RF, momento; regresión CP-83 a CP-88, CP-102 a CP-106, CP-115 | Tabla 28, §5.5 | `registro_defectos*.md`, `m22_defectos.json` | Coinciden (los CP existen en `tests/`: máximo CP-115) | Sí | V |
| 46 | Inc. 2 agregó 21 archivos (18 → 39) y 11 clases (8 → 19) | §7.2.1 | `m22_defectos.json` (kloc.archivos), `m11` | 39−18 = 21; 19−8 = 11 | Sí | R |
| 47 | API: 12 rutas frente a 9; 3 endpoints nuevos | §2.1 | `m31_brechas.json` (hechos), `api.py` | 12 y 9; agenda, controles-vencidos, resumen | Sí | V |
| 48 | Avance 2/4 historias (50,0 %) y 10/18 SP (55,6 %) | Tabla 5 | S3-4 (Tabla 19); cálculo | 10/18 = 55,56 | Sí | R |
| 49 | 31 PNG: 24 de fichas, 5 de regresión y 2 de arquitectura; 2 CSV | Tabla 38, Anexo A | `find evidencias_capturas` | 24 + 5 + 2 = 31 PNG y 2 CSV; Tabla 38 idéntica al contenido real | Sí | V |
| 50 | Conjunto semilla de 14 niños (v1.0) y 27 (v1.5); 15 y 28 tras registrar a 72000001 | §5.0, Anexo G.1 | `scripts/cargar_datos_prueba.py`; capturas | Semilla de 14 (71000001-14) y 27; 15 y 28 solo tras RF-01. Coincide con lo que dicen ahora §5.0 y G.1 | Sí (H-05 resuelto) | V |
| 51 | Capturas de v1.5 del 16/10/2026 14:16-14:17; pruebas y métricas del código final | Tabla 4, §5.0 nota 2, §5.3, Anexo G.1 | mtime de los PNG; mtime de `sqlalchemy_repo.py` | Capturas 14:16-14:17; corrección de DEF-08 a las 18:02; pruebas 18:09-18:10 | Sí (H-09 resuelto) | V |
| 52 | Tag `v1.0-PMV` existente; `app/` en la raíz del tag | Tabla 1, Anexo B | `git ls-remote --tags origin`; `git ls-tree v1.0-PMV` | `refs/tags/v1.0-PMV` (reverificado en la segunda pasada); `app` en la raíz | Sí | V |
| 53 | v1.5 sin commit ni tag; rama y tag no existen | Tabla 1, Anexo B | `git status`, `git tag`, `git branch -a` | Cambios sin commit; solo existe `v1.0-PMV` | Sí | V |
| 54 | Trazabilidad: S3-4 Tablas 11, 19, 23; Sprint 3 29/09-12/10; Sprint 4 13-26/10; Sprint 5 27/10-09/11 | Tablas 5-6 | `Entregable_Semana3y4...md` | Tabla 11 = WBS con HIST-2.1 a 2.4; Tabla 19 = 18 SP; Tabla 23 = calendario | Sí | V |
| 55 | Trazabilidad: S6 Tabla 4 (B1-B6), Tabla 5 (intervención), Tabla 23 (pirámide), 77 pruebas del PMV, DEF-01 y DEF-02 | Tablas 4, 30 | `git show temp-s6:...Informe_Integrador...md` | Coinciden (77 = 62+11+4; Tabla 23 pirámide; DEF-01 N+1 2 200 → 74 ms) | Sí | V |
| 56 | Reglas de agenda (6, 9, 12, 15, 18, 21, 24, 30, 36, 39, 48, 51 meses; ventana −15/+30; 7 días; prioridades) | Tabla 42 (Anexo G.5) | `ADR-007`, `CHANGELOG.md` | Coinciden | Sí | V |
| 57 | Instrumento SUS: etiqueta en su archivo y remisión | §6.5, Anexo D | `metricas/instrumento_SUS.md` | Línea 3: «Indicador V7, complemento de V6»; ya no remite a `RESULTADOS_GQM.md`. El informe usa «V6 (proxy)» | Sí (matiz N-06) | V |
| 58 | M2.2 alternativa: 6/7 = 0,86 Def/RF; variación 1,4 → 0,86 = −38,8 % (−0,54) | Tablas 7, 29, 36; §5.5 | Cálculo del auditor; `m22_defectos.json` (6 hallados en el ciclo del Inc. 2) | 6/7 = 0,857; (0,857−1,4)/1,4 = −38,78 %; −0,543 | Sí | R |
| 59 | M3.1 estricta (solo puntaje 1,0): 16,7 % (1/6) en ambas versiones; variación 0,0 % | Tabla 33, Tabla 36, §6.3 | `datos/m31_brechas.json` (puntajes B1..B6) | Solo B1 = 1,0 en v1.0 y en v1.5; 1/6 = 16,67 % | Sí | R |
| 60 | Figuras clave por pilar: 7 a 30 (capturas), 31 (defectos), 32 a 34 (valor) | Tabla 3, Anexo E | Pies de figura del documento | Fig. 7-30 = capturas RF-01 a RF-07; Fig. 31 = g6; Fig. 32 = g5; Fig. 33 = g4; Fig. 34 = g3 | Sí | V |
| 61 | Numeración: 48 tablas y 40 figuras sin saltos; toda tabla y figura citada en el texto | Todo el documento | Script del auditor (títulos `**Tabla N.**` y `![Figura N.`) | 1..48 y 1..40 consecutivas; 0 sin citar; 0 referencias a número inexistente | Sí | V |
| 62 | Enlaces locales (43) y anclas del índice (43) | Índice, Anexos A y G, Figuras | Script del auditor (existencia de archivo y de encabezado) | 0 rotos; 0 anclas sin encabezado | Sí | V |
| 63 | Pie de las capturas de los árboles: sin ruta del contenedor; hora de generación | §4.1 «Limitación de la evidencia» | `arquitectura/arbol_v1.0.png` (abierto), `resultados_arquitectura.json`, `INDICE.md` | Pie con ruta relativa `app/ (tag v1.0-PMV)`; generadas a las 18:46:42 y 18:46:43; el informe dice «14:17» | No (N-01) | V |
| 64 | Reejecución del auditor en la segunda pasada: 228 + 8 pruebas, ruff limpio | §5.0, Tabla 18 | `pytest`, `pytest tests/e2e`, `ruff check` en `pmv_fastapi/` | 228 passed (2,60 s sin cobertura); 8 passed (11,42 s); All checks passed | Sí | V |
| 65 | CHANGELOG de v1.5 incluye DEF-08 | Tabla 28 (DEF-08) | `pmv_fastapi/CHANGELOG.md`, líneas 24-29 | DEF-03 a DEF-08 listados | Sí (H-18 resuelto) | V |
| 66 | Ruta `GQM_RAIZ_V10=../inc1_v1.0_PMV` tras `cd herramientas/gqm` | Anexo C | `herramientas/gqm/comun.py` línea 22 (prueba con la variable) | La ruta relativa se resuelve desde el directorio actual: `herramientas/inc1_v1.0_PMV` (no existe) | No (N-02) | V |

**Resumen:** 66 filas auditadas (23 recalculadas a mano); 64 coinciden (algunas con un matiz anotado) y 2 no coinciden: la hora de generación de las capturas de los árboles (N-01) y la ruta relativa de `GQM_RAIZ_V10` en el Anexo C (N-02). **Ninguna cifra de métrica (M1.1 a M3.2, V1 a V6, pruebas, cobertura, p95, disponibilidad, defectos) difiere de su JSON o salida.** La discrepancia de la primera revisión sobre «15 y 27 niños» quedó corregida. Afirmaciones que podrían leerse como aceptación real del usuario: ninguna; el informe rotula «simulado», «sintético», «sin piloto» y «firma pendiente» donde corresponde.

## Parte E. Hallazgos por severidad

### E.1 Seguimiento de los 22 hallazgos de la primera revisión

| N.º | Severidad original | Resumen | Estado | Verificación en la segunda pasada | Pendiente |
| --- | --- | --- | --- | --- | --- |
| **H-01** | MAYOR | Evidencia de GitHub de v1.5 (rama, tag, capturas) y `v2.0-Inc2` | **PARCIAL** | Documentado en §1 (Tabla 1), §2.2 (conclusión 1 con reserva), §4.1, Tabla 15 («por publicar»), Tabla 4 (clase Pendiente), Tabla 6 y Anexo B (comandos y lista previa a la exposición). Se regeneraron los árboles con ruta relativa y se retiró «copia intacta» (ahora «contenido idéntico al tag»). `git tag` y `git ls-remote`: solo existe `v1.0-PMV`. | Publicar rama y tag, capturar GitHub, acordar el uso de `v1.5.0-inc2-avance` mientras `v2.0-Inc2` no exista (depende del equipo; ver Pendientes). |
| **H-02** | MAYOR | M2.2 del Inc. 2 solo por atribución | **RESUELTO** | Tabla 7 («0,0 (0/2) con atribución…; 0,86 (6/7) si se cuentan los hallados en el ciclo»; ¿Cumple? «Sí por atribución; No por hallazgo»), Tabla 29 (fila «Lectura alternativa»), Tabla 36 (fila alternativa, −38,8 %), §2.2 y §5.5, Anexo E. | — |
| **H-03** | MAYOR | Índice M3.2 sin V4 a V6 aunque Q3.2 los nombra | **RESUELTO** | Tabla 7 («solo V1 a V3» y fila V4 fuera del índice), Tabla 12 (salvedad en la fórmula), §2.2 conclusión 3 y 4, §3.3.3, §6.4 («Advertencia»), Tabla 48 («¿Entra al índice?»). | — |
| **H-04** | MENOR | «El docente expondrá el informe…» | **RESUELTO** | Anexo E: «El equipo expondrá el informe en tres bloques de unos 5 minutos (15 minutos en total)». | — |
| **H-05** | MENOR | 15 y 27 niños como conjunto semilla | **RESUELTO** | §5.0 y G.1: semilla de 14 y 27; 15 y 28 tras registrar a 72000001. Coincide con `cargar_datos_prueba.py`. | — |
| **H-06** | MENOR | Fecha de la acción 1 del PDCA frente al Anexo E | **RESUELTO** | Tabla 37 acción 1: perfilado 21/10 y nueva medición 26/10 (cierre del Sprint 4); Anexo E: «nueva medición el 26/10, al cierre del INC-2». | — |
| **H-07** | MENOR | Causa del retraso sin respaldo | **RESUELTO** | Tabla 6: columna «Causa declarada por el equipo (sin registro de horas del Sprint 3)», verbo «habría consumido»; lección 4 con la misma cautela. | — |
| **H-08** | MENOR | Campos de fecha en mm/dd/aaaa en las capturas | **PARCIAL** | §5.0, nota 1: se declara el formato y su causa. Las capturas no se regeneraron (aceptado por el orquestador). | Opcional: fijar `locale="es-PE"` y regenerar (ver Pendientes). |
| **H-09** | MENOR | «Se repitió» y hora de las capturas de v1.5 | **RESUELTO** | §5.0 nota 2 (capturas 14:16-14:17, antes de DEF-08 a las 18:02); §5.3 y G.1: «se ejecutó también». | — |
| **H-10** | MENOR | Figuras y tablas sin referencia en el texto | **RESUELTO** | Script: las 48 tablas y las 40 figuras se citan en el texto; cada captura lleva «(Figura N)» y cada ficha abre con «La Tabla N y las Figuras…». | — |
| **H-11** | MENOR | Anexo F con notas pendientes y fuentes de las láminas ausentes | **RESUELTO** | Anexo F sin notas «Verificar»; incluye Basili et al. (2010), Sánchez-Seco et al. (2015), Hernández et al. (2015), IEEE (2014) SWEBOK, Sommerville y Pressman (7.ª ed.), todas presentes en `Semana09_S1.pdf`. | — |
| **H-12** | MENOR | `instrumento_SUS.md` con «V7» y `RESULTADOS_GQM.md` inexistente | **RESUELTO** | Línea 3: «Indicador V7, complemento de V6»; ya no remite al archivo inexistente; §6.5 ya no menciona V7. Queda un matiz de rótulo (N-06). | Ver N-06. |
| **H-13** | MENOR | Rutas absolutas y v1.0 fuera del repositorio | **PARCIAL** | Anexo C usa `python`, `git worktree add ../inc1_v1.0_PMV v1.0-PMV` y `GQM_RAIZ_V10`; `comun.py` y `ejecutar_pruebas.sh` con valor por omisión relativo. Pero la variable relativa se resuelve desde `herramientas/gqm` (comprobado). | Corregir la línea del Anexo C (N-02). |
| **H-14** | MENOR | «14 pruebas» y «ultra estricto» | **RESUELTO** | §4.3: «14 casos: siete pruebas CP-37 a CP-43 y siete casos de dos pruebas del verificador, seis de ellos parametrizados»; §4.2 define el criterio ultra estricto (20,0 %). | — |
| **H-15** | MENOR | Lectura literal de M3.1 sin mostrar | **RESUELTO** | Tabla 33 (fila «Estricta»), Tabla 36 (fila «M3.1 estricta»), nota d) de la Tabla 12 y §6.3. | — |
| **H-16** | MENOR | RF-08 y RF-09 sin ficha | **RESUELTO** | §5.1.1 y Tabla 26 (fichas planificadas, «PLANIFICADA — NO EJECUTADA», CP-RF08-01 y CP-RF09-01 reservados), Tabla 27 con las 9 filas. | Las capturas de RF-08 y RF-09 requieren HIST-2.3 y 2.4 (acción 3 del PDCA). |
| **H-17** | MENOR | Longitud y repetición | **PARCIAL** | Se creó el Anexo G (4 441 palabras) y se acortaron las fichas; «de 175 a 610» ya no se repite 7 veces. Pero el documento creció a ≈ 21 650 palabras (cuerpo §1-§7 ≈ 17 200) frente a ≈ 19 800. | Opcional: ver N-08 para reducir el cuerpo. |
| **H-18** | MENOR | CHANGELOG sin DEF-08 | **RESUELTO** | `pmv_fastapi/CHANGELOG.md` línea 29: «DEF-08: dos registros simultáneos con el mismo DNI devolvían 500 (ahora 409)». | — |
| **H-19** | ESTILO | Capturas RF-05 JSON/CSV y altas poco informativas | **ABIERTO** | La Figura 24 declara «renderizado en una página simple»; no se regeneraron (aceptado). | Opcional (ver Pendientes). |
| **H-20** | ESTILO | «Figuras clave» vago en la Tabla 3 | **RESUELTO** | Tabla 3: «Figuras 7 a 30 (capturas por RF) y Figura 31 (defectos)»; «32, 33, 34»; «6, 5, 4». | — |
| **H-21** | ESTILO | Índice sin enlaces y celdas largas | **RESUELTO** | Índice con enlaces: las 43 anclas resuelven. La fórmula de M3.2 en la Tabla 12 sigue siendo larga pero legible. | — |
| **H-22** | ESTILO | Rótulos de captura distintos de la guía | **RESUELTO** | La primera y la última captura de cada ficha usan «CAPTURA DE PANTALLA 1: DATOS DE ENTRADA» y «CAPTURA DE PANTALLA N: CONFIRMACIÓN Y RESULTADO»; las intermedias usan rótulos cortos (la guía no las define). | — |

### E.2 Hallazgos abiertos y nuevos (con corrección exacta)

No hay hallazgos **CRÍTICOS**. Orden: mayor, menor, estilo.

**MAYOR (1, aún abierto en parte)**

| N.º | Ubicación exacta | Problema | Corrección |
| --- | --- | --- | --- |
| **H-01 (parcial)** | §4.1; Tabla 15 (columna «Ruta en Repositorio GitHub»); Anexo B | Falta el hecho: v1.5 no tiene commit, rama ni tag ni captura de la interfaz de GitHub; `v2.0-Inc2` no existe. El texto ya lo declara con honestidad (§1, §2.2, §4.1, Tabla 15, Anexo B). | Ejecutar la lista del Anexo B; después cambiar «por publicar» por «publicada» en la Tabla 1 (fila «Versiones del software evaluadas»), la Tabla 15 y §4.1, agregar las capturas de GitHub como Figuras 3b y 4b y actualizar el Anexo A. Si el tag no existirá antes de la exposición, el texto actual ya es suficiente. |

**MENOR**

| N.º | Ubicación exacta | Problema | Texto actual → texto propuesto |
| --- | --- | --- | --- |
| **N-01** | §4.1, párrafo «Limitación de la evidencia», frase «generadas el 16/10/2026 14:17» | Los árboles se regeneraron: el pie de `arbol_v1.0.png` y `resultados_arquitectura.json` e `INDICE.md` dan 18:46:42 y 18:46:43. La hora del informe quedó obsoleta (14:17 es la de las capturas de RF de v1.5). | **Actual:** `generadas el 16/10/2026 14:17.` → **Nuevo:** `generadas el 16/10/2026 18:46.` |
| **N-02** | Anexo C, primer bloque `bash`: línea `export PY=python GQM_RAIZ_V10=../inc1_v1.0_PMV` seguida de `cd herramientas/gqm` | La ruta relativa de la variable se resuelve desde el directorio donde se ejecuta cada script: tras `cd herramientas/gqm` apunta a `herramientas/inc1_v1.0_PMV`, que no existe (comprobado con `comun.py`). Con esa línea los scripts de v1.0 fallan; sin ella funcionan, porque el valor por omisión ya es `../inc1_v1.0_PMV` respecto de la raíz del repositorio. | **Actual:** `export PY=python GQM_RAIZ_V10=../inc1_v1.0_PMV   # ruta de v1.0; por defecto ../inc1_v1.0_PMV` → **Nuevo:** `export PY=python   # v1.0 se busca por omisión en ../inc1_v1.0_PMV (junto al repositorio); para otra ruta use GQM_RAIZ_V10="$(pwd)/ruta" (ruta absoluta)` |
| **N-03** | §5.4, última frase: «Registro completo: Anexo G.3; exploratorias y corridas: Anexo G.4 (Tabla 41).» | La Tabla 41 está en el Anexo G.3 (registro de ejecución), no en G.4 (que no tiene tabla); la referencia a número de tabla queda en el lugar equivocado. | **Actual:** `Registro completo: Anexo G.3; exploratorias y corridas: Anexo G.4 (Tabla 41).` → **Nuevo:** `Registro completo: Anexo G.3 (Tabla 41); exploratorias y corridas: Anexo G.4.` |
| **N-04** | Anexo B, bloque PowerShell: `git add pmv_fastapi herramientas/gqm entregables/semana-09 diagramas`; y §3.1 y Anexo F, que citan `ArchivosComplementarios/Semana09_S1.pdf` | `ArchivosComplementarios/` está sin versionar (`git status`: `??`) y no entra en el `git add`: tras publicar, el enlace a las láminas de la sesión no abre en GitHub, pese a que el informe lo cita como respaldo de la plantilla GQM. | **Actual:** `git add pmv_fastapi herramientas/gqm entregables/semana-09 diagramas` → **Nuevo:** `git add pmv_fastapi herramientas/gqm entregables/semana-09 diagramas ArchivosComplementarios/Semana09_S1.pdf   (o, si el equipo no desea versionar material del curso, añadir en el Anexo F «(material de la sesión; no incluido en el repositorio)»)` |
| **H-13 (parcial)** | Anexo C | Ver N-02. | Ver N-02. |
| **H-08 (parcial)** | §5.0 nota 1; Figuras 7, 8, 21, 22, 25 y 28 a 30 (campos de fecha) | Las capturas conservan el formato mm/dd/aaaa; está declarado, pero no corregido. | Opcional: en `capturar_evidencias.py` fijar `locale="es-PE"` y `timezone_id="America/Lima"` en el contexto de Playwright, regenerar y actualizar las horas de §5.0, §5.3, Anexo G.1 e `INDICE.md`. |
| **H-17 (parcial)** | Documento completo | Ver N-08. | Ver N-08. |

**ESTILO**

| N.º | Ubicación exacta | Problema | Texto actual → texto propuesto |
| --- | --- | --- | --- |
| **N-05** | §6.1, primer párrafo: «las de S1 y S6 (Tabla 4) y … matriz de intervención de S6 (Tabla 5)» | Los números de tabla son los del informe integrador de S6, pero en este informe la Tabla 4 y la Tabla 5 existen (clases de evidencia y avance del Inc. 2); riesgo de confusión. | **Actual:** `son las de S1 y S6 (Tabla 4) y la intervención prevista por incremento es la matriz de intervención de S6 (Tabla 5)` → **Nuevo:** `son las de S1 y S6 (Tabla 4 del informe integrador de S6) y la intervención prevista por incremento es la matriz de intervención de S6 (Tabla 5 del informe integrador de S6)` |
| **N-06** | `entregables/semana-09/metricas/instrumento_SUS.md`, línea 3: «Indicador V7, complemento de V6» | El informe no define «V7» (V6 es el proxy y el SUS está «pendiente»); el rótulo sigue sin coincidir con el informe, aunque ya no se contradice. | **Actual:** `**Indicador V7, complemento de V6 (M3.2, G-03 / Q3.2).**` → **Nuevo:** `**Indicador complementario de V6 (satisfacción real; M3.2, G-03 / Q3.2).**` |
| **N-07** | Anexo G, párrafo introductorio: «…(G.6) la definición operacional de las métricas (G.7) los ADR del Incremento 2 (G.8)…»; y G.4, primera línea con un espacio inicial | Faltan comas en la enumeración; el espacio inicial de G.4 rompe la sangría. | **Actual:** `(G.6) la definición operacional de las métricas (G.7) los ADR` → **Nuevo:** `(G.6), la definición operacional de las métricas (G.7), los ADR` |
| **N-08** | Documento completo (≈ 21 650 palabras; cuerpo §1-§7 ≈ 17 200) | La reorganización con el Anexo G no redujo el total (creció por las fichas planificadas, las notas y las salvedades). Para una exposición de 15 minutos sigue siendo extenso; es una cuestión de lectura, no de cumplimiento. | **Actual:** `—` → **Nuevo:** `Opcional: mover a anexos las Tablas 16 y 17 y el párrafo de exploratorias de §5.4; dejar en §4.3 solo las conclusiones y la Figura 6.` |
| **H-19 (abierto)** | Figuras 23 y 24 (RF-05, JSON y CSV) | Siguen siendo capturas poco informativas (una línea de JSON; CSV renderizado en HTML); declarado en la descripción de la Figura 24. | Opcional: activar «Pretty-print» y recortar la captura JSON; abrir el CSV en una hoja de cálculo; regenerar con el mismo script que H-08. |

## Parte F. Porcentaje global de cumplimiento estricto

| Bloque | Requisitos | CUMPLE | PARCIAL | NO CUMPLE | Cumplimiento ponderado |
| --- | --- | --- | --- | --- | --- |
| A.1 Actividades 1 a 7 | 51 | 51 | 0 | 0 | 100,0 % |
| A.2 Estructura III y anexos | 12 | 10 | 1 | 1 | 87,5 % |
| **Subtotal guía (A.1 + A.2)** | **63** | **61** | **1** | **1** | **97,6 %** |
| B. Aclaraciones del cliente | 6 | 6 | 0 | 0 | 100,0 % |
| **Total (guía + aclaraciones)** | **69** | **67** | **1** | **1** | **97,8 %** |

**Cumplimiento estricto global: 97,8 %** (actualización del 17/10/2026, tras publicar la rama y el tag y añadir las capturas de GitHub; segunda pasada: 97,1 %; primera revisión: 95,7 %). Los dos ítems que no están en CUMPLE son E-05 (RF-08 y RF-09 sin captura, fuera del avance del 50 %) y E-12 (la etiqueta `v2.0-Inc2` se crea al cierre del Inc. 2). Al cerrar el Incremento 2 ambos pasan a CUMPLE.

## Pendientes del equipo antes de la exposición

Acciones que no se pudieron hacer desde el contenedor (sin acceso a GitHub ni permiso para commits o etiquetas) o que dependen de personas.

| N.º | Pendiente | Responsable propuesto (informe) | Fecha del informe | Hallazgo o ítem que cierra |
| --- | --- | --- | --- | --- |
| 1 | ~~Revisar `git status` y publicar la rama `feature/inc2-agenda-alertas` y el tag `v1.5.0-inc2-avance` con los comandos del Anexo B (decidir antes si `ArchivosComplementarios/Semana09_S1.pdf` se versiona; N-04).~~ **Hecho el 17/10/2026** (commit `416dfbc`) | Porras V. y Auqui H. | 19/10/2026 (acción 8) | H-01, A4-09, N-04 |
| 2 | ~~Abrir en GitHub el árbol `app/` del tag `v1.0-PMV` y `pmv_fastapi/app/` del tag `v1.5.0-inc2-avance`; capturar ambas vistas con la URL visible; guardarlas en `evidencias_capturas/arquitectura/`; agregarlas como Figuras 3b y 4b; cambiar «por publicar» por «publicada» en las Tablas 1 y 15 y en §4.1; comprobar que los enlaces abren.~~ **Hecho el 17/10/2026** (Figuras 3 y 4) | Porras V. y Auqui H. | 19/10/2026 | H-01, A4-09 |
| 3 | Acordar con el docente: (a) que `v1.5.0-inc2-avance` identifica el avance mientras `v2.0-Inc2` no exista; (b) que el alcance del Inc. 2 evaluado es el 50 % (RF-06 y RF-07); (c) las metas acumuladas de M3.1 (acción 7). | Porras V. | 19/10/2026 | E-12, criterio 3 de la rúbrica, A3-06 |
| 4 | Firmar las 7 fichas ejecutadas como QA Lead («firma pendiente» en las Tablas 19 a 25) o dejar la constancia de que la ejecución es automatizada. | Huamani R. | Antes de la exposición | A5-06 |
| 5 | Aplicar el instrumento SUS (≥ 5 respondientes por versión: Product Owner y personal de salud) y reportar el valor; hasta entonces el informe lo declara «pendiente». | Porras V. | 30/10/2026 (acción 5) | V6 como proxy (Tabla 35) |
| 6 | Confirmar por escrito con los tres integrantes y el docente el reparto de expositores y de responsabilidades (hoy es «propuesta del equipo») y ensayar los tres bloques de 5 minutos con el Anexo E. | Equipo | Antes de la exposición | Tabla 2, Tabla 39 |
| 7 | Corregir las observaciones nuevas N-01 a N-07 (texto exacto en E.2); en particular N-02 antes de que alguien reproduzca el Anexo C. | Porras V. (integración) | Antes de entregar | N-01 a N-07, H-13 |
| 8 | Opcional: regenerar las capturas con `locale="es-PE"` y mejorar las de RF-05 (JSON y CSV); actualizar horas en §5.0, §5.3, Anexo G.1 e `INDICE.md`. | Huamani R. | Antes de entregar | H-08, H-19 |
| 9 | Completar HIST-2.3 y HIST-2.4, ejecutar sus fichas (Tabla 26), capturar RF-08 y RF-09, crear el tag `v2.0-Inc2` solo si se cumple el Check (acción 3). | Auqui H. y Huamani R. | 26/10/2026 | A5-08, E-05, E-12 |
| 10 | Perfilar y corregir la regresión del p95 (V4: 175 → 610 ms) y repetir `ejecutar_carga.py` (acción 1); activar SonarCloud y ejecutar el job de PostgreSQL de v1.5 (acción 6); actualizar la DoD con exploración de entradas límite (acción 2). | Auqui H. y Huamani R. | 21/10 a 26/10/2026 | Tabla 37 |
| 11 | Confirmar con la microred los parámetros de la agenda (`ESQUEMA_AGENDA_V1`) y validar el valor con el Product Owner real; mientras tanto el informe lo declara referencial y simulado. | Equipo con el Product Owner | Sprint 4 | Tabla 35, Tabla 42 |
| 12 | Decidir si se acorta el cuerpo del informe para la exposición (N-08) y generar el PDF final comprobando que las imágenes SVG y los saltos de página se ven bien. | Porras V. | Antes de la exposición | H-17, N-08 |
