# Requisitos de la consigna integradora S6 (Unidades I y II)

- **Fuente única:** `guias/S6.CONSIGNA DE TRABAJO E INSTRUMENTO DE EVALUACIÓN INTEGRADOR.md`, una copia en Markdown de la consigna oficial. La copia en texto plano está en `archivo/tmp-revision/S6.CONSIGNA DE TRABAJO E INSTRUMENTO DE EVALUACIÓN INTEGRADOR.txt`.
- **Elaborado por:** el agente `sincronizador` el 2026-10-01, en la rama `feature/s6-integrador-final`.
- **Uso:** es la referencia común de todos los agentes S6. El `inspector-guia` evalúa cada R-xx y lo marca CUMPLE, PARCIAL o NO CUMPLE en `coordinacion/s6/INSPECCION_S6.md`. Nadie modifica los textos citados. Las *notas de aplicación* interpretan el requisito para este proyecto (PMV oficial `pmv_fastapi/`).
- **Totales:** 91 requisitos en 7 bloques:

| Bloque | Requisitos |
| --- | --- |
| A. Modalidad y entregables | R-01 a R-05 |
| B. Portada del informe | R-06 a R-09 |
| C. Estructura del informe | R-10 a R-39 |
| D. Siete diapositivas | R-40 a R-75 |
| E. Repositorio | R-76 a R-80 |
| F. Rúbrica de 8 criterios | R-81 a R-88 |
| G. Puntaje y formato de exposición | R-89 a R-91 |

Convención de la columna **Pts**: indica el criterio de la rúbrica (F) que evalúa el requisito. C1 a C4 valen 2,0 puntos cada uno y C5 a C8 valen 3,0 puntos cada uno.

---

## A. Modalidad y entregables obligatorios (consigna §I.1–I.2)

| ID | Requisito (texto fiel o paráfrasis mínima) | Pts | Nota de aplicación |
| --- | --- | --- | --- |
| R-01 | El **Informe Académico Integrador se entrega en PDF**, "estructurado según el formato oficial adjunto" (bloque C) | C1–C4 | Fuente: `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md`. PDF en `exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf`, generado por `conversor-entregas`. |
| R-02 | **Presentación visual (PDF/PPTX) con exactamente 7 diapositivas** diseñadas para la defensa | C5 | Fuente Marp en `entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md`. Salida en `exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pptx` y `.pdf`. Si se añade portada o agradecimiento, el total deja de ser 7; está prohibido. |
| R-03 | **Enlace al repositorio GitHub/GitLab** con código fuente del PMV, scripts de base de datos, pruebas automatizadas y `README.md` de despliegue | C6 | https://github.com/woshtsu/ProcesosSoftwareAnemia; PMV en `pmv_fastapi/` (ver bloque E). |
| R-04 | **Tiempo de exposición:** 7 min de exposición grupal + 5 min de defensa oral individual | C7, C8 | Ver la contradicción de tiempos en R-90. |
| R-05 | **Propósito integrador:** conectar problema organizacional → TO-BE → selección/adaptación del ciclo de vida (tailoring) → arquitectura → estrategia de pruebas → demostración funcional del PMV; modalidad grupal | C4 | La consigna habla de "Semanas 1 a 7". En este repositorio, S5 cubre lo que la consigna llama "Guía Semana 6" (arquitectura) y "Guía Semana 7" (pruebas). |

## B. Portada del informe (consigna §II, encabezado)

| ID | Requisito | Pts | Nota de aplicación |
| --- | --- | --- | --- |
| R-06 | Título "INFORME ACADÉMICO INTEGRADOR: UNIDADES I Y II" y subtítulo "DISEÑO E IMPLEMENTACIÓN DEL PROCESO DE SOFTWARE CON ENTREGA DE VALOR" | C1 | Textual. |
| R-07 | CARRERA (Ingeniería de Sistemas e Informática), ASIGNATURA (Procesos de Software ASUC01702 – Noveno Ciclo), PROYECTO DE ASIGNATURA [nombre de la solución / organización] | C1 | Nombre de la solución: "Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín" (`pmv_fastapi/README.md`). |
| R-08 | INTEGRANTES: Apellidos, Nombres, Código y Rol. La plantilla propone 4 roles: Leader / Software Architect; Process & QA Analyst; Backend / Data Engineer; Frontend / Mobile Developer | C8 | El equipo tiene **3 integrantes** con roles propios (Ingeniero de Proceso, de Desarrollo y Prototipado, de Calidad y Mejora). Hay que mapear los 4 roles de la plantilla a 3 personas y explicarlo. Los códigos de alumno son dato del equipo: van como PASO MANUAL y no se inventan. |
| R-09 | FECHA DE ENTREGA (DD/MM/AAAA) y DOCENTE | C1 | Dato del equipo (PASO MANUAL). No puede quedar `[PENDIENTE]` en la versión exportada. |

## C. Estructura del informe (consigna §II, secciones 1–6)

| ID | Sección | Requisito | Pts | Nota de aplicación / fuente |
| --- | --- | --- | --- | --- |
| R-10 | 1 | **Resumen ejecutivo ≤ 300 palabras** que sintetice: problema organizacional, solución tecnológica, modelo de proceso adaptado, arquitectura adoptada y resultados del PMV/Incremento 1 | C1, C4 | Debe describir FastAPI + PostgreSQL, 77 pruebas, 99 % de cobertura y p95 = 58 ms (DATOS_PMV_FASTAPI). Contar las palabras. |
| R-11 | 2.1 | Diagnóstico del problema organizacional y **matriz de actores/necesidades** | C1 | S1 §1–2. |
| R-12 | 2.1 | **Diagrama del proceso actual (AS-IS)** e identificación de **mínimo 5 brechas** | C1 | S1 §3–4 (B1 a B6); diagrama `diagramas/svg/10_s1_proceso_as_is.svg`. |
| R-13 | 2.1 | **Diagrama del proceso propuesto (TO-BE)** y **matriz de intervención del software** | C1 | S1 §5–6; `diagramas/svg/11_s1_proceso_to_be.svg`. |
| R-14 | 2.1 | **Cadena de valor organizacional e indicadores** de Proceso, Producto, Resultado y Valor (los 4 tipos) | C1, C4 | S1 §7–8; `diagramas/svg/12_s1_cadena_valor.svg`. |
| R-15 | 2.2 | **Matriz de factores del proyecto:** Incertidumbre, Complejidad, Riesgo, Integración y Datos/IA (los 5 deben aparecer con esos nombres) | C1 | S2 §1–2. |
| R-16 | 2.2 | **Matriz de comparación de modelos de ciclo de vida:** Cascada, Incremental, Scrum, DevOps y MLOps (los 5 como mínimo) | C1 | S2 §3, Tabla 3 (incluye además Espiral y Kanban). |
| R-17 | 2.2 | **Justificación técnica de la selección** y del **enfoque de adaptación híbrido (tailoring)** | C1 | S2 §4–5; matriz ponderada 4,75 / 3,85 / 2,95. |
| R-18 | 2.2 | **Representación gráfica del modelo de proceso aplicado** al proyecto | C1 | `diagramas/svg/15_s2_modelo_proceso_aplicado.svg` (o VIS-002). |
| R-19 | 2.3 | **Matriz de actividades del proceso** con Entradas, Productos de trabajo (artifacts) y Salidas | C2 | S3-4 §3, §6. |
| R-20 | 2.3 | **Matriz RAE** (Responsable de Ejecución, Revisión y Aprobación) | C2 | S3-4 §5. |
| R-21 | 2.3 | **Criterios de terminación (Definition of Done) por actividad** | C2 | S3-4 §7. |
| R-22 | 2.3 | **WBS:** Épicas → Historias de Usuario → Tareas del Incremento 1 | C2 | S3-4 §8.2; `diagramas/svg/31_s34_wbs_proyecto.svg`. Hay que conciliar las HU de FastAPI (HU-01 a HU-05) con HIST-1.1 a 1.5. |
| R-23 | 2.3 | **Estimación de esfuerzo**, **matriz de priorización (valor/riesgo)** y **plan de trabajo (cronograma/sprint)** | C2 | S3-4 §9–11 (21 SP, 113 h-p; Gantt `32_s34_gantt_incremento1.svg`). |
| R-24 | 2.3 | **Mecanismos de seguimiento, control de desviaciones e indicadores de avance** | C2 | S3-4 §13–15; burndown `35_s34_burndown_sprint1.svg`. |
| R-25 | 3.1 | **Clasificación en procesos principales, de soporte y organizacionales/gestión** | C3 | S5, más la consigna. |
| R-26 | 3.1 | **Matriz de adaptación práctica (tailoring) a las restricciones** del proyecto | C3 | Debe reflejar el PMV FastAPI: monolito modular, PWA, PostgreSQL/SQLite, CI. |
| R-27 | 3.2 | **ADRs que impactan en atributos de calidad (NFRs)** | C3 | `pmv_fastapi/docs/adr/ADR-001` a `ADR-006`. |
| R-28 | 3.2 | **Vistas C4: Nivel 1 (Contexto), Nivel 2 (Contenedores) y Nivel 3 (Componentes)**, las tres | C3 | Los C4 actuales de `diagramas/svg/03-05` describen **Flask**. Usar los C4 de FastAPI (VIS-003). |
| R-29 | 3.2 | **Modelo de datos** y **contratos de interfaces/API (OpenAPI/JSON)** | C3 | `pmv_fastapi/db/01_esquema_postgresql.sql` (figura VIS-004), `pmv_fastapi/docs/openapi.json`. |
| R-30 | 3.3 | **Pirámide de pruebas adaptada:** unitarias, integración/API, rendimiento/carga y UI/E2E (los 4 niveles con casos) | C3 | 62 + 11 + 4 + 1 escenario Locust. |
| R-31 | 3.3 | **Matriz de registro de ejecución de pruebas** y **reporte de cobertura de código** | C3 | `pmv_fastapi/docs/evidencias/cobertura.txt` (99 %). |
| R-32 | 3.3 | **Análisis estático (linting/SonarQube)** y **gestión de defectos** | C3 | `ruff.txt`, `registro_defectos.md` (DEF-01, DEF-02). Sonar: ver contradicción C-04 en DATOS_PMV_FASTAPI. |
| R-33 | 3.4 | **Arquitectura del entorno de despliegue** (Staging / Nube / Emulador) | C3, C6 | Docker Compose (api + postgres:16) y CI (VIS-006). |
| R-34 | 3.4 | **Evidencia del incremento funcional operativo** (capturas de pantalla / flujo de ejecución) | C3, C6 | `pmv_fastapi/docs/evidencias/capturas/01-08`, `demo_pmv.mp4`. |
| R-35 | 4 | **Matriz de trazabilidad integral** con las 8 columnas en este orden: [Problema Org.] ➔ [Proceso TO-BE] ➔ [Modelo Adaptado] ➔ [Categoría/Actividad] ➔ [Decisión Arquitectura] ➔ [Caso Prueba] ➔ [PMV Entregado] ➔ [Indicador Valor]. Debe demostrar coherencia lógica desde el problema hasta el PMV | C4 | La matriz actual tiene 4 columnas: NO CUMPLE el formato. |
| R-36 | 5 | **Tres conclusiones técnicas** sobre la efectividad del proceso de software diseñado (exactamente 3) | C4 | — |
| R-37 | 5 | **Tres lecciones aprendidas** sobre el control de desviaciones y la adaptación del ciclo de vida (exactamente 3) | C4 | — |
| R-38 | 6 | **Enlace al repositorio Git con tag `v1.0-PMV`** | C6 | El tag existe en origin (commit 9ce90c3); ver contradicción C-01. |
| R-39 | 6 | **README.md** con instrucciones de compilación, despliegue y scripts de base de datos | C6 | `pmv_fastapi/README.md` y README raíz. |

## D. Formato de exposición: 7 diapositivas visuales (consigna §III)

| ID | Diap. | Requisito | Pts | Nota de aplicación |
| --- | --- | --- | --- | --- |
| R-40 | 1 | **Esquema visual:** comparativo "Proceso Reactivo AS-IS (Manual/Retrasos)" vs. "Proceso Preventivo TO-BE (Software/Valor)" | C5 | VIS-001. |
| R-41 | 1 | Contenido: definición del **problema central** y **brechas operativas principales** | C5 | B1 a B6 resumidas. |
| R-42 | 1 | Contenido: **cadena de valor Datos ➔ Software ➔ Decisión ➔ Impacto organizacional** | C5 | — |
| R-43 | 1 | Contenido: **indicador de valor objetivo** (p. ej. "reducción del tiempo de respuesta de 2.5 h a 5 s") | C5 | Indicador real disponible: triple registro → expediente único (3 → 1 registros por evaluación). No inventar tiempos que no se hayan medido. |
| R-44 | 1 | Pitch de **1,5 min**: "cómo la solución resuelve la pérdida de valor organizacional" | C7 | En las notas del orador. |
| R-45 | 2 | **Esquema visual:** matriz de factores del proyecto + **diagrama del ciclo de vida adaptado** | C5 | VIS-002 (ciclo de vida) + VIS-015 (matriz de factores). |
| R-46 | 2 | Contenido: factores determinantes: incertidumbre, complejidad técnica, integración y componentes de datos/IA | C5 | — |
| R-47 | 2 | Contenido: **justificación del enfoque híbrido** (iterativo/incremental + Scrum + prácticas DevOps/MLOps) | C5 | — |
| R-48 | 2 | Contenido: **rechazo explícito** de Cascada tradicional o de Scrum puro sin ingeniería continua | C5 | Debe verse en el gráfico (VIS-002). |
| R-49 | 2 | Pitch de **1,5 min**: "por qué las características del proyecto exigieron esta adaptación" | C7 | — |
| R-50 | 3 | **Esquema visual:** **C4 nivel 2 (contenedores)** + **cuadro de ADRs** | C5 | VIS-003 (N2). |
| R-51 | 3 | Contenido: estructura tecnológica (apps móviles/web, API gateway, microservicios, base de datos y caché) | C5 | El PMV no tiene gateway, microservicios ni caché. Hay que **explicitar por qué no** (ADR-001: monolito modular) en lugar de inventarlos. La PWA sí tiene caché de interfaz (service worker). |
| R-52 | 3 | Contenido: **ADRs críticos vinculados a atributos de calidad** (concurrencia, latencia, disponibilidad) | C5 | ADR-003 (integridad/concurrencia por UNIQUE), ADR-006 (latencia p95), ADR-002 (disponibilidad de la interfaz con red intermitente). Cuadro visual: VIS-014. |
| R-53 | 3 | Contenido: **protocolos de comunicación** (REST, WebSockets, gRPC) | C5 | REST/JSON + OpenAPI 3.1; ADR-005 descarta WebSockets y gRPC. |
| R-54 | 3 | Pitch de **1,5 min**: "cómo la arquitectura soporta los requerimientos no funcionales" | C7 | — |
| R-55 | 4 | **Esquema visual:** **pirámide de pruebas** + **gráficos de cobertura** y **de pruebas de carga** | C5 | VIS-007, VIS-008, VIS-009. |
| R-56 | 4 | Contenido: cobertura de pruebas unitarias e integración (la consigna cita Jacoco/Istanbul/Jest; en Python el equivalente es pytest-cov) | C5 | 99 %. |
| R-57 | 4 | Contenido: pruebas de carga/estrés con **latencia p95** y **throughput RPS** (cita k6/JMeter; equivalente: Locust) | C5 | p95 = 58 ms; 39,6 req/s; 0 % de errores. |
| R-58 | 4 | Contenido: **cumplimiento de la Definition of Done** | C5 | DoD: cobertura ≥ 80 %, 0 hallazgos de ruff, suite en verde. |
| R-59 | 4 | Pitch de **1,5 min**: "evidencia objetiva de calidad y estabilidad del código" | C7 | — |
| R-60 | 5 | **Esquema visual:** mockup/capturas del software ejecutable + **video corto o demo en vivo (2 min)** | C5, C6 | Capturas 01–08 (collage VIS-013) y `demo_pmv.mp4`. |
| R-61 | 5 | Contenido: alcance del PMV con **HU-01, HU-02 y HU-03 operativas** | C6 | El PMV cumple HU-01 a HU-05. |
| R-62 | 5 | Contenido: **entorno de despliegue** (emulador / cloud / staging) | C6 | Staging con Docker Compose. Si no hay despliegue en la nube, decirlo. |
| R-63 | 5 | Contenido: **validación de criterios de aceptación con el usuario final** | C6 | No hay acta de un usuario real: PASO MANUAL. No inventarla. |
| R-64 | 5 | Pitch de **2,0 min**: "demostrar el software funcionando en vivo o en video ejecutable" | C6, C7 | — |
| R-65 | 6 | **Esquema visual:** **dashboard de métricas integradas** (proceso + producto + valor) | C5 | VIS-010. |
| R-66 | 6 | Contenido: **historias planificadas vs. completadas** (velocidad / burndown) | C5 | VIS-011. |
| R-67 | 6 | Contenido: **densidad de defectos** y **cobertura %** | C5 | 2,0 defectos/KLOC; 99 %. |
| R-68 | 6 | Contenido: **métricas de impacto organizacional**: medición real alcanzada en el PMV | C5 | Solo lo medido; datos sintéticos. |
| R-69 | 6 | Pitch de **1,0 min**: "datos cuantitativos del éxito de la iteración" | C7 | — |
| R-70 | 7 | **Esquema visual:** **flujo de trazabilidad unificada** (Problema ➔ Proceso ➔ Arquitectura ➔ Pruebas ➔ Valor) | C5 | VIS-012. |
| R-71 | 7 | Contenido: **matriz de trazabilidad** que conecta las Unidades I y II | C5 | Versión sintética de R-35. |
| R-72 | 7 | Contenido: **conclusiones principales** del proceso de ingeniería aplicado | C5 | — |
| R-73 | 7 | Contenido: **siguiente incremento planificado para la Unidad III** | C5 | INC-2 (agenda y alertas), sprint 3 del cronograma (VIS-016). |
| R-74 | 7 | Pitch de **1,0 min**: "coherencia completa del trabajo" | C7 | — |
| R-75 | Todas | **Exactamente 7 diapositivas**, alto impacto visual, esquemas de procesos, vistas C4 y datos numéricos, **sin bloques de texto**, diagramas legibles, sin material copiado de internet | C5 | Rúbrica C5. Máximo recomendado: unas 40 palabras visibles por diapositiva; el resto va a las notas. |

## E. Repositorio de código (consigna §I.2 punto 3 y §II.6)

| ID | Requisito | Pts | Nota de aplicación |
| --- | --- | --- | --- |
| R-76 | Código fuente del PMV en el repositorio | C6 | `pmv_fastapi/app/`. |
| R-77 | Scripts de base de datos | C6 | `pmv_fastapi/db/01_esquema_postgresql.sql`, `pmv_fastapi/scripts/cargar_datos_prueba.py`. |
| R-78 | Pruebas automatizadas | C3, C6 | `pmv_fastapi/tests/`. El CI debe ejecutarse en GitHub, pero hoy `ci.yml` está en `pmv_fastapi/.github/` y GitHub lo ignora (C-02). |
| R-79 | `README.md` de despliegue con compilación, despliegue y scripts de BD | C6 | `pmv_fastapi/README.md` cumple. El README raíz debe remitir a él. |
| R-80 | **Tag `v1.0-PMV`** | C6 | Existe en origin, pero no es alcanzable desde `main` (C-01). |

## F. Rúbrica de evaluación (consigna §IV): 8 criterios

Niveles de la sección A: Excelente 2,0 · Bueno 1,5 · Básico 1,0 · Inicial 0,5. Niveles de la sección B: Excelente 3,0 · Bueno 2,25 · Básico 1,5 · Inicial 0,75.

| ID | Criterio | Máx. | Descriptor de "Excelente" (meta) | Lo que baja a Básico/Inicial |
| --- | --- | --- | --- | --- |
| R-81 | **C1. Fundamentación del proceso organizacional y modelo** (Unidad I, S1–S2) | 2,0 | Modela con alto rigor AS-IS y TO-BE, brechas e indicadores. Justifica la selección y el tailoring del modelo según los factores reales del proyecto | Diagnóstico incompleto o justificación por "modas" o conceptos genéricos; sin diagramas de procesos |
| R-82 | **C2. Operatividad de actividades y planificación** (Unidad I, S3–S4) | 2,0 | Actividades con entradas/salidas, RAE y DoD. WBS, priorización valor/riesgo, estimación y matriz de seguimiento de desviaciones | Actividades genéricas sin DoD ni seguimiento; cronograma desvinculado de las actividades |
| R-83 | **C3. Categorización, arquitectura y pruebas del PMV** (Unidad II, S5–S7) | 2,0 | Clasifica los procesos normativos. Documenta la arquitectura con vistas C4 y ADRs. Diseña y documenta casos de prueba en múltiples niveles con reportes de cobertura | Diagramas genéricos o pruebas superficiales sin cobertura; sin arquitectura ni estrategia de pruebas |
| R-84 | **C4. Trazabilidad integral y medición de valor** | 2,0 | Matriz de trazabilidad "impecable" desde el problema hasta el PMV, sustentada en un **tablero de indicadores de proceso, producto y valor** | Trazabilidad parcial o desconectada de los resultados medidos; elementos aislados |
| R-85 | **C5. Estructura visual y síntesis de diapositivas** | 3,0 | Cumple **estrictamente** las 7 diapositivas, con alto impacto visual, esquemas de procesos, vistas C4 y datos numéricos, evitando bloques de texto | Más o menos diapositivas, cargadas de texto, diagramas ilegibles, desorganizadas o copiadas |
| R-86 | **C6. Demostración operativa y despliegue del PMV** | 3,0 | Demo fluida del PMV ejecutable **desplegado en Staging/Cloud**, comprobando HU y criterios de aceptación | Demo con fallos o **solo capturas estáticas** (Básico); software no ejecutable (Inicial) |
| R-87 | **C7. Sustentación oral técnica y argumentación** | 3,0 | Domina la jerga técnica. Fundamenta tailoring, ADRs y estrategia de pruebas **dentro del tiempo límite** | Lectura de diapositivas o exceso de tiempo |
| R-88 | **C8. Defensa oral individual y preguntas de dominio** | 3,0 | **Cada integrante** responde con solvencia sobre el repositorio, la arquitectura y las pruebas | Respuestas evasivas; desconocimiento del código |

## G. Puntaje y formato de exposición

| ID | Requisito | Nota |
| --- | --- | --- |
| R-89 | Distribución: **Informe 8 pts (40 %)** (C1–C4) + **Exposición y evaluación oral 12 pts (60 %)** (C5–C8) = **20 pts** | El 60 % depende de la presentación, la demo y la defensa. Ver `coordinacion/s6/PASOS_MANUALES.md`. |
| R-90 | El guion debe ajustarse a **7 minutos** de exposición grupal | **Contradicción interna de la consigna:** los pitches suman 1,5 + 1,5 + 1,5 + 1,5 + 2,0 + 1,0 + 1,0 = **10 min**, más que los 7 min de §I.2. Recomendación: guion de 7 min con la proporción reducida al 70 % (1:05, 1:05, 1:05, 1:05, 1:25, 0:40 y 0:35 = 7:00). Durante la demo de la diapositiva 5 se usa el video. |
| R-91 | El PMV debe poder **demostrarse en vivo o en video ejecutable** desde un entorno de pruebas/staging | Video `pmv_fastapi/docs/evidencias/demo_pmv.mp4` como respaldo. Para "Excelente" en C6 conviene una demo en vivo en staging (Docker Compose) o en la nube. |

## Requisitos implícitos de coherencia (no puntúan por sí solos, pero afectan a C1–C4)

- El informe y las diapositivas deben describir **el mismo PMV** (FastAPI + PostgreSQL) con las mismas cifras de `coordinacion/s6/DATOS_PMV_FASTAPI.md`. El prototipo Flask (`anemia_junin/`) se menciona solo como antecedente o espiga técnica (spike).
- La versión exportada no debe contener marcadores `CARGA_CIERRE`, `[PENDIENTE]` ni `<!-- ... pendiente -->`.
- Ninguna cifra, acta ni aceptación de usuario se inventa. Lo que dependa de personas va a `PASOS_MANUALES.md`.
