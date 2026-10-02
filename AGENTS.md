# Instrucciones de trabajo del repositorio

## Antes de trabajar

1. Leer `README.md`, `coordinacion/RUTAS.md`, `coordinacion/PROTOCOLO.md` y `coordinacion/TABLERO.md`. Para el cierre S6, leer además `coordinacion/s6/PROTOCOLO_S6.md`, `coordinacion/s6/TABLERO_S6.md`, `coordinacion/s6/REQUISITOS_S6.md` y `coordinacion/s6/DATOS_PMV_FASTAPI.md`.
2. Revisar `git status` y conservar los cambios previos del usuario.
3. Consultar la guía vigente de `guias/` para la semana correspondiente. S5 tiene guía propia; no sustituirla por la consigna del integrador.
4. Identificar la tarea y el rol aplicable. Las definiciones de `.claude/agents/` describen responsabilidades; sus nombres de herramientas y modelos corresponden a Claude y no obligan a usar ese runtime.

## Estructura que se debe conservar

- `coordinacion/RUTAS.md` es el mapa canónico. Registrar nuevas rutas mediante una solicitud ORQ antes de utilizarlas.
- `guias/` son insumos del docente de solo lectura. Conservar los nombres originales aportados por el usuario.
- `entregables/semana-*/` contiene una sola versión vigente en Markdown por entregable, junto con sus anexos y checklists.
- `diagramas/src/`, `diagramas/svg/` y `diagramas/png/` contienen las fuentes y sus derivados. No dar una figura por terminada si solo existe el enlace.
- `pmv_fastapi/` es el **PMV oficial** (FastAPI + PostgreSQL, tag `v1.0-PMV`) con sus pruebas, evidencias, ADR y README de despliegue. Respetar su arquitectura hexagonal.
- `anemia_junin/` es el **antecedente** (prototipo Flask del Incremento 1). Es de solo lectura y sus cifras no se presentan como resultados del PMV.
- `exportados/` contiene PDF/DOCX derivados; `archivo/` conserva el histórico. No sobrescribir el histórico ni eliminar material para reorganizarlo.

## Coordinación y verificación

- Trabajar en español. Registrar la tarea, sus pendientes y el informe de salida en `coordinacion/` usando las plantillas existentes.
- Se puede trabajar secuencialmente por roles. No es obligatorio iniciar subagentes para seguir esta estructura.
- Comunicar dependencias entre roles mediante solicitudes y respuestas en archivos, manteniendo el tablero coherente.
- Distinguir evidencia reproducida, evidencia heredada, propuestas y pendientes. No inventar resultados, capturas, aprobaciones de integrantes ni aceptación de usuarios.
- El cierre de una sesión de revisión no equivale a cumplimiento total del entregable. Mantener EN REVISIÓN si faltan figuras, evidencias o criterios de aceptación.
- Verificar enlaces relativos y ejecutar las comprobaciones pertinentes al cambio. Para el PMV, consultar `pmv_fastapi/README.md`.
- No crear commits, tags, publicaciones o pushes por el mero hecho de revisar. Seguir la autorización del usuario para esas acciones.

