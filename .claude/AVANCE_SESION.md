# Avance de la sesión en curso

Archivo vivo para continuar el trabajo en un chat nuevo. Actualizarlo durante la sesión. Al cerrar la tarea, mover el detalle a `coordinacion/informes/` y dejar aquí solo el enlace.

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

## Siguiente paso

1. El usuario ejecuta `%TEMP%\limpieza_demo_anemia.sql` en Supabase (cubre los DEMO de ensayos y grabación).
2. Decidir si se quita el aviso de traducción y se vuelve a grabar, o la compañera recorta la escena 5.
3. Locución de la compañera, subida a Drive y enlace en el Anexo A del informe S12; cerrar T-022 con informe en `coordinacion/informes/`.

## T-023 — Cierre de la entrega S13 (Huamani R., 13/11/2026)

- Hecho: `exportados/semana-13/` con el informe S13 (DOCX y PDF), el cuadro PDCA y el informe del laboratorio SCM; informe `coordinacion/informes/2026-11-13_documentador_T-023.md`; fila T-023 en el tablero.
- Hecho directamente, sin delegar en `agy`: no está instalado en este entorno y la tarea es copiar archivos ya generados y redactar el informe de cierre.
- Siguiente paso: entrega en el aula virtual por el equipo; aprobación de las RFC y protección de ramas por el Leader.
