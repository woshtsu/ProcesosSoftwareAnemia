# Guion ejecutable de la demostración (5:00) — Anemia Junín v4.0-Inc4

Este guion es la versión ejecutable del Anexo C de [`../Informe_Integrador_S12_Anemia_Junin.md`](../Informe_Integrador_S12_Anemia_Junin.md). Está escrito para que otro agente o integrante grabe el video con Playwright (Python, Chromium) sobre datos sintéticos, sin tocar producción ni datos reales.

Salida esperada: `entregables/semana-12/video/demo_anemia_junin_v4.webm` (respaldo local; el enlace de Drive está pendiente de que lo suba el equipo). **Este archivo no se genera aquí.**

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
- Comprobación previa: `GET http://127.0.0.1:8765/api/salud` debe responder la versión `4.0.0-inc4`.
- Datos sembrados esperados: 27 niños, 6 con anemia moderada, 9 controles vencidos (7 ALTA, 1 MEDIA, 1 BAJA), 13 controles registrados, 24 recordatorios simulados, 18 visitas priorizadas (puntaje de 49,5 a 25,0).
- Contexto de grabación: viewport 1280x720, `locale="es-PE"`, `timezone_id="America/Lima"`, `record_video_dir` y `record_video_size` 1280x720 (misma configuración de `scripts/grabar_demo.py`, que es de v1.0 y se toma solo como referencia de la leyenda superpuesta).
- Los DNI usados son sintéticos (72000001, 71000001, 71000022, 72300001, 72300003, 72300004). No usar DNI reales ni datos del dataset DIRESA en la grabación.

## 2. Convenciones

- Los selectores son atributos `data-testid` (ej.: `[data-testid="tab-registro"]`). Los campos del formulario usan `id` (`#dni`, `#nombres`, ...).
- Esperar siempre el resultado visible (`expect`/`wait_for_selector`) antes de seguir; las pausas fijas son solo para que el espectador lea (1 a 3 s).
- Sobre cada escena puede inyectarse una leyenda inferior con el texto de la columna «Locución abreviada» (función `leyenda` de `grabar_demo.py`).
- Los tiempos son objetivo; el total debe quedar entre 4:50 y 5:10.

## 3. Escenas

### Escena 1 — 00:00 a 00:30 · Inicio de sesión (AUTH)

- **Nota importante.** Con `AUTH_MODE=demo` no hay pantalla de inicio de sesión. La pantalla solo aparece con `AUTH_MODE=supabase` y Supabase simulado (el mismo montaje de `tests/e2e/test_login.py`). Dos opciones:
  1. Grabar esta escena aparte con el montaje de `test_login.py` (proveedor simulado, usuario de prueba), y unirla a las demás con un editor.
  2. Omitirla en la grabación continua y dejar la locución sobre la pantalla de registro, indicando que la sesión demo está precargada.
- **Qué mostrar:** pantalla de acceso, ingreso de credenciales de prueba (valores ficticios del test, nunca cuentas reales), entrada a la aplicación.
- **Esperado:** redirección a la aplicación; la cabecera muestra la sesión activa.
- **Criterio:** AUTH, sesión con cookies HttpOnly y CSRF.

### Escena 2 — 00:30 a 01:15 · Registro y clasificación (RF-01, RF-03)

1. `goto http://127.0.0.1:8765/`; clic en `[data-testid="tab-registro"]`.
2. Completar: `#dni`=`72000001`, `#nombres`=`Lucía`, `#apellidos`=`Quispe Rojas`, `#sexo`=`F`, `#fecha_nacimiento`=`2025-09-10`, `#comunidad`=`Comunidad de prueba`, `#altitud_m`=`3720`, `#tutor_nombre`=`Tutor de prueba`, `#hemoglobina_observada`=`11.6`, `#peso_kg`=`6.8`, `#talla_cm`=`62`, `#fecha`=fecha de hoy.
3. Esperar `[data-testid="clasificacion-previa"]`.
   - **Esperado:** «Anemia moderada»; hemoglobina ajustada por altitud 9,1 g/dL.
4. Clic en `[data-testid="guardar"]`.
   - **Esperado:** el niño aparece en `[data-testid="tabla-evaluaciones"]`.
5. Validación (opcional, 5 s): repetir con `#dni`=`123` y `#hemoglobina_observada`=`25`, guardar.
   - **Esperado:** mensaje de error por datos inválidos (la API responde 422); no se guarda.
6. Locución: el sistema clasifica y no diagnostica ni prescribe.

### Escena 3 — 01:15 a 02:00 · Seguimiento, agenda y alertas (RF-04, RF-06, RF-07, RF-08)

1. Clic en `[data-testid="tab-expediente"]`; buscar `71000001` en `[data-testid="buscar"]`.
   - **Esperado:** `[data-testid="expediente"]` muestra la historia con 3 evaluaciones.
2. Clic en `[data-testid="tab-agenda"]`; buscar `71000022`.
   - **Esperado:** `[data-testid="agenda-tabla"]` con C1M CUMPLIDO, C3M VENCIDO, C6M PENDIENTE; `[data-testid="agenda-vencidos"]` indica «2 vencidos».
3. Clic en `[data-testid="tab-alertas"]`; filtrar con `[data-testid="filtro-alerta-prioridad"]`=`ALTA`.
   - **Esperado:** `[data-testid="alertas-tabla"]` con las alertas de prioridad alta (7 en los datos sembrados).
4. Opcional: `[data-testid="tab-seguimiento"]` y `[data-testid="filtro-clasificacion"]` para filtrar por «moderada».

### Escena 4 — 02:00 a 02:50 · Sin conexión, sincronización y conflicto (HIST-3.1 a 3.4)

1. Con la página controlada por el service worker (esperar `navigator.serviceWorker.ready` y recargar una vez), ejecutar `ctx.set_offline(True)`.
2. En la pestaña de registro, guardar dos niños: `72300001` y otro de prueba (p. ej. `72300002`).
   - **Esperado:** `[data-testid="indicador-sync"]` con `data-pendientes="2"`.
3. `ctx.set_offline(False)`; clic en `[data-testid="tab-sincronizacion"]`.
   - **Esperado:** el indicador baja a `data-pendientes="0"`; la sincronización es idempotente (reintentar no duplica).
4. Conflicto: usar el niño `72300003`, que tiene un conflicto sembrado. Esperar `[data-testid="conflicto"]`, elegir `[data-testid="conflicto-conservar"]`.
   - **Esperado:** aparece `[data-testid="sin-conflictos"]`.
5. Locución: la cola local (IndexedDB) y el identificador de operación evitan duplicados.

### Escena 5 — 02:50 a 03:20 · Visitas domiciliarias (VIS-3.5)

1. Clic en `[data-testid="tab-visitas"]`.
   - **Esperado:** lista ordenada por `[data-testid="visita-priorizada"]`, con `[data-testid="puntaje"]` (49,5 el mayor) y `[data-testid="desglose"]`.
2. Clic en `[data-testid="btn-visitar"]` del primero; confirmar con `[data-testid="visita-confirmar"]`.
   - **Esperado:** `[data-testid="visita-resultado"]` con el resultado registrado.

### Escena 6 — 03:20 a 04:00 · Recordatorios simulados y barreras (HIST-4.1 a 4.4)

1. Clic en `[data-testid="tab-recordatorios"]`; clic en `[data-testid="recordatorios-generar"]`.
   - **Esperado:** `[data-testid="recordatorios-resultado"]`; los recordatorios llevan `[data-testid="marca-simulado"]` (SIMULADO). **Decirlo en voz alta: no hay envío real a WhatsApp/SMS.**
2. En un `[data-testid="recordatorio"]`, clic en `[data-testid="btn-responder"]`, opción `NO_PUEDE` (`[data-testid="respuesta-opcion"]`), barrera `RECHAZO_TRATAMIENTO` (`[data-testid="respuesta-barrera"]`), confirmar `[data-testid="respuesta-confirmar"]`.
3. Verificar la alerta crítica: en `[data-testid="tab-alertas"]` debe verse `[data-testid="alerta-barrera"]` con `[data-testid="prioridad-barrera"]` y `[data-testid="razones-barrera"]` (tipo BARRERA_CRITICA, puntaje 40,0); `[data-testid="total-alertas-barreras"]` se incrementa.
4. Opcional: `[data-testid="btn-barrera-nino"]` para registrar una barrera por niño (`[data-testid="barrera-tipo"]`, `[data-testid="barrera-confirmar"]`).
5. Nota para la locución: el webhook de WhatsApp en modo simulado responde 200 pero no registra respuestas; la respuesta de esta escena se registra desde la interfaz.

### Escena 7 — 04:00 a 04:15 · Reporte (RF-05)

1. Clic en `[data-testid="tab-reporte"]`; clic en `[data-testid="generar-reporte"]`.
   - **Esperado:** `[data-testid="kpi-registrados"]` con el total de niños registrados (incluye los creados en la grabación).

### Escena 8 — 04:15 a 05:00 · Arquitectura, CI y limitaciones

Esta escena no usa la aplicación. Abrir en el navegador, con zoom legible:

1. `https://github.com/woshtsu/ProcesosSoftwareAnemia/tree/v4.0-Inc4/pmv_fastapi/app` — mostrar `domain/`, `ports/`, `adapters/`, `application/` y `main.py`.
2. Pestaña Actions del mismo repositorio — ejecución verde del CI (#16 sobre el PR #8).
3. Cierre con las limitaciones declaradas: envío real no probado, proveedor de identidad simulado, rendimiento p95 de 1,1 s a vigilar, hallazgos OWASP abiertos.

## 4. Verificación posterior

- Duración total del `.webm` entre 4:50 y 5:10.
- Cada pantalla de la columna «Pantalla» del Anexo C aparece en el orden indicado.
- Ninguna pantalla muestra contraseñas, tokens ni datos personales reales.
- Detener el servidor, borrar `demo_s12.db` y el directorio temporal de video de Playwright.
- Subir el archivo a Drive y reemplazar `[pendiente: enlace de Drive]` en el Anexo A del informe.
