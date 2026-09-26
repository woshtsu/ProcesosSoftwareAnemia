# Informe de salida — orquestador — T-001

- **Agente:** orquestador
- **Fecha:** 2026-09-25
- **Tareas / solicitudes atendidas:** T-001
- **Estado final:** HECHO

## Resumen

Reestructuración del repositorio (antes `Entrega 1/` y `Entrega 2/`) en `guias/`, `entregables/semana-XX/`, `diagramas/`, `archivo/`, `coordinacion/` y `exportados/`, usando `git mv` para preservar historial. Creación de los 6 subagentes en `.claude/agents/`, protocolo, plantillas, tablero y README general. `anemia_junin/` se mantiene en la raíz (no hay rutas que dependan de su ubicación, pero moverlo no aportaba nada).

## Archivos creados / modificados / movidos

| Acción | Ruta | Nota |
| --- | --- | --- |
| movido | `guias/*` | S1, S2, S3-4 (md) y S6 (pdf), renombrados sin espacios/tildes |
| creado | `guias/S6_Consigna_integrador_extraccion.md` | texto extraído con pypdf |
| movido+modificado | `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` | ex v5; 11 imágenes base64 → `img/image1..11.png` (2,4 MB → 27 KB; texto verificado idéntico línea a línea salvo las 11 definiciones de imagen) |
| movido | `entregables/semana-01/img/image1..11.png` | eran `tmp/revision/s1-imageN.png`, byte-idénticas a las base64 (MD5 verificado) |
| movido+modificado | `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md` | ex v2 `.docx.md`; 1 imagen base64 → `img/image1.png` |
| movido | `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` | ex v1 |
| movido | `entregables/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf` | referencia |
| creado | `entregables/semana-05/_extraccion_Informe_Actividad5.md` | pypdf modo layout, 12 págs. |
| movido+modificado | `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` | ex `_revision.md`; enlaces a `../../diagramas/svg/` |
| movido | `diagramas/png`, `diagramas/svg`, `diagramas/src` | 9 PNG + 9 SVG + 1 puml + generador ReportLab (rutas actualizadas a la nueva estructura) |
| movido | `archivo/…` | v3/v4 de S1, v1 de S2, PDFs generados, zip, verificación S2, material de `tmp/revision` |
| eliminado | duplicados byte-idénticos | ver sección siguiente |

## Duplicados eliminados (MD5 idéntico al archivo conservado)

- `Entrega 2/S2.Guía…md`, `Entrega 2/tmp/revision/S2.Guía…md` (= `guias/S2_…`)
- `Entrega 2/tmp/revision/S3.GUÍA…md` (= `guias/S3-4_…`)
- `Entrega 2/tmp/revision/Entregable_Semana2_…_v2.docx.md`, `…Semana3y4_…_v1.md`, `verificacion_s2_y_guia_uml.md`, `contenido.py`, `diagramas.py`, `generar.py`
- `Entrega 2/Informe_Integrador_…_revision.pdf`, `Entrega 2/Revision_Cumplimiento_…pdf` (= copias en `archivo/pdf-generados/`)
- `Entrega 2/tmp/revision/__pycache__/` (caché)

## Verificación realizada

MD5 de todos los duplicados; comparación línea a línea del texto de S1/S2 antes y después de extraer imágenes; `py_compile` de los generadores; Grep de enlaces `diagramas/` en entregables.

## Pendientes y riesgos

- Discrepancia Actividad 5 (PDF: `tools/*.py`, unittest, "sin frameworks") vs. código (Flask, pytest, `scripts/`) → T-005 / T-008.
- Faltan pandoc, PlantUML y Graphviz en el equipo.

## Nota sobre historial git

Como S1 (2,4 MB → 27 KB) y S2 cambiaron sustancialmente al extraer las imágenes base64 en el mismo commit, git no los detecta como renombrados. Su historial previo se consulta por la ruta antigua:
`git log -- "Entrega 2/Entregable_Semana1_Anemia_Junin_v5.md"` y `git log -- "Entrega 2/Entregable_Semana2_Anemia_Junin_v2.docx.md"`.
