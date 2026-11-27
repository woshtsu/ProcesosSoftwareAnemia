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

## T-027 — Informe Final de la Unidad IV (26/11/2026)

- Rama `docs/s15-informe-unidad-iv`. Sin commits ni pushes.
- Hecho: Creación del informe final de la Unidad IV en `entregables/semana-15/Informe_Unidad_IV_Anemia_Junin.md` (256 153 caracteres, 2 859 líneas, 38 304 palabras, ~76,6 páginas) estructurado exactamente según la plantilla de la guía S14 (`guias/s14/PSW-INFORME ACADÉMICO INTEGRADOR DEL PROYECTO DE ASIGNATURA.md`):
  1. Carátula oficial: Universidad Continental, NRC 30173, Asignatura ASUC01702, IX Ciclo, 3 créditos, Docente Ing. Jorge Alfredo Guevara Jimenez, integrantes y roles RAE completos, fecha 26/11/2026.
  2. Front matter: Tabla 1 (Reparto de roles), Índices dinámicos actualizados (General, Tablas 1..48, Figuras 1..134), Tabla 2 (Control de cambios respecto a S13 con 9 observaciones resueltas), Resumen Ejecutivo / Abstract bilingüe con cobertura de la Unidad IV.
  3. Sección 1 (Introducción): 1.1 con los 7 antecedentes del estado del arte verificados en bases de datos científicas (Nunkesser, Heeager, Chaabane, Marandi, Cuadros, Santos, Westgard) con DOIs y aportes específicos, más contexto del proyecto y secuencia de entregables S1..S15 (Tabla 3); 1.2 Diagnóstico AS-IS y justificación (Tabla 4, Fig. 1); 1.3 Objetivos alineados al sílabo (resultado de aprendizaje de asignatura y 4 específicos de Unidades I–IV, más matriz de objetivos del proyecto con Unidad IV SCM, Tabla 5).
  4. Sección 2 (Marco Teórico): 2.1 a 2.5 consolidados de S13; 2.6 nuevo sobre SCM, GitFlow y SemVer respaldado en 5 referencias reales (Sommerville, ISO/IEC/IEEE 828:2012, Chacon & Straub, Driessen, Preston-Werner).
  5. Sección 3 (Desarrollo por Unidades):
     - 3.1 Unidad I: 3.1.1 AS-IS vs TO-BE (Tabla 7, Fig. 2 y 3); 3.1.2 Brechas B1–B6 e indicadores de valor (Tablas 8 y 9); 3.1.3 Factores y Selección del modelo (Tablas 10 y 11); 3.1.4 Planificación, WBS, priorización y control de desviaciones (Fig. 4, 5, 6; Tablas 12 y 13).
     - 3.2 Unidad II: 3.2.1 Categorización de procesos (Tabla 14); 3.2.2 Sastrería (Tailoring), ciclo híbrido y DoD (Tablas 15 y 16, Fig. 7); 3.2.3 Arquitectura Hexagonal en GitHub (Tablas 17 y 18, Fig. 8 a 12); 3.2.4 PMV e Incrementos 1 al 4 (Tablas 19, 20, 21).
     - 3.3 Unidad III: 3.3.1 Evaluación GQM, estrategia de pruebas y fichas funcionales F01 a F30 con capturas (Tablas 22 a 28, Fig. 13 a 82); 3.3.2 Auditoría FURPS+, psicología del color, WCAG 2.1 AA y OWASP Top 10:2025 (Tablas 29 a 35, Fig. 83 a 96); 3.3.3 Capacidad CMMI-DEV niveles 0 a 3 (Tablas 36 a 38, Fig. 97 a 119); 3.3.4 Plan de mejora CAR y 5 porqués (Tablas 39 a 41).
     - 3.4 Unidad IV: 3.4.1 Administración del cambio en GitHub (RFC #14 a #20, ruleset ownermerge, code review verificado con PR #36 y #37, Fig. 120 a 124, Tabla 42); 3.4.2 Gestión de versiones (GitFlow, tags semánticos v1.0 a v4.0.1, catálogo de GitHub Releases, Fig. 125 a 128, Tablas 43 y 44); 3.4.3 Automatización CI/CD con filtro de rutas (Fig. 129, 130, 134); 3.4.4 Mejora continua SCM con ciclo PDCA de 12 dominios, matriz unificada de trazabilidad SCM (Tabla 45), tabla de indicadores antes/después (Tabla 46) y cuadro PDCA (Tabla 47). Incluye las 6 capturas obligatorias del laboratorio SCM con rutas relativas funcionales.
  6. Sección 4 (Conclusiones): 5 conclusiones (Unidades I a IV + producto).
  7. Sección 5 (Recomendaciones): 6 recomendaciones concretas derivadas de los pendientes del PDCA y de T-026.
  8. Referencias Bibliográficas: 32 referencias en formato ISO 690:2021 numérico, ordenadas por estricta primera aparición [1..32] con correspondencia recíproca al 100% con las citas del texto.
  9. Anexos: ANEXO A (Repositorio GitHub actualizado con v4.0.1, main/develop, ruleset); ANEXO B (Video demostrativo `Porras-Auqui-Huamani-video-unidad-IV.mp4` y marcador `[ENLACE_VIDEO_POR_PUBLICAR]`); ANEXO C (Guión técnico con marcador `<!-- GUION_VIDEO_UNIDAD_IV -->`); ANEXO D (Tabla 48: Cotejo exhaustivo de las 32 referencias). Sin rúbrica S12 al final.
- Verificación exhaustiva aprobada (`scratch/verify_final.py`):
  - 48 tablas estrictamente correlativas del 1 al 48 sin duplicados ni vacíos.
  - 134 figuras estrictamente correlativas del 1 al 134 sin duplicados ni vacíos.
  - 134 imágenes verificadas en disco (rutas relativas existentes desde `entregables/semana-15/`).
  - 32 citas en texto y 32 referencias bibliográficas en recíproco 100%.
  - 6 capturas obligatorias de la guía de laboratorio SCM presentes.
- Siguiente paso:
  1. Completar la grabación y locución del video demostrativo de la Unidad IV y publicar el enlace en el Anexo B.
  2. Completar el guión técnico en el Anexo C (`<!-- GUION_VIDEO_UNIDAD_IV -->`).
  3. Exportar el informe a formato PDF y DOCX en `exportados/semana-15/`.

