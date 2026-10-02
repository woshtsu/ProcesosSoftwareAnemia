# Prompts para revisar o redibujar los diagramas

Los SVG y PNG de la carpeta `diagramas` ya están generados. Los SVG conservan texto y formas vectoriales; los PNG son para insertar en Word o presentaciones. No requieren generación de imágenes por IA. Son modelos basados en los documentos, pendientes de contraste con el código.

## Prompt de revisión contra el repositorio

Actúa como revisor de arquitectura y UML. Adjuntaré el repositorio del PMV Anemia Junín, su Informe de Actividad 5, el informe integrado y nueve diagramas SVG. Primero inspecciona el código, db/schema.sql, docs/openapi.yaml, pruebas y configuración. No supongas que lo declarado en el PDF está implementado. Construye una tabla “elemento del diagrama → archivo y símbolo real → discrepancia → corrección”. Verifica las vistas C4 de contexto, contenedores y componentes, la dirección de dependencias hexagonales, los actores y relaciones UML, la cardinalidad niño-dosajes y la topología de despliegue. Diferencia llamadas en ejecución de imports. No añadas HIS, WhatsApp, PostgreSQL, móvil offline ni IA a INC-1 si no hay código y pruebas de esas funciones. Devuelve diagramas corregidos en SVG y fuente editable, además de los cambios justificados. No inventes resultados de pruebas ni enlaces de repositorio.

## Prompt de casos de uso del primer incremento

Crea un diagrama UML de casos de uso en SVG vectorial y PlantUML, con actores fuera de un límite “Sistema PMV Anemia Junín”. Actores: Personal de salud y Coordinador del proyecto. Personal de salud se asocia mediante líneas sólidas sin flecha a UC-01 Registrar niño, UC-02 Consultar expediente, UC-03 Actualizar expediente, UC-04 Registrar dosaje, UC-05 Listar y filtrar seguimiento. Coordinador se asocia a UC-06 Generar reporte del periodo. UC-01, UC-03 y UC-04 incluyen obligatoriamente UC-07 Validar datos de entrada; dibuja dependencias discontinuas «include» desde cada caso base hacia UC-07. No uses al sistema como actor de sí mismo. No incluyas sincronización, agenda, WhatsApp ni predicción, pues son incrementos posteriores. No añadas autenticación ni autorización no documentadas. Los actores indican participación, no acreditan permisos implementados. Entrega una tabla que relacione UC-01 con HIST-1.1, UC-02/03/04 con HIST-1.2, UC-07 con HIST-1.3, UC-05 con HIST-1.4 y UC-06 con HIST-1.5. Mantén etiquetas legibles y evita cruces sobre textos.

## Prompt para las tres vistas C4

Genera tres diagramas separados y consistentes, en SVG y fuente editable. Alcance: primer incremento del PMV Anemia Junín descrito en su avance, no la plataforma futura. C4-1: personas Personal de salud y Coordinador del proyecto interactúan con el Sistema PMV; no hay sistemas externos operativos acreditados. C4-2: dentro del límite del PMV existe una Aplicación web y API Python/Flask con HTML Jinja2 y REST/JSON, y un almacén de datos en archivo SQLite. El usuario usa navegador y HTTP local; la aplicación accede a SQLite con sqlite3/SQL dentro del proceso. Jinja2 no es una SPA desplegable; SQLite no es servidor remoto ni usa HTTP. C4-3: amplía únicamente la aplicación; muestra adaptador Web, adaptador REST, servicio de expedientes, reglas de dominio, adaptador SQLite y adaptadores de normativa JSON y reloj. Usa los puertos GestionExpedientes, NinoRepositorio, ProveedorNormativa y Reloj del avance. Si las flechas representan llamadas de ejecución, indícalo: servicio → implementación inyectada no implica import hacia el adaptador. En una nota separada explica que las dependencias de código van hacia los puertos del núcleo y bootstrap ensambla. No dibujes cada componente como microservicio. Cada vista debe tener título, alcance, tipos, responsabilidades, tecnología donde corresponda, etiquetas y leyenda. No añadas API Gateway, caché, PostgreSQL, HIS, WhatsApp ni modelo de ML a la arquitectura entregada. Señala que debe verificarse con el repositorio.

## Prompt de la arquitectura futura y continuidad con Semana 1

Con los entregables S1 v5, S2 v2 y S3-S4 v1, modela por separado una arquitectura objetivo futura. Conserva INC-1 registro, INC-2 agenda, INC-3 captura sin conexión y sincronización, INC-4 mensajería y barreras, INC-5 riesgo de abandono y no recuperación, e INC-6 tablero territorial. Señala que S1 exige también visitas, consumo/adherencia, referencias hasta cierre y captura cifrada, pero el WBS no les da cobertura explícita suficiente: propón historias pendientes sin inventar que fueron aprobadas. Resuelve primero la elección cliente PWA versus aplicación nativa; una PWA no accede por sí sola a sqlite3 del servidor. Si propones SQLite en navegador, explica su mecanismo y prueba de compatibilidad; si propones IndexedDB, registra el cambio de arquitectura. Diseña sincronización con IDs de eventos, idempotencia, control de versiones, confirmación del servidor y conservación de conflictos; no sobrescribas historia clínica por “última fecha gana”. Un modelo predictivo es compartido y versionado: Niño 1–0..* PrediccionRiesgo y ModeloPredictivo 1–0..* PrediccionRiesgo. No confundas clasificación actual de Hb con predicción de abandono. Entrega decisiones, diagramas y pruebas propuestas; no lo presentes como PMV implementado.

# Guion propuesto de siete diapositivas

La consigna fija 7 minutos globales, aunque sus tiempos por diapositiva suman 10. Este reparto conserva 7 minutos, incluida una demostración de 2 minutos. Confirmar la contradicción con el docente. Este guion no sustituye el PDF/PPTX final.

| N.º | Tiempo | Contenido y visual | Qué debe decir el equipo |
| --- | --- | --- | --- |
| 1 | 45 s | Problema y valor; diagrama 01 AS-IS/TO-BE; B1, B2 y B6. | El problema es la discontinuidad del seguimiento. INC-1 mejora la captura; eliminar el triple registro requiere cambio institucional. No atribuir reducción de anemia al PMV. |
| 2 | 45 s | Factores y ciclo; diagrama 02; tailoring local y futuro. | Iterativo-incremental + Scrum + DevOps. MLOps desde INC-5. Explicar por qué el registro se entrega primero y qué cambió del plan móvil. |
| 3 | 70 s | C4-2 diagrama 04 y tres ADR. | Flask/Jinja2/API comparten proceso; SQLite es archivo. Hexagonal separa dominio de adaptadores. No hay IA ni sincronización entregadas en INC-1. |
| 4 | 50 s | Pirámide de pruebas y métricas verificadas. | Mostrar 49 solo después de conciliar log y matriz. Cobertura reportada 95,8 %. Añadir p95/RPS y evidencia E2E reales antes de la defensa. No presentar smoke como carga. |
| 5 | 120 s | Demo del ejecutable y entorno. | Crear registro, rechazar duplicado/inválido, consultar/actualizar, añadir dosaje y revisar reporte. Usar datos sintéticos; tener video de la misma versión como respaldo. |
| 6 | 45 s | Indicadores de proceso, producto, resultado y valor. | Mostrar avance real del backlog. 24/28 = 85,7 % es aceptación de intentos sintéticos; resultado clínico no medido. No reutilizar horas/SP simulados de S3-S4. |
| 7 | 45 s | Una fila de trazabilidad completa y tres conclusiones. | B1 → registro → proceso iterativo → ADR-02/03 → CP de alta/duplicado → expediente → calidad de captura. Siguiente: agenda y validación normativa; offline antes de piloto rural. |

Total: 420 segundos. Rotar participación según dominio: Proceso presenta problema y planificación; Desarrollo arquitectura y demo; Calidad pruebas e indicadores. Los tres deben poder defender todo el recorrido.

## Preguntas para ensayar la defensa individual

1. ¿Por qué hexagonal y monolito son compatibles y cómo se verifica la dirección de dependencias?
2. ¿Qué diferencia hay entre un contenedor C4, un componente C4 y un contenedor Docker?
3. ¿Qué puede hacer realmente la aplicación al perder Internet o al perder conexión con el servidor local?
4. ¿Por qué el sistema no debe ser actor de su propio diagrama de casos de uso?
5. ¿Qué mide 24/28, qué no mide y cómo se trata un periodo sin intentos?
6. ¿Dónde están las nueve ejecuciones que faltan en el resumen de pruebas?
7. ¿Qué cambia de HIST-1.4 entre el plan y el avance, y dónde se registra esa decisión?
8. ¿Cómo se asocia una clasificación a la versión de la norma aplicada?
9. ¿Cómo demostrarían que un cambio de SQLite a PostgreSQL conserva datos y restricciones?
10. ¿Qué evidencia permitiría afirmar que se redujo la pérdida de seguimiento de S1?
