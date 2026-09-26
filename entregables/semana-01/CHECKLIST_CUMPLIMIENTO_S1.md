# Checklist de cumplimiento — Semana 1

- **Guía:** `guias/S1_Guia_trabajo_semana_1.md`
- **Entregable revisado:** `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md`
- **Versiones anteriores consultadas:** `archivo/versiones-anteriores/semana-01/Entregable_Semana1_Anemia_Junin_v3.md`, `..._v4.md`
- **Revisor:** revisor-documental (T-002)
- **Fecha:** 2026-09-25
- **Resultado global:** antes 74,1 % → después 96,3 % (50 CUMPLE, 4 PARCIAL, 0 NO CUMPLE de 54 requisitos; F-09 cerrado con INV-001). Fórmula: CUMPLE = 1, PARCIAL = 0,5, NO CUMPLE = 0.

## Matriz de requisitos

Requisitos R-xx extraídos de la guía (actividades, productos esperados, preguntas, estructura del entregable y criterio clave). Requisitos F-xx de formato exigidos por el protocolo del proyecto (`coordinacion/RUTAS.md`, definición del revisor) y por la solicitud de revisión (portada, índice, numeración, compatibilidad con pandoc).

| ID | Requisito (cita / paráfrasis fiel) | Ubicación en guía | Sección del entregable | Antes | Después | Evidencia / observación |
| --- | --- | --- | --- | --- | --- | --- |
| R-01 | Presentar el problema organizacional | §1 productos; §11 punto 1 | §1 | CUMPLE | CUMPLE | Problema de seguimiento con evidencia de la entrevista |
| R-02 | "Primero se analiza y mejora el proceso de la organización; después se determina cómo el software lo soportará" | §2 Regla | §1, §3, §5 | CUMPLE | CUMPLE | Problema no formulado como ausencia de software |
| R-03 | Tabla Actor / Necesidad / Decisión que debe tomar | §4 Actividad 1 | §2, Tabla 2 | CUMPLE | CUMPLE | Formato de tres columnas |
| R-04 | Completar la tabla de actores (plantilla con 5 filas) | §4 Actividad 1 | §2, Tabla 2 | CUMPLE | CUMPLE | 6 actores |
| R-05 | Pregunta orientadora: ¿qué actor recibe el mayor valor? | §4 | §2 | CUMPLE | CUMPLE | Respuesta argumentada (el niño) |
| R-06 | Modelar el AS-IS "sin la nueva solución tecnológica" (representación gráfica) | §5 Actividad 2 | §3, Figura 2 | PARCIAL | PARCIAL | Antes: PNG 620 px ilegible. Después: enlace a SVG pendiente de **DIAG-001** |
| R-07 | AS-IS identifica el inicio | §5 | §3 "Elementos" | CUMPLE | CUMPLE | Explícito en texto y en la especificación DIAG-001 |
| R-08 | AS-IS identifica actividades principales | §5 | §3 flujo 1-9 | CUMPLE | CUMPLE | |
| R-09 | AS-IS identifica decisiones | §5 | §3 D1-D4 | PARCIAL | CUMPLE | Antes: implícitas en el texto; ahora enumeradas D1-D4 |
| R-10 | AS-IS identifica actores | §5 | §3, carriles | CUMPLE | CUMPLE | 5 carriles |
| R-11 | AS-IS identifica problemas | §5 | §3 P1-P9 | CUMPLE | CUMPLE | Codificados P1-P9 |
| R-12 | AS-IS identifica el fin del proceso | §5 | §3 "Elementos" | PARCIAL | CUMPLE | Antes solo en la imagen |
| R-13 | "No incorporar todavía la solución propuesta" en el AS-IS | §5 Importante | §3 | CUMPLE | CUMPLE | Sin carril de sistema |
| R-14 | Identificar mínimo cinco brechas (Proceso actual / Problema-brecha / Consecuencia) | §6 Actividad 3 | §4, Tabla 3 | CUMPLE | CUMPLE | 6 brechas B1-B6 (la v4 tenía 4; la v5 ya las había ampliado) |
| R-15 | TO-BE que incorpora "únicamente las mejoras que resuelvan las brechas" | §7 Actividad 4 | §5, Tabla 4 | PARCIAL | CUMPLE | Nueva trazabilidad B1-B6 → M1-M6 |
| R-16 | Diagrama TO-BE | §7 | §5, Figura 7 | PARCIAL | PARCIAL | PNG ilegible → **DIAG-002** pendiente |
| R-17 | TO-BE muestra 1. entrada de información | §7 | §5, Tabla 5 | PARCIAL | CUMPLE | |
| R-18 | TO-BE muestra 2. actividades mejoradas | §7 | §5, Tablas 4-5 | CUMPLE | CUMPLE | |
| R-19 | TO-BE muestra 3. decisiones | §7 | §5, Tabla 5 | CUMPLE | CUMPLE | Decisiones humanas explícitas |
| R-20 | TO-BE muestra 4. intervención del software | §7 | §5, carril Sistema | CUMPLE | CUMPLE | |
| R-21 | TO-BE muestra 5. resultado | §7 | §5, Tabla 5 | PARCIAL | CUMPLE | Antes no rotulado |
| R-22 | TO-BE muestra 6. generación de valor | §7 | §5, Tabla 5 | PARCIAL | CUMPLE | Antes no rotulado |
| R-23 | Tabla Actividad organizacional / ¿Interviene software? (Sí/No) / ¿Cómo aporta? (≥5 filas) | §8 Actividad 5 | §6, Tabla 6 | CUMPLE | CUMPLE | 11 actividades; columna normalizada a Sí/No con matiz |
| R-24 | Mostrar la secuencia de dónde interviene el software (ejemplo Datos → … → Valor) | §8 ejemplo | §6 párrafo de secuencia | NO CUMPLE | CUMPLE | Secuencia añadida |
| R-25 | "El software no reemplaza todo el proceso organizacional" | §8 | §5 y §6 | CUMPLE | CUMPLE | Explícito |
| R-26 | Cadena de valor Entrada → Actividad → Resultado → Decisión → Acción → Valor | §9 Actividad 6 | §7, Tabla 7 | CUMPLE | CUMPLE | Pasada a tabla |
| R-27 | Representación gráfica de la cadena de valor | §9 (ejemplo gráfico) | §7, Figura 8 | PARCIAL | PARCIAL | PNG 620×98 ilegible → **DIAG-003** pendiente |
| R-28 | Relación actividad mejorada → mejor resultado → valor organizacional | §9 | §7 relaciones | CUMPLE | CUMPLE | 7 relaciones |
| R-29 | Mínimo seis indicadores | §10 Actividad 7 | §8, Tabla 8 | CUMPLE | CUMPLE | 14 indicadores |
| R-30 | Indicadores de proceso | §10 | Tabla 8 | CUMPLE | CUMPLE | 4 |
| R-31 | Indicadores de producto | §10 | Tabla 8 | CUMPLE | CUMPLE | 5 |
| R-32 | Indicadores de resultado | §10 | Tabla 8 | CUMPLE | CUMPLE | 2 |
| R-33 | Indicadores de valor | §10 | Tabla 8 | CUMPLE | CUMPLE | 3 |
| R-34 | Entregable con las 8 secciones en el orden de la guía (1 Problema … 8 Indicadores) | §11 | §1-§8 | CUMPLE | CUMPLE | |
| R-35 | "Documento breve" | §11 | §6, Anexo A | PARCIAL | CUMPLE | Detalle técnico (esquema, IA, WhatsApp, offline) y UML movidos a anexos sin perder contenido |
| R-36 | Pregunta 1: ¿Qué problema del proceso se pretende resolver? | §12 | §9.1 | CUMPLE | CUMPLE | |
| R-37 | Pregunta 2: ¿Qué actividad del AS-IS genera mayor pérdida de valor? | §12 | §9.2 | CUMPLE | CUMPLE | Ahora referida a pasos y brechas |
| R-38 | Pregunta 3: ¿Qué cambia concretamente en el TO-BE? | §12 | §9.3 | CUMPLE | CUMPLE | |
| R-39 | Pregunta 4: ¿Qué actividades serán automatizadas o mejoradas? | §12 | §9.4 | CUMPLE | CUMPLE | |
| R-40 | Pregunta 5: ¿Cómo se demostrará que el nuevo proceso genera valor? | §12 | §9.5 | CUMPLE | CUMPLE | |
| R-41 | Criterio clave: argumentar Problema → necesidad de cambio → TO-BE → necesidad de software → resultado → valor → indicador | Criterio clave | §10, Tabla 9 | PARCIAL | CUMPLE | Cadena explícita añadida |
| R-42 | No justificar diciendo solamente "se utilizará Scrum, DevOps o IA" | Criterio clave | Todo el documento | CUMPLE | CUMPLE | |
| R-43 | Dejar preparado el trabajo para el Eje 2 (modelo de proceso) | Criterio clave (cierre) | §10, Tabla 10 | NO CUMPLE | CUMPLE | Mapeo M1-M6 → INC-1..INC-6 y características para S2 |
| R-44 | Contexto de valor esperado (situación actual frente a valor esperado) | §3.2 ejemplo | §1, Tabla 1 | NO CUMPLE | CUMPLE | Añadida a partir de las brechas del propio documento |
| F-01 | Portada: curso, título, integrantes (tal como están), fecha | Solicitud de revisión | Portada | PARCIAL | CUMPLE | Faltaba la fecha y la universidad |
| F-02 | Índice | Solicitud de revisión | Índice | NO CUMPLE | CUMPLE | Índice general, de tablas y de figuras (sin enlaces, para portabilidad pandoc/GitHub) |
| F-03 | Tablas numeradas | Solicitud de revisión | Tablas 1-10, A.1-A.6 | NO CUMPLE | CUMPLE | |
| F-04 | Figuras numeradas con leyenda en el texto alternativo | RUTAS.md regla 5 | Figuras 1-11 | PARCIAL | CUMPLE | Antes: referencias `![][imageN]` sin texto alternativo |
| F-05 | Imágenes por ruta relativa, sin base64 | RUTAS.md regla 4 | Todo | CUMPLE | CUMPLE | |
| F-06 | Markdown limpio compatible con pandoc (sin negrita en encabezados, sin escapes `\.`, sin notas de "resaltado en amarillo" inexistente) | Solicitud de revisión | Todo | PARCIAL | CUMPLE | Encabezados `#`/`##` limpios; nota de versión eliminada (el historial está en git) |
| F-07 | Diagramas legibles con fuente editable (PlantUML), SVG en `../../diagramas/svg/` | RUTAS.md; solicitud | Figuras 2, 7, 8, 10, 11 | NO CUMPLE | PARCIAL | Solicitudes DIAG-001 a DIAG-005 abiertas; enlaces SVG ya insertados |
| F-08 | Coherencia con el software real (PMV Flask/SQLite, hexagonal, `anemia_junin/`) | Definición del revisor §5 | §10, Anexo B | PARCIAL | CUMPLE | Se aclara que el PMV implementa INC-1 y que los UML del anexo son visión TO-BE |
| F-09 | Coherencia normativa con la norma usada por el PMV (NTS 213-2024) | Definición del revisor §5 | §1, Anexo A.1 | PARCIAL | CUMPLE | INV-001 aplicado (2026-09-25): §1, Anexo A.1 y §11 declaran la NTS 213-2024 como vigente y la NTS 134-2017 como derogada (RM 251-2024-MINSA); el esquema del Anexo A.1 se presenta como operativo local compatible con la NTS 213 |
| F-10 | No inventar datos; marcar pendientes | Definición del revisor §4 | Todo | CUMPLE | CUMPLE | No se añadieron cifras; el `[PENDIENTE: INV-001]` se retiró al resolverse INV-001, sin citar umbrales de la NTS 134 no verificados |

## Resumen

| Momento | CUMPLE | PARCIAL | NO CUMPLE | Total | Cumplimiento |
| --- | --- | --- | --- | --- | --- |
| Antes de la revisión | 32 | 16 | 6 | 54 | 74,1 % |
| Después de la revisión | 50 | 4 | 0 | 54 | 96,3 % |

Los cuatro PARCIAL restantes dependen de solicitudes a otros agentes: R-06 (DIAG-001), R-16 (DIAG-002), R-27 (DIAG-003) y F-07 (DIAG-001 a DIAG-005). F-09 quedó en CUMPLE al aplicar INV-001. Al resolverse, el cumplimiento será del 100 %.

## Cambios aplicados en esta revisión

- Portada completa (universidad, curso, unidad, eje, título, integrantes y roles tal como estaban, fecha) e índices general, de tablas y de figuras.
- Encabezados limpios y numerados; preguntas de análisis como §9.1-§9.5; eliminada la "nota de versión (v5)" que remitía a un resaltado en amarillo inexistente en Markdown.
- §1: nueva Tabla 1 "situación actual / valor esperado"; mención de la NTS 213-2024 junto a la NTS 134.
- §3: elementos exigidos del AS-IS explícitos (inicio, actores, decisiones D1-D4, fin) y problemas codificados P1-P9.
- §4: brechas codificadas B1-B6; las cuatro infografías se asocian a las brechas B1, B3, B5 y B6 y se numeran como Figuras 3-6.
- §5: nueva Tabla 4 (trazabilidad brecha → mejora M1-M6) y Tabla 5 (seis elementos del TO-BE exigidos).
- §6: secuencia de intervención del software; tabla con columna Sí/No normalizada; detalle técnico movido al Anexo A para cumplir "documento breve".
- §7: cadena de valor en tabla (Tabla 7).
- §10 nuevo: cadena de argumentación del criterio clave (Tabla 9) y conexión con la Semana 2 (Tabla 10), con el estado real del PMV (INC-1 en Flask + SQLite, hexagonal).
- Anexo A: esquema normativo, modelo predictivo (con nota sobre las dos variables no ponderadas), WhatsApp (ejemplo marcado como ficticio) y offline. Anexo B: UML de la visión TO-BE. Anexo C: referencia a la entrevista.
- Figuras 2, 7, 8, 10 y 11 enlazadas a los SVG destino de las solicitudes DIAG-001 a DIAG-005 (marcadores `<!-- DIAG-### pendiente -->`). Los PNG anteriores (`img/image2.png`, `image7.png`, `image9.png`, `image10.png`, `image11.png`) se conservan en disco como referencia y dejan de enlazarse.
- INV-001 (2026-09-25): §1 declara la NTS 213-2024 como norma vigente y la NTS 134-2017 como derogada; Anexo A.1 presenta el esquema como operativo local compatible con la NTS 213 (se retira `[PENDIENTE: INV-001]`); §11 marca la NTS 134 como derogada.

## Pendientes (con solicitud asociada)

- [ ] Proceso AS-IS por carriles → `coordinacion/solicitudes/DIAG-001.md` → `diagramas/svg/10_s1_proceso_as_is.svg`
- [ ] Proceso TO-BE con mejoras M1-M6 → `DIAG-002` → `diagramas/svg/11_s1_proceso_to_be.svg`
- [ ] Cadena de valor → `DIAG-003` → `diagramas/svg/12_s1_cadena_valor.svg`
- [ ] Casos de uso de la visión TO-BE → `DIAG-004` → `diagramas/svg/13_s1_casos_uso_vision.svg`
- [ ] Clases del dominio de la visión TO-BE → `DIAG-005` → `diagramas/svg/14_s1_clases_dominio_vision.svg`
- [x] Vigencia del esquema de tamizaje frente a la NTS 213-2024 → `INV-001` (aplicado el 2026-09-25; informe `coordinacion/informes/2026-09-25_investigador_INV-001.md`)
- [ ] Antes de exportar a PDF/DOCX, verificar que los cinco SVG existan (si no, pandoc no podrá incrustarlos).
- Observación (sin solicitud): las figuras 1, 3-6 y 9 son PNG de baja resolución (320-520 px) sin fuente; son infografías o una fotografía del esquema, no diagramas de proceso, por lo que se mantienen.
