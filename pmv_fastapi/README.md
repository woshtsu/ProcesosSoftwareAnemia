# Anemia Junín — Incremento 2 (avance del 50 %)

Producción desde `main`: [guía paso a paso de Supabase, GitHub Actions y Render](docs/DESPLIEGUE.md). El workflow está en `../.github/workflows/ci.yml`, en la raíz del repositorio. Configuración remota pendiente; no implica despliegue verificado.

**Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín**
Procesos de Software (ASUC01702) · 2026-20 · Versión `v1.5.0-inc2-avance` (el PMV liberado es `v1.0-PMV`)

El Incremento 1 resolvió el **triple registro manual** con un expediente digital único por niño y la hemoglobina ajustada por altitud y clasificada automáticamente. El Incremento 2 (S3-4, «Agenda automática y alertas») ataca la brecha B2: la agenda de controles se calculaba a mano, de modo que había controles fuera de la ventana normativa y citas olvidadas.

El sistema es **referencial: programa y vigila fechas, no diagnostica ni prescribe**. Todos los datos incluidos son **sintéticos**.

## Incremento 1 (PMV, `v1.0-PMV`)

| HU | Historia de usuario | Estado |
|---|---|---|
| HU-01 | Registrar niño con su evaluación inicial | ✅ |
| HU-02 | Consultar y actualizar el expediente (incluye nuevos controles) | ✅ |
| HU-03 | Validar datos según reglas clínicas (vista previa y rechazo con mensaje comprensible) | ✅ |
| HU-04 | Listar niños en seguimiento con estado de control (desde la v1.5: «atrasado» = tiene al menos un control vencido) | ✅ |
| HU-05 | Reporte del periodo (JSON y CSV) | ✅ |

## Incremento 2 — avance del 50 % (10 de 18 SP más el habilitador de arquitectura)

| Historia | Descripción | SP | Estado |
|---|---|---|---|
| HIST-2.1 | Generar agenda de controles según la normativa | 5 | ✅ |
| HIST-2.2 | Identificar controles vencidos y alertas internas | 5 | ✅ |
| HIST-2.3 | Visualizar agenda del personal | 5 | ⏳ |
| HIST-2.4 | Registrar asistencia a control | 3 | ⏳ |

Habilitador: estructura de puertos y adaptadores explícita y verificada con pruebas de arquitectura (ADR-008).

### Reglas de la agenda (esquema `ESQUEMA_AGENDA_V1`, ADR-007)

- **Dosajes por edad** (esquema operativo del establecimiento, S1 Anexo A, Tablas A.3 y A.4, compatible con la NTS N.° 213-MINSA/DGIESP-2024): a los 6 DHx, 9 DHc1, 12 DHc2, 15 DHx, 18 DHc1, 21 DHc2, 24 DHx, 30 DHc1, 36 DHx, 39 DHc1, 48 DHx y 51 DHc1 meses; fecha = nacimiento + N meses (el día 31 pasa al último día del mes).
- **Seguimiento del tratamiento**: una evaluación LEVE, MODERADA o SEVERA programa C1M, C3M y C6M a +1, +3 y +6 meses. Si una evaluación posterior es SIN_ANEMIA, los controles de tratamiento que aún no vencían se cierran (`CERRADO_RECUPERADO`); los ya vencidos siguen vencidos (historial fiel).
- **Cumplimiento**: hay una evaluación entre 15 días antes y 30 días después de la fecha programada; cada evaluación cumple a lo sumo un control (la más cercana).
- **Estados**: `CUMPLIDO`, `PENDIENTE` (con `proximo` si vence en 7 días o menos) y `VENCIDO` (hoy > programada + 30 días y no cumplido). La agenda empieza cuando el niño entra al sistema (dosajes con fecha ≥ primera evaluación − 15 días). Solo niños `ACTIVO` y controles con el niño menor de 60 meses.
- **Prioridad de la alerta**: `ALTA` si el control es de tratamiento, o la última clasificación es MODERADA/SEVERA, o el atraso supera 30 días; `MEDIA` de 8 a 30 días; `BAJA` hasta 7 días (el atraso se cuenta desde la fecha límite).
- La agenda se calcula en línea desde el expediente: no hay tabla nueva.

### Interfaz

- **Expediente → «Agenda de controles»**: resumen con chips de estado (`data-testid="agenda-resumen"`) y tabla de controles (`agenda-tabla`).
- **Pestaña «Alertas»** (`tab-alertas`): tarjetas de resumen, tabla filtrable por comunidad y prioridad (`alertas-tabla`), clic en un niño abre su expediente. La cabecera muestra el total de controles vencidos (`insignia-alertas`).

## Arquitectura

Arquitectura **hexagonal** en un monolito modular (ADR-001 y ADR-008). Las dependencias apuntan siempre hacia el dominio y las verifican las pruebas de `tests/arquitectura/`.

```
app/
├── domain/model/        entidades y objetos de valor puros (Nino, Evaluacion, ControlProgramado, AlertaControl…)
├── domain/service/      reglas clínicas, validaciones, agenda y alertas (funciones puras)
├── ports/inbound/       casos de uso como typing.Protocol (GestionarExpediente, GenerarAgenda, ConsultarControlesVencidos…)
├── ports/outbound/      RepositorioNinos y Reloj
├── application/         implementación de los casos de uso (servicio_expediente, servicio_agenda, servicio_alertas)
├── adapters/inbound/http/          FastAPI y DTO; depende solo de ports.inbound y domain.model
├── adapters/outbound/persistence/  SQLAlchemy (PostgreSQL/SQLite) y en memoria
├── adapters/outbound/reloj_sistema.py   reloj en hora de Perú
├── web/                 cliente PWA (HTML/CSS/JS, service worker, Swagger UI local)
└── main.py              raíz de composición (único módulo que conoce las implementaciones)
tests/
├── unitarias/           dominio y casos de uso con el repositorio en memoria
├── integracion/         API + SQLAlchemy (SQLite; PostgreSQL con TEST_DATABASE_URL)
├── arquitectura/        reglas de dependencias por análisis AST de los import
├── e2e/                 Playwright con servidor real y datos sintéticos
└── rendimiento/         Locust
```

## API

Contrato completo en `docs/openapi.json` (se regenera con `python -m scripts.exportar_openapi`) y Swagger UI en `/docs`.

| Método y ruta | Descripción |
|---|---|
| `GET /api/salud` | Estado del servicio |
| `POST /api/validaciones/evaluacion` | Vista previa de la clasificación (HU-03) |
| `POST /api/ninos` · `GET /api/ninos` | Registrar niño (HU-01) · listado de seguimiento (HU-04) |
| `GET /api/ninos/{id}` · `GET /api/ninos/dni/{dni}` · `PATCH /api/ninos/{id}` | Expediente (HU-02) |
| `POST /api/ninos/{id}/evaluaciones` | Registrar un nuevo control (HU-02) |
| `GET /api/reportes/periodo` | Reporte del periodo en JSON o CSV (HU-05) |
| **`GET /api/ninos/{id}/agenda`** | **Nuevo (HIST-2.1)**: controles ordenados por fecha y resumen (total, cumplidos, pendientes, vencidos, próximo control); 404 si no existe |
| **`GET /api/alertas/controles-vencidos?comunidad=&prioridad=`** | **Nuevo (HIST-2.2)**: controles vencidos de niños activos, por prioridad y días de atraso; 422 si la prioridad no es ALTA, MEDIA o BAJA |
| **`GET /api/alertas/resumen`** | **Nuevo (HIST-2.2)**: `total_vencidos`, `por_prioridad`, `ninos_con_vencidos`, `proximos_7_dias` |

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

El Incremento 2 no cambia el esquema de la base de datos (la agenda no se persiste, ADR-007).

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

Resultados de la versión `v1.5.0-inc2-avance` (salidas completas en `docs/evidencias/inc2/`):

| Control | Resultado |
|---|---|
| ruff | 0 hallazgos; 64 archivos con formato correcto |
| pytest (unitarias, integración, arquitectura) | **228 pruebas en verde**: 174 unitarias, 40 de integración y 14 de arquitectura |
| Cobertura de `app/` | **100 %** (1 046 sentencias, 158 ramas); umbral configurado: 80 % |
| E2E (Playwright, Chromium) | **8 en verde**: las 4 del PMV y 4 nuevas (agenda en el expediente, casos especiales, pestaña de alertas con filtros y vista móvil) |
| Carga de humo (50 usuarios, 30 s, con las tareas nuevas) | 1 161 solicitudes, 0 fallos, p95 agregado 140 ms (alertas 140 ms, agenda 62 ms) |

La prueba de carga de humo se ejecutó en un contenedor de desarrollo con SQLite y pocos niños (de 27 a 139 durante la prueba); no reemplaza la prueba de carga formal con PostgreSQL. Los casos de prueba nuevos están numerados desde CP-37 en los docstrings (CP-01 a CP-36 son del Incremento 1).

Defectos hallados al explorar entradas límite de la API heredada y corregidos con prueba de regresión: **DEF-03** a **DEF-08** (ver `docs/evidencias/registro_defectos_inc2.md`). Los del Incremento 1 (DEF-01 y DEF-02) siguen en `docs/evidencias/registro_defectos.md`.

El pipeline `.github/workflows/ci.yml` ejecuta lint, pruebas con cobertura (incluye arquitectura), verificación del contrato OpenAPI, integración contra PostgreSQL, E2E y (si existe el secreto `SONAR_TOKEN`) el análisis de SonarCloud.

## Flujo de ramas

`main` (versiones liberadas, con tag) ← `develop` (integración) ← `feature/histXX-...` (una rama por historia). Todo cambio entra por pull request con el pipeline en verde.

## Limitaciones conocidas (backlog)

- HIST-2.3 (visualizar la agenda del personal) y HIST-2.4 (registrar asistencia a control) no están implementados.
- Un control vencido sigue vencido aunque el niño regrese después de su ventana; la reprogramación o justificación es alcance de HIST-2.4. Mientras tanto una alerta solo desaparece si el niño pasa a alta.
- Los parámetros de `ESQUEMA_AGENDA_V1` (meses de los dosajes, tolerancias de −15/+30 días, umbrales de prioridad) y los puntos de corte clínicos deben ser confirmados por la microred antes del uso clínico.
- La agenda y las alertas se calculan en cada consulta (costo lineal en los niños activos: ≈ 185 ms con 1 000 niños en SQLite); se materializarán si se supera el criterio de ADR-007.
- Sin autenticación: el usuario se identifica con el encabezado `X-Usuario` solo para auditoría. La autenticación por roles se incorpora antes de usar datos reales (Ley N.° 29733).
- El registro definitivo requiere conexión; la cola de sincronización offline es alcance del INC-3.
- Los diagramas de `docs/diagramas/` corresponden a la versión `v1.0-PMV` y no se regeneraron para esta estructura.
- Las fechas del sistema se interpretan en hora de Perú (UTC-5, sin horario de verano).

## Equipo

| Integrante | Rol |
|---|---|
| Porras Veli Ricardo | Ingeniero de Proceso |
| Auqui Huincho Tania | Ingeniero de Desarrollo y Prototipado |
| Huamani Rodriguez Jean Piero | Ingeniero de Calidad y Mejora del Proceso |
