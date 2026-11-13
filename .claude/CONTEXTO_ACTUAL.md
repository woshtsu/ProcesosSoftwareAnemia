# Contexto actual para continuar el proyecto

Actualizado: **23/10/2026, America/Lima**. Responsable de esta actualización: Codex, con roles secuenciales de orquestador, desarrollador y conversor. Es una instantánea; consultar siempre el [tablero](coordinacion/TABLERO.md), el código y `git status` antes de actuar.

## Qué proyecto se está trabajando

Anemia Junín es un proyecto académico de la Universidad Continental para apoyar el registro y seguimiento de anemia infantil. El software vigente está en [pmv_fastapi/](../pmv_fastapi/README.md): FastAPI, interfaz HTML/CSS/JS y arquitectura hexagonal, con SQLite o PostgreSQL. `anemia_junin/` conserva el prototipo Flask anterior. Las reglas y la clasificación son referenciales; no se ha realizado un piloto clínico ni una evaluación de satisfacción con usuarios reales.

## Últimos cambios

| Tarea | Qué se hizo | Estado y evidencia |
| --- | --- | --- |
| T-013 | Resueltos 88 conflictos del merge de `main` en `feature/inc2-agenda-alertas`, conservando el Incremento 2 completo. `main` avanzó por fast-forward. Se mantuvo una figura 1.5 heredada y se corrigió CP-177 para rutas de Windows. | Commit de integración `f9e8597`, padres `031da6d` y `e24d8bd`. [Informe](coordinacion/informes/2026-10-23_orquestador_T-013.md). |
| T-014 | Síntesis de feria con problemática, solución, impacto y tres capturas de S9. PDF A4 de tres páginas, aproximadamente 617 KB, con revisión visual. | [Fuente Markdown](../entregables/semana-11/feria/Proyecto_Feria_Anemia_Junin.md), [PDF](../exportados/feria/Proyecto_Feria_Anemia_Junin.pdf), [generador](.claude/herramientas/conversion/exportar_feria.py), [informe](coordinacion/informes/2026-10-23_conversor-entregas_T-014.md). El usuario lo subirá a la feria. |
| T-015 | Login con Supabase Auth: correo/contraseña, sesión, renovación, cierre, protección de API y auditoría con UUID verificado. | Implementación local verificada; **EN REVISIÓN**, pendiente primera cuenta y prueba remota. [Informe](coordinacion/informes/2026-10-23_desarrollador_T-015.md), [ADR-011](../pmv_fastapi/docs/adr/ADR-011-supabase-auth.md). |
| T-016 | Entrada y contexto compartidos, canal de intercambios y plantilla en `.claude/`, enlazados al protocolo existente. | [Entrada](CLAUDE.md), [intercambios](intercambios/README.md), [informe](coordinacion/informes/2026-10-23_orquestador_T-016.md). |

Al preparar este resumen, la rama activa es `main`, HEAD es `f9e8597` y la referencia local `origin/main` apunta al mismo commit. Los cambios de feria, Auth y esta documentación aún están en el directorio de trabajo, sin commit. No inferir que el remoto recibió esos archivos: verificar Git al retomar. No se ha hecho push como parte de estas tareas.

## Supabase: implementado y pendiente

La **base de datos todavía no se ha migrado**. El acceso sigue usando `DATABASE_URL` (SQLite si no se configura otra). No se han creado tablas de aplicación ni políticas RLS en Supabase durante esta integración.

Se configuró localmente el proyecto suministrado por el usuario. La URL y clave pública están en `pmv_fastapi/.env`, ignorado por Git; **no copiar sus valores aquí**. En otro equipo, crear ese archivo desde [.env.example](../pmv_fastapi/.env.example) y obtener la configuración del responsable del proyecto. No hace falta `service_role` para el login.

Implementación relevante:

- [Modelo de sesión](../pmv_fastapi/app/domain/model/autenticacion.py), [puerto de entrada](../pmv_fastapi/app/ports/inbound/sesiones.py), [puerto de identidad](../pmv_fastapi/app/ports/outbound/proveedor_identidad.py) y [servicio](../pmv_fastapi/app/application/servicio_sesion.py).
- [Adaptador Supabase](../pmv_fastapi/app/adapters/outbound/supabase_auth.py) y [adaptador HTTP](../pmv_fastapi/app/adapters/inbound/http/autenticacion.py), compuestos en [main.py](../pmv_fastapi/app/main.py).
- [auth.js](../pmv_fastapi/app/web/auth.js) controla la pantalla, la sesión y el reintento tras un 401; el código clínico usa ese cliente. El service worker excluye la API de su caché.
- Cookies HttpOnly y SameSite=Strict, Secure por defecto; los tokens no se exponen en JSON ni se almacenan en localStorage. `AUTH_COOKIE_SECURE=false` se usa únicamente en HTTP local.
- `AUTH_MODE=supabase` es el valor predeterminado. Sin configuración se bloquea el acceso clínico. `AUTH_MODE=demo` habilita expresamente la demostración sintética anterior. Las pruebas históricas lo configuran explícitamente, incluidos los servidores E2E de alcance de módulo.
- La API verifica al usuario mediante Supabase. `X-Usuario` se ignora en modo autenticado y la auditoría utiliza el UUID. Las mutaciones requieren `X-CSRF-Protection: 1` y rechazan un Origin distinto.
- No hay roles ni aislamiento por establecimiento: todos los usuarios confirmados del proyecto tienen las mismas funciones. Cada petición clínica añade una consulta al proveedor; una caída responde 503.

El usuario difirió estas acciones porque tenía que salir del laboratorio:

1. Desactivar **Allow new users to sign up** en Supabase.
2. Crear la primera cuenta autorizada con correo confirmado desde **Authentication → Users**.
3. Ingresar personalmente en el formulario y verificar acceso, recarga y cierre contra el proyecto real; no enviar contraseñas a una IA ni guardarlas en el repositorio.
4. Registrar el resultado en T-015 antes de cerrarla. Solo después continuar con el diseño de migración, autorización y RLS.

La última consulta real de solo lectura a `/auth/v1/settings` respondió HTTP 200: Email habilitado, confirmación automática deshabilitada y registro público permitido. **Es evidencia del 23/10/2026, no una lectura actual del panel.** No se crearon cuentas ni se probó un login remoto.

## Cómo retomar y verificar

Desde `pmv_fastapi/`, con Python 3.11 o superior y un entorno virtual propio del equipo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
# Crear .env desde .env.example y completar la configuración local antes de iniciar.
.\.venv\Scripts\python.exe -m uvicorn app.main:crear_app --factory --env-file .env --reload --port 8000
```

Abrir `http://127.0.0.1:8000`. Si `.venv` ya existe y es utilizable, conservarlo. El entorno, los navegadores y el `.env` del laboratorio no viajan con Git.

Comprobaciones desde esa misma carpeta:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m scripts.exportar_openapi --verificar
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path (Get-Location) '.venv/browsers'
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m pytest tests/e2e -m e2e -q --no-cov
```

Resultados reproducidos en la sesión T-015 (Windows, Python 3.14.4): **349 pruebas aprobadas, cobertura 99,50 %; 17 E2E aprobadas**; Ruff y contrato OpenAPI conformes. Las 17 E2E incluyen dos escenarios nuevos de login, en escritorio y móvil, con **Supabase simulado**. No presentar estas cifras como ejecución propia de una nueva sesión ni como evidencia de login remoto. Las capturas de S9 son heredadas; las previsualizaciones temporales en `diagramas/_build/` están ignoradas por Git.

## Próximos pasos compartidos

- Activar y validar la primera cuenta (T-015).
- Diseñar la migración de PostgreSQL a Supabase sin perder datos, con autorización por establecimiento y RLS aún pendientes. No cambiar `DATABASE_URL` ni ejecutar migraciones solo por leer este contexto.
- Revisar los cambios locales antes de preparar commits y publicación; la petición actual solo autoriza documentar. Preservar el PDF y fuentes de feria al integrar Auth.
- Mantener las revisiones S9 y los pendientes anteriores del tablero: un login que pasa pruebas no certifica el entregable completo ni aceptación de usuarios.
- Para comunicar dudas, propuestas o un traspaso a otro compañero, usar [intercambios/](intercambios/README.md) y actualizar la tarea canónica cuando corresponda.

## Actualización de integración 30/10/2026

T-017 integra preparación de CI/CD (5f4c255) con origin/main (49f07da). ORQ-008 conserva la solicitud de despliegue que colisionaba con ORQ-004. Guía vigente: pmv_fastapi/docs/DESPLIEGUE.md. El código entrante incluye Auth y requiere sus variables en Render, además de PostgreSQL. Si la base se creó con el esquema anterior, aplicar la migración v2.0 una sola vez y luego 02_supabase.sql actualizado. Commit de merge y publicación pendientes del usuario.
