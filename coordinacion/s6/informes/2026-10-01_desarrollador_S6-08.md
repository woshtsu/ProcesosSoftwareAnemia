# Informe desarrollador — S6-08 (2026-10-01)

Rama `feature/s6-integrador-final`. Sin commits, push ni tags.

## Cambios
- Nuevo `.github/workflows/ci.yml` (raíz): `defaults.run.working-directory: pmv_fastapi`, `paths` filtrados, caché pip con `cache-dependency-path`, artefactos `pmv_fastapi/coverage.xml` y `reporte-pruebas.xml`, `docker build ... pmv_fastapi`. YAML validado con PyYAML (2 jobs: `calidad-y-pruebas`, `imagen-staging`).
- Sonar condicional: se ejecuta solo si existen el secreto `SONAR_TOKEN` y la variable `SONAR_ORGANIZATION` (se pasa como `-Dsonar.organization`; `projectBaseDir: pmv_fastapi`). No se inventó organización. Corrige además el `if: env.SONAR_TOKEN` original, que nunca veía el secreto.
- El original `pmv_fastapi/.github/workflows/ci.yml` se conserva como referencia (no se movió).
- `pmv_fastapi/README.md`: comandos para Windows, Docker Compose con URL, qué corre `pytest` por defecto, cifras reproducidas, sección CI y activación de Sonar.
- `pmv_fastapi/docs/evidencias/verificacion_s6_2026-10-01.md` (salidas literales).
- `coordinacion/s6/DATOS_PMV_FASTAPI.md` §17 (nota de reproducción), `TABLERO_S6.md` (S6-08 HECHO).
- `.venv` creado en `pmv_fastapi/.venv` (ignorado por `pmv_fastapi/.gitignore`).

## Cifras reales (Python 3.14.6, SQLite)
- ruff: 0 hallazgos; 33 archivos formateados.
- pytest: 73 pasadas, 0 fallidas, 0 saltadas (62 unitarias + 11 integración).
- Cobertura 99,07 % (548 sentencias, 2 sin cubrir; ramas 98, 4 parciales).
- E2E (4): no ejecutadas, falta el navegador de Playwright (`chromium_headless_shell-1194`); descargarlo requiere permiso.
- PostgreSQL: no ejecutada (sin Docker). Humo manual: seed de 14 niños, `/api/salud`, `/`, `/docs`, `/api/ninos` responden 200.

## Ejecutar
- Local: ver README (`py -m venv .venv`; `pip install -r requirements-dev.txt`; `python -m scripts.cargar_datos_prueba`; `python -m uvicorn app.main:crear_app --factory --port 8000`) en http://127.0.0.1:8000 (docs en `/docs`).
- Docker: `POSTGRES_PASSWORD=... docker compose up -d --build` en `pmv_fastapi/`, http://localhost:8000.

## Problemas
- La instalación de pip falló una vez por un corte de red; se reintentó con éxito.
- Python 3.14: sin incompatibilidades; solo ResourceWarning y StarletteDeprecationWarning. El conteo de sentencias difiere del declarado (548 vs 641) por coverage en 3.14.
- Docker no está instalado: Compose y la imagen no se probaron.
- Pendiente manual: la ejecución en verde del CI en GitHub (requiere push del usuario).
