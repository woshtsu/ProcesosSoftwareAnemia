# Video demostrativo — Anemia Junín v4.0.0-inc4

Respaldo de la demostración: `demo_anemia_junin_v4.mp4` (5:59, 1920x1080, **sin pista de audio**; el guion apuntaba a 5:00).
Es la grabación de T-022 del 09/11/2026 **sobre producción** (<https://softwareanemia-virginia.onrender.com>), con datos sintéticos «DEMO»
(DNI 7999xxxx) que se borran de la base al terminar. La locución (`GUION_LOCUCION.md`) y el recorte a 4:50-5:10 están pendientes del equipo.
El archivo está versionado en este directorio y la copia para el aula está en Drive (Anexo A del informe). Corrección T-026 (15/11/2026): este párrafo describía antes una grabación local de 1280x720.

El procedimiento siguiente (`grabar_demo.py`) regenera una **variante local** con datos sintéticos y login simulado; no es el archivo del repositorio.

## Regenerarlo

Desde la raíz del repositorio, con el entorno virtual del proyecto (Playwright, Pillow, uvicorn) y Chromium ya instalado
(no se ejecuta `playwright install`), `ffmpeg` disponible y el puerto 8770 libre:

```bash
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python entregables/semana-12/video/grabar_demo.py
```

El script crea una base SQLite temporal, levanta la aplicación en `127.0.0.1:8770`, graba la interfaz con
`record_video_dir` (viewport 1280x720, rótulo de sección y cursor visibles), genera la portada y las diapositivas con Pillow
(capturas reales de `semana-10/evidencias/github/`), monta todo con ffmpeg y borra los temporales al terminar.
Variables opcionales: `PERFIL=1` (imprime el tiempo de cada rótulo), `CONSERVAR_WEBM=1` (deja el webm de la interfaz
en esta carpeta), `DESFASE_VIDEO=<s>` (ajuste fino del corte).

## Duración real por sección (última grabación: 5:10)

| Sección | Desde | Hasta | Duración |
|---|---|---|---|
| Portada | 0:00 | 0:15 | 0:15 |
| PMV · Incremento 1 (RF-01..RF-05): login, validación, registro, Hb ajustada, expediente, seguimiento, reporte | 0:15 | 1:17 | 1:02 |
| Incremento 2 (RF-06..RF-09): agenda normativa, alertas, agenda del personal, asistencia/inasistencia | 1:17 | 2:17 | 1:00 |
| Incremento 3 (HIST-3.1..3.4, VIS-3.5): sin conexión, «2 pendientes», sincronización sin duplicados, conflicto, visitas priorizadas | 2:17 | 3:46 | 1:29 |
| Incremento 4 (HIST-4.1..4.4): recordatorios SIMULADOS y métricas, «No puede», barreras, alerta crítica | 3:46 | 4:38 | 0:53 |
| Calidad y arquitectura (hexagonal, pruebas de dependencias, Actions en verde, etiquetas) y cierre | 4:38 | 5:10 | 0:32 |

Los tiempos varían unos segundos entre ejecuciones.

## Para la entrega

El equipo debe **regrabar sobre producción** (<https://softwareanemia.onrender.com>) siguiendo las mismas secciones y el
mismo rótulo, usando `GUION_DEMO.md` y solo datos sintéticos (nunca datos reales de niños). Este mp4 sirve de respaldo.
