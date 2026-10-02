# Datos verificables del PMV oficial: `pmv_fastapi/`

- **Elaborado por:** `sincronizador` el 2026-10-01, en la rama `feature/s6-integrador-final` (base `main` = 0c9e302).
- **Regla de uso:** todas las cifras del informe y de las diapositivas salen de este archivo. Cada dato indica su archivo de origen. Las rutas son relativas a la raíz del repositorio.
- **Leyenda de verificación:**

| Marca | Significado |
| --- | --- |
| **[V]** | Verificado en esta sesión leyendo el archivo o con git. |
| **[E]** | Verificado estáticamente: conteo por AST o lectura de CSV. |
| **[D]** | Declarado en el repositorio; no se reprodujo en esta sesión porque el entorno local (Python 3.14) no tiene instaladas las dependencias. |

- **Decisión del usuario:** el **PMV oficial es `pmv_fastapi/`**. `anemia_junin/` (Flask + SQLite, 266 pruebas, 96,69 %) es el **antecedente**, es decir, el prototipo previo del Incremento 1. Sus cifras **no** se presentan como resultados del PMV.

## 1. Identidad y versión

| Dato | Valor | Fuente |
| --- | --- | --- |
| Nombre | Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín, PMV (Incremento 1) [V] | `pmv_fastapi/README.md` l.1-4 |
| Versión | `1.0.0` (pyproject) / `v1.0-PMV` [V] | `pmv_fastapi/pyproject.toml`; `git tag` |
| Tag | `v1.0-PMV` (anotado, objeto 6a17c63) → commit **9ce90c3** "release: v1.0-PMV — Incremento 1". Mensaje: "PMV / Incremento 1: HU-01 a HU-05, 77 pruebas, cobertura 99 %" [V] | `git show v1.0-PMV`; `git ls-remote --tags origin` |
| Repositorio | https://github.com/woshtsu/ProcesosSoftwareAnemia [V] | `git remote -v` |
| Equivalencia | El contenido de 9ce90c3 (raíz) es **idéntico** a `main:pmv_fastapi/` en `app`, `tests`, `db`, `docs`, `scripts`, `Dockerfile`, `docker-compose.yml`, `README.md` y `.github` [V] | `git diff --quiet 9ce90c3:<p> main:pmv_fastapi/<p>` |
| Alcance | HU-01 Registrar niño con evaluación inicial; HU-02 Consultar/actualizar expediente y nuevos controles; HU-03 Validar datos con reglas clínicas (vista previa y rechazo comprensible); HU-04 Listar niños en seguimiento con estado de control; HU-05 Reporte del periodo (JSON y CSV). Las 5 están ✅ [V] | `pmv_fastapi/README.md` tabla HU |
| Equivalencia HU ↔ S3-4/S5 | HU-01 = HIST-1.1 · HU-02 = HIST-1.2 · HU-03 = HIST-1.3 · HU-04 = HIST-1.4 · HU-05 = HIST-1.5 [V] | `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` (§4.2, §8.2) |
| Brecha atendida | B1, el triple registro manual (historia clínica, tarjeta y HIS), sustituido por un expediente digital único con Hb ajustada por altitud y clasificada [V] | `pmv_fastapi/README.md` l.6 |

## 2. Stack

| Capa | Tecnología y versión | Fuente |
| --- | --- | --- |
| Lenguaje | Python ≥ 3.11 (`target-version py311`); imagen `python:3.11-slim`; CI con 3.11 [V] | `pmv_fastapi/pyproject.toml`, `pmv_fastapi/Dockerfile`, `pmv_fastapi/.github/workflows/ci.yml` |
| API | FastAPI 0.142.0 + Uvicorn[standard] 0.46.0 [V] | `pmv_fastapi/requirements.txt` |
| ORM / BD | SQLAlchemy 2.1.1; psycopg2-binary 2.9.13; **PostgreSQL 16** (staging/CI); SQLite en desarrollo y pruebas (`./datos/anemia.db` si no hay `DATABASE_URL`) [V] | `requirements.txt`, `docker-compose.yml`, `README.md` |
| Cliente | PWA: HTML/CSS/JS, `manifest.json`, service worker `sw.js` y Swagger UI servido localmente (`app/web/vendor/`) [V] | `pmv_fastapi/app/web/` |
| Pruebas | pytest 9.1.1, pytest-cov 7.1.0, httpx 0.28.1, Playwright 1.56.0, Locust 2.46.6 [V] | `pmv_fastapi/requirements-dev.txt` |
| Calidad estática | Ruff 0.15.11 (reglas E, F, W, I, B, UP, S, C90; McCabe ≤ 12; línea de 120) [V] | `pmv_fastapi/pyproject.toml` |
| Umbral de cobertura | `fail_under = 80`, cobertura de ramas activada [V] | `pmv_fastapi/pyproject.toml` |

## 3. Arquitectura y capas (hexagonal, monolito modular)

| Capa | Ruta | Contenido |
| --- | --- | --- |
| Dominio | `pmv_fastapi/app/domain/` | `entidades.py`, `reglas_clinicas.py` (corte de Hb y ajuste por altitud, OMS 2024) y `errores.py`, sin dependencias de frameworks [V] |
| Aplicación | `pmv_fastapi/app/application/` | `casos_uso.py` (`ServicioExpediente`) y `puertos.py` (`RepositorioNinos`, `Reloj`) [V] |
| Adaptador de entrada | `pmv_fastapi/app/adapters/entrada/http/` | `api.py` (router FastAPI `/api`) y `esquemas.py` (DTO Pydantic) [V] |
| Adaptadores de salida | `pmv_fastapi/app/adapters/salida/persistencia/` | `sqlalchemy_repo.py` (PostgreSQL/SQLite) y `memoria.py` (pruebas unitarias) [V] |
| Interfaz | `pmv_fastapi/app/web/` | PWA [V] |
| Raíz de composición | `pmv_fastapi/app/main.py` | `crear_app` (factory); rutas `/`, `/docs` y `/sw.js` [V] |
| Tamaño | 1 191 líneas en `app/**/*.py` (conteo `wc`). El registro de defectos declara 1,02 KLOC de Python [V]/[D] | `wc -l`; `docs/evidencias/registro_defectos.md` |

Diagramas propios del PMV, ya existentes **solo en PNG** (con su fuente):

| Diagrama | Archivos |
| --- | --- |
| C4 contexto | `pmv_fastapi/docs/diagramas/C4_contexto.{puml,png}` |
| C4 contenedores | `pmv_fastapi/docs/diagramas/C4_contenedores.{puml,png}` |
| C4 componentes | `pmv_fastapi/docs/diagramas/C4_componentes.{puml,png}` |
| Paquetes | `P1_paquetes.{puml,png}` |
| Despliegue | `P2_despliegue_pmv.png` (fuente `P2.dot`) y `D4_despliegue.png` (`D4.dot`) |
| Modelo de datos | `P3_modelo_datos.{puml,png}` |
| Casos de uso | `D1_casos_uso.png` |
| Secuencia | `D3_secuencia.{puml,png}` |
| Estados | `D6_estados.{puml,png}` |
| Clases | `D7_clases.{puml,png}` |
| Seguimiento | `D8_seguimiento.{puml,png}` |
| Gráficos | `G1_piramide_pruebas.png`, `G2_cobertura.png`, `G3_carga.png` (generador `graficos.py`) y `G4_tablero_metricas.png` (`tablero.py`) |
| Planificación | `V1_gantt.png` (`gantt.py`) y `V2_red_dependencias.png` (`V2.dot`) |

## 4. Endpoints (router `prefix="/api"`; `pmv_fastapi/app/adapters/entrada/http/api.py`) [V]

| Método y ruta | HU / etiqueta | Respuestas | Línea |
| --- | --- | --- | --- |
| GET `/api/salud` | Operación (healthcheck de Docker) | 200 `{"estado":"ok"}` | l.110 |
| POST `/api/validaciones/evaluacion` | HU-03 Validación (vista previa: Hb ajustada y clasificación antes de guardar) | 200 / 422 | l.115 |
| POST `/api/ninos` | HU-01 Registro | 201 / 409 duplicado / 422 | l.127 |
| GET `/api/ninos?estado=&q=&clasificacion=` | HU-04 Seguimiento | 200 (lista `FilaSeguimiento` con `control_atrasado`) | l.141 |
| GET `/api/ninos/dni/{dni}` | HU-02 Expediente | 200 / 404 | l.167 |
| GET `/api/ninos/{nino_id}` | HU-02 Expediente | 200 / 404 | l.172 |
| PATCH `/api/ninos/{nino_id}` | HU-02 Expediente | 200 | l.182 |
| POST `/api/ninos/{nino_id}/evaluaciones` | HU-02 Expediente (nuevo control) | 201 | l.193 |
| GET `/api/reportes/periodo?desde=&hasta=&formato=json\|csv` | HU-05 Reporte | 200 (JSON o CSV) | l.206 |

En total hay **9 operaciones REST**. Fuera del esquema están `/`, `/docs` (Swagger local) y `/sw.js` (`app/main.py` l.37-51).

- **Contrato:** OpenAPI 3.1 en `pmv_fastapi/docs/openapi.json` [V]. Errores con un formato único `{mensaje, errores:[{campo, mensaje}]}` en español: 422 validación, 409 duplicado y 404 no encontrado (ADR-005) [V].
- **Auditoría:** encabezado `X-Usuario`. **No hay autenticación** (limitación conocida; Ley N.° 29733) [V] (`README.md`, "Limitaciones").

## 5. Modelo de datos (`pmv_fastapi/db/01_esquema_postgresql.sql`, PostgreSQL 14+) [V]

| Objeto | Definición |
| --- | --- |
| Tabla `nino` (16 columnas) | `id` VARCHAR(36) PK; `dni` VARCHAR(8) **UNIQUE** con CHECK `^[0-9]{8}$`; nombres y apellidos; `sexo` CHECK F/M; `fecha_nacimiento`; establecimiento, distrito y comunidad; `altitud_m` CHECK 0–5000; tutor; `tutor_celular` CHECK `^9[0-9]{8}$`; `estado` ACTIVO/ALTA; `registrado_por`; `creado_en` y `actualizado_en` TIMESTAMPTZ. Índices `ix_nino_comunidad` e `ix_nino_estado` |
| Tabla `evaluacion_hemoglobina` (13 columnas) | `id` PK; `nino_id` FK → `nino(id)` ON DELETE CASCADE; `fecha`; `edad_meses` CHECK 0–59; `hemoglobina_observada` CHECK 3–20; `altitud_m`; `hemoglobina_ajustada`; `clasificacion` CHECK SIN_ANEMIA/LEVE/MODERADA/SEVERA/NO_APLICA; `peso_kg` CHECK 1,5–30; `talla_cm` CHECK 40–125; `registrado_por`; `creado_en`. Índices `ix_eval_nino` e `ix_eval_fecha` |
| Vista `v_ultimo_control` | Último control por niño (`DISTINCT ON`), apoyo de HU-04 |
| Relación | 1 niño : 0..N evaluaciones |
| Defensa en profundidad | Los CHECK repiten las reglas del dominio (ADR-003) |

## 6. Pruebas

| Nivel | Casos | Archivos | Marca |
| --- | --- | --- | --- |
| Unitarias | **62** | `tests/unitarias/test_reglas_clinicas.py` 24 · `test_entidades.py` 24 · `test_casos_uso.py` 14 | [E] (AST con `parametrize`) |
| Integración / API | **11** | `tests/integracion/test_api.py` 10 · `test_zona_horaria.py` 1. Se ejecutan contra SQLite y también contra PostgreSQL 16 en CI | [E] |
| E2E / UI (Playwright) | **4** | `tests/e2e/test_interfaz.py`: hu01_hu03 registro con vista previa; hu03 datos inválidos; hu04 seguimiento; hu05 reporte | [E] |
| **Total automatizadas** | **77** (62 + 11 + 4), "77/77 en verde" | coincide con README y tag | [E] + [D] |
| Rendimiento / carga | 1 escenario Locust: `tests/rendimiento/locustfile.py`, clase `PersonalPosta`, `wait_time between(0.5, 2)`, tareas con pesos 5/4/3; 50 usuarios, 60 s | — | [V] |
| IDs de casos citados en el código | CP-01, 06, 07, 12, 13, 20, 21, 32, 33 y 36 (grep `tests/`). El registro de defectos cita además CP-14, CP-15 y CP-16 | — | [V] |

## 7. Cobertura (`pmv_fastapi/docs/evidencias/cobertura.txt`, también `cobertura.xml`) [V]

| Indicador | Valor |
| --- | --- |
| Total | **641 sentencias, 2 sin cubrir; 98 ramas, 4 parciales → 99 %** |
| Por sentencias | ≈ 99,7 % (639/641) |
| Combinada (sentencias + ramas) | ≈ 99,2 % (733/739), cálculo propio |
| Por módulo | `api.py` 100 % · `esquemas.py` 100 % · `memoria.py` 100 % · `sqlalchemy_repo.py` 97 % · `casos_uso.py` 100 % · `puertos.py` 100 % · `entidades.py` 99 % · `errores.py` 100 % · `reglas_clinicas.py` 100 % · `main.py` 100 % |
| Umbral DoD | 80 % (`pyproject.toml`) |

## 8. Análisis estático y defectos

| Elemento | Dato | Fuente |
| --- | --- | --- |
| Ruff | "All checks passed!" y "33 files already formatted": **0 hallazgos** [V] | `pmv_fastapi/docs/evidencias/ruff.txt` |
| DEF-01 | N+1 en `GET /api/reportes/periodo`; p95 de 2 200 ms con 50 usuarios. Severidad mayor (rendimiento); detectado por CP-15 y carga. Corregido en la rama `fix/def-01-reporte-n-mas-1` (ADR-006). Estado: **Cerrado** [V] | `pmv_fastapi/docs/evidencias/registro_defectos.md` |
| DEF-02 | El reporte contaba días en UTC y perdía los registros posteriores a las 19:00 en Perú. Severidad mayor (exactitud). Detectado por CP-14 y E2E (30/09/2026 20:40). Corregido en `fix/def-02-zona-horaria` y verificado por CP-16 (unitaria, integración SQLite/PostgreSQL y E2E). Estado: **Cerrado** [V] | ídem |
| Densidad de defectos | **2 defectos / 1,02 KLOC = 2,0 defectos/KLOC**; 0 abiertos [V] | ídem |
| SonarCloud | `sonar-project.properties` con `sonar.projectKey=anemia-junin-pmv` y **`sonar.organization=REEMPLAZAR_ORGANIZACION`**. El paso del CI solo corre si existe el secreto `SONAR_TOKEN`. **No hay evidencia de un análisis SonarCloud ejecutado** [V] | `pmv_fastapi/sonar-project.properties`, `ci.yml` |

## 9. Carga (Locust; `pmv_fastapi/docs/evidencias/carga/`) [V]

| Escenario (50 usuarios, 60 s) | Solicitudes | Fallos | Mediana | p95 | p99 | Req/s |
| --- | --- | --- | --- | --- | --- | --- |
| Línea base, antes de DEF-01 (agregado) | 2 170 | 0 | 24 ms | **310 ms** | 1 600 ms | 36,74 |
| Después de DEF-01 (agregado) | 2 336 | 0 | 9 ms | **58 ms** | 97 ms | **39,56** |
| `GET /api/reportes/periodo` antes → después | — | — | 530 → 13 ms | **2 200 → 74 ms** | — | — |
| `GET /api/ninos` antes → después | — | — | — | 250 → 75 ms | — | — |
| `GET /api/ninos/{id}` antes → después | — | — | — | 56 → 30 ms | — | — |
| `POST /api/ninos` antes → después | — | — | — | 100 → 36 ms | — | — |

- El usuario máximo en `despues_DEF-01_historial.csv` es **50** [E].
- Archivos: `linea_base_antes_DEF-01_stats.csv`, `despues_DEF-01_stats.csv` y `despues_DEF-01_historial.csv`.

## 10. CI/CD (`pmv_fastapi/.github/workflows/ci.yml`) [V]

- **Disparadores:** push a `main`, `develop` y `feature/**`; PR a `main` y `develop`.
- **Job `calidad-y-pruebas`** (ubuntu-latest, servicio `postgres:16`):
  1. checkout;
  2. Python 3.11;
  3. `pip install -r requirements-dev.txt`;
  4. `ruff check` + `ruff format --check`;
  5. `pytest --cov=app --cov-report=xml --junitxml` (SQLite);
  6. aplicación de `db/01_esquema_postgresql.sql` con psql y `pytest tests/integracion` contra PostgreSQL;
  7. Playwright chromium + `pytest tests/e2e -m e2e`;
  8. publicación del artefacto `reportes-calidad` (`coverage.xml` y `reporte-pruebas.xml`);
  9. SonarCloud, condicionado a `SONAR_TOKEN`.
- **Job `imagen-staging`** (solo en `main`, tras el job anterior): `docker build -t anemia-junin-pmv:${sha}`.
- **⚠ Ubicación:** en `main` el archivo está en `pmv_fastapi/.github/workflows/`. GitHub **solo** lee `.github/workflows/` en la raíz, así que **el pipeline no se ejecuta en `main`**. En el historial del tag (9ce90c3, rama `origin/entrega-s5-s7`) sí estaba en la raíz. No hay evidencia en el repositorio de ejecuciones en verde (por ejemplo, un enlace a Actions o una captura).

## 11. Docker y despliegue [V]

| Elemento | Dato | Fuente |
| --- | --- | --- |
| `Dockerfile` | `python:3.11-slim`; instala `requirements.txt`; copia `app` y `scripts`; usuario sin privilegios `appuser`; `EXPOSE 8000`; HEALTHCHECK a `/api/salud` cada 30 s; `CMD uvicorn app.main:crear_app --factory --host 0.0.0.0 --port 8000` | `pmv_fastapi/Dockerfile` |
| `docker-compose.yml` (staging) | Servicio `db` `postgres:16-alpine` (BD `anemia`, usuario `anemia`, contraseña `${POSTGRES_PASSWORD:-cambiar_en_staging}`, volumen `datos_pg`, el esquema se monta en `docker-entrypoint-initdb.d`, healthcheck `pg_isready`) y servicio `api` (build `.`, `DATABASE_URL` psycopg2 a `db:5432`, puerto `8000:8000`, `depends_on` con `service_healthy`) | `pmv_fastapi/docker-compose.yml` |
| Comandos de staging | `POSTGRES_PASSWORD=... docker compose up -d --build` y `docker compose exec api python -m scripts.cargar_datos_prueba` | `pmv_fastapi/README.md` |
| Desarrollo | `pip install -r requirements-dev.txt`, `python -m scripts.cargar_datos_prueba` y `uvicorn app.main:crear_app --factory --reload --port 8000`. App en http://127.0.0.1:8000; Swagger en `/docs` | `pmv_fastapi/README.md` |
| Nube | **No hay** despliegue en la nube documentado: solo staging local con Docker Compose y la imagen construida en CI | — |
| Flujo de ramas | `main` (liberaciones con tag) ← `develop` ← `feature/huXX-...`; PR con el pipeline en verde. Ramas reales en el historial del tag: `feature/infra-ci-bd`, `feature/hu03-validacion-nts`, `feature/hu01-hu05-expediente`, `test/e2e-y-carga`, `fix/def-01-...`, `fix/def-02-...` y `docs/arquitectura-evidencias` | `README.md`; `git log origin/entrega-s5-s7` |

## 12. Evidencias de demostración [V]

- **Capturas** en `pmv_fastapi/docs/evidencias/capturas/`:

| Archivo | Contenido |
| --- | --- |
| `01_registro_vista_previa.png` | Registro con vista previa |
| `02_validacion_datos_invalidos.png` | Validación de datos inválidos |
| `03_expediente_nuevo.png` | Expediente nuevo |
| `04_seguimiento.png` | Seguimiento |
| `05_expediente_evolucion.png` | Evolución del expediente |
| `06_reporte_periodo.png` | Reporte del periodo |
| `07_vista_movil.png` | Vista móvil |
| `08_openapi_swagger.png` | OpenAPI / Swagger |

- **Video:** `pmv_fastapi/docs/evidencias/demo_pmv.mp4` (1 640 388 bytes ≈ 1,6 MB). Lo genera `pmv_fastapi/scripts/grabar_demo.py`. Duración no verificada.
- **Datos:** **sintéticos** (nombres y DNI ficticios), generados con `pmv_fastapi/scripts/cargar_datos_prueba.py`.

## 13. ADRs (`pmv_fastapi/docs/adr/`) [V]

| ADR | Decisión | NFR principal | Dato clave |
| --- | --- | --- | --- |
| ADR-001 | Arquitectura hexagonal en un monolito modular; microservicios descartados | Mantenibilidad, capacidad de prueba, evolución | 62 unitarias en < 1 s con el adaptador en memoria; la misma suite de integración pasa en SQLite y en PostgreSQL |
| ADR-002 | Cliente PWA web adaptable (manifest + SW + borrador en `localStorage`) | Portabilidad, despliegue en postas, tolerancia a red intermitente | El registro definitivo requiere conexión; la cola offline queda para INC-3 |
| ADR-003 | PostgreSQL 16 central con UNIQUE(dni), FK y CHECK | Integridad y confiabilidad del dato | Dos motores; se mitiga con integración en ambos en CI |
| ADR-004 | Reglas clínicas parametrizadas en el dominio (OMS 2024; < 6 meses = NO_APLICA) | Exactitud clínica, trazabilidad normativa | El sistema no diagnostica; los parámetros esperan la confirmación de la microred |
| ADR-005 | API REST JSON + OpenAPI 3.1 y errores por campo en español | Interoperabilidad, usabilidad | Sin WebSockets ni gRPC: el INC-1 no necesita tiempo real |
| ADR-006 | Consultas por lotes en reportes (corrige DEF-01) | Rendimiento (latencia p95) | p95 del reporte 2 200 → 74 ms; p95 agregado 310 → 58 ms; 39,6 req/s; 0 fallos |

## 14. Limitaciones declaradas (`pmv_fastapi/README.md`) [V]

- Sin autenticación (solo `X-Usuario`).
- El registro definitivo requiere conexión; la cola offline llega en INC-3.
- Los puntos de corte deben confirmarse con la microred.
- Datos sintéticos.
- Zona horaria fija UTC-5.

## 15. Contradicciones y riesgos detectados (para el sincronizador y el inspector)

| ID | Contradicción | Impacto | Acción propuesta (responsable) |
| --- | --- | --- | --- |
| C-01 | El tag `v1.0-PMV` → 9ce90c3 está en `origin/entrega-s5-s7` y **no es alcanzable desde `main`**, porque `main` integró el PMV con un squash (0c9e302) bajo `pmv_fastapi/`. En el tag, el PMV está en la raíz del repo y el código es idéntico | R-38/R-80 se cumplen (el tag existe en GitHub), pero quien navegue el tag no verá los entregables | No mover el tag sin autorización del usuario. Documentar en informe y README: "tag v1.0-PMV (commit 9ce90c3); el mismo código está en `main` bajo `pmv_fastapi/`". Opcional, con permiso: tag adicional `v1.1-integrador` en `main` (PASO MANUAL/usuario) |
| C-02 | `ci.yml` está en `pmv_fastapi/.github/workflows/`, así que GitHub no lo ejecuta en `main` | El informe no puede afirmar "CI en verde en main" | Crear `.github/workflows/ci.yml` en la raíz con `defaults.run.working-directory: pmv_fastapi` y `paths` adecuados (tarea S6-08, desarrollador), y obtener la captura de Actions en verde (PASO MANUAL) |
| C-03 | El integrador (`entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md`) y S5 (`entregables/semana-05/Entregable_Semana5_Anemia_Junin.md`) describen **Flask**: 266 pruebas, 96,69 %, Waitress, SQLite y `/api/v1/...`. También dicen "Tag pendiente", tienen marcadores `CARGA_CIERRE` (integrador l.260; S5 l.107) y `[PENDIENTE]`, y afirman "No se utiliza SonarCloud" | C1–C4 incoherentes con el PMV oficial | Reescribir el integrador con este archivo (`redactor-informe-integrador`). La corrección de S5 queda a decisión del usuario (tarea S6-11) |
| C-04 | SonarCloud está configurado pero sin organización real (`REEMPLAZAR_ORGANIZACION`) y sin evidencia de análisis | R-32: no se puede afirmar un análisis Sonar | En el informe, "Ruff como análisis estático obligatorio; SonarCloud preparado, pendiente de activación". Activarlo es PASO MANUAL |
| C-05 | Las figuras C4/despliegue/modelo de datos de `diagramas/svg/03-09` son del **prototipo Flask** (ReportLab) | R-28/R-29/R-33 con figuras equivocadas | VIS-003 a VIS-006: SVG a partir de `pmv_fastapi/docs/diagramas/*.puml` |
| C-06 | La consigna pide pitches que suman 10 min frente a 7 min de exposición | R-90 | Guion de 7 min (`disenador-diapositivas`) |
| C-07 | La plantilla de portada pide 4 roles y el equipo tiene 3 integrantes | R-08 | Tabla de mapeo de roles en la portada |
| C-08 | `coordinacion/RUTAS.md` (ORQ-002) reservaba `entregables/semana-06-integrador/Presentacion_Integrador_Anemia_Junin.md` y `exportados/semana-06-integrador/` | Rutas duplicadas | Se adoptan las rutas del usuario: `entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md` y `exportados/semana-06/`. RUTAS ya está actualizado |
| C-09 | Sin acta de aceptación de un usuario final real (R-63) ni códigos de alumno ni docente (R-08/R-09) | No se pueden inventar | Registrados en `PASOS_MANUALES.md` (`inspector-guia`) |
| C-10 | El tablero G4 de `pmv_fastapi` usa SP por HU `[5,3,3,2,3,5]` = 21 SP, mientras S3-4 reparte 13 + 8 SP por sprint en las épicas EP-1.T/B/A/C | Posible discrepancia de desglose | Verificar contra S3-4 §10 antes de reutilizar G4 (`recursos-visuales` / redactor) |

## 16. Antecedente Flask (`anemia_junin/`), solo para citarlo como antecedente

- Stack: Flask, Jinja2, SQLite, Waitress y arquitectura hexagonal.
- Resultados: 266 pruebas pytest y 96,69 % de cobertura (1315/1360) en la ejecución de cierre (base 67f2c01).
- Evidencias: `anemia_junin/docs/evidencias/`.
- Carga: Locust con 20 usuarios durante 60 s.
- Uso en el informe: como **espiga técnica (spike) / prototipo del Incremento 1**. Mostró la viabilidad de la arquitectura hexagonal y detectó DEV-101 (números no finitos → HTTP 500). Se sustituyó por FastAPI + PostgreSQL para cumplir los NFR de integridad (PostgreSQL), contrato OpenAPI nativo y despliegue en contenedores/CI. Esta justificación del cambio es una **propuesta de redacción**: debe confirmarla el equipo (PASO MANUAL).

## 17. Nota de reproducción del 2026-10-01 (S6-08, `desarrollador`)

Reproducido en Windows 11, Python 3.14.6, SQLite, sin Docker. Salida literal en `pmv_fastapi/docs/evidencias/verificacion_s6_2026-10-01.md`.

| Dato | Declarado (v1.0-PMV) | Reproducido | Observación |
| --- | --- | --- | --- |
| Pruebas `pytest` por defecto | 73 (62 + 11) | **73 pasadas, 0 fallidas, 0 saltadas** | Coincide. `testpaths` excluye las E2E |
| Pruebas E2E | 4 | **no ejecutadas** (4 errores de entorno: falta `chromium_headless_shell-1194` de Playwright) | La cifra "77 = 62 + 11 + 4" sigue siendo la declarada en el tag; en esta sesión solo se reprodujeron 73 |
| Integración PostgreSQL | 11 | no ejecutada (sin Docker ni PostgreSQL local) | Las 11 de integración pasan en SQLite |
| Cobertura | 99 % (641 sentencias, 2 sin cubrir) | **99,07 %** (548 sentencias, 2 sin cubrir; 98 ramas, 4 parciales) | El porcentaje coincide; el conteo de sentencias difiere porque coverage con Python 3.14 cuenta distinto las sentencias multilínea (`esquemas.py` 28 vs 96; `entidades.py` 105 vs 123) |
| ruff | 0 hallazgos | **0 hallazgos**, 33 archivos formateados | Coincide |

Las marcas **[D]** de pruebas, cobertura y ruff pasan a **[V]** para la suite por defecto (73 pruebas). Siguen **[D]** las 4 E2E, la integración en PostgreSQL y la carga. La CI de la raíz es `.github/workflows/ci.yml` (la de `pmv_fastapi/.github/` queda como referencia, ver §10).
