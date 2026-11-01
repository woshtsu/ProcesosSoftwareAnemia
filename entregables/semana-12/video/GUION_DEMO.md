# Guion ejecutable de la demostración (5:00) — Anemia Junín v4.0-Inc4

Este guion es la versión ejecutable del Anexo C de [`../Informe_Integrador_S12_Anemia_Junin.md`](../Informe_Integrador_S12_Anemia_Junin.md). Está escrito para que otro agente o integrante grabe el video con Playwright (Python, Chromium) sobre datos sintéticos, sin tocar producción ni datos reales.

**El video no muestra el informe.** Va directo al software y rotula en pantalla qué parte se demuestra: **PMV · Incremento 1**, **Incremento 2**, **Incremento 3** e **Incremento 4**; abre con una portada de 15 s y cierra con calidad y arquitectura.

Salida esperada: `entregables/semana-12/video/demo_anemia_junin_v4.mp4` (respaldo local; el enlace de Drive está pendiente de que lo suba el equipo). Playwright graba `.webm`; convertirlo a `.mp4` con `ffmpeg` (H.264, 1280x720) y borrar el `.webm`. **Este archivo no se genera aquí.**

## 1. Preparación (una sola vez)

Todos los comandos se ejecutan desde `pmv_fastapi/`, con el entorno virtual del proyecto activado y `playwright install chromium` ya hecho.

```bash
export AUTH_MODE=demo
export DATABASE_URL=sqlite:///./demo_s12.db
export WHATSAPP_APP_SECRET=secreto-de-prueba
export WHATSAPP_VERIFY_TOKEN=token-de-prueba

python -m scripts.cargar_datos_prueba
python -m uvicorn app.main:crear_app --factory --port 8765
```

- La base `demo_s12.db` es temporal y descartable; borrarla al terminar. No se versiona.
- Comprobación previa: `GET http://127.0.0.1:8765/api/salud` debe responder la versión `4.0.0-inc4`. (La producción, <https://softwareanemia.onrender.com>, responde la misma versión con reloj fijo al 30/06/2024; **no se usa para grabar** porque escribiría datos en ella.)
- Datos sembrados esperados: 27 niños, 6 con anemia moderada, 9 controles vencidos (7 ALTA, 1 MEDIA, 1 BAJA), 13 controles registrados, 24 recordatorios simulados, 18 visitas priorizadas (puntaje de 49,5 a 25,0).
- Contexto de grabación: viewport 1280x720, `locale="es-PE"`, `timezone_id="America/Lima"`, `record_video_dir` y `record_video_size` 1280x720 (misma configuración de `scripts/grabar_demo.py`, que es de v1.0 y se toma solo como referencia de la leyenda superpuesta).
- Los DNI usados son sintéticos (72000001, 71000001, 71000022, 71000018, 72300001, 72300003, 72300004). No usar DNI reales ni datos del dataset DIRESA en la grabación.

## 2. Convenciones

- Los selectores son atributos `data-testid` (ej.: `[data-testid="tab-registro"]`). Los campos del formulario de registro usan `id` (`#dni`, `#nombres`, ...); la búsqueda de expediente usa `[data-testid="buscar-dni"]` con `#btn-buscar-dni`.
- Esperar siempre el resultado visible (`expect`/`wait_for_selector`) antes de seguir; las pausas fijas son solo para que el espectador lea (1 a 3 s).
- **Rótulo de parte.** Al empezar cada bloque (escenas 1, 2, 3 y 4) inyectar sobre la página una banda superior fija, visible durante todo el bloque, con el texto exacto: `PMV · Incremento 1 (v1.0-PMV)`, `Incremento 2 (v2.0-Inc2)`, `Incremento 3 (v3.0-Inc3)` o `Incremento 4 (v4.0-Inc4)`. Debajo, una leyenda inferior con la locución abreviada (función `leyenda` de `grabar_demo.py`). Sin rótulo no se considera cumplido el requisito del equipo.
- Los tiempos son objetivo; el total debe quedar entre 4:50 y 5:10. Entre paréntesis, el RF o historia que cubre cada paso.

## 3. Escenas

### Escena 0 — 00:00 a 00:15 · Portada

- Tarjeta de título (HTML inyectado con `page.set_content` o banda sobre la aplicación): «Anemia Junín · v4.0-Inc4» y los cuatro rótulos: PMV · Incremento 1, Incremento 2, Incremento 3, Incremento 4.
- Locución: sistema web progresivo para el seguimiento de la anemia infantil en postas de Junín; se mostrarán el PMV y los incrementos 2, 3 y 4, cada uno rotulado; los datos son sintéticos.
- Con `AUTH_MODE=demo` no hay pantalla de inicio de sesión. La autenticación no se graba; su evidencia es la ficha AUTH del informe (3.6.4).

### Escena 1 — 00:15 a 01:15 · Rótulo «PMV · Incremento 1» (RF-01 a RF-05)

1. **00:15 · Registro y clasificación (RF-01, RF-03).** `goto http://127.0.0.1:8765/`; clic en `[data-testid="tab-registro"]`. Completar: `#dni`=`72000001`, `#nombres`=`Lucía`, `#apellidos`=`Quispe Rojas`, `#sexo`=`F`, `#fecha_nacimiento`=`2025-09-10`, `#comunidad`=`Comunidad de prueba`, `#altitud_m`=`3720`, `#tutor_nombre`=`Tutor de prueba`, `#hemoglobina_observada`=`11.6`, `#peso_kg`=`6.8`, `#talla_cm`=`62`, `#fecha`=fecha de hoy.
   - Esperar `[data-testid="clasificacion-previa"]`. **Esperado:** «Anemia moderada»; hemoglobina ajustada por altitud 9,1 g/dL.
   - Clic en `[data-testid="guardar"]`. **Esperado:** el niño aparece en `[data-testid="tabla-evaluaciones"]` (menos de 2 s).
   - Validación (5 s): repetir con `#dni`=`123` y `#hemoglobina_observada`=`25`. **Esperado:** mensaje de error por campo (la API responde 422); no se guarda. Un DNI repetido responde 409.
   - Locución: el sistema clasifica; no diagnostica ni prescribe.
2. **00:40 · Expediente (RF-02).** Clic en `[data-testid="tab-expediente"]`; `[data-testid="buscar-dni"]`=`71000001`; clic en `#btn-buscar-dni`. **Esperado:** `[data-testid="tabla-evaluaciones"]` con 2 evaluaciones. En `#form-control` completar `hemoglobina_observada`=`11.5`, `peso_kg`=`8.2`, `talla_cm`=`69` y clic en `[data-testid="guardar-control"]`. **Esperado:** 3 evaluaciones.
3. **00:55 · Seguimiento (RF-04).** Clic en `[data-testid="tab-seguimiento"]`; `[data-testid="filtro-clasificacion"]` = «Moderada». **Esperado:** listado filtrado (6 niños de la base sembrada, más los creados en la grabación).
4. **01:05 · Reporte (RF-05).** Clic en `[data-testid="tab-reporte"]`; clic en `[data-testid="generar-reporte"]`. **Esperado:** `[data-testid="kpi-registrados"]` con el total de niños registrados; `[data-testid="descargar-csv"]` disponible.

### Escena 2 — 01:15 a 02:10 · Rótulo «Incremento 2» (RF-06 a RF-09)

1. **01:15 · Agenda del expediente (RF-06).** `tab-expediente`; buscar `71000022`. **Esperado:** `[data-testid="agenda-tabla"]` con 13 controles; C1M CUMPLIDO y C3M VENCIDO; `[data-testid="agenda-vencidos"]` indica «2 vencidos».
2. **01:30 · Alertas (RF-07).** Clic en `[data-testid="tab-alertas"]`; `[data-testid="filtro-alerta-prioridad"]`=`ALTA`. **Esperado:** `[data-testid="alertas-tabla"]` con las alertas de prioridad alta (7 en los datos sembrados; 9 vencidos en total sin filtro).
3. **01:45 · Agenda del personal (RF-08).** Clic en `[data-testid="tab-agenda"]`; `[data-testid="agenda-desde"]`=hoy, `[data-testid="agenda-hasta"]`=hoy + 30 días; clic en `[data-testid="agenda-consultar"]`. **Esperado:** `[data-testid="agenda-personal-tabla"]` con los controles por día (17 controles de 14 niños en los datos sembrados). Opcional (5 s): `agenda-hasta`=hoy + 40 días muestra `[data-testid="agenda-error"]` (rango mayor de 31 días).
4. **02:00 · Inasistencia (RF-09).** `tab-expediente`; buscar `71000018`; en la fila de un control vencido (`[data-testid="agenda-tabla"] tr[data-estado="VENCIDO"]`) clic en `[data-testid="btn-no-asistio"]`; en `[data-testid="modal-asistencia"]` elegir `[data-testid="asistencia-motivo"]`=`Enfermedad del niño`, `[data-testid="asistencia-detalle"]`=`Fiebre`, clic en `[data-testid="asistencia-confirmar"]`. **Esperado:** `[data-testid="marca-inasistencia"]` con «Inasistencia registrada»; en «Alertas» la fila de 71000018 muestra la marca y prioridad MEDIA.

### Escena 3 — 02:10 a 03:20 · Rótulo «Incremento 3» (HIST-3.1 a 3.4, VIS-3.5)

1. **02:10 · Sin conexión (HIST-3.1).** Con la página controlada por el service worker (esperar `navigator.serviceWorker.ready` y recargar una vez), ejecutar `ctx.set_offline(True)`. En la pestaña de registro guardar un niño (`72300001`, Hb 9,4) y, en su expediente, un control (Hb 10,1; 8,6 kg; 72 cm). **Esperado:** `[data-testid="indicador-sync"]` con `data-pendientes="2"` y el texto «2 pendientes».
2. **02:30 · Pendientes y antigüedad (HIST-3.4).** Clic en `[data-testid="tab-sincronizacion"]`. **Esperado:** `[data-testid="sync-resumen"]` con la cantidad de pendientes y desde cuándo; filas `[data-testid="pendiente"]`.
3. **02:40 · Sincronización (HIST-3.2).** `ctx.set_offline(False)`. **Esperado:** el indicador baja a `data-pendientes="0"` («Al día»); la sincronización es idempotente (reenviar la misma operación se marca DUPLICADA y no duplica).
4. **02:55 · Conflicto (HIST-3.3).** Usar el niño `72300003`, que tiene un conflicto sembrado. Esperar `[data-testid="conflicto"]`, elegir `[data-testid="conflicto-conservar"]`. **Esperado:** aparece `[data-testid="sin-conflictos"]`.
5. **03:05 · Visitas (VIS-3.5).** Clic en `[data-testid="tab-visitas"]`. **Esperado:** lista ordenada (`[data-testid="visita-priorizada"]`) con `[data-testid="puntaje"]` (49,5 el mayor) y `[data-testid="desglose"]`. Clic en `[data-testid="btn-visitar"]` del primero; `[data-testid="visita-resultado"]`=`REALIZADA`, `[data-testid="visita-suplemento"]`=`SI`, `[data-testid="visita-observaciones"]`=`Familia receptiva`; confirmar con `[data-testid="visita-confirmar"]`. **Esperado:** el modal se cierra y el niño sale del primer lugar.
6. Locución: la cola local (IndexedDB) y el identificador de operación evitan duplicados; los pesos del puntaje son una propuesta sin validar con la microred.

### Escena 4 — 03:20 a 04:30 · Rótulo «Incremento 4» (HIST-4.1 a 4.4)

1. **03:20 · Recordatorios (HIST-4.1).** Clic en `[data-testid="tab-recordatorios"]`; clic en `[data-testid="recordatorios-generar"]`. **Esperado:** `[data-testid="recordatorios-resultado"]`; los recordatorios llevan `[data-testid="marca-simulado"]` (SIMULADO), 24 en los datos sembrados. **Decirlo en voz alta: no hay envío real a WhatsApp/SMS.**
2. **03:40 · Respuesta del tutor (HIST-4.2).** En un `[data-testid="recordatorio"]`, clic en `[data-testid="btn-responder"]`, opción `NO_PUEDE` (`[data-testid="respuesta-opcion"]`), barrera `RECHAZO_TRATAMIENTO` (`[data-testid="respuesta-barrera"]`), confirmar `[data-testid="respuesta-confirmar"]`. **Esperado:** «Respuesta registrada». Nota para la locución: el webhook de WhatsApp responde 403 sin firma o con firma inválida; con firma válida responde 200 pero, en modo simulado, no registra respuestas, de modo que la respuesta de esta escena se registra desde la interfaz.
3. **03:55 · Barrera por niño, también sin conexión (HIST-4.3).** Abrir un expediente; clic en `[data-testid="btn-barrera-nino"]`; `[data-testid="barrera-tipo"]` (p. ej. «Falta de transporte») y detalle; `[data-testid="barrera-confirmar"]`. **Esperado:** la barrera aparece en `[data-testid="barreras-nino-tabla"]`; si se hace con `ctx.set_offline(True)` queda `[data-testid="barrera-pendiente"]` y se sincroniza al reconectar.
4. **04:10 · Barreras críticas (HIST-4.4).** `[data-testid="tab-alertas"]`: debe verse `[data-testid="alerta-barrera"]` con `[data-testid="prioridad-barrera"]` y `[data-testid="razones-barrera"]` (tipo BARRERA_CRITICA); `[data-testid="total-alertas-barreras"]` se incrementa. Luego `[data-testid="tab-visitas"]`: la fila del niño muestra el componente BARRERA_CRITICA (40,0 puntos) en `[data-testid="desglose"]`.

### Escena 5 — 04:30 a 05:00 · Calidad y arquitectura

Esta escena no usa la aplicación ni el informe. Abrir en el navegador, con zoom legible:

1. **04:30** `https://github.com/woshtsu/ProcesosSoftwareAnemia/tree/v4.0-Inc4/pmv_fastapi/app`: mostrar `domain/`, `ports/`, `adapters/`, `application/` y `main.py` (arquitectura hexagonal).
2. **04:42** Pestaña Actions del mismo repositorio: ejecución verde del CI (#16 sobre el PR #8).
3. **04:52** `https://github.com/woshtsu/ProcesosSoftwareAnemia/tags`: las etiquetas `v1.0-PMV`, `v2.0-Inc2`, `v3.0-Inc3` y `v4.0-Inc4`.
4. Cierre de la locución con las limitaciones declaradas: envío real no probado, proveedor de identidad simulado, rendimiento p95 de 1,1 s a vigilar, 12 hallazgos OWASP abiertos y validación en una posta pendiente.

## 4. Verificación posterior

- Duración total del `.mp4` entre 4:50 y 5:10.
- Cada bloque muestra su rótulo (PMV · Incremento 1, Incremento 2, Incremento 3, Incremento 4) durante toda la parte; ninguna escena muestra el informe.
- Cada pantalla de la columna «Pantalla mostrada» del Anexo C aparece en el orden indicado.
- Ninguna pantalla muestra contraseñas, tokens ni datos personales reales.
- Detener el servidor, borrar `demo_s12.db`, el `.webm` intermedio y el directorio temporal de video de Playwright.
- Subir el archivo a Drive y reemplazar `[pendiente: enlace de Drive]` en el Anexo A del informe.
