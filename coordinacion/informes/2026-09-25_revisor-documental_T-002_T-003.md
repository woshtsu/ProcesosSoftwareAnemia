# Informe de salida — revisor-documental — T-002 (S1) y T-003 (S2)

- **Agente:** revisor-documental
- **Fecha:** 2026-09-25
- **Tareas / solicitudes atendidas:** T-002, T-003; solicitudes abiertas: DIAG-001 a DIAG-006, INV-001
- **Estado final:** HECHO (la parte del revisor). Quedan PARCIAL solo los requisitos que dependen de diagramas (DIAG) y de la verificación normativa (INV).

## Resumen

Se extrajeron todos los requisitos de las guías S1 y S2 (actividades, productos, preguntas orientadoras, estructura del entregable, preguntas de análisis, reto, criterio clave y rúbrica) más los requisitos de formato del proyecto, y se evaluaron antes y después de la revisión.

| Semana | Requisitos | Antes | Después | PARCIAL restantes |
| --- | --- | --- | --- | --- |
| S1 | 54 | 74,1 % (32 C / 16 P / 6 NC) | 95,4 % (49 C / 5 P / 0 NC) | R-06, R-16, R-27, F-07 (DIAG-001 a 005) y F-09 (INV-001) |
| S2 | 74 | 84,5 % (56 C / 13 P / 5 NC) | 98,0 % (71 C / 3 P / 0 NC) | R-24, R-63, F-07 (DIAG-006) |

Fórmula: CUMPLE = 1, PARCIAL = 0,5, NO CUMPLE = 0. Con los diagramas y la verificación normativa resueltos, ambos entregables quedan al 100 %.

Principales cambios: portada (universidad, curso, eje, título, integrantes y roles tal como estaban, fecha) e índices en ambos documentos; tablas y figuras numeradas; encabezados limpios compatibles con pandoc; eliminadas las "notas de versión" que remitían a un resaltado en amarillo inexistente. En S1: elementos AS-IS explícitos (inicio, D1-D4, fin, P1-P9), brechas codificadas B1-B6, trazabilidad brecha → mejora M1-M6, tabla con los seis elementos del TO-BE, secuencia de intervención del software, cadena de valor en tabla, cadena de argumentación del criterio clave, conexión con S2 y detalle técnico movido a anexos ("documento breve"). En S2: columna Evidencia restaurada en características y herramientas (esta última con el estado real del repositorio), sustento de la comparación de modelos, respuesta a la pregunta central, cadena argumentativa del criterio clave, tabla de los diez elementos del proceso, incrementos INC-1..INC-6, conceptos de la guía (restaurados de la v1) y conexión con S3-4.

## Archivos creados / modificados / movidos

| Acción | Ruta | Nota |
| --- | --- | --- |
| modificado | `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` | Reestructurado según la guía S1 |
| modificado | `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md` | Reestructurado según la guía S2 |
| creado | `entregables/semana-01/CHECKLIST_CUMPLIMIENTO_S1.md` | Nombre indicado por el usuario (RUTAS.md dice `CHECKLIST_cumplimiento.md`: el orquestador debe unificarlo) |
| creado | `entregables/semana-02/CHECKLIST_CUMPLIMIENTO_S2.md` | Ídem |
| creado | `coordinacion/solicitudes/DIAG-001.md` a `DIAG-006.md` | Diagramas a rehacer en PlantUML |
| creado | `coordinacion/solicitudes/INV-001.md` | Vigencia NTS 134 frente a NTS 213-2024 |
| modificado | `coordinacion/TABLERO.md` | T-002 y T-003 → HECHO; solicitudes registradas |

No se borró ni movió ningún archivo. Los PNG que dejan de enlazarse (`semana-01/img/image2.png`, `image7.png`, `image9.png`, `image10.png`, `image11.png`; `semana-02/img/image1.png`) siguen en disco como referencia para el diagramador; el orquestador puede archivarlos cuando se resuelvan las solicitudes DIAG.

## Solicitudes de diagrama creadas

| ID | Diagrama | Entregable / figura | SVG destino (enlace ya insertado) |
| --- | --- | --- | --- |
| DIAG-001 | Proceso AS-IS por carriles | S1, Figura 2 | `diagramas/svg/10_s1_proceso_as_is.svg` |
| DIAG-002 | Proceso TO-BE con carril Sistema y mejoras M1-M6 | S1, Figura 7 | `diagramas/svg/11_s1_proceso_to_be.svg` |
| DIAG-003 | Cadena de valor | S1, Figura 8 | `diagramas/svg/12_s1_cadena_valor.svg` |
| DIAG-004 | Casos de uso de la visión TO-BE (ex Mermaid v4) | S1, Anexo B, Figura 10 | `diagramas/svg/13_s1_casos_uso_vision.svg` |
| DIAG-005 | Clases del dominio de la visión TO-BE (ex Mermaid v4) | S1, Anexo B, Figura 11 | `diagramas/svg/14_s1_clases_dominio_vision.svg` |
| DIAG-006 | Modelo de proceso aplicado al proyecto (ex Mermaid v1) | S2, Figura 1 | `diagramas/svg/15_s2_modelo_proceso_aplicado.svg` |

## Verificación realizada

- Lectura completa de las guías S1 y S2, de los entregables vigentes, de las versiones v3/v4 (S1) y v1 (S2), de `archivo/verificaciones/verificacion_s2_y_guia_uml.md`, de `diagramas/README.md` y de `anemia_junin/` (pyproject, ADR 001/002, `config/normativa_v1.json`).
- Verificación aritmética de todas las matrices ponderadas (S1 Tabla A.6; S2 Tablas 3, 6, 12-14): sin errores.
- Script de control: número de columnas uniforme en todas las tablas y existencia de las rutas de imagen (solo faltan los 6 SVG pendientes de DIAG).
- Búsqueda de HTML y base64 en los `.md`: solo quedan los comentarios `<!-- DIAG-### pendiente -->` (pandoc los ignora).
- No se pudo probar la conversión con pandoc (no está instalado).

## Pendientes y riesgos

- Seis diagramas pendientes (DIAG-001 a 006). **Hasta que existan los SVG, la conversión a PDF/DOCX mostrará imágenes rotas**; T-009 debe esperar.
- INV-001: el esquema de tamizaje de S1 se basa en la NTS 134-2017 y en el esquema local; el PMV usa la NTS 213-2024 (RM 251 y 429-2024). Queda una nota de coherencia y un `[PENDIENTE: INV-001]` en el Anexo A.1.
- Datos del equipo marcados `[PENDIENTE]` en S2: enlaces al tablero de GitHub Projects y a los prototipos de Figma; no existe `.github/workflows/`, por lo que GitHub Actions figura como planificado.
- Discrepancia de nombres: RUTAS.md y la definición del revisor indican `CHECKLIST_cumplimiento.md`; la solicitud del usuario pidió `CHECKLIST_CUMPLIMIENTO_S1.md` / `_S2.md` y se siguió esta última. El orquestador debe unificar RUTAS.md.
- Todos los factores de S2 figuran con nivel "Alto" (decisión del equipo, sustentada); podría matizarse en una revisión futura si el docente lo observa.

## Solicitudes abiertas a otros agentes

- `coordinacion/solicitudes/DIAG-001.md` — AS-IS S1
- `coordinacion/solicitudes/DIAG-002.md` — TO-BE S1
- `coordinacion/solicitudes/DIAG-003.md` — Cadena de valor S1
- `coordinacion/solicitudes/DIAG-004.md` — Casos de uso de la visión TO-BE (S1, anexo)
- `coordinacion/solicitudes/DIAG-005.md` — Clases del dominio de la visión TO-BE (S1, anexo)
- `coordinacion/solicitudes/DIAG-006.md` — Modelo de proceso aplicado (S2)
- `coordinacion/solicitudes/INV-001.md` — Vigencia NTS 134 vs. NTS 213-2024

## Nota posterior (2026-09-25): aplicación de INV-001

Se aplicaron al entregable S1 las recomendaciones de `coordinacion/informes/2026-09-25_investigador_INV-001.md`, contrastadas antes con fuentes públicas y con `anemia_junin/config/normativa_v1.json`:

- **§1:** la NTS N.° 213-MINSA/DGIESP-2024 figura como norma vigente (RM 251-2024-MINSA, modificada por la RM 429-2024-MINSA) y se indica que la RM 251-2024-MINSA derogó la NTS N.° 134-MINSA/2017/DGIESP. Antes se la presentaba como una "actualización".
- **Anexo A.1:** el esquema de las Tablas A.1 a A.4 se presenta como esquema operativo local compatible con la NTS 213 (inicio del tamizaje a los 6 meses; el corte de Hb ≥ 10,5 g/dL de la Tabla A.3 coincide con el de 6 a 23 meses). Se aclara que el PMV toma los umbrales de la NTS 213 (10,5 g/dL para 6 a 23 meses y 11,0 g/dL para 24 a 59 meses) y no del esquema local. Se retira el `[PENDIENTE: INV-001]`, y se deja constancia de que el calendario de dosajes y suplementación no se contrastó fila por fila con el texto de la norma.
- **§11 Fuentes:** la NTS 134 queda marcada como derogada y la NTS 213 como vigente.
- **Checklist S1:** F-09 pasa de PARCIAL a CUMPLE. El resultado global sube de 95,4 % a 96,3 % (50 C / 4 P / 0 NC).
- **Descartado del informe INV-001:** su afirmación de que la NTS 134 usaba un umbral de "~9,5 g/dL" para 6 a 23 meses es una inferencia sin fuente, y el propio informe reconoce que no tuvo acceso a la NTS 134. No se incorporó ninguna cifra de la NTS 134. Tampoco se incorporaron las fechas exactas de las RM que proponía el informe, porque no pudieron verificarse.
- **Discrepancia de nombres resuelta:** en `coordinacion/RUTAS.md` el patrón de los checklists pasa a ser `CHECKLIST_CUMPLIMIENTO_S<n>.md`. Queda desalineada la definición `.claude/agents/revisor-documental.md` (línea 24), que sigue diciendo `CHECKLIST_cumplimiento.md`. El revisor no la modifica, así que la unificación corresponde al orquestador.
