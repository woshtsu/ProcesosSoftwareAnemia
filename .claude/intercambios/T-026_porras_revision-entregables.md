# T-026 — Encargo de revisión integral: guías, entregables y exportados

- **Fecha:** 15/11/2026, America/Lima
- **Autor humano:** Porras V., Ricardo (Leader) · **Asistente:** Claude (orquestador)
- **Destinatario:** compañero del equipo que tome T-026, con su propio Claude (rol `revisor-documental`)
- **Tarea:** T-026 · **Rama base:** `develop` (commit de esta entrega) · **Estado:** PENDIENTE de asignar

## Objetivo

Hacer una revisión independiente de todos los entregables del curso contra sus guías y el sílabo, documentar cada hallazgo con evidencia visual, corregirlo y volver a verificar hasta llegar al **100 % de cumplimiento**. La respuesta final es un checklist con el visto bueno de cada elemento.

## Antes de empezar (obligatorio)

1. `git switch develop && git pull`. Crear la rama `docs/t026-revision` desde `develop`.
2. Leer `AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/AVANCE_SESION.md`, `.claude/coordinacion/RUTAS.md`, `.claude/coordinacion/PROTOCOLO.md` y `.claude/coordinacion/TABLERO.md`.
3. Leer `.claude/contexto/SILABO_RESUMEN.md`: es el resumen del sílabo (el PDF no se versiona). Ante dudas manda el PDF del aula virtual.
4. Tomar T-026 en el tablero con tu nombre y rol.
5. Forma de trabajo: si tienes `agy` instalado, delega el trabajo pesado y revísalo. Si no, usa subagentes (haiku para leer y buscar, sonnet para redactar o corregir). Si existe `graphify-out/graph.json`, usa `graphify query` antes de buscar.

## Alcance

| Semana | Guía | Entregable | Exportado |
| --- | --- | --- | --- |
| S1 | `guias/semana-01.md` | `entregables/semana-01/` | — |
| S2 | `guias/semana-02.md` | `entregables/semana-02/` | — |
| S3-4 | `guias/semana-03-04.md` | `entregables/semana-03-04/` | — |
| S5 | `guias/semana-05.md` | `entregables/semana-05/` | `exportados/semana-05/` |
| S6 | `guias/semana-06-integrador.md` | `entregables/semana-06-integrador/` | — |
| S9 | `guias/semana-09.md` | `entregables/semana-09/` | `exportados/semana-09/` |
| S10 | `guias/semana-10.md` | `entregables/semana-10/` | — |
| S11 | `guias/semana-11.docx` | `entregables/semana-11/` (incluye `feria/`) | `exportados/semana-11/`, `exportados/feria/` |
| S12 | `guias/semana-12.md` | `entregables/semana-12/` | `exportados/semana-12/` |
| S13 | `guias/s13/` (laboratorio SCM, cuadro PDCA, lecturas) | `entregables/semana-13/` | `exportados/semana-13/` |
| S14 y S16 | `guias/s14/`, `guias/s16/` | Revisar qué piden y si el proyecto ya cubre algo; listar lo que falta (no crear el entregable salvo que el usuario lo pida) | — |

## Método

1. **Requisitos.** Por cada guía, extrae los requisitos en una lista `R-xx` (actividades, productos, estructura, formato, evidencias, rúbrica). Agrega los requisitos del sílabo que apliquen (unidad, resultado de aprendizaje, evaluación).
2. **Cotejo.** Para cada requisito, marca Cumple / Cumple parcialmente / No cumple, con la ubicación exacta en el entregable (archivo, sección, figura o página).
3. **Coherencia.** Revisa también:
   - Que el `.md` o `.html` y su PDF/DOCX de `exportados/` digan lo mismo: versión, fecha, cifras y figuras.
   - Enlaces e imágenes rotos.
   - Citas y referencias según la norma usada en cada entregable.
   - Cifras repetidas entre semanas: pruebas, cobertura, versiones, SP, fechas.
   - Ausencia de datos personales sensibles o secretos.
4. **Hallazgos.** Registra cada uno en `.claude/revision/T-026/HALLAZGOS.md` con: ID `H-###`, severidad (alta/media/baja), semana, archivo y ubicación, requisito afectado, descripción, **evidencia antes**, corrección aplicada, **evidencia después** y estado.
5. **Capturas (obligatorio).** Todo hallazgo lleva captura del problema **antes** de corregirlo y otra **después**, en `.claude/revision/T-026/capturas/`, con nombres `H-###_antes.png` y `H-###_despues.png`.
   - Páginas de PDF: renderízalas con PyMuPDF (`fitz`) a PNG, recortando la zona del problema.
   - HTML o Markdown: captura con Playwright y Edge (`channel="msedge"`, sin interfaz).
   - Páginas de GitHub: Playwright, o el script `entregables/semana-13/laboratorio-scm/capturar_evidencias_scm.py` con `--salida` y `--filtro`.
   - Nunca borres una captura «antes».
6. **Reparación.** Corrige en la fuente (`.md` o `.html`), nunca solo en el PDF. Regenera el exportado afectado con su script: `entregables/semana-13/exportar_pdf_s13.py`, `.claude/herramientas/conversion/*`, o el agente `conversor-entregas`. Vuelve a cotejar. Repite hasta que no quede ningún «No cumple» ni «Parcial» corregible. Lo que no se pueda corregir sin decisión del equipo o del docente queda como pendiente justificado, no como cumplido.
7. **Entregas ya calificadas.** Si corriges una entrega ya presentada, no cambies su sentido: registra el cambio en la tabla de control de cambios del documento (si la tiene) y en `HALLAZGOS.md`.

## Reglas

- No tocar `pmv_fastapi/` salvo que un hallazgo lo exija; en ese caso, pedirlo primero al Leader.
- Sin contraseñas, tokens, `.env` ni datos personales en capturas o textos.
- Publicar por PR `docs/t026-revision → develop`. La rama `develop` está protegida y exige 1 aprobación: **pide la revisión a Porras V. y no integres con excepción de administrador**. Así se cierra el dominio 4 del PDCA (revisión por pares).
- Al cerrar: informe `.claude/coordinacion/informes/AAAA-MM-DD_revisor-documental_T-026.md`, tablero y `.claude/AVANCE_SESION.md`.

## Terminado

1. `HALLAZGOS.md` completo y con capturas antes y después de cada hallazgo.
2. Fuentes y exportados corregidos y coherentes entre sí.
3. Un checklist final en la respuesta del chat y en `.claude/revision/T-026/CHECKLIST.md`, con:
   - Una fila por semana y por exportado.
   - Requisitos cumplidos/total, hallazgos abiertos/cerrados y visto bueno (✅ o ❌).
   - Porcentaje global.
   - Una línea final: «Revisión al 100 %: sí/no» y, si es no, qué falta y por qué.
