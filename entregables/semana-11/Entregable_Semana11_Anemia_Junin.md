# INFORME TÉCNICO: EVALUACIÓN DEL PROCESO Y PRODUCTO MEDIANTE EL MODELO CMMI — Semana 11

## 1. CARÁTULA E INTEGRANTES DEL EQUIPO (Noveno Ciclo)

**Tabla 1.** Datos generales del entregable.

| Campo | Detalle |
| --- | --- |
| **Carrera** | Ingeniería de Sistemas e Informática |
| **Asignatura** | Procesos de Software (ASUC01702), Universidad Continental, periodo 2026-20, Noveno ciclo |
| **Proyecto de asignatura** | Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín |
| **Docente** | Guevara Jimenez, Jorge Alfredo |
| **Semana y guía** | Semana 11: «Evaluación de proceso y producto de software mediante el modelo CMMI (CMMI-DEV)» (`guias/S11-PSW-GUÍA DE TRABAJO 11.docx`) |
| **Fecha** | 30/10/2026 |
| **Versiones evaluadas** | `v1.0-PMV` (Incremento 1), `v1.5.0-inc2-avance` (hito al 50 % del Incremento 2) y `v2.0-Inc2` (Incremento 2 completo, commit `fb26626`), más el estado actual de `main` (commit `72e7025`), que añade autenticación con Supabase y la configuración de producción |
| **Repositorio** | <https://github.com/woshtsu/ProcesosSoftwareAnemia> |
| **Producción** | <https://softwareanemia.onrender.com/> |

**Tabla 2.** Integrantes del equipo.

| N.° | Apellidos, Nombres | Código | Rol en el proyecto |
| --- | --- | --- | --- |
| 1 | Porras Veli, Ricardo | 76659572 | Ingeniero de Proceso |
| 2 | Auqui Huincho, Tania Tifani | 75280128 | Ingeniera de Desarrollo y Prototipado |
| 3 | Huamani Rodriguez, Jean Piero | 72156889 | Ingeniero de Calidad y Mejora del Proceso (QA Lead) |

**Índice**

1. Carátula e integrantes del equipo
2. Resumen ejecutivo y enfoque CMMI seleccionado
3. Matriz de selección de áreas de práctica CMMI (Actividad 1)
4. Evaluación de niveles de capacidad del proceso (Actividad 2)
5. Auditoría de productos de trabajo (Actividad 3)
6. Evaluación de verificación (VER) y validación (VAL) con capturas (Actividad 4)
7. Análisis de causa raíz (CAR) y plan de mejora continua (Actividad 5)
8. Conclusiones y lecciones aprendidas en la adopción de CMMI
9. Anexos y evidencias técnicas

---

## 2. RESUMEN EJECUTIVO Y ENFOQUE CMMI SELECCIONADO

El proyecto desarrolla un producto mínimo viable (PMV) para registrar y dar seguimiento a la anemia infantil en establecimientos de Junín. Está construido con FastAPI, una interfaz web HTML/CSS/JS y arquitectura hexagonal; usa SQLite en desarrollo y PostgreSQL en producción, y se entregó en dos incrementos: el Incremento 1 (RF-01 a RF-05, `v1.0-PMV`) y el Incremento 2 (RF-06 a RF-09, `v2.0-Inc2`). Tras la semana 9, el repositorio incorporó autenticación con Supabase Auth y un flujo de integración y despliegue continuos hacia Render.

Este informe aplica el modelo CMMI (CMMI-DEV) con la **representación continua**: se evalúa la capacidad de seis áreas de práctica (PLAN, ESTIM, VER, VAL, PQA y CM) en la escala de 0 a 3 de la guía (Incompleto, Ejecutado, Gestionado, Definido), y se audita la calidad de los productos de trabajo que cada área genera. La evaluación es una **autoevaluación del equipo basada en evidencia verificable del repositorio**; no constituye una apreciación formal ni una certificación de madurez organizacional.

**Resultados principales.**

- **PLAN, CM y VER están en Nivel 2; ESTIM, PQA y VAL están en Nivel 1.** Ninguna área alcanza el Nivel 3. VER sobresale: 349 pruebas automáticas aprobadas, cobertura de `app/` de 99,50 %, cero hallazgos de Ruff y 18 pruebas de arquitectura que vigilan la regla de dependencia.
- Los nueve requerimientos funcionales cuentan con ficha de verificación y validación, pruebas automatizadas y capturas de entrada y resultado (sección 6).
- Las brechas con mayor impacto son: ausencia de registro de horas reales (ESTIM), revisiones de código sin plantilla ni lista de chequeo (PQA), análisis estático con SonarCloud sin activar (VER) y falta de aceptación formal por usuarios (VAL). La sección 7 las convierte en un plan de mejora con responsables, métricas y fechas.

**Limitaciones de la evaluación.** Las cifras de pruebas por defecto, cobertura, análisis estático y contrato OpenAPI se reprodujeron el 30/10/2026 sobre el estado actual de `main`. Las 17 pruebas E2E con navegador se ejecutaron por última vez el 23/10/2026 (15 de la versión v2.0 evaluada en la semana 9 más 2 de autenticación); las capturas y las mediciones de tiempos proceden de las ejecuciones de la semana 9 (16 y 17/10/2026). No se pudo verificar durante la elaboración de este informe el historial de ejecuciones de GitHub Actions, el tablero de GitHub Projects, las aprobaciones de revisión de los *pull requests*, la construcción de la imagen Docker (el motor de contenedores no estaba activo) ni el estado del servicio en el panel de Render. Cada vez que una calificación depende de uno de estos elementos, se indica.

---

## 3. MATRIZ DE SELECCIÓN DE ÁREAS DE PRÁCTICA CMMI (Actividad 1)

Se seleccionaron las seis áreas de práctica propuestas por la guía porque cubren el ciclo completo de un incremento de este proyecto: se estima y planifica el trabajo, se construye y verifica el código, se valida con el usuario, se audita la calidad y se controla la configuración. El tamaño del equipo (tres integrantes) y la naturaleza académica del proyecto no justifican áreas de nivel organizacional, como Desarrollo de Procesos de la Organización.

**Tabla 3.** Matriz 1.1: Mapeo de áreas de práctica CMMI del proyecto.

| Categoría CMMI | Área de práctica (PA) | Propósito de la evaluación en el proyecto | Productos de trabajo auditados |
| --- | --- | --- | --- |
| Gestión | ESTIM (Estimating) | Determinar si la estimación de tamaño y esfuerzo se registró con una técnica formal y se contrastó con lo real | Estimación del *backlog* en puntos de historia (133 SP; INC-1 = 21 SP, INC-2 = 18 SP) y en horas-persona del Incremento 1 (Entregable S3-4, Tablas 19 y 20) |
| Gestión | PLAN (Planning) | Evaluar si el plan, los hitos y las dependencias se establecieron y se mantuvieron frente a las desviaciones | WBS, cronograma de sprints e hitos H1 y H2, red y ruta crítica (Entregable S3-4, Tablas 11 y 22 a 25); replanificación del Sprint 4 y 5 (Entregable S9, sección 2.1) |
| Ingeniería | VER (Verification) | Comprobar que el código y el diseño cumplen las especificaciones técnicas | Código fuente en `pmv_fastapi/app/`, 349 pruebas, cobertura, Ruff, pruebas de arquitectura, contrato OpenAPI |
| Ingeniería | VAL (Validation) | Comprobar que el software satisface la necesidad del usuario | Fichas por requerimiento con criterio Dado-Cuando-Entonces, capturas de pantalla, registro de defectos |
| Soporte | PQA (Process and Product Quality Assurance) | Auditar de forma objetiva el cumplimiento del proceso y de los productos | Definición de terminado (DoD, Entregable S3-4, Tabla 9), reglas de calidad del CI, revisiones por *pull request* |
| Soporte | CM (Configuration Management) | Evaluar el control de versiones, ramas, etiquetas y entregas | Repositorio GitHub, etiquetas `v1.0-PMV`, `v1.5.0-inc2-avance` y `v2.0-Inc2`, flujo de CI/CD (`.github/workflows/ci.yml`) |

El análisis de causa raíz (CAR), área de práctica de soporte mencionada en el marco teórico de la guía, se aplica en la sección 7 a los hallazgos de las seis áreas anteriores.

---

## 4. EVALUACIÓN DE NIVELES DE CAPACIDAD DEL PROCESO (Actividad 2)

### 4.1 Criterio de calificación

Para evitar asignaciones arbitrarias, cada nivel se otorgó con el siguiente criterio, aplicado a la evidencia del repositorio.

**Tabla 4.** Criterio de asignación del nivel de capacidad.

| Nivel | Condición exigida |
| --- | --- |
| 0 — Incompleto | Las prácticas específicas del área no se realizan o no dejan producto de trabajo |
| 1 — Ejecutado | Las prácticas se realizan y producen sus productos, pero sin registro sistemático, sin seguimiento frente a lo planificado o con cobertura parcial |
| 2 — Gestionado | Las prácticas están planificadas, tienen responsables, se contrastan con lo real y sus productos se controlan y revisan con evidencia verificable |
| 3 — Definido | Además del Nivel 2, existe un estándar documentado y adaptado al proyecto que se aplica de forma consistente en todos los incrementos, con plantillas o automatización que lo hacen exigible |

### 4.2 Auditoría de las prácticas específicas

**Tabla 5.** Matriz 2.1: Diagnóstico de capacidad CMMI por área de práctica.

| PA | Práctica específica | Criterio / evidencia requerida | Valor medido / estado | Nivel de capacidad |
| --- | --- | --- | --- | --- |
| ESTIM | Estimar el alcance y el tamaño del trabajo | Historias estimadas con técnica formal (Planning Poker, puntos de historia en Fibonacci) | **Cumple.** 133 SP para el proyecto, 21 SP para el INC-1 y 18 SP para el INC-2 (Entregable S3-4, Tabla 19); los 18 SP del INC-2 se cerraron 18/18 (Entregable S9, Tabla 5) | (ver fila siguiente) |
| ESTIM | Estimar el esfuerzo en horas y contrastarlo con lo real | Horas planificadas frente a horas reales por sprint y recalibración de la velocidad | **No cumple.** El INC-1 se estimó en 113 horas-persona (S3-4, Tabla 20), pero el informe integrador de S6 consigna que no hay registro de horas reales; los valores de la Tabla 27 del S3-4 son un escenario simulado. No se recalibró la velocidad (20 SP por sprint) | **Nivel 1 (Ejecutado)** |
| PLAN | Establecer el plan, los hitos y las dependencias | WBS, cronograma de sprints, hitos, ruta crítica, responsables por rol | **Cumple.** Entregable S3-4 con WBS, Gantt, red y ruta crítica, hitos H1 y H2 y asignación por rol | (ver fila siguiente) |
| PLAN | Dar seguimiento y mantener el plan | Desviaciones medidas y plan replanificado | **Cumple parcialmente.** El hito H2 se planificó para el 12/10/2026; el 50 % del INC-2 se alcanzó el 16/10 y el cierre el 17/10 (etiqueta `v2.0-Inc2` el 18/10). La desviación, su causa y la replanificación del INC-3 al Sprint 5 están documentadas (S9, Tabla 6). No se pudo verificar el tablero de GitHub Projects | **Nivel 2 (Gestionado)** |
| PQA | Evaluar objetivamente los productos con criterios definidos | Definición de terminado (DoD) por actividad y por historia | **Cumple.** DoD de 13 actividades (S3-4, Tabla 8) y de 6 condiciones por historia (Tabla 9) | (ver fila siguiente) |
| PQA | Aplicar lista de chequeo de revisión de código y registrar las desviaciones | Plantilla de *pull request*, aprobación de revisor y registro | **No cumple.** No existe `.github/pull_request_template.md`; la DoD (S3-4, Tabla 8, fila «Implementación») exige aprobación de al menos un revisor, pero no hay registro verificable de las aprobaciones en el repositorio. Los *pull requests* #1, #2 y #4 se integraron sin lista de chequeo documentada | **Nivel 1 (Ejecutado)** |
| CM | Establecer la línea base y las etiquetas de versión | Etiquetas publicadas por incremento | **Cumple.** `v1.0-PMV` (30/09/2026), `v1.5.0-inc2-avance` (17/10/2026) y `v2.0-Inc2` (18/10/2026), publicadas en `origin` | (ver fila siguiente) |
| CM | Controlar los cambios y las ramas | Estrategia de ramas, integración mediante *pull request*, historial trazable | **Cumple parcialmente.** Tres integraciones a `main` mediante *pull request* (#1 desde `desarrollo-anemia`; #2 y #4, esta última desde `feature/inc2-agenda-alertas`); otros cinco *commits* entraron directamente a `main`. Una rama `develop` se usó durante el Incremento 1 y hoy no existe; no hay convención escrita de ramas. Varios mensajes de *commit* no describen el cambio («Supabase v1», «Subiendo a produccion») y las etiquetas no siguen un formato uniforme. La etiqueta `v1.0-PMV` apunta al commit `9ce90c3`, que no pertenece al historial de `main` | **Nivel 2 (Gestionado)** |
| VER | Verificar el código con pruebas automáticas antes de integrar | Pruebas unitarias y de integración, cobertura, ejecución en CI | **Cumple.** 349 pruebas aprobadas el 30/10/2026; cobertura 99,50 % (umbral de la DoD: 80 %); el flujo `ci.yml` ejecuta pruebas, cobertura, PostgreSQL y E2E en cada *push* a `main`, `develop` y `feature/**` y en cada *pull request* hacia `main` o `develop` | (ver fila siguiente) |
| VER | Analizar el código de forma estática y revisar la arquitectura | Linter o SonarQube, reglas de arquitectura | **Cumple parcialmente.** Ruff (reglas E, F, W, I, B, UP, S y complejidad ≤ 12): 0 hallazgos; 18 pruebas de arquitectura. SonarCloud está configurado en el CI, pero la organización está sin definir (`REEMPLAZAR_ORGANIZACION`) y no existe un reporte | **Nivel 2 (Gestionado)** |
| VAL | Validar el producto con criterios de aceptación y evidencia visual | Criterios Dado-Cuando-Entonces por RF y capturas | **Cumple.** 48 de 48 criterios verificados en 9 RF; capturas de entrada y resultado por RF (sección 6) | (ver fila siguiente) |
| VAL | Obtener la aceptación del usuario final | Acta de aceptación o instrumento de satisfacción aplicado | **No cumple.** El SUS no se ha aplicado; las firmas de QA y del Product Owner están pendientes; no hay piloto con usuarios reales | **Nivel 1 (Ejecutado)** |

### 4.3 Resumen de capacidad

**Tabla 6.** Nivel de capacidad alcanzado por área de práctica.

| PA | Nivel actual | Nivel objetivo | Brecha | Principal razón |
| --- | --- | --- | --- | --- |
| ESTIM | 1 | 2 | 1 | Sin registro de horas reales ni recalibración |
| PLAN | 2 | 3 | 1 | Plan y replanificación documentados; tablero no verificable |
| PQA | 1 | 2 | 1 | Sin plantilla de *pull request* ni lista de chequeo |
| CM | 2 | 3 | 1 | Etiquetas y *pull requests* sí; falta convención de ramas y de *commits* |
| VER | 2 | 3 | 1 | Verificación sólida; SonarCloud sin activar |
| VAL | 1 | 2 | 1 | Validación funcional sin aceptación del usuario |

El perfil resultante es de tres áreas en Nivel 2 y tres en Nivel 1. Es coherente con un proyecto cuya ingeniería (VER, CM) está automatizada y cuyas prácticas de gestión y de aseguramiento de calidad dependen todavía del criterio individual.

---

## 5. AUDITORÍA DE PRODUCTOS DE TRABAJO / WORK PRODUCTS (Actividad 3)

Cada producto se contrastó con su ubicación real en el repositorio. La columna «Estado» distingue **Aprobado** (cumple su criterio con evidencia verificada), **Aprobado con observaciones** (cumple, con una limitación identificada), **Pendiente de verificación** (el producto existe, pero no se pudo comprobar su criterio) y **Pendiente** (el producto no existe).

**Tabla 7.** Matriz 3.1: Lista de chequeo de productos de trabajo.

| Fase del proceso | Producto de trabajo | Ubicación / evidencia | Criterio de calidad CMMI | Estado |
| --- | --- | --- | --- | --- |
| Requisitos | *Backlog* priorizado e historias con criterios de aceptación | `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` (historias HIST-1.1 a HIST-2.4); 48 criterios Dado-Cuando-Entonces verificados en `entregables/semana-09/metricas/datos/m21_cobertura_rf.json` | Criterios redactados en formato Dado-Cuando-Entonces y trazables a una prueba | **Aprobado** |
| Planificación | Estimación, WBS, cronograma e hitos | `entregables/semana-03-04/` (Tablas 11 y 19 a 25) | Plan estimado, con responsables y desviaciones registradas | **Aprobado con observaciones**: no hay horas reales ni evidencia del tablero de GitHub Projects |
| Diseño | Arquitectura hexagonal, modelo C4 y decisiones (ADR) | `pmv_fastapi/docs/adr/` (ADR-001 a ADR-011), `pmv_fastapi/docs/diagramas/` (C4 de contexto, contenedores y componentes), `diagramas/` | Diagramas de componentes, puertos y adaptadores y decisiones justificadas | **Aprobado** |
| Construcción | Código fuente e historial de *commits* | `pmv_fastapi/app/` (dominio sin dependencias externas; puertos de entrada y salida; adaptadores) y 17 *commits* en `main` | Estructura conforme a la arquitectura y mensajes de *commit* descriptivos | **Aprobado con observaciones**: 18 pruebas de arquitectura en verde; varios mensajes de *commit* no son descriptivos |
| Verificación | Pruebas automáticas y cobertura | `pmv_fastapi/tests/` (234 unitarias, 97 de integración, 18 de arquitectura; 17 E2E) y `pmv_fastapi/docs/evidencias/` | Pruebas en verde y cobertura mayor o igual al 80 % | **Aprobado**: 349 aprobadas y 99,50 % de cobertura (30/10/2026) |
| Validación | Evidencias funcionales por requerimiento | `entregables/semana-09/evidencias_capturas/RF-01` a `RF-09` y `INDICE.md` | Captura de entrada y de salida para cada RF | **Aprobado**: 9 de 9 RF |
| Gestión de defectos | Registro de defectos | `pmv_fastapi/docs/evidencias/registro_defectos.md` y `registro_defectos_inc2.md` (DEF-01 a DEF-09) | Defectos con causa, corrección y verificación de la corrección | **Aprobado**: 9 cerrados; 8 con prueba de regresión automatizada y DEF-01 (rendimiento) verificado con prueba de carga |
| Configuración | Etiquetas de versión | `v1.0-PMV`, `v1.5.0-inc2-avance`, `v2.0-Inc2` en `origin` | Una etiqueta por incremento liberado | **Aprobado con observaciones**: ninguna etiqueta cubre el estado actual de `main` (autenticación y producción) |
| Configuración | Artefacto de despliegue | `pmv_fastapi/Dockerfile`, `docker-compose.yml`, job `imagen` de `.github/workflows/ci.yml` | Imagen que se construye sin errores | **Pendiente de verificación**: el Dockerfile y el job existen, pero el motor de contenedores no estaba activo y no se pudo reconstruir la imagen |
| Despliegue | Servicio en producción y guía de despliegue | `pmv_fastapi/docs/DESPLIEGUE.md`; <https://softwareanemia.onrender.com/api/salud> | Servicio accesible y prueba de humo superada | **Aprobado**: el 30/10/2026 respondió HTTP 200 con `{"estado":"ok"}` en 22,5 s |
| Aseguramiento de calidad | Plantilla de revisión de *pull request* y lista de chequeo | No existe | Lista de chequeo derivada de la DoD aplicada a cada integración | **Pendiente** |

**Síntesis de la auditoría.** De los once productos auditados, seis están aprobados, tres están aprobados con observaciones, uno está pendiente de verificación y uno no existe. La auditoría del *backlog* se hizo sobre el entregable S3-4; no se pudo auditar el tablero de GitHub Projects. Los productos de ingeniería (diseño, pruebas, evidencias, defectos) están completos y son trazables; los productos de gestión y de aseguramiento de calidad son los menos desarrollados.

---

## 6. EVALUACIÓN DE VERIFICACIÓN (VER) Y VALIDACIÓN (VAL) CON CAPTURAS (Actividad 4)

### 6.1 Método y resultados globales de verificación

La **verificación** responde a si el software está bien construido; la **validación**, a si se construyó el software correcto. Para la verificación se ejecutaron el 30/10/2026, desde `pmv_fastapi/`, las comprobaciones del CI sobre el estado actual de `main`.

**Tabla 8.** Resultados de la verificación del 30/10/2026.

| Comprobación | Resultado |
| --- | --- |
| Pruebas por defecto (`pytest --cov=app`) | **349 aprobadas**, 0 fallidas, en unos 9 s (234 unitarias, 97 de integración y 18 de arquitectura) |
| Cobertura de `app/` (líneas y ramas) | **99,50 %** (1 675 sentencias; 5 sin cubrir). Todos los módulos de dominio y de aplicación en 100 %; `adapters/inbound/http/autenticacion.py` en 93,6 % |
| Análisis estático (Ruff) | **0 hallazgos**; 103 archivos con formato correcto |
| Contrato OpenAPI | `docs/openapi.json` **al día** |
| Pruebas E2E (Playwright) | 17 pruebas identificadas en `tests/e2e/` (15 de la versión v2.0 y 2 de inicio de sesión). **No se reejecutaron el 30/10/2026**; la última ejecución registrada (17 aprobadas, con Supabase simulado) consta en el informe de desarrollo del 23/10/2026 (`coordinacion/informes/2026-10-23_desarrollador_T-015.md`) |
| SonarQube / SonarCloud | **No ejecutado.** No existe reporte; el análisis estático efectivo es Ruff (salida exportada en el Anexo A) |
| Integración con PostgreSQL | Definida en el CI; no se reejecutó localmente |

Los 349 casos superan en 21 a los 328 de la semana 9 y la cobertura baja de 100 % a 99,50 %: la diferencia corresponde al código de autenticación incorporado después (`autenticacion.py` al 93,6 % y `supabase_auth.py` al 97 %), que las fichas de requerimientos no cubren (véase el hallazgo H4 de la sección 7). La suite se ejecuta con Python 3.14 en el equipo de evaluación; el CI y el Dockerfile usan Python 3.11.

La **validación** se sustenta en las capturas del software en ejecución tomadas con Chromium (Playwright, viewport 1366 × 900) el 16/10/2026 para RF-01 a RF-07 y el 17/10/2026 para RF-08 y RF-09. Las de RF-01 a RF-07 usan datos sintéticos; las de RF-08 y RF-09, una muestra de 500 niños del dataset anonimizado de la DIRESA Junín. Las capturas son anteriores a la autenticación; la funcionalidad de cada RF no cambió.

**Tabla 9.** Resumen de verificación y validación por requerimiento.

| RF | Requerimiento | Pruebas asociadas (unitarias / integración / E2E) | Criterios D-C-E verificados | Tiempo medido (umbral 2 s) | Estado |
| --- | --- | --- | --- | --- | --- |
| RF-01 | Registrar niño con evaluación inicial | 17 (9 / 7 / 1) | 100 % | 188 ms | VERIFICADO Y VALIDADO |
| RF-02 | Consultar y actualizar expediente; nuevo control | 7 (4 / 2 / 1) | 100 % | 97 a 107 ms | VERIFICADO Y VALIDADO |
| RF-03 | Validar datos con reglas clínicas | 14 (9 / 4 / 1) | 100 % | 830 ms (incluye 350 ms de antirrebote) | VERIFICADO Y VALIDADO |
| RF-04 | Listar niños en seguimiento | 10 (4 / 4 / 2) | 100 % | 32 a 288 ms | VERIFICADO Y VALIDADO |
| RF-05 | Reporte del periodo en JSON y CSV | 8 (4 / 3 / 1) | 100 % | 80 a 82 ms | VERIFICADO Y VALIDADO |
| RF-06 | Agenda de controles según la normativa | 28 (16 / 9 / 3) | 100 % | 119 ms | VERIFICADO Y VALIDADO |
| RF-07 | Controles vencidos y alertas priorizadas | 17 (10 / 5 / 2) | 100 % | 69 a 176 ms | VERIFICADO Y VALIDADO |
| RF-08 | Agenda del personal | 15 (8 / 4 / 3) | 100 % | 40 a 133 ms | VERIFICADO Y VALIDADO |
| RF-09 | Registro de asistencia a control | 26 (19 / 5 / 2) | 100 % | 54 a 92 ms | VERIFICADO Y VALIDADO |

Una misma prueba puede respaldar más de un RF, por lo que la suma de la tabla supera el total de pruebas; la columna E2E suma 16 de las 17 existentes porque las 2 de inicio de sesión no corresponden a un RF. Los conteos y los criterios proceden de `entregables/semana-09/metricas/datos/m21_cobertura_rf.json` (versión v2.0). Las pruebas unitarias y de integración pasan en la suite del 30/10/2026; las E2E se ejecutaron por última vez el 23/10/2026. «Verificado y validado» significa criterio Dado-Cuando-Entonces cumplido por ejecución automatizada con captura de resultado; **no implica aceptación firmada por un usuario**, que sigue pendiente (hallazgo H3).

### 6.2 Fichas CMMI de verificación y validación por requerimiento

Todas las fichas pertenecen al proyecto «Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín». El estado «VERIFICADO Y VALIDADO» significa que el criterio de aceptación se cumplió en una ejecución automatizada con captura de resultado, revisada por el evaluador de calidad; la aceptación del usuario final está pendiente (sección 6.3).

#### FICHA CMMI — RF-01 / HIST-1.1 (HU-01) · Registrar niño con evaluación inicial

| Campo | Detalle |
| --- | --- |
| **VER · Pruebas** | Ejecutadas: SÍ · Aprobadas: SÍ (17 pruebas: 9 unitarias, 7 de integración, 1 E2E) |
| **VER · Cobertura** | `servicio_expediente.py`, `validaciones.py` y `api.py` en 100 %; cobertura global de `app/`: 99,50 % (herramienta: pytest-cov) |
| **VER · Análisis estático** | Ruff: 0 hallazgos (reglas de errores, seguridad y complejidad ≤ 12); SonarQube no ejecutado |
| **VER · Estructura** | Conforme a la arquitectura hexagonal: 18 pruebas de arquitectura en verde |
| **VAL · Criterio de aceptación** | **Dado que** el personal completa el formulario con datos válidos, **cuando** presiona «Guardar registro», **entonces** el sistema almacena el registro, muestra la confirmación y abre el expediente en menos de 2 s |
| **VAL · Resultado** | Aprobado por el evaluador de calidad (ejecución automatizada); aceptación del usuario pendiente. Confirmación en 188 ms; un DNI repetido responde HTTP 409 y no duplica el expediente |
| **Fecha · Evaluador** | VER: 30/10/2026; VAL (captura): 16/10/2026 · QA Lead (Huamani Rodriguez, Jean Piero); firma pendiente |
| **Estado final CMMI** | **VERIFICADO Y VALIDADO** |

![Figura 1. RF-01, captura 1: datos de entrada (elaboración propia)](../semana-09/evidencias_capturas/RF-01/RF01_inc1_paso1_entrada.png)

![Figura 2. RF-01, captura 2: resultado en pantalla (elaboración propia)](../semana-09/evidencias_capturas/RF-01/RF01_inc1_paso2_resultado.png)

#### FICHA CMMI — RF-02 / HIST-1.2 (HU-02) · Consultar y actualizar el expediente

| Campo | Detalle |
| --- | --- |
| **VER · Pruebas** | Ejecutadas: SÍ · Aprobadas: SÍ (7 pruebas: 4 unitarias, 2 de integración, 1 E2E) |
| **VER · Cobertura** | `servicio_expediente.py` y `api.py` en 100 %; cobertura global de `app/`: 99,50 % (herramienta: pytest-cov) |
| **VER · Análisis estático** | Ruff: 0 hallazgos (reglas de errores, seguridad y complejidad ≤ 12); SonarQube no ejecutado |
| **VER · Estructura** | Conforme a la arquitectura hexagonal: 18 pruebas de arquitectura en verde |
| **VAL · Criterio de aceptación** | **Dado que** existe un expediente, **cuando** se consulta y se actualizan campos permitidos y se agrega un nuevo control, **entonces** los cambios persisten, el historial anterior se conserva y hay confirmación en menos de 2 s |
| **VAL · Resultado** | Aprobado por el evaluador de calidad (ejecución automatizada); aceptación del usuario pendiente. Consulta en 98 ms; actualización en 107 ms (comunidad y celular persistidos); nuevo control en 97 ms (evaluaciones de 2 a 3) |
| **Fecha · Evaluador** | VER: 30/10/2026; VAL (captura): 16/10/2026 · QA Lead (Huamani Rodriguez, Jean Piero); firma pendiente |
| **Estado final CMMI** | **VERIFICADO Y VALIDADO** |

![Figura 3. RF-02, captura 1: datos de entrada (elaboración propia)](../semana-09/evidencias_capturas/RF-02/RF02_inc1_paso1_entrada.png)

![Figura 4. RF-02, captura 2: expediente consultado (elaboración propia)](../semana-09/evidencias_capturas/RF-02/RF02_inc1_paso2_resultado.png)

#### FICHA CMMI — RF-03 / HIST-1.3 (HU-03) · Validar datos con reglas clínicas

| Campo | Detalle |
| --- | --- |
| **VER · Pruebas** | Ejecutadas: SÍ · Aprobadas: SÍ (14 pruebas: 9 unitarias, 4 de integración, 1 E2E), con valores frontera clínicos |
| **VER · Cobertura** | `validaciones.py`, `reglas_clinicas.py` y `clasificacion.py` en 100 %; cobertura global de `app/`: 99,50 % (herramienta: pytest-cov) |
| **VER · Análisis estático** | Ruff: 0 hallazgos (reglas de errores, seguridad y complejidad ≤ 12); SonarQube no ejecutado |
| **VER · Estructura** | Conforme a la arquitectura hexagonal: 18 pruebas de arquitectura en verde |
| **VAL · Criterio de aceptación** | **Dado que** se digitan datos clínicos, **cuando** se ingresa la hemoglobina, **entonces** la vista previa muestra la hemoglobina ajustada y la clasificación; y si los datos son inválidos, se rechazan con un mensaje comprensible por campo |
| **VAL · Resultado** | Aprobado por el evaluador de calidad (ejecución automatizada); aceptación del usuario pendiente. Vista previa «Anemia moderada» (Hb ajustada 9,1 g/dL) en 830 ms; el rechazo marca 2 campos y responde HTTP 422 |
| **Fecha · Evaluador** | VER: 30/10/2026; VAL (captura): 16/10/2026 · QA Lead (Huamani Rodriguez, Jean Piero); firma pendiente |
| **Estado final CMMI** | **VERIFICADO Y VALIDADO** |

![Figura 5. RF-03, captura 1: datos de entrada sin hemoglobina (elaboración propia)](../semana-09/evidencias_capturas/RF-03/RF03_inc1_paso1_entrada.png)

![Figura 6. RF-03, captura 2: vista previa de la validación clínica (elaboración propia)](../semana-09/evidencias_capturas/RF-03/RF03_inc1_paso2_resultado.png)

#### FICHA CMMI — RF-04 / HIST-1.4 (HU-04) · Listar niños en seguimiento

| Campo | Detalle |
| --- | --- |
| **VER · Pruebas** | Ejecutadas: SÍ · Aprobadas: SÍ (10 pruebas: 4 unitarias, 4 de integración, 2 E2E) |
| **VER · Cobertura** | `servicio_expediente.py` y `api.py` en 100 %; cobertura global de `app/`: 99,50 % (herramienta: pytest-cov) |
| **VER · Análisis estático** | Ruff: 0 hallazgos (reglas de errores, seguridad y complejidad ≤ 12); SonarQube no ejecutado |
| **VER · Estructura** | Conforme a la arquitectura hexagonal: 18 pruebas de arquitectura en verde |
| **VAL · Criterio de aceptación** | **Dado que** hay niños en seguimiento, **cuando** se filtra por clasificación o se busca por comunidad, **entonces** el listado respeta el filtro y muestra el estado de control de cada niño en menos de 2 s |
| **VAL · Resultado** | Aprobado por el evaluador de calidad (ejecución automatizada); aceptación del usuario pendiente. Filtro «Anemia leve»: 7 de 7 filas en 32 ms; búsqueda «Palmayoc»: 4 de 4 filas en 288 ms |
| **Fecha · Evaluador** | VER: 30/10/2026; VAL (captura): 16/10/2026 · QA Lead (Huamani Rodriguez, Jean Piero); firma pendiente |
| **Estado final CMMI** | **VERIFICADO Y VALIDADO** |

![Figura 7. RF-04, captura 1: listado sin filtros (elaboración propia)](../semana-09/evidencias_capturas/RF-04/RF04_inc1_paso1_entrada.png)

![Figura 8. RF-04, captura 2: filtro por clasificación (elaboración propia)](../semana-09/evidencias_capturas/RF-04/RF04_inc1_paso2_resultado.png)

#### FICHA CMMI — RF-05 / HIST-1.5 (HU-05) · Reporte del periodo

| Campo | Detalle |
| --- | --- |
| **VER · Pruebas** | Ejecutadas: SÍ · Aprobadas: SÍ (8 pruebas: 4 unitarias, 3 de integración, 1 E2E), incluida la regresión de la zona horaria y de fechas extremas |
| **VER · Cobertura** | `servicio_expediente.py` y `api.py` en 100 %; cobertura global de `app/`: 99,50 % (herramienta: pytest-cov) |
| **VER · Análisis estático** | Ruff: 0 hallazgos (reglas de errores, seguridad y complejidad ≤ 12); SonarQube no ejecutado |
| **VER · Estructura** | Conforme a la arquitectura hexagonal: 18 pruebas de arquitectura en verde |
| **VAL · Criterio de aceptación** | **Dado que** se elige un periodo válido, **cuando** se pulsa «Generar», **entonces** se muestran los indicadores y el mismo conjunto puede descargarse como CSV, en menos de 2 s |
| **VAL · Resultado** | Aprobado por el evaluador de calidad (ejecución automatizada); aceptación del usuario pendiente. Reporte en 82 ms (15 niños registrados, igual al valor de la API); CSV en 80 ms con 15 filas |
| **Fecha · Evaluador** | VER: 30/10/2026; VAL (captura): 16/10/2026 · QA Lead (Huamani Rodriguez, Jean Piero); firma pendiente |
| **Estado final CMMI** | **VERIFICADO Y VALIDADO** |

![Figura 9. RF-05, captura 1: periodo seleccionado (elaboración propia)](../semana-09/evidencias_capturas/RF-05/RF05_inc1_paso1_entrada.png)

![Figura 10. RF-05, captura 2: reporte generado (elaboración propia)](../semana-09/evidencias_capturas/RF-05/RF05_inc1_paso2_resultado.png)

#### FICHA CMMI — RF-06 / HIST-2.1 · Agenda de controles según la normativa

| Campo | Detalle |
| --- | --- |
| **VER · Pruebas** | Ejecutadas: SÍ · Aprobadas: SÍ (28 pruebas: 16 unitarias, 9 de integración, 3 E2E), con valores frontera de la agenda |
| **VER · Cobertura** | `domain/service/agenda.py` (124 sentencias), `model/agenda.py` y `servicio_agenda.py` en 100 %; cobertura global de `app/`: 99,50 % (herramienta: pytest-cov) |
| **VER · Análisis estático** | Ruff: 0 hallazgos (reglas de errores, seguridad y complejidad ≤ 12); SonarQube no ejecutado |
| **VER · Estructura** | Conforme a la arquitectura hexagonal: 18 pruebas de arquitectura en verde |
| **VAL · Criterio de aceptación** | **Dado que** existe un niño con anemia en tratamiento, **cuando** se abre su expediente, **entonces** se muestra la agenda normativa con el estado de cada control (cumplido, pendiente, próximo o vencido) en menos de 2 s |
| **VAL · Resultado** | Aprobado por el evaluador de calidad (ejecución automatizada); aceptación del usuario pendiente. Agenda de 13 controles (2 cumplidos, 9 pendientes y 2 vencidos) en 119 ms, igual a la API |
| **Fecha · Evaluador** | VER: 30/10/2026; VAL (captura): 16/10/2026 · QA Lead (Huamani Rodriguez, Jean Piero); firma pendiente |
| **Estado final CMMI** | **VERIFICADO Y VALIDADO** |

![Figura 11. RF-06, captura 1: niño seleccionado en el seguimiento (elaboración propia)](../semana-09/evidencias_capturas/RF-06/RF06_inc2_paso1_entrada.png)

![Figura 12. RF-06, captura 2: agenda de controles del expediente (elaboración propia)](../semana-09/evidencias_capturas/RF-06/RF06_inc2_paso2_resultado.png)

#### FICHA CMMI — RF-07 / HIST-2.2 · Controles vencidos y alertas priorizadas

| Campo | Detalle |
| --- | --- |
| **VER · Pruebas** | Ejecutadas: SÍ · Aprobadas: SÍ (17 pruebas: 10 unitarias, 5 de integración, 2 E2E), con filtros por prioridad y comunidad |
| **VER · Cobertura** | `domain/service/alertas.py`, `model/alertas.py` y `servicio_alertas.py` en 100 %; cobertura global de `app/`: 99,50 % (herramienta: pytest-cov) |
| **VER · Análisis estático** | Ruff: 0 hallazgos (reglas de errores, seguridad y complejidad ≤ 12); SonarQube no ejecutado |
| **VER · Estructura** | Conforme a la arquitectura hexagonal: 18 pruebas de arquitectura en verde |
| **VAL · Criterio de aceptación** | **Dado que** hay niños con controles, **cuando** se abre la pestaña «Alertas» y se filtra por prioridad o comunidad, **entonces** se listan los controles vencidos priorizados con su resumen en menos de 2 s |
| **VAL · Resultado** | Aprobado por el evaluador de calidad (ejecución automatizada); aceptación del usuario pendiente. Pestaña en 176 ms; filtro «Alta»: 7 filas en 69 ms; filtro «Huaycha»: 1 de 1 fila en 70 ms |
| **Fecha · Evaluador** | VER: 30/10/2026; VAL (captura): 16/10/2026 · QA Lead (Huamani Rodriguez, Jean Piero); firma pendiente |
| **Estado final CMMI** | **VERIFICADO Y VALIDADO** |

![Figura 13. RF-07, captura 1: pestaña de alertas sin filtros (elaboración propia)](../semana-09/evidencias_capturas/RF-07/RF07_inc2_paso1_entrada.png)

![Figura 14. RF-07, captura 2: filtro por prioridad (elaboración propia)](../semana-09/evidencias_capturas/RF-07/RF07_inc2_paso2_resultado_filtro_prioridad.png)

#### FICHA CMMI — RF-08 / HIST-2.3 · Agenda del personal

| Campo | Detalle |
| --- | --- |
| **VER · Pruebas** | Ejecutadas: SÍ · Aprobadas: SÍ (15 pruebas: 8 unitarias, 4 de integración, 3 E2E), incluida la vista móvil |
| **VER · Cobertura** | `domain/service/agenda_personal.py`, `model/agenda_personal.py` y `servicio_agenda_personal.py` en 100 %; cobertura global de `app/`: 99,50 % (herramienta: pytest-cov) |
| **VER · Análisis estático** | Ruff: 0 hallazgos (reglas de errores, seguridad y complejidad ≤ 12); SonarQube no ejecutado |
| **VER · Estructura** | Conforme a la arquitectura hexagonal: 18 pruebas de arquitectura en verde |
| **VAL · Criterio de aceptación** | **Dado que** existen controles programados, **cuando** se consulta un rango de hasta 31 días y se filtra por establecimiento o comunidad, **entonces** se listan los controles por día con el total y el desglose por estado, coherentes con la API, en menos de 2 s |
| **VAL · Resultado** | Aprobado por el evaluador de calidad (ejecución automatizada); aceptación del usuario pendiente. Consulta del rango en 133 ms; filtro por establecimiento en 40 ms. Datos de la muestra DIRESA Junín |
| **Fecha · Evaluador** | VER: 30/10/2026; VAL (captura): 17/10/2026 · QA Lead (Huamani Rodriguez, Jean Piero); firma pendiente |
| **Estado final CMMI** | **VERIFICADO Y VALIDADO** |

![Figura 15. RF-08, captura 1: rango de fechas de entrada (elaboración propia)](../semana-09/evidencias_capturas/RF-08/RF08_inc2final_paso1_entrada.png)

![Figura 16. RF-08, captura 2: agenda del personal por día (elaboración propia)](../semana-09/evidencias_capturas/RF-08/RF08_inc2final_paso2_resultado.png)

#### FICHA CMMI — RF-09 / HIST-2.4 · Registro de asistencia a control

| Campo | Detalle |
| --- | --- |
| **VER · Pruebas** | Ejecutadas: SÍ · Aprobadas: SÍ (26 pruebas: 19 unitarias, 5 de integración, 2 E2E), incluido el rechazo del segundo registro |
| **VER · Cobertura** | `domain/service/asistencia.py`, `model/asistencia.py` y `servicio_asistencia.py` en 100 %; cobertura global de `app/`: 99,50 % (herramienta: pytest-cov) |
| **VER · Análisis estático** | Ruff: 0 hallazgos (reglas de errores, seguridad y complejidad ≤ 12); SonarQube no ejecutado |
| **VER · Estructura** | Conforme a la arquitectura hexagonal: 18 pruebas de arquitectura en verde |
| **VAL · Criterio de aceptación** | **Dado que** existe un control programado sin registro, **cuando** el personal registra «Asistió» o «No asistió» con motivo, **entonces** el control queda cumplido o marcado como inasistencia (con la alerta elevada un nivel) y un segundo registro se rechaza con HTTP 409, en menos de 2 s |
| **VAL · Resultado** | Aprobado por el evaluador de calidad (ejecución automatizada); aceptación del usuario pendiente. «Asistió» en 90 ms; «No asistió» en 92 ms; segundo registro rechazado en 54 ms |
| **Fecha · Evaluador** | VER: 30/10/2026; VAL (captura): 17/10/2026 · QA Lead (Huamani Rodriguez, Jean Piero); firma pendiente |
| **Estado final CMMI** | **VERIFICADO Y VALIDADO** |

![Figura 17. RF-09, captura 1: control sin registro de asistencia (elaboración propia)](../semana-09/evidencias_capturas/RF-09/RF09_inc2final_paso1_entrada.png)

![Figura 18. RF-09, captura 2: control registrado como «Asistió» (elaboración propia)](../semana-09/evidencias_capturas/RF-09/RF09_inc2final_paso2_asistio.png)

### 6.3 Validación pendiente

La validación funcional se realizó con ejecuciones automatizadas y datos sintéticos o anonimizados. Queda pendiente la validación con usuarios reales: aplicar el instrumento SUS (`entregables/semana-09/metricas/instrumento_SUS.md`), obtener el acta de aceptación del Product Owner y las firmas de QA. Además, la autenticación con Supabase Auth, incorporada después de la semana 9, no tiene todavía ficha de VER y VAL ni captura propias; su verificación local consta en el informe de desarrollo del 23/10/2026 (`coordinacion/informes/2026-10-23_desarrollador_T-015.md`) y en el ADR-011.

---

## 7. ANÁLISIS DE CAUSA RAÍZ (CAR) Y PLAN DE MEJORA CONTINUA (Actividad 5)

### 7.1 Hallazgos de la evaluación

**Tabla 10.** Hallazgos y análisis de causa raíz.

| ID | Área | Hallazgo / brecha identificada | Síntoma observable | Causa raíz del proceso |
| --- | --- | --- | --- | --- |
| H1 | ESTIM | No se registra el esfuerzo real, por lo que la estimación no se contrasta ni se recalibra | El INC-1 tiene 113 horas-persona estimadas y ninguna real; el INC-2 se completó 5 días después del hito H2 (17/10 frente al 12/10/2026) | El tablero no tiene un campo de horas reales y la retrospectiva no incluye la revisión de la velocidad; el Sprint 3 compartió capacidad con el informe integrador sin holgura |
| H2 | PQA | Las revisiones de código no son consistentes ni dejan evidencia | No existe plantilla de *pull request*; no hay registro verificable de aprobaciones, aunque la DoD las exige | La DoD vive en un documento académico, no en la herramienta donde se integra el código |
| H3 | VAL | No existe aceptación del usuario ni medición de satisfacción | SUS sin aplicar; firmas de QA pendientes | La validación se planificó como evidencia automatizada y no se reservó tiempo del Product Owner en el cronograma |
| H4 | VER | El análisis estático efectivo es solo Ruff y el código nuevo de autenticación quedó fuera de las fichas | SonarCloud sin organización (`REEMPLAZAR_ORGANIZACION`); `autenticacion.py` con 93,6 % y `supabase_auth.py` con 97 % de cobertura; login sin ficha de VER y VAL | La autenticación se incorporó fuera de un incremento planificado y sin pasar por la DoD |
| H5 | CM | Historial y versiones poco trazables | Mensajes de *commit* como «Supabase v1» y «Subiendo a produccion»; ninguna etiqueta cubre `main` actual; no hay rama `develop` | No existe convención escrita de *commits*, ramas ni etiquetas |
| H6 | VER | Defectos que escaparon pese a una cobertura cercana al 100 % (DEF-03 a DEF-08, hallados en el ciclo del Incremento 2) | 6 de 7 defectos funcionales del Incremento 1 no se detectaron antes de liberar | Las pruebas del PMV verificaban casos válidos y no entradas hostiles (NaN, Unicode, fechas extremas, textos enormes, comodines, concurrencia) |

Se aplicó la técnica de los cinco porqués a los hallazgos de mayor impacto. En todos los casos la causa raíz se atribuye al último eslabón, una condición del proceso, y no a las personas.

**Tabla 11.** Cinco porqués de los hallazgos H1, H2, H3 y H6.

| Hallazgo | Porqué 1 | Porqué 2 | Porqué 3 | Porqué 4 | Porqué 5 (causa raíz) |
| --- | --- | --- | --- | --- | --- |
| H1 · El INC-2 se cerró 5 días después del hito H2 | El Sprint 3 no alcanzó a terminarlo | Absorbió además el integrador de S6 y la reestructuración hexagonal (ADR-008) | La capacidad del sprint no se contrastó con datos reales | No hay horas reales registradas | El tablero y la retrospectiva no exigen registrar el esfuerzo |
| H2 · Revisiones de código sin evidencia | No se puede comprobar quién revisó cada cambio | La DoD pide un revisor, pero nada obliga a registrarlo | No hay lista de chequeo en el *pull request* | La plantilla de *pull request* no existe | La DoD vive en un documento y no en la herramienta de integración |
| H3 · Sin aceptación del usuario | No hay acta ni SUS | No se coordinó una sesión con el personal de salud | La validación se planificó como evidencia automatizada | El cronograma no reserva tiempo del Product Owner | La aceptación del usuario no figura como criterio de cierre del incremento |
| H6 · Defectos escapados con alta cobertura | Las pruebas no incluían entradas hostiles | Se verificaron los casos válidos y los límites esperados | La cobertura de líneas se tomó como indicador de calidad suficiente | La DoD no exigía pruebas exploratorias | La DoD mide cuánto código se ejecuta y no la variedad de entradas |

### 7.2 Plan de mejora continua

Las acciones se programan para el Sprint 5 (27/10 al 09/11/2026) y los días posteriores, y se asignan según el rol de cada integrante (Tabla 2). Para H6 se conserva la acción ya definida en el informe de la semana 9 (PDCA, acción 2).

**Tabla 12.** Matriz 5.1: Plan de mejora CMMI del proceso y del producto.

| N.° | Área | Hallazgo | Causa raíz | Acción de mejora | Impacto esperado / métrica | Responsable | Fecha objetivo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ESTIM | H1 | Sin registro de esfuerzo real ni recalibración | Añadir al tablero el campo «horas reales» por tarea, registrado al cerrarla; desagregar tareas a máximo 6 horas con Planning Poker; recalibrar la velocidad (20 SP por sprint) al cierre de cada sprint | Desviación de esfuerzo por historia menor o igual a ±20 % (umbral del S3-4), reducible a ±10 % con tres sprints de datos; 100 % de las tareas con horas reales | Porras V. | Inicio: 03/11/2026; primera recalibración: 09/11/2026 | Planificada |
| 2 | PQA | H2 | La DoD no está en la herramienta de integración | Crear `.github/pull_request_template.md` con la lista de la DoD (Tabla 9 del S3-4) y activar la protección de `main` que exija un revisor aprobado | 100 % de los *pull requests* con lista de chequeo y aprobación registrada antes de integrar | Huamani R. | 06/11/2026 | Planificada |
| 3 | VER | H4, H6 | Análisis estático parcial; pruebas sin entradas hostiles | Definir `sonar.organization` y el secreto `SONAR_TOKEN` para activar SonarCloud en el CI; incorporar a la DoD las pruebas de entradas límite; añadir un *hook* de `pre-commit` con Ruff y las pruebas rápidas | Reporte de SonarCloud publicado con 0 incidencias críticas; 0 defectos escapados por incremento; ejecución previa a la integración en el 100 % de los *commits* locales | Huamani R. | 06/11/2026 | En curso: las pruebas de entradas límite se aplicaron en el Incremento 2; faltan SonarCloud y el *hook* |
| 4 | VER | H4 | Autenticación sin pasar por la DoD | Completar las pruebas de ramas de `autenticacion.py` (líneas 86, 100, 110, 126 y 130) y de `supabase_auth.py` (línea 64) hasta el 100 % y redactar la ficha de VER y VAL del inicio y cierre de sesión | Cobertura global de 100 %; ficha de autenticación con capturas | Auqui H. | 09/11/2026 | Planificada |
| 5 | VAL | H3 | Sin tiempo reservado del Product Owner | Programar una sesión de aceptación con el personal de salud: tarea guiada, acta firmada y SUS con al menos cinco respondientes | SUS mayor o igual a 68 (Inc. 1) y 80 (Inc. 2), metas por confirmar; acta firmada por RF | Porras V. | 13/11/2026 | Planificada |
| 6 | CM | H5 | Sin convención de *commits*, ramas y etiquetas | Documentar la convención (mensajes con tipo y alcance, ramas `feature/*` y `develop`, etiquetas con versionado semántico) y etiquetar el estado desplegado en producción | 100 % de los *commits* nuevos con mensaje descriptivo; etiqueta que identifique la versión en producción | Auqui H. | 09/11/2026 | Planificada |
| 7 | PLAN | H1 | Capacidad compartida sin holgura | Reservar al menos 20 % de la capacidad de cada sprint para trabajo no planificado y registrar los cambios de alcance en el plan | Hitos con desviación menor a 3 días | Porras V. | Sprint 5 | Planificada |

---

## 8. CONCLUSIONES Y LECCIONES APRENDIDAS EN LA ADOPCIÓN DE CMMI

**Conclusiones.**

1. El proyecto tiene una base de ingeniería sólida: la verificación (VER) alcanza el Nivel 2 con 349 pruebas aprobadas, 99,50 % de cobertura, cero hallazgos de Ruff y reglas de arquitectura ejecutables. Los nueve requerimientos funcionales cuentan con ficha, criterio de aceptación, prueba automatizada y captura.
2. El perfil de capacidad es desigual. Tres áreas están en Nivel 2 (PLAN, CM y VER) y tres en Nivel 1 (ESTIM, PQA y VAL). Ninguna llega al Nivel 3 porque los estándares del equipo, como la DoD y la estrategia de ramas, no están incorporados a plantillas ni a controles automáticos.
3. Las brechas se concentran en las prácticas de gestión y de aseguramiento de calidad, no en la construcción del producto: faltan el esfuerzo real, la lista de chequeo de revisión, la aceptación del usuario y un reporte de análisis estático más completo.
4. La auditoría de los productos de trabajo confirma la trazabilidad entre requisito, diseño, código, prueba y evidencia. Los productos pendientes son la plantilla de revisión y la verificación de la imagen del contenedor.
5. El plan de mejora de la sección 7 ataca la causa raíz de cada brecha mediante cambios en la herramienta (campo de horas, plantilla de *pull request*, SonarCloud, *hook* de *pre-commit*) y no solo mediante recordatorios.

**Lecciones aprendidas.**

1. **Una cobertura alta no sustituye la verificación de casos hostiles.** Seis defectos del Incremento 1 escaparon con 99 % de cobertura; el estándar debe exigir entradas límite.
2. **Lo que no se registra no se puede estimar mejor.** Sin horas reales, la estimación en puntos no puede calibrarse; el registro debe formar parte del cierre de cada tarea.
3. **Los estándares deben vivir en la herramienta.** Una DoD escrita en un informe no se aplica por sí sola; una plantilla de *pull request* y una protección de rama la hacen exigible.
4. **Todo cambio posterior a un incremento debe pasar por el mismo proceso.** La autenticación se incorporó sin ficha de VER y VAL y quedó fuera de las métricas.
5. **Separar lo verificado de lo supuesto.** Distinguir una prueba automatizada de la aceptación de un usuario, y un archivo de configuración de un servicio ejecutado, evita sobrevalorar el nivel de capacidad.

---

## 9. ANEXOS Y EVIDENCIAS TÉCNICAS

### Anexo A. Reporte de pruebas, cobertura y análisis estático

Salidas reproducidas el 30/10/2026 desde `pmv_fastapi/` con Python 3.14 y las dependencias de `requirements-dev.txt`. Los reportes exportados completos están en `entregables/semana-11/anexos/ruff.txt` y `entregables/semana-11/anexos/cobertura_y_pruebas.txt` (cobertura por archivo con las líneas sin cubrir). Resumen:

```text
ruff check .                         -> All checks passed!
ruff format --check .                -> 103 files already formatted
python -m scripts.exportar_openapi --verificar -> docs/openapi.json está al día
pytest --cov=app --cov-report=term   -> 349 passed; Total coverage: 99.50 %
                                        (umbral fail_under = 80)
```

Las salidas históricas de cada versión (v1.0, v1.5 y v2.0), las métricas y los gráficos están en `entregables/semana-09/metricas/` y `pmv_fastapi/docs/evidencias/` (`cobertura.txt`, `cobertura.xml`, `ruff.txt` e `inc2/e2e.txt`). El análisis con SonarCloud no se ejecutó; la configuración está en `pmv_fastapi/sonar-project.properties`.

### Anexo B. Carpeta de capturas por requerimiento

Las capturas están en `entregables/semana-09/evidencias_capturas/`, organizadas en `RF-01/` a `RF-09/`, con el índice `INDICE.md` y el script reproducible `capturar_evidencias.py`. El índice incluye el criterio de aceptación, los tiempos medidos y la fecha de cada captura. Las fichas de la sección 6 enlazan dos capturas por requerimiento; el resto de pasos (por ejemplo, el rechazo de datos inválidos en RF-03 y el segundo registro con HTTP 409 en RF-09) están en la misma carpeta. Los campos de fecha de algunas capturas muestran el formato mm/dd/aaaa porque el navegador de captura usó la configuración regional en-US; la aplicación almacena y muestra las fechas en dd/mm/aaaa.

### Anexo C. Repositorio GitHub y etiquetas

- Repositorio: <https://github.com/woshtsu/ProcesosSoftwareAnemia>.
- `v1.0-PMV` (30/09/2026): Incremento 1, RF-01 a RF-05.
- `v1.5.0-inc2-avance` (17/10/2026): hito al 50 % del Incremento 2, commit `416dfbc`.
- `v2.0-Inc2` (18/10/2026): Incremento 2 completo, commit `fb26626`; es la etiqueta de la versión `v2.0` que menciona la guía.
- Estado actual de `main` (30/10/2026): commit `72e7025`, que añade autenticación con Supabase, integración y despliegue continuos y la guía `pmv_fastapi/docs/DESPLIEGUE.md`.
- Producción: <https://softwareanemia.onrender.com/> (`/api/salud` respondió HTTP 200 el 30/10/2026).

### Anexo D. Flujo de integración continua

El archivo `.github/workflows/ci.yml` define tres trabajos: `calidad-y-pruebas` (Ruff, pruebas con cobertura, contrato OpenAPI, integración con PostgreSQL 16, E2E con Playwright y SonarCloud si existe el secreto), `imagen` (construcción de la imagen Docker) y `produccion` (verificación del esquema y solicitud de despliegue en Render, solo desde `main`). La ejecución remota de este flujo no se verificó durante la elaboración de este informe.

### Anexo E. Referencias

- CMMI Institute (2018). *CMMI Development V2.0*. ISACA.
- Universidad Continental (2026). *Guía de trabajo 11: Evaluación de proceso y producto de software mediante el modelo CMMI (CMMI-DEV)*. Asignatura Procesos de Software (ASUC01702).
- Equipo del proyecto (2026). *Entregables S3-4 (plan, estimación y DoD), S5 (primer incremento), S6 (informe integrador) y S9 (evaluación GQM)*. Repositorio ProcesosSoftwareAnemia.
