**Curso: Procesos de Software — 2026-20**

Eje 2: Modelo de procesos de software

**Entregable Semana 2 — Selección y justificación del modelo de proceso**

Proyecto: Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín

## **Equipo de proyecto**

| Integrante | Rol en el proyecto |
| :---- | :---- |
| Porras Veli Ricardo | Ingeniero de Proceso |
| Auqui Huincho Tania | Ingeniero de Desarrollo y Prototipado |
| Huamani Rodriguez Jean Piero | Ingeniero de Calidad y Mejora del Proceso |

**Nota de versión (v2).** Se conserva el contenido de la versión previa —caracterización del proyecto, comparación de modelos, matriz ponderada, incrementos, riesgos, herramientas y trazabilidad— y se corrigen o completan los puntos que la guía exige y que faltaban: se aclara la distinción entre modelo de proceso, marco de trabajo y prácticas; se explicita el puente entre la comparación de modelos individuales y la decisión sobre combinaciones; se reemplaza el código sin renderizar por el diagrama del proceso; y se añaden la Actividad 10 (caso de decisión) y el reto de aplicación (defensa de cinco minutos). **Los cambios están resaltados en amarillo.**

# **0\. Punto de partida: el TO-BE de la Semana 1**

La Semana 1 concluyó en un proceso TO-BE donde el software interviene en seis puntos concretos: registro nominal validado, agenda automática según la NTS 134, funcionamiento sin conexión, notificaciones a la familia por WhatsApp, priorización mediante un modelo predictivo y tablero de indicadores para gestión territorial. Esos seis puntos son la entrada de esta guía: de ellos se derivan las características del proyecto y, a partir de ellas, el modelo de proceso.

# **1\. Características del proyecto**

| Factor | Nivel | Situación del proyecto y evidencia |
| :---- | :---- | :---- |
| Incertidumbre de requisitos | Alto | Los requisitos clínicos están acotados por la NTS 134, pero el componente de IA, la interacción por WhatsApp y el modo offline no lo están: el algoritmo, las variables predictivas y los umbrales de riesgo solo pueden definirse experimentando con datos reales. |
| Complejidad técnica | Alto | Modelo predictivo, API de WhatsApp, sincronización offline con resolución de conflictos e interfaces diferenciadas por rol (posta, agente comunitario, microred). |
| Cambios esperados | Alto | La entrevista mostró que el proceso se ajusta según resultados; el modelo requerirá refinamiento sucesivo tras cada validación con el personal. |
| Riesgo tecnológico | Alto | Cobertura móvil intermitente en las zonas rurales de Junín, rendimiento incierto del modelo y dependencia de una API externa sujeta a cambios. |
| Necesidad de retroalimentación | Alto | El personal de salud debe validar que los casos marcados como de alto riesgo coincidan con su criterio clínico; sin esa validación el sistema no se adopta. |
| Frecuencia de entrega | Alto | Es necesario validar el registro nominal antes de añadir la agenda, y la agenda antes de añadir el modelo predictivo. |
| Necesidad de integración | Alto | HIS existente, API de WhatsApp Business, artefacto del modelo y módulo offline. |
| Participación del usuario | Alto | Personal de salud, agentes comunitarios y familias intervienen directamente en el proceso. |
| Necesidad de automatización | Alto | Despliegue hacia postas dispersas, sincronización automática y reentrenamiento periódico del modelo. |
| Dependencia de datos | Alto | El modelo se entrena con datos históricos del HIS (hemoglobina, edad, altitud, adherencia) de calidad variable. |
| Necesidad de experimentación | Alto | Selección de algoritmo (Random Forest frente a Gradient Boosting) e ingeniería de variables. |
| Criticidad del sistema | Alto | El sistema apoya decisiones sobre salud infantil; un fallo retrasa la atención de un niño con anemia. |

**Las tres características determinantes.** (1) La incertidumbre y la necesidad de experimentación del componente de IA, porque impiden definir el alcance por adelantado. (2) El riesgo tecnológico del entorno rural, porque la conectividad intermitente condiciona la arquitectura y obliga a probar la sincronización en cada entrega. (3) La necesidad de retroalimentación del personal de salud, porque sin su validación la priorización no se usa y el sistema no genera valor.

# **2\. Factores de selección del modelo**

| Factor | Importancia | ¿Por qué afecta la selección? |
| :---- | :---- | :---- |
| Cambios de requisitos | Alta | El componente de IA y las reglas de tamizaje evolucionan con nueva evidencia; se necesita un proceso que admita replanificación frecuente sin retrabajo masivo. |
| Retroalimentación | Alta | Hay que validar predicciones, alertas y mensajes con personal y familias; el proceso debe incluir puntos formales de revisión con el usuario. |
| Riesgo | Alta | Una predicción errónea puede desplazar un caso grave y la conectividad intermitente puede perder datos; el proceso debe acotar el riesgo en ventanas cortas. |
| Integración | Alta | HIS, WhatsApp y modelo deben integrarse de forma verificable; se requieren pruebas de integración automatizadas. |
| Entrega incremental | Alta | El valor debe demostrarse antes de completar todo el sistema: primero registro, luego agenda, después IA. |
| Automatización | Alta | Despliegue a postas dispersas y reentrenamiento del modelo no pueden depender de pasos manuales. |
| Datos e IA | Alta | El modelo exige pipeline de datos, experimentación versionada, validación y monitoreo continuo. |
| Conectividad intermitente | Alta | La funcionalidad offline obliga a diseñar y probar sincronización robusta en cada incremento. |

# **3\. Comparación de modelos**

*Aclaración previa. En sentido estricto solo Cascada, Incremental y Espiral son modelos de ciclo de vida. Scrum es un marco de trabajo de gestión; Kanban es un método de gestión del flujo; DevOps y MLOps son conjuntos de prácticas de ingeniería. Se comparan aquí en una misma tabla, como pide la guía, para evaluar qué capacidades aporta cada enfoque, pero la decisión de la sección 4 respeta esa distinción.*

Escala: 1 \= muy bajo · 2 \= bajo · 3 \= medio · 4 \= alto · 5 \= muy alto.

| Enfoque | Adapta-bilidad | Gestión de riesgos | Entrega incremental | Retroali-mentación | Automa-tización | Adecuación | Total |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Cascada | 1 | 2 | 1 | 1 | 2 | 1 | 8 |
| Incremental | 3 | 3 | 4 | 3 | 2 | 3 | 18 |
| Espiral | 4 | 5 | 3 | 4 | 2 | 3 | 21 |
| Scrum | 5 | 4 | 5 | 5 | 3 | 5 | 27 |
| Kanban | 4 | 3 | 4 | 4 | 3 | 3 | 21 |
| DevOps | 4 | 4 | 5 | 4 | 5 | 4 | 26 |
| MLOps/DataOps | 4 | 4 | 4 | 4 | 5 | 5 | 26 |

**¿El modelo con mayor puntuación debe seleccionarse automáticamente?** No. La tabla mide capacidades aisladas y ningún enfoque cubre por sí solo las necesidades del proyecto. Scrum obtiene 27 pero su automatización es media (3): no resuelve el despliegue a postas dispersas ni el ciclo del modelo. DevOps (26) automatiza la entrega pero no organiza la retroalimentación con el personal de salud. MLOps (26) gobierna el modelo pero no gestiona el resto del producto. La lectura correcta de la tabla no es «gana Scrum», sino que las tres necesidades críticas del proyecto —gestión iterativa con el usuario, entrega automatizada y gobierno del modelo— corresponden a tres enfoques distintos y complementarios. Por eso la sección 4 evalúa combinaciones y no enfoques sueltos.

# **4\. Modelo seleccionado**

**Composición de la decisión (aclaración de categorías)**

| Nivel | Elemento | Función en el proyecto |
| :---- | :---- | :---- |
| Modelo de ciclo de vida | Iterativo e incremental | Es la base: el producto se construye en incrementos funcionales sucesivos que se refinan con la evidencia obtenida. |
| Marco de gestión | Scrum | Organiza la iteración: sprints de dos semanas, backlog priorizado con el personal de salud y revisión formal con el usuario. |
| Prácticas de ingeniería | DevOps | Automatizan construcción, pruebas de sincronización offline y despliegue hacia las postas. |
| Prácticas de datos y modelo | MLOps | Gobiernan el ciclo del modelo predictivo: datos, entrenamiento, publicación, monitoreo y reentrenamiento. |
| Herramientas | GitHub, Actions, MLflow, etc. | Instrumentan las prácticas anteriores; se eligen después del proceso, nunca antes (sección 9). |

**Modelo de proceso seleccionado: desarrollo iterativo-incremental, gestionado con Scrum, con prácticas DevOps para la entrega y prácticas MLOps para el componente predictivo.**

## **4.1 Matriz de decisión ponderada**

Alternativas evaluadas — Alt. 1: iterativo-incremental \+ Scrum \+ DevOps \+ MLOps. Alt. 2: flujo continuo con Kanban \+ DevOps \+ DataOps. Alt. 3: enfoque tradicional, Incremental \+ Espiral sin prácticas de automatización.

*Justificación de los pesos: los cuatro criterios con peso 15 % (adaptabilidad, gestión de riesgos, entrega incremental y retroalimentación) corresponden a las tres características determinantes de la sección 1 —incertidumbre, riesgo del entorno y necesidad de validación con el usuario—. Los cuatro criterios con peso 10 % son habilitadores necesarios pero no determinantes de la elección.*

| Criterio | Peso | Alt. 1  (puntaje → ponderado) | Alt. 2  (puntaje → ponderado) | Alt. 3  (puntaje → ponderado) |
| :---- | :---- | :---- | :---- | :---- |
| Adaptabilidad | 15 % | 5  →  0,75 | 4  →  0,60 | 3  →  0,45 |
| Gestión de riesgos | 15 % | 4  →  0,60 | 3  →  0,45 | 4  →  0,60 |
| Entrega incremental | 15 % | 5  →  0,75 | 4  →  0,60 | 3  →  0,45 |
| Retroalimentación | 15 % | 5  →  0,75 | 4  →  0,60 | 3  →  0,45 |
| Integración | 10 % | 4  →  0,40 | 4  →  0,40 | 3  →  0,30 |
| Automatización | 10 % | 5  →  0,50 | 5  →  0,50 | 2  →  0,20 |
| Gestión de datos / IA | 10 % | 5  →  0,50 | 4  →  0,40 | 2  →  0,20 |
| Participación del usuario | 10 % | 5  →  0,50 | 3  →  0,30 | 3  →  0,30 |
| **Puntaje total ponderado** | **100 %** | **4,75** | **3,85** | **2,95** |

**Lectura de la matriz.** La alternativa 1 no gana por margen general sino por los criterios que pesan más: retroalimentación y entrega incremental, donde la alternativa 2 pierde por no tener puntos formales de revisión con el usuario, y gestión de datos/IA, donde la alternativa 3 queda muy por debajo. Conviene notar que la alternativa 3 empata con la 1 en gestión de riesgos (0,60), porque el modelo Espiral está expresamente construido para eso; se descarta por su débil capacidad de automatización y de gobierno del modelo, no por su tratamiento del riesgo.

# **5\. Justificación**

## **1\. ¿Qué característica del proyecto hace necesario este modelo?**

La imposibilidad de definir por adelantado el componente predictivo. Las variables, el algoritmo y los umbrales de riesgo solo pueden establecerse experimentando con datos históricos reales del HIS, cuya calidad además es variable. A esto se suma que el entorno rural obliga a probar la sincronización offline en condiciones reales y que el personal de salud debe validar la priorización antes de confiar en ella.

## **2\. ¿Qué problema del proceso de desarrollo ayuda a resolver?**

Evita construir durante meses funcionalidades que después no se usan. Al entregar incrementos operativos y revisarlos con la posta, la desviación se detecta en semanas y no al final. Además, resuelve el problema de desplegar hacia establecimientos dispersos sin un procedimiento manual y propenso a error.

## **3\. ¿Cómo permite entregar valor progresivamente?**

Mediante sprints de dos semanas que producen un incremento funcional validado. El orden de los seis incrementos (sección 7\) está diseñado para que cada uno genere valor por sí mismo: el registro nominal ya elimina el triple registro aunque todavía no exista el modelo predictivo.

## **4\. ¿Cómo permite gestionar cambios?**

El backlog se prioriza con el personal de salud y se refina de forma continua. Lo aprendido en la revisión de un sprint se incorpora al siguiente sin alterar la arquitectura central, que se mantiene estable porque el registro nominal y la sincronización se construyen primero.

## **5\. ¿Cómo permite controlar riesgos?**

* **Scrum** acota el impacto de un cambio o de un error de interpretación al ciclo de un sprint.

* **DevOps** reduce el riesgo de despliegue defectuoso mediante integración continua y pruebas automatizadas de sincronización offline.

* **MLOps** controla la degradación y el sesgo del modelo mediante monitoreo por zona y reentrenamiento.

* **La base iterativa** permite descartar tempranamente un algoritmo que no alcanza precisión suficiente, sin haber comprometido el resto del sistema.

## **6\. ¿Qué limitaciones presenta?**

Exige disciplina técnica sostenida para mantener los pipelines y una curva de aprendizaje considerable al combinar tres enfoques. La disponibilidad del personal de salud rural para participar cada dos semanas es limitada por distancia y carga asistencial, por lo que la revisión deberá adaptarse (sesiones cortas, remotas o agrupadas). Finalmente, la calidad del modelo depende de datos históricos que pueden ser insuficientes; si lo son, el incremento 5 deberá posponerse sin bloquear los demás.

## **7\. ¿Por qué se descartaron las alternativas?**

* **Cascada:** exigiría congelar los requisitos del modelo antes de empezar, lo que es inviable porque dependen de la experimentación.

* **Incremental o Espiral sin prácticas de automatización (Alt. 3):** gestionan bien el riesgo, pero no resuelven el despliegue a postas dispersas ni el gobierno del modelo predictivo, que son necesidades centrales aquí.

* **Kanban \+ DevOps \+ DataOps (Alt. 2):** es una opción sólida y de hecho será preferible en la fase de operación, pero en la etapa de construcción inicial carece de los puntos formales de revisión con el usuario que este proyecto necesita para validar la priorización clínica.

# **6\. Representación del proceso**

*En la versión previa esta sección contenía código sin renderizar. Se presenta el diagrama del proceso adaptado al proyecto, cubriendo los diez elementos que exige la guía.*

![][image1]

*Figura 1\. Aplicación del modelo al proyecto: ciclo principal numerado según los diez elementos de la guía, con el subciclo de MLOps que se activa a partir del incremento 5 (elaboración propia).*

El ciclo principal recorre entrada de requerimientos (el TO-BE de la Semana 1), planificación del sprint, desarrollo, integración continua, pruebas —incluida la prueba específica de sincronización offline—, revisión con el usuario, despliegue a la posta piloto, medición con los indicadores definidos en la Semana 1, retrospectiva y paso al siguiente incremento. El subciclo de MLOps corre en paralelo desde el incremento 5 y entrega el artefacto del modelo al pipeline de despliegue; su monitoreo se alimenta de la misma medición del ciclo principal y dispara el reentrenamiento cuando la precisión se degrada.

# **7\. Entregas incrementales de valor**

| Inc. | Funcionalidad | Resultado esperado | Valor generado | Indicador |
| :---- | :---- | :---- | :---- | :---- |
| 1 | Registro nominal validado y expediente digital | Información única y confiable de cada niño | Elimina el triple registro y sus errores | Registros sin error crítico ÷ evaluados × 100 |
| 2 | Agenda automática de controles según NTS 134 y alertas | Controles programados visibles y vencidos identificados | Mayor oportunidad en la atención | Cobertura oportuna de controles × 100 |
| 3 | Funcionalidad offline y sincronización | Registro sin pérdida de datos en zonas sin cobertura | Continuidad del servicio en el ámbito rural | Registros sincronizados ÷ pendientes × 100 |
| 4 | Notificaciones por WhatsApp y reporte de barreras | Familias informadas y barreras reportadas a tiempo | Menor pérdida de seguimiento | Mensajes entregados y leídos ÷ enviados × 100 |
| 5 | Modelo predictivo y priorización de la agenda | Casos de alto riesgo priorizados | Uso más eficiente del personal disponible | Casos confirmados ÷ señalados por el modelo × 100 |
| 6 | Tablero de gestión territorial e indicadores | Supervisión en tiempo real por microred y MINSA | Decisiones territoriales basadas en evidencia | Indicadores de cobertura y resultado actualizados |

*Nota sobre el orden. Los incrementos 1 a 3 se construyen primero porque el modelo predictivo del incremento 5 depende de que existan datos nominales confiables y sincronizados; invertir ese orden dejaría al modelo sin insumo válido.*

# **8\. Riesgos y controles**

| Riesgo | Causa | Impacto | Mecanismo de control |
| :---- | :---- | :---- | :---- |
| Cambios frecuentes en los requisitos del modelo | Incertidumbre sobre variables y algoritmo | Retrabajo en el componente predictivo | Sprints de dos semanas y spikes técnicos acotados para explorar antes de comprometer |
| Datos históricos insuficientes o de baja calidad | Errores previos de digitación en el HIS y registros incompletos | Modelo con precisión insuficiente para priorizar | Validación de datos previa al entrenamiento y pipeline de limpieza en MLOps; criterio explícito para posponer el incremento 5 |
| Fallas de sincronización offline | Conflictos y duplicados al reconectar | Pérdida o corrupción de registros clínicos | Pruebas de integración automatizadas en cada build y resolución de conflictos por marca de tiempo de captura |
| Baja adopción por el personal de salud | Resistencia al cambio y capacitación insuficiente | El sistema no se usa y no genera valor | Revisión de sprint con la posta y capacitación incremental asociada a cada entrega |
| Indisponibilidad o cambios en la API de WhatsApp | Modificaciones de la plataforma o restricciones de la cuenta | Recordatorios no entregados a las familias | Monitoreo del estado de entrega y canal alternativo por SMS previsto desde el diseño |
| Despliegue defectuoso en postas rurales | Conectividad limitada y dispositivos heterogéneos | Interrupción del servicio en el establecimiento | Pipeline de entrega continua con despliegue a una posta piloto antes de extender |
| Sesgo del modelo predictivo | Datos de entrenamiento no representativos de todas las zonas | Subpriorización sistemática de un grupo o distrito | Monitoreo de desempeño desagregado por zona y grupo etario; validación cruzada y revisión profesional de las alertas |

# **9\. Herramientas de soporte**

| Necesidad del proceso | Herramienta | ¿Qué actividad soporta? |
| :---- | :---- | :---- |
| Gestión del trabajo | GitHub Projects | Backlog, sprints e historias, en el mismo lugar que el código |
| Control de versiones | Git / GitHub | Código y configuración versionados |
| Integración y entrega continua | GitHub Actions | Build, pruebas y despliegue automáticos (DevOps) |
| Calidad de código | SonarCloud | Análisis estático y control de deuda técnica |
| Pruebas | Pytest y Selenium | Pruebas de backend y de interfaz, incluida la sincronización offline |
| Experimentación y modelos | Google Colab y MLflow | Experimentación y versionado de modelos (MLOps) |
| Persistencia | PostgreSQL con SQLite local | Almacenamiento central y base local para el modo offline |
| Notificaciones | WhatsApp Business API | Envío de recordatorios y recepción de respuestas de la familia |
| Documentación | Markdown en el repositorio | Documentación versionada junto al código |
| Prototipado | Figma | Diseño de las interfaces antes de construirlas |

## **9.1 Comparativa ponderada de las herramientas críticas**

Gestión del trabajo — criterios: integración con Git (25 %), facilidad de uso (20 %), gestión de sprints (25 %), costo (15 %), colaboración (15 %).

| Herramienta | Int. Git | Uso | Sprints | Costo | Colab. | Total |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| GitHub Projects | 5 | 4 | 4 | 5 | 4 | 4,40 |
| Jira | 4 | 3 | 5 | 2 | 5 | 3,90 |
| Trello | 2 | 5 | 3 | 4 | 4 | 3,45 |

Integración continua — criterios: integración con GitHub (30 %), facilidad de configuración (20 %), capacidad del pipeline (25 %), costo (15 %), comunidad (10 %).

| Herramienta | Int. GH | Config. | Pipeline | Costo | Comun. | Total |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| GitHub Actions | 5 | 5 | 4 | 5 | 5 | 4,75 |
| GitLab CI | 3 | 4 | 5 | 4 | 4 | 3,95 |
| Jenkins | 3 | 2 | 5 | 5 | 4 | 3,70 |

Plataforma de modelos — criterios: facilidad de experimentación (25 %), seguimiento de modelos (25 %), costo (20 %), GPU (15 %), integración con CI/CD (15 %).

| Herramienta | Experim. | Tracking | Costo | GPU | CI/CD | Total |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Colab \+ MLflow | 5 | 5 | 5 | 4 | 3 | 4,55 |
| AWS SageMaker | 4 | 5 | 2 | 5 | 5 | 4,15 |
| Azure ML | 4 | 5 | 2 | 4 | 5 | 4,00 |

**¿La herramienta determina el modelo o al revés?** El modelo de proceso determina las herramientas. En este proyecto la decisión de automatizar la entrega y de gobernar el ciclo del modelo se tomó a partir de las características de la sección 1; solo después se eligieron herramientas capaces de sostener esas prácticas. Si se hubiera partido de la herramienta —por ejemplo, adoptando un gestor de tareas sin integración con el repositorio— el proceso habría quedado limitado por ella.

# **10\. Trazabilidad de la decisión**

| Elemento | Evidencia del proyecto |
| :---- | :---- |
| Problema | Discontinuidad en la prevención, medición, registro y seguimiento de la anemia infantil en zonas rurales de Junín |
| Brecha | Triple registro con errores; agenda manual sin recordatorios; barreras ocultas hasta el abandono; capacidad comunitaria limitada; sin anticipación del riesgo; conectividad intermitente |
| Necesidad de software | Registro nominal validado, agenda NTS 134, operación offline, notificación por WhatsApp, priorización predictiva y tablero de indicadores |
| Característica del proyecto | Alta incertidumbre y experimentación en el componente de IA; riesgo tecnológico del entorno rural; necesidad de validación con el personal de salud |
| Factor de selección | Adaptabilidad, retroalimentación, entrega incremental, automatización y gestión de datos e IA |
| Modelo seleccionado | Iterativo-incremental, gestionado con Scrum, con prácticas DevOps y MLOps |
| Forma de trabajo | Sprints de dos semanas con incremento funcional; integración y despliegue automatizados; ciclo de datos y modelo gobernado con MLOps |
| Incremento | Registro nominal → agenda y alertas → offline → WhatsApp → modelo predictivo → tablero de gestión |
| Resultado | Atención más oportuna, seguimiento continuo, priorización explicable y comunicación efectiva con las familias |
| Valor | Protección de la salud y el desarrollo del niño: menor pérdida de seguimiento, mayor recuperación documentada y mejor uso de recursos limitados |

**11\. Caso de decisión (Actividad 10 de la guía)**

*Situación planteada: un equipo desarrolla una plataforma de salud digital. Los requerimientos no están completamente definidos, el sistema debe integrarse con otros servicios, se espera retroalimentación frecuente de los usuarios y se requiere entregar funcionalidades progresivamente. Algunas funcionalidades utilizan modelos de inteligencia artificial que deberán entrenarse y evaluarse con nuevos datos.*

### ***1\. ¿Qué características del proyecto condicionan la selección del proceso?***

La incertidumbre de los requerimientos, la necesidad de integración con servicios externos, la expectativa de retroalimentación frecuente, la exigencia de entregas progresivas y la presencia de componentes de aprendizaje automático que dependen de datos que aún no se han analizado. A ello se añade la criticidad propia del dominio de salud.

### ***2\. ¿Qué modelo tradicional podría presentar dificultades?***

Cascada. Requiere congelar los requisitos antes de diseñar y construir, y aquí no están definidos. Además concentra la validación al final, cuando corregir un error de interpretación resulta mucho más costoso.

### ***3\. ¿Qué ventajas ofrecería un enfoque iterativo e incremental?***

Permite entregar funcionalidad utilizable desde temprano, obtener evidencia real de uso y ajustar el alcance con esa evidencia. También acota el impacto de un error a un ciclo corto y hace posible descartar una hipótesis técnica antes de haber construido todo el sistema.

### ***4\. ¿Qué aportaría Scrum?***

Un marco de gestión para esa iteración: backlog priorizado con los usuarios, sprints de duración fija, y una revisión formal al final de cada uno que convierte la retroalimentación en una actividad planificada y no en algo ocasional.

### ***5\. ¿Qué aportaría DevOps?***

Automatización de la construcción, las pruebas y el despliegue. En un sistema que se integra con otros servicios, las pruebas de integración automatizadas en cada cambio son el mecanismo que evita que una modificación rompa la interoperabilidad sin que nadie lo note.

### ***6\. Si existe aprendizaje automático, ¿qué problemas adicionales deben considerarse?***

* El modelo depende de datos cuya calidad y representatividad hay que verificar antes de entrenar.

* El desempeño se degrada con el tiempo si cambia la población atendida, por lo que requiere monitoreo y reentrenamiento.

* Aparece el riesgo de sesgo: el modelo puede desfavorecer sistemáticamente a un grupo, lo que en salud es especialmente grave.

* Se necesita versionar datos, experimentos y modelos, no solo código.

* En un dominio clínico, la predicción debe ser explicable y quedar siempre supeditada al criterio profesional.

### ***7\. ¿Sería suficiente utilizar Scrum para todo el proyecto?***

No. Scrum organiza el trabajo y la retroalimentación, pero no dice nada sobre cómo automatizar la integración y el despliegue ni sobre cómo gobernar el ciclo de vida de un modelo. Un equipo que solo aplique Scrum puede terminar con sprints bien gestionados y, aun así, despliegues manuales frágiles y un modelo cuya degradación nadie vigila.

### ***8\. ¿Qué combinación de enfoques podría resultar conveniente?***

Una base iterativa e incremental, gestionada con Scrum, con prácticas DevOps para la entrega y prácticas MLOps para el componente de aprendizaje automático. Cada elemento cubre una necesidad que los otros no atienden.

### ***9\. ¿Cómo se entregaría valor en los primeros incrementos?***

Priorizando la funcionalidad que ya resuelve un problema por sí sola aunque el componente de IA todavía no exista: típicamente el registro confiable de la información y su disponibilidad para quien la necesita. Esos incrementos, además, generan los datos que después harán posible entrenar el modelo.

### ***10\. ¿Qué indicadores permitirían verificar que el proceso está funcionando?***

Del proceso de desarrollo: incrementos entregados y aceptados por sprint, frecuencia de despliegues exitosos, cobertura de pruebas automatizadas y tiempo de recuperación ante un fallo. Del producto y su resultado: adopción real por los usuarios, precisión del modelo validada contra criterio experto y los indicadores de valor propios del dominio.

# **12\. Preguntas de análisis**

### ***1\. ¿Qué características fueron determinantes para seleccionar el modelo?***

La incertidumbre y la necesidad de experimentación del componente predictivo, el riesgo tecnológico del entorno rural (conectividad intermitente) y la necesidad de que el personal de salud valide la priorización. Las tres exigen un proceso que entregue en ciclos cortos, automatice la entrega y gobierne el modelo de forma explícita.

### ***2\. ¿Por qué es más adecuado que una alternativa tradicional?***

Porque un enfoque tradicional exigiría definir los requisitos del modelo antes de desarrollar, lo cual es inviable: el algoritmo, las variables y los umbrales dependen de la experimentación con datos reales. Además, dejaría la validación con el personal para etapas tardías, con el riesgo de construir funcionalidades que no se ajustan al contexto rural de Junín.

### ***3\. ¿Qué riesgos del proyecto trata el modelo seleccionado?***

Los sprints acotan el retrabajo ante cambios; las prácticas DevOps reducen el riesgo de despliegue defectuoso y verifican la sincronización offline en cada build; las prácticas MLOps controlan la degradación y el sesgo del modelo; y las revisiones periódicas mitigan el riesgo de baja adopción, que es el riesgo con mayor impacto sobre el valor esperado.

### ***4\. ¿Cómo se incorporará la retroalimentación de los usuarios?***

Mediante la revisión al final de cada sprint con personal de salud, agente comunitario y microred, adaptada a su disponibilidad (sesiones breves y, cuando sea necesario, remotas). Las familias retroalimentan de forma indirecta a través de las tasas de respuesta y confirmación de los mensajes. El modelo se valida contrastando los casos que marca como de alto riesgo con el criterio clínico del profesional.

### ***5\. ¿Cómo se realizará la entrega incremental de valor?***

En los seis incrementos de la sección 7, ordenados de modo que cada uno sea funcional por sí mismo y que los primeros generen los datos que los posteriores necesitan.

### ***6\. ¿Qué actividades del proceso serán automatizadas?***

Con DevOps: construcción, pruebas unitarias y de integración (incluida la de sincronización offline), despliegue y monitoreo del sistema. Con MLOps: ingesta y limpieza de datos, entrenamiento y evaluación del modelo, publicación del artefacto, monitoreo de desempeño y reentrenamiento. La gestión del backlog y el seguimiento del sprint se apoyan en la herramienta de gestión del trabajo.

### ***7\. ¿Qué herramientas soportarán el proceso?***

Las de la sección 9, seleccionadas después de definir el proceso: GitHub y GitHub Projects, GitHub Actions, SonarCloud, Pytest y Selenium, Google Colab con MLflow, PostgreSQL con SQLite local, la API de WhatsApp Business, documentación en Markdown y Figma para prototipado.

### ***8\. ¿Qué limitaciones presenta el modelo seleccionado?***

Alta exigencia de disciplina técnica, curva de aprendizaje por combinar tres enfoques, disponibilidad limitada del personal rural para las revisiones y dependencia de la calidad de los datos históricos para el incremento 5\.

### ***9\. ¿En qué situación cambiarían o complementarían el modelo?***

Al pasar a operación y mantenimiento continuo convendría sustituir los sprints por un flujo continuo tipo Kanban, más adecuado para atender correcciones y mejoras menores con prioridades cambiantes. Si más adelante se requiriera analítica poblacional a mayor escala, se incorporarían prácticas de DataOps sobre los pipelines de datos.

### ***10\. ¿Cómo demostrarán que el modelo de proceso contribuye al éxito?***

Contrastando indicadores de proceso —incrementos aceptados por sprint, frecuencia de despliegue exitoso, cobertura de pruebas, tiempo de recuperación ante fallos y precisión del modelo en cada reentrenamiento— con los indicadores de valor definidos en la Semana 1: cobertura oportuna, adherencia y recuperación documentada. Si la forma de trabajo funciona, la mejora debe verse en ambos planos.

**13\. Defensa de cinco minutos (reto de aplicación)**

## **1\. ¿Qué problema tenemos? (aprox. 1 minuto)**

En las zonas rurales de Junín el seguimiento de la anemia infantil se rompe. La meta clínica es diagnosticar al niño a los 6 meses y recuperarlo al año, lo que exige seis meses continuos de suplementación con controles periódicos. Ese seguimiento se apoya hoy en un triple registro manual —historia clínica, tarjeta de control y digitación posterior en el HIS— con agendamiento a mano y sin recordatorios. Las barreras de la familia, como no tener pasaje, solo se descubren cuando el niño ya abandonó. La brecha principal es que no existe visibilidad oportuna del estado real de cada niño.

## **2\. ¿Qué características tiene nuestro proyecto? (aprox. 1 minuto)**

Tres condicionan todo lo demás. Primero, no podemos definir el componente predictivo por adelantado: las variables y los umbrales solo se pueden fijar experimentando con los datos históricos del HIS. Segundo, el entorno tiene cobertura móvil intermitente, así que la aplicación debe funcionar sin conexión y eso hay que probarlo en cada entrega. Tercero, si el personal de salud no valida la priorización, no la usa, y el sistema no genera ningún valor.

## **3\. ¿Por qué elegimos este modelo? (aprox. 2 minutos)**

Comparamos siete enfoques. Ninguno alcanzaba por sí solo: Scrum puntúa alto en adaptabilidad y retroalimentación pero medio en automatización; DevOps automatiza pero no organiza la validación con el usuario; MLOps gobierna el modelo pero no el resto del producto. Por eso evaluamos combinaciones en una matriz ponderada, dando más peso a adaptabilidad, retroalimentación, entrega incremental y gestión de riesgos, que son las que se desprenden de nuestras tres características.

Elegimos una base iterativa e incremental, gestionada con Scrum, con prácticas DevOps para la entrega y prácticas MLOps para el modelo. Conviene ser precisos con las categorías: el modelo de ciclo de vida es el iterativo-incremental; Scrum es el marco de gestión; DevOps y MLOps son conjuntos de prácticas de ingeniería. Descartamos Cascada porque exigiría congelar requisitos que aún no existen, y descartamos Kanban para esta etapa porque carece de puntos formales de revisión, aunque será la mejor opción cuando pasemos a operación.

## **4\. ¿Cómo generará valor? (aprox. 1 minuto)**

En seis incrementos, cada uno funcional por sí mismo y con su propio indicador. El primero, el registro nominal validado, ya elimina el triple registro aunque todavía no exista nada de inteligencia artificial. Después vienen la agenda automática según la NTS 134, el modo offline, las notificaciones por WhatsApp, el modelo predictivo y el tablero de gestión. El orden no es arbitrario: el modelo del incremento 5 necesita que antes existan datos nominales confiables y sincronizados. Cada incremento se mide contra los indicadores que definimos en la Semana 1, de modo que podemos demostrar el valor generado antes de haber terminado el sistema completo.

# **14\. Fuentes**

* Guía de trabajo semana 2 — Eje 2: Modelo de procesos de software (documento del curso).

* Entregable Semana 1 del equipo: proceso TO-BE, brechas e indicadores del proyecto.

* Entrevista a personal de salud de una posta rural de Junín (2026, comunicación personal).

* NTS N.° 134-MINSA/2017/DGIESP. [bvs.minsa.gob.pe/local/MINSA/4190.pdf](https://bvs.minsa.gob.pe/local/MINSA/4190.pdf)

[image1]: img/image1.png