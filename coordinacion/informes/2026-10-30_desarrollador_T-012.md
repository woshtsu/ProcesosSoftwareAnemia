# Informe de salida — desarrollador / orquestador — T-012

- **Agente:** roles ejecutados secuencialmente
- **Fecha:** 2026-10-30
- **Tareas / solicitudes atendidas:** T-012, ORQ-004
- **Estado final:** PARCIAL; tablero EN REVISIÓN

## Resumen

Se trasladó el workflow a la raíz y se adaptaron rutas de ejecución, caché, reportes y Sonar al monorepositorio. CI conserva PostgreSQL efímero y construye Docker también en PR. Solo main, tras los jobs aprobados, comprueba en modo lectura el esquema Supabase y solicita a Render desplegar el SHA probado. Se documentaron secrets, configuración de runtime y puesta en marcha.

## Archivos creados / modificados / movidos

| Acción | Ruta | Nota |
| --- | --- | --- |
| movido/modificado | `.github/workflows/ci.yml` | Desde `pmv_fastapi/.github/workflows/ci.yml` |
| creado | `pmv_fastapi/db/02_supabase.sql` | RLS y revocación de grants de Data API |
| creado | `pmv_fastapi/docs/DESPLIEGUE.md` | SQL inicial, prompt opcional y pasos Render/GitHub |
| modificado | `pmv_fastapi/README.md` | Enlace de producción |
| creado/modificado | `coordinacion/solicitudes/ORQ-004.md`, `coordinacion/RUTAS.md`, `coordinacion/TABLERO.md` | Registro de estructura y pendientes |

## Verificación realizada

- Estado inicial git limpio; sin commits ni pushes realizados.
- `git diff --check`: aprobado.
- Parseo YAML con PyYAML BaseLoader y AST Python del script inline: aprobado.
- Verificación de enlaces locales de DESPLIEGUE.md: cero faltantes.
- `python -m venv pmv_fastapi/.venv`: ensurepip falló; entorno parcial ignorado por git.
- Instalación con `python -m pip --python ... install -r ...`: falló por resolución DNS (getaddrinfo). No se ejecutaron pytest/Ruff/E2E.
- `docker info`: daemon Docker Desktop Linux no disponible. No se construyó imagen ni se ejecutó PostgreSQL local.
- No se ejecutó SQL remoto ni se contactó un deploy hook. No hay credenciales en archivos.

## Pendientes y riesgos

- Usuario: ejecutar SQL, configurar secrets y Render; publicar cambios mediante su flujo habitual y ejecutar Actions.
- Verificar Live y SHA en Render: aceptar un hook no prueba que el despliegue terminó.
- Aplicación pública sin autenticación: limitar esta demostración a datos sintéticos. RLS no añade autenticación a FastAPI.
- Confirmar disponibilidad de dependencias fijadas y resultados completos en GitHub; pendientes por limitaciones locales, no reportados como aprobados.
- Mantener DATABASE_URL de Render igual a SUPABASE_DATABASE_URL de Actions; no se sincronizan automáticamente.

## Solicitudes abiertas a otros agentes

Ninguna adicional. ORQ-004 resuelta; configuración y evidencias remotas pendientes en T-012.
