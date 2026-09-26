# PMV Anemia Junín — INC-1: registro nominal validado y expediente digital

Producto mínimo viable del *Sistema de detección temprana y seguimiento de anemia infantil en zonas rurales de Junín* (curso Procesos de Software). Implementa las historias **HIST-1.1 a HIST-1.5** del Incremento 1 con **Python + Flask**, **arquitectura hexagonal** (puertos y adaptadores) y **SQLite**.

> **Demostración académica con datos sintéticos.** La clasificación de hemoglobina es **referencial** (NTS N.° 213-MINSA/DGIESP-2024) y no constituye diagnóstico clínico. No registre datos de personas reales.

## 1. Requisitos

| Requisito | Versión verificada |
| --- | --- |
| Python | ≥ 3.12 (verificado con **CPython 3.14.6**, Windows 11) |
| pip | ≥ 23 (verificado con 26.x) |
| Navegador | cualquiera moderno (solo para usar la interfaz web) |

No requiere servicios externos: la base de datos es un archivo SQLite que se crea solo.

## 2. Instalación

Desde la carpeta `anemia_junin/`:

```powershell
py -3 -m venv .venv                 # o: python -m venv .venv
.venv\Scripts\activate              # Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"             # app + herramientas de prueba (pytest, ruff, locust…)
```

Solo para ejecutar la app (sin herramientas de desarrollo): `pip install -e .`

> Las dependencias se declaran con **versiones mínimas** (`>=`). Las versiones fijas originales (p. ej. `locust==2.32.3`) arrastraban `gevent`/`greenlet` sin *wheels* para Python 3.14 en Windows y exigían compilar con Visual Studio. Las versiones instaladas y verificadas están en `docs/evidencias/versiones_instaladas.txt`.

## 3. Configuración (opcional)

| Variable de entorno | Por defecto | Uso |
| --- | --- | --- |
| `ANEMIA_DB_PATH` | `instance/anemia.db` | Ruta de la BD SQLite |
| `ANEMIA_NORMATIVA_PATH` | `config/normativa_v1.json` | Tabla normativa (umbrales y ajuste por altitud) |
| `ANEMIA_SECRET_KEY` | clave de desarrollo | Sesiones y token CSRF de formularios (**cámbiela** fuera de la demo) |
| `ANEMIA_HOST` / `ANEMIA_PORT` | `127.0.0.1` / `8000` | Interfaz y puerto del servidor |

Las **migraciones** (`migrations/*.sql`) se aplican automáticamente al arrancar (idempotentes, tabla `schema_version`). Si `config/normativa_v1.json` falta o es inválido, la aplicación **no arranca** (`NormativaInvalidaError`).

## 4. Carga de datos sintéticos

```powershell
python scripts/cargar_datos_sinteticos.py                   # → instance/anemia.db
python scripts/cargar_datos_sinteticos.py --db instance/demo.db
```

Crea **30 niños sintéticos** (DNI 10000000–10000029) en 10 distritos de Junín (628 a 4107 msnm), 24 con dosaje inicial y ~11 con un segundo dosaje, y **3 intentos de alta inválidos** a propósito para poblar el indicador de calidad. Todas las altas pasan por la API (mismas validaciones que la interfaz). Solo carga sobre una BD sin niños; para repetir, use otra ruta con `--db` o borre el archivo de la BD de demostración.

## 5. Ejecución

```powershell
python -m anemia_junin                 # Waitress (servidor WSGI de producción) en http://127.0.0.1:8000/
python -m anemia_junin --port 8080     # otro puerto
python -m anemia_junin --dev           # servidor de desarrollo de Flask (recarga y depuración)
python -m anemia_junin --db instance/demo.db
```

Abra **http://127.0.0.1:8000/** (redirige a la lista de niños). Detener: `Ctrl+C`.

| Página | URL |
| --- | --- |
| Lista de niños en seguimiento (HIST-1.4) | `/ninos` |
| Registrar niño (HIST-1.1 / 1.3) | `/ninos/nuevo` |
| Expediente (HIST-1.2) | `/ninos/<dni>` |
| Editar datos permitidos | `/ninos/<dni>/editar` |
| Nuevo dosaje | `/ninos/<dni>/dosajes/nuevo` |
| Reporte del periodo (HIST-1.5) | `/reportes/registros?desde=AAAA-MM-DD&hasta=AAAA-MM-DD` |

Verificación rápida con el servidor levantado (15 comprobaciones HTTP y latencia):

```powershell
python scripts/smoke_test.py --url http://127.0.0.1:8000
```

## 6. Pruebas, cobertura, lint y carga

```powershell
ruff check .                                  # análisis estático (0 hallazgos)
pytest                                        # suite completa
pytest --cov --cov-report=term-missing        # cobertura (umbral mínimo 80 %, falla si no se alcanza)
pytest --cov --cov-report=html:docs/evidencias/htmlcov
pytest -W error                               # advertencias tratadas como error
pytest -n auto                                # en paralelo (pytest-xdist)
pytest -m e2e                                 # solo el flujo extremo a extremo
```

**Resultado verificado (2026-09-25, Python 3.14.6):** `242 passed`, cobertura de líneas **96,66 %** (1348 sentencias, 45 sin cubrir), `ruff check .` → *All checks passed!* Salidas completas en `docs/evidencias/`.

| Carpeta | Tipo | Casos |
| --- | --- | ---: |
| `tests/domain/` | Unitarias de dominio (validaciones, clasificador, umbrales y bandas de altitud) | 108 |
| `tests/api/` | Integración HTTP de la API, endurecimiento de entrada y **contrato OpenAPI** (rutas + esquemas con jsonschema) | 60 |
| `tests/web/` | Interfaz web: PRG 303, errores por campo, semáforo con texto, CSRF, advertencias | 33 |
| `tests/persistencia/` | SQLite real: repositorios, migraciones, transacciones, **concurrencia**, reloj inyectado | 24 |
| `tests/arquitectura/` | Reglas de dependencia hexagonal (análisis AST) | 8 |
| `tests/test_entrypoint_y_scripts.py` | Punto de entrada, variables de entorno, script de datos, error 500 sin trazas | 7 |
| `tests/e2e/` | Servidor HTTP real (Werkzeug) con CSRF activo + smoke test | 2 |

**E2E sin navegador.** `tests/e2e/test_flujo_http.py` levanta la app en un puerto libre y recorre el flujo completo con peticiones HTTP reales y cookies (lista → alta con token CSRF → expediente → error de validación → nuevo dosaje → reporte → API). No se usa Playwright porque exige descargar navegadores (`playwright install`); la dependencia queda declarada para cuando se disponga de ellos.

**Carga (Locust).** Con el servidor levantado sobre una BD de prueba:

```powershell
python scripts/cargar_datos_sinteticos.py --db instance/carga.db
python -m anemia_junin --port 8001 --db instance/carga.db      # en otra terminal
locust -f tests/carga/locustfile.py --host http://127.0.0.1:8001 --headless -u 20 -r 5 -t 60s --csv tests/carga/results/carga
```

Resultado verificado (20 usuarios, 60 s, Waitress 8 hilos, equipo local): **1011 peticiones, 0 fallos, 17,0 req/s, mediana 17 ms, p95 53 ms, p99 74 ms, máximo 113 ms** (`docs/evidencias/carga_locust_20u_60s.txt`). Criterio propuesto: 0 % de errores y p95 < 2000 ms → **cumple**.

## 7. API REST (`/api/v1`, contrato en `openapi.yaml`)

| Método | Ruta | Descripción | Respuestas |
| --- | --- | --- | --- |
| GET | `/salud` | Estado de la app y de la BD | 200 |
| GET | `/ninos?q=&distrito=&clasificacion=&pagina=&tamano=` | Niños de 6–59 meses, ordenados por severidad | 200, 400 |
| POST | `/ninos` | Alta con dosaje inicial opcional (atómica) | 201, 400, 409, 415 |
| GET | `/ninos/{dni}` | Expediente e historial de dosajes | 200, 404 |
| PATCH | `/ninos/{dni}` | Actualiza solo `peso_kg`, `distrito`, `altitud_msnm`, `cuidador`, `telefono` | 200, 400, 404, 415 |
| POST | `/ninos/{dni}/dosajes` | Nuevo dosaje (ajuste por altitud y clasificación calculados) | 201, 400, 404, 415 |
| GET | `/reportes/registros?desde=&hasta=` | Conteos, distribución y **% de registros sin error crítico** | 200, 400 |

Errores con formato uniforme `{"error": {"code", "message", "fields"}}`, sin trazas internas. Ejemplo:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/ninos -H "Content-Type: application/json" `
  -d '{\"dni\":\"90000001\",\"nombres\":\"Ana\",\"apellidos\":\"Quispe Rojas\",\"fecha_nacimiento\":\"2024-05-10\",\"sexo\":\"F\",\"tipo_nacimiento\":\"TERMINO\",\"peso_kg\":9.2,\"distrito\":\"Huancayo\",\"altitud_msnm\":3271,\"cuidador\":\"Rosa Rojas\",\"dosaje_inicial\":{\"fecha_dosaje\":\"2026-09-20\",\"hb_observada\":11.4}}'
```

## 8. Estructura (arquitectura hexagonal)

```text
anemia_junin/
├── src/anemia_junin/
│   ├── domain/            # Núcleo: entidades, validadores, clasificador, puertos (Protocol). Sin Flask ni SQLite.
│   ├── application/       # Casos de uso (registrar, consultar, actualizar, agregar dosaje, listar, reporte) y DTO
│   ├── adapters/
│   │   ├── inbound/       # rest_api/ (JSON) y web_ui/ (HTML + CSRF): solo invocan casos de uso
│   │   └── outbound/      # sqlite/ (repositorios, unidad de trabajo, migraciones) y normativa/ (JSON)
│   ├── templates/, static/  # Jinja2 + CSS (sin JavaScript ni CDN)
│   ├── bootstrap.py       # Único punto de cableado (inyección de dependencias)
│   └── __main__.py        # python -m anemia_junin
├── config/normativa_v1.json   # Umbrales por edad y ajuste por altitud (versionado)
├── migrations/001_initial.sql # Esquema: ninos, dosajes, intentos_registro, schema_version
├── scripts/                   # cargar_datos_sinteticos.py, smoke_test.py
├── tests/                     # domain, api, web, persistencia, arquitectura, e2e, carga
├── docs/adr/                  # Decisiones de arquitectura (ADR-001, ADR-002)
├── docs/trazabilidad.md       # HIST-1.x → caso de uso → pruebas
├── docs/evidencias/           # Salidas reales de pytest, ruff, smoke test y Locust
└── openapi.yaml               # Contrato de la API (validado por pruebas)
```

Reglas verificadas automáticamente (`tests/arquitectura/`): el dominio y la aplicación no importan Flask, SQLite ni adaptadores; los adaptadores de entrada no importan los de salida ni `sqlite3`; `bootstrap.py` es el único punto de cableado. El tiempo se obtiene del puerto `Reloj` (también en el listado de 6–59 meses).

## 9. Normativa

`config/normativa_v1.json` — NTS N.° 213-MINSA/DGIESP-2024, **aprobada por la RM 251-2024-MINSA** (deroga la NTS 134-2017) y **modificada por la RM 429-2024-MINSA** (ver `coordinacion/solicitudes/INV-001.md`). Hb y ajustes se guardan como enteros en décimas de g/dL. Las bandas de altitud **≥ 4000 msnm** están marcadas `"verificada": false`: cada dosaje que las usa lleva una advertencia visible en el expediente («solo referencial») hasta contrastarlas con la tabla oficial.

## 10. Limitaciones conocidas (backlog)

- Sin cuentas de usuario ni roles; solo uso local (`127.0.0.1`), sin HTTPS.
- Sin modo offline/sincronización ni PostgreSQL (INC-3), sin agenda/alertas (INC-2), sin integración HIS.
- Sin integración continua (GitHub Actions) ni SonarCloud: el análisis estático es `ruff`.
- E2E con navegador (Playwright) no ejecutado; el criterio «registrar en < 3 minutos» no está instrumentado.
- Datos sintéticos: las fechas se calculan respecto al día de carga, por lo que las clasificaciones exactas varían según la fecha.
