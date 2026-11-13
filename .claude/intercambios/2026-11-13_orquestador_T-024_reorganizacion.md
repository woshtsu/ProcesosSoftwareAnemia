# T-024 — Reorganización del repositorio por semanas (traspaso a otra PC)

- **Autor humano:** Porras V., Ricardo (Leader) · **Asistente:** Claude (orquesta) + `agy` (ejecuta)
- **Rama:** `chore/reorganizar-por-semanas` · **Base:** `main` / `fb90686` · **Fecha:** 13/11/2026 · **Estado:** EN CURSO (trabajo parcial, commit WIP)

## Objetivo acordado con el usuario

- `entregables/semana-XX/` contiene **solo** los trabajos entregables que siguen la guía de `guias/`; las ediciones se hacen en el `.md`.
- `exportados/semana-XX/` guarda el PDF/DOCX más reciente de cada semana (opcional).
- Todo lo demás que no es software pasa a `.claude/` (`coordinacion/`, `diagramas/`, `herramientas/`, `archivo/`). `pmv_fastapi/` y `anemia_junin/` quedan en la raíz como carpetas hermanas (no se anidan).
- `Dataset/` pasa a `pmv_fastapi/datos/` (el importador lo lee; el Dockerfile solo copia `app/` y `scripts/`, así que no entra en la imagen).
- CI: `ci.yml` solo se dispara con cambios en `pmv_fastapi/**` o en el propio `ci.yml`.

## Hecho (por `agy`, detenido a mitad por el usuario)

- `git mv` de `coordinacion/`, `diagramas/`, `herramientas/`, `archivo/` a `.claude/`, y de `Dataset/` a `pmv_fastapi/datos/` (`config.py` del importador actualizado).
- `guias/` renombradas a `semana-01.md` … `semana-12.md` (`semana-11.docx`).
- `entregables/feria/` → `entregables/semana-11/feria/`; `entregables/sonarcloud/2026-11-05/` → `entregables/semana-12/sonarcloud/`.
- PDF de la Actividad 5 → `exportados/semana-05/`; DOCX de correcciones S12 → `exportados/semana-12/`.
- CHECKLIST, CAPTURAS_*PENDIENTES, ADENDA y `_extraccion_*` → `.claude/archivo/semana-XX/`.
- Borrados en `entregables/semana-13/`: DOCX y PDF del informe (las versiones comprimidas están en `exportados/semana-13/`) y los PDF de PDCA y SCM (hash idéntico al de `exportados/semana-13/`, comprobado por Claude).
- Filtro `paths` en `ci.yml` (push y pull_request) y `.gitignore` actualizado.
- Rutas ya corregidas en `.claude/CLAUDE.md`, `.claude/agents/*`, `AVANCE_SESION.md`, `CONTEXTO_ACTUAL.md` y parte de los entregables e informes.

## Pendiente (para terminar en la otra PC)

1. **Terminar de corregir rutas viejas.** Al detenerse quedaban referencias a `coordinacion/`, `diagramas/`, `herramientas/`, `archivo/` o `Dataset/` sin el prefijo `.claude/` (o `pmv_fastapi/datos/`), sobre todo en:
   `entregables/semana-11|12|13/*.md`, `entregables/semana-03-04`, `entregables/semana-12/sonarcloud/ANALISIS_SONARCLOUD.md`, `entregables/semana-12/correcciones/*.md`, `entregables/semana-13/laboratorio-scm/Informe_SCM_Lab13.html`, `entregables/semana-11/anexos/generar_figuras_s11.py`, `README.md`, `.claude/CLAUDE.md`, `.claude/CONTEXTO_ACTUAL.md`, `.claude/coordinacion/informes/*` y `solicitudes/ORQ-00*`, `.claude/herramientas/conversion/exportar_s9.py`, `.claude/diagramas/src/integrador/generar.py`. Además, los nombres viejos de las guías (`S1.Guía…`, `S9-PSW-GUÍA…`, etc.).
   Para listarlas: `git grep -nE "(^|[^./a-zA-Z_-])(coordinacion|diagramas|herramientas|archivo|Dataset)/" -- . ':!pmv_fastapi/docs' ':!anemia_junin'`
2. **Scripts que calculan la raíz con `parents[N]`** dentro de `.claude/herramientas/**` (de `parents[2]` a `parents[3]`): comprobar uno por uno.
3. **`.claude/coordinacion/RUTAS.md` y `README.md`**: describir la nueva estructura.
4. **Verificación:** enlaces relativos rotos en los `.md` (comparar con `main`), `python -m py_compile` de los `.py` movidos y las pruebas del importador en `pmv_fastapi`.
5. Revisión del diff por Claude, PR a `main` y fila T-024 del tablero a EN REVISIÓN/HECHO.

Para relanzar: `agy -p "$(cat .claude/intercambios/2026-11-13_T-024_encargo_agy.md)" --mode accept-edits --sandbox --settings '{"permissions":{"allow":["command(*)"]}}' --print-timeout 0`, desde Bash (en PowerShell 5.1 las comillas del encargo se rompen). El encargo es idempotente: lo que ya está movido se debe saltar.

## Fuera del repositorio (lo hace el usuario)

- **Render:** `softwareanemia-virginia` tiene *Auto-Deploy* activado con cada commit a `main` (comprobado con el conector el 13/11). Desactivarlo en Settings → Build & Deploy para que solo despliegue el *deploy hook* del CI. Si no se desactiva, el filtro `paths` del CI no evita los despliegues por cambios de documentos.
- **Ruleset `ownermerge`** (hoy desactivada): al activarla, no marcar `calidad-y-pruebas` como check obligatorio (con el filtro `paths`, las PR solo de documentos se quedarían esperando) y no exigir aprobaciones, o agregar el rol *Repository admin* a la bypass list, porque el propietario no puede aprobar sus propias PR.
