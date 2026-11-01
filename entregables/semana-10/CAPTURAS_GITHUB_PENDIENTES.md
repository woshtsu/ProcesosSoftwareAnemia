# Capturas de GitHub — Semana 10 (FURPS+)

> **Estado: completadas (30/10/2026).** Las 23 capturas se tomaron en GitHub sobre la etiqueta `v4.0-Inc4` (commit `e6886e2`) y la ejecución verde #14 de Actions; están en `evidencias/github/` y enlazadas en el informe. La lista se conserva como registro.

Las capturas de código deben salir de GitHub (repositorio privado `woshtsu/ProcesosSoftwareAnemia`), no del entorno local. Cada fila corresponde a un marcador `<captura de pantalla de GitHub: ...>` del informe `Entregable_Semana10_Anemia_Junin.md`.

## Cómo tomarlas

1. Abrir el archivo en GitHub en la etiqueta indicada (`/blob/v4.0-Inc4/<ruta>`). Si la etiqueta aún no existe, usar el commit `e6886e2` (`/blob/e6886e2/<ruta>`) y anotarlo en el pie de la figura.
2. Para rangos de líneas, abrir la URL con `#Lx-Ly` para que GitHub resalte el rango; la captura debe mostrar la ruta, el selector de rama o etiqueta y los números de línea.
3. Los números de línea se midieron en el commit `e6886e2` (`pmv_fastapi/` es idéntico en `ada827f`). Si la etiqueta `v4.0-Inc4` apunta a otro commit (por ejemplo, `5c1f1eb`), comprobar que las líneas coinciden con lo que debe verse y ajustar el rango en el informe.
4. Guardar cada PNG en `entregables/semana-10/evidencias/github/` con el nombre de la última columna. No incluir tokens, correos ni datos personales.
5. Las dos últimas filas no son archivos: son páginas de GitHub (`actions` y `tags`).

## Lista de capturas

| N.° figura | Ruta del archivo | Líneas | Rama o etiqueta | Qué debe verse | PNG de destino |
| --- | --- | --- | --- | --- | --- |
| 63 | `pmv_fastapi/app/web/estilos.css` | L1-L6 | `v4.0-Inc4` | las variables `:root` con la paleta (azul, fondo, verde, ámbar, naranja, rojo y sus fondos suaves) | `evidencias/github/GH_paleta_estilos_css.png` |
| 76 | `pmv_fastapi/app/adapters/outbound/persistence/sqlalchemy_repo.py` | L533-L533 | `v4.0-Inc4` | `create_engine(url, ..., pool_pre_ping=True)`, la reconexión del pool que se probó con el caos | `evidencias/github/GH_pool_pre_ping.png` |
| 78 | `pmv_fastapi/app/` | vista de carpeta o página, sin líneas | `v4.0-Inc4` | el árbol de carpetas `domain/`, `ports/` (`inbound/` y `outbound/`), `application/` y `adapters/` (`inbound/` y `outbound/`) en GitHub | `evidencias/github/GH_arbol_app.png` |
| 79 | `pmv_fastapi/app/domain/model/entidades.py` | L1-L12 | `v4.0-Inc4` | la docstring «Puras: sin frameworks ni reglas clínicas» y solo importaciones de la biblioteca estándar y de `app.domain.model` | `evidencias/github/GH_dominio_entidades_imports.png` |
| 80 | `pmv_fastapi/app/ports/outbound/notificador.py` | L1-L13 | `v4.0-Inc4` | el puerto de salida `Notificador` como interfaz abstracta, sin importar adaptadores | `evidencias/github/GH_puerto_notificador.png` |
| 81 | `pmv_fastapi/app/main.py` | L40-L122 | `v4.0-Inc4` | la raíz de composición donde se conectan casos de uso y adaptadores (único módulo que conoce ambos) | `evidencias/github/GH_main_composicion.png` |
| 91 | `pmv_fastapi/tests/arquitectura/test_dependencias.py` | L55-L104 | `v4.0-Inc4` | las pruebas CP-37 a CP-43 que impiden que el dominio, los puertos y la aplicación importen frameworks o adaptadores | `evidencias/github/GH_pruebas_arquitectura.png` |
| 101 | `pmv_fastapi/app/adapters/inbound/http/autenticacion.py` | L40-L82 | `v4.0-Inc4` | cookies `httponly=True`, `samesite="strict"`, `path="/api"`, `Cache-Control: no-store` y la comprobación de `X-CSRF-Protection` y `Origin` | `evidencias/github/GH_sesion_cookies_csrf.png` |
| 102 | `pmv_fastapi/app/domain/service/notificaciones.py` | L206-L226 | `v4.0-Inc4` | `firma_valida`, `verificacion_valida` y `firmar` con `hmac.compare_digest` y HMAC-SHA256 | `evidencias/github/GH_webhook_firma_hmac.png` |
| 103 | `pmv_fastapi/app/adapters/inbound/http/api.py` | L1025-L1045 | `v4.0-Inc4` | la ruta POST del webhook de WhatsApp que exige `X-Hub-Signature-256` | `evidencias/github/GH_webhook_ruta_api.png` |
| 104 | `pmv_fastapi/app/adapters/inbound/http/api.py` | L238-L242 | `v4.0-Inc4` | el manejador que responde 503 sin secreto configurado y 403 con firma inválida (falla cerrado) | `evidencias/github/GH_webhook_falla_cerrado.png` |
| 105 | `pmv_fastapi/db/02_supabase.sql` | L1-L16 | `v4.0-Inc4` | `ENABLE ROW LEVEL SECURITY` en las 8 tablas y `REVOKE ALL ... FROM anon, authenticated` | `evidencias/github/GH_rls_supabase.png` |
| 106 | `pmv_fastapi/app/domain/service/validaciones.py` | L39-L130 | `v4.0-Inc4` | las funciones de validación de altitud, fecha de nacimiento, datos del niño, evaluación y rangos | `evidencias/github/GH_validaciones_dominio.png` |
| 107 | `pmv_fastapi/app/application/servicio_sincronizacion.py` | L93-L108 | `v4.0-Inc4` | la sincronización bajo cerrojo y el reenvío de una operación ya aplicada (idempotencia por `id_operacion`) | `evidencias/github/GH_sincronizacion_idempotente.png` |
| 108 | `pmv_fastapi/app/web/app.js` | L41-L41 | `v4.0-Inc4` | la función `esc()` que escapa `& < > "` antes de usar `innerHTML` | `evidencias/github/GH_esc_app_js.png` |
| 112 | `pmv_fastapi/app/adapters/inbound/http/api.py` | L749-L793 | `v4.0-Inc4` | el endpoint del reporte que escribe nombre y comunidad al CSV con `csv.writer` sin neutralizar fórmulas (H-3) | `evidencias/github/GH_csv_reporte_hallazgo.png` |
| 114 | `pmv_fastapi/Dockerfile` | L1-L12 | `v4.0-Inc4` | `FROM python:3.11-slim`, `USER appuser` y `HEALTHCHECK` | `evidencias/github/GH_dockerfile.png` |
| 115 | `pmv_fastapi/docker-compose.yml` | L1-L40 | `v4.0-Inc4` | los servicios `db` (PostgreSQL 16) y la aplicación con `AUTH_MODE` y `healthcheck` | `evidencias/github/GH_docker_compose.png` |
| 116 | `pmv_fastapi/docs/openapi.json` | L1-L12 | `v4.0-Inc4` | el encabezado del contrato OpenAPI 3 con título y versión | `evidencias/github/GH_openapi_json.png` |
| 117 | `pmv_fastapi/pyproject.toml` | L7-L21 | `v4.0-Inc4` | la configuración de Ruff (reglas `E,F,W,I,B,UP,S,C90`, complejidad máxima 12) | `evidencias/github/GH_pyproject_ruff.png` |
| 118 | `.github/workflows/ci.yml` | L1-L91 | `v4.0-Inc4` | los trabajos `calidad-y-pruebas` (Ruff, pytest con cobertura, OpenAPI, PostgreSQL, E2E) e `imagen` (`docker build`) | `evidencias/github/GH_ci_workflow.png` |
| 119 | `actions/workflows/ci.yml` | vista de carpeta o página, sin líneas | `v4.0-Inc4` | la lista de ejecuciones de «CI y producción — PMV Anemia Junín» con una ejecución en verde del commit de `v4.0-Inc4` y sus trabajos `calidad-y-pruebas` e `imagen` completados | `evidencias/github/GH_actions_ejecucion_verde.png` |
| 120 | `tags` | vista de carpeta o página, sin líneas | `v4.0-Inc4` | la lista de etiquetas con `v1.0-PMV`, `v2.0-Inc2`, `v3.0-Inc3` y `v4.0-Inc4`, con su fecha y commit | `evidencias/github/GH_etiquetas.png` |

Total: 23 capturas pendientes.

## Marcadores tal como aparecen en el informe

- Figura 63: `<captura de pantalla de GitHub: pmv_fastapi/app/web/estilos.css#L1-L6 en la etiqueta v4.0-Inc4 mostrando las variables `:root` con la paleta (azul, fondo, verde, ámbar, naranja, rojo y sus fondos suaves)>`
- Figura 76: `<captura de pantalla de GitHub: pmv_fastapi/app/adapters/outbound/persistence/sqlalchemy_repo.py#L533-L533 en la etiqueta v4.0-Inc4 mostrando `create_engine(url, ..., pool_pre_ping=True)`, la reconexión del pool que se probó con el caos>`
- Figura 78: `<captura de pantalla de GitHub: pmv_fastapi/app/ en la etiqueta v4.0-Inc4 mostrando el árbol de carpetas `domain/`, `ports/` (`inbound/` y `outbound/`), `application/` y `adapters/` (`inbound/` y `outbound/`) en GitHub>`
- Figura 79: `<captura de pantalla de GitHub: pmv_fastapi/app/domain/model/entidades.py#L1-L12 en la etiqueta v4.0-Inc4 mostrando la docstring «Puras: sin frameworks ni reglas clínicas» y solo importaciones de la biblioteca estándar y de `app.domain.model`>`
- Figura 80: `<captura de pantalla de GitHub: pmv_fastapi/app/ports/outbound/notificador.py#L1-L13 en la etiqueta v4.0-Inc4 mostrando el puerto de salida `Notificador` como interfaz abstracta, sin importar adaptadores>`
- Figura 81: `<captura de pantalla de GitHub: pmv_fastapi/app/main.py#L40-L122 en la etiqueta v4.0-Inc4 mostrando la raíz de composición donde se conectan casos de uso y adaptadores (único módulo que conoce ambos)>`
- Figura 91: `<captura de pantalla de GitHub: pmv_fastapi/tests/arquitectura/test_dependencias.py#L55-L104 en la etiqueta v4.0-Inc4 mostrando las pruebas CP-37 a CP-43 que impiden que el dominio, los puertos y la aplicación importen frameworks o adaptadores>`
- Figura 101: `<captura de pantalla de GitHub: pmv_fastapi/app/adapters/inbound/http/autenticacion.py#L40-L82 en la etiqueta v4.0-Inc4 mostrando cookies `httponly=True`, `samesite="strict"`, `path="/api"`, `Cache-Control: no-store` y la comprobación de `X-CSRF-Protection` y `Origin`>`
- Figura 102: `<captura de pantalla de GitHub: pmv_fastapi/app/domain/service/notificaciones.py#L206-L226 en la etiqueta v4.0-Inc4 mostrando `firma_valida`, `verificacion_valida` y `firmar` con `hmac.compare_digest` y HMAC-SHA256>`
- Figura 103: `<captura de pantalla de GitHub: pmv_fastapi/app/adapters/inbound/http/api.py#L1025-L1045 en la etiqueta v4.0-Inc4 mostrando la ruta POST del webhook de WhatsApp que exige `X-Hub-Signature-256`>`
- Figura 104: `<captura de pantalla de GitHub: pmv_fastapi/app/adapters/inbound/http/api.py#L238-L242 en la etiqueta v4.0-Inc4 mostrando el manejador que responde 503 sin secreto configurado y 403 con firma inválida (falla cerrado)>`
- Figura 105: `<captura de pantalla de GitHub: pmv_fastapi/db/02_supabase.sql#L1-L16 en la etiqueta v4.0-Inc4 mostrando `ENABLE ROW LEVEL SECURITY` en las 8 tablas y `REVOKE ALL ... FROM anon, authenticated`>`
- Figura 106: `<captura de pantalla de GitHub: pmv_fastapi/app/domain/service/validaciones.py#L39-L130 en la etiqueta v4.0-Inc4 mostrando las funciones de validación de altitud, fecha de nacimiento, datos del niño, evaluación y rangos>`
- Figura 107: `<captura de pantalla de GitHub: pmv_fastapi/app/application/servicio_sincronizacion.py#L93-L108 en la etiqueta v4.0-Inc4 mostrando la sincronización bajo cerrojo y el reenvío de una operación ya aplicada (idempotencia por `id_operacion`)>`
- Figura 108: `<captura de pantalla de GitHub: pmv_fastapi/app/web/app.js#L41-L41 en la etiqueta v4.0-Inc4 mostrando la función `esc()` que escapa `& < > "` antes de usar `innerHTML`>`
- Figura 112: `<captura de pantalla de GitHub: pmv_fastapi/app/adapters/inbound/http/api.py#L749-L793 en la etiqueta v4.0-Inc4 mostrando el endpoint del reporte que escribe nombre y comunidad al CSV con `csv.writer` sin neutralizar fórmulas (H-3)>`
- Figura 114: `<captura de pantalla de GitHub: pmv_fastapi/Dockerfile#L1-L12 en la etiqueta v4.0-Inc4 mostrando `FROM python:3.11-slim`, `USER appuser` y `HEALTHCHECK`>`
- Figura 115: `<captura de pantalla de GitHub: pmv_fastapi/docker-compose.yml#L1-L40 en la etiqueta v4.0-Inc4 mostrando los servicios `db` (PostgreSQL 16) y la aplicación con `AUTH_MODE` y `healthcheck`>`
- Figura 116: `<captura de pantalla de GitHub: pmv_fastapi/docs/openapi.json#L1-L12 en la etiqueta v4.0-Inc4 mostrando el encabezado del contrato OpenAPI 3 con título y versión>`
- Figura 117: `<captura de pantalla de GitHub: pmv_fastapi/pyproject.toml#L7-L21 en la etiqueta v4.0-Inc4 mostrando la configuración de Ruff (reglas `E,F,W,I,B,UP,S,C90`, complejidad máxima 12)>`
- Figura 118: `<captura de pantalla de GitHub: .github/workflows/ci.yml#L1-L91 en la etiqueta v4.0-Inc4 mostrando los trabajos `calidad-y-pruebas` (Ruff, pytest con cobertura, OpenAPI, PostgreSQL, E2E) e `imagen` (`docker build`)>`
- Figura 119: `<captura de pantalla de GitHub: actions/workflows/ci.yml en la etiqueta v4.0-Inc4 mostrando la lista de ejecuciones de «CI y producción — PMV Anemia Junín» con una ejecución en verde del commit de `v4.0-Inc4` y sus trabajos `calidad-y-pruebas` e `imagen` completados>`
- Figura 120: `<captura de pantalla de GitHub: tags en la etiqueta v4.0-Inc4 mostrando la lista de etiquetas con `v1.0-PMV`, `v2.0-Inc2`, `v3.0-Inc3` y `v4.0-Inc4`, con su fecha y commit>`
