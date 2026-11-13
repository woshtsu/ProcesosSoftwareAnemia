# Adenda v4.0 al informe GQM de la semana 9 — referencia para el informe integrador S12

Fecha de recálculo: 30/10/2026. Código evaluado: rama `docs/s12-integrador`, commit `e6886e2` (`4.0.0-inc4`; etiqueta prevista `v4.0-Inc4`, no existe en el clon local).

## 1. Propósito y alcance

- Reunir los valores GQM actualizados de Inc. 1 a Inc. 4 como **insumo del informe integrador S12**. El informe entregado en la semana 9 (`Entregable_Semana9_Anemia_Junin.md`) **no cambia**: sus cifras son las de `v1.0-PMV` y `v2.0-Inc2`.
- Se reutilizaron los scripts de `.claude/herramientas/gqm/` con las fórmulas de la Tabla 12 del informe S9. Las salidas nuevas están en `metricas/salidas/` con sufijo `_v4`; `metricas/datos/` (S9) no se tocó.
- Las columnas Inc. 1 e Inc. 2 se copian de `metricas/datos/*.json` (S9). Inc. 3 e Inc. 4 son mediciones nuevas, salvo donde se indica «no recalculada».
- Atención: en estas salidas la clave de versión del script sigue siendo `v2.0` (el script apunta a `GQM_RAIZ_V20`); el contenido es el código de Inc. 3 (`e920820`, exportado con `git archive` a un directorio temporal) o de Inc. 4.

## 2. Métricas GQM por incremento

| Métrica | Inc. 1 (`v1.0-PMV`) | Inc. 2 (`v2.0-Inc2`) | Inc. 3 (`e920820`) | Inc. 4 (`e6886e2`) | Fuente / comando del valor nuevo |
| --- | --- | --- | --- | --- | --- |
| M1.1 contaminación del dominio | 0,0 % (0/8 clases) | 0,0 % (0/32) | 0,0 % (0/55) | 0,0 % (0/86) | `python m11_contaminacion.py --version v2.0 --json ../../entregables/semana-09/metricas/salidas/m11_contaminacion_v4.json` |
| M1.2 conformidad hexagonal (estricta) | 40,0 % (2/5) | 100,0 % (5/5) | 100,0 % (5/5) | 100,0 % (5/5) | `m12_conformidad.py` igual; `salidas/m12_conformidad_v4.json` |
| M1.2 ultra estricta (sensibilidad) | 20,0 % | 100,0 % | 80,0 % | 80,0 % | idem; ver hallazgo 1 de la sección 7 |
| M1.3 violaciones de la regla de dependencia | 1 | 0 | 0 | 0 | `m13_acoplamiento.py`; `salidas/m13_acoplamiento_v4.json` (I del dominio = 0,00) |
| M2.1 cobertura funcional con capturas | 100 % (5/5 RF) | 100 % (4/4 RF; 9/9 acumulado) | **no recalculada** | **no recalculada** | Ver nota 1 |
| M2.2 defectos funcionales (Def/RF) | 1,4 (7/5) | 0,25 (1/4) | **no recalculada** (indicativo 0,20) | **no recalculada** (indicativo 0,75) | Ver nota 2 |
| M3.1 principal (Σ ÷ 6) | 25,0 % (1,5/6) | 33,3 % (2,0/6) | 50,0 % (3,0/6) | **75,0 %** (4,5/6) | `m31_brechas_v4.py --version v3.0\|v4.0` (con `GQM_RAIZ_V20`); `salidas/m31_brechas_v4.json` |
| M3.1 complementaria (brechas comprometidas) | 100,0 % (B1) | 75,0 % (B1, B2) | 75,0 % (B1, B2, B4, B6: 3,0/4) | **90,0 %** (B1, B2, B3, B4, B6: 4,5/5) | idem |
| M3.1 estricta (solo puntaje 1,0) | 16,7 % (1/6) | 16,7 % (1/6) | 33,3 % (2/6) | **66,7 %** (4/6) | idem |
| M3.2 índice de impacto en valor (V1, V2, V3) | 57,6 % | 100,0 % | 100,0 % | 100,0 % | `m32_valor.py` (V1, V2, V3); `salidas/m32_valor_v3_v4.json` y `m32_valor_v4.json`; nota 3 |
| V3 F1 de vencidos frente al oráculo (B150) | 0,729 | 1,000 (476/476 controles) | 1,000 (476/476) | 1,000 (476/476) | idem |
| p95 agregado, mix común (V4) | 175 ms (2 corridas) | 815 ms (2 corridas) | **no medido** | **1 100 ms** (1 corrida) | `ejecutar_carga.py --corridas v20_comun:1`; `salidas/m32_carga_v4.json`; nota 4 |
| Disponibilidad durante la carga (V5) | 100 % (S9: 856/856 sondas, tres versiones) | 100 % (idem) | no medida | 100 % (64/64; sin sesión de 10 min) | `salidas/m32_disponibilidad_v4.json` |

Metas de la guía: M1.1 0 %; M1.2 100 %; M2.1 100 %; M2.2 ≤ 1,0 (Inc. 1) y ≤ 0,2 (Inc. 2); M3.1 ≥ 60 % (Inc. 1) y ≥ 90 % (Inc. 2); M3.2 ≥ 50 % y ≥ 80 %. La guía no fija metas para Inc. 3 e Inc. 4. Con las metas acumuladas propuestas en la sección 6.4 del informe S9 (no aprobadas: INC-3 50,0 % e INC-4 66,7 %), la lectura principal de M3.1 las alcanza (50,0 % y 75,0 %).

**Notas.**

1. **M2.1.** Las capturas de HIST-3.1 a HIST-3.4, VIS-3.5 y HIST-4.1 a HIST-4.4 no se generaron (se pidió no regenerarlas) y `m21_cobertura_rf.py` solo tiene el mapa curado de RF-01 a RF-09. No se inventa un porcentaje. Dato de contexto, no es M2.1: hay 11 pruebas E2E nuevas (7 de Inc. 3 y 4 de Inc. 4) y los criterios Dado-Cuando-Entonces están en `coordinacion/TABLERO.md`.
2. **M2.2.** No existe registro de defectos posterior a DEF-09 (`pmv_fastapi/docs/evidencias/registro_defectos_inc2.md`). Los cuatro hallazgos corregidos de la revisión independiente (sección 7) no se registraron como DEF. Si se contaran: Inc. 3, 1 hallazgo (sincronización) ÷ 5 historias = 0,20; Inc. 4, 3 hallazgos (webhook, doble envío, recorte de detalle) ÷ 4 historias = 0,75. La atribución a cada incremento es del autor de la adenda. Son indicativos, no M2.2 oficial: antes de citarlos en S12 debe decidirse si se registran como DEF-10 a DEF-13.
3. **M3.2.** V1 = 1 escritura por evaluación; V2 = 140/140 activos con agenda; V3 = F1 1,000 con B150 y `FECHA_REFERENCIA=2026-10-16`. En la primera corrida de V1 con el reloj fijado a 16/10 la comprobación «reporte cuenta la evaluación» dio `false`: la sonda consulta el reporte por la fecha del servidor, pero la evaluación queda registrada con la hora real del 30/10. Se repitió V1 con el servidor sin `FECHA_REFERENCIA` y dio `true` en Inc. 3 e Inc. 4. Las salidas guardan la segunda ejecución. Sigue siendo el índice de V1 a V3 (no incluye V4, V5 ni V6).
4. **p95.** Una sola corrida (50 usuarios, 10/s, 60 s, SQLite nueva, B150, `AUTH_MODE=demo`, 2 CPU compartidas): 1 960 solicitudes, 0 fallos, mediana 120 ms, p99 1 800 ms, máximo 2 897 ms, 33,2 solicitudes/s. Por endpoint (p95): `GET /api/ninos` 1 200, `GET /api/ninos/{id}` 870, `GET /api/reportes/periodo` 1 200, `POST /api/ninos` 1 300, `POST /api/validaciones/evaluacion` 210 ms. Frente a Inc. 2 (815 ms, corridas de 790 y 840) sube 35 %, y el máximo supera 2 s en una solicitud. **No se pudo repetir v1.0 en la misma sesión como control**: el conjunto B150 ya no carga en v1.0 con el reloj real del 30/10 (2 niños superan los 59 meses y el arnés aborta), así que la causa del aumento (código nuevo, autenticación o máquina) no está aislada. No se midieron los endpoints nuevos (sin tareas de Locust).

## 3. M3.1: puntaje por brecha y evidencia en el código

Misma regla del S9: 1 = mecanismo TO-BE completo, operativo y probado; 0,5 = parcial; 0 = no. Evidencia en `salidas/m31_brechas_v4.json` (rutas HTTP presentes, archivos, palabras clave en `app/`).

| Brecha | Plan | Inc. 2 (S9) | Inc. 3 | Inc. 4 | Evidencia del código y de las pruebas (Inc. 4) |
| --- | --- | --- | --- | --- | --- |
| B1 Triple registro manual | INC-1 | 1,0 | 1,0 | 1,0 | V1 = 1 escritura por evaluación (`m32_valor.py`, sección V1); sin cambios |
| B2 Agenda sin recordatorios | INC-2 | 0,5 | 0,5 | **1,0** | `POST /api/recordatorios/generar`, `GET /api/recordatorios`, `POST /api/recordatorios/{id}/respuesta`, webhook de WhatsApp; puerto `Notificador` con adaptadores simulado, WhatsApp Cloud y SMS (`app/adapters/outbound/notificaciones/`); 59 unitarias de recordatorios, 17 de notificadores, 41 de API y E2E CP-402. En Inc. 3 sigue en 0,5 (0 ocurrencias de «recordatorio»). Limitación: solo el modo simulado y `httpx.MockTransport` están probados |
| B3 Barreras ocultas | INC-4 | 0,0 | 0,0 | **1,0** | `POST/GET /api/ninos/{id}/barreras` (8 tipos, 4 fuentes), `GET /api/alertas/barreras` con `REGLAS_BARRERAS_V1` (barrera grave, recurrentes, anemia con control vencido; vigencia de 90 días), componente `BARRERA_CRITICA` en la visita; 26 unitarias, 41 de API, E2E CP-402 a CP-405 (incluye sin conexión). Reglas sin validar con la microred |
| B4 Visita domiciliaria en papel | INC-3 | 0,0 | **1,0** | 1,0 | `POST/GET /api/ninos/{id}/visitas`, `GET /api/visitas/priorizadas` (puntaje explicable `VISITA-V1`, `V2` en Inc. 4), captura sin conexión por la cola de IndexedDB (`cola.js`, `sync.js`); 34 unitarias de visitas, E2E CP-301 y CP-302. Pesos sin validar con la microred |
| B5 Riesgo identificado tarde | INC-5 | 0,0 | 0,0 | 0,0 | Sin modelo ni regla de riesgo de abandono (`abandono`: 0 ocurrencias; `riesgo`: 2, un comentario y un texto de interfaz). La visita priorizada usa controles ya vencidos e inasistencias: es reactiva. INC-5 no se implementó |
| B6 Conectividad intermitente | INC-3 e INC-6 | 0,5 | 0,5 | 0,5 | Operación sin conexión y sincronización (`POST /api/sincronizacion` idempotente, conflictos, pendientes; 37 unitarias de sincronización y 26 de conflictos; E2E CP-297 a CP-300 y CP-303). Se mantiene parcial: INC-6 no existe, no hay prueba en un dispositivo real con red intermitente (los E2E simulan la desconexión) y el alta de niños y la edición de expedientes exigen conexión |
| **Σ puntos** | | **2,0** | **3,0** | **4,5** | |

Sensibilidades de Inc. 4 (principal): B6 = 0, 66,7 %; B2 = 0,5 si se exigiera un envío real probado, 66,7 %; B5 = 0,5 si la visita priorizada contara como búsqueda activa, 83,3 %. Excluyendo B6 de las comprometidas, la complementaria sería 100 %. Lectura honesta para S12: cuatro brechas (B1 a B4) tienen mecanismo operativo y probado **en el entorno de pruebas**; ninguna se ha medido en una posta.

## 4. Pruebas, cobertura y calidad estática por incremento

| Concepto | Inc. 1 | Inc. 2 (S9) | Antes de INC-3 | Inc. 3 | Inc. 4 |
| --- | --- | --- | --- | --- | --- |
| Pruebas unitarias + integración + arquitectura | 73 | 328 (234 + 76 + 18) | 349 | 499 (331 + 147 + 21) | **660** (416 + 219 + 25) |
| Pruebas E2E (Playwright) | 4 | 15 | 17 | 24 | **28** |
| Pruebas nuevas del incremento | — | — | — | +97 unit., +50 integ., +3 arq., +7 E2E | +85 unit., +69 integ., +4 arq., +4 E2E, +3 de la revisión |
| Cobertura de líneas y ramas de `app/` | 99 % | 100 % | umbral previo 99,55 % | 99,70 % | **99,79 %** (4 025 + 675 de 4 030 + 680) |
| `ruff check` / `ruff format --check` | limpio | limpio | limpio | limpio | limpio (142 archivos) |

- Fuentes: Inc. 1 e Inc. 2, `metricas/salidas/v1.0` y `v2.0`; «antes de INC-3» e Inc. 3, informe T-019; Inc. 4, **re-ejecutado el 30/10/2026**: `pytest tests/unitarias tests/integracion tests/arquitectura --cov=app` (660 aprobadas en 43 s) y `pytest tests/e2e -m e2e --no-cov` (28 aprobadas). Extracto en `salidas/pruebas_v4.txt`. Las 660 no incluyen los E2E (688 con ellos). Inc. 3 no se re-ejecutó (cifras de T-019).
- La primera corrida E2E de este recálculo tuvo 1 fallo por tiempo de espera (`test_cp110_hist21_agenda_casos_especiales`) mientras la máquina de 2 CPU atendía otras mediciones; aislada y en la repetición sin carga pasó. Consistente con la inestabilidad de agenda corregida el 30/10 (sección 8): conviene vigilarla.
- La cobertura bajó de 100 % (S9) a 99,70 % y 99,79 % por `autenticacion.py` (94 %) y `supabase_auth.py` (97 %), incorporados con la autenticación Supabase antes de INC-3. Todos los archivos nuevos de Inc. 3 e Inc. 4 tienen 100 %.
- Contrato OpenAPI: 29 rutas en `docs/openapi.json`; `python -m scripts.exportar_openapi --verificar` al día con Python 3.13.

## 5. Requerimientos e historias por incremento

Las etiquetas son las de las etiquetas OpenAPI y del CHANGELOG. Inc. 3 e Inc. 4 no tienen número RF; se usan sus HIST.

| Incremento | Versión | Etiquetas | Contenido |
| --- | --- | --- | --- |
| Inc. 1 | `v1.0-PMV` | HU-01 a HU-05 (RF-01 a RF-05) | Registro nominal, expediente, validación clínica, seguimiento, reporte del periodo |
| Inc. 2 | `v2.0-Inc2` | HIST-2.1 a HIST-2.4 (RF-06 a RF-09) | Agenda normativa, alertas de vencidos, agenda del personal, asistencia |
| Inc. 3 | `3.0.0-inc3` | HIST-3.1 a HIST-3.4, VIS-3.5 | Registro sin conexión, sincronización, conflictos, pendientes, visita domiciliaria priorizada |
| Inc. 4 | `4.0.0-inc4` | HIST-4.1 a HIST-4.4 | Recordatorios WhatsApp con respaldo SMS (modo simulado por defecto), confirmación, barreras, alerta de barreras críticas |

## 6. Decisiones de arquitectura nuevas (ADR-011 a ADR-014)

| ADR | Decisión | Estado / nota |
| --- | --- | --- |
| ADR-011 | Supabase Auth y sesiones en el servidor (`AUTH_MODE` `supabase` por omisión; `demo` para pruebas) | Anterior a INC-3; implementado localmente; primer acceso remoto pendiente de una cuenta autorizada |
| ADR-012 | Sincronización sin conexión: cola en el dispositivo, idempotencia por `id_operacion`, conflictos explícitos que nunca se sobrescriben a ciegas | Implementado; cerrojo de concurrencia agregado en la revisión |
| ADR-013 | Visita domiciliaria priorizada con puntaje explicable (`VISITA-V1`; `V2` suma `BARRERA_CRITICA`, rango 0 a 115) | Pesos propuestos por el equipo, no norma del MINSA |
| ADR-014 | Puerto `Notificador` (simulado, WhatsApp Cloud, SMS, respaldo), respuesta del tutor, barreras y su vigencia de 90 días | Webhook falla cerrado tras la revisión; vigencia de 90 días decidida por el equipo |

## 7. Revisión independiente de Inc. 3 e Inc. 4 (commit `d2ab78b`)

Veredicto: aprobado con observaciones; sobre `git diff a8df23b..HEAD` (42 archivos de `app/`, +5 527 líneas). Corregido:

1. Seguridad, alta: el webhook de WhatsApp aceptaba cuerpos sin firma si faltaba `WHATSAPP_APP_SECRET`. Ahora falla cerrado: 503 sin secreto, 403 con firma ausente o inválida.
2. Concurrencia, media: el reenvío simultáneo del mismo `id_operacion` duplicaba una evaluación; `ServicioSincronizacion` procesa un lote a la vez (CP-264b).
3. Concurrencia, media: dos generaciones simultáneas de recordatorios enviaban el mismo mensaje dos veces; se serializan (CP-382b).
4. Interfaz, baja: el detalle de una barrera de una visita no lograda superaba 200 caracteres y el servidor lo rechazaba; DNI y celular pasan por `esc()`.

Sin corregir (aceptables para el piloto): el caché del service worker se borra al cerrar sesión pero no al vencer; la cola IndexedDB conserva datos clínicos tras cerrar sesión por diseño; un tutor con varios niños que no cita el mensaje se asocia al recordatorio sin respuesta más reciente; `id_operacion` distingue mayúsculas; sin límite de tamaño del cuerpo del webhook.

Hallazgo de este recálculo: la conformidad **ultra estricta** de M1.2 bajó de 100 % a 80 % porque `app/application/servicio_sesion.py` implementa el puerto `ProveedorIdentidad` dentro de la capa de aplicación (introducido en `49f07da`, Supabase, antes de INC-3). Las lecturas laxa y estricta siguen en 100 % y no hay violaciones de dependencia; conviene decidir si se mueve el adaptador o se documenta la excepción.

## 8. Cambios de CI del 30/10/2026

- `87c0748`: contrato OpenAPI idéntico en Python 3.11 y 3.13. FastAPI toma la descripción del estado 422 de `http.HTTPStatus`, que cambió entre 3.12 y 3.13; `scripts/exportar_openapi.py` la normaliza. Verificado en 3.11: 660 pruebas, 219 de integración contra PostgreSQL 16 y 28 E2E.
- `03719c2`: el workflow fija `ubuntu-24.04`, porque Playwright 1.56 no instala Chromium en Ubuntu 26.04 (nuevo `ubuntu-latest`).
- `e6886e2`: CP-186 inestable en CI; la prueba espera a que la agenda termine de pintarse (`data-cargando`, `to_have_count`) y el service worker pasa a `v5`.
- Antes (T-017): el workflow se movió a la raíz del repositorio; el despliegue a Render solo ocurre desde `main` y tras pasar los jobs.

## 9. Pendientes externos al software

- **Meta:** aprobación de la plantilla `recordatorio_control`; credenciales; `WHATSAPP_APP_SECRET` (obligatorio) y `WHATSAPP_VERIFY_TOKEN` en Render; registro del webhook. El envío real nunca se probó.
- **Consentimiento:** el celular del tutor viaja a Meta o al proveedor SMS; la familia debe consentir y el software no lo gestiona. Los niños del dataset DIRESA no tienen celular («sin contacto»).
- **Microred:** validar los pesos de `VISITA-V1` y `V2`, `REGLAS_BARRERAS_V1`, la vigencia de 90 días y el peso de `BARRERA_CRITICA`.
- **Posta piloto:** prueba en un dispositivo real con red intermitente; despliegue; SUS real (V6 sigue siendo un proxy).
- **Base de datos:** ejecutar `db/03_migracion_v3_0.sql`, `db/04_migracion_v4_0.sql` y `db/02_supabase.sql` en Supabase antes de desplegar; configurar Auth (ADR-011).

## 10. Riesgos y limitaciones para S12

1. p95 de 1 100 ms con una corrida y sin control; los endpoints de Inc. 3 e Inc. 4 y la lista priorizada con el dataset completo no se midieron. Las alertas sin paginar ya superaban 2 s con el dataset completo (acción 10 del S9).
2. M2.1 y M2.2 de Inc. 3 e Inc. 4 no existen todavía: faltan fichas y capturas y el registro de defectos.
3. B2, B3 y B4 se puntúan 1,0 por funcionalidad probada con simulaciones; si S12 exige envío real o dispositivo real, bajan a 0,5 y M3.1 queda en 50,0 % (B2, B3, B4 y B6 en 0,5).
4. Datos clínicos en el navegador (cola y caché de lecturas); generación de recordatorios manual y síncrona; respuestas por SMS no se reciben.
5. Dependencia de aprobaciones externas (Meta, microred, consentimiento) con fechas fuera del control del equipo.

## 11. Archivos nuevos de esta adenda

`metricas/salidas/`: `m11_contaminacion_v4.json`, `m12_conformidad_v4.json`, `m13_acoplamiento_v4.json`, `m31_brechas_v4.json`, `m32_valor_v3_v4.json` (Inc. 3), `m32_valor_v4.json` (Inc. 4), `m32_carga_v4.json`, `m32_disponibilidad_v4.json`, `pruebas_v4.txt`. Script nuevo: `.claude/herramientas/gqm/m31_brechas_v4.py`. Las mediciones de valor y carga se ejecutaron desde una copia temporal de `.claude/herramientas/gqm/` para no sobrescribir `metricas/datos/` del S9 (los scripts originales escriben ahí); con `AUTH_MODE=demo` y `AUTH_COOKIE_SECURE=false` en el servidor de pruebas.
