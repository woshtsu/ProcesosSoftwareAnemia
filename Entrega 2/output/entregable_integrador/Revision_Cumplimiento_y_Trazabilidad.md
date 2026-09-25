# Revisión de cumplimiento y errores de trazabilidad

Proyecto Anemia Junín · Consigna integradora S6 · Corte documental del 25 de septiembre de 2026

> Dictamen: Informe_Actividad5_PMV_AnemiaJunin.pdf NO cumple por sí solo toda la consigna integradora. Es un avance técnico reutilizable para INC-1, pero no integra de forma suficiente S1-S7 ni acredita todas las evidencias de la entrega. No se asigna nota porque faltan código, defensa y validación de resultados.

Se revisaron la consigna completa, Actividad 5, S1 v5, S2 v2, S3-S4 v1, las guías S2/S3-S4 y la guía local de UML. La incorporación de S1 permite comprobar la cadena desde el problema original. Las cifras del PMV se consideran reportadas; no se recibió el repositorio para ejecutarlas.

| Área de la rúbrica | Diagnóstico del avance | Acción principal |
| --- | --- | --- |
| Proceso organizacional y modelo · 2 puntos | Faltan AS-IS/TO-BE, brechas, actores, factores y comparación integrados. | Recuperar S1/S2 y corregir alcance y valor. |
| Actividades y planificación · 2 puntos | Referencias a S3-S4 sin RAE, WBS, estimación ni seguimiento completos. | Integrar matrices y registrar cambios frente al plan. |
| Categoría, arquitectura y pruebas · 2 puntos | Hexagonal, ER y pruebas parciales; faltan C4-1/2/3, ADR y evidencia completa. | Completar diseño, conciliar pruebas y verificar repositorio. |
| Trazabilidad y valor · 2 puntos | Persisten cambios semánticos y valor sobreatribuido al registro. | Vincular brecha-HU-ADR-CP-indicador con estado de evidencia. |
| Exposición y defensa · 12 puntos | No hay presentación ni demostración verificable disponibles. | 7 diapositivas, demo y dominio individual. |

## Cómo leer las observaciones

Crítico: puede invalidar la cadena requisito-producto-resultado. Alto: impide demostrar un requisito o una decisión. Medio: reduce precisión o legibilidad. “No acreditado” significa falta de evidencia disponible, no prueba de que el equipo nunca lo haya realizado.

# Matriz de cumplimiento de la consigna

| Requisito S6 | Estado en Actividad 5 | Qué falta o debe corregirse |
| --- | --- | --- |
| Portada y resumen ≤ 300 palabras | Parcial | Portada de Actividad 5; sin resumen integrador, códigos, docente y fecha de entrega. |
| 2.1 Actores, AS-IS, ≥5 brechas y TO-BE | Ausente | Integrar S1, conservando responsables y alcance organizacional. |
| 2.1 Intervención y cuatro tipos de indicadores | Parcial | El reporte sintético cubre producto; no resultado ni valor real. |
| 2.2 Factores, comparación y tailoring | Parcial | El enfoque se nombra; faltan matrices y diagrama aplicado. |
| 2.3 Actividades, entradas/productos/salidas, RAE y DoD | Parcial | DoD técnicos por componente; falta proceso completo y RAE separado. |
| 2.3 WBS, estimación, prioridad, plan y seguimiento | Ausente en informe | Se citan secciones anteriores sin integrar contenido ni cambios. |
| 3.1 Categorías y adaptación | Parcial | Se justifica cambio de herramientas; no existe matriz completa. |
| 3.2 ADR, C4-1/2/3, datos y API | Parcial | Paquetes y despliegue no sustituyen C4. ER presente, OpenAPI solo mencionado. |
| 3.3 Unitarias, API, carga, E2E, cobertura y defectos | Parcial | Pruebas reportadas; faltan detalle conciliado, reportes, carga y navegador real. |
| 3.4 Despliegue y demostración | Parcial | Capturas presentes; entorno local. Falta reproducción del ejecutable. |
| 4 Trazabilidad integral | Ausente | Falta matriz completa desde problema hasta medición. |
| 5 Tres conclusiones y tres lecciones | Parcial | Conclusión y siguiente incremento; no estructura solicitada. |
| 6 Repositorio, README, scripts y tag | No acreditado | No hay URL ni tag verificable. Archivos solo referidos. |
| Presentación de 7 diapositivas | No disponible | Obligatoria además del informe. |

La versión integrada adjunta completa la organización documental y propone correcciones. No convierte automáticamente en cumplidos los requisitos que dependen de código, mediciones reales o aceptación externa.

# Errores críticos que rompen la trazabilidad

| ID y ubicación | Ruptura y consecuencia | Corrección concreta |
| --- | --- | --- |
| T01 · S1 §6.4; S2 §9; S3-S4 §3/7/8; A5 pp. 3-4 | PWA con captura local y sincronización central cambia a Flask/SQLite servidor. “Funciona local” no demuestra captura móvil offline. | CH-01: formalizar demostración local para INC-1; mantener cifrado, cola y sincronización en INC-3 con pruebas nuevas. |
| T02 · S1 §5/6/7; S2 §7; A5 p. 12 | Se afirma eliminar triple registro sin integración HIS ni acuerdo de sustitución del proceso. Un registro adicional puede incluso sumar digitación. | Reescribir como expediente validado dentro del PMV. Medir duplicidad operativa y validar cambio institucional antes de atribuir eliminación. |
| T03 · S1 §6.2; S3-S4 §8; A5 p. 2 | Riesgo predictivo de abandono se confunde con severidad de última Hb. HIST-1.4 pasa de estado de control a clasificación. | CH-03: separar clasificación actual (INC-1), vencimiento de controles (INC-2) y predicción de abandono (INC-5). |
| T04 · S1 §6/7/8; WBS S3-S4 §8 | Referencias hasta cierre, visitas, consumo/adherencia y cifrado local no tienen cobertura explícita en historias del WBS. | Crear historias y criterios o exclusión aprobada. No cerrar sus indicadores por entregar el registro nominal. |
| T05 · S1 §8; S3-S4 §15; A5 pp. 10/12 | 24/28 mide aceptación de intentos sintéticos, no calidad de todos los datos persistidos ni reducción del abandono. | Definir población, unidad, denominador y periodo; clasificarlo como producto. Conservar valor clínico como no medido. |
| T06 · S1 §6.1; S2/S3-S4; A5 pp. 5/12 | Cambio NTS 134 → NTS 213 y modificación 429 sin matriz de reglas. “134/213” deja ambigua la versión. | CH-04: identificar fuente y regla aplicada; versionar configuración y casos frontera; retirar el nombre ambiguo. |

La actualización normativa puede ser correcta y necesaria; el error de trazabilidad es dejar requisitos y pruebas atados a versiones diferentes sin documentar la transición. No se preservan reglas antiguas por mera continuidad.

# Inconsistencias de evidencia planificación e indicadores

| ID y ubicación | Problema comprobable | Corrección y prioridad |
| --- | --- | --- |
| T07 · A5 p. 6 | 7 + 16 + 5 + 6 + 4 + 2 = 40; se declaran 49. Casos con sufijo b figuran en p. 2 pero no se concilian. | Alta. Enumerar todas las ejecuciones; no asumir que son falsas ni que los sufijos explican exactamente las 9. |
| T08 · A5 p. 10/12 | Captura: 28 intentos y 4 rechazados. Siembra descrita: 24 niños + 3 inválidos. | Alta. Explicar secuencia de siembra/demo. Un intento puede tener varios errores; no sumar códigos como intentos. |
| T09 · A5 p. 2 y Figura 4 p. 5 | Texto: altitud 0-4999; ER: CHECK 0-6000. | Alta. Contrastar UI, dominio, JSON y DDL. Añadir pruebas de 4999/5000 y rango admitido; no escoger arbitrariamente un máximo. |
| T10 · A5 pp. 6/12 | 25,8 ms es máximo de smoke. 60 operaciones secuenciales no prueban carga. HTML con cliente de test no prueba navegador E2E. | Alta. Reportar herramientas, concurrencia, duración, p95, RPS y errores; ejecutar recorrido con navegador. |
| T11 · S3-S4 §11.1/20; A5 p. 12 | Historia 1.2 y 1.4 en Sprint 2 en tabla; en Sprint 1 en plan ejecutable. “Inicio 20 agosto” frente a 1 septiembre. | Alta. Fijar una línea base y registrar cambios por historia y fecha; no mezclar tres calendarios. |
| T12 · S3-S4 §14/17 | 16 SP, 58 horas y reunión de seguimiento son ejemplos/simulación. | Crítica si se usan como resultados. Obtener horas y SP reales; mantener simulación etiquetada. |
| T13 · S3-S4 §6/16 | DoD cobertura ≥80 %, pero bloqueo solo bajo 70 %. | Alta. Bloquear si no cumple ≥80 % o modificar DoD explícitamente. |
| T14 · S1 §8; S3-S4 §15 | S1 no fija metas. S3-S4 incorpora +15 %, -20 %, precisión ≥75 % y acción <70 % sin aceptación mostrada. | Alta. Etiquetar metas propuestas, establecer línea base y separar precisión/recall del modelo futuro. |

# Correcciones de diagramas UML y arquitectura

| Diagrama y fuente | Error o límite | Cómo corregir |
| --- | --- | --- |
| S1 Figura 7 · Casos de uso | “Sistema inteligente (IA + Web/App)” es actor del propio sistema. Se incluyen sincronización y predicción como si siempre formaran parte de registrar. | Actores externos al límite. PMV separado de visión futura. Sincronización no es obligatoria en cada registro; modelarla según eventos/conectividad. |
| S1 Figura 7 · Relaciones | Hay flechas de actor a caso que pueden leerse como flujo; no se identifican claramente todos los estereotipos y condiciones. | Asociaciones simples sin dirección para evitar ambigüedad; «include» al caso incluido; «extend» al base con condición y punto de extensión. |
| S1 Figura 8 · Clases | Niño y ModeloPredictivo con cardinalidad 1 a 1; confunde modelo entrenado compartido con predicción individual. | Niño 1 → 0..* PrediccionRiesgo; ModeloPredictivo 1 → 0..* PrediccionRiesgo. Evaluar por separado historia y versión. |
| S1 Figuras 2/4 · Procesos | Mezclan flechas discontinuas entre carriles y decisiones sin leyenda formal. En TO-BE la entrada se ve como familia, personal y luego sistema separados. | Conservar decisiones y carriles; definir UML o BPMN. En UML, flujo de control sólido aunque cruce carriles; no confundir mensajes con control. |
| A5 Figuras 1/2 | Paquetes e imports explican hexagonal, pero no son las vistas C4-1/2/3 exigidas. | Añadir C4 por nivel y alcance. Hexagonal organiza dependencias internas; C4 comunica estructura. Son compatibles. |
| A5 Figura 3 | El despliegue mezcla entorno local, CI y extensiones futuras con texto muy pequeño. | Diagrama del PMV local separado del objetivo futuro. CI es entorno de construcción; no componente clínico de ejecución. |
| Guía UML local D3 | Indica punteada = asíncrona o retorno; prescribe sobrescribir por marca de tiempo. | En UML, retorno discontinuo; mensaje asíncrono sólido con punta abierta. Diseñar reconciliación sin pérdida antes de formalizar offline. |
| Guía UML D1 y D2 | Sugiere SMS como extensión de enviar por WhatsApp y MLOps desde Sprint 5 sin alinear calendario. | Modelar “Notificar familia” con canales alternativos según diseño; distinguir preparación de datos y ejecución de INC-5. |

Las vistas nuevas son especificaciones coherentes con el PMV descrito; no se presentan como ingeniería inversa del código ausente. La fuente SVG permite modificar cajas y textos sin generar una imagen por IA.

# Cambios adicionales y orden de cierre

| Hallazgo | Reparación necesaria |
| --- | --- |
| Prioridad INC-3 = 4,40 mayor que INC-2 = 4,15, pero agenda va antes | Explicar demostración local, o reordenar el piloto rural. No decir que la matriz determina automáticamente el calendario. |
| S3-S4 §12 atribuye dependencia de WhatsApp a INC-5 | Mover dependencia principal a INC-4; exigirla en INC-5 solo si una variable necesita datos de ese canal. |
| S1 alcance <5 años frente a lista 6-59 meses del PMV | Diferenciar alta, clasificación y seguimiento visible. Especificar atención preventiva fuera del listado y pruebas de borde. |
| S3-S4 54 horas no cubren todas las tareas del INC-1 | Añadir filtros, reporte, dosajes, pruebas y documentación al WBS y reestimar. |
| “Sin modificar núcleo” al añadir agenda en A5 p. 12 | La reutilización del puerto ayuda, pero nuevas reglas y entidades pueden exigir ampliar aplicación y dominio. |
| DDL “portable a PostgreSQL” solo probado en SQLite | No afirmar portabilidad verificada; probar migración, tipos y restricciones en PostgreSQL al implementarlo. |
| Tabla 1 normativa con bandas no verificadas | La RM 429-2024 publica los valores. Contrastar configuración y pruebas con la fuente; una alerta no reemplaza esa comprobación. |
| S6: 7 minutos globales, pitches individuales suman 10 | Preparar 7 minutos como límite principal y confirmar la contradicción con el docente. Propuesta de tiempos en guion. |

## Orden recomendado para cerrar la entrega

1. Acordar CH-01 a CH-04 y el alcance por incremento. 2. Corregir historias y necesidades de S1 sin cobertura. 3. Incorporar C4/ADR/UML y contrato real. 4. Identificar repositorio y tag, ejecutar pruebas y conciliar cifras. 5. Obtener aceptación de usuario y métricas con denominador verificable. 6. Preparar exactamente siete diapositivas y ensayar la demo.

La consigna solicita informe PDF, presentación PDF/PPTX y enlace al repositorio. Los diagramas de casos de uso responden además a la solicitud del equipo y a la continuidad de S1; no reemplazan los C4 exigidos en S6.

# Trazabilidad normativa y fuentes de revisión

La revisión se concentra en ingeniería del software y consistencia documental. No valida un algoritmo clínico. El cambio de fuente normativa debe reflejarse en los requisitos, configuración, etiquetas de la interfaz, reglas de cálculo y casos de prueba.

La RM 429-2024 modifica la NTS 213 aprobada por RM 251-2024. Su tabla de ajuste documenta 2,9 g/dL para 4000-4499 msnm y 3,3 g/dL para 4500-4999 msnm. Estos datos permiten cerrar la consulta documental que el avance dejó pendiente; falta comprobar el JSON y el comportamiento del programa. Fuente: https://bvs.minsa.gob.pe/local/fi-admin/RM-429-2024-minsa.pdf .

## Fuentes principales

S6, pp. 1-6: entregables y estructura. S6, pp. 7-9: rúbrica. Actividad 5, pp. 2-6: requisitos, diseño y pruebas; pp. 7-11: capturas; p. 12: demostración y conclusiones. S1, secciones 4-9: brechas, intervención, indicadores y UML. S2, secciones 3-10: modelo y trazabilidad. S3-S4, secciones 6-20: DoD, WBS, calendario y seguimiento.

C4 Model: https://c4model.com/diagrams ; https://c4model.com/diagrams/notation ; https://c4model.com/diagrams/component . Se consultaron para mantener alcance, jerarquía, relaciones y tecnologías de las vistas.

OMG UML 2.5.1: https://www.omg.org/spec/UML/2.5.1 . MINSA RM 251-2024: https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa . MINSA RM 429-2024: https://www.gob.pe/institucion/minsa/normas-legales/5670414-429-2024-minsa .

## Límites de la revisión

No se recibió código, OpenAPI, DDL, logs, acta ni presentación. Tampoco se dispone de la transcripción de entrevista de S1. Por ello, las afirmaciones sobre entrevista se atribuyen al entregable, y las métricas de Actividad 5 se conservan como reportadas. No se vuelve a publicar la prevalencia ENDES 2025 sin comprobar el cuadro y la población exactos.

Los archivos originales se conservan. El informe integrado es una propuesta de cierre documental; las decisiones nuevas y evidencias pendientes están identificadas para que no se confundan con trabajo ya ejecutado.
