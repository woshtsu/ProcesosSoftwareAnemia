**INFORME ACADÉMICO INTEGRADOR DEL PROYECTO DE ASIGNATURA**

\========================================================================================================  
                                      UNIVERSIDAD CONTINENTAL  
                           FACULTAD DE INGENIERÍA DE SISTEMAS E INFORMÁTICA  
                                PROGRAMA ACADÉMICO PROFESIONAL DE  
                             INGENIERÍA DE SISTEMAS E INFORMÁTICA

                                   INFORME ACADÉMICO FINAL  
              "DISEÑO, ADAPTACIÓN, EVALUACIÓN E IMPLEMENTACIÓN DEL PROCESO DE  
                SOFTWARE CON ENTREGA DE VALOR APLICADO AL PROYECTO DE ASIGNATURA"

\--------------------------------------------------------------------------------------------------------  
ASIGNATURA: Procesos de Software (Código: ASUC01702)  
NIVEL / CICLO: Noveno Ciclo (IX Período \- Electivo de Especialidad)  
DOCENTE: \[Nombres y Apellidos del Docente\]  
BLOQUE / SECCIÓN: \[Código de Sección / NRC\]

INTEGRANTES DEL EQUIPO DE PROYECTO:  
1\. \[Apellidos, Nombres\] \- Código: \[XXXXX\] \- Rol: Leader / Software Architect  
2\. \[Apellidos, Nombres\] \- Código: \[XXXXX\] \- Rol: Process Analyst & QA Lead  
3\. \[Apellidos, Nombres\] \- Código: \[XXXXX\] \- Rol: Backend & Data Engineer  
4\. \[Apellidos, Nombres\] \- Código: \[XXXXX\] \- Rol: Frontend & Mobile Developer

FECHA DE ENTREGA: \[DD/MM/AAAA\]  
PERIODO ACADÉMICO: 2026-20  
\========================================================================================================  
---

**ÍNDICE GENERAL**

ÍNDICE GENERAL .................................................................................... i  
ÍNDICE DE TABLAS .................................................................................. ii  
ÍNDICE DE FIGURAS ................................................................................. iii

RESUMEN EJECUTIVO / ABSTRACT ....................................................................... iv

1\. INTRODUCCIÓN .................................................................................... 1  
  1.1 Antecedentes del Proyecto ................................................................... 1  
  1.2 Definición del Problema Organizacional ..................................................... 1  
  1.3 Objetivos del Proyecto e Informe Académico ................................................. 2

2\. MARCO TEÓRICO .................................───────────────────────────────────────────────── 3  
  2.1 Enfoque de Procesos Organizacionales (AS-IS y TO-BE) ........................................ 3  
  2.2 Modelos de Ciclo de Vida y Sastrería de Procesos (Tailoring) ................................ 3  
  2.3 Categorización Normativa de Procesos de Software ........................................... 4  
  2.4 Arquitectura de Software Hexagonal (Puertos y Adaptadores) ................................. 4  
  2.5 Modelos de Evaluación de Calidad y Procesos (GQM, FURPS+, OWASP 2025 y CMMI) ................ 5

3\. DESARROLLO DEL PROCESO Y PRODUCTO DE SOFTWARE (INTEGRACIÓN DE GUÍAS) ............................ 6  
  3.1 EJE 1: Diagnóstico y Diseño del Proceso Organizacional (AS-IS / TO-BE) ...................... 6  
  3.2 EJE 2: Selección y Adaptación del Modelo de Ciclo de Vida (Tailoring) ...................... 8  
  3.3 EJE 3: Operatividad, Actividades, Responsabilidades RAE y DoD .............................. 10  
  3.4 EJE 4: Planificación, WBS, Priorización Valor/Riesgo y Control de Desviaciones .............. 12  
  3.5 EJE 5: Ejecución de Procesos Principales del Primer Incremento (PMV) ........................ 14  
  3.6 EJE 6: Evaluación GQM, Arquitectura Hexagonal en Git y Pruebas Funcionales .................. 16  
  3.7 EJE 7: Evaluación FURPS+, Psicología de Colores, WCAG 2.1 y OWASP 2025 ....................... 18  
  3.8 EJE 8: Evaluación de Capacidad del Proceso según CMMI-DEV y Mejora Continua ................ 20

4\. CONCLUSIONES Y LECCIONES APRENDIDAS ............................................................. 22  
  4.1 Conclusiones Técnicas del Proceso y Producto .............................................. 22  
  4.2 Lecciones Aprendidas en la Adaptación del Ciclo de Vida .................................... 22

REFERENCIAS BIBLIOGRÁFICAS ........................................................................ 23

ANEXOS .................................................─────────────────────────────────────────── 24  
  ANEXO A: Enlace del Video Demostrativo del Software ........................................... 24  
  ANEXO B: Enlace del Repositorio de Código en GitHub (Estructura Hexagonal) ..................... 24  
  ANEXO C: Guión Técnico y Narrativo del Video de Demostración del Software ...................... 25  
---

**RESUMEN EJECUTIVO / ABSTRACT**

**Resumen:**  
El presente informe académico documenta de manera integral el diseño, adaptación, implementación, evaluación y evolución del proceso de software aplicado al desarrollo de la solución tecnológica del proyecto de asignatura. A través de la integración sistemática de las Guías de Trabajo del curso, se diagnostica el proceso organizacional en su estado actual (**AS-IS**), identificando las brechas operativas que limitan la generación de valor. Se diseña el proceso futuro (**TO-BE**) y se justifica técnicamente la selección y adaptación (*tailoring*) de un modelo de ciclo de vida híbrido (Iterativo/Incremental \+ Scrum \+ Prácticas DevOps). Asimismo, se estructura la **Arquitectura Hexagonal (Puertos y Adaptadores)** directamente en la carpeta del repositorio GitHub, aislando las reglas de negocio del *Domain Core* de los detalles de infraestructura. La verificación y validación del software se ejecuta mediante fichas de prueba funcional acompañadas de evidencias visuales (capturas de pantalla) para cada requerimiento del **Producto Mínimo Viable (PMV)** e incrementos posteriores. Finalmente, se aplican los modelos de evaluación **GQM (Goal-Question-Metric)**, **FURPS+** (con auditoría de seguridad **OWASP Top 10 \- 2025**, accesibilidad **WCAG 2.1 AA** y psicología de colores) y el modelo de capacidad **CMMI-DEV**, demostrando una reducción cuantitativa de brechas y la generación de valor organizacional medible.

---

**1\. INTRODUCCIÓN**

**1.1 Antecedentes del Proyecto**

En el entorno operativo de las organizaciones modernas, la incorporación desordenada de tecnología sin un análisis previo del proceso organizacional suele derivar en automatizaciones de ineficiencias existentes. El presente proyecto de asignatura, enmarcado en el noveno ciclo de la carrera de Ingeniería de Sistemas e Informática de la Universidad Continental, responde a la necesidad de construir soluciones tecnológicas fundamentadas en una rigurosa ingeniería de procesos de software.

**1.2 Definición del Problema Organizacional**

La organización bajo estudio presenta procesos predominantemente manuales y reactivos. La falta de monitoreo en tiempo real, la dispersión de datos y el registro manual en soportes físicos generan cuellos de botella operativos, retrasos en la toma de decisiones y pérdidas económicas directas. La intervención de software propuesta busca transformar el flujo tradicional hacia un proceso preventivo e integrado, donde la tecnología actúa como un elemento habilitador de valor.

**1.3 Objetivos del Proyecto e Informe Académico**

* **Objetivo General:** Diseñar, adaptar e implementar un proceso de software ejecutable y medible que soporte la construcción de una solución tecnológica alineada con las necesidades de la organización, garantizando la entrega de valor al usuario final.  
* **Objetivos Específicos:**   
  1. Diagnosticar el proceso organizacional actual (**AS-IS**) e identificar las brechas operativas para diseñar el proceso propuesto (**TO-BE**).  
  2. Adaptar el modelo de ciclo de vida del software (*tailoring*) evaluando los factores de riesgo, incertidumbre y complejidad técnica del proyecto.  
  3. Implementar la solución tecnológica aplicando el patrón de **Arquitectura Hexagonal** en el repositorio institucional de GitHub.  
  4. Evaluar la calidad del producto y la capacidad del proceso mediante los modelos **GQM**, **FURPS+** (con auditoría **OWASP 2025**) y **CMMI-DEV**.

---

**2\. MARCO TEÓRICO**

**2.1 Enfoque de Procesos Organizacionales (AS-IS y TO-BE)**

El enfoque de procesos establece que antes de definir la tecnología o programar líneas de código, se debe comprender el flujo de actividades de la organización. El modelado **AS-IS** documenta el estado actual para evidenciar ineficiencias, mientras que el diseño **TO-BE** reestructura las actividades incorporando puntos de control automatizados donde el software aporta un valor directo.

**2.2 Modelos de Ciclo de Vida y Sastrería de Procesos (Tailoring)**

El ciclo de vida del software organiza las fases de desarrollo. La sastrería de procesos (*tailoring*) consiste en adaptar conscientemente modelos estándar (Cascada, Incremental, Scrum, DevOps) según los factores reales del proyecto: nivel de incertidumbre, cambios esperados, riesgo y componentes de datos e IA.

**2.3 Categorización Normativa de Procesos de Software**

De acuerdo con estándares de ingeniería de software, los procesos se clasifican en:

* **Procesos Principales:** Especificación de Requisitos, Análisis y Diseño, Implementación, Integración/Pruebas y Despliegue.  
* **Procesos de Soporte:** Gestión de Configuración (SCM), Aseguramiento de Calidad (PQA), Verificación y Validación.  
* **Procesos de Gestión/Organizacionales:** Gestión del Proyecto, Gestión de Riesgos y Mejora Continua.

**2.4 Arquitectura de Software Hexagonal (Puertos y Adaptadores)**

La Arquitectura Hexagonal aísla el núcleo de dominio (*Domain Core*) de las tecnologías externas (marcos web, bases de datos, controladores). Utiliza **Puertos de Entrada/Salida** (interfaces) y **Adaptadores** (implementaciones concretas) para garantizar la testabilidad y mantenibilidad del software.

**2.5 Modelos de Evaluación de Calidad y Procesos (GQM, FURPS+, OWASP 2025 y CMMI)**

* **GQM (Goal-Question-Metric):** Modela la medición definiendo Objetivos de evaluación, Preguntas de caracterización y Métricas cuantitativas.  
* **FURPS+:** Clasifica la calidad del producto en Funcionalidad (**F**), Usabilidad (**U** \- incluyendo accesibilidad **WCAG 2.1** y psicología de colores), Confiabilidad (**R**), Rendimiento (**P**), Soportabilidad (**S** \- Arquitectura) y Restricciones Adicionales (**\+** \- auditoría de seguridad **OWASP Top 10 \- 2025**).  
* **CMMI-DEV:** Evalúa el nivel de capacidad de las áreas de práctica del proceso (*Practice Areas*: ESTIM, PLAN, PQA, CM, VER, VAL, CAR).

---

**3\. DESARROLLO DEL PROCESO Y PRODUCTO DE SOFTWARE (INTEGRACIÓN DE GUÍAS DE TRABAJO)**

**3.1 EJE 1: Diagnóstico y Diseño del Proceso Organizacional (AS-IS / TO-BE)**

**Matriz 3.1.1: Identificación de Actores y Necesidades del Sistema**

| Actor | Necesidad Operativa | Decisión que debe tomar en el Proceso |
| :---- | :---- | :---- |
| **Usuario Operativo / Cliente** | Registro y procesamiento rápido de solicitudes sin demoras manuales. | Aprobación e inicio de la atención del servicio. |
| **Supervisor / Administrador** | Visibilidad en tiempo real de eventos, alertas y estado de operaciones. | Reasignación inmediata de recursos y control operativo. |
| **Equipo Técnico / Mantenimiento** | Disponer de registros trazables y auditoría de eventos del sistema. | Ejecución de acciones correctivas ante alertas críticas. |

**Matriz 3.1.2: Matriz de Brechas Operativas (AS-IS vs. TO-BE)**

| Proceso Actual (AS-IS) | Brecha / Problema Detectado | Consecuencia en la Organización | Proceso Propuesto (TO-BE) |
| :---- | :---- | :---- | :---- |
| Registro manual en soporte de papel. | Comunicación tardía y pérdida de datos. | Demora de 8 horas en la atención. | Ingesta automática mediante aplicación móvil/web. |
| Procesamiento reactivo posterior. | Ausencia de capacidad preventiva. | Ocurrencia recurrente de fallas. | Motor de reglas para detección en tiempo real. |
| Reportes e información dispersa. | Falta de integración institucional. | Decisiones con datos desactualizados. | Panel de control (*Dashboard*) centralizado. |
| Evaluación sin métricas claras. | Imposibilidad de medir el desempeño. | Pérdida sostenida de eficiencia. | Indicadores automáticos de rendimiento. |
| Notificación por llamadas manuales. | Alta tasa de error en la comunicación. | Retraso en la atención de emergencias. | Alertas push automáticas georreferenciadas. |

**Sistema de Indicadores de Gestión del Proceso**

* **Indicador de Proceso:** Tiempo promedio de atención del flujo (Meta: Reducción de 8 h a 5 s).  
* **Indicador de Producto:** Disponibilidad de la API REST (Meta: \\(\\ge 99.5%\\)).  
* **Indicador de Resultado:** Porcentaje de eventos anómalos detectados a tiempo (Meta: \\(\\ge 95%\\)).  
* **Indicador de Valor Organizacional:** Reducción porcentual de pérdidas operativas (Meta: Del 22% al \\(\< 3%\\)).

---

**3.2 EJE 2: Selección y Adaptación del Modelo de Ciclo de Vida (Tailoring)**

**Matriz 3.2.1: Análisis de Factores de Adaptación del Proyecto**

| Factor de Adaptación | Situación Real del Proyecto | Nivel | Justificación Técnica de la Adaptación |
| :---- | :---- | :---: | :---- |
| **Incertidumbre de Requisitos** | Requisitos ajustables según retroalimentación del usuario. | **Alto** | Exige iteraciones cortas para validar incrementos funcionales. |
| **Complejidad Técnica** | Integración de servicios REST, base de datos y componentes. | **Alto** | Exige desacoplamiento arquitectónico (Arquitectura Hexagonal). |
| **Frecuencia de Cambios** | Ajustes esperados en la interfaz y reglas operativas. | **Medio** | Rechaza el modelo Cascada estricto por alto costo de retrabajo. |
| **Criticidad y Riesgo** | Impacto directo en la operación de la organización. | **Alto** | Requiere automatización de pruebas e integración continua. |

**Selección del Modelo Híbrido Adaptado (Tailoring)**

**Modelo Seleccionado:** Desarrollo Iterativo/Incremental \+ Marco Scrum \+ Prácticas DevOps.  
**Justificación Técnica:** El modelo Cascada fue descartado porque congelar requisitos al inicio genera un alto riesgo de entregar un producto desalineado. Scrum aislado es insuficiente al carecer de prácticas de ingeniería continua; por ello, se integra con prácticas DevOps (integración continua, análisis estático y pruebas automatizadas) para garantizar despliegues estables en cada Sprint.

---

**3.3 EJE 3: Operatividad, Actividades, Responsabilidades RAE y DoD**

**Matriz 3.3.1: Categorización Normativa y Productos de Trabajo**

| Categoría Normativa | Actividad Específica del Proyecto | Producto de Trabajo (*Work Product*) | Responsable RAE |
| :---- | :---- | :---- | :---: |
| **Proceso Principal** | Especificación de Historias de Usuario. | Backlog del proyecto priorizado. | **R:** Analyst / **A:** Product Owner |
| **Proceso Principal** | Diseño de Arquitectura Hexagonal. | Diagramas C4 y especificación OpenAPI. | **R:** Architect / **A:** Tech Lead |
| **Proceso Principal** | Construcción del Código Fuente. | Módulos ejecutables en GitHub. | **R:** Developers / **A:** Tech Lead |
| **Proceso de Soporte** | Gestión de Configuración (SCM). | Repositorio Git con estrategia GitFlow. | **R:** DevOps / **A:** Tech Lead |
| **Proceso de Soporte** | Aseguramiento de Calidad (PQA). | Reporte SonarQube y Pruebas. | **R:** QA Lead / **A:** Architect |
| **Proceso de Gestión** | Control de Desviaciones de Sprint. | Matriz de seguimiento de desviaciones. | **R:** Scrum Master / **A:** Leader |

**Definición de Criterios de Terminación (Definition of Done \- DoD)**

Una Historia de Usuario se considera **completada (Done)** únicamente si cumple:

1. Código fuente compilado sin advertencias ni errores en la rama de integración.  
2. Cobertura de pruebas unitarias \\(\\ge 80%\\) sobre las clases del núcleo de dominio.  
3. Análisis estático con SonarQube con 0 vulnerabilidades y 0 deudas técnicas críticas.  
4. Pruebas funcionales de UI ejecutadas con capturas de pantalla adjuntas en la ficha.  
5. Código revisado por pares (*Code Review*) y aprobado en el Pull Request de GitHub.

---

**3.4 EJE 4: Planificación, WBS, Priorización Valor/Riesgo y Control de Desviaciones**

**Estructura de Descomposición del Trabajo (WBS)**

PROYECTO DE SOFTWARE  
├── 1\. INCREMENTO 1 (PMV \- Núcleo Operativo)  
│   ├── HU-01: Autenticación y Registro de Usuarios  
│   ├── HU-02: Ingesta y Recepción de Eventos  
│   └── HU-03: Motor Básico de Alertas Visuales  
├── 2\. INCREMENTO 2 (Procesamiento Avanzado)  
│   ├── HU-04: Panel de Monitoreo Georreferenciado  
│   └── HU-05: Módulo de Reglas y Notificaciones Push  
└── 3\. INCREMENTO 3 (Consolidación e Integración)  
    ├── HU-06: Exportación de Reportes Consolidados  
    └── HU-07: Integración con APIs de Sistemas Externos

**Matriz de Control de Desviaciones del Proyecto**

| Iteración / Sprint | Avance Planificado | Avance Real | Desviación (%) | Causa Raíz Detectada | Acción Correctiva Aplicada |
| :---: | :---: | :---: | :---: | :---- | :---- |
| **Sprint 1 (Inc. 1\)** | 100% (10 HUs) | 70% (7 HUs) | \-30.0% | Complejidad no prevista en la base de datos. | Desglose de tareas a máximo 6 h y refactorización. |
| **Sprint 2 (Inc. 2\)** | 100% (12 HUs) | 95% (11 HUs) | \-4.1% | Ajustes de diseño de interfaz de usuario. | Reestimación mediante *Planning Poker*. |

---

**3.5 EJE 5: Ejecución de Procesos Principales del Primer Incremento (PMV)**

**Especificación de Historias de Usuario del PMV**

* **HU-01 (Registro y Accesos):** *Como* usuario del sistema, *quiero* registrar mi perfil con credenciales seguras, *para* acceder a las funcionalidades según mi rol.   
  * *Criterio de Aceptación (Given-When-Then):* **Dado** que el usuario ingresa datos válidos, **cuando** presiona "Registrar", **entonces** el sistema almacena el usuario y retorna un token JWT firmado.  
* **HU-02 (Ingesta de Datos):** *Como* servicio backend, *quiero* recibir eventos telemáticos vía API REST, *para* procesar la información de la operación.   
  * *Criterio de Aceptación:* **Dado** un paquete JSON estructurado, **cuando** ingresa al endpoint de ingesta, **entonces** se valida y guarda en base de datos en \\(\< 2 \\text{ s}\\).  
* **HU-03 (Alerta Visual Básica):** *Como* operador, *quiero* visualizar una alerta de emergencia en pantalla, *para* tomar decisiones preventivas inmediatas.   
  * *Criterio de Aceptación:* **Dado** que un dato supera el umbral crítico, **cuando** el motor evalúa la regla, **entonces** se despliega la notificación de alerta en la interfaz.

---

**3.6 EJE 6: Evaluación GQM, Arquitectura Hexagonal en Git y Pruebas Funcionales**

**Estructura de Directorios de la Arquitectura Hexagonal en GitHub**

La estructura del repositorio institucional demuestra el desacoplamiento estricto del *Domain Core*:

/src  
├── domain/                         \<── DOMAIN CORE (100% Código Nativo Puro)  
│   ├── model/                      \<── Entidades de Dominio (cero importaciones de ORMs/Frameworks)  
│   └── service/                    \<── Lógica y Reglas de Negocio  
├── ports/                          \<── PUERTOS (Interfaces de Abstracción)  
│   ├── inbound/                    \<── Input Ports (Interfaces de Casos de Uso)  
│   └── outbound/                   \<── Output Ports (Interfaces para Persistencia y Notificaciones)  
└── adapters/                       \<── ADAPTADORES (Infraestructura Externa)  
    ├── inbound/                    \<── Inbound Adapters (Controllers REST, Subscribers)  
    └── outbound/                   \<── Outbound Adapters (Repositories JPA/PostgreSQL, Redis)

**Ficha Modelo de Prueba Funcional con Evidencia Fotográfica**

\========================================================================================================  
            FICHA DE PRUEBA FUNCIONAL Y EVIDENCIA VISUAL POR REQUERIMIENTO (RF-01)  
\========================================================================================================  
PROYECTO: \[Nombre del Proyecto de Asignatura\]  
INCREMENTO EVALUADO: Incremento 1 (PMV)  
REQUERIMIENTO: RF-01 / HU-01 \- Autenticación y Registro de Usuario  
\--------------------------------------------------------------------------------------------------------  
CASO DE PRUEBA: CP-RF01-01 (Prueba Funcional de UI / Aceptación)  
DATO DE ENTRADA: { usuario: "operador\_01", pass: "P@ssword2026", rol: "SUPERVISOR" }  
RESULTADO ESPERADO: Registro exitoso, redirección a dashboard y emisión de token JWT.  
\--------------------------------------------------------------------------------------------------------  
EVIDENCIAS FOTOGRÁFICAS (CAPTURAS DE PANTALLA EN EJECUCIÓN):

 \[ CAPTURA 1: DATOS DE ENTRADA CARGADOS \]  
 Descripción: Formulario de registro con datos cargados antes del envío.  
 Archivo de Imagen: /docs/evidencias/inc1/RF01\_paso1\_entrada.png

 \[ CAPTURA 2: CONFIRMACIÓN Y NAVEGACIÓN EXITOSA \]  
 Descripción: Pantalla de confirmación mostrando el ID de usuario registrado y token activo.  
 Archivo de Imagen: /docs/evidencias/inc1/RF01\_paso2\_resultado.png  
\--------------------------------------------------------------------------------------------------------  
EVALUACIÓN: APROBADO \| FECHA: \[DD/MM/AAAA\] \| EVALUADOR: QA Lead  
\========================================================================================================  
---

**3.7 EJE 7: Evaluación FURPS+, Psicología de Colores, WCAG 2.1 y OWASP 2025**

**Matriz de Evaluación del Factor U (Usability): Psicología de Colores y Accesibilidad**

* **Psicología de Colores Aplicada:** Color Primario \#1E3A8A (Azul Noche: transmite seguridad y estabilidad en el manejo de datos); Color Secundario \#059669 (Verde Esmeralda: representa estados operativos seguros); Color de Alerta \#DC2626 (Rojo Carmesí: estimula la atención inmediata ante eventos críticos).  
* **Accesibilidad e Inclusión (WCAG 2.1 AA):** Relación de contraste medido de \\(7.1:1\\) (supera el estándar \\(\\ge 4.5:1\\)); compatibilidad 100% con lectores de pantalla mediante etiquetas aria-label y roles ARIA semánticos.

**Auditoría de Seguridad de Código Fuente (OWASP Top 10 \- Edición 2025\)**

| Código OWASP 2025 | Vulnerabilidad Evaluada | Estado en Código Source | Mecanismo de Mitigación Implementado en GitHub |
| :---: | :---- | :---: | :---- |
| **A01:2025** | Broken Access Control | **Mitigado** | Middleware RBAC con tokens JWT validados en cada petición. |
| **A02:2025** | Cryptographic Failures | **Mitigado** | Cifrado AES-256 en reposo y hashing Argon2id para contraseñas. |
| **A03:2025** | Injection (SQL/NoSQL) | **Mitigado** | Uso estricto de consultas preparadas (*Prepared Statements*) en ORM. |
| **A04:2025** | Insecure Design | **Mitigado** | Arquitectura Hexagonal que aísla las reglas de negocio del exterior. |
| **A05:2025** | Security Misconfiguration | **Mitigado** | Eliminación de credenciales en duro; uso de variables .env. |

---

**3.8 EJE 8: Evaluación de Capacidad del Proceso según CMMI-DEV y Mejora Continua**

**Diagnóstico de Nivel de Capacidad CMMI (Capability Levels 0 a 3\)**

* **ESTIM (Estimating):** **Nivel 2 (Gestionado)** \- Historias estimadas formalmente mediante *Planning Poker*.  
* **PLAN (Planning):** **Nivel 2 (Gestionado)** \- Sprint Backlog administrado en GitHub Projects con asignación de roles.  
* **CM (Configuration Mgmt.):** **Nivel 3 (Definido)** \- Estrategia GitFlow estandarizada con tags de versión (v1.0-PMV, v2.0).  
* **VER / VAL (Verification & Validation):** **Nivel 2 (Gestionado)** \- Pipelines de CI/CD ejecutando pruebas unitarias y fichas de prueba con capturas.  
* **CAR (Causal Analysis & Resolution):** **Nivel 2 (Gestionado)** \- Plan de mejora continua implementando *pre-commit hooks* para eliminar fallas de compilación.

---

**4\. CONCLUSIONES Y LECCIONES APRENDIDAS**

**4.1 Conclusiones Técnicas del Proceso y Producto**

1. La alineación previa entre el proceso **TO-BE** y la solución de software garantizó que cada componente desarrollado responda a una brecha operativa real, asegurando la entrega de valor organizacional.  
2. La implementación de la **Arquitectura Hexagonal** en la estructura de directorios de GitHub permitió desacoplar totalmente las reglas de negocio del *Domain Core*, facilitando la ejecución de pruebas unitarias de alta velocidad sin dependencias de infraestructura.  
3. La aplicación combinada de los modelos **GQM**, **FURPS+** (con seguridad **OWASP 2025**) y **CMMI-DEV** proporcionó un marco cuantitativo de evaluación que certifica la estabilidad y mantenibilidad de los incrementos liberados.

**4.2 Lecciones Aprendidas en la Adaptación del Ciclo de Vida**

1. Seleccionar un modelo de proceso por moda o popularidad genera desajustes operativos; la adaptación (*tailoring*) debe sustentarse estrictamente en los factores de riesgo e incertidumbre del proyecto.  
2. El establecimiento riguroso de los **Criterios de Terminación (*Definition of Done \- DoD*)** en cada iteración es el mecanismo más efectivo para prevenir la acumulación de deuda técnica.  
3. La automatización de pruebas y análisis estático mediante *pipelines* de CI/CD reduce drásticamente el tiempo dedicado al retrabajo en las fases finales del desarrollo.

---

**REFERENCIAS BIBLIOGRÁFICAS**

* Pressman, R. S. y Maxim, B. R. (2021). *Ingeniería de software: un enfoque práctico* (9.ª ed.). McGraw-Hill.  
* Sommerville, I. (2016). *Software engineering* (10.ª ed.). Pearson Educación.  
* O'Regan, G. (2017). *Concise guide to software engineering: from fundamentals to application methods*. Springer.  
* CMMI Institute. (2018). *CMMI for Development, Version 2.0*. Software Engineering Institute.  
* OWASP Foundation. (2025). *OWASP Top 10:2025 The Ten Most Critical Web Application Security Risks*.

---

**ANEXOS**

**ANEXO A: Enlace del Video Demostrativo del Software**

* **URL del Video Demostrativo (drive):** https\://demo-software-procesos-2026

**ANEXO B: Enlace del Repositorio de Código en GitHub**

* **URL del Repositorio GitHub:** https\://github.com/org-ucontinental/proyecto-procesos-software-2026  
* **Etiquetas de Versión (*Tags*):** v1.0-PMV, v2.0-Inc2, v3.0-Inc3

---

**ANEXO C: GUIÓN TÉCNICO Y NARRATIVO DEL VIDEO DE DEMOSTRACIÓN DEL SOFTWARE**

**Duración Total:** 05 minutos 00 segundos  
**Formato:** Grabación de pantalla con voz en off del equipo y demostración en entorno activo (Staging/Cloud).

| Tiempo | Escena / Pantalla Mostrada | Locución / Explicación Técnica | Criterio de Aceptación / Requerimiento Verificado |
| :---: | :---- | :---- | :---- |
| **00:00 \- 00:45** | Carátula del proyecto, arquitectura de procesos TO-BE y estructura de carpetas de Arquitectura Hexagonal en GitHub. | *"Buenas tardes. Presentamos la demostración funcional del software. Iniciamos mostrando la estructura de directorios en GitHub, donde el núcleo de dominio está 100% desacoplado en /src/domain/ sin dependencias de frameworks."* | **Arquitectura Hexagonal & SCM** (Verificación de Puertos y Adaptadores sin acoplamiento). |
| **00:45 \- 01:45** | Pantalla de Login e interfaz principal. Ejecución del flujo de registro de usuario y autenticación RBAC. | *"Procedemos con el Requerimiento RF-01. Ingresamos las credenciales del operador. Observe el cumplimiento de la paleta de colores (\#1E3A8A) y el contraste de accesibilidad WCAG 2.1. El sistema valida el formulario y genera el token JWT seguro."* | **RF-01 (Autenticación):** Given usuario con datos válidos, When ingresa, Then genera token JWT seguro. |
| **01:45 \- 02:45** | Envío de paquete telemático/evento mediante cliente API REST y recepción inmediata en el panel de monitoreo. | *"Demostramos el RF-02 e ingesta de datos. Enviamos una petición JSON simulando la llegada de un evento. La API responde en menos de 500 ms y actualiza la interfaz automáticamente gracias al patrón asíncrono."* | **RF-02 (Ingesta de Datos):** Procesamiento de paquete de datos y respuesta en \\(\< 2 \\text{ s}\\). |
| **02:45 \- 03:45** | Generación de evento anómalo y despliegue de alerta visual georreferenciada en el mapa. | *"Evaluamos el RF-03 y RF-04 del Incremento 2\. Al ingresar un valor fuera del umbral térmico/operativo, el motor de reglas dispara la alerta de color \#DC2626 y ubica las coordenadas GPS en el mapa interactivo."* | **RF-03 / RF-04 (Alertas y Mapa):** Emisión de alerta push y renderizado georreferenciado. |
| **03:45 \- 04:30** | Módulo de generación de reportes y exportación en formato PDF/Excel. | *"Mostramos el RF-05 del Incremento 3\. Seleccionamos el rango de fechas de la operación y exportamos el reporte consolidado que valida el cumplimiento del valor esperado por la organización."* | **RF-05 (Reportes):** Exportación de información histórica para toma de decisiones. |
| **04:30 \- 05:00** | Ejecución del pipeline de GitHub Actions en pantalla (pruebas unitarias aprobadas y escaneo SonarQube con 0 vulnerabilidades). | *"Finalizamos mostrando la evidencia de calidad. Nuestro pipeline de CI/CD ejecuta el 100% de los tests y confirma 0 vulnerabilidades OWASP 2025 en SonarQube. Muchas gracias."* | **OWASP 2025 & CI/CD:** Verificación de código seguro y pipeline automatizado. |

---

---

**RÚBRICA DE EVALUACIÓN CUANTITATIVA POR NIVELES DE DESEMPEÑO (SOBRE 20 PUNTOS)**

**Asignatura:** Procesos de Software (Código: ASUC01702)  
**Objeto de Evaluación:** Proceso de Software, Producto en GitHub (Arquitectura Hexagonal) y Video Demostrativo  
**Escala de Calificación:** 0 a 20 Puntos

\==================================================================================================================================  
                                    RÚBRICA DE EVALUACIÓN CUANTITATIVA INTEGRADORA (20 PUNTOS)  
\==================================================================================================================================

| Criterio de Evaluación | Excelente (100% Puntaje) | Bueno (75% Puntaje) | Básico (50% Puntaje) | Inicial (25% Puntaje) | Puntaje Máximo |
| :---- | :---- | :---- | :---- | :---- | :---: |
| **1\. Evaluación del Proceso de Software (*Tailoring*, WBS, RAE, CMMI)** | Sustenta con rigor la adaptación del ciclo de vida (*tailoring*), categoriza procesos, define matriz RAE, criterios *DoD*, WBS, control de desviaciones y audita la capacidad según CMMI-DEV. | Adapta el ciclo de vida, categoriza los procesos principales, organiza el trabajo con matriz RAE, WBS y evalúa el proceso adecuadamente. | Presenta una planificación de proceso parcial; justificaciones de *tailoring* débiles o sin evaluación clara de capacidad CMMI. | Proceso desorganizado, sin adaptación de ciclo de vida (*tailoring*), sin WBS ni controles de desviación. | **5.0 Puntos** |
| **2\. Evaluación del Producto de Software en GitHub y Arquitectura Hexagonal** | Estructura en GitHub la **Arquitectura Hexagonal** (/src/domain/, /src/ports/, /src/adapters/) demostrando cero acoplamiento de frameworks en el Dominio y tags de versión (v1.0-PMV). | Organiza la Arquitectura Hexagonal en GitHub con separación de carpetas y repositorio estructurado con historial de commits. | Estructura de carpetas en GitHub incompleta o con acoplamiento entre clases de dominio y frameworks externos. | No demuestra la aplicación de la Arquitectura Hexagonal en GitHub ni presenta repositorio estructurado. | **6.0 Puntos** |
| **3\. Estrategia de Pruebas, FURPS+ y Seguridad OWASP 2025** | Adjunta fichas de prueba con capturas para **TODOS** los RFs, evalúa usabilidad (WCAG 2.1 AA, colores) y audita seguridad de código bajo **OWASP Top 10 (2025)** con 0 vulnerabilidades. | Presenta fichas de prueba con capturas de pantalla para la mayoría de RFs, evalúa usabilidad y verifica seguridad de código. | Presenta pruebas o capturas de pantalla parciales/borrosas; revisión superficial de seguridad OWASP o accesibilidad. | Sin evidencias visuales de pruebas por requerimiento, sin auditoría de seguridad OWASP 2025 ni evaluación FURPS+. | **4.0 Puntos** |
| **4\. Video Demostrativo y Guión Técnico del Software** | Presenta un video fluido del software desplegado que cumple el guión técnico minuto a minuto, demostrando los RFs, la arquitectura en Git y la generación de valor. | Presenta un video claro del software en ejecución demostrando las funcionalidades principales del PMV e incrementos. | Presenta un video con fallos operacionales durante la demostración o que no sigue una estructura técnica guiada. | El software no es ejecutable, no se presenta video demostrativo o este dura menos del mínimo requerido. | **5.0 Puntos** |

\==================================================================================================================================  
                                                TABLA RESUMEN DE EVALUACIÓN  
\==================================================================================================================================  
Criterio Evaluado                                                  Puntaje Máximo      Puntaje Obtenido     Observaciones  
\----------------------------------------------------------------------------------------------------------------------------------  
1\. Evaluación del Proceso de Software (Tailoring, WBS, CMMI)          5.0 Puntos            \_\_\_\_\_\_          \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
2\. Producto de Software en GitHub y Arquitectura Hexagonal            6.0 Puntos            \_\_\_\_\_\_          \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
3\. Estrategia de Pruebas, FURPS+ y Seguridad OWASP 2025                4.0 Puntos            \_\_\_\_\_\_          \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
4\. Video Demostrativo y Guión Técnico del Software                    5.0 Puntos            \_\_\_\_\_\_          \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
\----------------------------------------------------------------------------------------------------------------------------------  
NOTA FINAL CONSOLIDADA                                                20.0 PUNTOS            \_\_\_\_\_\_          \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
\==================================================================================================================================  
---

