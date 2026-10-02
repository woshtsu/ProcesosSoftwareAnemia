# Sistema de detección temprana y seguimiento de anemia infantil (Junín, Perú)

Proyecto de la asignatura **Procesos de Software** (ASUC01702, Universidad Continental, ciclo 2026-20).

**Problema.** En las zonas rurales de Junín se pierde el seguimiento del tamizaje de hemoglobina, del tratamiento con hierro y de los controles de los niños con anemia. Las causas son:

- el *triple registro* manual (historia clínica, tarjeta de control y HIS);
- la agenda manual;
- las barreras familiares que no se ven;
- la conectividad limitada.

**Qué hace el proyecto.**

- Diseña el proceso TO-BE.
- Adapta (*tailoring*) un modelo iterativo-incremental gestionado con Scrum y apoyado en prácticas DevOps (y MLOps a partir del INC-5).
- Construye el **PMV del Incremento 1**: registro nominal validado y expediente digital único.

**Equipo.**

| Integrante | Rol |
| --- | --- |
| Porras Veli, Ricardo | Ingeniero de Proceso |
| Auqui Huincho, Tania | Ingeniera de Desarrollo y Prototipado |
| Huamani Rodriguez, Jean Piero | Ingeniero de Calidad y Mejora del Proceso |

> Todos los datos del software son **sintéticos**. La clasificación de anemia es referencial y no sustituye el criterio del profesional de salud.

## PMV oficial: `pmv_fastapi/` (tag `v1.0-PMV`)

| Aspecto | Valor (fuente: [`coordinacion/s6/DATOS_PMV_FASTAPI.md`](coordinacion/s6/DATOS_PMV_FASTAPI.md)) |
| --- | --- |
| Stack | Python 3.11, FastAPI, SQLAlchemy, **PostgreSQL 16** (staging/CI) y SQLite (desarrollo), cliente PWA |
| Arquitectura | Hexagonal (puertos y adaptadores) en un monolito modular. ADR-001 a ADR-006 en [`pmv_fastapi/docs/adr/`](pmv_fastapi/docs/adr/) |
| Alcance | HU-01 a HU-05 completas: registro, expediente, validación clínica, seguimiento y reporte JSON/CSV |
| Pruebas | **77 automatizadas** (62 unitarias, 11 de integración/API, 4 E2E con Playwright) y carga con Locust |
| Calidad | Cobertura del **99 %** (umbral del DoD: 80 %), **0 hallazgos de Ruff**, 2 defectos detectados y cerrados (2,0/KLOC) |
| Carga | 50 usuarios durante 60 s: **p95 = 58 ms**, 39,6 req/s, 0 % de errores (antes de DEF-01 el p95 era de 310 ms) |
| Despliegue | Docker Compose (API + `postgres:16-alpine`) como entorno de staging. Pipeline de GitHub Actions en `pmv_fastapi/.github/workflows/ci.yml` (ver nota) |
| Evidencias | [`pmv_fastapi/docs/evidencias/`](pmv_fastapi/docs/evidencias/): cobertura, ruff, CSV de carga, registro de defectos, capturas 01–08 y `demo_pmv.mp4` |

**Tag `v1.0-PMV`.**

- Apunta al commit `9ce90c3` de la rama `entrega-s5-s7`, que contiene el PMV en la raíz con su historial de ramas `feature/*` y `fix/*`.
- `main` contiene el **mismo código** dentro de `pmv_fastapi/` (integrado con el commit `0c9e302`).
- El tag no es alcanzable desde `main`. Moverlo o crear un tag nuevo es una decisión del equipo.

**CI.** GitHub solo ejecuta los flujos que están en `.github/workflows/` en la raíz del repositorio. Copiar el pipeline a esa ubicación es la tarea S6-08.

**Antecedente: `anemia_junin/`.** Es el prototipo Flask + SQLite del Incremento 1 que describían los entregables anteriores (266 pruebas y 96,69 % de cobertura en su ejecución de cierre). Se conserva como antecedente técnico y **no es el PMV que se entrega**.

## Cómo ejecutar el PMV

Desde `pmv_fastapi/`. El detalle completo está en [`pmv_fastapi/README.md`](pmv_fastapi/README.md).

**Desarrollo local.** Requiere Python 3.11 o superior. En PowerShell:

```powershell
cd pmv_fastapi
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m scripts.cargar_datos_prueba          # datos SINTÉTICOS
.\.venv\Scripts\python.exe -m uvicorn app.main:crear_app --factory --reload --port 8000
```

Abre http://127.0.0.1:8000 para la aplicación y http://127.0.0.1:8000/docs para la documentación OpenAPI.

**Staging con Docker (PostgreSQL 16).** En Bash:

```bash
cd pmv_fastapi
POSTGRES_PASSWORD=una_clave_segura docker compose up -d --build
docker compose exec api python -m scripts.cargar_datos_prueba
```

El esquema de base de datos está en `pmv_fastapi/db/01_esquema_postgresql.sql` y se aplica automáticamente al iniciar el contenedor `db`.

**Pruebas y calidad.**

```bash
cd pmv_fastapi
ruff check . && ruff format --check .
pytest --cov=app                                                     # unitarias + integración (SQLite)
TEST_DATABASE_URL=postgresql+psycopg2://... pytest tests/integracion --no-cov
python -m playwright install chromium && pytest tests/e2e -m e2e --no-cov
locust -f tests/rendimiento/locustfile.py --host http://127.0.0.1:8000 --headless -u 50 -r 10 -t 60s
```

## Entregables por semana (estado real al 2026-10-01)

| Semana | Tema | Guía | Entregable vigente | Estado |
| --- | --- | --- | --- | --- |
| S1 | Enfoque de procesos: problema, actores, AS-IS, brechas, TO-BE, cadena de valor e indicadores | [Guía S1](guias/S1.Gu%C3%ADa%20de%20trabajo%20semana%201.md) | [`Entregable_Semana1`](entregables/semana-01/Entregable_Semana1_Anemia_Junin.md) | En revisión. Las figuras 10–14 ya existen en SVG/PNG (DIAG-001..005 resueltas); queda retirar los marcadores `<!-- DIAG pendiente -->` |
| S2 | Selección y justificación del modelo de proceso | [Guía S2](guias/S2.Gu%C3%ADa%20de%20trabajo%20semana%202.md) | [`Entregable_Semana2`](entregables/semana-02/Entregable_Semana2_Anemia_Junin.md) | En revisión. La figura 15 existe (DIAG-006 resuelta); quedan `[PENDIENTE]` de datos del equipo |
| S3-4 | Actividades, RAE, DoD, WBS, priorización, estimación, plan y seguimiento | [Guía S3-4](guias/S3.GU%C3%8DA%20DE%20TRABAJO%20SEMANA%203%20Y%204.md) | [`Entregable_Semana3y4`](entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md) | En revisión. Las figuras 30–35 existen (DIAG-100..105 resueltas); el burndown es simulado |
| S5 | Ejecución de los procesos principales del Incremento 1 | [Guía S5](guias/S5-PSW-GU%C3%8DA%20DE%20TRABAJO%20SEMANA%205.md) | [`Entregable_Semana5`](entregables/semana-05/Entregable_Semana5_Anemia_Junin.md) | Existe, pero **describe el antecedente Flask** y tiene `CARGA_CIERRE` y `[PENDIENTE]`. Pendiente de la decisión del usuario (S6-11) |
| S6 | Integrador de las Unidades I y II: informe, 7 diapositivas y repositorio con tag | [Consigna S6](guias/S6.CONSIGNA%20DE%20TRABAJO%20E%20INSTRUMENTO%20DE%20EVALUACI%C3%93N%20INTEGRADOR.md) | [`Informe_Integrador`](entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md); presentación en `entregables/semana-06-integrador/presentacion/` (por crear) | **En curso** en la rama `feature/s6-integrador-final`. El informe actual describe Flask y se va a reescribir (S6-03). La presentación de 7 diapositivas aún no existe (S6-04). `exportados/` está vacío (S6-05) |

El seguimiento del cierre S6 está en [`coordinacion/s6/TABLERO_S6.md`](coordinacion/s6/TABLERO_S6.md) y los requisitos de la consigna en [`coordinacion/s6/REQUISITOS_S6.md`](coordinacion/s6/REQUISITOS_S6.md) (91 requisitos, R-01 a R-91).

## Estructura del repositorio

```text
.
├── README.md                    este archivo
├── AGENTS.md                    instrucciones de continuidad para agentes
├── .claude/agents/              definiciones de los subagentes
├── coordinacion/                canal de comunicación entre agentes
│   ├── TABLERO.md · RUTAS.md · PROTOCOLO.md · plantillas/ · solicitudes/ · informes/
│   └── s6/                      cierre S6: REQUISITOS_S6, DATOS_PMV_FASTAPI, CONTEXTO_PROCESOS_S1_S5,
│                                PROTOCOLO_S6, TABLERO_S6, solicitudes/VIS-###.md
├── guias/                       guías y consigna del docente (solo lectura)
├── entregables/                 versión VIGENTE de cada entregable (.md)
├── diagramas/                   src/ (puml, py) · png/ · svg/ · README.md (catálogo)
├── pmv_fastapi/                 PMV OFICIAL (FastAPI + PostgreSQL, Docker, CI, pruebas, evidencias)
├── anemia_junin/                antecedente: prototipo Flask del Incremento 1 (solo lectura)
├── herramientas/                generador de diagramas (PlantUML local) y conversión
├── exportados/                  PDF/DOCX/PPTX derivados para el aula virtual (exportados/semana-06/)
└── archivo/                     histórico: versiones anteriores, agentes anteriores, PDF, zip
```

Cada ruta se detalla en [`coordinacion/RUTAS.md`](coordinacion/RUTAS.md).

## Agentes y coordinación

| Agente | Modelo | Rol |
| --- | --- | --- |
| `sincronizador` | opus | Coordinación, fuentes de verdad, rutas, tableros, README y commits |
| `redactor-informe-integrador` | sonnet | Informe Integrador S6 |
| `disenador-diapositivas` | sonnet | 7 diapositivas (Marp), guion de 7 min y PPTX/PDF |
| `recursos-visuales` | haiku | Diagramas y gráficos (PlantUML local y matplotlib), solicitudes `VIS-###` |
| `inspector-guia` | sonnet | Verificación al 100 % frente a la consigna y pasos manuales |
| `guardian-merge` | haiku | Comprobaciones previas al merge (sin push) |
| `conversor-entregas` | haiku | Conversión de .md a PDF/DOCX |
| `desarrollador` | opus | PMV `pmv_fastapi/`, CI y evidencias |
| `revisor-documental` | opus | Entregables S1–S5 |
| `investigador` | haiku | Investigación con fuentes (solo lectura) |

Los agentes se comunican **solo mediante archivos**: tareas en los tableros, solicitudes `<PREFIJO>-###` e informes. Las reglas están en [`coordinacion/PROTOCOLO.md`](coordinacion/PROTOCOLO.md) y, para S6, en [`coordinacion/s6/PROTOCOLO_S6.md`](coordinacion/s6/PROTOCOLO_S6.md).

## Herramientas locales (2026-10-01)

| Herramienta | Estado |
| --- | --- |
| Python 3.14.6 | Disponible, sin las dependencias del PMV instaladas. El PMV apunta a Python 3.11 |
| Java 17 (OpenJDK 17.0.19) | Disponible |
| Node v24.19.0 | Disponible (marp-cli necesita descargarse con permiso del usuario) |
| PlantUML (`herramientas/plantuml/plantuml.jar`) | No descargado: obtenerlo de Maven Central (ver [`herramientas/README.md`](herramientas/README.md)) |
| Pandoc | No instalado |
