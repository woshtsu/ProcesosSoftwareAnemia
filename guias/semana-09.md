**GUÍA DE TRABAJO Semana 9: EVALUACIÓN DEL PROCESO Y PRODUCTO DE SOFTWARE MEDIANTE EL MODELO GQM**

**Asignatura:** Procesos de Software (Código: ASUC01702)
**Nivel:** 9.º período / Noveno ciclo (Electivo de Especialidad - Nivel Logrado)
**Unidad III / IV:** Evolución de los procesos, actividades y medición del software
**Resultado de Aprendizaje de la Asignatura:** Aplicar la mejora continua en el proceso de software usado en una organización, incorporando las técnicas y actividades requeridas en el ciclo de vida del desarrollo de software.
**Eje Temático Evaluado:** Evaluación de Proceso y Producto mediante el paradigma **GQM (Goal-Question-Metric)**, auditando la **Arquitectura Hexagonal en el repositorio GitHub**, la **Estrategia de Pruebas de los Incrementos 1 y 2 con Evidencias Fotográficas** y la **Entrega Directa de Valor al Usuario Final**.

**I. CONSIGNA GENERAL DEL TRABAJO**

**1. Propósito de la Actividad**

Guiar a los equipos de trabajo en la construcción e implementación de un **Plan de Evaluación y Medición del Proceso y Producto de Software** aplicando el modelo **GQM (Goal-Question-Metric)**. La guía integra los tres pilares técnicos del noveno ciclo:

1. **Evaluación de la Arquitectura Hexagonal:** Verificación del desacoplamiento estructural de la lógica de negocio directamente en la carpeta y repositorio de GitHub.
2. **Evaluación de Pruebas de Software (Incrementos 1 y 2):** Verificación funcional de cada requerimiento mediante Fichas de Pruebas y evidencias visuales (capturas de pantalla).
3. **Evaluación del Proceso y Producto con Entrega de Valor:** Medición del impacto real de los incrementos entregados frente a las brechas y necesidades del usuario final.

**2. Cadena Metodológica de Trazabilidad Integrada**

Problema Organizacional-Proceso TO-BE-Modelo Adaptado-Arquitectura Hexagonal en Git-Pruebas Inc. 1 y 2-GQM-Valor al Usuario

**II. ACTIVIDADES PRÁCTICAS A DESARROLLAR EN EL PROYECTO DE ASIGNATURA**

**ACTIVIDAD 1: Formulación de Objetivos de Medición GQM (Nivel G - Goal)**

Cada equipo debe redactar **3 Objetivos GQM** utilizando la estructura formal de 5 elementos (Objeto, Propósito, Enfoque de Calidad, Punto de Vista y Contexto):

**Matriz 1.1: Objetivos de Medición GQM del Proyecto**

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| **Código Goal** | **Dimensión Evaluada** | **Objeto a Evaluar** | **Propósito de Medición** | **Enfoque de Calidad / Atributo** | **Punto de Vista** | **Contexto de Aplicación** |
| **G-01** | **Producto (Arquitectura)** | Estructura de código en el repositorio GitHub | Evaluar el nivel de desacoplamiento | Mantenibilidad e independencia tecnológica | Arquitecto de Software | Estructura de carpetas de Arquitectura Hexagonal |
| **G-02** | **Producto (Pruebas)** | Incremento 1 (PMV) e Incremento 2 | Verificar la estabilidad funcional | Cobertura de pruebas y tasa de fallas | Responsable de QA / Testers | Pruebas de integración con capturas de evidencia |
| **G-03** | **Proceso y Producto (Valor)** | Proceso de software y entregables funcionales | Evaluar la efectividad del proceso | Generación de valor organizacional e impacto | Usuario Final / Product Owner | Operación real del software frente al proceso TO-BE |

**ACTIVIDAD 2: Formulación del Árbol de Preguntas de Evaluación (Nivel Q - Questions)**

Para cada objetivo definido en la Actividad 1, formule preguntas orientadoras específicas:

* **Preguntas para G-01 (Arquitectura Hexagonal en GitHub):**
  + **Q1.1:** ¿El núcleo de dominio (*Domain Core*) se encuentra aislado de marcos de trabajo (*frameworks*) y librerías externas en la estructura de directorios?
  + **Q1.2:** ¿Los Puertos de Entrada/Salida (*Ports*) y Adaptadores (*Adapters*) están organizados correctamente en módulos independientes de GitHub?
* **Preguntas para G-02 (Pruebas de Incrementos 1 y 2):**
  + **Q2.1:** ¿Qué porcentaje de Requerimientos Funcionales del Incremento 1 y 2 cuenta con evidencias fotográficas aprobadas?
  + **Q2.2:** ¿Cuál es la densidad de defectos funcionales detectados entre la entrega del PMV (Inc. 1) y el Incremento 2?
* **Preguntas para G-03 (Proceso y Valor al Usuario Final):**
  + **Q3.1:** ¿En qué medida las funcionalidades entregadas en los incrementos reducen las brechas operativas identificadas en el proceso AS-IS?
  + **Q3.2:** ¿Cómo evolucionan los indicadores de valor del usuario (tiempos de respuesta, disponibilidad y satisfacción) con cada incremento liberado?

**ACTIVIDAD 3: Matriz Operativa de Métricas e Indicadores (Nivel M - Metrics)**

**Matriz 3.1: Definición de Métricas GQM**

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Cód. Goal** | **Cód. Preg.** | **Cód. Mét.** | **Nombre de la Métrica** | **Fórmula / Método de Extracción** | **Fuente de Datos** | **Valor Meta (Inc. 1)** | **Valor Meta (Inc. 2)** |
| **G-01** | **Q1.1** | **M1.1** | Índice de Contaminación del Dominio | Librerías de Frameworks Importadas en Domain Total de Clases de Dominio | Estructura de carpetas / SonarQube | \[0.0%\] | \[0.0%\] |
| **G-01** | **Q1.2** | **M1.2** | Cohesión de Módulos Hexagonales | Conforme / Non-Conforme según mapeo Git | Repositorio GitHub | \[100%\] Conformidad | \[100%\] Conformidad |
| **G-02** | **Q2.1** | **M2.1** | Cobertura Funcional con Capturas | RFs con Captura Aprobada Total de RFs del Incremento \ 100% | Fichas de Pruebas / Capturas | \[100%\] | \[100%\] |
| **G-02** | **Q2.2** | **M2.2** | Tasa de Defectos Funcionales | \[\frac{\text{N.º Defectos Funcionales Detectados}}{\text{Total de Requerimientos Funcionales}}\] | GitHub Issues / QA Report | \[\le 1.0\text{ Def/RF}\] | \[\le 0.2\text{ Def/RF}\] |
| **G-03** | **Q3.1** | **M3.1** | Cobertura de Brechas Resueltas | \[\left(\frac{\text{Brechas del AS-IS Resueltas}}{\text{Total de Brechas Identificadas}}\right) \times 100%\] | Matriz de Trazabilidad | \[\ge 60%\] | \[\ge 90%\] |
| **G-03** | **Q3.2** | **M3.2** | Índice de Impacto en Valor | Medición del indicador de valor del usuario | Dashboard / Feedback | Mejora \(\ge 50%\) | Mejora \(\ge 80%\) |

**ACTIVIDAD 4: Evaluación de la Arquitectura Hexagonal en la Carpeta GitHub**

El equipo debe auditar la estructura de directorios del repositorio institucional de GitHub para verificar el cumplimiento del patrón de **Puertos y Adaptadores**:

/src

├── domain/ <── NÚCLEO DE DOMINIO (100% Peticiones Puras en Lenguaje Nativo)

│ ├── model/ <── Entidades y Objetos de Valor (sin anotaciones de BD/Frameworks)

│ └── service/ <── Servicios de Dominio (Reglas de Negocio)

├── ports/ <── PUERTOS (Interfaces)

│ ├── inbound/ <── Input Ports (Casos de Uso de la Aplicación)

│ └── outbound/ <── Output Ports (Interfaces para Persistencia, Notificaciones, etc.)

└── adapters/ <── ADAPTADORES (Infraestructura Externa)

├── inbound/ <── Inbound Adapters (Controllers REST, MQTT Subscribers, CLI)

└── outbound/ <── Outbound Adapters (Repositories JPA/PostgreSQL, Redis, Firebase)

**Matriz 4.1: Lista de Chequeo de Auditoría Arquitectónica en GitHub**

|  |  |  |  |
| --- | --- | --- | --- |
| **Componente Hexagonal** | **Ruta en Repositorio GitHub** | **Estado (Conforme / No Conforme)** | **Evidencia de Desacoplamiento / Hallazgo** |
| **Núcleo de Dominio** | /src/domain/model/ | **Conforme** | Cero importaciones de Spring Boot, Hibernate u ORMs. |
| **Puertos de Entrada** | /src/ports/inbound/ | **Conforme** | Interfaces puras que definen los casos de uso. |
| **Puertos de Salida** | /src/ports/outbound/ | **Conforme** | Interfaces de persistencia e integración sin implementación. |
| **Adaptadores Entrada** | /src/adapters/inbound/rest/ | **Conforme** | Controladores REST inyectan puertos de entrada. |
| **Adaptadores Salida** | /src/adapters/outbound/persistence/ | **Conforme** | Implementación concreta de repositorios usando JPA/PostgreSQL. |

**ACTIVIDAD 5: Evaluación de Pruebas de Software de los Incrementos 1 y 2 con Evidencias Visuales**

Documente la ejecución de casos de prueba para cada Requerimiento Funcional (RF) de ambos incrementos, incluyendo **capturas de pantalla del software en ejecución**:

**5.1 Ficha Modelo de Evidencia de Prueba Funcional por Requerimiento**

========================================================================================================

FICHA DE PRUEBA FUNCIONAL CON EVIDENCIA FOTOGRÁFICA (INCREMENTO 1 Y 2)

========================================================================================================

PROYECTO: [Nombre de la Solución Tecnológica]

INCREMENTO: [Incremento 1 (PMV) / Incremento 2]

CÓDIGO REQUERIMIENTO: RF-01 / HU-01

NOMBRE DEL REQUERIMIENTO: [Ej. Registro de Solicitud en Tiempo Real]

CRITERIO DE ACEPTACIÓN (\*Given-When-Then\*):

- Dado que el usuario completa el formulario con datos válidos,

- Cuando presiona el botón "Enviar",

- Entonces el sistema almacena el registro y emite una confirmación en menos de 2 segundos.

--------------------------------------------------------------------------------------------------------

ESPECIFICACIÓN DEL CASO DE PRUEBA:

- ID Caso de Prueba: CP-RF01-01

- Tipo de Prueba: Prueba Funcional de Interfaz / Aceptación

- Resultado Esperado: Registro exitoso en base de datos y notificación visual en pantalla.

--------------------------------------------------------------------------------------------------------

EVIDENCIAS FOTOGRÁFICAS (CAPTURAS DE PANTALLA DEL SOFTWARE):

[ CAPTURA DE PANTALLA 1: DATOS DE ENTRADA ]

Descripción: Formulario con los datos de prueba cargados antes de la ejecución.

Archivo de Imagen: `/evidencias/inc1/RF01\_paso1\_entrada.png`

[ CAPTURA DE PANTALLA 2: CONFIRMACIÓN Y RESULTADO ]

Descripción: Pantalla del software mostrando el mensaje de éxito e ID de transacción.

Archivo de Imagen: `/evidencias/inc1/RF01\_paso2\_resultado.png`

--------------------------------------------------------------------------------------------------------

EVALUACIÓN: [ APROBADO ] | FECHA: [DD/MM/AAAA] | EVALUADOR: [Nombre del QA Lead]

========================================================================================================

**Matriz 5.2: Trazabilidad de Pruebas Funcionales e Incrementos**

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **Código RF** | **Descripción del Requerimiento** | **Incremento** | **ID Caso Prueba** | **Archivo de Captura de Pantalla** | **Estado** |
| **RF-01** | *Registro y autenticación de usuario.* | Inc. 1 (PMV) | CP-RF01-01 | RF01\_inc1\_registro\_ok.png | **Aprobado** |
| **RF-02** | *Procesamiento y alertas en tiempo real.* | Inc. 1 (PMV) | CP-RF02-01 | RF02\_inc1\_alerta\_pantalla.png | **Aprobado** |
| **RF-03** | *Consulta de historial y monitoreo.* | Inc. 2 | CP-RF03-01 | RF03\_inc2\_historial\_tabla.png | **Aprobado** |
| **RF-04** | *Exportación de reportes de calidad.* | Inc. 2 | CP-RF04-01 | RF04\_inc2\_pdf\_descargado.png | **Aprobado** |

**ACTIVIDAD 6: Evaluación del Proceso y Producto con Entrega de Valor al Usuario Final**

Demuestre cómo las funcionalidades probadas resuelven las brechas del proceso AS-IS y generan valor directo para la organización:

**Matriz 6.1: Trazabilidad Proceso–Producto–Valor al Usuario**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Problema Organizacional (AS-IS)** | **Brecha Resuelta** | **Incremento / Funcionalidad Entregada** | **Indicador de Proceso / Producto** | **Valor Organizacional Generado** |
| *Ej. Registro manual en papel con demoras de 8 horas.* | Falta de información en tiempo real. | **Inc. 1:** App móvil para registro y transmisión de eventos. | *Tiempo de envío:* Reducido de 8 horas a 3 segundos. | Toma de decisiones preventivas e inmediatas. |
| *Ej. Pérdida de productos por fallas no detectadas.* | Ausencia de monitoreo preventivo. | **Inc. 2:** Motor de reglas y alertas automáticas. | *Disponibilidad:* 99.5% / *Precisión:* 98%. | Reducción de pérdidas económicas de 22% a 3%. |

**ACTIVIDAD 7: Diagnóstico Comparativo y Plan de Mejora Continua (PDCA)**

Compare los resultados de las métricas GQM entre el Incremento 1 y el Incremento 2, identificando las mejoras logradas en el proceso de software:

**Matriz 7.1: Comparativa GQM y Evolución del Proceso (Inc. 1 vs. Inc. 2)**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Métrica GQM Evaluada** | **Incremento 1 (PMV) Real** | **Incremento 2 Real** | **Variación (%)** | **Causa Raíz / Acción de Mejora Aplicada** |
| **Contaminación del Dominio (M1.1)** | 12% importaciones | 0% importaciones | **-100%** | Refactorización de entidades aislando frameworks en la carpeta adaptadores. |
| **Tasa de Defectos Funcionales (M2.2)** | 1.2 Def/RF | 0.1 Def/RF | **-91.6%** | Incorporación de *Code Reviews* obligatorios y checklists antes de fusionar ramas. |
| **Cobertura de Brechas (M3.1)** | 60% resuelto | 95% resuelto | **+58.3%** | Priorización de historias de usuario con mayor impacto en el usuario final. |

**III. ESTRUCTURA DEL ENTREGABLE EN EL AULA VIRTUAL**

========================================================================================================

INFORME TÉCNICO: EVALUACIÓN GQM DE ARQUITECTURA, PRUEBAS Y VALOR AL USUARIO

========================================================================================================

1. CARÁTULA E INTEGRANTES DEL EQUIPO (Noveno Ciclo)

2. RESUMEN EJECUTIVO Y OBJETIVOS DE EVALUACIÓN GQM

3. MATRIZ DE OBJETIVOS, PREGUNTAS Y MÉTRICAS GQM (Actividades 1, 2 y 3)

4. AUDITORÍA DE ARQUITECTURA HEXAGONAL EN GITHUB (Actividad 4)

- Estructura de carpetas y reporte de desacoplamiento del dominio.

5. FICHAS DE PRUEBAS FUNCIONALES CON CAPTURAS DE PANTALLA (Actividad 5)

- Registro de pruebas e imágenes de evidencia para cada RF de los Incrementos 1 y 2.

6. EVALUACIÓN DE ENTREGA DE VALOR AL USUARIO FINAL (Actividad 6)

7. COMPARATIVA GQM Y PLAN DE MEJORA CONTINUA (Actividad 7 - Inc. 1 vs. Inc. 2)

8. ANEXOS:

- Carpeta de capturas `/evidencias\_capturas/` organizadas por RF.

- Enlace al Repositorio GitHub con las etiquetas `v1.0-PMV` y `v2.0-Inc2`.

**IV. RÚBRICA DE EVALUACIÓN SUMATIVA (20 PUNTOS)**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Criterio de Evaluación** | **Excelente (4 pts)** | **Bueno (3 pts)** | **Básico (2 pts)** | **Inicial (1 pt)** |
| **Formulación del Modelo GQM (Act. 1, 2 y 3)** | Formula los Objetivos GQM con los 5 elementos de Basili, derivando preguntas y métricas cuantitativas para arquitectura, pruebas y valor. | Formula los Objetivos GQM y sus métricas asociadas de forma adecuada. | Formula Objetivos GQM incompletos o sin diferenciar adecuadamente producto y proceso. | Redacta objetivos ambiguos que confunden metas de prueba con deseos de gestión. |
| **Auditoría de Arquitectura Hexagonal en GitHub (Act. 4)** | Estructura y demuestra el aislamiento del dominio en GitHub, verificando carpetas de Puertos y Adaptadores sin contaminación. | Organiza las carpetas en GitHub según el patrón hexagonal con pocas inconsistencias. | Presenta una estructura de carpetas incompleta o con acoplamiento entre dominio y frameworks. | No demuestra la aplicación de Arquitectura Hexagonal en el repositorio GitHub. |
| **Pruebas Funcionales con Capturas por RF (Act. 5)** | Presenta fichas de prueba y capturas de pantalla claras del software en ejecución para **TODOS** los RFs de los Incrementos 1 y 2. | Presenta pruebas y capturas de pantalla para la mayoría de los Requerimientos Funcionales. | Presenta capturas de pantalla parciales, borrosas o que no permiten verificar la ejecución. | No adjunta capturas de pantalla del software o faltan la mayoría de los RFs. |
| **Evaluación de Entrega de Valor al Usuario (Act. 6)** | Demuestra con trazabilidad e indicadores cómo el software resuelve las brechas del AS-IS y genera valor al usuario. | Relaciona las funcionalidades entregadas con las brechas organizacionales y el valor generado. | Muestra una relación parcial entre el software desarrollado y el valor esperado por el usuario. | No demuestra cómo el producto o proceso genera valor para la organización o usuario. |
| **Comparativa GQM y Mejora Continua (Act. 7)** | Mide y compara los resultados de ambos incrementos, demostrando evoluciones cuantitativas y acciones de mejora. | Compara adecuadamente los resultados de ambos incrementos e identifica variaciones. | Presenta datos aislados de los incrementos sin análisis comparativo de evolución. | No presenta mediciones comparativas entre incrementos ni plan de mejora. |

**Puntaje Máximo:** 20 puntos