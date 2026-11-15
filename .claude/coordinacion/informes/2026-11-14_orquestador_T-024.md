# Informe T-024 — Reorganización del repositorio por semanas (cierre de rutas y verificación)

- **Responsable humano:** Porras V., Ricardo (Leader) · **Asistente:** Claude (orquestador)
- **Rama / commit base:** `chore/reorganizar-por-semanas` / `57a1ccd` (WIP sobre `main` `fb90686`) · **Fecha:** 14/11/2026 · **Estado:** EN REVISIÓN
- **Traspaso de origen:** `.claude/intercambios/2026-11-13_orquestador_T-024_reorganizacion.md`

## Resumen

Se terminó el trabajo que `agy` dejó a mitad el 13/11: los movimientos ya estaban hechos y faltaba corregir rutas y verificar. Se hizo directamente, sin relanzar `agy`, porque quedaban unas 140 líneas que había que revisar una por una (muchas coincidencias eran falsos positivos: enlaces relativos correctos dentro de `.claude/`, plantillas `NN_nombre`, comentarios) y además había que revisar errores que `agy` había introducido (prefijo `.claude/.claude/`). Sin commits.

## Cambios

| Tipo | Archivos | Detalle |
| --- | --- | --- |
| corregido | `.claude/coordinacion/solicitudes/DIAG-001…006, DIAG-100…105` | Enlaces `../../.claude/.claude/diagramas/` → `../../diagramas/` (error de `agy`). |
| corregido | `.claude/CONTEXTO_ACTUAL.md` | Enlace al generador de la feria relativo a `.claude/`; `diagramas/_build/` con prefijo. |
| prefijado `.claude/` | informes y solicitudes de `.claude/coordinacion/`, `.claude/archivo/`, fuentes `.puml`, entregables S3-4, S11, S12, S13, `ANALISIS_SONARCLOUD.md`, `Informe_SCM_Lab13.html`, `generar_figuras_s11.py` | Menciones de `coordinacion/`, `diagramas/`, `herramientas/`, `archivo/` como rutas desde la raíz (120 sustituciones). |
| ruta nueva | informes T-001, T-002/3, T-004, T-023, `DEV-100.md`, `anemia_junin/docs/trazabilidad.md`, S11, `semana-12/evidencias/generar_figuras.py` | Menciones a archivos movidos (CHECKLIST, ADENDA, `_extraccion_*`, CAPTURAS, PDF de S13) con su ruta completa nueva. |
| script | `.claude/diagramas/src/integrador/generar.py` | Salida en `.claude/diagramas/_build/` (antes creaba `diagramas/_build/` en la raíz) y enlaces generados `../../.claude/diagramas/svg/`. |
| comentario | `.claude/diagramas/src/70_s9_cadena_trazabilidad.dot` | Guía S9 → `guias/semana-09.md`. |
| agente | `.claude/agents/revisor-documental.md` | El checklist se guarda en `.claude/archivo/semana-XX/CHECKLIST_CUMPLIMIENTO_S<n>.md`, como dice RUTAS.md. |
| registro | `TABLERO.md` (T-024 → EN REVISIÓN), `AVANCE_SESION.md` | Estado y siguiente paso. |
| local (ignorado) | `plantuml.jar` y `diagramas/_build/` | Movidos a `.claude/herramientas/plantuml/` y `.claude/diagramas/_build/` en esta PC. |

Se dejaron sin cambiar, a propósito: el pie de la Figura 65 de S11 (describe una captura de `coordinacion/TABLERO.md` en `main`, L30-L31, tomada antes de la reorganización), los dos documentos de traspaso del 13/11 (describen el movimiento) y el comentario de `.gitignore`.

## Comprobaciones

| Verificación | Resultado |
| --- | --- |
| a) Enlaces relativos rotos en `.md` | `main`: 15 · rama: 5, todos falsos positivos (4 ejemplos de plantilla `NN_nombre.svg` y la palabra `ruta` en el encargo de `agy`). No hay roturas nuevas. |
| b) `git grep` de rutas viejas en la raíz | Solo quedan los enlaces relativos correctos dentro de `.claude/`, el árbol del README, la expresión regular de `exportar_s9.py`, el comentario de `.gitignore`, la Figura 65 y los traspasos. Sin nombres viejos de guías. |
| `parents[N]` | Comprobados todos los scripts de `.claude/herramientas/**` (`parents[3]`) y `.claude/diagramas/src/integrador/diagramas.py` (`parents[4]`): apuntan a la raíz. |
| c) `py_compile` | 34 `.py` movidos o editados: compilan. |
| d) Pruebas del importador | `pytest -k "importa or dataset or diresa"`: 46 aprobadas; 2 E2E (CP-185, CP-186) no se ejecutan en esta PC porque falta el navegador de Playwright (`playwright install`), ajeno a la reorganización. `CSV_POR_DEFECTO` existe en `pmv_fastapi/datos/`. |
| CI | `ci.yml` con filtro `paths` en `push` y `pull_request`; `mantener-activo.yml` sin tocar. |
| Fin de línea | El diff tiene tantas inserciones como eliminaciones (solo líneas editadas). |

## Pendientes

1. Revisión del usuario, commit y PR a `main` (requiere autorización).
2. **Render:** desactivar *Auto-Deploy* de `softwareanemia-virginia` (Settings → Build & Deploy); si no, cada commit a `main` sigue desplegando aunque el CI no corra.
3. **Ruleset `ownermerge`:** al activarla, no exigir `calidad-y-pruebas` ni aprobaciones (ver el traspaso).
4. Los `.md` de S11 a S13 cambiaron solo en rutas; los PDF/DOCX de `exportados/` conservan las rutas anteriores y no se regeneraron.
