# Producción de main: GitHub Actions, Render y Supabase

Configuración preparada el 2026-10-30; pendiente ejecución remota. Tras integrar origin/main (49f07da), la versión 2.0 incorpora Supabase Auth. Configurar sus variables en Render y crear la primera cuenta según el README del PMV. Utilizar datos sintéticos en la demostración.

Si ya ejecutaste el SQL de la versión anterior (antes de este pull), ejecutar una sola vez `db/02_migracion_v2_0.sql` y después volver a ejecutar `db/02_supabase.sql`. No basta volver a ejecutar CREATE TABLE IF NOT EXISTS: no actualiza columnas. Para un proyecto vacío siguen aplicando los pasos siguientes con el SQL actualizado.

### Versión 3.0 (sin conexión, sincronización y visitas): qué SQL ejecutar

La versión 3.0.0-inc3 agrega tres tablas (`visita_domiciliaria`, `operacion_sincronizada` y `conflicto_sincronizacion`); no cambia ni elimina columnas de las tablas existentes.

- **Proyecto vacío (nuevo):** ejecutar `db/01_esquema_postgresql.sql` y después `db/02_supabase.sql`, como en el paso 1. El esquema 3.0 ya incluye las tablas nuevas; **no** hay que ejecutar las migraciones.
- **Base que ya está en 2.0** (esquema 2.0 con Supabase ya configurado): ejecutar una sola vez `db/03_migracion_v3_0.sql` y después volver a ejecutar `db/02_supabase.sql`, que activa RLS y revoca el acceso de `anon` y `authenticated` sobre las tablas nuevas. La migración usa `IF NOT EXISTS`, está en una transacción y puede repetirse sin efecto.
- **Base que todavía está en 1.x:** ejecutar primero `db/02_migracion_v2_0.sql`, luego `db/03_migracion_v3_0.sql` y por último `db/02_supabase.sql`.
- **SQLite de desarrollo:** `crear_esquema()` crea las tablas nuevas al arrancar; no requiere migración.

Comprobación posterior: `select to_regclass('public.visita_domiciliaria'), to_regclass('public.operacion_sincronizada'), to_regclass('public.conflicto_sincronizacion');` debe devolver los tres nombres.

Después de desplegar, cada dispositivo instala el nuevo service worker al abrir la aplicación con conexión (actualiza solo, `skipWaiting`); la cola de registros sin conexión vive en el navegador de cada equipo y se envía sola al reconectar.

## 1. Inicializar Supabase

En el proyecto vacío, abrir **SQL Editor → New query**. Allí se ejecuta SQL:

1. Copiar y ejecutar [01_esquema_postgresql.sql](../db/01_esquema_postgresql.sql). Crea tablas, índices y vista sin insertar datos.
2. Copiar y ejecutar [02_supabase.sql](../db/02_supabase.sql). Activa RLS y revoca acceso de los roles públicos de Data API; permite seguir usando la conexión PostgreSQL de servidor.
3. Ejecutar esta consulta: los tres resultados deben tener nombre, no NULL.

```sql
select to_regclass('public.nino'),
       to_regclass('public.evaluacion_hemoglobina'),
       to_regclass('public.v_ultimo_control');
```

Los scripts inicializan el proyecto vacío; IF NOT EXISTS no migra estructuras antiguas.

Prompt opcional para el asistente de Supabase (adjuntar ambos SQL):

> Revisa estos dos scripts para inicializar mi proyecto vacío. Mi backend usa FastAPI, SQLAlchemy y psycopg2 con conexión PostgreSQL. Conserva nombres, tipos y restricciones exactamente como están. Primero aplica el esquema y luego las restricciones de Data API. No crees datos ni políticas públicas ni expongas credenciales. Verifica public.nino, public.evaluacion_hemoglobina y public.v_ultimo_control. La conexión del backend se configurará en Render, no en SQL Editor.

## 2. Obtener la conexión

Abrir **Connect → Session pooler**, puerto 5432, compatible con IPv4. Copiar host y usuario exactos del panel. Usar la contraseña de base de datos, no una API key. Cambiar el prefijo para SQLAlchemy y añadir SSL:

```text
postgresql+psycopg2://postgres.PROJECT_REF:CONTRASENA_CODIFICADA@HOST_DEL_POOLER:5432/postgres?sslmode=require
```

Codificar caracteres especiales de la contraseña como componente URL (`@` → `%40`, `#` → `%23`, `%` → `%25`). No guardar la cadena en git. DATABASE_URL es para PostgreSQL; SUPABASE_URL y SUPABASE_PUBLISHABLE_KEY son variables adicionales para el login incorporado en el pull. No usar service role key.

## 3. Configurar GitHub

**Settings → Secrets and variables → Actions → Secrets → New repository secret**:

| Secret | Valor |
| --- | --- |
| `SUPABASE_DATABASE_URL` | Cadena PostgreSQL completa anterior |
| `RENDER_DEPLOY_HOOK_URL` | URL completa del Deploy Hook de Render (se obtiene al crear el servicio) |
| `SONAR_TOKEN` (opcional) | Token del proyecto Sonar configurado en sonar-project.properties |

Guardar credenciales en Secrets, no Variables. Los secrets de GitHub **no se transfieren a Render**: allí también hay que configurar DATABASE_URL con la misma cadena.

El [workflow](../../.github/workflows/ci.yml) ejecuta Ruff, pruebas SQLite/PostgreSQL temporal, OpenAPI, E2E y construcción Docker. Las pruebas hacen TRUNCATE: nunca poner producción en TEST_DATABASE_URL. El job de producción únicamente lee el esquema de Supabase y solicita el despliegue del SHA probado; no ejecuta pruebas ni migraciones allí.

## 4. Crear el servicio en Render

1. Iniciar sesión y conectar GitHub con acceso al repositorio.
2. Elegir **New → Web Service** y seleccionar el repositorio.
3. Completar los campos siguientes:

| Campo | Valor |
| --- | --- |
| Name | `anemia-junin` o un nombre disponible |
| Branch | `main` |
| Language / Runtime | `Docker` |
| Root Directory | `pmv_fastapi` |
| Dockerfile Path | `./Dockerfile` |
| Docker Build Context | `.` (si aparece) |
| Docker Command | Vacío; usa CMD del Dockerfile |
| Health Check Path | `/api/salud` |
| Environment | `DATABASE_URL` = cadena PostgreSQL completa |
| Environment | `PORT` = `8000` |
| Environment | `AUTH_MODE` = `supabase` |
| Environment | `SUPABASE_URL` = URL HTTPS del proyecto |
| Environment | `SUPABASE_PUBLISHABLE_KEY` = clave publicable del proyecto |
| Environment | `AUTH_COOKIE_SECURE` = `true` |
| Auto-Deploy | `Off`; el workflow disparará el hook |

Las rutas Docker son relativas al Root Directory. Elegir región cercana a Supabase y plan según presupuesto. Free se suspende tras 15 minutos sin tráfico y puede tardar aproximadamente un minuto en despertar.

4. Crear el servicio. Render puede iniciar un primer despliegue de aprovisionamiento automáticamente: ese arranque no certifica el CI. Si Auto-Deploy no apareció al crear, cambiarlo a Off en Settings.
5. En **Settings → Deploy Hook**, copiar la URL completa al secret RENDER_DEPLOY_HOOK_URL de GitHub.
6. Cuando los cambios estén publicados en main, ir a **Actions → CI y producción — PMV Anemia Junín → Run workflow → main**. Los siguientes pushes a main ejecutan todo automáticamente. Los PR ejecutan CI sin desplegar.
7. Comprobar jobs aprobados y Render **Live**, con el mismo SHA. El hook es asíncrono: el job verde significa solicitud aceptada, no despliegue terminado.
8. Abrir la URL del servicio, `/api/salud` y `/docs`. Registrar un niño sintético y comprobar persistencia después de un redeploy.

No hace falta Static Site, Private Service ni otra base en Render: FastAPI sirve página y API juntas. Se recomienda proteger main con PR y checks requeridos `calidad-y-pruebas` e `imagen`.

## Diagnóstico y mantenimiento

- Conexión fallida: revisar usuario completo del pooler, contraseña codificada, SSL y restricciones de red.
- Tabla/vista ausente: ejecutar los dos SQL en el proyecto correcto.
- Deploy aceptado pero fallido: revisar Events/logs y DATABASE_URL de Render.
- Workflow no aparece: debe estar publicado en `.github/workflows/ci.yml` en la raíz.
- Cambios futuros de esquema: preparar migraciones; crear tablas al iniciar no actualiza columnas existentes.

## Fuentes oficiales

- [Conexiones Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [RLS y permisos](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Docker en Render](https://render.com/docs/docker)
- [Rutas relativas de monorepositorios](https://render.com/docs/monorepo-support)
- [Deploy hooks y commits específicos](https://render.com/docs/deploy-hooks)
- [Plan gratuito Render](https://render.com/docs/free)
