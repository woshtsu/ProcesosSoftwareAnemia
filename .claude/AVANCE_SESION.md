# Avance de la sesión en curso

Archivo vivo para continuar el trabajo en un chat nuevo. Actualizarlo durante la sesión. Al cerrar la tarea, mover el detalle a `.claude/coordinacion/informes/` y dejar aquí solo el enlace.

## Tarea en curso

- **T-022** — Regrabar el video de la demo (S12) contra producción <https://softwareanemia-virginia.onrender.com> grabando el escritorio completo con ffmpeg (gdigrab). Rama `main`, sin commits. Rol: desarrollador.

## Hecho

- ffmpeg 9.0.2 instalado con `winget install --id Gyan.FFmpeg -e` (el script lo localiza en la carpeta de paquetes de WinGet si no está en PATH).
- `pmv_fastapi/scripts/grabar_demo.py` reescrito: Edge visible y maximizado (perfil temporal, sin aviso de automatización), espera del inicio de sesión manual, ffmpeg alrededor del recorrido, datos sintéticos DEMO (DNI 7999xxxx) y SQL de limpieza.
- Prueba de 10 s correcta (`--prueba 10`): MP4 H.264 1920x1080, 11,9 s, con barra de tareas y reloj visibles.
- Decisiones del usuario (09/11/2026): fecha de referencia leída de `/api/salud`; rótulo bajo las pestañas; filtrar por la comunidad DEMO donde haya filtro; recrear inasistencia y respuesta del tutor con niños DEMO; generar recordatorios solo si el modo es SIMULADO; la limpieza la ejecuta el usuario en el editor SQL de Supabase con `limpieza_demo_anemia.sql` (carpeta temporal).
- Ajustes anteriores delegados en `agy` (encargo sin commits); pendiente de revisar.

- Segunda prueba de 10 s correcta: sin aviso de `--no-sandbox`, rótulo bajo las pestañas, fecha de referencia 2024-06-30. Correo de la cabecera ocultado con CSS inyectado (cambio directo de una línea).
- Grabación completa del 09/11/2026 (~13:35): `demo_anemia_junin_v4.mp4`, 3:12 (objetivo 4:50–5:10). **No apta**: Seguimiento y Visitas vacíos, filtro «DEMO Comunidad» no encontrado en Agenda/Alertas, inasistencia y respuesta del tutor saltadas, el niño registrado sin conexión quedó «Pendiente de sincronizar», la búsqueda de expediente mostró el niño equivocado y GitHub mostró el aviso «Traducir».
- SQL de limpieza generado en `%TEMP%\limpieza_demo_anemia.sql`; el usuario debe ejecutarlo en Supabase.

- Diagnóstico y correcciones delegados en `agy` (tres encargos): verificación por paso con `expect_response` (90 s), calentamiento previo, modo `--ensayo`, fechas DEMO que generan control C1M vencido (verificado en local con el dominio), HIST-4.4 sin depender del filtro de comunidad. Correcciones directas de revisión: la respuesta del tutor solo se registra sobre recordatorios DEMO; el SQL de limpieza volvió a `AND` (agy lo había dejado en `OR`); DNI DEMO distintos por ejecución.
- Ensayos: 1.º falló en RF-09, 2.º en HIST-4.4, 3.º 17/17 OK (5:49).
- Grabación final (09/11/2026): `entregables/semana-12/video/demo_anemia_junin_v4.mp4`, 5:59, 5,3 MB, 17 pasos verificados. Defecto menor: Edge muestra el aviso «¿Traducir?» en las páginas de GitHub (escena 5).

- PR #25 fusionado en `main` (`1215517`): video, `GUION_LOCUCION.md` y script.
- Limpieza DEMO ejecutada por el usuario en Supabase; la consulta de comprobación devolvió 0 niños DEMO.
- Workflow «Mantener activo el servicio de Render» desactivado (`gh workflow disable mantener-activo.yml`) porque el usuario suspende el servicio de Render. Para reactivarlo: `gh workflow enable mantener-activo.yml`.

## Siguiente paso

1. Locución de la compañera, subida a Drive y enlace en el Anexo A del informe S12.
2. Cerrar T-022 con su informe en `.claude/coordinacion/informes/`.
3. Si el docente pide el software en vivo: reanudar Render y reactivar el workflow.

## T-023 — Cierre de la entrega S13 (Huamani R., 13/11/2026)

- Hecho: `exportados/semana-13/` con el informe S13 (DOCX y PDF), el cuadro PDCA y el informe del laboratorio SCM; informe `.claude/coordinacion/informes/2026-11-13_documentador_T-023.md`; fila T-023 en el tablero.
- Hecho directamente, sin delegar en `agy`: no está instalado en este entorno y la tarea es copiar archivos ya generados y redactar el informe de cierre.
- Siguiente paso: entrega en el aula virtual por el equipo; aprobación de las RFC y protección de ramas por el Leader.

## T-024 — Reorganización del repositorio por semanas (Porras V., 13/11/2026)

- Rama `chore/reorganizar-por-semanas`, commit WIP subido. `agy` lo dejó a mitad: los movimientos están hechos y falta terminar de corregir rutas y verificar.
- Traspaso completo: `.claude/intercambios/2026-11-13_orquestador_T-024_reorganizacion.md`.
- 14/11/2026: rutas y verificación terminadas por Claude (sin commit). Detalle en `.claude/coordinacion/informes/2026-11-14_orquestador_T-024.md`.
- 14/11 noche: integrado en `develop` por la PR #29 (CI verde tras corregir formato de Ruff). Llega a `main` con la release develop → main.

## T-025 — Observaciones del docente a S13: PDCA de gestión de la configuración y laboratorio SCM (Porras V., 14/11/2026)

- Rama `docs/t025-scm-pdca` desde `develop`. Informe: `.claude/coordinacion/informes/2026-11-14_orquestador_T-025.md`.
- PDCA rehecho (12 dominios del proceso SCM, indicadores antes/después, 21 evidencias) e informe del laboratorio con 43 figuras; PDF en `exportados/semana-13/`.
- Evidencias: `capturar_evidencias_scm.py`; hallazgos de la tarde conservados en `evidencias/antes_2026-11-14_tarde/` y ramas previas al borrado en `evidencias/limpieza_ramas_antes/`.
- Acciones en GitHub (cuenta woshtsu): ruleset activo, RFC evaluadas, PR #28 y #29 por develop, 17 ramas borradas con respaldo `archivo/docs-s12-correcciones`, `v4.0.1` y artefactos en 2 releases.
- 15/11: PR #30 (T-025 → develop, sin CI por el filtro de rutas) y PR #31 (release develop → main, `c4d2ae6`) integradas con excepción de administrador. Quedan solo `main` y `develop`.
- **Pendiente despliegue:** Render responde (`/api/salud` ok), pero el trabajo `produccion` del CI de `main` falla al llamar al deploy hook aun con `RENDER_DEPLOY_HOOK_URL` renovado (04:38 UTC); reintento 2 de la ejecución 43677270776 también falló. El paso oculta el error HTTP: revisar en Render el hook y los eventos.
- Siguiente paso: diagnosticar el hook; primera PR con aprobación de un par (dominio 4).

## T-026 — Revisión integral por un compañero (15/11/2026)

- Encargo: `.claude/intercambios/T-026_porras_revision-entregables.md`. Contexto del sílabo: `.claude/contexto/SILABO_RESUMEN.md`.
- Guías S14 y S16 versionadas en `guias/s14/` y `guias/s16/`; `guias/Sílabo.pdf` queda fuera de Git.

### Avance T-026 (Jean, 15/11/2026)

- Rama `docs/t026-revision` desde develop (250fdf5). Revisión y correcciones terminadas: 117 hallazgos (82 cerrados, 35 pendientes justificados) en `.claude/revision/T-026/HALLAZGOS.md`; checklist en `.claude/revision/T-026/CHECKLIST.md` (requisitos 79,5 %, global 79,7 %, «Revisión al 100 %: no»).
- S6: develop tenía el borrador del 25/09; se restauró el cierre del 02/10 desde la rama local `feature/s6-integrador-final` (borrada del remoto).
- Exportados regenerados en Linux con `.claude/revision/T-026/herramientas/ejecutar_exportador.py` (Chrome + `fonts-win.conf`).
- Hecho directamente por Claude solo la orquestación, la restauración de S6 y las decisiones de revisión; `agy` no está instalado y el resto se delegó en subagentes (haiku para leer, sonnet para corregir).
- Informe: `.claude/coordinacion/informes/2026-11-15_revisor-documental_T-026.md`.
- **Siguiente paso:** push de la rama y PR a develop con revisión de Porras V. (woshtsu). Cuando la apruebe: paso final del dominio 4 (capturas de aprobación, PDCA, informe del laboratorio 13 y PDF) en la misma PR y aviso a Porras V. para integrar.
- 16/11/2026: la rama se subió y se abrió la PR #35, con revisión pedida a woshtsu. woshtsu la integró a las 16:25 sin aprobarla (0 revisiones; H-223).
- **Siguiente paso:** PR de continuación `docs/t026-paso-final` → develop, con revisión de Porras V. Cuando la apruebe con «Review changes → Approve»: capturas, dominio 4 del PDCA, informe del laboratorio 13 y sus PDF en esa misma PR; después la integra él, sin excepción de administrador.
- 16/11/2026, 17:13: Porras V. aprobó la PR #36 y la integró con esa aprobación (bf1b95e). Paso final del dominio 4 hecho en la PR `docs/t026-dominio4-evidencia`: capturas de la aprobación, PDCA (dominio 4 «Verificado»), informe del laboratorio 13 y PDF. T-026 queda HECHO; el detalle está en `.claude/coordinacion/informes/2026-11-15_revisor-documental_T-026.md`.

