**Guía de trabajo semana 2 – 2026-20**

**Guía de trabajo – Eje 2: Modelo de procesos de software**

**Curso:** Procesos de Software
**Unidad:** Diseño de procesos de software con entrega de valor
**Eje temático:** 2. Modelo de procesos de software
**Proyecto guía:** Plataforma de Seguridad Vial Inteligente para la Carretera Central

**1. Objetivo de la guía**

Al finalizar la actividad, el estudiante será capaz de:

**Analizar las características de un proyecto de software y seleccionar, comparar y justificar un modelo de proceso de software que permita desarrollar la solución de manera coherente con las necesidades del proceso organizacional, los requerimientos, los riesgos, la incertidumbre y la necesidad de entrega de valor.**

**Productos esperados**

* Identificación de características del proyecto.
* Identificación de factores que condicionan la selección del modelo de proceso.
* Comparación de modelos de procesos de software.
* Selección del modelo de proceso más adecuado.
* Justificación técnica de la selección.
* Representación del modelo de proceso seleccionado.
* Relación entre modelo de proceso, entregas de valor y características del proyecto.
* Identificación de riesgos y mecanismos de control del proceso.

**2. Conexión con la Guía de Trabajo 1**

En la Guía de Trabajo 1 se analizó primero el **proceso de la organización**, evitando comenzar directamente por la tecnología.

La lógica desarrollada fue:

**Problema organizacional**
↓
**Actores y necesidades**
↓
**Proceso AS-IS**
↓
**Brechas**
↓
**Proceso TO-BE**
↓
**Intervención del software**
↓
**Valor organizacional**
↓
**Indicadores**

En esta guía se da el siguiente paso:

**Proceso TO-BE**
↓
**Características de la solución de software**
↓
**Características del proyecto**
↓
**Factores de decisión**
↓
**Comparación de modelos**
↓
**Selección del modelo de proceso**
↓
**Aplicación del modelo al proyecto**
↓
**Entregas de valor**

**Regla fundamental**

**No se debe seleccionar Scrum, Kanban, DevOps, MLOps, DataOps, Lean u otro modelo solamente porque sea conocido o esté de moda.**

La selección debe responder a las características concretas del proyecto.

La argumentación esperada es:

**Necesidad organizacional → características de la solución → características del proyecto → factores de decisión → modelo de proceso → forma de trabajo → entregas de valor → resultados esperados.**

**3. Conceptos que se aplicarán**

En esta actividad se trabajarán los siguientes conceptos:

* Modelo de proceso de software.
* Proceso tradicional.
* Proceso incremental.
* Proceso evolutivo.
* Proceso iterativo.
* Prototipado.
* Desarrollo ágil.
* Scrum.
* Kanban.
* DevOps.
* MLOps.
* DataOps.
* Lean.
* Gestión de riesgos.
* Entrega incremental de valor.
* Adaptabilidad.
* Retroalimentación.
* Integración y entrega continua.

**Pregunta central**

**¿Qué modelo de proceso permite desarrollar este proyecto con menor riesgo y mayor capacidad de entrega de valor, considerando sus características reales?**

**4. Ejemplo aplicado: Plataforma de Seguridad Vial**

**4.1 Características del proyecto**

A partir del análisis realizado en la Guía 1, el proyecto de seguridad vial presenta características como:

| **Característica** | **Situación del proyecto** |
| --- | --- |
| Problema | Prevención del riesgo vial |
| Usuarios | Conductores, centro de monitoreo, policía, servicios de emergencia y autoridades |
| Información | Datos provenientes de diferentes fuentes |
| Tiempo de respuesta | Necesidad de respuesta oportuna |
| Incertidumbre | Condiciones climáticas, tránsito y comportamiento vial |
| Integración | Necesidad de integrar información institucional |
| Inteligencia artificial | Predicción del riesgo |
| Conectividad | Cobertura móvil variable |
| Evolución | El sistema puede requerir ajustes según resultados |
| Valor | Prevención y reducción del riesgo vial |

Por tanto, el proyecto presenta **incertidumbre, integración, necesidad de retroalimentación, componentes de datos e inteligencia artificial y necesidad de entregar funcionalidad progresivamente**.

**5. Actividad 1 – Identificar las características del proyecto**

Cada equipo debe analizar su proyecto seleccionado en la Guía 1.

Complete la siguiente matriz:

| **Factor** | **Situación del proyecto** | **Nivel: Bajo/Medio/Alto** | **Evidencia** |
| --- | --- | --- | --- |
| Incertidumbre de requisitos |  |  |  |
| Complejidad técnica |  |  |  |
| Cambios esperados |  |  |  |
| Riesgo tecnológico |  |  |  |
| Necesidad de retroalimentación |  |  |  |
| Frecuencia de entrega |  |  |  |
| Necesidad de integración |  |  |  |
| Participación del usuario |  |  |  |
| Necesidad de automatización |  |  |  |
| Dependencia de datos |  |  |  |
| Necesidad de experimentación |  |  |  |
| Criticidad del sistema |  |  |  |

**Pregunta orientadora**

**¿Cuáles son las tres características del proyecto que más deberían influir en la selección del modelo de proceso?**

**6. Actividad 2 – Identificar los factores para seleccionar un modelo**

No todos los proyectos requieren el mismo proceso de desarrollo.

Cada equipo debe identificar los factores que deben considerarse antes de seleccionar el modelo.

**Ejemplo**

Para la Plataforma de Seguridad Vial:

| **Factor** | **Importancia** | **Justificación** |
| --- | --- | --- |
| Cambios de requisitos | Alta | El sistema puede evolucionar con el conocimiento obtenido |
| Retroalimentación | Alta | Se requiere validar alertas y funcionalidades |
| Riesgo | Alta | Una predicción incorrecta puede afectar la toma de decisiones |
| Integración | Alta | Existen diferentes fuentes y actores |
| Entrega incremental | Alta | Es conveniente validar funcionalidades progresivamente |
| Automatización | Alta | Se requiere integrar pruebas, construcción y despliegue |
| Datos | Alta | El sistema depende de información para generar predicciones |

**Actividad para otro proyecto**

Identifique **mínimo seis factores** que condicionen la selección del modelo.

| **Factor** | **Importancia** | **¿Por qué afecta la selección?** |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

**7. Actividad 3 – Comparar modelos de procesos**

El equipo debe comparar diferentes alternativas antes de seleccionar una.

Se recomienda analizar como mínimo:

* Cascada.
* Incremental.
* Espiral.
* Scrum.
* Kanban.
* DevOps.
* MLOps/DataOps, cuando el proyecto utilice componentes de datos o aprendizaje automático.

**Matriz de comparación**

| **Modelo** | **Adaptabilidad** | **Gestión de riesgos** | **Entrega incremental** | **Retroalimentación** | **Automatización** | **Adecuación al proyecto** |
| --- | --- | --- | --- | --- | --- | --- |
| Cascada |  |  |  |  |  |  |
| Incremental |  |  |  |  |  |  |
| Espiral |  |  |  |  |  |  |
| Scrum |  |  |  |  |  |  |
| Kanban |  |  |  |  |  |  |
| DevOps |  |  |  |  |  |  |
| MLOps/DataOps |  |  |  |  |  |  |

Utilice una escala:

**1 = Muy bajo**
**2 = Bajo**
**3 = Medio**
**4 = Alto**
**5 = Muy alto**

**Pregunta orientadora**

**¿El modelo que obtenga mayor puntuación es necesariamente el modelo que debe seleccionarse? ¿Por qué?**

La respuesta debe considerar la **naturaleza del proyecto y la evidencia obtenida**, no únicamente el resultado numérico.

**8. Actividad 4 – Seleccionar el modelo de proceso**

Seleccione el modelo o enfoque de proceso que considere más adecuado para su proyecto.

**Ejemplo**

Para la Plataforma de Seguridad Vial Inteligente podría considerarse una combinación de enfoques:

**Desarrollo iterativo/incremental + Scrum + DevOps + MLOps/DataOps**

La selección debe justificarse según las necesidades del proyecto.

**Matriz de decisión**

| **Criterio** | **Peso** | **Alternativa 1** | **Alternativa 2** | **Alternativa 3** |
| --- | --- | --- | --- | --- |
| Adaptabilidad |  |  |  |  |
| Gestión de riesgos |  |  |  |  |
| Entrega incremental |  |  |  |  |
| Retroalimentación |  |  |  |  |
| Integración |  |  |  |  |
| Automatización |  |  |  |  |
| Gestión de datos/IA |  |  |  |  |
| Participación del usuario |  |  |  |  |
| **Puntaje total** |  |  |  |  |

**Decisión**

**Modelo de proceso seleccionado:**

**Justificación**

La justificación debe responder:

1. ¿Qué característica del proyecto hace necesario este modelo?
2. ¿Qué problema del proceso de desarrollo ayuda a resolver?
3. ¿Cómo permite entregar valor progresivamente?
4. ¿Cómo permite gestionar cambios?
5. ¿Cómo permite controlar riesgos?
6. ¿Qué limitaciones presenta?
7. ¿Por qué las otras alternativas fueron descartadas?

**9. Actividad 5 – Representar el modelo de proceso**

El equipo debe representar gráficamente cómo funcionará el modelo seleccionado en su proyecto.

El diagrama debe mostrar:

1. Entrada/requerimientos.
2. Planificación.
3. Desarrollo.
4. Integración.
5. Pruebas.
6. Retroalimentación.
7. Entrega.
8. Medición.
9. Mejora.
10. Repetición o siguiente incremento.

**Ejemplo conceptual**

**Necesidad del usuario**
↓
**Priorización**
↓
**Incremento 1**
↓
**Desarrollo**
↓
**Pruebas**
↓
**Integración**
↓
**Entrega**
↓
**Retroalimentación**
↓
**Medición del resultado**
↓
**Incremento 2**
↓
**Mejora continua**

El diagrama debe adaptarse al modelo realmente seleccionado.

**Importante**

No se debe copiar un diagrama de Scrum, Kanban o DevOps de Internet.

El diagrama debe representar **cómo se aplicará el modelo al proyecto específico del equipo**.

**10. Actividad 6 – Relacionar el modelo de proceso con la entrega de valor**

La finalidad del modelo de proceso no es solamente organizar actividades de desarrollo.

Debe contribuir a generar valor.

La relación esperada es:

**Necesidad**
↓
**Incremento de software**
↓
**Funcionalidad operativa**
↓
**Resultado para el usuario**
↓
**Valor**

**Ejemplo: Seguridad Vial**

| **Incremento** | **Funcionalidad** | **Resultado** | **Valor** |
| --- | --- | --- | --- |
| Incremento 1 | Registro de condiciones viales | Información centralizada | Mejor información |
| Incremento 2 | Monitoreo | Identificación de zonas críticas | Mayor capacidad de vigilancia |
| Incremento 3 | Predicción | Identificación anticipada del riesgo | Prevención |
| Incremento 4 | Alertas | Comunicación oportuna | Mejor respuesta |
| Incremento 5 | Integración institucional | Información compartida | Coordinación |

**Actividad para otro proyecto**

Construya su propia matriz:

| **Incremento** | **Funcionalidad** | **Resultado esperado** | **Valor generado** | **Indicador** |
| --- | --- | --- | --- | --- |
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**11. Actividad 7 – Identificar riesgos del modelo seleccionado**

La selección de un modelo también debe considerar sus riesgos.

**Ejemplo**

| **Riesgo** | **Causa** | **Impacto** | **Respuesta** |
| --- | --- | --- | --- |
| Cambios frecuentes | Incertidumbre | Retrabajo | Desarrollo iterativo |
| Datos insuficientes | Baja disponibilidad | Predicciones deficientes | Validación de datos |
| Fallas de integración | Sistemas heterogéneos | Interrupción del servicio | Pruebas de integración |
| Baja participación del usuario | Comunicación insuficiente | Producto no adecuado | Retroalimentación frecuente |
| Despliegue defectuoso | Falta de automatización | Interrupción | Integración/entrega automatizada |

**Actividad para otro proyecto**

Identifique **mínimo cinco riesgos relacionados con el modelo de proceso seleccionado**.

| **Riesgo** | **Causa** | **Impacto** | **Mecanismo de control** |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

**12. Actividad 8 – Modelo de proceso y herramientas**

El equipo debe identificar qué herramientas podrían soportar el modelo seleccionado.

**Ejemplo**

| **Necesidad** | **Herramienta posible** | **Propósito** |
| --- | --- | --- |
| Gestión del trabajo | Trello/GitHub Projects | Gestionar tareas |
| Control de versiones | Git/GitHub | Gestionar código |
| Integración | GitHub Actions | Automatizar integración |
| Calidad | SonarQube/SonarCloud | Analizar calidad |
| Pruebas | Framework de pruebas | Validar software |
| Datos/IA | Google Colab | Experimentación |
| Documentación | Wiki/Markdown | Gestionar conocimiento |

**Actividad**

Complete:

| **Necesidad del proceso** | **Herramienta** | **¿Qué actividad soporta?** | **Evidencia** |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

**Pregunta orientadora**

**¿La herramienta determina el modelo de proceso o el modelo de proceso determina qué herramientas necesita el equipo? Justifique.**

**13. Actividad 9 – Construir la trazabilidad del proceso**

El equipo debe demostrar que la selección del modelo tiene relación con el problema y el valor esperado.

Construya la siguiente cadena:

**Problema organizacional**
↓
**Brecha**
↓
**Necesidad de software**
↓
**Característica del proyecto**
↓
**Factor de selección**
↓
**Modelo de proceso seleccionado**
↓
**Forma de trabajo**
↓
**Incremento de software**
↓
**Resultado**
↓
**Valor**

**Matriz de trazabilidad**

| **Elemento** | **Evidencia del proyecto** |
| --- | --- |
| Problema |  |
| Brecha |  |
| Necesidad de software |  |
| Característica del proyecto |  |
| Factor de selección |  |
| Modelo seleccionado |  |
| Forma de trabajo |  |
| Incremento |  |
| Resultado |  |
| Valor |  |

Esta actividad es fundamental para demostrar que la selección del modelo **no fue arbitraria**.

**14. Actividad 10 – Caso de decisión**

Analice la siguiente situación:

Un equipo desarrolla una plataforma de salud digital. Los usuarios todavía no tienen completamente definidos todos los requerimientos. El sistema debe integrarse con otros servicios, se espera retroalimentación frecuente de los usuarios y se requiere entregar funcionalidades progresivamente. Además, algunas funcionalidades utilizan modelos de inteligencia artificial que deberán ser entrenados y evaluados con nuevos datos.

**Preguntas**

1. ¿Qué características del proyecto condicionan la selección del proceso?
2. ¿Qué modelo tradicional podría presentar dificultades?
3. ¿Qué ventajas ofrecería un enfoque iterativo/incremental?
4. ¿Qué aportaría Scrum?
5. ¿Qué aportaría DevOps?
6. Si existe aprendizaje automático, ¿qué problemas adicionales deben considerarse?
7. ¿Sería suficiente utilizar Scrum para todo el proyecto? Justifique.
8. ¿Qué combinación de enfoques podría resultar conveniente?
9. ¿Cómo se entregaría valor en los primeros incrementos?
10. ¿Qué indicadores permitirían verificar que el proceso está funcionando?

**15. Entregable de la actividad**

Cada equipo debe presentar un documento breve con:

┌─────────────────────────────────────────────┐

│ 1. CARACTERÍSTICAS DEL PROYECTO │

├─────────────────────────────────────────────┤

│ 2. FACTORES DE SELECCIÓN │

├─────────────────────────────────────────────┤

│ 3. COMPARACIÓN DE MODELOS │

├─────────────────────────────────────────────┤

│ 4. MODELO SELECCIONADO │

├─────────────────────────────────────────────┤

│ 5. JUSTIFICACIÓN │

├─────────────────────────────────────────────┤

│ 6. REPRESENTACIÓN DEL PROCESO │

├─────────────────────────────────────────────┤

│ 7. ENTREGAS INCREMENTALES DE VALOR │

├─────────────────────────────────────────────┤

│ 8. RIESGOS Y CONTROLES │

├─────────────────────────────────────────────┤

│ 9. HERRAMIENTAS DE SOPORTE │

├─────────────────────────────────────────────┤

│ 10. TRAZABILIDAD DE LA DECISIÓN │

└─────────────────────────────────────────────┘

**16. Preguntas de análisis**

Al finalizar, el equipo debe responder brevemente:

1. ¿Qué características de su proyecto fueron determinantes para seleccionar el modelo de proceso?
2. ¿Por qué el modelo seleccionado es más adecuado que una alternativa tradicional?
3. ¿Qué riesgos del proyecto son tratados por el modelo seleccionado?
4. ¿Cómo se incorporará la retroalimentación de los usuarios?
5. ¿Cómo se realizará la entrega incremental de valor?
6. ¿Qué actividades del proceso serán automatizadas?
7. ¿Qué herramientas soportarán el proceso?
8. ¿Qué limitaciones presenta el modelo seleccionado?
9. ¿En qué situación cambiarían de modelo o complementarían el modelo seleccionado?
10. ¿Cómo demostrarán mediante indicadores que el modelo de proceso está contribuyendo al éxito del proyecto?

**17. Reto de aplicación**

Cada equipo debe presentar una **defensa de cinco minutos** de su decisión.

La exposición debe responder únicamente a cuatro preguntas:

**1. ¿Qué problema tenemos?**

Presentar brevemente el problema y la brecha identificada en la Guía 1.

**2. ¿Qué características tiene nuestro proyecto?**

Mostrar las características que condicionan el desarrollo.

**3. ¿Por qué elegimos este modelo?**

Presentar evidencia de comparación y justificar la decisión.

**4. ¿Cómo generará valor?**

Mostrar cómo el modelo permitirá entregar incrementos de software y resultados para los usuarios.

**18. Criterio clave de evaluación**

El estudiante **no debe justificar** la selección del modelo mediante afirmaciones como:

“Elegimos Scrum porque es ágil.”

o:

“Elegimos DevOps porque permite automatizar.”

La argumentación esperada debe ser:

**Característica del proyecto → problema/riesgo → necesidad del proceso → característica del modelo → aplicación al proyecto → resultado → valor.**

Por ejemplo:

“Debido a que los requerimientos presentan incertidumbre y se requiere retroalimentación frecuente de los usuarios, se necesita un proceso iterativo que permita entregar incrementos funcionales y adaptar las prioridades. Por ello, se selecciona Scrum como marco de trabajo para la gestión iterativa, complementado con prácticas DevOps para automatizar integración, pruebas y despliegue.”

**19. Rúbrica de evaluación – 20 puntos**

| **Criterio** | **Excelente 4** | **Bueno 3** | **Básico 2** | **Inicial 1** |
| --- | --- | --- | --- | --- |
| **Análisis de características del proyecto** | Identifica y sustenta claramente las características determinantes | Identifica las principales características | Identifica características sin suficiente sustento | Presenta características genéricas |
| **Comparación de modelos** | Compara alternativas con criterios pertinentes y evidencia | Compara varias alternativas adecuadamente | Comparación limitada | No realiza comparación significativa |
| **Selección y justificación** | La selección está plenamente sustentada y relacionada con el proyecto | La selección está adecuadamente sustentada | Presenta justificación parcial | La selección es arbitraria |
| **Aplicación del modelo al proyecto** | Representa claramente cómo se aplicará el modelo y cómo generará valor | Representa adecuadamente su aplicación | La aplicación presenta vacíos | No demuestra aplicación concreta |
| **Riesgos, valor y trazabilidad** | Relaciona riesgos, proceso, entregas, resultados e indicadores con excelente trazabilidad | Presenta relaciones adecuadas | Presenta relaciones parciales | No evidencia relación |

**Puntaje máximo: 20 puntos**

**20. Resultado esperado de aprendizaje**

Al terminar la guía, el estudiante debe ser capaz de explicar:

**“No seleccionamos un modelo de proceso porque sea el más conocido, sino porque las características de nuestro proyecto requieren determinadas capacidades del proceso para controlar riesgos, gestionar cambios, entregar incrementos y generar valor.”**

La Guía 2 deja preparada la transición hacia las siguientes actividades del curso, donde el modelo seleccionado podrá profundizarse mediante prácticas específicas de **Agile, Scrum, Kanban, DevOps, MLOps, DataOps, Lean u otros enfoques**, de acuerdo con las necesidades del proyecto.