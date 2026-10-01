# Anemia Junín — PMV (Incremento 1)

**Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín**
Procesos de Software (ASUC01702) · 2026-20 · Versión `v1.0-PMV`

El Incremento 1 resuelve la primera brecha del proceso: el **triple registro manual** (historia clínica, tarjeta de control y digitación en el HIS). Cada niño tiene un expediente digital único, con la hemoglobina ajustada por altitud y clasificada automáticamente.

| HU | Historia de usuario | Estado |
|---|---|---|
| HU-01 | Registrar niño con su evaluación inicial | ✅ |
| HU-02 | Consultar y actualizar el expediente (incluye nuevos controles) | ✅ |
| HU-03 | Validar datos según reglas clínicas (vista previa y rechazo con mensaje comprensible) | ✅ |
| HU-04 | Listar niños en seguimiento con estado de control | ✅ |
| HU-05 | Reporte del periodo (JSON y CSV) | ✅ |

## Arquitectura

Arquitectura **hexagonal** en un monolito modular (ver `docs/adr/`):

```
app/
├── domain/            Núcleo: entidades, reglas clínicas, errores (sin frameworks)
├── application/       Casos de uso (ServicioExpediente) y puertos (RepositorioNinos, Reloj)
├── adapters/
│   ├── entrada/http/  Adaptador REST (FastAPI) y contratos DTO
│   └── salida/persistencia/  Adaptadores SQLAlchemy (PostgreSQL/SQLite) y en memoria
├── web/               Cliente PWA (HTML/CSS/JS, service worker, Swagger UI local)
└── main.py            Raíz de composición
```

## Ejecución local (desarrollo)

Requisitos: Python 3.11+.

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m scripts.cargar_datos_prueba                   # datos SINTÉTICOS de prueba
uvicorn app.main:crear_app --factory --reload --port 8000
```

- Aplicación: <http://127.0.0.1:8000>
- API documentada (OpenAPI/Swagger): <http://127.0.0.1:8000/docs>

Sin `DATABASE_URL` se usa SQLite en `./datos/anemia.db`.

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

## Pruebas y calidad

```bash
ruff check . && ruff format --check .            # análisis estático
pytest --cov=app                                  # unitarias + integración (SQLite) con cobertura
TEST_DATABASE_URL=postgresql+psycopg2://... pytest tests/integracion --no-cov   # integración en PostgreSQL
python -m playwright install chromium && pytest tests/e2e -m e2e --no-cov      # E2E de interfaz
locust -f tests/rendimiento/locustfile.py --host http://127.0.0.1:8000 \
       --headless -u 50 -r 10 -t 60s --csv docs/evidencias/carga/carga          # carga
```

Resultados de la versión `v1.0-PMV`: **77 pruebas automatizadas** (62 unitarias, 11 de integración, 4 E2E), **cobertura 99 %**, 0 hallazgos de ruff, carga de 50 usuarios con **p95 = 58 ms y 0 % de errores**. Defectos detectados y cerrados antes de liberar: **DEF-01** (consultas N+1 en el reporte, ver `docs/adr/ADR-006-consultas-por-lotes.md`) y **DEF-02** (el reporte usaba días UTC y omitía registros hechos después de las 19:00 en Perú). Detalle en `docs/evidencias/registro_defectos.md`.

El pipeline `.github/workflows/ci.yml` ejecuta lint, pruebas con cobertura, integración contra PostgreSQL, E2E y (si existe el secreto `SONAR_TOKEN`) el análisis de SonarCloud.

## Flujo de ramas

`main` (versiones liberadas, con tag) ← `develop` (integración) ← `feature/huXX-...` (una rama por historia). Todo cambio entra por pull request con el pipeline en verde.

## Limitaciones conocidas del PMV (backlog de los siguientes incrementos)

- Sin autenticación: el usuario se identifica con el encabezado `X-Usuario` solo para auditoría. La autenticación por roles se incorpora antes de usar datos reales (Ley N.° 29733).
- El registro definitivo requiere conexión; la cola de sincronización offline es alcance del INC-3.
- Los puntos de corte y la ecuación de ajuste por altitud deben ser confirmados por la microred antes del uso clínico.
- Los datos incluidos son **sintéticos** (nombres y DNI ficticios).
- Las fechas del sistema se interpretan en hora de Perú (UTC-5, sin horario de verano).

## Equipo

| Integrante | Rol |
|---|---|
| Porras Veli Ricardo | Ingeniero de Proceso |
| Auqui Huincho Tania | Ingeniero de Desarrollo y Prototipado |
| Huamani Rodriguez Jean Piero | Ingeniero de Calidad y Mejora del Proceso |
