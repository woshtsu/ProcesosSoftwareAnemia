**Curso: Procesos de Software — 2026-20**

**Proyecto: Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín**

**Entregable — Semana 1**

**Nota de versión:** esta versión completa las secciones y diagramas pendientes del entregable original e incorpora tres mejoras solicitadas: (1) diagramas de proceso AS-IS/TO-BE y diagramas UML (casos de uso y clases), (2) notificaciones a la familia por WhatsApp dentro del proceso TO-BE, y (3) un modelo predictivo de IA como aporte del software. Todo el contenido nuevo o modificado respecto de la versión previa se muestra **resaltado en amarillo** para su fácil identificación.

**Integrantes y roles del equipo**

| **Integrante** | **Rol en el proyecto** |
| --- | --- |
| Porras Veli Ricardo | Ingeniero de Proceso |
| Auqui Huincho Tania | Ingeniero de Desarrollo y Prototipado |
| Huamani Rodriguez Jean Piero | Ingeniero de Calidad y Mejora del Proceso |

# 1. Problema organizacional

El proceso rural de prevención, identificación, medición, evaluación, registro y seguimiento de anemia infantil no asegura una continuidad nominal, oportuna y coordinada entre familias, personal de salud, actores comunitarios, instituciones educativas y gestión territorial. En Junín se han documentado errores en el registro HIS del control de hemoglobina, seguimiento débil, brecha de personal en distritos alejados y deserción del tratamiento (Gobierno Regional de Junín).

El problema no se formula como ausencia de software. El valor perdido aparece cuando una oportunidad preventiva, un dosaje o una indicación no se convierte en seguimiento y acción oportunos. Como contexto, ENDES 2025 estimó 39,0 % de anemia en niñas y niños de 6 a 35 meses de Junín con la directriz vigente (INEI); esta cifra no es un resultado atribuible al futuro sistema.

# 2. Actores y necesidades

| **Actor** | **Necesidad** | **Decisión que debe tomar** |
| --- | --- | --- |
| Niña o niño | Atención preventiva, medición y seguimiento oportunos y seguros | No toma decisiones clínicas; participa según edad y comunica síntomas/tolerancia cuando puede |
| Madre, padre o cuidador | Indicaciones comprensibles, recordatorios y apoyo ante barreras | Acudir, cumplir el plan indicado, solicitar apoyo y aceptar referencia |
| Personal de salud del primer nivel | Información nominal confiable, resultados y pendientes visibles | Evaluar, diagnosticar, indicar/ajustar intervención y referir según competencia y norma |
| Agente comunitario o actor social | Casos priorizados y canal de referencia | Visitar, registrar barreras y referir; no modificar tratamiento |
| Institución educativa | Coordinación preventiva y acceso solo a datos necesarios | Facilitar actividades y comunicar necesidad de coordinación |
| Gestión sanitaria territorial | Indicadores confiables de cobertura, retraso y resultado | Priorizar supervisión, capacitación, recursos y acciones correctivas |
| Gobierno local | Información territorial agregada | Priorizar sectores y organizar apoyo comunitario dentro de su competencia |

**Actor que recibe mayor valor:** la niña o el niño, porque el resultado esperado protege directamente su salud y desarrollo. La familia es coproductora del valor y recibe acompañamiento, pero el beneficio final se materializa en el menor.

# 3. Proceso AS-IS

## Descripción

1. El menor es identificado por control, padrón, campaña, visita, institución educativa o iniciativa familiar.
2. La familia acude o recibe una intervención territorial.
3. Salud evalúa antecedentes y determina si corresponde dosaje.
4. Personal autorizado realiza/gestiona hemoglobina y el profesional interpreta según edad, condición y altitud.
5. Si no hay anemia, indica prevención y control; si hay anemia, diagnostica e indica tratamiento, evaluación o referencia.
6. La atención se registra en historia clínica, formatos y/o HIS.
7. La familia ejecuta la indicación; el actor comunitario refuerza prácticas y comunica barreras.
8. Salud controla adherencia/evolución y decide cierre, continuidad, ajuste o referencia.
9. Gestión territorial consolida información y coordina acciones.

**Problemas:** errores de registro; seguimiento débil y capacidad limitada; inasistencia; abandono por barreras; coordinación por canales separados; indicadores debilitados por información incompleta.

**Diagrama de actividades UML — Proceso AS-IS**

Se representa el proceso AS-IS como diagrama de actividades UML, con nodo inicial y final, estados de acción, nodos de decisión y anotaciones de "Problema" ancladas a las actividades donde se origina cada brecha (detalladas en la sección 4). El color de cada actividad identifica al actor responsable, según la leyenda del propio diagrama.

![](data:image/png;base64...)

*Figura 1. Diagrama de actividades UML del proceso AS-IS, con anotaciones de problema por actividad (elaboración propia).*

# 4. Brechas

| **Proceso actual** | **Problema / Brecha** | **Consecuencia** |
| --- | --- | --- |
| Registro en historia clínica/formatos/HIS | Errores y falta de una vista nominal validada | Estado y pendientes poco confiables |
| Seguimiento con personal y visitas limitados | Capacidad insuficiente en territorios alejados | Controles tardíos o perdidos |
| Intervención ejecutada en el hogar | Barreras y abandono no visibles oportunamente | Menor finalización y recuperación tardía |
| Detección activada por asistencia/contacto | Menores fuera de contacto pueden no ser atendidos a tiempo | Oportunidades preventivas perdidas |
| Coordinación por canales separados | Referencias sin circuito compartido ni cierre | Duplicidad, demora o falta de respuesta |
| Consolidación posterior de información | Errores y pendientes reducen capacidad de priorización | Supervisión y recursos menos focalizados |

# 5. Proceso TO-BE

## Cambio propuesto

1. Salud registra o sincroniza un expediente nominal con validaciones y autoría.
2. El sistema aplica reglas institucionales para identificar controles próximos/vencidos y crea tareas.
3. El modelo predictivo de IA estima el riesgo de anemia y de pérdida de seguimiento de cada caso, y prioriza junto con el motor de reglas las tareas que revisará el personal de salud.
4. El sistema envía a la familia un recordatorio o confirmación de cita mediante notificación por WhatsApp.
5. La familia confirma la cita o reporta una barrera respondiendo por el mismo canal de WhatsApp; si existe atraso, salud asigna seguimiento comunitario.
6. La institución educativa facilita únicamente coordinación preventiva y el gobierno local apoyo territorial.
7. Salud evalúa y registra dosaje; la captura funciona en modo offline cuando no hay señal y se sincroniza automáticamente al recuperar conectividad; el profesional decide prevención, diagnóstico, tratamiento o referencia.
8. Familia y actor comunitario registran cumplimiento/barreras; las alertas son revisadas por salud.
9. Referencias mantienen estados hasta cierre.
10. Gestión revisa cobertura, calidad, atrasos y resultados para actuar.

**Diagrama de actividades UML — Proceso TO-BE**

El proceso TO-BE se representa también como diagrama de actividades UML, con nodo inicial y final, decisiones y estados de acción coloreados por actor responsable. En amarillo se resaltan las actividades nuevas o mejoradas: registro y evaluación con funcionalidad offline, priorización mediante modelo predictivo de IA, y notificación/confirmación por WhatsApp, cada una con una anotación breve de "Mejora".

![](data:image/png;base64...)

*Figura 2. Diagrama de actividades UML del proceso TO-BE, con anotaciones de mejora (elaboración propia).*

La priorización inteligente se limita a atrasos y riesgo de pérdida de seguimiento; debe ser explicable, validada y supervisada. No diagnostica ni prescribe. El modelo de IA y el canal de WhatsApp son mecanismos de apoyo a la coordinación y al recordatorio: no reemplazan el criterio profesional ni sustituyen la visita cuando esta es necesaria. La funcionalidad offline asegura que el registro no se pierda ni se retrase por falta de cobertura, típica de las zonas rurales de Junín.

**Requisito no funcional: funcionalidad offline**

* Captura local: el aplicativo permite registrar expediente, dosaje, visitas y barreras sin conexión a internet, almacenando los datos de forma cifrada en el dispositivo.
* Sincronización diferida: al recuperar señal, el sistema sincroniza automáticamente los registros pendientes con el servidor central, validando duplicados y conflictos.
* Notificación diferida: los recordatorios de WhatsApp y las alertas del modelo de IA se generan al sincronizar si no pudieron enviarse en el momento.
* Trazabilidad: cada registro conserva la fecha/hora real de captura (aunque se sincronice después) para no distorsionar los indicadores de oportunidad.

# 6. Aporte del software

| **Actividad organizacional** | **¿Interviene software?** | **¿Cómo aporta?** |
| --- | --- | --- |
| Identificar elegibles/pendientes | Sí, automatizada y validada por salud | Agenda según reglas aprobadas |
| Convocar familia | Sí, asistida | Recordatorio, confirmación y reporte de barrera mediante mensajería de WhatsApp |
| Evaluar y medir hemoglobina | Sí, asistida | Antecedentes, captura y validación de datos; ejecución humana |
| Diagnosticar e indicar intervención | Sí, como apoyo | Presenta información; la decisión y firma son profesionales |
| Registrar/sincronizar | Sí, automatizada | Valida, deduplica, audita y opera con conectividad intermitente |
| Administrar indicación en hogar | No en la ejecución | Instrucciones y recordatorios; acción humana |
| Realizar visita | Sí, asistida | Priorización y captura offline; contacto humano |
| Cerrar referencia | Sí, asistida/automatizada | Estados, responsables y alertas de atraso |
| Supervisar proceso | Sí, asistida | Indicadores y excepciones para decisión territorial |
| **Priorizar casos con riesgo de anemia o de pérdida de seguimiento** | **Sí, mediante modelo predictivo de IA** | El modelo estima un puntaje de riesgo a partir de antecedentes, hemoglobina previa, edad, altitud y adherencia; ordena la agenda de salud y explica los factores de cada predicción. No diagnostica ni decide: la validación y la decisión clínica siguen siendo del profesional de salud. |
| **Registrar y evaluar sin conexión** | **Sí, funcionalidad offline** | Captura local cifrada de expediente, dosaje, visitas y barreras en zonas sin cobertura; sincronización automática y validación de duplicados/conflictos al recuperar conectividad. |

# 7. Valor organizacional (Entrega de valor)

**Diagrama de Flujo de Procesos y Entrega de Valor**

La entrega de valor se representa con un Diagrama de Flujo de Procesos: cada actor entrega o recibe información en un paso concreto de la cadena, hasta que gestión territorial evalúa, decide y actúa, generando el valor final para la niña o el niño.

![](data:image/png;base64...)

*Figura 3. Diagrama de Flujo de Procesos y Entrega de Valor. Los pasos en amarillo son los mecanismos nuevos (IA, WhatsApp, modo offline) (elaboración propia).*

**Datos validados → identificación de pendiente → evaluación profesional → decisión → intervención/seguimiento → atención más oportuna y continua.**

* Registro validado → información confiable → decisiones con menor riesgo de error.
* Agenda y alerta → seguimiento humano oportuno → menor pérdida de contacto.
* Modelo predictivo de IA → priorización explicable de casos en riesgo → uso más eficiente del personal de salud disponible.
* Notificación por WhatsApp → recordatorio de bajo costo y alto alcance en zonas rurales → mayor confirmación de citas y reporte temprano de barreras.
* Funcionalidad offline → ningún registro se pierde por falta de cobertura → datos completos y oportunos para decisiones y auditoría.
* Barrera visible → respuesta adaptada → mayor continuidad.
* Referencia cerrada → coordinación verificable → menor incertidumbre.
* Indicadores oportunos → acción correctiva → mejor uso de capacidad limitada.

Los valores son esperados y deberán comprobarse contra una línea base.

# 8. Indicadores

| **Tipo** | **Indicador** | **Qué mide** | **Cómo se mide** |
| --- | --- | --- | --- |
| Proceso | Cobertura oportuna de medición/control | Atención dentro de ventana | Atendidos oportunamente ÷ elegibles × 100 |
| Proceso | Demora de controles vencidos | Retraso del proceso | Mediana de días entre fecha prevista y realizada |
| Proceso | Cumplimiento de visitas priorizadas | Ejecución comunitaria | Visitas oportunas ÷ visitas priorizadas × 100 |
| Proceso | Cierre oportuno de referencias | Continuidad entre actores | Referencias cerradas a tiempo ÷ referencias vencibles × 100 |
| Producto | Registros que superan validaciones | Calidad del dato | Registros sin error crítico/duplicidad pendiente ÷ evaluados × 100 |
| Producto | Sincronización offline exitosa | Fiabilidad rural | Registros sincronizados y confirmados ÷ pendientes × 100 |
| Producto | Disponibilidad operativa | Uso de funciones esenciales | Minutos disponibles ÷ minutos programados × 100 |
| Producto | Tasa de entrega de notificaciones WhatsApp | Alcance efectivo del recordatorio | Mensajes entregados y leídos ÷ mensajes enviados × 100 |
| Producto | Precisión del modelo predictivo de IA | Calidad de la priorización de riesgo | Casos de alto riesgo confirmados por salud ÷ casos señalados por el modelo × 100 |
| Resultado | Finalización documentada | Continuidad del plan | Casos que completan ÷ casos que debían completar × 100 |
| Resultado | Recuperación documentada | Resultado clínico confirmado | Recuperados ÷ casos con control de cierre válido × 100 |
| Valor | Pérdida de seguimiento | Casos sin atención/cierre | Casos sobre umbral sin cierre ÷ casos con seguimiento × 100 |
| Valor | Oportunidades recuperadas | Atención tras acción de seguimiento | Vencidos atendidos tras acción ÷ vencidos con acción × 100 |
| Valor | Prevalencia de anemia | Evolución poblacional | Fuente oficial/protocolo comparable; sin atribuirla solo al sistema |

No se fijan metas numéricas todavía. Toda futura Meta propuesta requerirá línea base y aprobación institucional.

# 9. Diagramas UML complementarios (nueva sección)

Las secciones 3 y 5 ya presentan el AS-IS y el TO-BE como diagramas de actividades UML. Esta sección añade dos diagramas UML adicionales que precisan, a nivel de solución, cómo el software soporta el proceso TO-BE: un diagrama de casos de uso (interacción de actores con el sistema, incluyendo WhatsApp y el modelo de IA como servicios de apoyo) y un diagrama de clases (entidades principales del dominio, incluida la funcionalidad offline).

## 9.1 Diagrama de casos de uso

![](data:image/png;base64...)

*Figura 4. Casos de uso del sistema. Resaltados en amarillo los casos de uso incorporados: notificación por WhatsApp y estimación de riesgo por IA (elaboración propia).*

## 9.2 Diagrama de clases (dominio principal)

![](data:image/png;base64...)

*Figura 5. Diagrama de clases del dominio. Resaltadas en amarillo las clases nuevas: ModeloPredictivoIA, AlertaSeguimiento, NotificacionWhatsApp y ColaSincronizacionOffline (elaboración propia).*

# Preguntas de análisis

## 1. ¿Qué problema del proceso organizacional se pretende resolver?

La discontinuidad, demora y coordinación poco confiable en prevención, medición, registro, seguimiento y recuperación; no simplemente la ausencia de una aplicación.

## 2. ¿Qué actividad del AS-IS genera mayor pérdida de valor?

El seguimiento posterior a la indicación, porque concentra inasistencia, barreras familiares, capacidad limitada y errores de registro. Una medición o prescripción sin control posterior pierde gran parte de su valor.

## 3. ¿Qué cambia concretamente en el TO-BE?

Se crea un circuito nominal validado con agenda, tareas, barreras, referencias cerrables e indicadores; las decisiones clínicas siguen siendo profesionales. Se añaden tres mecanismos de apoyo: el recordatorio y la confirmación por WhatsApp con la familia, un modelo predictivo de IA que ayuda a priorizar los casos con mayor riesgo de anemia o de pérdida de seguimiento, y una funcionalidad offline que permite registrar y evaluar sin conexión en zonas sin cobertura, sincronizando automáticamente al recuperar la señal.

## 4. ¿Qué actividades serán automatizadas o mejoradas mediante software?

Validación, deduplicación, agenda, recordatorios, sincronización, estados de referencia e indicadores se automatizan. Convocatoria, evaluación, registro, visita y priorización se asisten. La convocatoria y el reporte de barreras se asisten específicamente mediante WhatsApp, la priorización se apoya en un modelo predictivo de IA, y el registro/evaluación en campo se mejora con captura offline y sincronización diferida. Diagnóstico y prescripción no se automatizan.

## 5. ¿Cómo se demostrará que el nuevo proceso genera valor?

Comparando con una línea base la cobertura oportuna, demoras, cierre de visitas/referencias, calidad de datos, finalización, recuperación documentada y pérdida de seguimiento. Una alerta sin acción y cierre no demuestra valor. Para los componentes nuevos, se hará seguimiento adicional de la tasa de entrega/lectura de WhatsApp y de la precisión del modelo de IA frente a la validación profesional.

# Fuentes principales

* Documentos del docente: lista de proyectos y Guía de Trabajo Semana 1.
* [RM N.° 251-2024-MINSA — NTS 213](https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa) y [RM N.° 429-2024-MINSA](https://www.gob.pe/institucion/minsa/normas-legales/5670414-429-2024-minsa).
* [Plan Multisectorial 2024–2030](https://cdn.www.gob.pe/uploads/document/file/5735214/5093832-decreto-supremo-n-002-2024-sa%282%29.pdf?v=1706299424).
* [Informe de resultados institucionales del Gobierno Regional de Junín](https://www.regionjunin.gob.pe/documentos_region/2026/2026-02-20/GRJ-172953a0409b63c23ea34470753707ceb60228.pdf).
* [ENDES 2025](https://proyectos.inei.gob.pe/endes/2025/ppr/Informe_Indicadores_de_Resultados_de_los_Programas_Presupuestales_ENDES_2025.pdf).
* [RM N.° 673-2018-MINEDU](https://www.gob.pe/institucion/minedu/normas-legales/223656-673-2018-minedu) y [convenio DREJ–DIRESA](https://www.gob.pe/institucion/regionjunin-dre/noticias/758978-drej-y-diresa-junin-firman-convenio-para-prevenir-y-recuperar-la-salud-de-estudiantes).
* [Reglamento de la Ley N.° 29733](https://www.gob.pe/institucion/anpd/normas-legales/6554453-16-2024-jus).