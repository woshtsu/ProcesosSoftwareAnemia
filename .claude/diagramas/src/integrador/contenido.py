REPORT=[]
AUDIT=[]
def page(dest,title,*blocks): dest.append((title,list(blocks)))
def p(t): return ('p',t)
def h(t): return ('h',t)
def tb(head,rows,widths=None): return ('table',head,rows,widths)
def fig(name,caption,maxh=430): return ('fig',name,caption,maxh)
def note(t): return ('note',t)

page(REPORT,'Informe académico integrador de las Unidades I y II',
p('Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín'),
p('Diseño e implementación del proceso de software con entrega de valor'),
tb(['Datos académicos','Información'],[
['Universidad y carrera','Universidad Continental · Ingeniería de Sistemas e Informática'],
['Asignatura','Procesos de Software · ASUC01702 · Noveno ciclo · 2026-20'],
['Proyecto y organización','PMV de registro nominal y expediente digital para una posta rural de Junín. Establecimiento no identificado en los antecedentes.'],
['Docente y fecha de entrega','Por completar por el equipo'],
['Fecha de esta revisión','25 de septiembre de 2026']],[135,370]),
tb(['Integrante','Rol conservado de S1 a Actividad 5'],[
['Porras Veli, Ricardo','Ingeniero de Proceso'],['Auqui Huincho, Tania','Ingeniero de Desarrollo y Prototipado'],['Huamani Rodriguez, Jean Piero','Ingeniero de Calidad y Mejora del Proceso']],[230,275]),
p('Códigos de estudiante: por completar por cada integrante. Se mantiene el equipo real de tres personas; las responsabilidades de arquitectura, backend y frontend se agrupan en Desarrollo, con revisión de Calidad.'),
note('Versión integrada para revisión del equipo. La arquitectura y los resultados técnicos se documentan a partir del avance disponible. La aceptación del PMV requiere vincular el código, los reportes y el tag de entrega. No se acredita despliegue institucional ni resultado clínico.'))

page(REPORT,'1 Resumen ejecutivo y alcance del proyecto',
p('El proyecto aborda la discontinuidad del seguimiento de la anemia infantil en zonas rurales de Junín. El entregable de Semana 1 identifica registros fragmentados, programación manual, barreras familiares poco visibles y conectividad intermitente. El valor esperado es que la información permita al personal actuar oportunamente y conservar la continuidad de la atención.'),
p('El primer incremento se limita al registro nominal validado, consulta y actualización del expediente, dosajes de hemoglobina, listado de seguimiento y reporte del periodo. La agenda, sincronización distribuida, WhatsApp, predicción de abandono y tablero territorial se mantienen en incrementos posteriores. La clasificación referencial por hemoglobina del PMV no constituye el modelo predictivo de abandono.'),
p('El proceso conserva la base iterativa e incremental, gestionada con Scrum y prácticas DevOps. MLOps se incorpora cuando exista un componente predictivo evaluable. El avance documenta una aplicación Python con Flask y Jinja2, persistencia SQLite y organización hexagonal. La integración propone vistas C4 y decisiones arquitectónicas que explican ese alcance local.'),
p('La Actividad 5 reporta 49 pruebas exitosas, cobertura de líneas de 95,8 % y una demostración con datos sintéticos. Su tabla detalla 40 ejecuciones; el total requiere conciliación con el registro de pruebas. La captura del reporte muestra 24 intentos aceptados de 28 evaluados, equivalentes a 85,7 %. Esta métrica describe aceptación de datos de demostración y no prueba una mejora asistencial. La liberación se condiciona a reportes reproducibles, evidencia E2E y de carga, aceptación del usuario y repositorio identificado.'),
h('Límites del primer incremento'),
tb(['Incluido en el alcance documentado','Fuera del primer incremento'],[
['HIST-1.1 a HIST-1.5 y validaciones de captura','Agenda y controles vencidos: INC-2'],
['Registro y consulta en el entorno local del PMV','Captura distribuida, cifrado local y sincronización: INC-3'],
['Semáforo referencial de la última clasificación','Mensajería y barreras: INC-4; predicción de abandono: INC-5'],
['Reporte básico de registros del periodo','Tablero territorial completo: INC-6; integración institucional con HIS pendiente de especificación']],[252,253]),
note('Lectura de estados: documentado significa que aparece en los antecedentes; propuesto significa una corrección o decisión que el equipo debe adoptar; pendiente significa que falta evidencia para darlo por cumplido.'))

page(REPORT,'2 Unidad I Fundamentos y diseño del proceso',
h('2.1 Diagnóstico y actores'),
p('La Semana 1 sitúa la pérdida de valor después de la atención: la medición o indicación no siempre se convierte en seguimiento oportuno. La historia clínica, la tarjeta y la digitación posterior en HIS dispersan la información. El proyecto conserva el diagnóstico, tratamiento y referencia bajo responsabilidad profesional. El registro digital es un habilitador de ese proceso.'),
tb(['Actor','Necesidad y decisión','Participación en INC-1'],[
['Niña o niño menor de 5 años','Recibir atención continua; beneficiario sin decisión clínica.','Sus datos son objeto del registro; no es actor que opera el software.'],
['Familia o cuidador','Acudir a controles y comunicar barreras.','Proporciona información al personal; no se documenta acceso directo.'],
['Personal de salud','Consultar antecedentes y decidir atención según competencia.','Registra, consulta, actualiza y revisa dosajes.'],
['Agente comunitario','Registrar visitas y escalar barreras.','Uso de campo diferido; no se acredita una interfaz propia en el PMV.'],
['Gestión territorial y MINSA','Supervisar cobertura y asignar recursos.','Tablero e intercambio institucional futuros.'],
['Coordinador del proyecto','Revisar registros y calidad de captura.','Consulta el reporte básico del periodo. Rol añadido en HIST-1.5; no equivale a MINSA.']],[110,210,185]),
h('Brechas que se mantienen desde Semana 1'),
tb(['ID','Brecha y consecuencia','Intervención prevista'],[
['B1','Registro fragmentado: duplicidad, errores y demora.','INC-1 registro validado; eliminación institucional del triple registro requiere un cambio adicional.'],
['B2','Agenda manual: controles fuera de fecha.','INC-2 programación y vencimientos.'],
['B3','Barreras ocultas: abandono detectado tarde.','INC-4 comunicación y barreras.'],
['B4','Visitas en papel: limitada cobertura comunitaria.','INC-3 captura en campo; backlog de visitas pendiente de completar.'],
['B5','Priorización reactiva: intervención tardía.','INC-5 riesgo de abandono supervisado.'],
['B6','Conectividad intermitente y consolidación tardía.','INC-3 sincronización e INC-6 indicadores.']],[32,241,232]))

page(REPORT,'2.1 Procesos actual y propuesto',
fig('01_procesos_as_is_to_be','Figura 1. Síntesis del AS-IS y TO-BE de S1, secciones 3 a 6. Las vistas originales por carriles mantienen el detalle clínico.',430),
p('En el AS-IS, la familia acude, el personal verifica si corresponde control y tamizaje, registra la atención y organiza el seguimiento. La familia administra el suplemento y el agente comunitario visita el hogar. El profesional reevalúa o refiere; gestión territorial consolida la información.'),
p('En el TO-BE se conserva esa responsabilidad humana. El sistema valida la captura, organiza controles y, en incrementos posteriores, sincroniza registros y apoya la comunicación y priorización. La figura resume el flujo; no representa un diagnóstico o prescripción automática.'),
note('La referencia hasta su cierre aparece en S1 pero no tiene una historia propia en el WBS de S3-S4. Se propone mantenerla como requisito pendiente de planificación, sin declararla entregada ni asignarla silenciosamente al PMV.'))

page(REPORT,'2.1 Intervención del software y generación de valor',
tb(['Actividad organizacional','Intervención','Aporte y alcance'],[
['Registrar y consultar expediente','Automatizada','INC-1: validación, identificador y consulta.'],
['Medir hemoglobina','Asistida','La medición es humana; INC-1 conserva el dosaje y presenta clasificación referencial.'],
['Diagnosticar y prescribir','Apoyo informativo','La decisión y firma permanecen en el profesional.'],
['Programar controles','Automatizada propuesta','INC-2: reglas verificadas y agenda.'],
['Administrar suplemento','Humana','La familia realiza la acción.'],
['Visitar y comunicar barreras','Asistida propuesta','INC-3/4: captura en campo y comunicación.'],
['Priorizar abandono','Asistida propuesta','INC-5: predicción explicable y revisada.'],
['Gestionar referencias','Asistida propuesta','Pendiente incorporar al backlog de evolución.'],
['Consolidar indicadores','Automatizada propuesta','INC-1 reporte básico; INC-6 gestión territorial.']],[160,115,230]),
h('Cadena de valor del PMV'),
p('Datos del niño → validación y persistencia → expediente consultable → el personal revisa antecedentes → organiza la atención → menor riesgo de decidir con datos incompletos. La reducción de errores, tiempo de registro o pérdida de seguimiento requiere comparación con una línea base.'),
tb(['Tipo','Indicador y cálculo','Estado y fuente'],[
['Proceso organizacional','Atendidos oportunamente / elegibles × 100.','Definido en S1. Sin medición en INC-1; requiere agenda.'],
['Producto','Intentos aceptados / intentos evaluados × 100.','24/28 = 85,7 % en captura sintética de Actividad 5, p. 10.'],
['Resultado','Recuperados / casos con control de cierre válido × 100.','Definido en S1. Sin seguimiento longitudinal acreditado.'],
['Valor','Casos sobre umbral sin cierre / casos con seguimiento × 100.','Definido en S1. Falta acordar umbral, cohorte y línea base.']],[95,230,180]),
note('La tasa de aceptación de intentos no equivale a calidad de registros persistidos ni a recuperación clínica. La cifra 85,7 % se conserva con su denominador explícito; no se presenta como impacto del sistema.'))

page(REPORT,'2.2 Selección y comparación del modelo de procesos',
tb(['Factor del proyecto','Nivel heredado de S2','Consecuencia para el proceso'],[
['Incertidumbre de requisitos','Alto','Refinar con usuarios; IA y comunicación evolucionan.'],
['Complejidad e integración','Alto','Probar límites entre componentes; integrar por incremento.'],
['Riesgo por conectividad','Alto','Diferenciar entorno local y operación móvil sin conexión.'],
['Datos e IA','Alto','Validar datos antes de INC-5; no bloquear el registro básico.'],
['Retroalimentación','Alto','Revisar funcionalidad con personal de salud y registrar decisiones.'],
['Automatización','Alto','Versionar build, pruebas, configuración y evidencias.']],[145,100,260]),
p('La valoración corresponde al proyecto completo. La incertidumbre de IA no obliga a implementar MLOps dentro de INC-1. El proceso se adapta a la funcionalidad efectivamente comprometida.'),
tb(['Enfoque','Adapt.','Riesgo','Increment.','Feedback','Autom.','Adecuac.','Total'],[
['Cascada','1','2','1','1','2','1','8'],['Incremental','3','3','4','3','2','3','18'],['Espiral','4','5','3','4','2','3','21'],['Scrum','5','4','5','5','3','5','27'],['Kanban','4','3','4','4','3','3','21'],['DevOps','4','4','5','4','5','4','26'],['MLOps/DataOps','4','4','4','4','5','5','26']],[115,50,50,60,62,55,60,53]),
p('Se conservan los puntajes de S2, sección 3, en escala de 1 a 5. Son juicios del equipo, no resultados experimentales. Cascada, Incremental y Espiral describen ciclos de vida; Scrum organiza trabajo y DevOps/MLOps aportan prácticas. Los puntajes no convierten esas categorías en alternativas equivalentes.'),
p('S2 seleccionó la combinación iterativa-incremental + Scrum + DevOps + MLOps (4,75), frente a Kanban + DevOps + DataOps (3,85) e Incremental + Espiral sin automatización (2,95). El 60 % del peso se asignó a adaptabilidad, riesgos, entrega y retroalimentación; el 40 % restante a integración, automatización, datos y participación.'),
p('Se mantiene la decisión por sus ciclos cortos de validación y control técnico. Cascada no se elige como base por la incertidumbre del alcance evolutivo; Scrum por sí solo no define pruebas ni despliegue. Kanban sí puede incorporar revisiones: la preferencia por Scrum responde a la cadencia acordada, no a una incapacidad de Kanban.'))

page(REPORT,'2.2 Modelo de proceso aplicado al proyecto',
fig('02_modelo_proceso','Figura 2. Ciclo adaptado que conserva los diez elementos de la guía de S2.',435),
p('Cada sprint se inicia con historias priorizadas y criterios verificables. Desarrollo y Calidad integran y prueban el código; Proceso coordina la revisión. Los hallazgos regresan al backlog y al trabajo de corrección. La entrega requiere satisfacer el DoD; el mero cierre de tareas no demuestra aceptación.'),
p('Para INC-1, la entrega documentada es de pruebas locales. La aceptación por una posta y el despliegue institucional son hitos separados. Desde INC-3 se incorporan pruebas de captura desconectada, reconciliación y pérdida de red; desde INC-5, evaluación y seguimiento del modelo.'))

page(REPORT,'2.3 Actividades y criterios de terminación',
tb(['Actividad y entrada','Producto y salida','DoD propuesto para INC-1'],[
['A1 Planificar y refinar\nBacklog y necesidad organizacional','Historias con criterios, tareas y estimación → compromiso de sprint.','Todas las historias tienen ID, aceptación, prioridad y responsable.'],
['A2 Diseñar\nHistorias acordadas','C4, ADR, esquema y contrato → diseño revisado.','Las tres vistas concuerdan y cada regla se vincula a un requisito.'],
['A3 Implementar\nDiseño y tareas','Código y cambios de BD → PR para revisión.','Funcionalidad completa, revisión por otro integrante, sin errores bloqueantes.'],
['A4 Verificar\nCódigo y criterios','Resultados por caso y cobertura → informe de calidad.','Casos críticos aprobados; cobertura ≥ 80 % con alcance explícito.'],
['A5 Integrar\nPR revisado','Build y análisis estático → artefacto identificable.','Pipeline verificable y sin errores críticos; herramientas equivalentes documentadas.'],
['A6 Entregar demostración\nArtefacto y BD de prueba','Aplicación local y smoke test → versión demostrable.','Arranque reproducible desde README y persistencia tras reinicio.'],
['A7 Revisar con usuario\nIncremento demostrable','Acta y observaciones → aceptación o correcciones.','Criterios contrastados con personal de salud; fecha y responsable del acta.'],
['A8 Medir y mejorar\nResultados y desviaciones','Tablero y retrospectiva → plan actualizado.','Diferenciar plan, ejecución y simulación; asignar acciones y fechas.']],[145,180,180]),
note('El umbral de cobertura se unifica en ≥ 80 %. S3-S4 usa 80 % en su DoD pero 70 % como umbral de bloqueo: esa brecha permitiría liberar una versión que no cumple su propio criterio. Aquí no se declara ningún hito completado sin su evidencia.'))

page(REPORT,'2.3 Responsabilidades y descomposición del trabajo',
p('Matriz RAE propuesta: E ejecuta, R revisa y A aprueba. Se separan las funciones que S3-S4 agrupaba en una sola columna. P = Porras; T = Auqui; J = Huamani. La aprobación académica interna no sustituye aceptación del usuario.'),
tb(['Actividad','E','R','A','Evidencia'],[
['A1 Planificación','P','T + J','P','Backlog y compromiso'],['A2 Arquitectura y contrato','T','J','P','C4, ADR y revisión'],['A3 Código','T','J','P','PR y commit'],['A4 Pruebas','J','T','P','Log, cobertura y defectos'],['A5 Integración','T','J','P','Ejecución CI'],['A6 Demostración local','T','J','P','Smoke test y versión'],['A7 Revisión funcional','P','J','Usuario designado','Acta; identidad y fecha pendientes'],['A8 Seguimiento','P','T + J','P','Tablero y retrospectiva']],[145,35,48,102,175]),
h('WBS del primer incremento'),
tb(['Épica e historia','Tareas del alcance integrado','SP de S3-S4'],[
['INC-1 / HIST-1.1','T1 formulario; T2 alta API; T3 interfaz; T4 rechazo de duplicados y aceptación.','5'],
['INC-1 / HIST-1.2','T5 consultar y actualizar; nuevas tareas: dosajes, historial y persistencia.','3'],
['INC-1 / HIST-1.3','T6 validar datos; probar límites y versión normativa.','3'],
['INC-1 / HIST-1.4','Completar WBS: listado, filtros y orden por clasificación actual.','2'],
['INC-1 / HIST-1.5','Completar WBS: rango de fechas, conteos y definición del indicador.','3'],
['INC-1 / infraestructura','T7 persistencia local; T8 CI; T9 análisis; T10 pruebas y cobertura.','5']],[140,315,50]),
p('Total heredado: 21 SP. El plan de S3-S4 estima 54 horas para Sprint 1, pero no desglosa todo el trabajo de reporte, filtros, actualización ni nuevas pruebas. Los SP no se convierten automáticamente en horas. Las tareas añadidas deben reestimarse; 54 horas no acredita el esfuerzo real de las cinco historias.'))

page(REPORT,'2.3 Priorización planificación y control',
p('Pesos de S3-S4: valor 30 %, reducción de riesgo 25 %, dependencia 20 %, complejidad inversa 15 % y validación 10 %. Se preservan los resultados para mantener la línea base.'),
tb(['Incremento','V / R / D / C / F','Puntaje','Calendario base'],[
['INC-1 Registro','5 / 4 / 5 / 4 / 5','4,60','Sprint 1-2 · 01-28 sep'],['INC-3 Sincronización','5 / 5 / 4 / 3 / 4','4,40','Sprint 4 · 13-26 oct'],['INC-2 Agenda','5 / 3 / 4 / 4 / 5','4,15','Sprint 3 · 29 sep-12 oct'],['INC-4 Mensajería','4 / 3 / 3 / 3 / 4','3,40','Sprint 5 · 27 oct-09 nov'],['INC-5 Modelo','5 / 4 / 2 / 1 / 3','3,35','Sprint 6-7 · 10 nov-07 dic'],['INC-6 Tablero','4 / 2 / 1 / 3 / 4','2,75','Sprint 7-8 · 24 nov-21 dic']],[125,125,65,190]),
p('Se conserva el calendario de la sección 11.1 de S3-S4 como línea base propuesta, con inicio de Sprint 1 el 01/09/2026. La fecha 20 de agosto del encabezado no coincide con la tabla. La agenda se mantiene antes de la sincronización únicamente para una demostración local; el despliegue rural queda condicionado a INC-3. Este criterio debe aprobarse como cambio explícito frente a la prioridad mayor de INC-3.'),
tb(['Desviación','Control y responsable','Registro pendiente'],[
['Flask/SQLite local frente a diseño móvil y central','P registra cambio; T delimita arquitectura; J ajusta pruebas.','Cambio CH-01 y aceptación de alcance.'],
['Reporte adelantado a INC-1','P compara Sprint Backlog y fecha real del commit.','CH-02; no dar por cumplida la aceptación de usuario.'],
['49 pruebas frente a 40 detalladas','J concilia IDs y ejecuciones antes de publicar indicadores.','Log completo y matriz corregida.'],
['Resultados de seguimiento simulados en S3-S4','P conserva el ejemplo separado de las métricas reales.','Backlog, horas y aceptación reales.']],[170,210,125]),
p('Seguimiento diario con bloqueo visible; revisión al cierre del sprint. Avance = SP aceptados / SP comprometidos × 100; esfuerzo = horas reales frente a estimadas; calidad = pruebas aprobadas, cobertura y defectos abiertos. Valores actuales: pendientes de evidencia. Se mantiene la duración de dos semanas y se renegocia alcance con el responsable del producto, en lugar de prolongar informalmente un sprint.'))

page(REPORT,'3 Unidad II Adaptación práctica del proceso',
h('3.1 Categorías y tailoring'),
p('Se usa la clasificación pedagógica exigida por la consigna. No se afirma certificación ni conformidad integral con una edición de ISO/IEC 12207 sin un mapeo específico de sus requisitos.'),
tb(['Categoría','Actividades del proyecto','Evidencia requerida'],[
['Principales','Definir requisitos, diseñar, construir, integrar, probar, entregar y preparar operación.','Historias, C4, ADR, código, pruebas y paquete de despliegue.'],
['Soporte','Documentación, configuración, verificación, revisiones y resolución de problemas.','Git, versiones normativas, PR, reportes y registro de defectos.'],
['Organizacionales y gestión','Planificación, seguimiento, infraestructura, capacitación y mejora.','Cronograma, RAE, desviaciones, material y retrospectiva.']],[120,220,165]),
tb(['Restricción','Adaptación documentada o propuesta','Efecto y control'],[
['Tres integrantes','Agrupar arquitectura, backend y frontend en Desarrollo.','Revisión independiente por Calidad; carga de trabajo visible.'],
['Primer incremento acotado','Aplicación local monolítica con organización hexagonal.','Menos operación distribuida; no declarar sincronización disponible.'],
['Entorno sin descarga de paquetes, según Actividad 5','unittest y scripts propios de lint/cobertura.','Conservar reportes y contrastar con herramientas estándar cuando estén disponibles.'],
['Conectividad rural','Diferir sincronización a INC-3.','Bloquea la aceptación de captura distribuida hasta sus pruebas.'],
['Norma cambia entre entregables','Versionar fuente, reglas y casos de límite.','Matriz de cambio normativo; recalcular solo con trazabilidad.'],
['Sin evidencias de aceptación de posta','Demostración local con datos sintéticos.','No etiquetar como producción, adopción o impacto real.'],
['Datos predictivos aún no acreditados','MLOps desde INC-5.','Evaluar etiquetas, representatividad y métricas antes de publicar modelo.']],[135,195,175]))

page(REPORT,'3.2 Arquitectura del primer incremento',
h('Decisiones arquitectónicas propuestas para formalización'),
tb(['ADR y estado','Contexto y decisión','Consecuencia y verificación'],[
['ADR-01\nDocumentar decisión existente','Equipo pequeño y alcance local. Mantener una aplicación Flask con UI y API en el mismo proceso; descartar microservicios para INC-1.','Reduce despliegues, pero concentra fallos. Arranque y smoke test; medir carga antes de uso concurrente.'],
['ADR-02\nDocumentar decisión existente','Variación futura de persistencia. Núcleo Python y puertos; adaptadores Web/REST, SQLite, normativa y reloj.','Facilita pruebas y sustitución. CP-30/31 y revisión de imports; cambiar adaptador no evita toda evolución del dominio.'],
['ADR-03\nDocumentar decisión existente','Demostración sin servidor central. Persistir en archivo SQLite.','Simplicidad local; no ofrece sincronización por sí mismo. Verificar reinicio, integridad y respaldo. PostgreSQL futuro requiere migración probada.'],
['ADR-04\nDocumentar decisión existente','Reglas y fuentes normativas variables. Configuración JSON versionada, separada de casos de uso.','Cambios auditables. Registrar versión por dosaje y probar límites; advertencia no acredita validez de una regla.'],
['ADR-05\nPropuesta de cierre','Separar demostración técnica de operación clínica. Mantener datos sintéticos en entorno local hasta aceptación.','Antes de uso institucional, definir autenticación, roles, protección de datos, respaldo y operación. No se acreditan en el PMV actual.']],[112,207,186]),
h('Atributos de calidad y escenarios'),
tb(['NFR','Escenario y criterio propuesto','Evidencia'],[
['Integridad','DNI duplicado: 409, sin segundo expediente.','CP-22 y consulta posterior.'],
['Mantenibilidad','Núcleo sin imports de Flask/SQLite ni adaptadores.','CP-30/31 + revisión de código.'],
['Rendimiento','Demostración: operaciones bajo 2 s. Carga: definir perfil y p95/RPS.','Smoke reportado; carga pendiente.'],
['Persistencia','Registrar, reiniciar y recuperar expediente y dosajes.','CP-17 y prueba reproducible.']],[105,275,125]))

page(REPORT,'3.2 Vista C4 de contexto',
fig('03_c4_contexto','Figura 3. C4 nivel 1. Actores que interactúan con el primer incremento documentado.',315),
p('El límite es el sistema PMV, no todo el proceso sanitario. El personal de salud opera el expediente y el coordinador revisa el reporte. El niño es beneficiario; no se dibuja como usuario de la interfaz. Familia, ACS, gestión territorial y MINSA permanecen como actores organizacionales del proyecto, pero sus interacciones digitales corresponden a evolución futura.'),
p('HIS y WhatsApp no se conectan en esta vista porque el avance no documenta integración operativa. Si se añade una vista del sistema objetivo, deberá llevar un título diferente y señalar cada incremento. El nombre “inteligente” del proyecto no demuestra IA implementada en INC-1.'),
h('Coherencia con las otras vistas'),
p('C4-1 abre el sistema a C4-2; C4-2 identifica la aplicación y el almacén; C4-3 descompone únicamente la aplicación. Los contenedores representan unidades de ejecución o almacenamiento, no necesariamente contenedores Docker. La vista de paquetes del avance se conserva como complemento de dependencias de código, no sustituye las tres vistas solicitadas. [R5-R7]'))

page(REPORT,'3.2 Vista C4 de contenedores',
fig('04_c4_contenedores','Figura 4. C4 nivel 2. Aplicación monolítica y archivo SQLite del primer incremento.',415),
p('Flask publica formularios renderizados con Jinja2 y operaciones REST/JSON. La base SQLite es un almacén embebido, accedido con sqlite3 dentro del proceso Python. No se dibuja una comunicación HTTP hacia SQLite ni se separa la plantilla HTML como un frontend independiente.'),
p('La normativa JSON es configuración de la aplicación; se detalla en componentes y despliegue. PostgreSQL, caché, API Gateway, microservicios, mensajería y modelo predictivo no se añaden para imitar el ejemplo de la consigna. Su incorporación debe responder a decisiones y funcionalidades reales.'),
note('La ausencia de esos componentes es coherente con un PMV local. Lo exigido es explicar las decisiones, protocolos y atributos de calidad del sistema elegido. Esta representación aún debe contrastarse con el código fuente.'))

page(REPORT,'3.2 Vista C4 de componentes',
fig('05_c4_componentes','Figura 5. C4 nivel 3. Llamadas entre componentes de la aplicación; organización propuesta a partir del avance.',520),
p('Las llamadas de ejecución y las dependencias de código son vistas distintas. El servicio invoca operaciones mediante puertos; los adaptadores dependen de esas interfaces. bootstrap ensambla las implementaciones. Una llamada desde el servicio al repositorio inyectado no implica importar sqlite3 dentro del núcleo.'),
p('Los nombres de los puertos proceden de la Figura 2 del avance. La vista agrupa normativa y reloj para mantener legibilidad; sus implementaciones permanecen separables. No se afirma que cada caja corresponda exactamente a un archivo.'))

page(REPORT,'3.2 Casos de uso del PMV',
fig('06_casos_de_uso','Figura 6. UML de casos de uso de INC-1. Validación incluida por alta, actualización y dosaje.',405),
tb(['Caso de uso','Historia relacionada'],[
['UC-01 Registrar niño','HIST-1.1 / HU-01'],['UC-02 Consultar y UC-03 Actualizar expediente; UC-04 Registrar dosaje','HIST-1.2 / HU-02'],['UC-07 Validar datos de entrada','HIST-1.3 / HU-03, requisito transversal'],['UC-05 Listar y filtrar','HIST-1.4 / HU-04'],['UC-06 Generar reporte','HIST-1.5 / HU-05']],[310,195]),
p('La asociación indica participación, no orden temporal. «include» apunta al comportamiento obligatorio incluido. El sistema no es actor de sí mismo. No se incluye sincronización ni riesgo de abandono en este alcance.'))

page(REPORT,'3.2 Especificación funcional y reglas de alcance',
tb(['Caso y precondición','Flujo y resultado','Alternativas y aceptación'],[
['UC-01 Registrar niño\nPersonal en entorno de prueba','Capturar datos → validar → comprobar identidad → guardar → confirmar. HIST-1.1/1.3.','Datos inválidos: 400 sin expediente; DNI existente: 409. Dosaje inicial opcional, sin inventar historial.'],
['UC-02/03 Expediente\nIdentificador existente','Consultar datos y dosajes; actualizar campos permitidos conservando identidad e historial. HIST-1.2.','No encontrado: confirmar contrato. Campos no editables: rechazar; ninguna actualización altera dosajes anteriores.'],
['UC-04 Dosaje\nExpediente existente','Capturar fecha y Hb → validar → aplicar regla versionada → conservar nuevo evento. HIST-1.2/1.3.','Dato inválido: rechazar. Bandas no verificadas: no considerar la clasificación validada.'],
['UC-05 Seguimiento\nRegistros disponibles','Filtrar por distrito, clasificación y texto; ordenar por severidad actual. HIST-1.4.','La falta de dosaje no equivale a “sin anemia”. Fuera de 6-59 meses: explicitar estado y conservar expediente.'],
['UC-06 Reporte\nPeriodo definido','Calcular conteos y aceptación de intentos con denominador explícito. HIST-1.5.','Cero intentos: “no calculable”; evitar 0 % o 100 % sin denominador. Fechas inválidas: error claro.']],[135,185,185]),
h('Correcciones de trazabilidad funcional'),
p('HIST-1.3 se redacta desde el personal de salud: “Como personal de salud, quiero que el sistema valide los datos ingresados para corregir errores antes de guardar”. Se conserva su ID y se reconoce que es una condición transversal de varios casos de uso.'),
p('HIST-1.4 cambió de “estado de control” a “clasificación de hemoglobina”. Se propone registrar CH-03: INC-1 muestra clasificación actual; cumplimiento y vencimiento de controles se mantienen en INC-2. Ordenar severidad de anemia no implementa una predicción de abandono.'),
p('S1 incluye menores de cinco años y seguimiento preventivo desde edades tempranas; el listado documentado filtra 6-59 meses. Debe explicarse la distinción entre registrar al niño y mostrarlo en esa lista, con pruebas de frontera por edad.'))

page(REPORT,'3.2 Modelo de datos y contratos de interfaz',
fig('08_modelo_datos','Figura 7. Entidades documentadas, con un niño relacionado con cero o más dosajes.',330),
p('La cardinalidad admite que el alta no contenga dosaje. Cada dosaje pertenece a un niño. intento_registro conserva resultados de captura sin duplicar datos personales; no se inventa una FK al expediente, pues un intento rechazado puede no crear ninguno. Los rangos y CHECK exactos deben verificarse contra db/schema.sql.'),
tb(['Operación documentada','Ruta o dato disponible','Respuesta reportada'],[
['Alta','POST /api/v1/ninos','201; 400; 409'],['Consulta y edición','GET y PATCH /api/v1/ninos/{dni}','200; errores por confirmar en contrato'],['Listado','GET /api/v1/ninos','200 y filtros'],['Nuevo dosaje','Ruta exacta pendiente de docs/openapi.yaml','Por contrastar con implementación'],['Reporte','GET /api/v1/reportes/registros','200 y conteos'],['Salud','GET /api/v1/salud','Respuesta de arranque reportada']],[125,235,145]),
note('El texto “5 endpoints, más el reporte” no identifica inequívocamente operaciones frente a rutas. La evidencia final debe adjuntar OpenAPI real con métodos, esquemas, campos obligatorios, ejemplos, errores y parámetros. No basta validar que una ruta exista.'))

page(REPORT,'3.2 Interacción del registro y evolución del diseño',
fig('09_secuencia_registro','Figura 8. Secuencia conceptual de alta válida e inválida. Debe contrastarse con los métodos reales.',460),
p('La aplicación devuelve errores de captura antes de crear un expediente. El conflicto por identidad debe ser controlado también en la persistencia. La clasificación, si existe dosaje, usa la normativa versionada; no invoca un modelo predictivo.'),
p('Para INC-3 se requiere una secuencia diferente: identificación de eventos, captura local, envío, aceptación idempotente, detección de conflictos y confirmación de sincronización. La política “gana la última marca de tiempo” de S2 es insuficiente sin reglas de reconciliación y conservación del historial. Esa funcionalidad no aparece entregada en esta secuencia.'))

page(REPORT,'3.3 Estrategia y ejecución de pruebas',
p('La pirámide propuesta concentra las validaciones en pruebas unitarias, verifica persistencia y contratos mediante integración, y reserva E2E para los recorridos críticos. La carga se prueba sobre un servidor real con concurrencia definida. Los resultados siguientes son declaraciones del avance, no ejecuciones realizadas durante esta revisión.'),
tb(['Nivel','Casos documentados y resultado','Brecha para cierre'],[
['Unitarias','CP-01 a CP-07: 7/7. Formatos, fechas y reglas.','Adjuntar casos con entradas, esperado y observado.'],
['Aplicación con repositorios','CP-08 a CP-15: 16/16 al duplicar memoria/SQLite.','Separar IDs de casos lógicos y ejecuciones parametrizadas.'],
['Persistencia','CP-16 a CP-19 y CP-32: 5/5.','DDL, reinicio e integridad verificables.'],
['API','CP-20 a CP-25: 6/6 con cliente de prueba.','Adjuntar contrato y validar también cuerpos/respuestas.'],
['UI y rendimiento básico','CP-26 a CP-29: 4/4. Formularios y operaciones secuenciales.','Cliente Flask y HTML no acreditan E2E en navegador ni concurrencia.'],
['Arquitectura','CP-30 y CP-31: 2/2.','Adjuntar prueba AST y límites de su análisis.'],
['Carga y E2E','No se identifican resultados completos.','Ejecutar y conservar reportes.']],[112,235,158]),
h('Registro de resultados documentados'),
tb(['Métrica','Valor reportado','Interpretación'],[
['Total automatizado','49 pruebas','La suma de la tabla es 40: falta mapear 9 ejecuciones.'],
['Cobertura','1038/1083 = 95,8 %','Verificar archivos incluidos, exclusiones y herramienta.'],
['Análisis estático','0 hallazgos de tools/lint.py','No equivale a 0 Blocker/Critical de SonarCloud.'],
['Smoke test','13 verificaciones; máximo 25,8 ms','No es p95 ni throughput bajo carga.'],
['Datos del reporte','24 niños, 23 dosajes, 28 intentos, 4 rechazados','Captura p. 10. Conciliar con la siembra que declara 3 inválidos.']],[120,175,210]))

page(REPORT,'3.3 Pruebas pendientes y gestión de defectos',
tb(['Caso propuesto','Preparación y acción','Aceptación y evidencia'],[
['P-01 E2E registro','Navegador real y BD temporal. Crear niño válido, consultar, actualizar y recargar.','Persisten cambios e historial; traza o video y versión. Estado: pendiente.'],
['P-02 E2E rechazo','Enviar DNI duplicado y valores inválidos desde navegador y API.','Mensaje por campo; sin nuevo expediente; 400/409 según contrato. Pendiente.'],
['P-03 Rendimiento','Perfil propuesto: 10 usuarios, 5 min, 80 % consultas / 20 % altas con identidades únicas, tras calentamiento.','Registrar entorno, solicitudes, errores, p95 y RPS. Meta propuesta: p95 < 2 s y errores inesperados < 1 %. Pendiente de acuerdo y ejecución.'],
['P-04 Integridad','Dos altas concurrentes con mismo DNI en servidor real.','Una alta y un conflicto; solo un expediente. Pendiente.'],
['P-05 Normativa','Tabla versionada y valores frontera por edad y altitud; fuente oficial adjunta.','Coinciden ajuste y clasificación esperados; no validar bandas por mera advertencia. Pendiente.'],
['P-06 Indicadores','Periodo vacío; 24 aceptados + 4 rechazados; intento con dos errores.','No calculable si n=0; 85,7 % para 24/28; contar intentos y errores por separado. Pendiente.']],[112,205,188]),
h('Registro de defectos de esta revisión'),
tb(['ID y prioridad','Hallazgo','Cierre requerido'],[
['D-01 Alta','Total de pruebas no reconciliado.','Matriz y log coincidentes; J revisa.'],['D-02 Alta','Altitud de dominio y CHECK no coinciden en PDF.','Comparar formulario, dominio y DDL; T corrige y J prueba.'],['D-03 Alta','Sin prueba E2E/carga acreditada.','Ejecutar P-01 a P-04 y adjuntar reportes.'],['D-04 Media','Indicador mezclado con valor organizacional.','Definir denominadores; P revisa redacción y J prueba.']],[110,215,180]),
p('Cada ejecución debe registrar ID, fecha, commit, entorno, datos, resultado esperado, resultado real, estado, evidencia y defecto asociado. El cierre de un defecto requiere reproducción y repetición de los casos afectados.'))

page(REPORT,'3.4 Despliegue y demostración del primer incremento',
fig('07_despliegue','Figura 9. Entorno local descrito en Actividad 5, sin atribuir operación en una posta.',285),
p('El avance describe Flask/Werkzeug, un archivo SQLite y un navegador. El esquema representa esa demostración local. Un teléfono accediendo al servidor por red no significa que el teléfono almacene datos o pueda trabajar desconectado. La exposición puede demostrar un entorno de pruebas; el despliegue institucional necesita su propia evidencia.'),
tb(['Paso de demostración','Verificación','Evidencia disponible'],[
['Abrir aplicación y listar','Seguimiento, filtros y clasificación con texto.','Captura de Actividad 5, p. 7.'],['Registrar datos inválidos','Mensajes por campo sin perder campos válidos.','Captura p. 8.'],['Consultar expediente','Historial y advertencia de altitud.','Captura p. 9.'],['Consultar reporte','24/28 intentos aceptados, 85,7 %.','Captura p. 10.'],['Verificar ancho móvil','Formulario a 420 px.','Captura p. 11; no acredita operación offline.'],['Repetir ejecución','README, siembra, pruebas, cobertura y smoke.','Comandos mencionados, archivos no disponibles para esta revisión.']],[132,195,178]),
p('Guion operativo: arrancar una BD de prueba limpia, crear un niño, intentar duplicarlo, consultar y actualizar su expediente, registrar dosaje, filtrar y revisar el reporte. Usar una identidad diferente en cada repetición o restaurar la BD. Registrar commit y fecha; conservar el historial de intentos sin confundirlo con el número de niños.'))

page(REPORT,'4 Trazabilidad integral del proceso y generación de valor',
p('Cada fila conecta una brecha con el proceso adaptado, actividad, arquitectura, prueba, producto y medición. Los casos CP conservan los IDs del avance; su ejecución permanece pendiente de contraste con el repositorio.'),
tb(['Problema y TO-BE','Proceso y actividad','Arquitectura y prueba','PMV e indicador'],[
['B1 Datos duplicados → registro validado','Iterativo + DevOps; principal A3 y soporte A4','ADR-02/03; UC-01; CP-08/22; P-04','HIST-1.1: expediente único por DNI. Duplicados rechazados; no elimina HIS.'],
['B1 Datos inválidos → validación de captura','Refinamiento y verificación A1/A4','ADR-04; UC-07; CP-01 a 07/21','HIST-1.3: errores por campo. Intentos aceptados/evaluados.'],
['B1 Antecedentes dispersos → expediente','Iteración con revisión; A3/A7','ADR-02/03; UC-02 a 04; CP-10 a 12/17','HIST-1.2: datos e historial. Persistencia y tiempo de consulta.'],
['B5 Información de atención poco visible → listado','Tailoring de alcance; A1/A2','ADR-01; UC-05; CP-14/24/28','HIST-1.4: clasificación actual. No mide predicción de abandono.'],
['B6 Consolidación tardía → reporte local','Medición y revisión A7/A8','ADR-03; UC-06; CP-15/32 y P-06','HIST-1.5: conteos sintéticos. 85,7 % de aceptación, sin comparación clínica.'],
['B2/B3/B4/B6 → agenda, comunicación, campo y tablero','Backlog posterior y gestión de dependencias','INC-2/3/4/6; pruebas específicas futuras','Funcionalidades pendientes; oportunidad y continuidad todavía no medidas.'],
['B5 → riesgo de abandono','MLOps propuesto desde INC-5','Modelo supervisado y evaluación temporal futura','Predicción pendiente; requiere etiquetas de abandono/no recuperación.']],[133,118,124,130]),
h('Continuidad que debe restituirse en el backlog'),
p('S1 también exige visitas y consumo de suplementos, referencia hasta cierre, captura local cifrada y trazabilidad temporal. Estas necesidades no quedan satisfechas por las cinco historias de INC-1. Se propone añadir historias explícitas o registrar su exclusión aprobada, manteniendo relación con el actor, brecha e indicador original.'),
p('Las metas de S3-S4 sobre cobertura oportuna (+15 %) y pérdida de seguimiento (-20 %) son propuestas posteriores a S1, donde no se fijaron metas. No deben presentarse como acuerdos institucionales ni como resultados hasta definir línea base, cohorte, periodo y modo de cálculo.'))

page(REPORT,'5 Conclusiones y lecciones aprendidas',
h('Tres conclusiones técnicas'),
p('1. El registro nominal y el expediente mantienen el núcleo del primer incremento planificado. La organización hexagonal es compatible con un monolito Flask/SQLite y puede describirse mediante C4. Las vistas de ejecución, dependencias y despliegue deben conservar su propósito para evitar atribuir al PMV infraestructura futura.'),
p('2. La evidencia del avance permite describir funcionalidades y resultados reportados, pero no cerrar su verificación reproducible. La conciliación de 49 pruebas con las 40 ejecuciones detalladas, los reportes de cobertura y la ejecución E2E/carga son necesarios para demostrar cumplimiento del DoD.'),
p('3. El indicador 24/28 describe aceptación de intentos sintéticos. El valor organizacional de S1 requiere seguimiento longitudinal y comparación con línea base. La clasificación actual de hemoglobina no demuestra predicción de abandono ni reducción de anemia.'),
h('Tres lecciones del control y adaptación documental'),
p('1. Un cambio tecnológico debe registrarse junto con su impacto en historias, pruebas e hitos. La transición de PWA/SQLite local y servidor central a Flask/SQLite de demostración necesita una decisión explícita; mantener la misma etiqueta “offline” oculta funcionalidades pendientes.'),
p('2. Conservar un ID no basta si cambia su significado. HIST-1.4 debe distinguir estado de control de clasificación actual, y HIST-1.5 debe conservar el denominador de su indicador. La trazabilidad exige equivalencia semántica, además de referencias cruzadas.'),
p('3. Planes, simulaciones y ejecuciones deben registrarse por separado. Los ejemplos de seguimiento de S3-S4 no acreditan horas consumidas ni aceptación real. El avance de un hito requiere un producto verificable y evidencia de revisión, no solo una conclusión redactada.'),
h('Siguiente incremento'),
p('La línea base sitúa INC-2 como agenda de controles y alertas internas. Antes de implementarlo se debe validar la normativa aplicable, definir la entidad ControlProgramado, la regla de vencimiento y sus pruebas. La captura móvil desconectada y la sincronización siguen en INC-3; su prioridad operativa debe revisarse antes de cualquier piloto rural.'))

page(REPORT,'6 Anexos repositorio y fuentes',
tb(['Elemento de entrega','Contenido requerido','Estado'],[
['Repositorio GitHub/GitLab','URL verificable, código, dependencias, pruebas y configuración.','Enlace pendiente.'],['Tag v1.0-PMV','Versión ligada al commit de las evidencias.','Pendiente de identificar.'],['README.md','Requisitos, instalación, configuración, inicialización de BD, ejecución, pruebas y reinicio.','Mencionado en avance; archivo pendiente.'],['Base de datos','db/schema.sql, siembra sintética y migración documentada.','Mencionados; pendientes.'],['Contrato','docs/openapi.yaml y ejemplos válidos/errores.','Pendiente de adjuntar y comprobar.'],['Pruebas y calidad','Logs, cobertura, análisis, E2E, carga y defectos.','Resumen documental parcial.'],['Defensa','Exactamente 7 diapositivas y demo ejecutable.','Guion propuesto en material complementario; presentación pendiente.'],['Aceptación','Acta de revisión y criterios satisfechos.','No acreditada.']],[118,270,117]),
h('Referencias documentales'),
p('[R1] Consigna S6 e instrumento integrador, pp. 1-9. [R2] Entregable Semana 1, v5, secciones 1-11. [R3] Entregable Semana 2, v2, secciones 1-10. [R4] Entregable Semanas 3 y 4, v1, secciones 3-20. [R8] Informe Actividad 5 PMV Anemia Junín, pp. 1-12. Todos son documentos del equipo o del curso disponibles en la carpeta de trabajo.'),
p('[R5] C4 Model, Diagrams: https://c4model.com/diagrams . [R6] C4 Model, Notation: https://c4model.com/diagrams/notation . [R7] C4 Model, Component diagram: https://c4model.com/diagrams/component . Consultados el 25/09/2026.'),
p('[R9] OMG, UML 2.5.1: https://www.omg.org/spec/UML/2.5.1 . [R10] MINSA, RM 251-2024: https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa . [R11] MINSA, RM 429-2024: https://www.gob.pe/institucion/minsa/normas-legales/5670414-429-2024-minsa .'),
p('La RM 429-2024 modifica la NTS 213 aprobada por RM 251-2024. La sustitución de las reglas citadas como NTS 134 en S1-S4 necesita una matriz regla-fuente-versión-prueba. Este informe no certifica la implementación clínica ni reproduce como validadas las tablas históricas.'))

page(AUDIT,'Revisión de cumplimiento y errores de trazabilidad',
p('Proyecto Anemia Junín · Consigna integradora S6 · Corte documental del 25 de septiembre de 2026'),
note('Dictamen: Informe_Actividad5_PMV_AnemiaJunin.pdf NO cumple por sí solo toda la consigna integradora. Es un avance técnico reutilizable para INC-1, pero no integra de forma suficiente S1-S7 ni acredita todas las evidencias de la entrega. No se asigna nota porque faltan código, defensa y validación de resultados.'),
p('Se revisaron la consigna completa, Actividad 5, S1 v5, S2 v2, S3-S4 v1, las guías S2/S3-S4 y la guía local de UML. La incorporación de S1 permite comprobar la cadena desde el problema original. Las cifras del PMV se consideran reportadas; no se recibió el repositorio para ejecutarlas.'),
tb(['Área de la rúbrica','Diagnóstico del avance','Acción principal'],[
['Proceso organizacional y modelo · 2 puntos','Faltan AS-IS/TO-BE, brechas, actores, factores y comparación integrados.','Recuperar S1/S2 y corregir alcance y valor.'],['Actividades y planificación · 2 puntos','Referencias a S3-S4 sin RAE, WBS, estimación ni seguimiento completos.','Integrar matrices y registrar cambios frente al plan.'],['Categoría, arquitectura y pruebas · 2 puntos','Hexagonal, ER y pruebas parciales; faltan C4-1/2/3, ADR y evidencia completa.','Completar diseño, conciliar pruebas y verificar repositorio.'],['Trazabilidad y valor · 2 puntos','Persisten cambios semánticos y valor sobreatribuido al registro.','Vincular brecha-HU-ADR-CP-indicador con estado de evidencia.'],['Exposición y defensa · 12 puntos','No hay presentación ni demostración verificable disponibles.','7 diapositivas, demo y dominio individual.']],[125,215,165]),
h('Cómo leer las observaciones'),
p('Crítico: puede invalidar la cadena requisito-producto-resultado. Alto: impide demostrar un requisito o una decisión. Medio: reduce precisión o legibilidad. “No acreditado” significa falta de evidencia disponible, no prueba de que el equipo nunca lo haya realizado.'))

page(AUDIT,'Matriz de cumplimiento de la consigna',
tb(['Requisito S6','Estado en Actividad 5','Qué falta o debe corregirse'],[
['Portada y resumen ≤ 300 palabras','Parcial','Portada de Actividad 5; sin resumen integrador, códigos, docente y fecha de entrega.'],['2.1 Actores, AS-IS, ≥5 brechas y TO-BE','Ausente','Integrar S1, conservando responsables y alcance organizacional.'],['2.1 Intervención y cuatro tipos de indicadores','Parcial','El reporte sintético cubre producto; no resultado ni valor real.'],['2.2 Factores, comparación y tailoring','Parcial','El enfoque se nombra; faltan matrices y diagrama aplicado.'],['2.3 Actividades, entradas/productos/salidas, RAE y DoD','Parcial','DoD técnicos por componente; falta proceso completo y RAE separado.'],['2.3 WBS, estimación, prioridad, plan y seguimiento','Ausente en informe','Se citan secciones anteriores sin integrar contenido ni cambios.'],['3.1 Categorías y adaptación','Parcial','Se justifica cambio de herramientas; no existe matriz completa.'],['3.2 ADR, C4-1/2/3, datos y API','Parcial','Paquetes y despliegue no sustituyen C4. ER presente, OpenAPI solo mencionado.'],['3.3 Unitarias, API, carga, E2E, cobertura y defectos','Parcial','Pruebas reportadas; faltan detalle conciliado, reportes, carga y navegador real.'],['3.4 Despliegue y demostración','Parcial','Capturas presentes; entorno local. Falta reproducción del ejecutable.'],['4 Trazabilidad integral','Ausente','Falta matriz completa desde problema hasta medición.'],['5 Tres conclusiones y tres lecciones','Parcial','Conclusión y siguiente incremento; no estructura solicitada.'],['6 Repositorio, README, scripts y tag','No acreditado','No hay URL ni tag verificable. Archivos solo referidos.'],['Presentación de 7 diapositivas','No disponible','Obligatoria además del informe.']],[190,100,215]),
p('La versión integrada adjunta completa la organización documental y propone correcciones. No convierte automáticamente en cumplidos los requisitos que dependen de código, mediciones reales o aceptación externa.'))

page(AUDIT,'Errores críticos que rompen la trazabilidad',
tb(['ID y ubicación','Ruptura y consecuencia','Corrección concreta'],[
['T01 · S1 §6.4; S2 §9; S3-S4 §3/7/8; A5 pp. 3-4','PWA con captura local y sincronización central cambia a Flask/SQLite servidor. “Funciona local” no demuestra captura móvil offline.','CH-01: formalizar demostración local para INC-1; mantener cifrado, cola y sincronización en INC-3 con pruebas nuevas.'],
['T02 · S1 §5/6/7; S2 §7; A5 p. 12','Se afirma eliminar triple registro sin integración HIS ni acuerdo de sustitución del proceso. Un registro adicional puede incluso sumar digitación.','Reescribir como expediente validado dentro del PMV. Medir duplicidad operativa y validar cambio institucional antes de atribuir eliminación.'],
['T03 · S1 §6.2; S3-S4 §8; A5 p. 2','Riesgo predictivo de abandono se confunde con severidad de última Hb. HIST-1.4 pasa de estado de control a clasificación.','CH-03: separar clasificación actual (INC-1), vencimiento de controles (INC-2) y predicción de abandono (INC-5).'],
['T04 · S1 §6/7/8; WBS S3-S4 §8','Referencias hasta cierre, visitas, consumo/adherencia y cifrado local no tienen cobertura explícita en historias del WBS.','Crear historias y criterios o exclusión aprobada. No cerrar sus indicadores por entregar el registro nominal.'],
['T05 · S1 §8; S3-S4 §15; A5 pp. 10/12','24/28 mide aceptación de intentos sintéticos, no calidad de todos los datos persistidos ni reducción del abandono.','Definir población, unidad, denominador y periodo; clasificarlo como producto. Conservar valor clínico como no medido.'],
['T06 · S1 §6.1; S2/S3-S4; A5 pp. 5/12','Cambio NTS 134 → NTS 213 y modificación 429 sin matriz de reglas. “134/213” deja ambigua la versión.','CH-04: identificar fuente y regla aplicada; versionar configuración y casos frontera; retirar el nombre ambiguo.']],[135,205,165]),
p('La actualización normativa puede ser correcta y necesaria; el error de trazabilidad es dejar requisitos y pruebas atados a versiones diferentes sin documentar la transición. No se preservan reglas antiguas por mera continuidad.'))

page(AUDIT,'Inconsistencias de evidencia planificación e indicadores',
tb(['ID y ubicación','Problema comprobable','Corrección y prioridad'],[
['T07 · A5 p. 6','7 + 16 + 5 + 6 + 4 + 2 = 40; se declaran 49. Casos con sufijo b figuran en p. 2 pero no se concilian.','Alta. Enumerar todas las ejecuciones; no asumir que son falsas ni que los sufijos explican exactamente las 9.'],
['T08 · A5 p. 10/12','Captura: 28 intentos y 4 rechazados. Siembra descrita: 24 niños + 3 inválidos.','Alta. Explicar secuencia de siembra/demo. Un intento puede tener varios errores; no sumar códigos como intentos.'],
['T09 · A5 p. 2 y Figura 4 p. 5','Texto: altitud 0-4999; ER: CHECK 0-6000.','Alta. Contrastar UI, dominio, JSON y DDL. Añadir pruebas de 4999/5000 y rango admitido; no escoger arbitrariamente un máximo.'],
['T10 · A5 pp. 6/12','25,8 ms es máximo de smoke. 60 operaciones secuenciales no prueban carga. HTML con cliente de test no prueba navegador E2E.','Alta. Reportar herramientas, concurrencia, duración, p95, RPS y errores; ejecutar recorrido con navegador.'],
['T11 · S3-S4 §11.1/20; A5 p. 12','Historia 1.2 y 1.4 en Sprint 2 en tabla; en Sprint 1 en plan ejecutable. “Inicio 20 agosto” frente a 1 septiembre.','Alta. Fijar una línea base y registrar cambios por historia y fecha; no mezclar tres calendarios.'],
['T12 · S3-S4 §14/17','16 SP, 58 horas y reunión de seguimiento son ejemplos/simulación.','Crítica si se usan como resultados. Obtener horas y SP reales; mantener simulación etiquetada.'],
['T13 · S3-S4 §6/16','DoD cobertura ≥80 %, pero bloqueo solo bajo 70 %.','Alta. Bloquear si no cumple ≥80 % o modificar DoD explícitamente.'],
['T14 · S1 §8; S3-S4 §15','S1 no fija metas. S3-S4 incorpora +15 %, -20 %, precisión ≥75 % y acción <70 % sin aceptación mostrada.','Alta. Etiquetar metas propuestas, establecer línea base y separar precisión/recall del modelo futuro.']],[130,205,170]))

page(AUDIT,'Correcciones de diagramas UML y arquitectura',
tb(['Diagrama y fuente','Error o límite','Cómo corregir'],[
['S1 Figura 7 · Casos de uso','“Sistema inteligente (IA + Web/App)” es actor del propio sistema. Se incluyen sincronización y predicción como si siempre formaran parte de registrar.','Actores externos al límite. PMV separado de visión futura. Sincronización no es obligatoria en cada registro; modelarla según eventos/conectividad.'],
['S1 Figura 7 · Relaciones','Hay flechas de actor a caso que pueden leerse como flujo; no se identifican claramente todos los estereotipos y condiciones.','Asociaciones simples sin dirección para evitar ambigüedad; «include» al caso incluido; «extend» al base con condición y punto de extensión.'],
['S1 Figura 8 · Clases','Niño y ModeloPredictivo con cardinalidad 1 a 1; confunde modelo entrenado compartido con predicción individual.','Niño 1 → 0..* PrediccionRiesgo; ModeloPredictivo 1 → 0..* PrediccionRiesgo. Evaluar por separado historia y versión.'],
['S1 Figuras 2/4 · Procesos','Mezclan flechas discontinuas entre carriles y decisiones sin leyenda formal. En TO-BE la entrada se ve como familia, personal y luego sistema separados.','Conservar decisiones y carriles; definir UML o BPMN. En UML, flujo de control sólido aunque cruce carriles; no confundir mensajes con control.'],
['A5 Figuras 1/2','Paquetes e imports explican hexagonal, pero no son las vistas C4-1/2/3 exigidas.','Añadir C4 por nivel y alcance. Hexagonal organiza dependencias internas; C4 comunica estructura. Son compatibles.'],
['A5 Figura 3','El despliegue mezcla entorno local, CI y extensiones futuras con texto muy pequeño.','Diagrama del PMV local separado del objetivo futuro. CI es entorno de construcción; no componente clínico de ejecución.'],
['Guía UML local D3','Indica punteada = asíncrona o retorno; prescribe sobrescribir por marca de tiempo.','En UML, retorno discontinuo; mensaje asíncrono sólido con punta abierta. Diseñar reconciliación sin pérdida antes de formalizar offline.'],
['Guía UML D1 y D2','Sugiere SMS como extensión de enviar por WhatsApp y MLOps desde Sprint 5 sin alinear calendario.','Modelar “Notificar familia” con canales alternativos según diseño; distinguir preparación de datos y ejecución de INC-5.']],[130,190,185]),
p('Las vistas nuevas son especificaciones coherentes con el PMV descrito; no se presentan como ingeniería inversa del código ausente. La fuente SVG permite modificar cajas y textos sin generar una imagen por IA.'))

page(AUDIT,'Cambios adicionales y orden de cierre',
tb(['Hallazgo','Reparación necesaria'],[
['Prioridad INC-3 = 4,40 mayor que INC-2 = 4,15, pero agenda va antes','Explicar demostración local, o reordenar el piloto rural. No decir que la matriz determina automáticamente el calendario.'],
['S3-S4 §12 atribuye dependencia de WhatsApp a INC-5','Mover dependencia principal a INC-4; exigirla en INC-5 solo si una variable necesita datos de ese canal.'],
['S1 alcance <5 años frente a lista 6-59 meses del PMV','Diferenciar alta, clasificación y seguimiento visible. Especificar atención preventiva fuera del listado y pruebas de borde.'],
['S3-S4 54 horas no cubren todas las tareas del INC-1','Añadir filtros, reporte, dosajes, pruebas y documentación al WBS y reestimar.'],
['“Sin modificar núcleo” al añadir agenda en A5 p. 12','La reutilización del puerto ayuda, pero nuevas reglas y entidades pueden exigir ampliar aplicación y dominio.'],
['DDL “portable a PostgreSQL” solo probado en SQLite','No afirmar portabilidad verificada; probar migración, tipos y restricciones en PostgreSQL al implementarlo.'],
['Tabla 1 normativa con bandas no verificadas','La RM 429-2024 publica los valores. Contrastar configuración y pruebas con la fuente; una alerta no reemplaza esa comprobación.'],
['S6: 7 minutos globales, pitches individuales suman 10','Preparar 7 minutos como límite principal y confirmar la contradicción con el docente. Propuesta de tiempos en guion.']],[205,300]),
h('Orden recomendado para cerrar la entrega'),
p('1. Acordar CH-01 a CH-04 y el alcance por incremento. 2. Corregir historias y necesidades de S1 sin cobertura. 3. Incorporar C4/ADR/UML y contrato real. 4. Identificar repositorio y tag, ejecutar pruebas y conciliar cifras. 5. Obtener aceptación de usuario y métricas con denominador verificable. 6. Preparar exactamente siete diapositivas y ensayar la demo.'),
p('La consigna solicita informe PDF, presentación PDF/PPTX y enlace al repositorio. Los diagramas de casos de uso responden además a la solicitud del equipo y a la continuidad de S1; no reemplazan los C4 exigidos en S6.'))

page(AUDIT,'Trazabilidad normativa y fuentes de revisión',
p('La revisión se concentra en ingeniería del software y consistencia documental. No valida un algoritmo clínico. El cambio de fuente normativa debe reflejarse en los requisitos, configuración, etiquetas de la interfaz, reglas de cálculo y casos de prueba.'),
p('La RM 429-2024 modifica la NTS 213 aprobada por RM 251-2024. Su tabla de ajuste documenta 2,9 g/dL para 4000-4499 msnm y 3,3 g/dL para 4500-4999 msnm. Estos datos permiten cerrar la consulta documental que el avance dejó pendiente; falta comprobar el JSON y el comportamiento del programa. Fuente: https://bvs.minsa.gob.pe/local/fi-admin/RM-429-2024-minsa.pdf .'),
h('Fuentes principales'),
p('S6, pp. 1-6: entregables y estructura. S6, pp. 7-9: rúbrica. Actividad 5, pp. 2-6: requisitos, diseño y pruebas; pp. 7-11: capturas; p. 12: demostración y conclusiones. S1, secciones 4-9: brechas, intervención, indicadores y UML. S2, secciones 3-10: modelo y trazabilidad. S3-S4, secciones 6-20: DoD, WBS, calendario y seguimiento.'),
p('C4 Model: https://c4model.com/diagrams ; https://c4model.com/diagrams/notation ; https://c4model.com/diagrams/component . Se consultaron para mantener alcance, jerarquía, relaciones y tecnologías de las vistas.'),
p('OMG UML 2.5.1: https://www.omg.org/spec/UML/2.5.1 . MINSA RM 251-2024: https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa . MINSA RM 429-2024: https://www.gob.pe/institucion/minsa/normas-legales/5670414-429-2024-minsa .'),
h('Límites de la revisión'),
p('No se recibió código, OpenAPI, DDL, logs, acta ni presentación. Tampoco se dispone de la transcripción de entrevista de S1. Por ello, las afirmaciones sobre entrevista se atribuyen al entregable, y las métricas de Actividad 5 se conservan como reportadas. No se vuelve a publicar la prevalencia ENDES 2025 sin comprobar el cuadro y la población exactos.'),
p('Los archivos originales se conservan. El informe integrado es una propuesta de cierre documental; las decisiones nuevas y evidencias pendientes están identificadas para que no se confundan con trabajo ya ejecutado.'))
