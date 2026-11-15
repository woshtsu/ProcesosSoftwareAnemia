# Informe T-025 — Observaciones del docente a S13: PDCA de gestión de la configuración y laboratorio SCM

- **Responsable humano:** Porras V., Ricardo (Leader) · **Asistente:** Claude (orquestador y revisor documental)
- **Rama:** `chore/reorganizar-por-semanas` (sin commit; conviene publicarlo en un commit o PR aparte del de T-024) · **Fecha:** 14/11/2026 · **Estado:** EN REVISIÓN

## Pedido

1. El PDCA debe centrarse en el **proceso** de administración de la configuración, con evidencias de código de la suite de GitHub.
2. Desarrollar la guía `guias/s13/GUÍA DE TRABAJO DE LABORATORIO_ GESTIÓN DE CONFIGURACIÓN DE SOFTWARE (UNIDAD IV).md` con la mayor cantidad posible de evidencias.

## Cambios

| Tipo | Ruta | Detalle |
| --- | --- | --- |
| creado | `entregables/semana-13/laboratorio-scm/capturar_evidencias_scm.py` | Auditoría reproducible: 20 capturas de páginas públicas de GitHub (Edge sin interfaz, Playwright) y 14 grupos de comandos `git`/`gh` como imagen de terminal, con salidas en `evidencias/salidas_cli.json`. Solo lectura. |
| creado | `entregables/semana-13/laboratorio-scm/evidencias/` | 34 PNG + JSON (14/11/2026). |
| reescrito | `entregables/semana-13/laboratorio-scm/Informe_SCM_Lab13.html` | Organizado según las actividades 1 a 5 de la guía, con las 6 capturas obligatorias en recuadro y 24 complementarias (30 figuras), matriz de trazabilidad (Tabla 1 de la guía, 12 filas), indicadores, autoevaluación con la rúbrica y anexos (correspondencia de evidencias, reproducibilidad y enlaces). Corte al 14/11; incluye las PR #21 a #27. |
| creado | `entregables/semana-13/pdca/PDCA_gestion_configuracion.html` | Diagnóstico con 11 indicadores medidos antes y después del 06/11, 12 dominios del proceso SCM con PLAN/DO/CHECK/ACT, responsables, fechas y estado, registro de seguimiento, escala y anexo con 15 evidencias E-1 a E-15. |
| archivado | `.claude/archivo/semana-13/PDCA_mejora_v1_2026-11-06.html` | PDCA anterior (12 dominios del proyecto), reemplazado. |
| creado | `entregables/semana-13/exportar_pdf_s13.py` | Exporta ambos HTML a PDF con Edge. |
| regenerado | `exportados/semana-13/Porras-Auqui-Huamani-PDCA-mejora.pdf` (13 págs.) y `Porras-Auqui-Huamani-Informe-SCM-Lab13.pdf` (29 págs.) | Mismos nombres que la entrega anterior. |
| registro | `RUTAS.md` (guía S13), `TABLERO.md` (T-025) | — |

## Hallazgos del proceso que salieron de la auditoría (14/11)

- Integraciones en `main` por PR: 9/19 antes del 06/11 y 9/9 después. Commits convencionales: 22 % → 83 %.
- 0 de 7 RFC evaluadas (todas siguen en `pendiente-evaluacion`); 1 de 19 PR con «Approved» (#9); 1 de 19 vinculada a RFC (#13).
- Ruleset `ownermerge` configurado pero desactivado; `main` sin protección.
- `develop` 5 commits detrás de `main` y sin PR; GitFlow solo se aplicó en el PMV.
- Despliegue en rojo en 6 de 7 ejecuciones de `main` (09–13/11): el *deploy hook* de Render falla con el servicio suspendido.
- 5 *releases* con notas y 0 artefactos; el *hotfix* de la PR #22 no tiene etiqueta.

## Comprobaciones

- Cifras verificadas contra la API (`gh`) y `git log`: PR solo de documentos (6 de 9), ramas con PR integrada (16), versión de Python del CI (3.11), número de figuras (30).
- Las evidencias de configuración (`ci.yml`, plantillas) se leen de `origin/main`, no de la copia de trabajo (que tiene el filtro `paths` de T-024 sin publicar).
- PDF revisados página a página en miniatura; los recuadros de capturas obligatorias no se parten.
- La captura de *checks* de la PR #13 sale vacía sin sesión iniciada; no se usa en el informe.

## Pendientes

1. Revisión del equipo y subida al aula virtual.
2. PR de la rama de trabajo de T-025 hacia `develop` (prevista para el 15/11/2026) y posterior release de `develop` a `main`.
3. Consolidar la revisión por pares obligatoria sin bypass de administrador durante el desarrollo del Incremento 5.
4. Reanudar el servicio en Render y reactivar el despliegue automático desde el pipeline de GitHub Actions.
5. Los archivos de `guias/s13/`, `s14/` y `s16/` están sin versionar y con nombres originales (con espacios).

## Acciones del 14/11 (noche)

Tras la redacción inicial del corte de la tarde, el propietario (`woshtsu`) y Claude ejecutaron y registraron acciones correctivas en GitHub, documentadas en ambos HTML con corte al 14/11/2026 (23:00):

1. **Ruleset `ownermerge` activo:** Activado formalmente para `main` y `develop` con PR obligatoria de 1 aprobación, sin borrado ni force push, y excepción exclusiva para *Repository admin* (actor id 5). `main` figura protegida (`protected: true`) en la API. Evidencia: `web_a2_settings_rulesets.png` (captura obligatoria 2 del informe) y `cli_a2_ruleset.png`.
2. **Evaluación formal de RFC:** El Leader evaluó las 6 RFC válidas: #18, #19 y #20 con etiqueta `aprobado` tras análisis de impacto; #14, #15 y #17 actualizadas a `implementado`; #16 conservada como duplicado cerrado. Indicador de RFC evaluadas: 6/6 (100 %).
3. **Reanudación de GitFlow en `develop`:** PR #28 sincronizó `main → develop` mediante merge commit. PR #29 integró `chore/reorganizar-por-semanas → develop` (T-024) tras superar un fallo inicial de Ruff mediante el commit `style(T-024)...`. Ambas se integraron con la excepción de administrador; `develop` quedó en 0 detrás / 2 delante de `main`.
4. **Limpieza de ramas remotas:** Se eliminaron 17 ramas remotas ya integradas o cerradas, dejando activas únicamente `main` y `develop` (y la rama local de T-025). Se creó la etiqueta de respaldo `archivo/docs-s12-correcciones` para preservar la historia de la S12.
5. **Releases con artefactos:** Se publicó la release `v4.0.1` Latest (hotfix PR #22 sobre `e6d8c4c`) con el artefacto `reportes-calidad-v4.0.1.zip` (690 pruebas, 0 fallos, 99,46 % cobertura). Se adjuntó `reportes-calidad-v4.0-Inc4.zip` a `v4.0-Inc4` (2 de 6 releases con artefactos).
6. **Actualización documental:** Se actualizaron `Informe_SCM_Lab13.html` (43 figuras, 6 obligatorias y 37 complementarias contrastando antes y después) y `PDCA_gestion_configuracion.html` (21 evidencias E-1 a E-21, 8 dominios verificados, 2 en proceso y 2 abiertos).

