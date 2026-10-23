# Instrucciones de trabajo del repositorio

## Antes de trabajar

1. Leer `README.md`, `coordinacion/RUTAS.md`, `coordinacion/PROTOCOLO.md` y `coordinacion/TABLERO.md`.
2. Revisar `git status` y conservar los cambios previos del usuario.
3. Consultar la guía vigente de `guias/` para la semana correspondiente. S5 tiene guía propia; no sustituirla por la consigna del integrador.
4. Identificar la tarea y el rol aplicable. Las definiciones de `.claude/agents/` describen responsabilidades; sus nombres de herramientas y modelos corresponden a Claude y no obligan a usar ese runtime.
5. Leer `.claude/CLAUDE.md`, `.claude/CONTEXTO_ACTUAL.md` y los intercambios de `.claude/intercambios/` relacionados con la tarea. Esta entrada es compartida por las IA de todos los compañeros.

## Estructura que se debe conservar

- `coordinacion/RUTAS.md` es el mapa canónico. Registrar nuevas rutas mediante una solicitud ORQ antes de utilizarlas.
- `guias/` son insumos del docente de solo lectura. Conservar los nombres originales aportados por el usuario.
- `entregables/semana-*/` contiene una sola versión vigente en Markdown por entregable, junto con sus anexos y checklists.
- `diagramas/src/`, `diagramas/svg/` y `diagramas/png/` contienen las fuentes y sus derivados. No dar una figura por terminada si solo existe el enlace.
- `anemia_junin/` contiene el PMV, pruebas y evidencias. Respetar su arquitectura hexagonal.
- `exportados/` contiene PDF/DOCX derivados; `archivo/` conserva el histórico. No sobrescribir el histórico ni eliminar material para reorganizarlo.

## Coordinación y verificación

- Trabajar en español. Registrar la tarea, sus pendientes y el informe de salida en `coordinacion/` usando las plantillas existentes.
- Se puede trabajar secuencialmente por roles. No es obligatorio iniciar subagentes para seguir esta estructura.
- Comunicar dependencias entre roles mediante solicitudes y respuestas en archivos, manteniendo el tablero coherente.
- Usar `.claude/intercambios/` para preguntas, propuestas y traspasos entre compañeros y sus IA, según la plantilla y el protocolo. Los estados de tareas, solicitudes formales e informes permanecen en `coordinacion/`; no crear un segundo tablero. La publicación y actualización mediante Git son necesarias para compartir mensajes entre computadoras, con la autorización aplicable.
- Distinguir evidencia reproducida, evidencia heredada, propuestas y pendientes. No inventar resultados, capturas, aprobaciones de integrantes ni aceptación de usuarios.
- El cierre de una sesión de revisión no equivale a cumplimiento total del entregable. Mantener EN REVISIÓN si faltan figuras, evidencias o criterios de aceptación.
- Verificar enlaces relativos y ejecutar las comprobaciones pertinentes al cambio. Para el PMV, consultar `anemia_junin/README.md`.
- No crear commits, tags, publicaciones o pushes por el mero hecho de revisar. Seguir la autorización del usuario para esas acciones.

