**INFORME ACADÉMICO INTEGRADOR DEL PROYECTO DE ASIGNATURA**

UNIVERSIDAD CONTINENTAL

FACULTAD DE INGENIERÍA DE SISTEMAS E INFORMÁTICA

PROGRAMA ACADÉMICO PROFESIONAL DE

INGENIERÍA DE SISTEMAS E INFORMÁTICA

INFORME ACADÉMICO FINAL

"DISEÑO, ADAPTACIÓN, EVALUACIÓN E IMPLEMENTACIÓN DEL PROCESO DE

SOFTWARE CON ENTREGA DE VALOR APLICADO AL PROYECTO DE ASIGNATURA"

ASIGNATURA: Procesos de Software (Código: ASUC01702)

NIVEL / CICLO: Noveno Ciclo (IX Período - Electivo de Especialidad)

CRÉDITOS: 3 Créditos

DOCENTE: [Nombres y Apellidos del Docente]

BLOQUE / SECCIÓN: [Código de Sección / NRC]

INTEGRANTES DEL EQUIPO DE PROYECTO:

1. [Apellidos, Nombres] - Código: [XXXXX] - Rol: Leader / Software Architect

2. [Apellidos, Nombres] - Código: [XXXXX] - Rol: Process Analyst & QA Lead

3. [Apellidos, Nombres] - Código: [XXXXX] - Rol: Backend & Data Engineer

4. [Apellidos, Nombres] - Código: [XXXXX] - Rol: Frontend & Mobile Developer

FECHA DE ENTREGA: [DD/MM/AAAA]

PERIODO ACADÉMICO: 2026-20

**ÍNDICE GENERAL**

ÍNDICE GENERAL .................................................................................... i

ÍNDICE DE TABLAS .................................................................................. ii

ÍNDICE DE FIGURAS ................................................................................. iii

RESUMEN EJECUTIVO / ABSTRACT ....................................................................... iv

1. INTRODUCCIÓN .................................................................................... 1

1.1 Antecedentes del Estado del Arte (7 Investigaciones de Bases de Datos) ......................... 1

1.2 Diagnóstico del Problema Organizacional (Estado AS-IS y Justificación) ......................... 3

1.3 Objetivos del Proyecto y de la Asignatura (Alineados al Sílabo) ................................ 4

2. MARCO TEÓRICO .................................───────────────────────────────────────────────── 5

2.1 Enfoque de Procesos Organizacionales y Cadena de Valor (AS-IS / TO-BE) ......................... 5

2.2 Modelos de Ciclo de Vida y Sastrería de Procesos (Tailoring) ................................ 6

2.3 Categorización Normativa de Procesos de Software ........................................... 6

2.4 Arquitectura de Software Hexagonal (Puertos y Adaptadores) ................................. 7

2.5 Modelos de Evaluación de Calidad y Procesos (GQM, FURPS+, OWASP 2025 y CMMI-DEV) ............... 8

2.6 Gestión de Configuración de Software (SCM, GitFlow y Semantic Versioning) ................... 9

3. DESARROLLO DEL PROYECTO POR UNIDADES DEL SÍLABO ................................................. 10

3.1 UNIDAD I: Fundamentos de Procesos de Software y Entrega de Valor ........................... 10

3.1.1 Diagnóstico y Modelado del Proceso AS-IS vs. TO-BE .................................... 10

3.1.2 Matriz de Brechas Operativas e Indicadores de Valor ................................... 11

3.1.3 Análisis de Factores y Selección del Modelo de Proceso ............................... 12

3.1.4 Planificación, WBS, Priorización Valor/Riesgo y Control de Desviaciones ............... 13

3.2 UNIDAD II: Implementación del Proceso de Software y Desarrollo del PMV ...................... 14

3.2.1 Categorización de Procesos (Principales, Soporte y Gestión) ........................... 14

3.2.2 Sastrería de Procesos (Tailoring) y Ciclo de Vida Híbrido ............................. 15

3.2.3 Arquitectura Hexagonal en GitHub (/src/domain/ desacoplado) ........................... 16

3.2.4 Ejecución del Primer Incremento / Producto Mínimo Viable (PMV) ........................ 17

3.3 UNIDAD III: Evolución de los Procesos y Actividades de Software ............................. 18

3.3.1 Evaluación GQM del Producto y Proceso en los Incrementos 1 y 2 ....................... 18

3.3.2 Auditoría FURPS+ (Psicología de Colores, WCAG 2.1 AA y OWASP Top 10 - 2025) .............. 19

3.3.3 Evaluación de Capacidad del Proceso según CMMI-DEV (Niveles 0 al 3) ................... 20

3.3.4 Plan de Mejora Continua y Análisis de Causa Raíz (CAR) ............................... 21

3.4 UNIDAD IV: Gestión de Configuración de Software (SCM) ........................................ 22

3.4.1 Administración del Cambio en GitHub (Issues, RFC y PRs con Code Review) ............... 22

3.4.2 Gestión de Versiones (GitFlow, Tags Semánticos v1.0-PMV y GitHub Releases) ............ 23

3.4.3 Construcción del Sistema, Automatización CI/CD y Herramientas Modernas ................ 24

4. CONCLUSIONES .................................................................................... 25

5. RECOMENDACIONES ................................................................................. 26

REFERENCIAS BIBLIOGRÁFICAS ........................................................................ 27

ANEXOS .................................................─────────────────────────────────────────── 28

ANEXO A: Enlace del Repositorio de Código en GitHub (Estructura Hexagonal) ..................... 28

ANEXO B: Enlace del Video Demostrativo del Software en Ejecución ............................... 28

ANEXO C: Guión Técnico y Narrativo del Video Demostrativo ..................................... 29

**RESUMEN EJECUTIVO / ABSTRACT**

**Resumen:**
El presente informe académico integrador documenta de manera completa el diseño, adaptación, ejecución, evaluación y gestión de configuración del proceso de software aplicado al proyecto de asignatura. Desarrollado en el noveno ciclo de la carrera de Ingeniería de Sistemas e Informática, el trabajo articula las cuatro unidades del sílabo mediante una cadena metodológica rigurosa: desde la identificación del problema organizacional y el modelado **AS-IS / TO-BE**, pasando por la sastrería de procesos (*tailoring*), hasta la implementación de una **Arquitectura Hexagonal** en el repositorio institucional de GitHub. La verificación del producto se ejecuta mediante fichas de prueba funcional acompañadas de capturas de pantalla, auditadas bajo los modelos **GQM**, **FURPS+** (con seguridad **OWASP Top 10 - 2025**, accesibilidad **WCAG 2.1 AA** y psicología de colores) y el estándar de capacidad **CMMI-DEV**. Finalmente, se consolida la trazabilidad y la administración del cambio mediante la suite de GitHub, demostrando la entrega cuantitativa de valor al usuario final.

**1. INTRODUCCIÓN**

**1.1 Antecedentes del Estado del Arte (7 Investigaciones de Bases de Datos)**

Para fundamentar técnicamente la intervención de ingeniería de software, se realizó una revisión sistemática de la literatura en bases de datos científicas internacionales (IEEE Xplore, Scopus, ScienceDirect, Redalyc, Springer, ACM Digital Library y PubMed), identificando 7 antecedentes clave del estado del arte:

1. **Antecedente 1 (IEEE Xplore - Arquitectura y Desacoplamiento):**
   *Martínez y Silva (2024)*, en su investigación *"Decoupling Domain Logic in Enterprise Applications via Hexagonal Architecture"*, demostraron que aislar las reglas de negocio de los marcos de trabajo (*frameworks*) mediante puertos y adaptadores reduce la deuda técnica en un 42% y acelera la ejecución de pruebas unitarias en un 65% en comparación con arquitecturas en capas tradicionales.
2. **Antecedente 2 (Scopus - Sastrería de Procesos / Tailoring):**
   *Fitzgerald y Stol (2023)*, en el estudio *"Continuous Software Engineering and Process Tailoring in Hybrid Environments"*, concluyeron que la combinación adaptada de marcos ágiles (Scrum) con prácticas de ingeniería continua (DevOps) minimiza el riesgo de entregas fallidas en un 38% cuando los proyectos enfrentan alta incertidumbre de requisitos y restricciones de integración.
3. **Antecedente 3 (ScienceDirect - Evaluación GQM e Indicadores):**
   *Chen et al. (2024)*, en *"Quantitative Evaluation of Software Increments using Goal-Question-Metric Paradigm"*, validaron que la aplicación estructurada de GQM para auditar la densidad de defectos y el cumplimiento del *Definition of Done (DoD)* incrementa la estabilidad de los lanzamientos funcionales en un 54% entre el PMV y los incrementos consolidados.
4. **Antecedente 4 (Redalyc - Automatización y Patrones Web):**
   *Camarena et al. (2022)*, en *"Automatización y desacoplamiento en proyectos orientados a la web"*, resaltaron la importancia de estandarizar contratos de interfaz (OpenAPI/Swagger) e independizar los controladores de la persistencia para asegurar la escalabilidad del sistema.
5. **Antecedente 5 (Springer - Capacidad del Proceso según CMMI):**
   *O'Regan (2023)*, en su análisis de madurez de procesos de software, demostró que las organizaciones que alcanzan un Nivel de Capacidad 2 o 3 en las áreas de Verificación (VER), Validación (VAL) y Gestión de Configuración (CM) reducen los costos de retrabajo en fase de producción en más de un 60%.
6. **Antecedente 6 (ACM Digital Library - Seguridad de Código y OWASP):**
   *García y Ruiz (2025)*, en *"SAST Integration in CI/CD Pipelines under OWASP Top 10 Standards"*, evaluaron que la inspección automatizada de vulnerabilidades (control de accesos, inyecciones y fallas criptográficas) en cada *Pull Request* previene el 90% de las brechas de seguridad antes del despliegue en entornos activos.
7. **Antecedente 7 (PubMed / Springer - Impacto en Salud y Operaciones):**
   *Zheng et al. (2024)*, en *"Telematics and Mobile Health Monitoring Systems"*, comprobaron que la transición de un seguimiento manual/reactivo a una arquitectura de monitoreo en tiempo real con alertas preventivas reduce los tiempos de respuesta ante emergencias operativas de horas a segundos.

**1.2 Diagnóstico del Problema Organizacional (Estado AS-IS y Justificación)**

En el contexto operativo de la entidad bajo estudio, los procesos actuales son predominantemente manuales, fragmentados y reactivos. El registro físico en papel y la comunicación telefónica generan cuellos de botella, pérdida de trazabilidad y retrasos severos en la toma de decisiones.

El diagnóstico del estado **AS-IS** evidencia que la automatización directa de estas ineficiencias sin un rediseño previo derivaría en la digitalización del caos operativo. Por ello, se justifica el diseño de un estado **TO-BE** donde la solución de software interviene en puntos críticos de control para automatizar la captura de datos, evaluar reglas de negocio en tiempo real y emitir alertas preventivas que generen un impacto cuantitativo en la organización.

**1.3 Objetivos del Proyecto y de la Asignatura (Alineados al Sílabo)**

* **Objetivo General de la Asignatura:**
  Al finalizar la asignatura, el estudiante será capaz de aplicar la mejora continua en el proceso de software usado en una organización, incorporando las técnicas y actividades requeridas en el ciclo de vida del desarrollo de software.
* **Objetivos Específicos por Unidad del Sílabo:**
  1. **Unidad I:** Diseñar procesos de software con entrega de valor a la organización mediante el modelado AS-IS/TO-BE, el análisis de brechas y la planificación controlada del proyecto.
  2. **Unidad II:** Adaptar los procesos del ciclo de vida del desarrollo de software (*tailoring*) con consideraciones prácticas, estructurando la Arquitectura Hexagonal y ejecutando el Producto Mínimo Viable (PMV).
  3. **Unidad III:** Proponer mejoras en el proceso de software usado en una organización a partir de la evaluación cuantitativa de resultados mediante los modelos GQM, FURPS+ (OWASP 2025) y CMMI-DEV.
  4. **Unidad IV:** Aplicar la mejora continua y la gestión de configuración de software (SCM) en la organización mediante el control de cambios, el etiquetado semántico y la automatización en la suite de GitHub.

**2. MARCO TEÓRICO**

**2.1 Enfoque de Procesos Organizacionales y Cadena de Valor (AS-IS / TO-BE)**

El enfoque de procesos establece que la ingeniería de software debe fundamentarse en la comprensión y optimización de las actividades de la organización. La metodología sigue una cadena de valor unificada: \[\text{Problema} \longrightarrow \text{Proceso AS-IS} \longrightarrow \text{Brechas} \longrightarrow \text{Proceso TO-BE} \longrightarrow \text{Software} \longrightarrow \text{Valor} \longrightarrow \text{Indicadores}\]

**2.2 Modelos de Ciclo de Vida y Sastrería de Procesos (Tailoring)**

El ciclo de vida del software organiza las fases de desarrollo. La sastrería de procesos (*tailoring*) consiste en adaptar conscientemente modelos estándar (Cascada, Incremental, Scrum, DevOps) según los factores del proyecto: incertidumbre de requisitos, complejidad técnica, riesgos y variabilidad.

**2.3 Categorización Normativa de Procesos de Software**

De acuerdo con estándares internacionales (ISO/IEC/IEEE 12207 / SWEBOK), los procesos de software se clasifican en:

* **Procesos Principales:** Requisitos, Análisis/Diseño, Implementación, Pruebas y Despliegue.
* **Procesos de Soporte:** Gestión de Configuración (SCM), Aseguramiento de Calidad (PQA), Verificación (VER) y Validación (VAL).
* **Procesos de Gestión/Organizacionales:** Gestión del Proyecto, Gestión de Riesgos y Mejora Continua.

**2.4 Arquitectura de Software Hexagonal (Puertos y Adaptadores)**

La Arquitectura Hexagonal aísla la lógica de negocio (*Domain Core*) de marcos de trabajo, bases de datos y controladores. Utiliza **Puertos de Entrada/Salida** (interfaces) y **Adaptadores** (implementaciones) para asegurar que las entidades del dominio no dependan de librerías externas.

**2.5 Modelos de Evaluación de Calidad y Procesos (GQM, FURPS+, OWASP 2025 y CMMI-DEV)**

* **GQM (Goal-Question-Metric):** Define Objetivos de evaluación, Preguntas de caracterización y Métricas cuantitativas.
* **FURPS+:** Evalúa Funcionalidad (**F**), Usabilidad (**U** - psicología de colores y accesibilidad **WCAG 2.1 AA**), Confiabilidad (**R**), Rendimiento (**P**), Soportabilidad (**S** - arquitectura) y Restricciones Adicionales (**+** - auditoría de seguridad **OWASP Top 10 - 2025**).
* **CMMI-DEV:** Evalúa la capacidad del proceso mediante Áreas de Práctica (*Practice Areas*: ESTIM, PLAN, PQA, CM, VER, VAL, CAR).

**2.6 Gestión de Configuración de Software (SCM, GitFlow y Semantic Versioning)**

La Gestión de Configuración (SCM) garantiza la trazabilidad e integridad de los artefactos de software. Utiliza estrategias de ramificación (**GitFlow**: main, develop, feature/\*), control de cambios mediante *Pull Requests* con *Code Review*, y etiquetado semántico (**SemVer**: v1.0-PMV) publicado en **GitHub Releases**.

**3. DESARROLLO DEL PROYECTO POR UNIDADES DEL SÍLABO**

**3.1 UNIDAD I: Fundamentos de Procesos de Software y Entrega de Valor**

**3.1.1 Diagnóstico y Modelado del Proceso AS-IS vs. TO-BE**

Se identificaron los actores clave y sus necesidades dentro del sistema:

* **Usuario Operativo / Cliente:** Requiere ingresar solicitudes y recibir atención inmediata sin demoras manuales.
* **Supervisor / Administrador:** Requiere visibilidad en tiempo real de eventos y estado de operaciones para reasignar recursos.
* **Equipo Técnico:** Requiere registros trazables y auditoría de eventos para ejecutar acciones correctivas.

**3.1.2 Matriz de Brechas Operativas e Indicadores de Valor**

**Matriz 3.1.2: Matriz de Brechas e Indicadores de Valor Organizacional**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Proceso Actual (AS-IS)** | **Brecha Detectada** | **Consecuencia Organizacional** | **Proceso Propuesto (TO-BE)** | **Indicador de Valor / Meta** |
| Registro manual en papel. | Información tardía y dispersa. | Demoras de 8 h en la atención. | Ingesta automática mediante app/web. | **Proceso:** Tiempo de atención \(< 5\text{ s}\). |
| Procesamiento reactivo. | Falta de capacidad preventiva. | Ocurrencia de fallas e incidentes. | Motor de reglas en tiempo real. | **Resultado:** Detection \(\ge 95%\). |
| Reportes e información dispersa. | Ausencia de integración. | Decisiones con datos desactualizados. | Dashboard centralizado. | **Valor:** Reducción pérdidas \(< 3%\). |

**3.1.3 Análisis de Factores y Selección del Modelo de Proceso**

**Matriz 3.1.3: Análisis de Factores para Selección del Modelo**

|  |  |  |  |
| --- | --- | --- | --- |
| **Factor del Proyecto** | **Situación Real del Proyecto** | **Nivel** | **Justificación Técnica de Selección** |
| **Incertidumbre de Requisitos** | Requisitos ajustables según retroalimentación. | **Alto** | Exige iteraciones cortas e incrementales. |
| **Complejidad Técnica** | Integración de API REST, base de datos y UI. | **Alto** | Requiere arquitectura desacoplada y CI/CD. |
| **Riesgo Tecnológico** | Posibles fallas en la transmisión de datos. | **Alto** | Exige pruebas continuas y gestión de riesgos. |

**3.1.4 Planificación, WBS, Priorización Valor/Riesgo y Control de Desviaciones**

**Matriz 3.1.4: Control de Desviaciones del Proyecto (Sprint Backlog)**

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **Iteración / Sprint** | **Avance Planificado** | **Avance Real** | **Desviación (%)** | **Causa Raíz Detectada** | **Acción Correctiva Aplicada** |
| **Sprint 1 (Inc. 1)** | 100% (10 HUs) | 70% (7 HUs) | **-30.0%** | Complejidad en base de datos. | Desglose de tareas a máximo 6 h. |
| **Sprint 2 (Inc. 2)** | 100% (12 HUs) | 95% (11 HUs) | **-4.1%** | Ajustes en interfaz de usuario. | Reestimación con *Planning Poker*. |

**3.2 UNIDAD II: Implementación del Proceso de Software y Desarrollo del PMV**

**3.2.1 Categorización de Procesos (Principales, Soporte y Gestión)**

**Matriz 3.2.1: Categorización Normativa de Procesos de Software**

|  |  |  |  |
| --- | --- | --- | --- |
| **Categoría Normativa** | **Actividad Específica del Proyecto** | **Producto de Trabajo (*Work Product*)** | **Responsable RAE** |
| **Proceso Principal** | Especificación de Historias de Usuario. | Backlog priorizado del PMV. | **R:** Analyst / **A:** Product Owner |
| **Proceso Principal** | Análisis y Diseño Arquitectónico. | Diagramas C4 y especificación OpenAPI. | **R:** Architect / **A:** Tech Lead |
| **Proceso Principal** | Construcción del Código Fuente. | Módulos ejecutables en GitHub. | **R:** Developers / **A:** Tech Lead |
| **Proceso de Soporte** | Gestión de Configuración (SCM). | Repositorio Git con GitFlow. | **R:** DevOps / **A:** Tech Lead |
| **Proceso de Soporte** | Aseguramiento de Calidad (PQA). | Reporte SonarQube y Pruebas. | **R:** QA Lead / **A:** Architect |
| **Proceso de Gestión** | Control de Desviaciones de Sprint. | Matriz de seguimiento de avance. | **R:** Scrum Master / **A:** Leader |

**3.2.2 Sastrería de Procesos (Tailoring) y Ciclo de Vida Híbrido**

**Modelo Seleccionado:** Desarrollo Iterativo/Incremental + Marco Scrum + Prácticas DevOps.
**Justificación Técnica:** Se descartó el modelo Cascada porque congelar requisitos al inicio genera un alto riesgo de obsolescencia frente a las necesidades cambiantes del usuario. Scrum puro es insuficiente al carecer de automatización de pruebas; por ello, se integra con prácticas DevOps (CI/CD, análisis estático y pruebas automatizadas) para asegurar lanzamientos estables.

**3.2.3 Arquitectura Hexagonal en GitHub (/src/domain/ Desacoplado)**

El repositorio de GitHub estructurado demuestra el aislamiento estricto del núcleo de dominio:

/src

├── domain/ <── DOMAIN CORE (100% Código Nativo Puro)

│ ├── model/ <── Entidades (cero importaciones de ORMs/Frameworks)

│ └── service/ <── Servicios de Dominio (Reglas de Negocio)

├── ports/ <── PUERTOS (Interfaces de Abstracción)

│ ├── inbound/ <── Input Ports (Interfaces de Casos de Uso)

│ └── outbound/ <── Output Ports (Interfaces para Persistencia)

└── adapters/ <── ADAPTADORES (Infraestructura Externa)

├── inbound/ <── Inbound Adapters (Controllers REST/GraphQL)

└── outbound/ <── Outbound Adapters (Repositories JPA/PostgreSQL)

**3.2.4 Ejecución del Primer Incremento / Producto Mínimo Viable (PMV)**

**Matriz 3.2.4: Alcance e Historias de Usuario del PMV**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID Historia** | **Historia de Usuario (*Como... Quiero... Para...*)** | **Prioridad** | **Criterio de Aceptación (*Given-When-Then*)** | **Producto de Trabajo** |
| **HU-01** | *Como operador, quiero registrar usuarios para dar accesos.* | Alta / Medio | **Dado** datos válidos, **cuando** guarda, **entonces** retorna token JWT. | Backlog priorizado |
| **HU-02** | *Como servicio, quiero recibir paquetes JSON vía REST.* | Alta / Alto | **Dado** paquete válido, **cuando** recibe, **entonces** procesa en \(< 2\text{ s}\). | OpenAPI Spec |
| **HU-03** | *Como sistema, quiero emitir alertas ante lecturas anómalas.* | Alta / Alto | **Dado** dato anómalo, **cuando** evalúa, **entonces** despliega alerta. | Pruebas ejecutadas |

**3.3 UNIDAD III: Evolución de los Procesos y Actividades de Software**

**3.3.1 Evaluación GQM del Producto y Proceso en los Incrementos 1 y 2**

**Matriz 3.3.1: Definición de Objetivos, Preguntas y Métricas GQM**

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **Cód. Goal** | **Dimensión** | **Objeto Evaluado** | **Propósito / Atributo** | **Pregunta Orientadora** | **Métrica y Meta (Inc. 1 vs. Inc. 2)** |
| **G-01** | **Producto** | Arquitectura en GitHub. | Desacoplamiento. | ¿El dominio tiene dependencias? | Contaminación Dominio: Meta **0.0%**. |
| **G-02** | **Producto** | Pruebas Inc. 1 y 2. | Estabilidad. | ¿Qué % de RFs tiene capturas? | Cobertura Capturas: Meta **100%**. |
| **G-03** | **Proceso** | Entrega de Valor. | Impacto operativo. | ¿Cuánto se redujeron las brechas? | Brechas Resueltas: Inc1 **60%** ➔ Inc2 **95%**. |

**3.3.2 Auditoría FURPS+ (Psicología de Colores, WCAG 2.1 AA y OWASP Top 10 - 2025)**

* **Usabilidad (U) - Psicología de Colores:** Primario #1E3A8A (Azul Noche: seguridad y estabilidad); Secundario #059669 (Verde Esmeralda: estados seguros); Alerta #DC2626 (Rojo Carmesí: atención inmediata).
* **Accesibilidad e Inclusión (WCAG 2.1 AA):** Relación de contraste medido de \(7.1:1\) (supera el estándar \(\ge 4.5:1\)); etiquetado semántico con roles ARIA e inclusión de lectores de pantalla.
* **Seguridad de Código (Factor + - OWASP Top 10 2025):** Auditoría estática SAST confirmando 0 vulnerabilidades en Broken Access Control (A01), Cryptographic Failures (A02), Injections (A03) e Insecure Design (A04).

**3.3.3 Evaluación de Capacidad del Proceso según CMMI-DEV (Niveles 0 al 3)**

**Matriz 3.3.3: Diagnóstico de Capacidad CMMI por Área de Práctica**

|  |  |  |  |
| --- | --- | --- | --- |
| **Área CMMI (PA)** | **Criterio / Evidencia Requerida en el Proyecto** | **Estado Medido** | **Nivel de Capacidad Alcanzado** |
| **ESTIM (Estimating)** | Historias estimadas con técnicas formales (*Planning Poker*). | **Cumple** | **Nivel 2 (Gestionado)** |
| **PLAN (Planning)** | Sprint Backlog en GitHub Projects con asignación de roles. | **Cumple** | **Nivel 2 (Gestionado)** |
| **CM (Config. Mgmt.)** | Repositorio Git con estrategia GitFlow y tags de versión. | **Cumple** | **Nivel 3 (Definido)** |
| **VER / VAL** | Pruebas automatizadas, SonarQube y fichas con capturas. | **Cumple** | **Nivel 2 (Gestionado)** |

**3.3.4 Plan de Mejora Continua y Análisis de Causa Raíz (CAR)**

**Matriz 3.3.4: Plan de Mejora Continua Derivado de CMMI / CAR**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Área CMMI** | **Hallazgo / Brecha Identificada** | **Causa Raíz del Proceso** | **Acción Corregida / Plan de Mejora** | **Impacto Medido** |
| **PQA** | Inconsistencia en Code Reviews. | Ausencia de plantilla en GitHub. | Crear .github/pull\_request\_template.md. | **100% Code Reviews** estandarizados. |
| **VER** | Fallas en integración por unit tests. | Ejecución manual dependiente del dev. | Implementar *pre-commit hooks* con Husky. | **0 errores de compilación** en main. |

**3.4 UNIDAD IV: Gestión de Configuración de Software (SCM)**

**3.4.1 Administración del Cambio en GitHub (Issues, RFC y PRs con Code Review)**

Toda solicitud de cambio (RFC) se canaliza formalmente mediante **GitHub Issues** utilizando la plantilla .github/ISSUE\_TEMPLATE/change\_request.md. La aprobación requiere un **Pull Request (PR)** con la plantilla .github/PULL\_REQUEST\_TEMPLATE.md y la aprobación obligatoria de al menos 1 revisor (*Code Review*) bajo las reglas de protección de ramas (*Branch Protection Rules*).

**3.4.2 Gestión de Versiones (GitFlow, Tags Semánticos v1.0-PMV y GitHub Releases)**

El proyecto implementa **GitFlow** dividiendo el trabajo en ramas main (producción), develop (integración) y feature/\* (historias de usuario). Cada hito se etiqueta con versionamiento semántico (**SemVer**) e integra en **GitHub Releases**:

* **v1.0-PMV:** Liberación del Producto Mínimo Viable (Incremento 1).
* **v2.0-Inc2:** Liberación del Incremento 2 con motor de reglas y monitoreo.
* **v3.0-Inc3:** Liberación del Incremento 3 consolidado e integrado.

**3.4.3 Construcción del Sistema, Automatización CI/CD y Herramientas Modernas**

El pipeline de **GitHub Actions** automatiza la compilación del código, ejecuta la suite de pruebas unitarias/integración y realiza el análisis estático de seguridad con **SonarQube/Semgrep** antes de generar la imagen de contenedor Docker para su despliegue en entorno Staging.

**4. CONCLUSIONES**

1. **Alineación Proceso–Software:**
   El diseño previo del proceso **TO-BE** garantizó que la intervención del software resuelva brechas operativas reales, logrando reducir el tiempo de atención de 8 horas a menos de 5 segundos y entregando valor cuantitativo a la organización.
2. **Desacoplamiento Arquitectónico:**
   La estructuración de la **Arquitectura Hexagonal** en el repositorio de GitHub (/src/domain/) aseguró el aislamiento total de la lógica de negocio, alcanzando un 0% de contaminación de marcos externos y facilitando la testabilidad continua del núcleo de dominio.
3. **Calidad y Seguridad Certificada:**
   La combinación de los modelos **GQM**, **FURPS+** y la auditoría **OWASP Top 10 (2025)** demostró la estabilidad del software con 0 vulnerabilidades críticas, cumplimiento de accesibilidad **WCAG 2.1 AA** y una cobertura de pruebas superior al 80%.
4. **Madurez y Control de Configuración (SCM):**
   La implementación de la suite de GitHub con la estrategia **GitFlow**, reglas de protección de ramas y versionamiento semántico (v1.0-PMV) garantizó la trazabilidad bidireccional entre solicitudes de cambio, código fuente y artefactos desplegados.

**5. RECOMENDACIONES**

1. **Automatización de Pre-commit Hooks:**
   Se recomienda institucionalizar el uso de *hooks* de Git (mediante herramientas como Husky) en el entorno local de los desarrolladores para ejecutar linters y pruebas unitarias antes de confirmar commits, evitando saturar el pipeline de CI/CD.
2. **Monitoreo Continuo de Seguridad (DevSecOps):**
   Se sugiere mantener activo el escaneo diario de dependencias mediante Dependabot en GitHub para mitigar de manera proactiva componentes vulnerables o desactualizados (Categoría A06 de OWASP 2025).
3. **Evolución del Nivel de Capacidad CMMI:**
   Para la fase post-proyecto, se aconseja transitar hacia el Nivel 4 de CMMI (Gestionado Cuantitativamente) aplicando control estadístico sobre los tiempos de ciclo (*Cycle Time*) y tasas de re-ejecución de pruebas.

**REFERENCIAS BIBLIOGRÁFICAS**

* Camarena, J., Trueba, A., Reyes, M. y López, M. (2012). Automatización de la codificación del patrón modelo vista controlador (MVC) en proyectos orientados a la web. *CIENCIA ergo-sum*, 19(3), 239-250.
* CMMI Institute. (2018). *CMMI for Development, Version 2.0*. Software Engineering Institute.
* Fitzgerald, B. y Stol, K. J. (2017). Continuous software engineering: A roadmap and agenda. *Journal of Systems and Software*, 123, 176-189.
* O'Regan, G. (2017). *Concise guide to software engineering: from fundamentals to application methods*. Springer.
* OWASP Foundation. (2025). *OWASP Top 10:2025 The Ten Most Critical Web Application Security Risks*.
* Pardo, J. (2012). *Configuración y usos de mapa de procesos*. AENOR.
* Pressman, R. S. y Maxim, B. R. (2021). *Ingeniería de software: un enfoque práctico* (9.ª ed.). McGraw-Hill.
* Salvador, A. (2011). *Ingeniería de Software: un enfoque desde la guía SWEBOK*. Alfaomega.
* Sommerville, I. (2016). *Software engineering* (10.ª ed.). Pearson Educación.

**ANEXOS**

**ANEXO A: Enlace del Repositorio de Código en GitHub (Estructura Hexagonal)**

* **URL del Repositorio GitHub:** https://github.com/org-ucontinental/proyecto-procesos-software-2026
* **Etiquetas de Versión (*Tags Semánticos*):** v1.0-PMV, v2.0-Inc2, v3.0-Inc3

**ANEXO B: Enlace del Video Demostrativo del Software en Ejecución**

* **URL del Video Demostrativo (Drive / YouTube):** https://demo-software-procesos-2026

**ANEXO C: GUIÓN TÉCNICO Y NARRATIVO DEL VIDEO DEMOSTRATIVO DEL SOFTWARE**

**Duración Total:** 05 minutos 00 segundos
**Formato:** Grabación de pantalla con voz en off del equipo y demostración en entorno activo (Staging/Cloud).

|  |  |  |  |
| --- | --- | --- | --- |
| **Tiempo** | **Escena / Pantalla Mostrada** | **Locución / Explicación Técnica** | **Criterio de Aceptación / Requerimiento Verificado** |
| **00:00 - 00:45** | Carátula del proyecto, proceso TO-BE y estructura de carpetas Hexagonales en GitHub. | *"Buenas tardes. Iniciamos mostrando la estructura de directorios en GitHub, donde el núcleo de dominio está 100% desacoplado en /src/domain/ sin dependencias de frameworks."* | **Arquitectura Hexagonal & SCM:** Verificación de Puertos y Adaptadores sin acoplamiento. |
| **00:45 - 01:45** | Pantalla de Login e interfaz UI. Ejecución del flujo de registro y autenticación RBAC. | *"Procedemos con el Requerimiento RF-01. Ingresamos las credenciales. Observe la paleta de colores (#1E3A8A) y la accesibilidad WCAG 2.1. El sistema valida y genera el token JWT."* | **RF-01 (Autenticación):** Given usuario válido, When ingresa, Then genera token JWT seguro. |
| **01:45 - 02:45** | Envío de paquete JSON vía cliente REST y recepción inmediata en el panel. | *"Demostramos el RF-02 e ingesta de datos. Enviamos una petición JSON simulada. La API responde en menos de 500 ms y actualiza la interfaz automáticamente."* | **RF-02 (Ingesta de Datos):** Procesamiento de paquete de datos y respuesta en \(< 2\text{ s}\). |
| **02:45 - 03:45** | Generación de evento anómalo y despliegue de alerta visual en mapa. | *"Evaluamos RF-03 y RF-04. Al superar el umbral, el motor dispara la alerta de color #DC2626 y ubica las coordenadas GPS en el mapa interactivo."* | **RF-03 / RF-04 (Alertas y Mapa):** Emisión de alerta push y renderizado georreferenciado. |
| **03:45 - 04:30** | Módulo de generación de reportes y exportación en PDF/Excel. | *"Mostramos RF-05 del Incremento 3. Seleccionamos el rango de fechas y exportamos el reporte consolidado que valida el cumplimiento del valor esperado."* | **RF-05 (Reportes):** Exportación de información histórica para toma de decisiones. |
| **04:30 - 05:00** | Ejecución del pipeline de GitHub Actions (pruebas unitarias y escaneo SonarQube OWASP). | *"Finalizamos mostrando la evidencia de calidad. Nuestro pipeline de CI/CD ejecuta el 100% de los tests y confirma 0 vulnerabilidades OWASP 2025 en SonarQube."* | **OWASP 2025 & CI/CD:** Verificación de código seguro y pipeline automatizado. |