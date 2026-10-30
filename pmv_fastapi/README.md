# Anemia Junín — Incremento 4 (v4.0.0-inc4)

## Inicio de sesión con Supabase Auth

La aplicación exige iniciar sesión por defecto. Esta etapa integra **Auth**; `DATABASE_URL` sigue seleccionando la base actual (SQLite o PostgreSQL). No se han migrado tablas a Supabase.

1. Crea el proyecto de Supabase. En **Connect**, copia Project URL y la clave **publishable** (también se admite la clave pública `anon` anterior). No utilices `service_role` ni claves secretas.
2. En **Authentication**, habilita el proveedor Email y desactiva **Allow new users to sign up**. En **Users → Add user → Create new user**, crea las cuentas del personal con correo confirmado. Todos los usuarios confirmados de este proyecto tendrán acceso; en esta etapa no hay roles ni separación por establecimiento.
3. En `pmv_fastapi/`, copia `.env.example` a `.env` y completa `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY`. El archivo real está ignorado por Git. La URL y clave proporcionadas por el usuario ya se configuraron localmente en la sesión T-015.
4. Inicia desde esa carpeta, en PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:crear_app --factory --env-file .env --reload --port 8000
```

Abre `http://127.0.0.1:8000` e ingresa con la cuenta creada en Supabase. El formulario informa credenciales incorrectas, correo sin confirmar o problemas de conexión. Al recargar conserva la sesión y **Cerrar sesión** elimina las cookies. El usuario de auditoría es el UUID verificado, no el selector de la demostración.

Para HTTP local: `AUTH_COOKIE_SECURE=false`; para HTTPS: `true` (valor predeterminado). Si faltan las variables de Supabase, el acceso clínico permanece bloqueado. El frontend y la API deben servirse desde el mismo origen.

Los tokens se guardan en cookies HttpOnly y no se exponen al JavaScript. La API clínica verifica la identidad con Supabase, las respuestas no se cachean y los cambios requieren protección CSRF. Los borradores persistentes del formulario se reservan para el modo demo. Detalles y límites: [ADR-011](docs/adr/ADR-011-supabase-auth.md).

Para reproducir las capturas y pruebas históricas sin autenticación, activa la demo explícitamente, solo en un entorno local con datos sintéticos:

```powershell
$env:AUTH_MODE = "demo"
.\.venv\Scripts\python.exe -m uvicorn app.main:crear_app --factory --port 8000
```

Pruebas del login: `python -m pytest tests/integracion/test_autenticacion.py -q`; navegador: `python -m pytest tests/e2e/test_login.py -m e2e -q --no-cov` (requiere Chromium de Playwright). Estas pruebas simulan Supabase y no crean cuentas reales. Los endpoints son `GET /api/auth/config`, `POST /api/auth/login`, `GET /api/auth/session` y `POST /api/auth/logout`. Las mutaciones deben enviar `X-CSRF-Protection: 1`; el frontend lo incorpora automáticamente.

Producción desde `main`: [guía paso a paso de Supabase, GitHub Actions y Render](docs/DESPLIEGUE.md). El workflow está en `../.github/workflows/ci.yml`, en la raíz del repositorio. Configuración remota pendiente; no implica despliegue verificado.

**Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín**
Procesos de Software (ASUC01702) · 2026-20 · Versión `v2.0.0-inc2` (etiqueta prevista `v2.0-Inc2`; el PMV liberado es `v1.0-PMV` y el avance del 50 % fue `v1.5.0-inc2-avance`)

El Incremento 1 resolvió el **triple registro manual** con un expediente digital único por niño y la hemoglobina ajustada por altitud y clasificada automáticamente. El Incremento 2 (S3-4, «Agenda automática y alertas») ataca la brecha B2: la agenda de controles se calculaba a mano, de modo que había controles fuera de la ventana normativa y citas olvidadas.

El sistema es **referencial: programa y vigila fechas, no diagnostica ni prescribe**. Los datos de `scripts/cargar_datos_prueba.py` y de las pruebas son **sintéticos**; además se puede cargar el **dataset real anonimizado de la DIRESA Junín** (`Dataset/`, sin DNI ni nombres) para la demostración (ADR-009).

## Incremento 1 (PMV, `v1.0-PMV`)

| HU | Historia de usuario | Estado |
|---|---|---|
| HU-01 | Registrar niño con su evaluación inicial | ✅ |
| HU-02 | Consultar y actualizar el expediente (incluye nuevos controles) | ✅ |
| HU-03 | Validar datos según reglas clínicas (vista previa y rechazo con mensaje comprensible) | ✅ |
| HU-04 | Listar niños en seguimiento con estado de control (desde la v1.5: «atrasado» = tiene al menos un control vencido) | ✅ |
| HU-05 | Reporte del periodo (JSON y CSV) | ✅ |

## Incremento 2 — 18 de 18 SP más el habilitador de arquitectura

| Historia | Descripción | SP | Estado |
|---|---|---|---|
| HIST-2.1 | Generar agenda de controles según la normativa | 5 | ✅ |
| HIST-2.2 | Identificar controles vencidos y alertas internas | 5 | ✅ |
| HIST-2.3 | Visualizar agenda del personal (RF-08) | 5 | ✅ |
| HIST-2.4 | Registrar asistencia a control (RF-09) | 3 | ✅ |

Habilitador: estructura de puertos y adaptadores explícita y verificada con pruebas de arquitectura (ADR-008).

### Reglas de la agenda (esquema `ESQUEMA_AGENDA_V1`, ADR-007)

- **Dosajes por edad** (esquema operativo del establecimiento, S1 Anexo A, Tablas A.3 y A.4, compatible con la NTS N.° 213-MINSA/DGIESP-2024): a los 6 DHx, 9 DHc1, 12 DHc2, 15 DHx, 18 DHc1, 21 DHc2, 24 DHx, 30 DHc1, 36 DHx, 39 DHc1, 48 DHx y 51 DHc1 meses; fecha = nacimiento + N meses (el día 31 pasa al último día del mes).
- **Seguimiento del tratamiento**: una evaluación LEVE, MODERADA o SEVERA programa C1M, C3M y C6M a +1, +3 y +6 meses. Si una evaluación posterior es SIN_ANEMIA, los controles de tratamiento que aún no vencían se cierran (`CERRADO_RECUPERADO`); los ya vencidos siguen vencidos (historial fiel).
- **Cumplimiento**: hay una evaluación entre 15 días antes y 30 días después de la fecha programada; cada evaluación cumple a lo sumo un control (la más cercana).
- **Estados**: `CUMPLIDO`, `PENDIENTE` (con `proximo` si vence en 7 días o menos) y `VENCIDO` (hoy > programada + 30 días y no cumplido). La agenda empieza cuando el niño entra al sistema (dosajes con fecha ≥ primera evaluación − 15 días). Solo niños `ACTIVO` y controles con el niño menor de 60 meses.
- **Prioridad de la alerta**: `ALTA` si el control es de tratamiento, o la última clasificación es MODERADA/SEVERA, o el atraso supera 30 días; `MEDIA` de 8 a 30 días; `BAJA` hasta 7 días (el atraso se cuenta desde la fecha límite).
- La agenda se calcula en línea desde el expediente: no hay tabla de controles. Solo se persiste la asistencia (HIST-2.4, ADR-010): **asistió** deja el control cumplido; **no asistió** lo deja pendiente o vencido con la marca «Inasistencia registrada» y sube un nivel la prioridad de su alerta.

### Interfaz

- **Expediente → «Agenda de controles»**: resumen con chips de estado (`data-testid="agenda-resumen"`) y tabla de controles (`agenda-tabla`).
- **Pestaña «Alertas»** (`tab-alertas`): tarjetas de resumen, tabla filtrable por comunidad y prioridad (`alertas-tabla`), clic en un niño abre su expediente. La cabecera muestra el total de controles vencidos (`insignia-alertas`).
- **Pestaña «Agenda»** (`tab-agenda`, HIST-2.3): rango de fechas (`agenda-desde`, `agenda-hasta`; por defecto la semana de la fecha de referencia, máximo 31 días), filtros por establecimiento y comunidad (`filtro-agenda-establecimiento`, `filtro-agenda-comunidad`), botones `agenda-consultar`, `agenda-anterior` y `agenda-siguiente`, resumen (`agenda-personal-resumen`) y tabla por día (`agenda-personal-tabla`) con los controles cumplidos atenuados.
- **Registrar asistencia** (HIST-2.4): botones «Asistió» (`btn-asistio`) y «No asistió» (`btn-no-asistio`) en cada control pendiente o vencido, en el expediente y en la pestaña «Agenda». La ventana (`modal-asistencia`) pide el motivo de la inasistencia (`asistencia-motivo`, `asistencia-detalle`) o deja vincular una evaluación (`asistencia-evaluacion`); confirma con `asistencia-confirmar`. El control con inasistencia muestra «Inasistencia registrada» (`marca-inasistencia`).
- **Registros del dataset**: sin DNI ni nombres se muestran como «Registro DJ-00002 (dataset anonimizado)» (`expediente-nombre`), con su código (`expediente-codigo`) y origen (`expediente-origen`), la severidad del HIS (`clasificacion-his`) y «no registrado» donde no hay peso ni talla (`sin-antropometria`). El buscador y la pestaña «Expediente» aceptan DNI o código.
- **Aviso de fecha de referencia** (`aviso-fecha-referencia`): visible solo cuando el servidor se inicia con `FECHA_REFERENCIA`; las fechas por defecto de los formularios salen del servidor.

## Incremento 3 — Sin conexión, sincronización y visita priorizada

| Historia | Descripción | Estado |
|---|---|---|
| HIST-3.1 | Registrar sin conexión (cola en IndexedDB, service worker) | ✅ |
| HIST-3.2 | Sincronizar al reconectar (`POST /api/sincronizacion`, idempotente) | ✅ |
| HIST-3.3 | Resolver conflictos sin sobrescribir a ciegas | ✅ |
| HIST-3.4 | Ver lo pendiente y los conflictos (indicador y pestaña «Sincronización») | ✅ |
| VIS-3.5 | Visita domiciliaria priorizada (pestaña «Visitas») | ✅ |

- **Sin conexión (ADR-012)**: niño con evaluación inicial, evaluación, asistencia y visita se guardan en el dispositivo (`app/web/cola.js`) con `id_operacion` UUID, `id_dispositivo` y fecha local, y se envían solos al volver la red (`app/web/sync.js`) o con «Sincronizar ahora». El service worker (`app/web/sw.js`) precachea el shell y sirve las lecturas con red primero y caché de respaldo; la aplicación abre sin conexión. El caché de datos se borra al cerrar sesión.
- **Resultados por operación**: `APLICADA`, `DUPLICADA` (reenviar no duplica), `CONFLICTO` (el servidor ya tenía un dato distinto; queda pendiente de resolver con `CONSERVAR_SERVIDOR`, `APLICAR_CLIENTE` o `DESCARTAR`) y `RECHAZADA` (error de validación; se corrige o se descarta). El servidor es la fuente de verdad.
- **Visita priorizada (ADR-013)**: puntaje de 0 a 100 con severidad (hasta 40), control vencido (30), inasistencias de los últimos 90 días (15) y días desde la última visita (15; sin visita, el máximo). **Los pesos son una propuesta del equipo, no una norma del MINSA.**
- **Qué SQL ejecutar**: ver `docs/DESPLIEGUE.md` (`db/03_migracion_v3_0.sql` migra una base 2.0).
- **Interfaz** (`data-testid`): `indicador-sync` (con `data-pendientes`), pestañas `tab-visitas` y `tab-sincronizacion`, `visita-priorizada`, `puntaje`, `btn-visitar`, `modal-visita`, `pendiente`, `conflicto`, `aviso-cache`.

## Incremento 4 — Recordatorios por WhatsApp y barreras

| Historia | Descripción | Estado |
|---|---|---|
| HIST-4.1 | Enviar recordatorio de control (WhatsApp con respaldo SMS; simulado por defecto) | ✅ |
| HIST-4.2 | Registrar la confirmación del tutor (personal o webhook de WhatsApp) | ✅ |
| HIST-4.3 | Registrar barreras de acceso al tratamiento (también sin conexión) | ✅ |
| HIST-4.4 | Alertar barreras críticas y sumarlas a la visita priorizada | ✅ |

- **Puerto `Notificador` (ADR-014)**: simulado (por defecto), WhatsApp Cloud API con mensaje de plantilla, SMS genérico y composición con respaldo. Se elige por variables de entorno (`.env.example`, `docs/DESPLIEGUE.md`); **sin ellas no sale ningún mensaje** y la pestaña «Recordatorios» rotula cada envío como SIMULADO. Las pruebas usan `httpx.MockTransport`: nunca hay llamadas reales a Meta ni a proveedores SMS.
- **Qué se recuerda**: control pendiente de hoy, control cuya ventana abre en 3 días o menos y control vencido. Idempotente (un recordatorio por niño, control y tipo), reintenta los fallidos y **no escribe a los niños del dataset DIRESA** (no tienen celular: «sin contacto»). El mensaje no incluye diagnóstico.
- **Respuesta del tutor**: `CONFIRMA`, `NO_PUEDE` o `REPROGRAMAR` (fecha de hasta 90 días), registrada por el personal o recibida por el webhook `/api/notificaciones/whatsapp/webhook` (verificación con token y firma `X-Hub-Signature-256`). Con `NO_PUEDE` se puede registrar la barrera en el mismo acto.
- **Barreras**: 8 tipos (`OTRA` exige detalle) desde el expediente, la respuesta `NO_PUEDE`, la inasistencia o la visita no lograda. Es **crítica** (alerta en la pestaña «Alertas») si es un rechazo del tratamiento o un efecto adverso del suplemento, si hay dos o más barreras distintas en 60 días, o si hay una barrera vigente (90 días) con anemia moderada o severa y un control vencido. **Reglas propuestas por el equipo, no validadas por la microred.**
- **Visita priorizada `VISITA-V2`**: los niños con barreras críticas suman el componente `BARRERA_CRITICA` (15 o 8 puntos); el puntaje va de 0 a 100 (hasta 115 con barreras críticas).
- **Qué SQL ejecutar**: ver `docs/DESPLIEGUE.md` (`db/04_migracion_v4_0.sql` migra una base 3.0).
- **Interfaz** (`data-testid`): pestaña `tab-recordatorios`, `recordatorios-generar`, `recordatorios-resultado`, `recordatorios-metricas`, `recordatorio`, `marca-simulado`, `btn-responder`, `modal-respuesta`, `btn-barrera-nino`, `modal-barrera`, `barrera-pendiente`, `alerta-barrera`, `asistencia-barrera`, `visita-barrera`.

## Arquitectura

Arquitectura **hexagonal** en un monolito modular (ADR-001 y ADR-008). Las dependencias apuntan siempre hacia el dominio y las verifican las pruebas de `tests/arquitectura/`.

```
app/
├── domain/model/        entidades y objetos de valor puros (Nino, Evaluacion, ControlProgramado, AsistenciaControl, AgendaPersonal, OrigenDatos…)
├── domain/service/      reglas clínicas, validaciones, agenda, agenda del personal, asistencia y alertas (funciones puras)
├── ports/inbound/       casos de uso como typing.Protocol (GestionarExpediente, GenerarAgenda, ConsultarAgendaPersonal, RegistrarAsistencia, ImportarDataset…)
├── ports/outbound/      RepositorioNinos, Reloj, Notificador, RepositorioRecordatorios y RepositorioBarreras
├── application/         implementación de los casos de uso (servicio_expediente, servicio_agenda, servicio_agenda_personal, servicio_asistencia, servicio_alertas, servicio_importacion, servicio_contexto, servicio_recordatorios, servicio_barreras)
├── adapters/inbound/http/          FastAPI y DTO; depende solo de ports.inbound y domain.model
├── adapters/outbound/persistence/  SQLAlchemy (PostgreSQL/SQLite) y en memoria
├── adapters/outbound/notificaciones/  Notificador simulado, WhatsApp Cloud, SMS y con respaldo
├── adapters/outbound/reloj_sistema.py   reloj en hora de Perú · reloj_fijo.py reloj con FECHA_REFERENCIA
├── web/                 cliente PWA (HTML/CSS/JS, service worker, Swagger UI local)
└── main.py              raíz de composición (único módulo que conoce las implementaciones)
tests/
├── unitarias/           dominio y casos de uso con el repositorio en memoria
├── integracion/         API + SQLAlchemy (SQLite; PostgreSQL con TEST_DATABASE_URL)
├── arquitectura/        reglas de dependencias por análisis AST de los import
├── e2e/                 Playwright con servidor real y datos sintéticos
└── rendimiento/         Locust y micro-benchmark de latencia
scripts/                 cargar_datos_prueba, importar_dataset_diresa (+ importador_diresa/), exportar_openapi
db/                      esquema PostgreSQL 4.0 y migraciones 02_migracion_v2_0.sql, 03_migracion_v3_0.sql y 04_migracion_v4_0.sql
```

## API

Contrato completo en `docs/openapi.json` (se regenera con `python -m scripts.exportar_openapi`) y Swagger UI en `/docs`.

| Método y ruta | Descripción |
|---|---|
| `GET /api/salud` | Estado del servicio; `fecha_hoy` y `fecha_referencia` (nula si no se fijó `FECHA_REFERENCIA`) |
| `POST /api/validaciones/evaluacion` | Vista previa de la clasificación (HU-03) |
| `POST /api/ninos` · `GET /api/ninos` | Registrar niño (HU-01) · listado de seguimiento (HU-04) |
| `GET /api/ninos/{id}` · `GET /api/ninos/dni/{dni}` · `PATCH /api/ninos/{id}` | Expediente (HU-02) |
| `POST /api/ninos/{id}/evaluaciones` | Registrar un nuevo control (HU-02) |
| `GET /api/reportes/periodo` | Reporte del periodo en JSON o CSV (HU-05) |
| **`GET /api/ninos/{id}/agenda`** | **Nuevo (HIST-2.1)**: controles ordenados por fecha y resumen (total, cumplidos, pendientes, vencidos, próximo control); 404 si no existe |
| **`GET /api/alertas/controles-vencidos?comunidad=&prioridad=`** | **Nuevo (HIST-2.2)**: controles vencidos de niños activos, por prioridad y días de atraso; 422 si la prioridad no es ALTA, MEDIA o BAJA |
| **`GET /api/alertas/resumen`** | **Nuevo (HIST-2.2)**: `total_vencidos`, `por_prioridad`, `ninos_con_vencidos`, `proximos_7_dias` |
| **`GET /api/agenda?desde=&hasta=&establecimiento=&comunidad=`** | **Nuevo (HIST-2.3)**: agenda del personal; por defecto la semana de la fecha de referencia; máximo 31 días (422 si `desde` > `hasta`, el formato es inválido o el rango supera 31 días); totales por día y del rango; controles cumplidos, pendientes y vencidos |
| **`POST /api/ninos/{id}/controles/{codigo}/asistencia`** | **Nuevo (HIST-2.4)**: `{fecha_programada, estado: ASISTIO\|NO_ASISTIO, motivo?, evaluacion_id?}`; 201; 404 (niño o control inexistente); 409 (ya registrada, control cumplido o cerrado); 422 (fecha futura, motivo faltante) |
| **`GET /api/ninos/{id}/asistencias`** | **Nuevo (HIST-2.4)**: asistencias registradas del niño |
| **`POST /api/sincronizacion`** | **Nuevo (HIST-3.2)**: lote de 1 a 200 operaciones `{id_operacion, tipo, id_dispositivo, fecha_local, id_cliente?, nino_ref?, datos}`; devuelve el resultado por operación (`APLICADA`, `DUPLICADA`, `CONFLICTO`, `RECHAZADA`) y un resumen; 422 si el lote está vacío, supera 200 o una operación es inválida |
| **`GET /api/sincronizacion/conflictos?estado=`** | **Nuevo (HIST-3.3)**: conflictos con `datos_cliente` y `datos_servidor`; `estado` PENDIENTE o RESUELTO |
| **`POST /api/sincronizacion/conflictos/{id}/resolver`** | **Nuevo (HIST-3.3)**: `{resolucion: CONSERVAR_SERVIDOR\|APLICAR_CLIENTE\|DESCARTAR}`; 404; 409 si ya está resuelto; 422 si el dominio no permite aplicar el dato del dispositivo |
| **`POST /api/ninos/{id}/visitas`** · **`GET /api/ninos/{id}/visitas`** | **Nuevo (VIS-3.5)**: registrar una visita `{fecha, resultado: REALIZADA\|NO_ENCONTRADO\|RECHAZADA, consume_suplemento?, observaciones?}` (201; 404; 409 si ya hay una ese día; 422) y listarlas |
| **`GET /api/visitas/priorizadas?establecimiento=&limite=`** | **Nuevo (VIS-3.5)**: niños en tratamiento por puntaje con sus componentes; `limite` de 1 a 200 (20 por defecto) |
| **`POST /api/ninos/{id}/barreras`** · **`GET /api/ninos/{id}/barreras`** | **Nuevo (HIST-4.3)**: registrar una barrera `{tipo, detalle?, fuente?, fecha?}` (201; 404; 409 si se repite tipo, fecha y fuente; 422) y listarlas |
| **`GET /api/alertas/barreras?comunidad=&prioridad=`** | **Nuevo (HIST-4.4)**: niños con barreras críticas, prioridad ALTA o MEDIA, razones y barreras vigentes; 422 si la prioridad no es ALTA o MEDIA |
| **`POST /api/recordatorios/generar`** | **Nuevo (HIST-4.1)**: genera y envía el lote de hoy (`{establecimiento?}`); devuelve enviados, fallidos, `omitidos_sin_contacto` y `omitidos_ya_enviado`; idempotente |
| **`GET /api/recordatorios?estado=&desde=&nino_id=&limite=`** | **Nuevo (HIST-4.1)**: recordatorios con el celular enmascarado; `limite` de 1 a 1000; 422 si el estado o el límite son inválidos |
| **`GET /api/recordatorios/metricas?desde=&hasta=`** | **Nuevo (HIST-4.1)**: tasas de envío, entrega (solo envíos reales), respuesta y confirmación, en total y por canal |
| **`POST /api/recordatorios/{id}/respuesta`** | **Nuevo (HIST-4.2)**: `{respuesta: CONFIRMA\|NO_PUEDE\|REPROGRAMAR, fecha_reprogramada?, barrera?}`; 404; 409 si ya tiene respuesta; 422 |
| **`GET`/`POST /api/notificaciones/whatsapp/webhook`** | **Nuevo (HIST-4.2)**: verificación (`hub.mode`, `hub.verify_token`, `hub.challenge`; 403 si no coincide) y recepción de estados y respuestas, públicos y protegidos por la firma `X-Hub-Signature-256` (403 si es inválida; 422 si el cuerpo no es JSON) |

Cambios de contrato en la 2.0 (aditivos salvo lo indicado): `dni`, `nombres`, `apellidos`, `sexo`, `tutor_nombre` y `tutor_celular` pueden ser `null` (solo en niños del dataset); se agregan `nombre_completo`, `origen`, `codigo_origen`, `provincia`, `red` y `microred`; las evaluaciones agregan `clasificacion_origen` y su peso y talla pueden ser `null`. `POST /api/ninos` siempre crea el origen `SISTEMA` y exige todos los campos como antes.

Cambio en `GET /api/ninos`: `control_atrasado` ahora significa «tiene al menos un control VENCIDO» (sustituye la heurística de 30 días) y se agrega `controles_vencidos` (entero).

## Ejecución local (desarrollo)

Requisitos: Python 3.11+.

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m scripts.cargar_datos_prueba                   # datos SINTÉTICOS (agrega --reiniciar para recargarlos)
uvicorn app.main:crear_app --factory --reload --port 8000
```

- Aplicación: <http://127.0.0.1:8000> · API documentada: <http://127.0.0.1:8000/docs>
- Sin `DATABASE_URL` se usa SQLite en `./datos/anemia.db`.

El conjunto sintético (27 niños) conserva los 14 del Incremento 1 (DNI 71000001 a 71000014) y agrega los 71000015 a 71000027, definidos **respecto de la fecha de hoy**, de modo que siempre hay controles cumplidos, pendientes, próximos a vencer y vencidos (de edad y de tratamiento) en varias comunidades, un caso recuperado, uno con alta y uno en el borde de los 60 meses.

## Demostración con el dataset real de la DIRESA Junín

El dataset (`Dataset/Niños_menores_de_36_meses_con_dx_de_anemia_en_la_Región_ Junín.csv`, 12 486 filas, fuente HIS, diagnósticos del 14-01-2022 al 21-06-2024) se importa como niños de origen `DATASET_DIRESA_JUNIN`, sin DNI ni nombres (ADR-009). El «hoy» de la demostración es la fecha de corte, **30-06-2024**:

```bash
# 1) base de la demo: muestra estratificada de 500 niños (Provincia × severidad HIS, semilla 2026)
DATABASE_URL=sqlite:///./datos/demo_dataset.db python -m scripts.importar_dataset_diresa --muestra 500 --reiniciar
# 2) servidor con la fecha de referencia fija
DATABASE_URL=sqlite:///./datos/demo_dataset.db FECHA_REFERENCIA=2024-06-30 uvicorn app.main:crear_app --factory --port 8000
```

Opciones del importador: `--completo` (todas las filas utilizables), `--reporte ruta.json`, `--semilla`, `--reiniciar`, `--fecha-referencia` y `--con-registros-sistema N` (agrega N niños «PRUEBA DEL SISTEMA», origen `SISTEMA`, con todos los campos). Si la base ya tiene niños importados y no se usa `--reiniciar`, termina con código 2. Resultados reales (reportes completos en `docs/evidencias/inc2/importacion_muestra500.json` e `importacion_completa.json`):

| | Muestra de 500 | Dataset completo |
|---|---|---|
| Filas leídas / con evaluación utilizable | 12 486 / 11 686 | 12 486 / 11 686 |
| Niños importados | 500 | 11 686 (800 omitidos por no tener ninguna evaluación válida) |
| Evaluaciones importadas (diagnóstico, 1 mes, 3 meses, 6 meses) | 1 290 (453, 309, 286, 242) | 29 712 (10 577, 7 584, 6 174, 5 377) |
| Evaluaciones descartadas por falta de hemoglobina | 106 | 3 770 |
| Concordancia de la severidad HIS con la del sistema (diagnósticos con severidad HIS) | 64,1 % de 449 | 65,8 % de 10 503 |
| Concordancia entre los niños con anemia según ambos | 78,9 % | 79,3 % |
| El sistema clasifica «sin anemia» un diagnóstico HIS | 18,7 % | 16,9 % |

La concordancia no es una medida de exactitud del sistema: la altitud es la de la **capital de la provincia** (INEI, *Perú: Compendio Estadístico 2014*, cuadro 1.12; Huancayo 3 245, Concepción 3 286, Chanchamayo 775, Jauja 3 389, Junín 4 113, Satipo 628, Tarma 3 059, Yauli 3 725 y Chupaca 3 281 m s. n. m.), no la del establecimiento, y el HIS puede usar otra regla de ajuste o registrar la hemoglobina sin ajustar. El dataset no trae peso ni talla: no se inventaron (el expediente muestra «no registrado»). Tampoco trae fechas fuera de ventana, por lo que las alertas son las que calcula el sistema respecto del 30-06-2024. Con la muestra de 500 niños las consultas responden en menos de 0,1 s; con el dataset completo la agenda del personal tarda ≈ 1,6 s y las alertas ≈ 2,5 s (`docs/evidencias/inc2/optimizacion_p95.md`).

## Entorno de staging (PostgreSQL)

Con Docker:

```bash
POSTGRES_PASSWORD=una_clave_segura docker compose up -d --build
docker compose exec api python -m scripts.cargar_datos_prueba
```

Sin Docker (PostgreSQL instalado):

```bash
createdb anemia
psql -d anemia -f db/01_esquema_postgresql.sql
export DATABASE_URL=postgresql+psycopg2://usuario:clave@localhost:5432/anemia
python -m scripts.cargar_datos_prueba
uvicorn app.main:crear_app --factory --host 0.0.0.0 --port 8000
```

La versión 2.0 **sí cambia el esquema** (origen de los datos, campos opcionales solo para el dataset y la tabla `asistencia_control`, ADR-009 y ADR-010). Una base nueva se crea con `db/01_esquema_postgresql.sql`; una base creada con la 1.x se migra con `psql -d anemia -f db/02_migracion_v2_0.sql`. En SQLite el esquema se crea solo, pero una base de la 1.x se rechaza con un mensaje claro: bórrela y vuelva a cargar los datos.

## Pruebas y calidad

```bash
ruff check . && ruff format --check .            # análisis estático
pytest --cov=app                                  # unitarias + integración (SQLite) + arquitectura, con cobertura
TEST_DATABASE_URL=postgresql+psycopg2://... pytest tests/integracion --no-cov   # integración en PostgreSQL
python -m playwright install chromium && pytest tests/e2e -m e2e --no-cov      # E2E de interfaz
python -m scripts.exportar_openapi --verificar    # el contrato publicado está al día
locust -f tests/rendimiento/locustfile.py --host http://127.0.0.1:8000 \
       --headless -u 50 -r 10 -t 60s --csv docs/evidencias/carga/carga          # carga
```

Resultados de la versión `4.0.0-inc4` (reproducibles con los comandos de arriba; el E2E usa `pytest tests/e2e`):

| Control | Resultado |
|---|---|
| ruff | 0 hallazgos; formato correcto |
| pytest (unitarias, integración, arquitectura) | **660 pruebas en verde**: 416 unitarias, 219 de integración (SQLite) y 25 de arquitectura (161 nuevas respecto de la 3.0) |
| Cobertura de `app/` | **99,79 %**; 100 % en todo lo nuevo del Incremento 4 (quedan `autenticacion.py` con 94 % y `supabase_auth.py` con 97 %, anteriores) |
| E2E (Playwright, Chromium) | **28 en verde**: 24 anteriores y 4 nuevas (recordatorios simulados con respuesta `NO_PUEDE` y alerta de barrera crítica, barrera sin conexión que sincroniza, barrera asociada a una inasistencia, barrera de una visita no lograda con su componente en el puntaje) |
| Contrato OpenAPI | `docs/openapi.json` al día (29 rutas) |

Resultados de la versión `3.0.0-inc3` (reproducibles con los comandos de arriba; el E2E usa `pytest tests/e2e`):

| Control | Resultado |
|---|---|
| ruff | 0 hallazgos; formato correcto |
| pytest (unitarias, integración, arquitectura) | **499 pruebas en verde**: 331 unitarias, 147 de integración (SQLite; también en PostgreSQL 16) y 21 de arquitectura |
| Cobertura de `app/` | **99,70 %**; 100 % en todo lo nuevo del Incremento 3 (quedan `autenticacion.py` con 94 % y `supabase_auth.py` con 97 %, anteriores) |
| E2E (Playwright, Chromium) | **24 en verde**: 17 anteriores y 7 nuevas (registro y control sin conexión que sincronizan, recarga sin conexión desde caché, datos incompletos sin conexión, asistencia sin conexión, visita priorizada en línea y sin conexión, conflicto resuelto desde el panel) |
| Contrato OpenAPI | `docs/openapi.json` al día |

Resultados de la versión `v2.0.0-inc2` (salidas completas en `docs/evidencias/inc2/`):

| Control | Resultado |
|---|---|
| ruff | 0 hallazgos; 95 archivos con formato correcto |
| pytest (unitarias, integración, arquitectura) | **328 pruebas en verde**: 234 unitarias, 76 de integración (SQLite) y 18 de arquitectura |
| Cobertura de `app/` | **100 %** (1 700 sentencias, 264 ramas); umbral configurado: 80 % |
| E2E (Playwright, Chromium) | **15 en verde**: las 8 anteriores y 7 nuevas (agenda del personal, rango inválido y navegación, no asistió con alerta que sube de prioridad, asistió, vista móvil, y registro del dataset sin nombre con el aviso de fecha de referencia) |
| Contrato OpenAPI | `docs/openapi.json` al día (`python -m scripts.exportar_openapi --verificar`) |

Las pruebas de integración también se pueden ejecutar contra PostgreSQL con `TEST_DATABASE_URL`. La prueba de carga de humo de la versión 1.5 (`docs/evidencias/inc2/carga/`) no se repitió con la 2.0; `tests/rendimiento/locustfile.py` incluye ahora tareas para la agenda del personal y las asistencias. Los casos de prueba nuevos están numerados desde CP-116 en los docstrings (CP-01 a CP-115 son anteriores). Los 20 registros reales de `tests/fixtures/dataset_muestra.csv` (con campos nulos) alimentan las pruebas del importador y de la API.

Defectos hallados y corregidos con prueba de regresión: **DEF-03** a **DEF-08** (entradas límite de la API heredada) y **DEF-09** (carrera en las fechas de la pestaña «Agenda», hallada por las pruebas E2E); ver `docs/evidencias/registro_defectos_inc2.md`. Los del Incremento 1 (DEF-01 y DEF-02) siguen en `docs/evidencias/registro_defectos.md`.

Optimización de la latencia (acción 1 del PDCA, `docs/evidencias/inc2/optimizacion_p95.md`): con 1 000 niños, p95 del listado de seguimiento de 159,6 a 128,2 ms y de las alertas de 185,7 a 155,3 ms (mediana de tres corridas intercaladas en la misma máquina; mejora de 12 a 21 %, con una dispersión entre corridas de ±15 %).

El pipeline `.github/workflows/ci.yml` ejecuta lint, pruebas con cobertura (incluye arquitectura), verificación del contrato OpenAPI, integración contra PostgreSQL, E2E y (si existe el secreto `SONAR_TOKEN`) el análisis de SonarCloud.

## Flujo de ramas

`main` (versiones liberadas, con tag) ← `develop` (integración) ← `feature/histXX-...` (una rama por historia). Todo cambio entra por pull request con el pipeline en verde.

## Limitaciones conocidas (backlog)

- Un control vencido sigue vencido aunque el niño regrese después de su ventana; la alerta desaparece si el niño asiste (HIST-2.4), se evalúa dentro de la ventana o pasa a alta.
- Una asistencia registrada por error no se puede anular ni corregir (backlog del Incremento 3, junto con la autenticación por roles).
- Dataset DIRESA Junín: la altitud es la de la capital de la provincia (aproximación); no hay peso ni talla (no se inventaron); solo constan dosajes dentro de ventana; el sistema y el HIS coinciden en la severidad en 64 a 66 % de los diagnósticos (ver arriba). Con el dataset completo (11 686 niños, casi seis veces el criterio de 2 000 niños activos de ADR-007) las alertas tardan ≈ 2,5 s y devuelven 22 MiB sin paginar; la muestra de 500 niños responde en menos de 0,1 s.
- La base de la versión 1.x no es compatible con la 2.0: se migra con `db/02_migracion_v2_0.sql` (PostgreSQL) o se recrea (SQLite).
- Los parámetros de `ESQUEMA_AGENDA_V1` (meses de los dosajes, tolerancias de −15/+30 días, umbrales de prioridad) y los puntos de corte clínicos deben ser confirmados por la microred antes del uso clínico.
- La agenda y las alertas se calculan en cada consulta (costo lineal en los niños activos: ≈ 120 a 155 ms con 1 000 niños en SQLite); se materializarán si se supera el criterio de ADR-007.
- Supabase Auth implementado (ADR-011). Pendientes: roles y permisos por establecimiento; en modo demo el selector `X-Usuario` sigue siendo solo auditoría sintética.
- Sin conexión solo se guardan en el dispositivo el registro de un niño con su evaluación inicial, las evaluaciones, las asistencias, las visitas (INC-3, ADR-012) y las barreras (INC-4); editar un expediente y dar de alta requieren conexión. La clasificación de un niño registrado sin conexión aparece al sincronizar.
- Los pesos del puntaje de visitas priorizadas (ADR-013, incluido `BARRERA_CRITICA`) son una propuesta del equipo y deben validarse con la microred.
- Recordatorios (INC-4, ADR-014): sin credenciales de Meta el envío es simulado; la plantilla de WhatsApp debe ser aprobada por Meta; el webhook falla cerrado (503 sin `WHATSAPP_APP_SECRET`; 403 con firma ausente o inválida); las respuestas por SMS no se reciben; la generación es manual y requiere conexión, igual que registrar la respuesta de un tutor (solo las barreras se guardan sin conexión). Las reglas de barreras críticas y su vigencia de 90 días no están validadas por la microred.
- Los diagramas de `docs/diagramas/` corresponden a la versión `v1.0-PMV` y no se regeneraron para esta estructura.
- Las fechas del sistema se interpretan en hora de Perú (UTC-5, sin horario de verano).

## Equipo

| Integrante | Rol |
|---|---|
| Porras Veli Ricardo | Ingeniero de Proceso |
| Auqui Huincho Tania | Ingeniero de Desarrollo y Prototipado |
| Huamani Rodriguez Jean Piero | Ingeniero de Calidad y Mejora del Proceso |
