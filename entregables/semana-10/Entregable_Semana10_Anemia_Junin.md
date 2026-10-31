# INFORME TÉCNICO: EVALUACIÓN DE CALIDAD DE PRODUCTO DE SOFTWARE (FURPS+) — Semana 10

> **Nota.** Todas las cifras de este informe salen de mediciones reproducibles: cada una tiene su comando o script en `metricas/` y su salida cruda en `metricas/salidas/`. Lo que no se pudo medir se declara como **no medido** y no se cuenta como cumplido. Las rutas son relativas a la raíz del repositorio, salvo las de imágenes (`evidencias/...`), que son relativas a `entregables/semana-10/`.

**Índice**

- 1. Carátula e integrantes
- 2. Resumen ejecutivo y criterios FURPS+ (Actividad 1)
- 3. Auditoría del Factor F en los incrementos 1 a 4 (Actividad 2)
- 4. Factores URPS: usabilidad, confiabilidad, rendimiento y soportabilidad (Actividad 3)
- 5. Factor +: OWASP Top 10:2025 y restricciones (Actividad 4)
- 6. Consolidado FURPS+ y plan de evolución (Actividad 5)
- 7. Conclusiones y lecciones aprendidas
- 8. Anexos y evidencias técnicas

## 1. CARÁTULA E INTEGRANTES DEL EQUIPO (Noveno Ciclo)

**Tabla 1.** Datos generales del entregable.

| Campo | Detalle |
| --- | --- |
| **Carrera** | Ingeniería de Sistemas e Informática |
| **Asignatura** | Procesos de Software (ASUC01702), Universidad Continental, periodo 2026-20, Noveno ciclo |
| **Proyecto de asignatura** | Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín |
| **Docente** | Guevara Jimenez, Jorge Alfredo |
| **Semana y guía** | Semana 10: «Evaluación de la calidad del producto de software mediante el modelo FURPS+» (`guias/S10-PSW-GUÍA DE TRABAJO SEMANA 10.docx.md`) |
| **Fecha** | 30/10/2026 (todas las mediciones se ejecutaron ese día) |
| **Versiones evaluadas** | Los cuatro incrementos: `v1.0-PMV` (Inc. 1, RF-01 a RF-05), `v2.0-Inc2` (Inc. 2, RF-06 a RF-09), `v3.0-Inc3` (Inc. 3, HIST-3.1 a 3.4 y VIS-3.5) y `v4.0-Inc4` (Inc. 4, HIST-4.1 a 4.4). La guía solo pide los incrementos 1 a 3; se agrega el 4 porque el código vigente lo incluye |
| **Código medido** | Rama `docs/s12-integrador`, versión `4.0.0-inc4`. Pruebas y cobertura: commit `e6886e2`; resto de mediciones: commit `ada827f` (difiere de `e6886e2` solo en documentación; `pmv_fastapi/` no cambió). Cada captura de terminal muestra comando, fecha y commit en su pie |
| **Repositorio** | <https://github.com/woshtsu/ProcesosSoftwareAnemia> (privado) |

**Tabla 2.** Integrantes, códigos, roles y responsabilidad propuesta en este entregable.

| N.° | Apellidos, Nombres | Código | Rol en el proyecto | Responsabilidad propuesta en este entregable (propuesta del equipo) |
| --- | --- | --- | --- | --- |
| 1 | Porras Veli, Ricardo | 76659572 | Ingeniero de Proceso | Consolidado FURPS+ (Actividad 5), plan de evolución e integración del informe |
| 2 | Auqui Huincho, Tania Tifani | 75280128 | Ingeniera de Desarrollo y Prototipado | Factor S (arquitectura hexagonal) y Factor + (OWASP 2025, restricciones técnicas) |
| 3 | Huamani Rodriguez, Jean Piero | 72156889 | Ingeniero de Calidad y Mejora del Proceso (QA Lead) | Factores F, U, R y P (pruebas de aceptación, accesibilidad, confiabilidad y carga) |
| 4 | Amaru — Claude, asistente de IA (Anthropic) | — | Asistente de IA: apoyo en desarrollo, pruebas automatizadas, evidencias y documentación técnica, bajo supervisión del equipo | Ejecutó los scripts de medición de `metricas/`, generó las capturas automáticas y redactó el borrador técnico; el equipo revisa y valida |

El reparto de responsabilidades es una **propuesta del equipo** basada en los roles de la matriz RAE de S3-4; no hay confirmación formal de los integrantes ni del docente.

**Nota sobre los datos.** Todos los datos de las pruebas y capturas son **sintéticos** (`pmv_fastapi/scripts/cargar_datos_prueba.py` y datos generados por cada script). Las capturas de software se tomaron con `AUTH_MODE=demo`, igual que las pruebas E2E; los controles de sesión, cookies y CSRF se midieron en `AUTH_MODE=supabase` con Supabase simulado (`httpx.MockTransport`), de modo que **no se probó un proyecto Supabase real**. No hubo usuarios reales ni piloto: ninguna cifra representa aceptación del usuario ni impacto clínico. La clasificación de anemia es referencial.

## 2. RESUMEN EJECUTIVO Y CRITERIOS DE EVALUACIÓN FURPS+ (Actividad 1)

El **Índice de Calidad FURPS+ (IC_P) es 87,67 %** calculado solo sobre los criterios medidos, y **78,43 %** si los criterios no medidos se cuentan como 0 % (índice conservador). Ambos quedan por debajo del umbral «Excelente (≥ 90 %)» de la guía. La funcionalidad (F) está al 100 %: 19 de 19 escenarios de aceptación y 688 de 688 pruebas automáticas aprobados. Las brechas están en U (contraste de componentes, etiquetas ARIA, foco en modales), R (caída de la base de datos responde 500), P (p95 de 2 s a 100 usuarios) y +, donde se hallaron 0 de 6 cabeceras de seguridad HTTP, inyección de fórmulas en el CSV, ausencia de control por roles y de registro de eventos de seguridad.

### 2.1 Matriz 1.1: ficha de criterios y métricas FURPS+ del proyecto

**Tabla 3.** Matriz 1.1. Criterios, herramienta realmente usada y umbral (las diferencias con la guía están en la columna «Herramienta»).

| Factor | Atributo evaluado | Método / herramienta usada (script en `metricas/`) | Umbral de aceptación |
| --- | --- | --- | --- |
| **F** | Cobertura funcional incremental | Playwright sobre la aplicación real, 19 escenarios con aserciones (`capturar_software.py`); pytest 660 + E2E 28 | 100 % de RF/historias aprobadas en Inc. 1 a 4 |
| **U** | Psicología de colores y accesibilidad | axe-core 4.14.0 (WCAG 2.1 A/AA) por pantalla en escritorio y móvil; razón de contraste calculada por par de colores; recorrido por teclado; objetivos táctiles; reflujo a 320 px (`accesibilidad.py`, `paleta_colores.py`). Lector de pantalla (NVDA/TalkBack): no ejecutado | Contraste ≥ 4,5:1 (texto) y ≥ 3:1 (componentes); 0 violaciones axe |
| **R** | Confiabilidad y tolerancia a fallas | Sondeo de `/api/salud` durante Locust; MTTR con `kill -9` y reinicio; prueba de caos con PostgreSQL 16 temporal (`rendimiento.py`, `caos_postgres.py`). Staging Render/AWS: no existe, no medido | Disponibilidad ≥ 99,5 %, MTTR < 5 min, recuperación sin reiniciar la aplicación |
| **P** | Latencia, concurrencia y recursos | Locust 20 y 100 usuarios, 60 s (en lugar de k6/JMeter), RSS, métricas del navegador con perfil móvil lento (`rendimiento.py`, `rendimiento_cliente.py`). 500 usuarios: no medido | p95 < 800 ms; error ≤ 1 %; LCP < 2500 ms |
| **S** | Arquitectura hexagonal y mantenibilidad | Análisis AST de importaciones (`auditoria_hexagonal.py`), 25 pruebas de arquitectura, pytest-cov, Ruff, radon (en lugar de SonarQube, que exige `SONAR_TOKEN` y no se ejecutó) | 0 importaciones de frameworks en el dominio; cobertura ≥ 80 %; 0 errores Ruff |
| **+** | Seguridad (OWASP Top 10:2025) y restricciones | bandit, pip-audit, semgrep con reglas locales, 30 comprobaciones estáticas y 32 dinámicas contra el servidor local (`owasp_estatico.py`, `seguridad_http.py`, `seguridad_xss.py`). OWASP ZAP: no ejecutado | 0 vulnerabilidades Alta/Crítica; controles OWASP implementados |

### 2.2 Cálculo del índice FURPS+ por criterio

Cada criterio pesa lo mismo dentro de su factor. Fórmulas: **ratio** = cumplen ÷ total × 100; **mayor es mejor** = mín(100, medido ÷ meta × 100); **menor es mejor** = mín(100, meta ÷ medido × 100) (medido 0 → 100 %; meta 0 y medido > 0 → 0 %). Pesos de la guía: F 30, U 15, R 15, P 15, S 10, + 15. Comando: `python entregables/semana-10/metricas/furps_calculo.py` (lee `metricas/salidas/*.json|xml|txt`, escribe `FURPS_calculo.json`).

**Tabla 4.** Cálculo por criterio. «N/M» = no medido: se excluye del índice primario y cuenta 0 % en el conservador.

| Factor | ID | Criterio | Fórmula | Valor medido | Meta | % cumplimiento | Fuente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F | F1 | Escenarios de aceptación aprobados (Inc. 1-4) | cumplen/total | 19/19 | 100 % | 100,0 % | `salidas/F_resultados_aceptacion.json` |
| F | F2 | Pruebas automatizadas aprobadas (unitarias+integración+arquitectura y E2E) | cumplen/total | 688/688 | 100 % | 100,0 % | `salidas/R02_junit_unit.xml, R03_junit_e2e.xml` |
| F | F3 | Tiempo de RF-01 (guardar) y RF-05 (reporte), peor caso | mín(100, meta/medido) | 130 ms | < 2 s | 100,0 % | `salidas/F_resultados_aceptacion.json` |
| U | U1 | axe-core WCAG 2.1 A/AA: reglas aprobadas sobre evaluadas (14 pantallas x 2 vistas) | cumplen/total | 626/684 reglas; 2/28 pantallas sin violaciones | 100 % (0 violaciones) | 91,5 % | `salidas/U_axe_por_pantalla.json` |
| U | U2 | Contraste de texto ≥ 4,5:1 (1.4.3), pares de color únicos | cumplen/total | 22/23 pares | 100 % | 95,7 % | `salidas/U_contraste_paleta.json` |
| U | U3 | Contraste de componentes ≥ 3:1 (1.4.11): bordes, foco y barras | cumplen/total | 3/8 | 100 % | 37,5 % | `salidas/U_contraste_paleta.json` |
| U | U4 | Teclado (2.1.1/2.4.3): ciclo, indicador de foco, registro, abrir/cerrar modal, foco contenido y devuelto | cumplen/total | 6/8 comprobaciones | 100 % | 75,0 % | `salidas/U_teclado.json` |
| U | U5 | Objetivos táctiles ≥ 24x24 px (2.5.8, WCAG 2.2) | cumplen/total | 734/924 (escritorio+móvil) | 100 % | 79,4 % | `salidas/U_objetivos_tactiles.json` |
| U | U6 | Reflujo a 320 px sin desplazamiento horizontal (1.4.10) | cumplen/total | 13/13 pantallas | 100 % | 100,0 % | `salidas/U_reflow_320px.json` |
| U | U7 | Estados de color con texto asociado (1.4.1, no solo color) | cumplen/total | 482/482 insignias | 100 % | 100,0 % | `salidas/U_estados_con_texto.json` |
| U | U8 | Lector de pantalla NVDA/TalkBack (4.1.2) | cumplen/total | no medido (sin lector instalado) | 100 % | N/M | `-` |
| R | R1 | Disponibilidad de /api/salud durante las 3 corridas de carga | mín(100, medido/meta) | 100,0 % (332 sondeos, 0 fallidos) | ≥ 99,5 % | 100,0 % | `salidas/P_resumen.json` |
| R | R2 | MTTR: kill -9 del servidor y reinicio hasta /api/salud 200 | mín(100, meta/medido) | 0,85 s (datos íntegros: True) | < 5 min | 100,0 % | `salidas/R_mttr_reinicio.json` |
| R | R3 | Caos PostgreSQL (kill -9): el pool se reconecta sin reiniciar la aplicación | cumplen/total | sí, 0,2 s tras volver la BD | sin reinicio | 100,0 % | `salidas/R_caos_postgres.json` |
| R | R4 | Caos PostgreSQL: peticiones durante la caída respondidas sin error 500 | cumplen/total | 1/26 (500: 25) | respuesta controlada (503), 0 x 500 | 3,8 % | `salidas/R_caos_postgres.json` |
| R | R5 | Tasa de error con carga nominal (20 usuarios, 2 corridas) | mín(100, meta/medido) | 0/1887 fallos | ≤ 1 % | 100,0 % | `salidas/P_resumen.json` |
| R | R6 | Lecturas servidas desde el caché del service worker con el servidor detenido | cumplen/total | 30/30 filas | 100 % | 100,0 % | `salidas/F_resultados_aceptacion.json` |
| R | R7 | Disponibilidad en staging (Render/AWS) y recuperación automática de la BD gestionada | cumplen/total | no medido (no hay entorno de staging) | ≥ 99,5 % | N/M | `-` |
| P | P1 | Latencia p95, 20 usuarios (peor de Inc. 1-2 e Inc. 3-4) | mín(100, meta/medido) | 98 ms (p50 10/9 ms) | < 800 ms | 100,0 % | `salidas/P_resumen.json` |
| P | P2 | Latencia p95, 100 usuarios (Inc. 1-2) | mín(100, meta/medido) | 2000 ms (p50 780 ms) | < 800 ms | 40,0 % | `salidas/P_resumen.json` |
| P | P3 | Latencia p95, 500 usuarios (meta de la guía) | mín(100, meta/medido) | no medido (máximo probado: 100) | < 800 ms | N/M | `-` |
| P | P4 | Tasa de error a 100 usuarios | mín(100, meta/medido) | 0,034 % (1 de 2904: DNI duplicado generado por el script) | ≤ 1 % | 100,0 % | `salidas/P_resumen.json` |
| P | P5 | LCP de la primera carga móvil (390x844, CPU x4, 1,6 Mbps, 150 ms) | mín(100, meta/medido) | 468 ms (con service worker: 84 ms) | < 2500 ms | 100,0 % | `salidas/P_cliente_pwa.json` |
| S | S1 | Importaciones de frameworks/terceros en el dominio (archivos limpios sobre archivos) | cumplen/total | 0 importaciones en 29 archivos | 0 | 100,0 % | `salidas/S_hexagonal.json` |
| S | S2 | Pruebas de arquitectura (regla de dependencias) aprobadas | cumplen/total | 25/25 | 100 % | 100,0 % | `salidas/R02_junit_unit.xml` |
| S | S3 | Cobertura de líneas y ramas (pytest-cov) | mín(100, medido/meta) | 99,79 % | ≥ 80 % (umbral del proyecto) | 100,0 % | `salidas/R01_cobertura.json` |
| S | S4 | Ruff (E,F,W,I,B,UP,S,C90): errores | mín(100, meta/medido) | 0 errores | 0 | 100,0 % | `salidas/R04_ruff_check.txt` |
| S | S5 | Bloques con complejidad ciclomática ≤ 10 (radon) | cumplen/total | 646/669 (máx. 17) | 100 % | 96,6 % | `salidas/S_radon_resumen.json` |
| S | S6 | Archivos con índice de mantenibilidad rango A (radon mi) | cumplen/total | 73/75 | 100 % | 97,3 % | `salidas/S_radon_resumen.json` |
| + | +1 | Comprobaciones OWASP 2025 que cumplen (estáticas E01-E30 y dinámicas T01-T32) | cumplen/total | 41/61 (+1 no medida) | 100 % | 67,2 % | `salidas/OWASP_estatico.json, OWASP_pruebas_http.json` |
| + | +2 | Vulnerabilidades Alta/Crítica por SAST y SCA (bandit, pip-audit) | mín(100, meta/medido) | 0 (bandit: 0 altas, 1 baja; pip-audit: 0) | 0 | 100,0 % | `salidas/O05_bandit.json, R09_pip_audit.txt` |
| + | +3 | Hallazgos Alta/Crítica confirmados por revisión manual y dinámica (A01: sin RBAC) | mín(100, meta/medido) | 1 (falta de roles/segmentación) | 0 | 0,0 % | `salidas/OWASP_estatico.json (E01)` |
| + | +4 | Restricciones técnicas verificadas por ejecución (diseño, implementación, interfaz) | cumplen/total | 3/3 (Docker: sin daemon, no ejecutado) | 100 % | 100,0 % | `salidas/R06, R04, R07` |
| + | +5 | Restricción de despliegue Docker verificada por ejecución (build/up) | cumplen/total | no medido (sin daemon Docker) | 100 % | N/M | `-` |
| + | +6 | Política de contraseñas, MFA y bloqueo por intentos (Supabase Auth, A07) | cumplen/total | no medido (se configura en el panel de Supabase) | 100 % | N/M | `salidas/OWASP_estatico.json (E23)` |

**Tabla 5.** Índice por factor y global. IC_P = Σ(% del factor × peso).

| Factor | Criterios medidos | Peso | % primario (solo medidos) | Ponderado primario | % conservador (no medidos = 0) | Ponderado conservador |
| --- | --- | --- | --- | --- | --- | --- |
| F — Funcionalidad | 3 de 3 | 30 % | 100,0 % | 30,00 % | 100,0 % | 30,00 % |
| U — Usabilidad | 7 de 8 | 15 % | 82,7 % | 12,41 % | 72,4 % | 10,86 % |
| R — Confiabilidad | 6 de 7 | 15 % | 84,0 % | 12,60 % | 72,0 % | 10,80 % |
| P — Rendimiento | 4 de 5 | 15 % | 85,0 % | 12,75 % | 68,0 % | 10,20 % |
| S — Soportabilidad | 6 de 6 | 10 % | 99,0 % | 9,90 % | 99,0 % | 9,90 % |
| + — Seguridad y restricciones | 4 de 6 | 15 % | 66,8 % | 10,02 % | 44,5 % | 6,68 % |
| **TOTAL (IC_P)** |  | **100 %** |  | **87,67 %** |  | **78,43 %** |

![Figura 1. Salida del cálculo del índice FURPS+ (comando, fecha y commit en el pie).](evidencias/terminal/FURPS01_calculo_indice.png)

**Figura 1.** Salida del cálculo del índice FURPS+ (comando, fecha y commit en el pie). Archivo: `evidencias/terminal/FURPS01_calculo_indice.png`.

**Criterios no medidos** (por qué): U8 lector de pantalla (no hay NVDA/TalkBack en el entorno de medición); R7 disponibilidad en staging (no hay entorno Render/AWS desplegado); P3 p95 a 500 usuarios (el máximo probado fue 100); +5 despliegue con Docker (no hay daemon Docker; el CI sí construye la imagen, ver Anexo C); +6 política de contraseñas, MFA y bloqueo (se configura en el panel de Supabase). El rendimiento (RPS) y la memoria (RSS 81 a 118 MB) se informan pero **no puntúan**: la guía no fija una meta y Locust en bucle cerrado depende del tiempo de espera entre tareas.

## 3. AUDITORÍA DEL FACTOR F: FUNCIONALIDAD EN INCREMENTOS 1, 2, 3 Y 4 (Actividad 2)

Cada escenario lo ejecuta `metricas/capturar_software.py` contra la aplicación real (uvicorn en `127.0.0.1:8765`, SQLite temporal con datos sintéticos, `AUTH_MODE=demo`) con Chromium de Playwright. Cada escenario incluye aserciones sobre la interfaz y la API; si una falla, el estado es «Rechazado». Resultado: **19 de 19 aprobados, 54 capturas** (escritorio 1366x768; móvil 390x844, solo ventana). Salida cruda: `metricas/salidas/F_resultados_aceptacion.json`. La etiqueta `v4.0-Inc4` incluye el código de los cuatro incrementos: cada historia se verifica en esa versión, no se ejecutaron de nuevo las etiquetas anteriores.

![Figura 2. Ejecución de los 19 escenarios de aceptación (salida del script de capturas).](evidencias/terminal/F01_aceptacion_software.png)

**Figura 2.** Ejecución de los 19 escenarios de aceptación (salida del script de capturas). Archivo: `evidencias/terminal/F01_aceptacion_software.png`.

### 3.1 Matriz 2.1: auditoría del Factor F en los Incrementos 1, 2, 3 y 4

**Tabla 6.** Matriz 2.1. Requerimientos y historias por incremento, criterio Given-When-Then, estado medido y evidencias (las pruebas están bajo `pmv_fastapi/`; las capturas, en `evidencias/software/`).

| Cód. | Requerimiento / historia | Incremento | Criterio de aceptación (Given-When-Then) | Estado | Evidencia en Git / captura |
| --- | --- | --- | --- | --- | --- |
| **RF-01** | Registro del niño con evaluación inicial | Inc. 1 (`v1.0-PMV`) | Dado un formulario con datos válidos, cuando se pulsa «Guardar registro», entonces se confirma y se abre el expediente en < 2 s (130 ms); con un DNI ya registrado la API responde 409. | **Aprobado** | `pmv_fastapi/tests/integracion/test_api.py`, `tests/unitarias/test_casos_uso.py`; `RF01_inc1_1_entrada_escritorio.png` y 2 más |
| **RF-02** | Consulta y actualización del expediente; nuevo control | Inc. 1 (`v1.0-PMV`) | Dado un expediente existente, cuando se consulta, se edita un campo permitido y se agrega un control, entonces los cambios persisten y el historial pasa de 2 a 3 evaluaciones. | **Aprobado** | `tests/integracion/test_api.py`, `tests/unitarias/test_entidades.py`; `RF02_inc1_1_expediente_escritorio.png` y 3 más |
| **RF-03** | Validación con reglas clínicas | Inc. 1 (`v1.0-PMV`) | Dado un formulario clínico, cuando se digita la Hb, entonces se muestran Hb ajustada por altitud y clasificación; con datos inválidos se rechaza con mensajes por campo (HTTP 422). | **Aprobado** | `tests/unitarias/test_reglas_clinicas.py`; `RF03_inc1_1_vista_previa_escritorio.png` y 2 más |
| **RF-04** | Listado de niños en seguimiento | Inc. 1 (`v1.0-PMV`) | Dado un conjunto de niños, cuando se filtra por clasificación o se busca por comunidad, entonces el listado respeta el filtro (27 niños; 6 con «Moderada»). | **Aprobado** | `tests/integracion/test_api.py`, `tests/e2e/test_interfaz.py`; `RF04_inc1_1_seguimiento_escritorio.png` y 2 más |
| **RF-05** | Reporte del periodo en JSON y CSV | Inc. 1 (`v1.0-PMV`) | Dado un periodo válido, cuando se pulsa «Generar», entonces se muestran los indicadores (28 registrados) y se descarga el CSV en < 2 s (86 ms; 43 líneas). | **Aprobado** | `tests/integracion/test_api.py`; `RF05_inc1_1_reporte_escritorio.png` y 1 más |
| **RF-06** | Agenda de controles según la normativa | Inc. 2 (`v2.0-Inc2`) | Dado un niño con anemia en tratamiento, cuando se abre su expediente, entonces se muestra la agenda normativa (13 controles) con estados cumplido, pendiente y vencido. | **Aprobado** | `tests/unitarias/test_agenda.py`; `RF06_inc2_1_agenda_expediente_escritorio.png` y 1 más |
| **RF-07** | Controles vencidos y alertas priorizadas | Inc. 2 (`v2.0-Inc2`) | Dado un conjunto de niños con controles, cuando se abre «Alertas» y se filtra por prioridad, entonces se listan los vencidos ordenados (9 vencidos: 7 ALTA, 1 MEDIA, 1 BAJA). | **Aprobado** | `tests/unitarias/test_alertas.py`, `tests/integracion/test_api_inc2.py`; `RF07_inc2_1_alertas_escritorio.png` y 2 más |
| **RF-08** | Agenda del personal por rango de fechas | Inc. 2 (`v2.0-Inc2`) | Dado el personal del establecimiento, cuando consulta un rango de hasta 31 días, entonces ve los controles por día (30 días: 17 controles, 14 niños); un rango mayor se rechaza. | **Aprobado** | `tests/unitarias/test_agenda_personal.py`, `tests/e2e/test_interfaz_inc2_final.py`; `RF08_inc2_1_agenda_semana_escritorio.png` y 3 más |
| **RF-09** | Registro de asistencia a un control | Inc. 2 (`v2.0-Inc2`) | Dado un control programado, cuando se registra «No asistió» con motivo, entonces queda la marca de inasistencia y sube la prioridad (vencidos sin registro: 9 → 8). | **Aprobado** | `tests/unitarias/test_asistencia.py`, `tests/e2e/test_interfaz_inc2_final.py`; `RF09_inc2_1_modal_inasistencia_escritorio.png` y 3 más |
| **HIST-3.1** | Registro sin conexión (cola en el dispositivo) | Inc. 3 (`v3.0-Inc3`) | Dado que no hay conexión, cuando se registra un niño, una evaluación y una visita, entonces quedan guardados en el dispositivo con indicador de pendientes (2) y el servidor no tiene el registro. | **Aprobado** | `tests/e2e/test_inc3_sin_conexion.py`; `HIST31_inc3_1_en_linea_escritorio.png` y 1 más |
| **HIST-3.1b** | Apertura sin conexión desde el caché (servidor detenido) | Inc. 3 (`v3.0-Inc3`) | Dado que no hay servidor ni red, cuando se recarga la aplicación, entonces el shell y las lecturas se sirven desde el service worker con aviso (30 de 30 filas desde caché). | **Aprobado** | `tests/e2e/test_inc3_sin_conexion.py`; `HIST31_inc3_3_recarga_sin_conexion_escritorio.png` |
| **HIST-3.2** | Sincronización idempotente al reconectar | Inc. 3 (`v3.0-Inc3`) | Dado que hay pendientes, cuando vuelve la red, entonces cada operación se aplica una sola vez (APLICADA) y reenviar la misma no duplica (DUPLICADA; evaluaciones sin cambio). | **Aprobado** | `tests/unitarias/test_sincronizacion.py`, `tests/integracion/test_api_inc3.py`; `HIST32_inc3_1_panel_antes_de_sincronizar_escritorio.png` y 1 más |
| **HIST-3.3** | Resolución de conflictos sin sobrescribir a ciegas | Inc. 3 (`v3.0-Inc3`) | Dado un dato distinto en el servidor, cuando se sincroniza, entonces queda un CONFLICTO pendiente y el personal decide (conservar el del servidor): 1 conflicto resuelto. | **Aprobado** | `tests/unitarias/test_conflictos.py`, `tests/integracion/test_api_inc3.py`; `HIST33_inc3_1_conflicto_escritorio.png` y 2 más |
| **HIST-3.4** | Ver lo pendiente y desde cuándo | Inc. 3 (`v3.0-Inc3`) | Dado un dispositivo con pendientes, cuando se mira la cabecera o la pestaña «Sincronización», entonces se ve cuántos hay y desde cuándo («1 pendiente(s)»). | **Aprobado** | `tests/e2e/test_inc3_sin_conexion.py`; `HIST34_inc3_1_panel_pendientes_escritorio.png` y 1 más |
| **VIS-3.5** | Visita domiciliaria priorizada | Inc. 3 (`v3.0-Inc3`) | Dado el conjunto de niños en tratamiento, cuando se abre «Visitas», entonces la lista va ordenada por puntaje 0 a 100 con desglose (18 filas, 49,5 a 25,0) y se puede registrar la visita. | **Aprobado** | `tests/unitarias/test_visitas.py`, `tests/integracion/test_api_inc3.py`; `VIS35_inc3_1_visitas_desglose_escritorio.png` y 2 más |
| **HIST-4.1** | Recordatorio de control (SIMULADO) | Inc. 4 (`v4.0-Inc4`) | Dado niños con control próximo o vencido, cuando se generan recordatorios, entonces los 24 mensajes salen rotulados SIMULADO y repetir la generación no duplica. | **Aprobado** | `tests/unitarias/test_recordatorios.py`, `tests/integracion/test_api_inc4.py`; `HIST41_inc4_1_recordatorios_antes_escritorio.png` y 2 más |
| **HIST-4.2** | Confirmación del tutor (personal y webhook firmado) | Inc. 4 (`v4.0-Inc4`) | Dado un recordatorio enviado, cuando el tutor responde 1, 2 o 3 (personal o webhook con firma válida), entonces queda registrada; sin firma o con firma inválida el webhook responde 403. | **Aprobado** | `tests/unitarias/test_recordatorios.py`, `tests/e2e/test_inc4_notificaciones.py`; `HIST42_inc4_1_modal_respuesta_escritorio.png` y 2 más |
| **HIST-4.3** | Barreras de acceso al tratamiento | Inc. 4 (`v4.0-Inc4`) | Dado un niño, cuando se registra una barrera (tipo y detalle), también sin conexión, entonces queda en el expediente y se sincroniza. | **Aprobado** | `tests/unitarias/test_barreras.py`, `tests/integracion/test_api_inc4.py`; `HIST43_inc4_1_modal_barrera_escritorio.png` y 3 más |
| **HIST-4.4** | Alerta de barreras críticas y suma a la visita priorizada | Inc. 4 (`v4.0-Inc4`) | Dado un niño con rechazo o efectos adversos, o 2 o más barreras en 60 días, cuando se abre «Alertas» o «Visitas», entonces hay alerta ALTA y el componente BARRERA_CRITICA en el puntaje (40,0). | **Aprobado** | `tests/unitarias/test_barreras.py`, `tests/integracion/test_api_inc4.py`; `HIST44_inc4_1_alertas_barreras_criticas_escritorio.png` y 2 más |

**Tabla 7.** Resumen del Factor F por incremento (19 escenarios; HIST-3.1b es la verificación del caché dentro del Inc. 3).

| Incremento | Escenarios | Aprobados | % | Capturas |
| --- | --- | --- | --- | --- |
| Inc. 1 — PMV | RF-01, RF-02, RF-03, RF-04, RF-05 | 5/5 | 100 % | 15 |
| Inc. 2 | RF-06, RF-07, RF-08, RF-09 | 4/4 | 100 % | 13 |
| Inc. 3 | HIST-3.1, HIST-3.2, HIST-3.3, HIST-3.4, VIS-3.5, HIST-3.1b | 6/6 | 100 % | 13 |
| Inc. 4 | HIST-4.1, HIST-4.2, HIST-4.3, HIST-4.4 | 4/4 | 100 % | 13 |
| **Total** |  | **19/19** | **100 %** | **54** |

**Tabla 8.** Pruebas automatizadas del repositorio por tipo (pytest; salida en `metricas/salidas/R02_pytest_junit.txt` y `R03_e2e_playwright.txt`).

| Conjunto | Pruebas | Resultado | Comando |
| --- | --- | --- | --- |
| Unitarias (416), integración (219) y arquitectura (25) | 660 | 660 aprobadas, 0 fallas (32 s); cobertura 99,79 % | `python -m pytest --cov=app` (en `pmv_fastapi/`) |
| E2E con Playwright (7 Inc. 3, 4 Inc. 4, 8 + 7 interfaz Inc. 1-2, 2 login) | 28 | 28 aprobadas, 0 fallas (66 s) | `python -m pytest tests/e2e -m e2e` |

![Figura 3. pytest con cobertura: 660 aprobadas, 99,79 % de cobertura (umbral del proyecto 80 %).](evidencias/terminal/R01_pytest_cobertura.png)

**Figura 3.** pytest con cobertura: 660 aprobadas, 99,79 % de cobertura (umbral del proyecto 80 %). Archivo: `evidencias/terminal/R01_pytest_cobertura.png`.

![Figura 4. Detalle de las 660 pruebas unitarias, de integración y de arquitectura (`-rA`): todas aprobadas.](evidencias/terminal/R02_pytest_junit.png)

**Figura 4.** Detalle de las 660 pruebas unitarias, de integración y de arquitectura (`-rA`): todas aprobadas. Archivo: `evidencias/terminal/R02_pytest_junit.png`.

![Figura 5. Pruebas E2E con Playwright: 28 aprobadas.](evidencias/terminal/R03_e2e_playwright.png)

**Figura 5.** Pruebas E2E con Playwright: 28 aprobadas. Archivo: `evidencias/terminal/R03_e2e_playwright.png`.

### 3.2 Capturas por requerimiento e historia (escritorio y móvil)

#### RF-01 — Registro del niño con evaluación inicial (Inc. 1)

Medido: {"tiempo_guardar_ms": 130, "dni_repetido_http": 409}.

![Figura 6. RF-01 (Inc. 1). Formulario de registro con datos sintéticos válidos, escritorio.](evidencias/software/RF01_inc1_1_entrada_escritorio.png)

**Figura 6.** RF-01 (Inc. 1). Formulario de registro con datos sintéticos válidos, escritorio. Archivo: `evidencias/software/RF01_inc1_1_entrada_escritorio.png`.

![Figura 7. RF-01. Confirmación y expediente creado tras «Guardar registro» (130 ms).](evidencias/software/RF01_inc1_2_resultado_escritorio.png)

**Figura 7.** RF-01. Confirmación y expediente creado tras «Guardar registro» (130 ms). Archivo: `evidencias/software/RF01_inc1_2_resultado_escritorio.png`.

![Figura 8. RF-01. Formulario de registro en móvil (390x844).](evidencias/software/RF01_inc1_3_entrada_movil.png)

**Figura 8.** RF-01. Formulario de registro en móvil (390x844). Archivo: `evidencias/software/RF01_inc1_3_entrada_movil.png`.

#### RF-02 — Consulta y actualización del expediente; nuevo control (Inc. 1)

Medido: {"consulta_ms": 82, "patch_ms": 139, "control_ms": 161, "evaluaciones": "2->3"}.

![Figura 9. RF-02 (Inc. 1). Expediente consultado, escritorio.](evidencias/software/RF02_inc1_1_expediente_escritorio.png)

**Figura 9.** RF-02 (Inc. 1). Expediente consultado, escritorio. Archivo: `evidencias/software/RF02_inc1_1_expediente_escritorio.png`.

![Figura 10. RF-02. Edición de campos permitidos del expediente.](evidencias/software/RF02_inc1_2_edicion_escritorio.png)

**Figura 10.** RF-02. Edición de campos permitidos del expediente. Archivo: `evidencias/software/RF02_inc1_2_edicion_escritorio.png`.

![Figura 11. RF-02. Nuevo control agregado: el historial pasa de 2 a 3 evaluaciones.](evidencias/software/RF02_inc1_3_nuevo_control_escritorio.png)

**Figura 11.** RF-02. Nuevo control agregado: el historial pasa de 2 a 3 evaluaciones. Archivo: `evidencias/software/RF02_inc1_3_nuevo_control_escritorio.png`.

![Figura 12. RF-02. Expediente en móvil.](evidencias/software/RF02_inc1_4_expediente_movil.png)

**Figura 12.** RF-02. Expediente en móvil. Archivo: `evidencias/software/RF02_inc1_4_expediente_movil.png`.

#### RF-03 — Validación con reglas clínicas (Inc. 1)

Medido: {"api_validacion_http": 422}.

![Figura 13. RF-03 (Inc. 1). Vista previa de Hb ajustada por altitud y clasificación.](evidencias/software/RF03_inc1_1_vista_previa_escritorio.png)

**Figura 13.** RF-03 (Inc. 1). Vista previa de Hb ajustada por altitud y clasificación. Archivo: `evidencias/software/RF03_inc1_1_vista_previa_escritorio.png`.

![Figura 14. RF-03. Datos inválidos rechazados con mensajes por campo.](evidencias/software/RF03_inc1_2_rechazo_escritorio.png)

**Figura 14.** RF-03. Datos inválidos rechazados con mensajes por campo. Archivo: `evidencias/software/RF03_inc1_2_rechazo_escritorio.png`.

![Figura 15. RF-03. Rechazo con mensajes por campo en móvil.](evidencias/software/RF03_inc1_3_rechazo_movil.png)

**Figura 15.** RF-03. Rechazo con mensajes por campo en móvil. Archivo: `evidencias/software/RF03_inc1_3_rechazo_movil.png`.

#### RF-04 — Listado de niños en seguimiento (Inc. 1)

Medido: {"total": 27, "filtro_moderada": 6}.

![Figura 16. RF-04 (Inc. 1). Listado de seguimiento (27 niños).](evidencias/software/RF04_inc1_1_seguimiento_escritorio.png)

**Figura 16.** RF-04 (Inc. 1). Listado de seguimiento (27 niños). Archivo: `evidencias/software/RF04_inc1_1_seguimiento_escritorio.png`.

![Figura 17. RF-04. Filtro por clasificación «Moderada» (6 niños).](evidencias/software/RF04_inc1_2_filtro_moderada_escritorio.png)

**Figura 17.** RF-04. Filtro por clasificación «Moderada» (6 niños). Archivo: `evidencias/software/RF04_inc1_2_filtro_moderada_escritorio.png`.

![Figura 18. RF-04. Seguimiento en móvil.](evidencias/software/RF04_inc1_3_seguimiento_movil.png)

**Figura 18.** RF-04. Seguimiento en móvil. Archivo: `evidencias/software/RF04_inc1_3_seguimiento_movil.png`.

#### RF-05 — Reporte del periodo en JSON y CSV (Inc. 1)

Medido: {"tiempo_ms": 86, "registrados": 28, "csv_lineas": 43}.

![Figura 19. RF-05 (Inc. 1). Reporte del periodo con indicadores y descarga CSV (86 ms).](evidencias/software/RF05_inc1_1_reporte_escritorio.png)

**Figura 19.** RF-05 (Inc. 1). Reporte del periodo con indicadores y descarga CSV (86 ms). Archivo: `evidencias/software/RF05_inc1_1_reporte_escritorio.png`.

![Figura 20. RF-05. Reporte en móvil.](evidencias/software/RF05_inc1_2_reporte_movil.png)

**Figura 20.** RF-05. Reporte en móvil. Archivo: `evidencias/software/RF05_inc1_2_reporte_movil.png`.

#### RF-06 — Agenda de controles según la normativa (Inc. 2)

Medido: {"controles": 13, "C1M/C3M/C6M": ["CUMPLIDO", "VENCIDO", "PENDIENTE"]}.

![Figura 21. RF-06 (Inc. 2). Agenda normativa de 13 controles en el expediente.](evidencias/software/RF06_inc2_1_agenda_expediente_escritorio.png)

**Figura 21.** RF-06 (Inc. 2). Agenda normativa de 13 controles en el expediente. Archivo: `evidencias/software/RF06_inc2_1_agenda_expediente_escritorio.png`.

![Figura 22. RF-06. Agenda del expediente en móvil.](evidencias/software/RF06_inc2_2_agenda_expediente_movil.png)

**Figura 22.** RF-06. Agenda del expediente en móvil. Archivo: `evidencias/software/RF06_inc2_2_agenda_expediente_movil.png`.

#### RF-07 — Controles vencidos y alertas priorizadas (Inc. 2)

Medido: {"vencidos": 9, "por_prioridad": {"ALTA": 7, "MEDIA": 1, "BAJA": 1}}.

![Figura 23. RF-07 (Inc. 2). Alertas de controles vencidos priorizadas (9 vencidos).](evidencias/software/RF07_inc2_1_alertas_escritorio.png)

**Figura 23.** RF-07 (Inc. 2). Alertas de controles vencidos priorizadas (9 vencidos). Archivo: `evidencias/software/RF07_inc2_1_alertas_escritorio.png`.

![Figura 24. RF-07. Filtro por prioridad MEDIA.](evidencias/software/RF07_inc2_2_filtro_media_escritorio.png)

**Figura 24.** RF-07. Filtro por prioridad MEDIA. Archivo: `evidencias/software/RF07_inc2_2_filtro_media_escritorio.png`.

![Figura 25. RF-07. Alertas en móvil.](evidencias/software/RF07_inc2_3_alertas_movil.png)

**Figura 25.** RF-07. Alertas en móvil. Archivo: `evidencias/software/RF07_inc2_3_alertas_movil.png`.

#### RF-08 — Agenda del personal por rango de fechas (Inc. 2)

Medido: {"resumen_30d": {"total": 17, "cumplidos": 5, "pendientes": 12, "vencidos": 0, "con_inasistencia": 0, "ninos": 14}}.

![Figura 26. RF-08 (Inc. 2). Agenda del personal de la semana.](evidencias/software/RF08_inc2_1_agenda_semana_escritorio.png)

**Figura 26.** RF-08 (Inc. 2). Agenda del personal de la semana. Archivo: `evidencias/software/RF08_inc2_1_agenda_semana_escritorio.png`.

![Figura 27. RF-08. Agenda de 30 días (17 controles, 14 niños).](evidencias/software/RF08_inc2_2_agenda_30_dias_escritorio.png)

**Figura 27.** RF-08. Agenda de 30 días (17 controles, 14 niños). Archivo: `evidencias/software/RF08_inc2_2_agenda_30_dias_escritorio.png`.

![Figura 28. RF-08. Rango mayor de 31 días rechazado.](evidencias/software/RF08_inc2_3_rango_invalido_escritorio.png)

**Figura 28.** RF-08. Rango mayor de 31 días rechazado. Archivo: `evidencias/software/RF08_inc2_3_rango_invalido_escritorio.png`.

![Figura 29. RF-08. Agenda del personal en móvil.](evidencias/software/RF08_inc2_4_agenda_movil.png)

**Figura 29.** RF-08. Agenda del personal en móvil. Archivo: `evidencias/software/RF08_inc2_4_agenda_movil.png`.

#### RF-09 — Registro de asistencia a un control (Inc. 2)

Medido: {"vencidos_antes": 9, "vencidos_despues": 8}.

![Figura 30. RF-09 (Inc. 2). Modal «No asistió» con motivo.](evidencias/software/RF09_inc2_1_modal_inasistencia_escritorio.png)

**Figura 30.** RF-09 (Inc. 2). Modal «No asistió» con motivo. Archivo: `evidencias/software/RF09_inc2_1_modal_inasistencia_escritorio.png`.

![Figura 31. RF-09. Inasistencia registrada y prioridad actualizada.](evidencias/software/RF09_inc2_2_inasistencia_registrada_escritorio.png)

**Figura 31.** RF-09. Inasistencia registrada y prioridad actualizada. Archivo: `evidencias/software/RF09_inc2_2_inasistencia_registrada_escritorio.png`.

![Figura 32. RF-09. Registro de «Asistió» desde la agenda.](evidencias/software/RF09_inc2_3_asistio_desde_agenda_escritorio.png)

**Figura 32.** RF-09. Registro de «Asistió» desde la agenda. Archivo: `evidencias/software/RF09_inc2_3_asistio_desde_agenda_escritorio.png`.

![Figura 33. RF-09. Agenda con asistencia en móvil.](evidencias/software/RF09_inc2_4_agenda_movil.png)

**Figura 33.** RF-09. Agenda con asistencia en móvil. Archivo: `evidencias/software/RF09_inc2_4_agenda_movil.png`.

#### HIST-3.1 — Registro sin conexión (cola en el dispositivo) (Inc. 3)

Medido: {"pendientes": 2, "servidor_sin_registro": true}.

![Figura 34. HIST-3.1 (Inc. 3). Aplicación en línea antes de perder la conexión.](evidencias/software/HIST31_inc3_1_en_linea_escritorio.png)

**Figura 34.** HIST-3.1 (Inc. 3). Aplicación en línea antes de perder la conexión. Archivo: `evidencias/software/HIST31_inc3_1_en_linea_escritorio.png`.

![Figura 35. HIST-3.1. Sin conexión: 2 operaciones pendientes en el dispositivo; el servidor no las tiene.](evidencias/software/HIST31_inc3_2_pendientes_sin_conexion_escritorio.png)

**Figura 35.** HIST-3.1. Sin conexión: 2 operaciones pendientes en el dispositivo; el servidor no las tiene. Archivo: `evidencias/software/HIST31_inc3_2_pendientes_sin_conexion_escritorio.png`.

#### HIST-3.1b — Apertura sin conexión desde el caché (servidor detenido) (Inc. 3)

Medido: {"filas_en_linea": 30, "filas_desde_cache": 30, "servidor_detenido": true}.

![Figura 36. HIST-3.1b. Recarga con el servidor detenido: la aplicación abre desde el caché con aviso.](evidencias/software/HIST31_inc3_3_recarga_sin_conexion_escritorio.png)

**Figura 36.** HIST-3.1b. Recarga con el servidor detenido: la aplicación abre desde el caché con aviso. Archivo: `evidencias/software/HIST31_inc3_3_recarga_sin_conexion_escritorio.png`.

#### HIST-3.2 — Sincronización idempotente al reconectar (Inc. 3)

Medido: {"primer_envio": ["APLICADA"], "segundo_envio": ["DUPLICADA"], "evaluaciones_tras_reenvio": 3}.

![Figura 37. HIST-3.2 (Inc. 3). Panel de sincronización con pendientes, antes de enviar.](evidencias/software/HIST32_inc3_1_panel_antes_de_sincronizar_escritorio.png)

**Figura 37.** HIST-3.2 (Inc. 3). Panel de sincronización con pendientes, antes de enviar. Archivo: `evidencias/software/HIST32_inc3_1_panel_antes_de_sincronizar_escritorio.png`.

![Figura 38. HIST-3.2. Operaciones aplicadas; el reenvío se marca DUPLICADA y no duplica datos.](evidencias/software/HIST32_inc3_2_sincronizado_escritorio.png)

**Figura 38.** HIST-3.2. Operaciones aplicadas; el reenvío se marca DUPLICADA y no duplica datos. Archivo: `evidencias/software/HIST32_inc3_2_sincronizado_escritorio.png`.

#### HIST-3.3 — Resolución de conflictos sin sobrescribir a ciegas (Inc. 3)

Medido: {"conflictos_resueltos": 1}.

![Figura 39. HIST-3.3 (Inc. 3). Conflicto pendiente: dato distinto en el servidor.](evidencias/software/HIST33_inc3_1_conflicto_escritorio.png)

**Figura 39.** HIST-3.3 (Inc. 3). Conflicto pendiente: dato distinto en el servidor. Archivo: `evidencias/software/HIST33_inc3_1_conflicto_escritorio.png`.

![Figura 40. HIST-3.3. Conflicto resuelto conservando el dato del servidor.](evidencias/software/HIST33_inc3_2_conflicto_resuelto_escritorio.png)

**Figura 40.** HIST-3.3. Conflicto resuelto conservando el dato del servidor. Archivo: `evidencias/software/HIST33_inc3_2_conflicto_resuelto_escritorio.png`.

![Figura 41. HIST-3.3. Panel de sincronización en móvil.](evidencias/software/HIST33_inc3_3_panel_movil.png)

**Figura 41.** HIST-3.3. Panel de sincronización en móvil. Archivo: `evidencias/software/HIST33_inc3_3_panel_movil.png`.

#### HIST-3.4 — Ver lo pendiente y desde cuándo (Inc. 3)

Medido: {"resumen_con_pendientes": "1 pendiente(s)"}.

![Figura 42. HIST-3.4 (Inc. 3). Cantidad de pendientes y desde cuándo.](evidencias/software/HIST34_inc3_1_panel_pendientes_escritorio.png)

**Figura 42.** HIST-3.4 (Inc. 3). Cantidad de pendientes y desde cuándo. Archivo: `evidencias/software/HIST34_inc3_1_panel_pendientes_escritorio.png`.

![Figura 43. HIST-3.4. Panel «al día» sin pendientes.](evidencias/software/HIST34_inc3_2_panel_al_dia_escritorio.png)

**Figura 43.** HIST-3.4. Panel «al día» sin pendientes. Archivo: `evidencias/software/HIST34_inc3_2_panel_al_dia_escritorio.png`.

#### VIS-3.5 — Visita domiciliaria priorizada (Inc. 3)

Medido: {"filas": 18, "puntaje_max": 49.5, "puntaje_min": 25.0}.

![Figura 44. VIS-3.5 (Inc. 3). Visitas ordenadas por puntaje 0-100 con desglose por componente.](evidencias/software/VIS35_inc3_1_visitas_desglose_escritorio.png)

**Figura 44.** VIS-3.5 (Inc. 3). Visitas ordenadas por puntaje 0-100 con desglose por componente. Archivo: `evidencias/software/VIS35_inc3_1_visitas_desglose_escritorio.png`.

![Figura 45. VIS-3.5. Registro de la visita domiciliaria.](evidencias/software/VIS35_inc3_2_modal_visita_escritorio.png)

**Figura 45.** VIS-3.5. Registro de la visita domiciliaria. Archivo: `evidencias/software/VIS35_inc3_2_modal_visita_escritorio.png`.

![Figura 46. VIS-3.5. Visitas priorizadas en móvil.](evidencias/software/VIS35_inc3_3_visitas_movil.png)

**Figura 46.** VIS-3.5. Visitas priorizadas en móvil. Archivo: `evidencias/software/VIS35_inc3_3_visitas_movil.png`.

#### HIST-4.1 — Recordatorio de control (SIMULADO) (Inc. 4)

Medido: {"recordatorios": 24, "todos_simulados": true, "segunda_generacion_duplica": false}.

![Figura 47. HIST-4.1 (Inc. 4). Recordatorios antes de generarlos.](evidencias/software/HIST41_inc4_1_recordatorios_antes_escritorio.png)

**Figura 47.** HIST-4.1 (Inc. 4). Recordatorios antes de generarlos. Archivo: `evidencias/software/HIST41_inc4_1_recordatorios_antes_escritorio.png`.

![Figura 48. HIST-4.1. 24 recordatorios rotulados SIMULADO.](evidencias/software/HIST41_inc4_2_recordatorios_simulados_escritorio.png)

**Figura 48.** HIST-4.1. 24 recordatorios rotulados SIMULADO. Archivo: `evidencias/software/HIST41_inc4_2_recordatorios_simulados_escritorio.png`.

![Figura 49. HIST-4.1. Recordatorios en móvil.](evidencias/software/HIST41_inc4_3_recordatorios_movil.png)

**Figura 49.** HIST-4.1. Recordatorios en móvil. Archivo: `evidencias/software/HIST41_inc4_3_recordatorios_movil.png`.

#### HIST-4.2 — Confirmación del tutor (personal y webhook firmado) (Inc. 4)

Medido: {"webhook_sin_firma": 403, "webhook_firma_invalida": 403, "webhook_firma_valida": 200, "webhook_respuesta": {"estados_aplicados": 0, "respuestas_registradas": 0, "ignorados": 1}, "verificacion_get": "777"}.

![Figura 50. HIST-4.2 (Inc. 4). Modal de respuesta del tutor (1 confirmo, 2 no puedo, 3 reprogramar).](evidencias/software/HIST42_inc4_1_modal_respuesta_escritorio.png)

**Figura 50.** HIST-4.2 (Inc. 4). Modal de respuesta del tutor (1 confirmo, 2 no puedo, 3 reprogramar). Archivo: `evidencias/software/HIST42_inc4_1_modal_respuesta_escritorio.png`.

![Figura 51. HIST-4.2. Respuesta registrada por el personal.](evidencias/software/HIST42_inc4_2_respuesta_registrada_escritorio.png)

**Figura 51.** HIST-4.2. Respuesta registrada por el personal. Archivo: `evidencias/software/HIST42_inc4_2_respuesta_registrada_escritorio.png`.

![Figura 52. HIST-4.2. Estado tras el webhook con firma válida (sin firma o firma inválida: 403).](evidencias/software/HIST42_inc4_3_tras_webhook_escritorio.png)

**Figura 52.** HIST-4.2. Estado tras el webhook con firma válida (sin firma o firma inválida: 403). Archivo: `evidencias/software/HIST42_inc4_3_tras_webhook_escritorio.png`.

#### HIST-4.3 — Barreras de acceso al tratamiento (Inc. 4)

Medido: {"barreras": [["TRANSPORTE", "PERSONAL"]]}.

![Figura 53. HIST-4.3 (Inc. 4). Modal de barrera de acceso al tratamiento.](evidencias/software/HIST43_inc4_1_modal_barrera_escritorio.png)

**Figura 53.** HIST-4.3 (Inc. 4). Modal de barrera de acceso al tratamiento. Archivo: `evidencias/software/HIST43_inc4_1_modal_barrera_escritorio.png`.

![Figura 54. HIST-4.3. Barrera registrada sin conexión, pendiente de sincronizar.](evidencias/software/HIST43_inc4_2_barrera_pendiente_sin_conexion_escritorio.png)

**Figura 54.** HIST-4.3. Barrera registrada sin conexión, pendiente de sincronizar. Archivo: `evidencias/software/HIST43_inc4_2_barrera_pendiente_sin_conexion_escritorio.png`.

![Figura 55. HIST-4.3. Barrera sincronizada en el expediente.](evidencias/software/HIST43_inc4_3_barrera_sincronizada_escritorio.png)

**Figura 55.** HIST-4.3. Barrera sincronizada en el expediente. Archivo: `evidencias/software/HIST43_inc4_3_barrera_sincronizada_escritorio.png`.

![Figura 56. HIST-4.3. Barrera en móvil.](evidencias/software/HIST43_inc4_4_barrera_movil.png)

**Figura 56.** HIST-4.3. Barrera en móvil. Archivo: `evidencias/software/HIST43_inc4_4_barrera_movil.png`.

#### HIST-4.4 — Alerta de barreras críticas y suma a la visita priorizada (Inc. 4)

Medido: {"componentes": ["SEVERIDAD", "CONTROL_VENCIDO", "INASISTENCIAS", "ULTIMA_VISITA", "BARRERA_CRITICA"], "puntaje": 40.0}.

![Figura 57. HIST-4.4 (Inc. 4). Alertas de barreras críticas.](evidencias/software/HIST44_inc4_1_alertas_barreras_criticas_escritorio.png)

**Figura 57.** HIST-4.4 (Inc. 4). Alertas de barreras críticas. Archivo: `evidencias/software/HIST44_inc4_1_alertas_barreras_criticas_escritorio.png`.

![Figura 58. HIST-4.4. Visita priorizada con el componente BARRERA_CRITICA (puntaje 40,0).](evidencias/software/HIST44_inc4_2_visita_con_barrera_critica_escritorio.png)

**Figura 58.** HIST-4.4. Visita priorizada con el componente BARRERA_CRITICA (puntaje 40,0). Archivo: `evidencias/software/HIST44_inc4_2_visita_con_barrera_critica_escritorio.png`.

![Figura 59. HIST-4.4. Alertas de barreras en móvil.](evidencias/software/HIST44_inc4_3_alertas_barreras_movil.png)

**Figura 59.** HIST-4.4. Alertas de barreras en móvil. Archivo: `evidencias/software/HIST44_inc4_3_alertas_barreras_movil.png`.

## 4. EVALUACIÓN DE FACTORES URPS: NO FUNCIONALES CLAVE (Actividad 3)

### 4.1 Factor U — Usabilidad: psicología de colores y accesibilidad WCAG 2.1 AA

#### A. Psicología de colores aplicada al dominio (salud infantil)

La paleta sale de las variables `:root` de `pmv_fastapi/app/web/estilos.css` (líneas 1 a 6). Las razones de contraste se calcularon con la fórmula de WCAG 2.1 ((L1+0,05)/(L2+0,05)) en `metricas/paleta_colores.py`.

**Tabla 9.** Matriz 3.1 A. Roles de color, código hexadecimal, justificación en el dominio y consistencia medida en la interfaz.

| Rol de color | Hexadecimal | Significado y justificación en salud infantil | Contraste medido | Consistencia UI |
| --- | --- | --- | --- | --- |
| Primario (dominante) | `#1F4E79` (azul) | Confianza, calma clínica y estabilidad con datos de salud: cabecera, títulos y acciones primarias | 8,66:1 sobre blanco | **Conforme** |
| Secundario (acento) | `#2E5C8A` (azul-2) | Variante del primario para subtítulos y enlaces | 6,97:1 sobre blanco | **Conforme** |
| Neutro / fondo | `#F4F7FB` | Gris azulado claro: reduce el brillo y la fatiga en jornadas largas; las tarjetas blancas resaltan | Texto `#1B2B3A` 13,45:1 sobre este fondo | **Conforme** |
| Éxito / sin anemia | `#1F7A3D` (verde) | Salud, control cumplido, estado operativo seguro | 5,37:1 blanco; 4,70:1 sobre `#E3F4E8` | **Conforme** |
| Precaución / leve | `#8A6200` (ámbar) | Atención sin urgencia: anemia leve, por vencer, simulado | 5,49:1 blanco; 4,99:1 sobre `#FFF4D1` | **Conforme** |
| Advertencia / moderada | `#B4530B` (naranja) | Riesgo creciente: anemia moderada, prioridad media, pendiente de sincronizar | 5,02:1 blanco; **4,23:1 sobre `#FDE8D7`** | **Observación**: no llega a 4,5:1 sobre su fondo suave |
| Alerta / severa | `#B0222B` (rojo) | Acción inmediata: anemia severa, control vencido, prioridad alta, conflicto, errores | 6,75:1 blanco; 5,46:1 sobre `#FBE1E3` | **Conforme** |

![Figura 60. Paleta real de la interfaz con muestras, hexadecimales, contraste y significado.](evidencias/usabilidad/U_paleta_colores.png)

**Figura 60.** Paleta real de la interfaz con muestras, hexadecimales, contraste y significado. Archivo: `evidencias/usabilidad/U_paleta_colores.png`.

![Figura 61. Semáforo de severidad bajo simulación de deuteranopía, protanopía y escala de grises (matrices de Machado). El texto de cada estado se conserva; los tonos moderada y severa se acercan, por eso el color nunca es el único canal.](evidencias/usabilidad/U_semaforo_severidad_daltonismo.png)

**Figura 61.** Semáforo de severidad bajo simulación de deuteranopía, protanopía y escala de grises (matrices de Machado). El texto de cada estado se conserva; los tonos moderada y severa se acercan, por eso el color nunca es el único canal. Archivo: `evidencias/usabilidad/U_semaforo_severidad_daltonismo.png`.

**Evaluación.** El rojo-naranja-ámbar-verde ordena el riesgo en el sentido que el personal de salud ya conoce. De 54 pares texto/fondo medidos (23 combinaciones únicas de color), el único que incumple 1.4.3 es naranja sobre naranja suave (4,23:1; lo usan las insignias «Anemia moderada», prioridad MEDIA, control LOCAL/INASISTENCIA/BARRERA y el indicador de pendientes). El semáforo también se codifica con texto en las 482 insignias de estado evaluadas (0 sin texto), cumpliendo 1.4.1. Acción propuesta, calculada y no aplicada: `--naranja` de `#B4530B` a `#A34A09` (5,00:1 sobre `#FDE8D7`; 5,93:1 sobre blanco).

**Tabla 10.** Contraste de componentes no textuales (WCAG 1.4.11, umbral 3:1).

| Componente | Colores | Razón | Estado |
| --- | --- | --- | --- |
| borde de campos (--borde) sobre blanco | `#D7E0EA` sobre `#FFFFFF` | 1.33:1 | **No cumple** |
| borde de boton secundario (#A9C4E2) sobre blanco | `#A9C4E2` sobre `#FFFFFF` | 1.8:1 | **No cumple** |
| contorno de foco de campos (#9CC3EA) sobre blanco | `#9CC3EA` sobre `#FFFFFF` | 1.84:1 | **No cumple** |
| barra SIN_ANEMIA del grafico | `#1F7A3D` sobre `#EEF2F6` | 4.77:1 | Cumple |
| barra LEVE del grafico (#C99200) | `#C99200` sobre `#EEF2F6` | 2.46:1 | **No cumple** |
| barra MODERADA del grafico (#D26A1B) | `#D26A1B` sobre `#EEF2F6` | 3.21:1 | Cumple |
| barra SEVERA del grafico | `#B0222B` sobre `#EEF2F6` | 6.0:1 | Cumple |
| barra NO_APLICA del grafico (#8C99A6) | `#8C99A6` sobre `#EEF2F6` | 2.58:1 | **No cumple** |

Propuesta calculada (no aplicada): borde de campos `#8795A5` (3,06:1), contorno de foco `#2E5C8A` (6,97:1), barra LEVE `#8A6200` (4,88:1), barra NO_APLICA `#707E8C` (3,69:1). Hasta corregirlo, las barras del gráfico de Hb se acompañan de etiqueta de texto.

![Figura 62. Salida de `paleta_colores.py`: razón de contraste de los 54 pares de texto y de 8 componentes.](evidencias/terminal/U01_paleta_contraste.png)

**Figura 62.** Salida de `paleta_colores.py`: razón de contraste de los 54 pares de texto y de 8 componentes. Archivo: `evidencias/terminal/U01_paleta_contraste.png`.

![Figura 63. Paleta definida en el repositorio (variables CSS).](evidencias/github/GH_paleta_estilos_css.png)

**Figura 63.** Paleta definida en el repositorio (variables CSS). Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_paleta_estilos_css.png`.

#### B. Accesibilidad e inclusión (WCAG 2.1 / 2.2 nivel AA)

**Tabla 11.** Matriz 3,1 B. Criterios WCAG evaluados, resultado medido y estado. Herramientas: axe-core 4.14.0 (reglas wcag2a, wcag2aa, wcag21a, wcag21aa), Playwright y cálculo propio.

| Criterio WCAG | Pauta evaluada | Resultado medido / herramienta | Estado |
| --- | --- | --- | --- |
| **1.4.3** Contraste (mínimo) | Texto normal ≥ 4,5:1 | 22 de 23 pares únicos cumplen (mín. 4,23:1, máx. 14,45:1). axe `color-contrast`: 25 nodos en 5 pantallas, mismo par naranja | **Parcial** |
| **1.4.11** Contraste no textual | Bordes, foco y gráficos ≥ 3:1 | 3 de 8 componentes (borde de campo 1,33:1; foco 1,84:1; barras LEVE 2,46:1 y NO_APLICA 2,58:1) | **No cumple** |
| **1.4.1** Uso del color | El color no es el único canal | 482 de 482 insignias de estado con texto; ver semáforo simulado | **Cumple** |
| **1.4.10** Reflujo | Sin desplazamiento horizontal a 320 px | 13 de 13 pantallas sin desborde | **Cumple** |
| **1.3.1 / 4.1.2** Estructura y nombre, rol, valor | Roles ARIA válidos; controles con nombre | axe: `aria-required-children` (nav con `role=tablist` sin `role=tab`) en 13 de 14 pantallas por vista; `label` 12 nodos en 3 pantallas; `select-name` 2 nodos (escritorio) y 15 (móvil) | **No cumple** |
| **2.1.1 / 2.1.3** Teclado | Todo operable con teclado | Tab recorre 29 elementos distintos en 56 paradas con ciclo completo; registro con Enter en «Guardar»; modal abre con Enter y cierra con Esc. axe `scrollable-region-focusable`: 3 regiones con desplazamiento en 2 pantallas móviles no son alcanzables por teclado | **Parcial** |
| **2.4.3 / 2.4.7** Orden y foco visible | Foco visible y devuelto | Todos los elementos muestran indicador de foco (0 sin indicador), pero el modal no retiene el foco (Tab escapa del diálogo 10 de 14 veces) y al cerrar el foco queda en `body` | **Parcial** |
| **2.5.8** Tamaño del objetivo (WCAG 2.2, mínimo 24 px) | Objetivos táctiles ≥ 24x24 px | 734 de 924 objetivos evaluados cumplen (escritorio+móvil). Menores: `#sync-indicador` 59x22, `#insignia-alertas` 31x20, enlaces de agenda 17 px de alto, botones de puntaje | **Parcial** |
| **4.1.2** Compatibilidad con lectores de pantalla | NVDA / TalkBack | **No medido**: no hay lector de pantalla en el entorno. axe valida solo la estructura (ver 1.3.1/4.1.2) | **No medido** |

**Tabla 12.** axe-core por pantalla: violaciones por vista (reglas violadas / nodos). Una pantalla sin violaciones es «Inicio de sesión»; las demás repiten el mismo patrón de la barra de pestañas.

| Pantalla | Escritorio (reglas / nodos) | Móvil (reglas / nodos) | Reglas aprobadas (escritorio) | Reglas aprobadas (móvil) |
| --- | --- | --- | --- | --- |
| Registrar niño | 1 / 1 | 2 / 2 | 18 | 19 |
| Seguimiento | 3 / 7 | 4 / 9 | 20 | 20 |
| Expediente | 2 / 5 | 3 / 6 | 28 | 27 |
| Agenda | 2 / 12 | 3 / 13 | 20 | 21 |
| Visitas | 2 / 5 | 3 / 6 | 19 | 20 |
| Recordatorios | 1 / 1 | 2 / 2 | 19 | 20 |
| Alertas | 2 / 3 | 4 / 6 | 20 | 21 |
| Sincronización | 1 / 1 | 2 / 2 | 19 | 19 |
| Reporte | 1 / 1 | 2 / 2 | 20 | 20 |
| Modal asistencia | 2 / 5 | 3 / 6 | 28 | 28 |
| Modal visita | 2 / 5 | 3 / 6 | 25 | 26 |
| Modal respuesta del tutor | 1 / 1 | 2 / 2 | 24 | 25 |
| Modal barrera | 2 / 5 | 3 / 6 | 28 | 28 |
| Inicio de sesión | 0 / 0 | 0 / 0 | 22 | 22 |
| **Total** | **22 / 52** | **36 / 68** | 310 | 316 |

![Figura 64. Resumen de axe-core por pantalla y vista (14 pantallas incluyendo 4 modales y el inicio de sesión).](evidencias/usabilidad/U_axe_resumen_pantallas.png)

**Figura 64.** Resumen de axe-core por pantalla y vista (14 pantallas incluyendo 4 modales y el inicio de sesión). Archivo: `evidencias/usabilidad/U_axe_resumen_pantallas.png`.

![Figura 65. Salida de `accesibilidad.py`: axe, reflujo a 320 px, teclado y objetivos táctiles.](evidencias/terminal/U02_accesibilidad.png)

**Figura 65.** Salida de `accesibilidad.py`: axe, reflujo a 320 px, teclado y objetivos táctiles. Archivo: `evidencias/terminal/U02_accesibilidad.png`.

**Tabla 13.** Hallazgos de accesibilidad y acción propuesta (ninguna aplicada en el código).

| N.° | Hallazgo | Criterio | Gravedad axe | Acción propuesta |
| --- | --- | --- | --- | --- |
| U-1 | `<nav role="tablist">` contiene `<button>` sin `role="tab"` | 1.3.1 / 4.1.2 | critical (13 pantallas) | Agregar `role="tab"`, `aria-selected` y `aria-controls`, o quitar `role="tablist"` y usar `<nav>` con botones |
| U-2 | Campos `select` y `input[type=date]` del filtro sin etiqueta asociada | 4.1.2 / 3.3.2 | critical | Agregar `<label for>` o `aria-label` a cada control de filtro |
| U-3 | Naranja `#B4530B` sobre `#FDE8D7` = 4,23:1 | 1.4.3 | serious (25 nodos) | Cambiar `--naranja` a `#A34A09` (5,00:1) |
| U-4 | Bordes de campo 1,33:1, foco 1,84:1, barras LEVE y NO_APLICA bajo 3:1 | 1.4.11 | no detecta axe (medido) | Usar `#8795A5`, `#2E5C8A`, `#8A6200` y `#707E8C` |
| U-5 | El modal no retiene el foco ni lo devuelve al botón que lo abrió | 2.4.3 | no detecta axe (medido) | Usar `<dialog>` con `showModal()` o atrapar Tab y restaurar el foco al cerrar |
| U-6 | Regiones con desplazamiento sin acceso por teclado (móvil) | 2.1.1 | serious (3 nodos) | Agregar `tabindex="0"` y nombre accesible a los contenedores de tabla |
| U-7 | Objetivos menores de 24 px (`#sync-indicador`, `#insignia-alertas`, enlaces de agenda, botones de puntaje) | 2.5.8 | no detecta axe (medido) | Aumentar a `min-height: 24px` (idealmente 44 px en móvil) |
| U-8 | El aviso emergente (toast) no tiene `role="status"` ni `aria-live` | 4.1.3 | no medido por axe (revisión del código) | Agregar `role="status"` y `aria-live="polite"` al contenedor |

![Figura 66. Foco visible al recorrer las pestañas con Tab.](evidencias/usabilidad/U_teclado_foco_pestana.png)

**Figura 66.** Foco visible al recorrer las pestañas con Tab. Archivo: `evidencias/usabilidad/U_teclado_foco_pestana.png`.

![Figura 67. Foco visible en un campo de formulario (contorno `#9CC3EA`, 1,84:1 sobre blanco).](evidencias/usabilidad/U_teclado_foco_campo.png)

**Figura 67.** Foco visible en un campo de formulario (contorno `#9CC3EA`, 1,84:1 sobre blanco). Archivo: `evidencias/usabilidad/U_teclado_foco_campo.png`.

![Figura 68. Pantalla de inicio de sesión, escritorio (axe: 0 violaciones).](evidencias/usabilidad/U_login_escritorio.png)

**Figura 68.** Pantalla de inicio de sesión, escritorio (axe: 0 violaciones). Archivo: `evidencias/usabilidad/U_login_escritorio.png`.

![Figura 69. Pantalla de inicio de sesión, móvil (axe: 0 violaciones).](evidencias/usabilidad/U_login_movil.png)

**Figura 69.** Pantalla de inicio de sesión, móvil (axe: 0 violaciones). Archivo: `evidencias/usabilidad/U_login_movil.png`.

**No medido en este factor:** pruebas con lectores de pantalla (NVDA/TalkBack), prueba de usabilidad con usuarios (SUS) y tiempo de tarea de personal real. La usabilidad percibida no tiene medición; solo la accesibilidad técnica.

### 4.2 Factores R (Confiabilidad) y P (Rendimiento)

Entorno de medición: una sola máquina virtual, un único proceso uvicorn, SQLite (Locust) o PostgreSQL 16 temporal (caos), datos sintéticos. **No son valores de producción**: sirven para comparar con el umbral y detectar brechas. Locust reemplaza a k6/JMeter de la guía. Los dos locustfile son `pmv_fastapi/tests/rendimiento/locustfile.py` (Inc. 1 y 2, del repositorio) y `metricas/locustfile_inc3_inc4.py` (Inc. 3 y 4, creado para esta medición).

**Tabla 14.** Matriz 3.2 (R y P). Valores medidos con scripts de `metricas/`.

| Factor | Atributo | Requerimiento no funcional | Método de extracción | Valor medido | Estado |
| --- | --- | --- | --- | --- | --- |
| **R** | Tolerancia a fallas (BD) | Recuperarse sin reiniciar la aplicación tras caer la base de datos | Caos: `kill -9` del árbol de procesos de un PostgreSQL 16 temporal (7 procesos), reinicio a los 5 s; sondeo cada 100 ms (`caos_postgres.py`) | La aplicación siguió viva y respondió 200 a los 0,2 s de volver la BD (`pool_pre_ping`). **Durante la caída 25 de 26 peticiones respondieron 500** (no 503); `/api/salud` respondió 200 en 26 de 26 | **Cumple** la reconexión; **No cumple** la respuesta controlada |
| **R** | MTTR | Restablecer el servicio < 5 min | `kill -9` del servidor y reinicio con el mismo comando (`rendimiento.py`) | 0,85 s hasta `/api/salud` 200; 329 niños antes y 329 después | **Cumple** (reinicio manual; el orquestador no se midió) |
| **R** | Disponibilidad | ≥ 99,5 % durante la carga | Sondeo de `/api/salud` cada 0,5 s durante las 3 corridas de Locust | 100 % (332 sondeos, 0 fallidos) | **Cumple** (solo durante 3 min de carga) |
| **R** | Disponibilidad en staging | Uptime del entorno de pruebas (Render/AWS) | No existe entorno de staging desplegado | — | **No medido** |
| **R** | Operación sin red | Abrir y leer sin servidor | Playwright con el servidor detenido (`HIST-3.1b`) | 30 de 30 filas servidas desde el caché del service worker | **Cumple** |
| **P** | Latencia REST, 20 usuarios | p95 < 800 ms | Locust 20 usuarios, 60 s; Inc. 1-2 y Inc. 3-4 | p95 29 ms y 98 ms (p50 10 y 9 ms) | **Cumple** |
| **P** | Latencia REST, 100 usuarios | p95 < 800 ms | Locust 100 usuarios, 60 s, Inc. 1-2 | p95 2000 ms, p50 780 ms, p99 2600 ms | **No cumple** |
| **P** | Latencia REST, 500 usuarios | p95 < 800 ms (meta de la guía) | No ejecutado (máximo probado: 100 usuarios) | — | **No medido** |
| **P** | Rendimiento (RPS) | Peticiones por segundo | Locust | 16.16 y 15,84 req/s con 20 usuarios; 49,29 req/s con 100 usuarios (bucle cerrado con espera entre tareas) | Informativo (sin meta) |
| **P** | Memoria | RSS del proceso uvicorn | Muestreo de `/proc` durante la carga | 81.4 a 117,8 MB | Informativo (sin meta) |
| **P** | Carga de la PWA (cliente) | LCP < 2500 ms en móvil lento | Playwright, 390x844, CPU x4, 1,6 Mbps, 150 ms, 5 repeticiones (`rendimiento_cliente.py`) | Primera carga: LCP 468 ms, 142 kB, 11 recursos. Segunda carga con service worker: LCP 84 ms, 302 B por red | **Cumple** |

**Tabla 15.** Resultados de Locust por corrida (60 s cada una; salida en `metricas/salidas/P_resumen.json`).

| Corrida | Usuarios | Peticiones | Fallos | p50 (ms) | p95 (ms) | p99 (ms) | RPS | Disponibilidad | RSS (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_inc1_inc2_20u | 20 | 953 | 0 (0,0 %) | 10 | 29 | 91 | 16.16 | 100,0 % | 81.4 a 88.1 |
| B_inc3_inc4_20u | 20 | 934 | 0 (0,0 %) | 9 | 98 | 300 | 15.84 | 100,0 % | 88.1 a 93.6 |
| C_inc1_inc2_100u | 100 | 2904 | 1 (0,034 %) | 780 | 2000 | 2600 | 49.29 | 100,0 % | 93.6 a 117.8 |

El único fallo de la corrida C es un 409 por DNI duplicado que genera el propio script de carga (no es un error del servidor). Con 100 usuarios el p95 pasa de 29 a 2000 ms y los endpoints más lentos son `POST /api/ninos` (p95 2500 ms), `GET /api/ninos` y `GET /api/reportes/periodo` (2200 ms). La causa probable es un único proceso con una base SQLite compartida; no se perfiló el código. Acción: medir con PostgreSQL y 2 a 4 *workers*, y perfilar el listado antes de optimizar.

![Figura 70. Locust, corrida A: Incrementos 1 y 2, 20 usuarios, 60 s (p50, p95 y umbral de 800 ms).](evidencias/rendimiento/P_locust_A_inc1_inc2_20u.png)

**Figura 70.** Locust, corrida A: Incrementos 1 y 2, 20 usuarios, 60 s (p50, p95 y umbral de 800 ms). Archivo: `evidencias/rendimiento/P_locust_A_inc1_inc2_20u.png`.

![Figura 71. Locust, corrida B: Incrementos 3 y 4, 20 usuarios, 60 s (sincronización, visitas, recordatorios).](evidencias/rendimiento/P_locust_B_inc3_inc4_20u.png)

**Figura 71.** Locust, corrida B: Incrementos 3 y 4, 20 usuarios, 60 s (sincronización, visitas, recordatorios). Archivo: `evidencias/rendimiento/P_locust_B_inc3_inc4_20u.png`.

![Figura 72. Locust, corrida C: Incrementos 1 y 2, 100 usuarios, 60 s: p95 por encima del umbral.](evidencias/rendimiento/P_locust_C_inc1_inc2_100u.png)

**Figura 72.** Locust, corrida C: Incrementos 1 y 2, 100 usuarios, 60 s: p95 por encima del umbral. Archivo: `evidencias/rendimiento/P_locust_C_inc1_inc2_100u.png`.

![Figura 73. Resumen de Locust por corrida, disponibilidad, memoria y MTTR.](evidencias/terminal/P01_locust_y_mttr.png)

**Figura 73.** Resumen de Locust por corrida, disponibilidad, memoria y MTTR. Archivo: `evidencias/terminal/P01_locust_y_mttr.png`.

![Figura 74. Prueba de caos con PostgreSQL 16 temporal: peticiones durante la caída y tiempo de recuperación.](evidencias/terminal/R13_caos_postgres.png)

**Figura 74.** Prueba de caos con PostgreSQL 16 temporal: peticiones durante la caída y tiempo de recuperación. Archivo: `evidencias/terminal/R13_caos_postgres.png`.

![Figura 75. Métricas de carga de la PWA en móvil lento, con y sin service worker.](evidencias/terminal/P02_cliente_pwa.png)

**Figura 75.** Métricas de carga de la PWA en móvil lento, con y sin service worker. Archivo: `evidencias/terminal/P02_cliente_pwa.png`.

![Figura 76. Pool con `pool_pre_ping=True`.](evidencias/github/GH_pool_pre_ping.png)

**Figura 76.** Pool con `pool_pre_ping=True`. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_pool_pre_ping.png`.

**Tabla 16.** Hallazgos de confiabilidad y rendimiento y acción propuesta.

| N.° | Hallazgo | Evidencia | Acción propuesta |
| --- | --- | --- | --- |
| R-1 | Sin manejador global de excepciones: una falla de la BD responde 500 genérico en lugar de 503 | R13 (25 de 26 peticiones con 500); E29 | Registrar un manejador para `OperationalError` que responda 503 con `Retry-After`, y probarlo con el mismo script de caos |
| R-2 | No se mide la disponibilidad real en staging ni el reinicio automático por el orquestador | No existe staging | Desplegar en Render (ver `DESPLIEGUE.md`) y registrar el uptime de 7 días con un monitor externo |
| P-1 | p95 de 2000 ms con 100 usuarios (umbral 800 ms) | P_locust_C | Repetir con PostgreSQL y varios *workers*; perfilar `GET /api/ninos` (agenda por niño) |
| P-2 | No se midió la meta de la guía (500 usuarios) | — | Definir con el equipo si 500 usuarios simultáneos es realista para una posta; si no, ajustar la meta a la demanda esperada |

### 4.3 Factor S — Soportabilidad: auditoría de la arquitectura hexagonal

El código del producto está en `pmv_fastapi/app/`. La guía propone `/src/domain|ports|adapters`; aquí el equivalente es `pmv_fastapi/app/domain|ports|adapters`, más una capa `application/` (casos de uso) que la guía no contempla y que implementa los puertos de entrada (ADR-001 y ADR-008).

**Tabla 17.** Equivalencia entre la estructura de la guía y la del repositorio, con archivos y líneas de código por capa (análisis AST, incluye `__init__.py`).

| Carpeta de la guía | Carpeta del repositorio (`pmv_fastapi/app/`) | Contenido | Archivos | LOC |
| --- | --- | --- | --- | --- |
| `domain/model/` | `domain/model/` | Entidades y reglas puras (niño, evaluación, barrera, visita, notificación...) | 17 | 699 |
| `domain/service/` | `domain/service/` | Reglas clínicas, agenda, alertas, validaciones, conflictos, puntaje de visitas (funciones puras) | 12 | 1593 |
| `ports/inbound/` | `ports/inbound/` | Interfaces de casos de uso | 15 | 156 |
| `ports/outbound/` | `ports/outbound/` | Interfaces de repositorios, reloj, notificador, identidad | 9 | 143 |
| (no existe en la guía) | `application/` | Casos de uso que implementan los puertos de entrada | 13 | 1227 |
| `adapters/inbound/` | `adapters/inbound/http/` | FastAPI: rutas, esquemas Pydantic, sesión y CSRF | 5 | 1437 |
| `adapters/outbound/` | `adapters/outbound/` | SQLAlchemy y memoria, WhatsApp Cloud, SMS, Supabase Auth, relojes | 12 | 1359 |

![Figura 77. Árbol real de carpetas de `pmv_fastapi/app/` (generado recorriendo el sistema de archivos).](evidencias/arquitectura/S_arbol_hexagonal.png)

**Figura 77.** Árbol real de carpetas de `pmv_fastapi/app/` (generado recorriendo el sistema de archivos). Archivo: `evidencias/arquitectura/S_arbol_hexagonal.png`.

![Figura 78. Estructura hexagonal de `pmv_fastapi/app/` en GitHub.](evidencias/github/GH_arbol_app.png)

**Figura 78.** Estructura hexagonal de `pmv_fastapi/app/` en GitHub. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_arbol_app.png`.

![Figura 79. Importaciones de una entidad del dominio: sin frameworks.](evidencias/github/GH_dominio_entidades_imports.png)

**Figura 79.** Importaciones de una entidad del dominio: sin frameworks. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_dominio_entidades_imports.png`.

![Figura 80. Ejemplo de puerto de salida.](evidencias/github/GH_puerto_notificador.png)

**Figura 80.** Ejemplo de puerto de salida. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_puerto_notificador.png`.

![Figura 81. `main.py` como única raíz de composición.](evidencias/github/GH_main_composicion.png)

**Figura 81.** `main.py` como única raíz de composición. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_main_composicion.png`.

**Tabla 18.** Matriz de dependencias: importaciones entre capas (conteo de `import`). Ninguna celda prohibida tiene valor.

| Capa (origen) | stdlib | tercero | dom.model | dom.service | ports.in | ports.out | application | adapt.in | adapt.out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| domain.model | 40 | 0 | 17 | 0 | 0 | 0 | 0 | 0 | 0 |
| domain.service | 23 | 0 | 47 | 3 | 0 | 0 | 0 | 0 | 0 |
| ports.inbound | 19 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 |
| ports.outbound | 13 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| application | 14 | 0 | 32 | 31 | 19 | 29 | 0 | 0 | 0 |
| adapters.inbound | 7 | 8 | 12 | 0 | 13 | 0 | 0 | 1 | 0 |
| adapters.outbound | 14 | 7 | 24 | 0 | 0 | 15 | 0 | 0 | 4 |

Terceros importados: `adapters.inbound` usa `fastapi` y `pydantic`; `adapters.outbound` usa `httpx` y `sqlalchemy`; **el dominio, los puertos y la aplicación usan 0 terceros**. Violaciones de la regla de dependencias: 0. El único módulo que conoce a la vez `application` y `adapters` es `main.py` (raíz de composición, permitido por la regla).

![Figura 82. Matriz de importaciones por capa; verde permitido, rojo violación (no hay celdas rojas).](evidencias/arquitectura/S_matriz_importaciones.png)

**Figura 82.** Matriz de importaciones por capa; verde permitido, rojo violación (no hay celdas rojas). Archivo: `evidencias/arquitectura/S_matriz_importaciones.png`.

![Figura 83. Salida de `auditoria_hexagonal.py`: matriz de importaciones, terceros y violaciones.](evidencias/terminal/S01_auditoria_hexagonal.png)

**Figura 83.** Salida de `auditoria_hexagonal.py`: matriz de importaciones, terceros y violaciones. Archivo: `evidencias/terminal/S01_auditoria_hexagonal.png`.

**Tabla 19.** Matriz 3.2 (S). Soportabilidad: valores medidos.

| Factor | Atributo | Requerimiento | Método | Valor medido | Estado |
| --- | --- | --- | --- | --- | --- |
| **S** | Arquitectura hexagonal | Cero importaciones de frameworks en el dominio | AST de `import` en `domain/` (29 archivos) y 25 pruebas de arquitectura | 0 importaciones de terceros; 0 violaciones; 25 de 25 pruebas aprobadas | **Cumple** |
| **S** | Testabilidad y cobertura | Cobertura ≥ 80 % (umbral del proyecto) | pytest-cov (líneas y ramas) | 99,79 % (4030 sentencias, 5 sin cubrir; 680 ramas, 5 parciales) | **Cumple** |
| **S** | Mantenibilidad: estilo | 0 errores de linter y formato | Ruff (E, F, W, I, B, UP, S, C90; complejidad máx. 12) | 0 errores; 142 archivos formateados | **Cumple** |
| **S** | Mantenibilidad: complejidad | CC ≤ 10 por bloque | radon cc sobre 669 bloques | Promedio 2.5; máximo 17; 23 bloques con CC > 10 (rango C) | **Parcial** (96,6 % de bloques ≤ 10) |
| **S** | Mantenibilidad: índice | Rango A de mantenibilidad | radon mi sobre 75 archivos | Promedio 75.54; 73 en rango A, 1 en B (`memoria.py` 18,1), 1 en C (`sqlalchemy_repo.py` 8,3) | **Parcial** (97,3 %) |
| **S** | Extensibilidad | Agregar un canal de notificación sin tocar el dominio | Revisión de `adapters/outbound/notificaciones/` (WhatsApp, SMS, simulado, respaldo) y prueba `CP-400` | 4 adaptadores detrás del mismo puerto `Notificador` | **Cumple** (observación del código; sin métrica numérica) |

Los bloques de mayor complejidad son `extraer_eventos` y `_contar` en `domain/service/notificaciones.py` (CC 17), `actualizar_datos` en `application/servicio_expediente.py` (16) y `validar_datos_barrera` en `domain/service/barreras.py` (16). El linter (límite 12 de mccabe) pasa; radon cuenta distinto, por eso los máximos difieren. SonarQube no se ejecutó (requiere `SONAR_TOKEN`).

![Figura 84. 25 pruebas de arquitectura (`tests/arquitectura/test_dependencias.py`): todas aprobadas.](evidencias/terminal/R06_arquitectura.png)

**Figura 84.** 25 pruebas de arquitectura (`tests/arquitectura/test_dependencias.py`): todas aprobadas. Archivo: `evidencias/terminal/R06_arquitectura.png`.

![Figura 85. Ruff: «All checks passed!».](evidencias/terminal/R04_ruff_check.png)

**Figura 85.** Ruff: «All checks passed!». Archivo: `evidencias/terminal/R04_ruff_check.png`.

![Figura 86. Ruff format: 142 archivos ya formateados.](evidencias/terminal/R05_ruff_format.png)

**Figura 86.** Ruff format: 142 archivos ya formateados. Archivo: `evidencias/terminal/R05_ruff_format.png`.

![Figura 87. radon cc: bloques de complejidad B o peor.](evidencias/terminal/R10_radon_cc.png)

**Figura 87.** radon cc: bloques de complejidad B o peor. Archivo: `evidencias/terminal/R10_radon_cc.png`.

![Figura 88. radon mi: archivos con índice de mantenibilidad B o peor.](evidencias/terminal/R11_radon_mi.png)

**Figura 88.** radon mi: archivos con índice de mantenibilidad B o peor. Archivo: `evidencias/terminal/R11_radon_mi.png`.

![Figura 89. radon raw: 8112 líneas totales (6216 de código fuente) en `app/`.](evidencias/terminal/R12_radon_raw.png)

**Figura 89.** radon raw: 8112 líneas totales (6216 de código fuente) en `app/`. Archivo: `evidencias/terminal/R12_radon_raw.png`.

![Figura 90. Resumen de radon por bloque y archivo (669 bloques, 75 archivos).](evidencias/terminal/S02_radon_resumen.png)

**Figura 90.** Resumen de radon por bloque y archivo (669 bloques, 75 archivos). Archivo: `evidencias/terminal/S02_radon_resumen.png`.

![Figura 91. Pruebas de arquitectura en el repositorio.](evidencias/github/GH_pruebas_arquitectura.png)

**Figura 91.** Pruebas de arquitectura en el repositorio. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_pruebas_arquitectura.png`.

## 5. EVALUACIÓN DEL FACTOR + (PLUS): OWASP TOP 10:2025 Y RESTRICCIONES (Actividad 4)

### 5.1 Marco: lista OWASP Top 10:2025 y diferencias con la tabla de la guía

La tabla de ejemplo de la guía usa los nombres de la edición 2021 con el rótulo «2025» (por ejemplo, A10 = SSRF y A06 = componentes vulnerables). La edición **OWASP Top 10:2025** reordenó la lista: el SSRF se integró en A01 y apareció A10 «Mishandling of Exceptional Conditions». Este informe evalúa la lista 2025 y deja la equivalencia con la guía para no perder la trazabilidad.

**Tabla 20.** Equivalencia entre las categorías de la guía y la lista OWASP Top 10:2025.

| Código 2025 | Categoría OWASP Top 10:2025 | Fila equivalente en la tabla de la guía |
| --- | --- | --- |
| A01 | Broken Access Control (incluye SSRF) | A01 Broken Access Control y A10 SSRF |
| A02 | Security Misconfiguration | A05 Security Misconfiguration |
| A03 | Software Supply Chain Failures | A06 Vulnerable & Outdated Components |
| A04 | Cryptographic Failures | A02 Cryptographic Failures |
| A05 | Injection | A03 Injection |
| A06 | Insecure Design | A04 Insecure Design |
| A07 | Authentication Failures | A07 Identification & Authentication Failures |
| A08 | Software or Data Integrity Failures | A08 Software & Data Integrity Failures |
| A09 | Security Logging & Alerting Failures | A09 Security Logging & Monitoring |
| A10 | Mishandling of Exceptional Conditions | (sin equivalente) |

**Método.** (1) 30 comprobaciones estáticas sobre el código y la configuración (`metricas/owasp_estatico.py`, `E01` a `E30`). (2) 32 pruebas dinámicas contra un servidor local en `AUTH_MODE=supabase` con Supabase simulado (`metricas/seguridad_http.py`, `T01` a `T32`, incluida una prueba de que las 27 operaciones no públicas del contrato OpenAPI responden 401 sin sesión). (3) Prueba de XSS dinámica con 4 cargas en 6 pantallas (`metricas/seguridad_xss.py`). (4) SAST y SCA: bandit, pip-audit y semgrep. Resultado: **estáticas 16 cumplen, 13 hallazgos, 1 no medida; dinámicas 25 cumplen, 7 hallazgos**. No se ejecutó OWASP ZAP ni se probó un proyecto Supabase real.

### 5.2 Matriz 4.1: auditoría OWASP Top 10:2025

**Tabla 21.** Matriz 4.1. Estado por categoría, mecanismo implementado en el código y pruebas. Estado: Mitigado / Parcial / No mitigado, según las comprobaciones de la columna «Pruebas».

| Código | Vulnerabilidad evaluada | Estado | Mecanismo de mitigación en el código (Git) | Pruebas (ID: resultado) | Hallazgo |
| --- | --- | --- | --- | --- | --- |
| **A01:2025** | Broken Access Control (incluye SSRF) | **Parcial** | Sesión obligatoria en toda ruta `/api` salvo las públicas (`autenticacion.py`, `registrar_seguridad`); CSRF con cabecera `X-CSRF-Protection` y comprobación de `Origin`; las peticiones salientes usan URL de entorno, nunca del usuario | T01, T02, T03, T03b (27 de 27 operaciones → 401), T09, T11, T12, T13, E02: cumplen | E01: **no hay roles ni separación por establecimiento**; todo usuario confirmado tiene acceso total (el README lo declara) |
| **A02:2025** | Security Misconfiguration | **No mitigado** (cabeceras) | `Cache-Control: no-store` en la API y en la sesión; CORS sin `Access-Control-Allow-Origin` para orígenes ajenos; `.env` ignorado por Git; imagen con `USER appuser`, base `slim`, `HEALTHCHECK` | T10, T15, E03, E04, E06: cumplen | T19/T20: **0 de 6 cabeceras de seguridad** (CSP, nosniff, anti-frame, Referrer-Policy, HSTS, Permissions-Policy); T21 `Server: uvicorn`; T22/T23 `/docs` y `/openapi.json` públicos; E05 contraseña por defecto en `docker-compose.yml` |
| **A03:2025** | Software Supply Chain Failures | **Parcial** | 5 de 5 dependencias de producción con versión exacta (`requirements.txt`); `pip-audit`: sin vulnerabilidades conocidas | E08: cumple; pip-audit: 0 | E09 sin hashes; E10 sin Dependabot/Renovate; E11 el CI no ejecuta SAST ni auditoría de dependencias; E12 6 acciones fijadas por etiqueta, no por SHA |
| **A04:2025** | Cryptographic Failures | **Mitigado** (en código) | La aplicación no almacena contraseñas (Supabase Auth); firma HMAC-SHA256 con `hmac.compare_digest`; sin MD5/SHA-1; cookies con `Secure` | E13, E14, E15, T07: cumplen | No medido: TLS en el despliegue (lo termina el proveedor) y cifrado en reposo de Supabase |
| **A05:2025** | Injection | **Parcial** | SQLAlchemy con parámetros (0 SQL por concatenación); sin `eval`/`exec`/`pickle`/`os.system`; el cliente escapa con `esc()` (106 usos frente a 33 asignaciones a `innerHTML`) | E16, E17, E18, T16, T17, T18 (`DROP TABLE` en parámetro: la tabla sigue), XSS dinámico 6 de 6 pantallas sin ejecución: cumplen | T32: **inyección de fórmulas en el CSV** (CWE-1236): un nombre `=HYPERLINK(...)` se escribe tal cual y Excel lo evalúa |
| **A06:2025** | Insecure Design | **Parcial** | Arquitectura hexagonal (25 pruebas); 14 ADR (sesión en ADR-011, webhook en ADR-014); cerrojos de concurrencia en sincronización y recordatorios con pruebas; webhook que falla cerrado | E19, E21: cumplen | E20 **sin limitación de tasa** (login ni API); E22 sin modelo de amenazas documentado |
| **A07:2025** | Authentication Failures | **Parcial** | Mensaje de login genérico (no revela si el correo existe); cookie de sesión `HttpOnly`, `SameSite=Strict`, `Secure`, `Path=/api`; token falso → 401; el cierre de sesión borra las cookies | T04, T05, T06, T08, T14, T30: cumplen | T26: 15 intentos fallidos seguidos sin bloqueo propio; E23 política de contraseñas y MFA: **no medido** (panel de Supabase) |
| **A08:2025** | Software or Data Integrity Failures | **Parcial** | Webhook de WhatsApp con firma HMAC-SHA256 (`X-Hub-Signature-256`) siempre exigida: 403 sin firma o con firma inválida; 503 si no hay secreto configurado (falla cerrado); sin deserialización insegura | T24, T25, E24 y los escenarios HIST-4.2: cumplen | E25: el CI construye la imagen pero no la firma ni emite atestaciones |
| **A09:2025** | Security Logging & Alerting Failures | **No mitigado** | Cada registro guarda su autor (`registrado_por`, UUID verificado en modo supabase) | E27: cumple | E26: **0 usos de logging**: no se registran logins fallidos, 401/403 ni firmas inválidas; E28 sin alertas automáticas |
| **A10:2025** | Mishandling of Exceptional Conditions | **Parcial** | 11 manejadores que convierten errores de dominio en 409/422/403/503/404; JSON malformado → 422 sin traza; recurso inexistente → 404 controlado | E30, T27, T28, T29: cumplen | E29: **sin manejador global**; una caída de la BD responde 500 genérico (R13: 25 de 26 peticiones) |

Las protecciones de sesión y CSRF de A01 y A07 solo se activan con `AUTH_MODE=supabase` (valor por defecto en `main.py`, `docker-compose.yml` y `.env.example`). Con `AUTH_MODE=demo` la API es pública; el modo existe solo para pruebas y capturas y no debe usarse en un despliegue.

![Figura 92. Pruebas dinámicas T01 a T32 contra el servidor local (sesión, CSRF, cookies, cabeceras, inyección, webhook, errores).](evidencias/terminal/O02_pruebas_http_owasp.png)

**Figura 92.** Pruebas dinámicas T01 a T32 contra el servidor local (sesión, CSRF, cookies, cabeceras, inyección, webhook, errores). Archivo: `evidencias/terminal/O02_pruebas_http_owasp.png`.

![Figura 93. Comprobaciones estáticas E01 a E30 con su estado (CUMPLE, HALLAZGO, NO_MEDIDO).](evidencias/terminal/O04_estatico_owasp.png)

**Figura 93.** Comprobaciones estáticas E01 a E30 con su estado (CUMPLE, HALLAZGO, NO_MEDIDO). Archivo: `evidencias/terminal/O04_estatico_owasp.png`.

![Figura 94. Prueba dinámica de XSS: cargas inyectadas en 4 campos y revisadas en 6 pantallas (0 ejecuciones, 0 diálogos).](evidencias/terminal/O03_xss_dinamico.png)

**Figura 94.** Prueba dinámica de XSS: cargas inyectadas en 4 campos y revisadas en 6 pantallas (0 ejecuciones, 0 diálogos). Archivo: `evidencias/terminal/O03_xss_dinamico.png`.

![Figura 95. XSS: la carga se muestra como texto literal en Seguimiento.](evidencias/seguridad/XSS1_seguimiento.png)

**Figura 95.** XSS: la carga se muestra como texto literal en Seguimiento. Archivo: `evidencias/seguridad/XSS1_seguimiento.png`.

![Figura 96. XSS: texto literal en Expediente.](evidencias/seguridad/XSS2_expediente.png)

**Figura 96.** XSS: texto literal en Expediente. Archivo: `evidencias/seguridad/XSS2_expediente.png`.

![Figura 97. XSS: texto literal en Alertas.](evidencias/seguridad/XSS3_alertas.png)

**Figura 97.** XSS: texto literal en Alertas. Archivo: `evidencias/seguridad/XSS3_alertas.png`.

![Figura 98. XSS: texto literal en Visitas.](evidencias/seguridad/XSS4_visitas.png)

**Figura 98.** XSS: texto literal en Visitas. Archivo: `evidencias/seguridad/XSS4_visitas.png`.

![Figura 99. XSS: texto literal en Recordatorios.](evidencias/seguridad/XSS5_recordatorios.png)

**Figura 99.** XSS: texto literal en Recordatorios. Archivo: `evidencias/seguridad/XSS5_recordatorios.png`.

![Figura 100. XSS: texto literal en el aviso y el expediente tras registrar.](evidencias/seguridad/XSS6_registro_ui.png)

**Figura 100.** XSS: texto literal en el aviso y el expediente tras registrar. Archivo: `evidencias/seguridad/XSS6_registro_ui.png`.

![Figura 101. Control de sesión y CSRF (A01, A07).](evidencias/github/GH_sesion_cookies_csrf.png)

**Figura 101.** Control de sesión y CSRF (A01, A07). Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_sesion_cookies_csrf.png`.

![Figura 102. Verificación de la firma del webhook (A04, A08).](evidencias/github/GH_webhook_firma_hmac.png)

**Figura 102.** Verificación de la firma del webhook (A04, A08). Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_webhook_firma_hmac.png`.

![Figura 103. Ruta del webhook con firma obligatoria.](evidencias/github/GH_webhook_ruta_api.png)

**Figura 103.** Ruta del webhook con firma obligatoria. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_webhook_ruta_api.png`.

![Figura 104. Webhook que falla cerrado.](evidencias/github/GH_webhook_falla_cerrado.png)

**Figura 104.** Webhook que falla cerrado. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_webhook_falla_cerrado.png`.

![Figura 105. Seguridad a nivel de fila en Supabase (A01).](evidencias/github/GH_rls_supabase.png)

**Figura 105.** Seguridad a nivel de fila en Supabase (A01). Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_rls_supabase.png`.

![Figura 106. Validaciones de entrada en el dominio (A05, A06).](evidencias/github/GH_validaciones_dominio.png)

**Figura 106.** Validaciones de entrada en el dominio (A05, A06). Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_validaciones_dominio.png`.

![Figura 107. Idempotencia de la sincronización (A06).](evidencias/github/GH_sincronizacion_idempotente.png)

**Figura 107.** Idempotencia de la sincronización (A06). Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_sincronizacion_idempotente.png`.

![Figura 108. Escape de texto libre en el cliente (A05).](evidencias/github/GH_esc_app_js.png)

**Figura 108.** Escape de texto libre en el cliente (A05). Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_esc_app_js.png`.

### 5.3 Reporte de análisis estático (SAST) y de dependencias (SCA)

**Tabla 22.** Herramientas, comando y resultado.

| Herramienta | Comando (desde `pmv_fastapi/`) | Resultado | Lectura |
| --- | --- | --- | --- |
| bandit 1.x | `bandit -r app -q --exclude app/web` | Severidad Alta 0, Media 0, Baja 1; 6723 líneas | El hallazgo Bajo (B107, `adapters/outbound/notificaciones/sms.py` línea 16) es un parámetro con valor por defecto vacío: falso positivo |
| pip-audit | `pip-audit -r requirements.txt` | No known vulnerabilities found | 5 dependencias de producción sin CVE conocidos al 30/10/2026 |
| semgrep (reglas locales de `semgrep-rules`; el registro estaba bloqueado) | `semgrep scan --config <reglas python> --config <reglas javascript> app` | 554 reglas, 97 archivos, **151 hallazgos** (73 ERROR, 77 WARNING, 1 INFO) | Ver clasificación abajo |

**Tabla 23.** Clasificación manual de los 151 hallazgos de semgrep.

| Regla | N.° | Archivos | Clasificación |
| --- | --- | --- | --- |
| `insecure-innerhtml` e `insecure-document-method` (ERROR) | 60 | `app.js` | Patrón de XSS. Mitigado con `esc()`; la prueba dinámica no ejecutó código en 6 pantallas. Defensa en profundidad: aplicar `esc()` también a `dni`, `sexo` y `celular` donde se interpolan sin escapar |
| `html-in-template-string` (WARNING) | 65 | `app.js` | Mismo patrón (HTML en plantillas); mismo tratamiento |
| `useless-inner-function` (ERROR) | 13 | `api.py`, `main.py`, `autenticacion.py` | Falso positivo: manejadores y middleware registrados con decorador dentro de una función |
| `return-not-in-function`, `is-function-without-parentheses`, `no-replaceall`, `javascript-alert` | 12 | dominio, adaptadores, `app.js` | Calidad de código, no seguridad; sin acción de seguridad |
| `use-defusedcsv` (INFO) | 1 | `api.py` línea 754 | **Verdadero positivo**: coincide con T32 (inyección de fórmulas en el CSV) |

![Figura 109. semgrep: 554 reglas sobre 97 archivos, 151 hallazgos.](evidencias/terminal/O01_semgrep.png)

**Figura 109.** semgrep: 554 reglas sobre 97 archivos, 151 hallazgos. Archivo: `evidencias/terminal/O01_semgrep.png`.

![Figura 110. bandit: 0 altas, 0 medias, 1 baja (falso positivo).](evidencias/terminal/R08_bandit_texto.png)

**Figura 110.** bandit: 0 altas, 0 medias, 1 baja (falso positivo). Archivo: `evidencias/terminal/R08_bandit_texto.png`.

![Figura 111. pip-audit: sin vulnerabilidades conocidas.](evidencias/terminal/R09_pip_audit.png)

**Figura 111.** pip-audit: sin vulnerabilidades conocidas. Archivo: `evidencias/terminal/R09_pip_audit.png`.

**Conteo de vulnerabilidades.** Las herramientas SAST/SCA no confirman ninguna vulnerabilidad Alta o Crítica. Sin embargo, la revisión manual y dinámica sí encuentra 1 hallazgo de severidad **Alta** (falta de control de acceso por roles y por establecimiento, A01) y varios de severidad Media. Por eso el criterio «0 vulnerabilidades críticas o altas» de la guía **no se cumple**.

### 5.4 Hallazgos de seguridad y acciones propuestas

**Tabla 24.** Hallazgos consolidados. Ninguna acción está aplicada en el código. Severidad estimada por el equipo (Alta / Media / Baja).

| N.° | OWASP | Hallazgo | Severidad | Evidencia | Acción propuesta | Verificación |
| --- | --- | --- | --- | --- | --- | --- |
| H-1 | A01 | Sin roles ni segmentación por establecimiento: todo usuario autenticado ve y modifica todo | Alta | E01; README | Definir roles (enfermería, coordinador, solo lectura) y filtrar por establecimiento con políticas RLS; guardar el rol en el JWT | Prueba que un usuario sin rol recibe 403 |
| H-2 | A02 | Ninguna de las 6 cabeceras de seguridad HTTP | Media | T19, T20 | Middleware que agregue CSP, `X-Content-Type-Options: nosniff`, `frame-ancestors 'none'`, `Referrer-Policy`, `Permissions-Policy` y HSTS | Repetir `seguridad_http.py`: 6 de 6 |
| H-3 | A05 | El reporte CSV no neutraliza celdas que empiezan con `=`, `+`, `-`, `@` | Media | T32; semgrep `use-defusedcsv` | Anteponer `'` a esas celdas al escribir el CSV (`api.py`, líneas 752 a 790) y probarlo con la carga de T32 | T32 pasa a CUMPLE |
| H-4 | A06 / A07 | Sin limitación de tasa en login ni en la API | Media | E20, T26 | Limitar intentos por IP y por correo (por ejemplo, 5 por minuto) en la aplicación o en el proxy; confirmar el bloqueo de Supabase | T26 devuelve 429 |
| H-5 | A09 | Sin registro ni alertas de eventos de seguridad | Media | E26, E28 | Registrar con `logging` los logins fallidos, 401/403 y firmas inválidas (sin tokens ni datos personales) y definir una alerta por umbral | E26 pasa a CUMPLE |
| H-6 | A10 | Sin manejador global de excepciones: la BD caída produce 500 | Media | E29, R13 | Manejador de `OperationalError` → 503 y de `Exception` → 500 genérico con identificador de correlación | R13: 0 respuestas 500 durante la caída |
| H-7 | A03 / A08 | CI sin SAST ni auditoría de dependencias, sin Dependabot, acciones por etiqueta, sin hashes ni firma | Media | E09 a E12, E25 | Agregar `pip-audit` y `bandit` al CI, activar Dependabot, fijar acciones por SHA y publicar atestaciones de la imagen | E09 a E12 y E25 pasan a CUMPLE |
| H-8 | A02 | `/docs` y `/openapi.json` públicos; `Server: uvicorn` | Baja | T21 a T23 | Desactivar `docs_url` y `openapi_url` en producción o protegerlos con sesión; `--no-server-header` | T21 a T23 pasan a CUMPLE |
| H-9 | A02 | Contraseña por defecto `cambiar_en_staging` en `docker-compose.yml` | Baja | E05 | Exigir `POSTGRES_PASSWORD` sin valor por defecto | E05 pasa a CUMPLE |
| H-10 | A05 | `esc()` ausente en `dni`, `sexo` y `celular` al construir HTML | Baja | semgrep, E18 | Aplicar `esc()` o usar `textContent` | prueba XSS ampliada con cargas en `dni`, `sexo` y `celular` |
| H-11 | A06 | Sin modelo de amenazas documentado | Baja | E22 | Documentar STRIDE de los flujos de sesión, sincronización y webhook en `docs/` | Documento en el repositorio |
| H-12 | A07 | Política de contraseñas, MFA y bloqueo de Supabase sin verificar | No medido | E23 | Revisar el panel de Supabase Auth (mínimo 12 caracteres, MFA para coordinación) y dejar captura | Captura del panel |

![Figura 112. Código afectado por el hallazgo H-3.](evidencias/github/GH_csv_reporte_hallazgo.png)

**Figura 112.** Código afectado por el hallazgo H-3. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_csv_reporte_hallazgo.png`.

### 5.5 Matriz 4.2: restricciones técnicas adicionales

**Tabla 25.** Restricciones técnicas, estado medido y evidencia.

| Tipo | Especificación del proyecto | Estado | Evidencia técnica |
| --- | --- | --- | --- |
| **Diseño** | Mantener la arquitectura hexagonal (`domain/`, `ports/`, `application/`, `adapters/`) | **Conforme** | 25 de 25 pruebas de arquitectura; 0 violaciones (S01, R06) |
| **Implementación** | Python 3.11+ con linter obligatorio (Ruff) y formato verificado en el CI | **Conforme** | Ruff: 0 errores; 142 archivos formateados (R04, R05). Observación: la medición local usó Python 3.13 y el CI y el `Dockerfile` usan 3.11 |
| **Interfaz** | Contrato OpenAPI 3 versionado y verificado | **Conforme** | `docs/openapi.json` al día (R07); prueba `test_openapi.py`; Swagger UI en `/docs` (público: ver H-8) |
| **Despliegue** | Contenerización con Docker y `docker-compose` | **No medido por ejecución** | El `Dockerfile` (usuario no root, `HEALTHCHECK`) y `docker-compose.yml` se revisaron en el código (E06); aquí no hay daemon Docker. El trabajo `imagen` del CI ejecuta `docker build` (ver Anexo C) |

![Figura 113. Verificación de que `docs/openapi.json` está al día con el código.](evidencias/terminal/R07_openapi.png)

**Figura 113.** Verificación de que `docs/openapi.json` está al día con el código. Archivo: `evidencias/terminal/R07_openapi.png`.

![Figura 114. Dockerfile del producto.](evidencias/github/GH_dockerfile.png)

**Figura 114.** Dockerfile del producto. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_dockerfile.png`.

![Figura 115. Orquestación con docker-compose.](evidencias/github/GH_docker_compose.png)

**Figura 115.** Orquestación con docker-compose. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_docker_compose.png`.

![Figura 116. Contrato OpenAPI versionado en el repositorio.](evidencias/github/GH_openapi_json.png)

**Figura 116.** Contrato OpenAPI versionado en el repositorio. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_openapi_json.png`.

![Figura 117. Configuración del linter.](evidencias/github/GH_pyproject_ruff.png)

**Figura 117.** Configuración del linter. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_pyproject_ruff.png`.

![Figura 118. Flujo de CI/CD en el repositorio.](evidencias/github/GH_ci_workflow.png)

**Figura 118.** Flujo de CI/CD en el repositorio. Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_ci_workflow.png`.

![Figura 119. Ejecución verde de GitHub Actions (ruta completa: `https://github.com/woshtsu/ProcesosSoftwareAnemia/actions/workflows/ci.yml`).](evidencias/github/GH_actions_ejecucion_verde.png)

**Figura 119.** Ejecución verde de GitHub Actions (ruta completa: `https://github.com/woshtsu/ProcesosSoftwareAnemia/actions/workflows/ci.yml`). Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_actions_ejecucion_verde.png`.

## 6. CONSOLIDADO DEL ÍNDICE DE CALIDAD FURPS+ Y PLAN DE EVOLUCIÓN (Actividad 5)

IC_P = Σ (puntaje del factor × peso). El detalle por criterio está en la sección 2.2; aquí se resume con las brechas y las acciones.

**Tabla 26.** Matriz 5.1. Cuadro de mando consolidado FURPS+ (índice primario sobre criterios medidos; índice conservador entre paréntesis).

| Factor FURPS+ | Peso | Cumplimiento obtenido | Puntaje ponderado | Brecha identificada | Acción de evolución / mejora |
| --- | --- | --- | --- | --- | --- |
| **F — Funcionalidad** | 30 % | 100,0 % (100,0 %) | 30,00 % (30,00 %) | Ninguna en los 19 escenarios. Límites: datos sintéticos, sin usuarios reales; cada incremento se verificó con el código de `v4.0-Inc4`, no con su etiqueta original | Mantener la matriz de aceptación y ejecutar `capturar_software.py` como paso del CI |
| **U — Usabilidad** | 15 % | 82,7 % (72,4 %) | 12,41 % (10,86 %) | 1.4.11: 3 de 8 componentes; ARIA (`tablist` sin `tab`, selects y fechas sin etiqueta); modal sin retención de foco; 190 de 924 objetivos menores de 24 px; naranja 4,23:1; NVDA/TalkBack no medido | U-1 a U-8 (sección 4.1): primero etiquetas y `role=tab`, luego colores y foco del modal |
| **R — Confiabilidad** | 15 % | 84,0 % (72,0 %) | 12,60 % (10,80 %) | La caída de la BD produce 500 en lugar de 503; sin staging para medir disponibilidad real | R-1 (manejador 503) y R-2 (desplegar en Render y monitorear 7 días) |
| **P — Rendimiento** | 15 % | 85,0 % (68,0 %) | 12,75 % (10,20 %) | p95 de 2000 ms con 100 usuarios; 500 usuarios sin medir | P-1 (PostgreSQL, varios workers, perfilar el listado) y P-2 (definir la meta realista) |
| **S — Soportabilidad** | 10 % | 99,0 % (99,0 %) | 9,90 % (9,90 %) | 23 de 669 bloques con CC > 10; 2 archivos fuera del rango A (`sqlalchemy_repo.py` MI 8,3; `memoria.py` 18,1) | Dividir `sqlalchemy_repo.py` por agregado y simplificar `extraer_eventos` y `_contar` |
| **+ — Seguridad / Restricciones** | 15 % | 66,8 % (44,5 %) | 10,02 % (6,68 %) | 41 de 61 comprobaciones; 1 hallazgo Alta (sin roles); 0 de 6 cabeceras; CSV con fórmulas; sin logs ni alertas de seguridad; 3 criterios no medidos | H-1 a H-12 (sección 5.4): primero H-1, H-2, H-3, H-5 y H-6 |
| **TOTAL** | **100 %** | — | **87,67 % (78,43 %)** | Por debajo de «Excelente (≥ 90 %)» de la guía; brechas en U, R, P y + | Plan de evolución siguiente |

**Sensibilidad.** El índice primario (87,67 %) ignora lo no medido; el conservador (78,43 %) lo cuenta como incumplido. La diferencia (9,24 puntos) cuantifica cuánto de la calidad depende de mediciones que faltan: lector de pantalla, staging, 500 usuarios, Docker en ejecución y política de Supabase.

**Tabla 27.** Plan de evolución del producto, ordenado por prioridad (la prioridad pondera severidad del hallazgo y esfuerzo estimado).

| Prioridad | Acción | Hallazgos | Factor | Esfuerzo estimado | Criterio de verificación (script a repetir) |
| --- | --- | --- | --- | --- | --- |
| 1 | Roles y filtro por establecimiento (JWT + RLS) | H-1 | + | Alto (2 a 3 días) | Prueba nueva de 403 por rol; E01 CUMPLE |
| 2 | Cabeceras de seguridad, `docs` protegidos, sin cabecera `Server` | H-2, H-8 | + | Bajo (0,5 día) | `seguridad_http.py`: T19 a T23 CUMPLEN |
| 3 | Neutralizar fórmulas en el CSV | H-3 | + | Bajo (0,5 día) | T32 CUMPLE |
| 4 | Manejador 503 ante falla de BD y registro de eventos de seguridad | H-5, H-6, R-1 | +, R | Medio (1 día) | `caos_postgres.py`: 0 respuestas 500; E26 y E29 CUMPLEN |
| 5 | Etiquetas ARIA, `role=tab`, foco del modal, `role=status` en avisos | U-1, U-2, U-5, U-8 | U | Medio (1 día) | `accesibilidad.py`: axe sin violaciones críticas |
| 6 | Ajustes de color (naranja, bordes, foco, barras) y objetivos táctiles ≥ 24 px | U-3, U-4, U-7 | U | Bajo (0,5 día) | `paleta_colores.py`: 23 de 23 pares y 8 de 8 componentes |
| 7 | SAST, auditoría de dependencias, Dependabot y acciones por SHA en el CI | H-4, H-7 | + | Bajo (0,5 día) | E09 a E12 CUMPLEN |
| 8 | Desplegar en Render y medir uptime 7 días; repetir carga con PostgreSQL y varios workers | R-2, P-1, P-2 | R, P | Medio (1 a 2 días) | Disponibilidad ≥ 99,5 %; p95 < 800 ms a 100 usuarios |
| 9 | Prueba con NVDA y TalkBack y revisión de Supabase Auth (MFA, política) | H-12, U8 | U, + | Bajo (0,5 día) | Capturas y lista de comprobación |

Meta de la siguiente medición: IC_P ≥ 90 % con los mismos scripts y sin criterios no medidos en U, R y +.

## 7. CONCLUSIONES Y LECCIONES APRENDIDAS SOBRE LA EVALUACIÓN DEL PRODUCTO

- **La funcionalidad está completa y verificada:** 19 de 19 escenarios de aceptación en los cuatro incrementos, 660 pruebas de pytest y 28 E2E aprobadas, cobertura de 99,79 %. El índice global es 87,67 % (primario) y 78,43 % (conservador): sólido, pero no «Excelente» según la guía.
- **La arquitectura hexagonal se sostiene con evidencia:** 0 importaciones de terceros en dominio, puertos y aplicación, 0 violaciones de la regla de dependencias y 25 pruebas que lo vigilan en cada ejecución. Es el factor mejor evaluado después de F (99,0 %).
- **La accesibilidad es la brecha principal de usabilidad:** axe marca violaciones en 26 de 28 vistas por un mismo patrón (barra de pestañas, etiquetas). Son pocas correcciones de bajo esfuerzo. El contraste de texto es bueno (22 de 23 pares); el de componentes no (3 de 8).
- **El rendimiento cumple con carga de una posta (20 usuarios, p95 ≤ 98 ms) pero no con 100 usuarios (p95 de 2 s):** no se midió la meta de 500 usuarios de la guía.
- **La seguridad de diseño es buena en sesión, firma del webhook y SQL, pero hay brechas operativas:** sin roles, sin cabeceras, sin registro de eventos de seguridad, CSV con fórmulas y 500 ante caída de la BD. La tabla de ejemplo de la guía marca todo «Mitigado»; aquí no se pudo decir lo mismo con evidencia.
- **Lecciones:** (1) medir con scripts reproducibles evita cifras sin respaldo y permitió encontrar defectos reales (CSV con fórmulas, 500 ante BD caída); (2) las pruebas con el navegador detectan fallas que el análisis estático no ve, por ejemplo que `context.set_offline` no afecta al service worker, y por eso el caso sin conexión se probó deteniendo el servidor; (3) declarar lo no medido separa lo verificado de lo supuesto: la diferencia entre el índice primario y el conservador es 9,24 puntos; (4) los umbrales de la guía (500 usuarios, AWS, SonarQube) requieren infraestructura que el proyecto no tiene: conviene acordar umbrales proporcionales al contexto de una posta rural.

## 8. ANEXOS Y EVIDENCIAS TÉCNICAS

### Anexo A. Cómo reproducir cada medición

Desde la raíz del repositorio, con un entorno virtual con `requirements-dev.txt`, `locust`, `radon`, `bandit`, `pip-audit`, `semgrep` y Playwright con Chromium instalado. Los scripts usan el puerto 8765. `metricas/ejecutar.py ID "Título" --cwd DIR -- comando` guarda la salida en `metricas/salidas/ID.txt` y su captura de terminal en `evidencias/terminal/ID.png` con comando, fecha y commit en el pie.

**Tabla 28.** Comandos de medición, salidas y figuras.

| ID | Comando | Directorio | Commit | Fecha | Salida | Captura |
| --- | --- | --- | --- | --- | --- | --- |
| `F01_aceptacion_software` | `python ../entregables/semana-10/metricas/capturar_software.py` | `pmv_fastapi` | ada827f | 2026-10-30 20:14 | `metricas/salidas/F01_aceptacion_software.txt` | `evidencias/terminal/F01_aceptacion_software.png` |
| `FURPS01_calculo_indice` | `python entregables/semana-10/metricas/furps_calculo.py` | `.` | ada827f | 2026-10-30 20:21 | `metricas/salidas/FURPS01_calculo_indice.txt` | `evidencias/terminal/FURPS01_calculo_indice.png` |
| `O01_semgrep` | `<venv>/bin/semgrep scan --config <tmp>/semgrep-rules/python --config <tmp>/semgrep-rules/javascript --metrics=off --disable-version-check --exclude vendor --exclude tests --json-output=<tmp>/semgrep.json --text app` | `pmv_fastapi` | ada827f | 2026-10-30 19:55 | `metricas/salidas/O01_semgrep.txt` | `evidencias/terminal/O01_semgrep.png` |
| `O02_pruebas_http_owasp` | `python ../entregables/semana-10/metricas/seguridad_http.py` | `pmv_fastapi` | ada827f | 2026-10-30 20:13 | `metricas/salidas/O02_pruebas_http_owasp.txt` | `evidencias/terminal/O02_pruebas_http_owasp.png` |
| `O03_xss_dinamico` | `python entregables/semana-10/metricas/seguridad_xss.py` | `.` | ada827f | 2026-10-30 20:12 | `metricas/salidas/O03_xss_dinamico.txt` | `evidencias/terminal/O03_xss_dinamico.png` |
| `O04_estatico_owasp` | `python entregables/semana-10/metricas/owasp_estatico.py` | `.` | ada827f | 2026-10-30 20:12 | `metricas/salidas/O04_estatico_owasp.txt` | `evidencias/terminal/O04_estatico_owasp.png` |
| `P01_locust_y_mttr` | `python entregables/semana-10/metricas/rendimiento.py` | `.` | ada827f | 2026-10-30 20:12 | `metricas/salidas/P01_locust_y_mttr.txt` | `evidencias/terminal/P01_locust_y_mttr.png` |
| `P02_cliente_pwa` | `python entregables/semana-10/metricas/rendimiento_cliente.py` | `.` | ada827f | 2026-10-30 20:13 | `metricas/salidas/P02_cliente_pwa.txt` | `evidencias/terminal/P02_cliente_pwa.png` |
| `R01_pytest_cobertura` | `python -m pytest --cov=app --cov-report=term-missing --cov-report=json:<tmp>/cov.json -q -p no:cacheprovider` | `pmv_fastapi` | e6886e2 | 2026-10-30 19:38 | `metricas/salidas/R01_pytest_cobertura.txt` | `evidencias/terminal/R01_pytest_cobertura.png` |
| `R02_pytest_junit` | `python -m pytest -q --no-cov -p no:cacheprovider --junitxml=<tmp>/junit_unit.xml -rA` | `pmv_fastapi` | e6886e2 | 2026-10-30 19:39 | `metricas/salidas/R02_pytest_junit.txt` | `evidencias/terminal/R02_pytest_junit.png` |
| `R03_e2e_playwright` | `python -m pytest tests/e2e -m e2e -v --no-cov -p no:cacheprovider --junitxml=<tmp>/junit_e2e.xml` | `pmv_fastapi` | e6886e2 | 2026-10-30 19:40 | `metricas/salidas/R03_e2e_playwright.txt` | `evidencias/terminal/R03_e2e_playwright.png` |
| `R04_ruff_check` | `<venv>/bin/ruff check . --no-cache` | `pmv_fastapi` | ada827f | 2026-10-30 19:51 | `metricas/salidas/R04_ruff_check.txt` | `evidencias/terminal/R04_ruff_check.png` |
| `R05_ruff_format` | `<venv>/bin/ruff format --check . --no-cache` | `pmv_fastapi` | ada827f | 2026-10-30 19:51 | `metricas/salidas/R05_ruff_format.txt` | `evidencias/terminal/R05_ruff_format.png` |
| `R06_arquitectura` | `python -m pytest tests/arquitectura -v --no-cov -p no:cacheprovider` | `pmv_fastapi` | ada827f | 2026-10-30 19:51 | `metricas/salidas/R06_arquitectura.txt` | `evidencias/terminal/R06_arquitectura.png` |
| `R07_openapi` | `python -m scripts.exportar_openapi --verificar` | `pmv_fastapi` | ada827f | 2026-10-30 19:51 | `metricas/salidas/R07_openapi.txt` | `evidencias/terminal/R07_openapi.png` |
| `R08_bandit_texto` | `<venv>/bin/bandit -r app -q --exclude app/web` | `pmv_fastapi` | ada827f | 2026-10-30 19:51 | `metricas/salidas/R08_bandit_texto.txt` | `evidencias/terminal/R08_bandit_texto.png` |
| `R09_pip_audit` | `<venv>/bin/pip-audit -r requirements.txt --progress-spinner off` | `pmv_fastapi` | ada827f | 2026-10-30 19:52 | `metricas/salidas/R09_pip_audit.txt` | `evidencias/terminal/R09_pip_audit.png` |
| `R10_radon_cc` | `<venv>/bin/radon cc app -a -s -nb` | `pmv_fastapi` | ada827f | 2026-10-30 19:52 | `metricas/salidas/R10_radon_cc.txt` | `evidencias/terminal/R10_radon_cc.png` |
| `R11_radon_mi` | `<venv>/bin/radon mi app -s -n B` | `pmv_fastapi` | ada827f | 2026-10-30 19:52 | `metricas/salidas/R11_radon_mi.txt` | `evidencias/terminal/R11_radon_mi.png` |
| `R12_radon_raw` | `<venv>/bin/radon raw app -s` | `pmv_fastapi` | ada827f | 2026-10-30 19:52 | `metricas/salidas/R12_radon_raw.txt` | `evidencias/terminal/R12_radon_raw.png` |
| `R13_caos_postgres` | `python entregables/semana-10/metricas/caos_postgres.py` | `.` | ada827f | 2026-10-30 20:08 | `metricas/salidas/R13_caos_postgres.txt` | `evidencias/terminal/R13_caos_postgres.png` |
| `S01_auditoria_hexagonal` | `python entregables/semana-10/metricas/auditoria_hexagonal.py` | `.` | ada827f | 2026-10-30 20:22 | `metricas/salidas/S01_auditoria_hexagonal.txt` | `evidencias/terminal/S01_auditoria_hexagonal.png` |
| `S02_radon_resumen` | `python entregables/semana-10/metricas/resumen_calidad.py` | `.` | ada827f | 2026-10-30 19:52 | `metricas/salidas/S02_radon_resumen.txt` | `evidencias/terminal/S02_radon_resumen.png` |
| `U01_paleta_contraste` | `python entregables/semana-10/metricas/paleta_colores.py` | `.` | ada827f | 2026-10-30 20:06 | `metricas/salidas/U01_paleta_contraste.txt` | `evidencias/terminal/U01_paleta_contraste.png` |
| `U02_accesibilidad` | `AXE_JS=<tmp>/axe/node_modules/axe-core/axe.min.js python entregables/semana-10/metricas/accesibilidad.py` | `.` | ada827f | 2026-10-30 20:15 | `metricas/salidas/U02_accesibilidad.txt` | `evidencias/terminal/U02_accesibilidad.png` |

`S01_auditoria_hexagonal`, `O05_bandit.json` (`bandit -r app -q --exclude app/web -f json`) y `U02_accesibilidad` (con `AXE_JS=<ruta a axe.min.js 4.14.0>`) se ejecutan igual. Las capturas derivadas (Locust, árbol, matriz de importaciones, resumen axe) las genera `metricas/graficos.py`; el índice, `metricas/furps_calculo.py`; las capturas por escenario, `metricas/capturar_software.py`; la paleta, `metricas/paleta_colores.py`.

**Tabla 29.** Versiones de las herramientas.

| Herramienta | Versión |
| --- | --- |
| Python | 3.13.16 (medición local; CI y Docker usan 3.11) |
| FastAPI / uvicorn / SQLAlchemy / httpx | 0.142.0 / 0.46.0 / 2.1.1 / 0.28.1 |
| pytest / pytest-cov / coverage | 9.1.1 / 7.1.0 / 7.16.2 |
| Playwright (Chromium) | 1.56.0 |
| axe-core | 4.14.0 |
| Locust | 2.46.6 |
| Ruff / radon | 0.15.11 / 6.0.1 |
| bandit / pip-audit / semgrep | 1.9.4 / ver `R09_pip_audit.txt` / 1.183.0 |
| PostgreSQL (prueba de caos) | 16 (clúster temporal en `127.0.0.1:5433`) |

### Anexo B. Reportes y gráficos de rendimiento y accesibilidad

Reportes crudos en `metricas/salidas/`: `U_axe_por_pantalla.json` (axe, 14 pantallas x 2 vistas), `U_contraste_paleta.json`, `U_teclado.json`, `U_objetivos_tactiles.json`, `U_reflow_320px.json`, `U_estados_con_texto.json`, `O01_semgrep.json`, `O05_bandit.json`, `OWASP_estatico.json`, `OWASP_pruebas_http.json`, `OWASP_xss.json`, `P_*_stats.csv` y `P_*_stats_history.csv` (Locust), `P_resumen.json`, `P_cliente_pwa.json`, `R_caos_postgres.json`, `R_mttr_reinicio.json`, `S_hexagonal.json`, `S_radon_resumen.json`, `R01_cobertura.json`, `R02_junit_unit.xml`, `R03_junit_e2e.xml`, `F_resultados_aceptacion.json` y `FURPS_calculo.json`. Los gráficos de Locust son las figuras de la sección 4.2 (`evidencias/rendimiento/`) y el resumen de axe es la figura de la sección 4.1 (`evidencias/usabilidad/U_axe_resumen_pantallas.png`). No se usó SonarQube ni k6.

### Anexo C. Repositorio y etiquetas

Repositorio (privado): <https://github.com/woshtsu/ProcesosSoftwareAnemia>.

**Tabla 30.** Etiquetas de los incrementos y estado verificado en el clon local (`git tag` no devuelve etiquetas en este clon; las capturas de GitHub las debe tomar el equipo).

| Incremento | Etiqueta | Commit de referencia | Estado de verificación |
| --- | --- | --- | --- |
| Inc. 1 — PMV | `v1.0-PMV` | (ver informe S9) | Existe en GitHub según el informe S9; no se verificó en este clon |
| Inc. 2 | `v2.0-Inc2` | `fb26626` (18/10/2026) | Existe según S9; el commit existe en el clon, la etiqueta no |
| Inc. 3 | `v3.0-Inc3` | `e920820` | El commit existe en el clon («Inc. 3 completo»); etiqueta no verificada |
| Inc. 4 | `v4.0-Inc4` | `5c1f1eb`; código medido en `e6886e2` | El commit existe; la adenda S9 indica que la etiqueta está prevista y no existe en el clon local |

![Figura 120. Etiquetas de los cuatro incrementos en GitHub (ruta completa: `https://github.com/woshtsu/ProcesosSoftwareAnemia/tags`).](evidencias/github/GH_etiquetas.png)

**Figura 120.** Etiquetas de los cuatro incrementos en GitHub (ruta completa: `https://github.com/woshtsu/ProcesosSoftwareAnemia/tags`). Captura de GitHub en la etiqueta `v4.0-Inc4` (30/10/2026). Archivo: `evidencias/github/GH_etiquetas.png`.

Si `v4.0-Inc4` no se publicó cuando se tomen las capturas, se debe crear sobre el commit `5c1f1eb` o sobre el de las correcciones de CI y registrar el commit elegido; el índice de este informe se midió en `e6886e2`/`ada827f`.

### Anexo D. Limitaciones de la medición

- Una sola máquina virtual, un único proceso y datos sintéticos: ninguna latencia ni capacidad es de producción.
- Las capturas usan `AUTH_MODE=demo`; las pruebas de seguridad usan Supabase simulado. No se probó Supabase real, TLS del despliegue ni cifrado en reposo.
- No se ejecutaron: lector de pantalla, SUS, SonarQube, OWASP ZAP, k6, 500 usuarios, staging Render/AWS ni Docker en ejecución.
- Cada incremento se evaluó con el código de `v4.0-Inc4`; no se restauraron las etiquetas anteriores ni se compararon métricas entre versiones (eso corresponde a la adenda S9 y al informe S12).
- La severidad de los hallazgos es estimación del equipo, no puntaje CVSS.
- Los datos de este informe y de las capturas los generó el asistente de IA con los scripts del repositorio; el equipo debe revisarlos antes de la entrega.

