**GUÍA DE TRABAJO SEMANA 10 – UNIDAD III: EVALUACIÓN DE LA CALIDAD DEL PRODUCTO DE SOFTWARE MEDIANTE EL MODELO FURPS+**

**Asignatura:** Procesos de Software (Código: ASUC01702)  
**Nivel:** 9.º período / Noveno ciclo (Electivo de Especialidad \- Nivel Logrado)  
**Unidad III:** Evolución de los procesos y actividades de software  
**Resultado de Aprendizaje de la Unidad:** Al finalizar la unidad, el estudiante será capaz de proponer mejoras en el proceso de software usado en una organización a partir de la evaluación de resultados.  
**Eje Temático Evaluado:** Modelos de Evaluación de Procesos y Productos de Software – Aplicación del **Modelo de Calidad FURPS+** para evaluar los **Requerimientos Funcionales (Factor F)** en los **Incrementos 1, 2 y 3**, los **Requerimientos No Funcionales Clave (Factores URPS: Usabilidad, Confiabilidad, Rendimiento, Soportabilidad)** incluyendo **Arquitectura Hexagonal, Psicología de Colores, Accesibilidad e Inclusión**, y el **Factor \+ (Seguridad con OWASP 2025 y Restricciones Técnicas)**.

---

**I. EXPLICACIÓN Y MARCO TEÓRICO DEL MODELO DE EVALUACIÓN FURPS+**

El modelo de calidad **FURPS+**, desarrollado por Robert Grady y Hewlett-Packard (HP) y expandido en el marco de Rational Unified Process (RUP), es una estructura normativa utilizada en la ingeniería de software para categorizar, auditar y medir exhaustivamente las características de calidad de un producto de software.

La taxonomía **FURPS+** divide los requerimientos y atributos de calidad en dos grandes dimensiones:

\========================================================================================================  
                          ESTRUCTURA DEL MODELO DE CALIDAD DE PRODUCTO FURPS+  
\========================================================================================================

 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐  
 │  F \- FUNCTIONALITY (Funcionalidad)                                                                 │  
 │  • Capacidades, características del sistema, generalidad de funciones y seguridad de acceso.        │  
 │  • Se evalúa de manera evolutiva en cada versión liberada: Incremento 1 (PMV), Incremento 2 e 3\.   │  
 └────────────────────────────────────────────────────────────────────────────────────────────────────┘  
                                                  │  
                                                  ▼  
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐  
 │  FACTORES URPS (Requerimientos No Funcionales Claves del Proyecto)                                  │  
 ├────────────────────────────────────────────────────────────────────────────────────────────────────┤  
 │  • U \- USABILITY (Usabilidad): Factores humanos, estética, Psicología de Colores según el dominio,  │  
 │    consistencia UI, y criterios normativos de Accesibilidad e Inclusión (WCAG 2.1/2.2 AA).       │  
 │  • R \- RELIABILITY (Confiabilidad): Frecuencia de fallas, tolerancia, disponibilidad (MTBF/MTTR).   │  
 │  • P \- PERFORMANCE (Rendimiento): Tiempo de respuesta (p95), throughput (RPS) y uso de memoria.    │  
 │  • S \- SUPPORTABILITY (Soportabilidad): Evaluación de la ARQUITECTURA HEXAGONAL (desacoplamiento    │  
 │    del dominio en GitHub), mantenibilidad, testabilidad, modularidad y extensibilidad.            │  
 └────────────────────────────────────────────────────────────────────────────────────────────────────┘  
                                                  │  
                                                  ▼  
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐  
 │  \+ (PLUS) \- RESTRICCIONES ADICIONALES Y SEGURIDAD DE CÓDIGO                                         │  
 ├────────────────────────────────────────────────────────────────────────────────────────────────────┤  
 │  • Auditoría de Seguridad de Código Fuente bajo el estándar OWASP Top 10 (Edición 2025).           │  
 │  • Restricciones de Diseño, Implementación, Interfaz (OpenAPI) y Físicas/Infraestructura (Docker). │  
 └────────────────────────────────────────────────────────────────────────────────────────────────────┘  
---

**II. CONSIGNA GENERAL Y OBJETIVOS DE LA GUÍA**

**1\. Propósito de la Actividad**

Guiar a los equipos de trabajo en la realización de una **auditoría integral de calidad del producto de software** para su proyecto de asignatura, aplicando el modelo **FURPS+**. Se verificará la evolución funcional en los **Incrementos 1 (PMV), 2 y 3**, se medirá el cumplimiento de los **Requerimientos No Funcionales clave (URPS)** —con especial énfasis en la **Arquitectura Hexagonal**, la **Psicología de Colores** aplicada a la temática del proyecto y los **Criterios de Accesibilidad e Inclusión (WCAG 2.1)**—, y se auditará la **seguridad del código fuente (OWASP 2025\)** junto con las restricciones técnicas en el repositorio de GitHub.

**2\. Productos Esperados del Equipo**

1. **Ficha de Criterios y Métricas de Calidad FURPS+** adaptada al dominio del proyecto.  
2. **Matriz de Evaluación del Factor F (Functionality):** Auditoría incremental de requerimientos funcionales en el **Incremento 1 (PMV), Incremento 2 e Incremento 3**.  
3. **Matriz de Evaluación de Factores URPS:**   
   * **Usabilidad (U):** Evaluación estética, **Psicología de Colores** por dominio y **Accesibilidad e Inclusión (WCAG 2.1 AA)**.  
   * **Confiabilidad (R):** Disponibilidad, tolerancia a fallas y MTTR.  
   * **Rendimiento (P):** Latencia p95, throughput (RPS) y uso de recursos.  
   * **Soportabilidad (S):** Auditoría de **Arquitectura Hexagonal** (Puertos y Adaptadores) en la estructura de carpetas de GitHub.  
4. **Informe de Auditoría de Código del Factor \+ (OWASP Top 10 \- 2025 y Restricciones Técnicas).**  
5. **Consolidado del Índice de Calidad FURPS+ (%) y Plan de Evolución del Producto.**

---

**III. ACTIVIDADES PRÁCTICAS A DESARROLLAR EN EL PROYECTO DE ASIGNATURA**

---

**ACTIVIDAD 1: Configuración de Criterios y Métricas FURPS+ del Proyecto**

Cada equipo debe definir los umbrales de calidad aplicables a las características de su solución tecnológica.

**Matriz 1.1: Ficha de Configuración de Criterios FURPS+**

| Factor FURPS+ | Atributo de Calidad Evaluado | Método de Extracción / Herramienta | Umbral / Criterio de Aceptación |
| :---: | :---- | :---- | :---- |
| **F** | Cobertura Funcional Incremental | Pruebas de Aceptación con Evidencias | \\(100%\\) de RFs aprobados en Inc. 1, 2 y 3 |
| **U** | Psicología de Colores y Accesibilidad | Paleta cromática \+ Lector de pantalla / Axe Core | Contraste \\(\\ge 4.5:1\\) y Cumplimiento WCAG 2.1 AA |
| **R** | Confiabilidad y Tolerancia a Fallas | Monitoreo en Staging / Logs de servidor | Disponibilidad \\(\\ge 99.5%\\) y MTTR \\(\< 5 \\text{ min}\\) |
| **P** | Latencia y Concurrencia | Pruebas de Carga con k6 / JMeter | Latencia p95 \\(\< 800 \\text{ ms}\\) a 500 usuarios |
| **S** | **Arquitectura Hexagonal** y Mantenibilidad | Estructura GitHub / SonarQube | Cero acoplamiento de frameworks en Dominio |
| **\+** | **Seguridad de Código (OWASP 2025\)** | Análisis SAST (Semgrep / SonarCloud / ZAP) | **0 Vulnerabilidades Críticas o Altas** |

---

**ACTIVIDAD 2: Evaluación del Factor F (Functionality) por Incrementos (Inc. 1, Inc. 2 e Inc. 3\)**

Audite la evolución funcional del producto de software verificando que cada Requerimiento Funcional (RF) o Historia de Usuario (HU) cumpla con sus criterios de aceptación en los tres hitos de entrega:

* **Incremento 1 (PMV \- Núcleo Operativo):** Funcionalidades de registro, autenticación, ingesta de datos y alerta básica.  
* **Incremento 2 (Evolución y Procesamiento):** Motor de reglas, procesamiento avanzado, mapa o monitoreo en tiempo real.  
* **Incremento 3 (Consolidación e Integración):** Exportación de reportes, analítica histórica e integración con APIs externas.

**Matriz 2.1: Auditoría del Factor F en los Incrementos 1, 2 y 3**

| Cód. RF | Descripción del Requerimiento Funcional | Incremento Evaluado | Criterio de Aceptación (*Given-When-Then*) | Estado (Aprobado / Rechazado) | Archivo de Evidencia en Git / Captura |
| :---: | :---- | :---: | :---- | :---: | :---- |
| **RF-01** | Registro de usuario y control de accesos. | **Inc. 1 (PMV)** | *Dado* un usuario con datos válidos, *cuando* presiona registrar, *entonces* se crea el perfil con token seguro. | **Aprobado** | tests/inc1/test\_auth.py/evidencias/RF01\_login.png |
| **RF-02** | Ingesta y recepción de datos telemáticos/eventos. | **Inc. 1 (PMV)** | *Dado* un paquete de datos, *cuando* ingresa a la API, *entonces* se procesa en \\(\< 2 \\text{ s}\\). | **Aprobado** | tests/inc1/test\_ingesta.py/evidencias/RF02\_ingesta.png |
| **RF-03** | Motor de evaluación de reglas y alertas. | **Inc. 2** | *Dado* un evento anómalo, *cuando* se evalúa la regla, *entonces* emite notificación push. | **Aprobado** | tests/inc2/test\_rules.py/evidencias/RF03\_alerta.png |
| **RF-04** | Panel de visualización y seguimiento en mapa. | **Inc. 2** | *Dado* un evento activo, *cuando* se abre el mapa, *entonces* renderiza las coordenadas GPS. | **Aprobado** | tests/inc2/test\_mapa.py/evidencias/RF04\_mapa.png |
| **RF-05** | Exportación de reportes y análisis consolidado. | **Inc. 3** | *Dado* un rango de fechas, *cuando* se solicita el reporte, *entonces* genera un archivo PDF/Excel. | **Aprobado** | tests/inc3/test\_export.py/evidencias/RF05\_reporte.png |
| **RF-06** | Integración API REST para consumo externo. | **Inc. 3** | *Dado* un sistema externo autenticado, *cuando* consume el endpoint, *entonces* recibe data JSON. | **Aprobado** | tests/inc3/test\_apiext.py/evidencias/RF06\_api.png |

---

**ACTIVIDAD 3: Evaluación de los Factores URPS (Requerimientos No Funcionales Clave)**

Mida los Requerimientos No Funcionales clave especificando métricas para cada una de las cuatro dimensiones URPS:

**3.1 Evaluaciones del Factor U (Usability): Psicología de Colores, Accesibilidad e Inclusión**

**A. Evaluación de la Psicología de Colores Aplicada a la Temática del Proyecto**

El equipo debe justificar la paleta cromática seleccionada según el dominio de aplicación del software (ej. *Salud:* Azul/Verde para calma y confianza; *Seguridad/Alertas:* Rojo/Naranja/Amarillo para jerarquía de riesgos; *Medio Ambiente/Agrícola:* Verde/Marrón para sostenibilidad):

| Rol de Color en la Interfaz | Código Hexadecimal | Significado Cromático yJustificación Psicológica según el Dominio | Evaluación de Consistencia UI |
| :---- | :---: | :---- | :---: |
| **Color Primario (Dominante)** | \#1E3A8A (Azul Noche) | Transmite profesionalismo, seguridad y estabilidad en el manejo de datos críticos. | **Conforme** |
| **Color Secundario (Acción)** | \#059669 (Verde Esmeralda) | Representa éxito, confirmación de procesos y estados operativos seguros. | **Conforme** |
| **Color Alerta / Emergencia** | \#DC2626 (Rojo Carmesí) | Estimula la atención inmediata ante rupturas de umbral o eventos de riesgo. | **Conforme** |
| **Color Neutro / Fondo** | \#F8FAFC (Gris Pálido) | Reduce la fatiga visual del usuario durante jornadas extendidas de monitoreo. | **Conforme** |

**B. Criterios de Accesibilidad e Inclusión (Estándar WCAG 2.1 / 2.2 Nivel AA)**

Evalúe la inclusión de usuarios con diversidad funcional (visutal, motora, cognitiva):

| Criterio WCAG 2.1 | Pauta de Accesibilidad e Inclusión Evaluada | Resultado Medido / Herramienta | Estado |
| :---- | :---- | :---- | :---: |
| **Contrast (1.4.3)** | Relación de contraste de texto normal \\(\\ge 4.5:1\\) sobre fondos. | Medido con *Color Contrast Analyzer* (Resultado: \\(7.1:1\\)). | **Cumple** |
| **Non-text Content (1.1.1)** | Todos los elementos visuales e íconos poseen atributos alt / aria-label. | Auditado con *Axe Core / Lighthouse* (100% de imágenes etiquetadas). | **Cumple** |
| **Keyboard Accessible (2.1.1)** | Navegación 100% funcional mediante teclado (Tab, Enter, Esc) con foco visible. | Prueba manual de recorrido por teclado sin trampas de foco. | **Cumple** |
| **Screen Reader Friendly (4.1.2)** | Compatibilidad de componentes interactivos con lectores de pantalla (NVDA / TalkBack). | Etiquetado correcto con roles semánticos ARIA (role="button", aria-live). | **Cumple** |

**3.2 Evaluación de Factores R (Reliability), P (Performance) y S (Supportability \- Arquitectura Hexagonal)**

**Matriz 3.2: Evaluaciones de R, P y S**

| Factor URPS | Atributo / Componente Evaluado | Requerimiento No Funcional Específico | Métrica / Método de Extracción | Valor Medido | Estado |
| :---: | :---- | :---- | :---- | :---: | :---: |
| **R (Reliability)** | **Tolerancia a Fallas** | El sistema debe recuperarse automáticamente ante caídas del servidor de BD. | Prueba de caos (*Kill process*) y reconexión en pool. | Reconexión en \\(3.2 \\text{ s}\\) | **Cumple** |
| **R (Reliability)** | **Disponibilidad** | Tiempo de actividad en el entorno de pruebas Staging. | Uptime de servicios en AWS / CloudWatch. | \\(99.78%\\) disponibilidad | **Cumple** |
| **P (Performance)** | **Latencia REST** | Tiempo de respuesta percentil 95 en endpoints principales. | Ejecución de script k6 con 500 usuarios virtuales. | \\(620 \\text{ ms}\\) | **Cumple** |
| **P (Performance)** | **Rendimiento (Throughput)** | Procesamiento de peticiones concurrentes por segundo. | Capacidad de respuesta del servidor (RPS). | \\(340 \\text{ req/s}\\) | **Cumple** |
| **S (Supportability)** | **ARQUITECTURA HEXAGONAL** | **Auditoría de desacoplamiento del Núcleo de Dominio en GitHub.** | Verificación de cero dependencias externas en /src/domain/. | **0 Importaciones de Frameworks** | **Cumple** |
| **S (Supportability)** | **Testabilidad y Cobertura** | Cobertura de código fuente por pruebas unitarias/integración. | Reporte automatizado en Jacoco / Istanbul / Jest. | \\(84.5%\\) cobertura | **Cumple** |

**C. Auditoría Detallada de la Arquitectura Hexagonal (Factor S) en la Carpeta GitHub**

El equipo debe verificar la estructura del repositorio GitHub demostrando la separación en **Puertos y Adaptadores**:

/src  
├── domain/                         \<── DOMAIN CORE (100% Código Puro: Entidades y Reglas de Negocio)  
│   ├── model/                      \<── Entidades (cero anotaciones JPA, Spring o marcos de BD)  
│   └── service/                    \<── Servicios de Dominio  
├── ports/                          \<── PUERTOS (Interfaces de Abstracción)  
│   ├── inbound/                    \<── Input Ports (Interfaces de Casos de Uso)  
│   └── outbound/                   \<── Output Ports (Interfaces para Persistencia/Notificaciones)  
└── adapters/                       \<── ADAPTADORES (Infraestructura Externa e Implementaciones)  
    ├── inbound/                    \<── Inbound Adapters (Controllers REST, MQTT Subscribers)  
    └── outbound/                   \<── Outbound Adapters (Repositories JPA/PostgreSQL, Redis, Firebase)  
---

**ACTIVIDAD 4: Evaluación del Factor \+ (Plus) – Seguridad de Código con OWASP 2025 y Restricciones Técnicas**

Ejecute un análisis estático de seguridad (SAST) sobre el código fuente en GitHub auditando las 10 vulnerabilidades críticas de **OWASP Top 10 (Edición 2025\)** y verificando las restricciones técnicas:

**4.1 Auditoría de Seguridad de Código Fuente (OWASP Top 10 \- Edición 2025\)**

| Código OWASP 2025 | Vulnerabilidad Evaluada | Estado en el Código Fuente | Mecanismo de Mitigación / Código Seguro Implementado en Git |
| :---: | :---- | :---: | :---- |
| **A01:2025** | **Broken Access Control** | **Mitigado** | Middleware RBAC (*Role-Based Access Control*) con tokens JWT validados. |
| **A02:2025** | **Cryptographic Failures** | **Mitigado** | Cifrado AES-256 para datos sensibles y hashing Argon2id para credenciales. |
| **A03:2025** | **Injection** (SQL/NoSQL/Command) | **Mitigado** | Consultas preparadas (*Prepared Statements*) en ORM; cero concatenación SQL. |
| **A04:2025** | **Insecure Design** | **Mitigado** | Aplicación de **Arquitectura Hexagonal** aislando reglas del entorno externo. |
| **A05:2025** | **Security Misconfiguration** | **Mitigado** | Uso de variables de entorno (.env) en Secrets Manager; cero credenciales en código. |
| **A06:2025** | **Vulnerable & Outdated Components** | **Mitigado** | Escaneo con Dependabot y OWASP Dependency-Check (0 vulnerabilidades). |
| **A07:2025** | **Identification & Auth Failures** | **Mitigado** | Políticas de contraseñas fuertes, MFA y bloqueo tras 3 intentos fallidos. |
| **A08:2025** | **Software & Data Integrity Failures** | **Mitigado** | Firma de artefactos en GitHub Actions y verificación de hashes en librerías. |
| **A09:2025** | **Security Logging & Monitoring** | **Mitigado** | Logs de auditoría centralizados sin registrar tokens ni contraseñas. |
| **A10:2025** | **Server-Side Request Forgery (SSRF)** | **Mitigado** | Lista blanca (*allowlist*) de dominios y URLs permitidas en peticiones salientes. |

**4.2 Restricciones Técnicas Adicionales (Factor \+)**

| Tipo de Restricción | Especificación del Proyecto | Estado | Evidencia Técnica en Repositorio GitHub |
| :---- | :---- | :---: | :---- |
| **Restricción de Diseño** | Mantenimiento del patrón de Arquitectura Hexagonal. | **Conforme** | Carpetas /src/domain/, /src/ports/, /src/adapters/ en Git. |
| **Restricción de Implementación** | Uso de lenguaje nativo y cumplimiento de linter. | **Conforme** | Reporte ESLint / Pylint con 0 errores bloqueantes. |
| **Restricción de Interfaz** | Contrato de API documentado con OpenAPI 3.0. | **Conforme** | Archivo openapi.json accesible en Swagger UI. |
| **Restricción de Despliegue** | Contenerización de servicios mediante Docker. | **Conforme** | Archivos Dockerfile y docker-compose.yml ejecutables. |

---

**ACTIVIDAD 5: Consolidación del Índice de Calidad FURPS+ (%) y Plan de Evolución del Producto**

Sume los puntajes obtenidos en cada dimensión para calcular el **Índice Global de Calidad del Producto (\\(IC\_P\\))**:

\\\[\\text{Índice Global de Calidad FURPS+} (IC\_P) \= \\sum \\left( \\text{Puntaje Obtenido en Factor (%)} \\times \\text{Peso Asignado} \\right)\\\]

**Matriz 5.1: Cuadro de Mando Consolidado FURPS+**

| Factor FURPS+ | Peso Asignado | Cumplimiento Obt. (%) | Puntaje Ponderado | Brecha Identificada | Acción de Evolución / Mejora |
| :---: | :---: | :---: | :---: | :---- | :---- |
| **F \- Funcionalidad** | \\(30%\\) | \\(100%\\) | \\(30.0%\\) | Ninguna brecha en Inc. 1, 2 y 3\. | Mantener matriz de pruebas de aceptación. |
| **U \- Usabilidad** | \\(15%\\) | \\(95%\\) | \\(14.25%\\) | Ajuste menor en contraste de texto. | Corregir color de botones secundarios en CSS. |
| **R \- Confiabilidad** | \\(15%\\) | \\(96%\\) | \\(14.4%\\) | Reintentos en conexión de BD. | Ajustar el pool de conexiones HikariCP. |
| **P \- Rendimiento** | \\(15%\\) | \\(92%\\) | \\(13.8%\\) | Latencia leve en consultas complejas. | Optimizar índices en la base de datos PostgreSQL. |
| **S \- Soportabilidad** | \\(10%\\) | \\(100%\\) | \\(10.0%\\) | Arquitectura Hexagonal 100% aislada. | Preservar estructura de carpetas en GitHub. |
| **\+ \- Seguridad / Restr.** | \\(15%\\) | \\(100%\\) | \\(15.0%\\) | Cero vulnerabilidades OWASP 2025\. | Mantener escaneo SAST en GitHub Actions. |
| **TOTAL** | **\\(100%\\)** | \-- | **\\(97.45%\\)** | **Calidad del Producto: EXCELENTE (\\(\\ge 90%\\))** |  |

---

**IV. ESTRUCTURA DEL ENTREGABLE GRUPAL EN EL AULA VIRTUAL**

Cada equipo deberá entregar en el aula virtual un **Informe de Evaluación de Calidad FURPS+ (PDF)** y adjuntar las evidencias en su repositorio de código:

\========================================================================================================  
           INFORME TÉCNICO: EVALUACIÓN DE CALIDAD DE PRODUCTO DE SOFTWARE (FURPS+)  
\========================================================================================================

1\. CARÁTULA E INTEGRANTES DEL EQUIPO (Noveno Ciclo)  
2\. RESUMEN EJECUTIVO Y CRITERIOS DE EVALUACIÓN FURPS+ (Actividad 1\)  
3\. AUDITORÍA DEL FACTOR F: FUNCIONALIDAD EN INCREMENTOS 1, 2 Y 3 (Actividad 2\)  
   \- Matriz de trazabilidad de Requerimientos Funcionales y evidencias  
4\. EVALUACIÓN DE FACTORES URPS: NO FUNCIONALES CLAVE (Actividad 3\)  
   \- Usabilidad: Psicología de Colores por Dominio y Accesibilidad WCAG 2.1 AA  
   \- Confiabilidad y Rendimiento  
   \- Soportabilidad: Auditoría de Arquitectura Hexagonal en GitHub  
5\. EVALUACIÓN DEL FACTOR \+ (PLUS): OWASP TOP 10 (2025) Y RESTRICCIONES (Actividad 4\)  
   \- Reporte de Análisis Estático de Seguridad (SAST) y Restricciones Técnicas (Docker/OpenAPI)  
6\. CONSOLIDADO DEL ÍNDICE DE CALIDAD FURPS+ Y PLAN DE EVOLUCIÓN (Actividad 5\)  
7\. CONCLUSIONES Y LECCIONES APRENDIDAS SOBRE LA EVALUACIÓN DEL PRODUCTO  
8\. ANEXOS Y EVIDENCIAS TÉCNICAS:  
   \- Reporte exportado de SonarQube / SAST / Axe Core.  
   \- Gráficos de pruebas de carga k6 para el Factor P (Performance).  
   \- Enlace al Repositorio GitHub con las etiquetas \`v1.0-PMV\`, \`v2.0-Inc2\` y \`v3.0-Inc3\`.  
---

**V. RÚBRICA DE EVALUACIÓN SUMATIVA (20 PUNTOS)**

| Criterio de Evaluación | Excelente (4 pts) | Bueno (3 pts) | Básico (2 pts) | Inicial (1 pt) |
| :---- | :---- | :---- | :---- | :---- |
| **Factor F (Funcionalidad por Incrementos)** | Audita el Factor F en los **Incrementos 1, 2 y 3** con criterios *Given-When-Then* y evidencias verificables en Git. | Audita el Factor F en los tres incrementos con criterios de aceptación claros. | Audita la funcionalidad de forma incompleta o sin diferenciar adecuadamente los tres incrementos. | Presenta una lista genérica de requerimientos sin evaluación ni relación con los incrementos. |
| **Factor U (Usabilidad: Colores y Accesibilidad)** | Evalúa la **Psicología de Colores** fundamentada en el dominio y verifica los criterios de **Accesibilidad e Inclusión (WCAG 2.1 AA)**. | Evalúa la usabilidad incluyendo la paleta de colores y criterios básicos de accesibilidad. | Evalúa la usabilidad de forma superficial sin análisis cromático ni normativo de accesibilidad. | Omite la evaluación de psicología de colores y accesibilidad e inclusión. |
| **Factor S (Soportabilidad y Arquitectura Hexagonal)** | Audita y demuestra la **Arquitectura Hexagonal** en la estructura de carpetas de GitHub con cero contaminación del dominio. | Audita la Arquitectura Hexagonal en GitHub identificando la separación de carpetas. | Presenta una auditoría de arquitectura incompleta o con acoplamiento en el dominio. | No audita la Arquitectura Hexagonal en el repositorio GitHub. |
| **Factor \+ (Seguridad OWASP 2025 y Restricciones)** | Audita la seguridad de código frente al estándar **OWASP Top 10 (2025)** y verifica las restricciones técnicas (OpenAPI, Docker). | Audita la seguridad del código frente a OWASP y verifica las restricciones principales. | Realiza una revisión superficial de seguridad o no utiliza el estándar OWASP 2025\. | No presenta evaluación de seguridad de código ni restricciones técnicas. |
| **Consolidado FURPS+ y Repositorio Git** | Calcula el Índice Global FURPS+, plantea un plan de evolución y adjunta repositorio Git con tags de los 3 incrementos. | Calcula el índice de calidad FURPS+ y presenta repositorio organizado con versiones. | Presenta un consolidado incompleto o inconsistencias en las etiquetas del repositorio Git. | Entregables desorganizados sin cálculo de índice ni repositorio de código. |

**Puntaje Máximo:** 20 puntos

