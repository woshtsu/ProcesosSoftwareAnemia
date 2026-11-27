# Anexo A4. Vinculación con el VIII Congreso Internacional de Ingeniería y Arquitectura

**Proyecto:** Anemia Junín (Procesos de Software, Universidad Continental, 2026-20)
**Fecha:** 26/11/2026
**Repositorio:** <https://github.com/woshtsu/ProcesosSoftwareAnemia>

## 1. Introducción

Se analizaron dos ponencias del VIII Congreso Internacional de Ingeniería y Arquitectura de la Universidad Continental: «Implementación de BIM en proyectos de infraestructura pública», del Ing. Ángel Vladimir Paredes Postales (Autoridad Nacional de Infraestructura, ANIN), y la de tecnología espacial del Ing. Alejandro Manuel Martínez (Universidad de Buenos Aires, UBA). Este anexo reproduce la sección 3.4.5 y el Anexo E del Informe de la Unidad IV, con las tablas y la figura renumeradas.

## 2. Aporte del congreso a la gestión de configuración

El equipo participó en el VIII Congreso Internacional de Ingeniería y Arquitectura (constancia en la Figura 1). La ponencia más relacionada con esta unidad fue «Implementación de BIM en proyectos de infraestructura pública», del Ing. Ángel Vladimir Paredes Postales, de la Autoridad Nacional de Infraestructura (ANIN). BIM es, en esencia, gestión de configuración aplicada a la información de obras. La consigna del curso sugería para la Unidad IV la ponencia del Ing. Alejandro Manuel Martínez (UBA), sobre tecnología espacial; se incluye en la matriz, pero la de BIM se corresponde de forma más directa con la gestión de configuración del proyecto (Tabla 1).

| Práctica presentada en la ponencia | Práctica equivalente en el proyecto | Evidencia |
| --- | --- | --- |
| Entorno de Datos Comunes (CDE) como «única fuente de verdad», para que nadie trabaje con una versión desfasada de un plano | Repositorio Git en GitHub con `main` como línea base y `develop` como integración; las 17 ramas ya integradas se eliminaron | 3.4.2 |
| Flujos de revisión formal antes de la validación contractual | Pull requests con plantilla de Definición de Terminado y aprobación obligatoria de un par (ruleset `ownermerge`) | 3.4.1 |
| Estándares de intercambio (ISO 19650) adaptados a la terminología del equipo | Plantillas de RFC y de PR, convención de commits y ramas en `CONTRIBUTING.md` | 3.4.1 |
| Gestión de incidencias con metadatos que alimentan tableros | RFC en Issues con etiquetas de evaluación (`pendiente-evaluacion`, `aprobado`, `implementado`) | 3.4.1 |
| Madurez «Definido → Integrado → Optimizado»; «lo que no se mide no se mejora» | Indicadores del proceso SCM medidos antes y después, ciclo PDCA y niveles de capacidad CMMI | 3.4.4 y 3.3.3 |
| Orden «procesos, personas y tecnología» antes de comprar herramientas | Se definió primero el flujo de cambio (RFC → PR → CI → release) y después se configuró la suite de GitHub | 3.4.1 a 3.4.3 |

**Tabla 1.** Correspondencia entre las prácticas de la ponencia BIM (ANIN) y la gestión de configuración del proyecto.

| Unidad del sílabo | Ponencia | Vinculación con el proyecto |
| --- | --- | --- |
| I. Fundamentos de procesos de software | BIM en ANIN (Paredes) | La ponencia empieza por un diagnóstico de madurez antes de implantar tecnología. Es el mismo principio del AS-IS/TO-BE del proyecto: rediseñar el proceso antes de automatizarlo. |
| II. Implementación del proceso de software | Tecnología espacial (Martínez) | Un sistema espacial se divide en segmentos con interfaces definidas (lanzador, vuelo y tierra) y se opera a distancia. La arquitectura hexagonal aplica la misma separación: dominio, puertos y adaptadores, con pruebas independientes por capa. |
| III. Evolución de los procesos y actividades | BIM en ANIN (Paredes) | Los niveles de madurez de la gestión de la información y la medición por indicadores corresponden a la evaluación con GQM y CMMI-DEV y al plan de mejora del proyecto. |
| IV. Gestión de configuración de software | BIM en ANIN (Paredes); tecnología espacial (Martínez) | El CDE y los flujos de revisión equivalen al repositorio con ramas protegidas y PR revisadas. Las constelaciones que reponen satélites cada cinco años ilustran la entrega continua de versiones sin interrumpir el servicio, como las releases con SemVer y CI/CD. |

**Tabla 2.** Matriz de vinculación de las ponencias con las unidades del sílabo (consigna S14).


## 3. Participación del equipo

El equipo siguió las ponencias del congreso. Su vinculación con las unidades del sílabo y con la gestión de configuración del proyecto se resume en las Tablas 1 y 2.

![Participación de un integrante del equipo en la transmisión del VIII Congreso Internacional.](../img/congreso_participacion.jpg)

**Figura 1.** Participación de un integrante del equipo en la transmisión del VIII Congreso Internacional de Ingeniería y Arquitectura.
