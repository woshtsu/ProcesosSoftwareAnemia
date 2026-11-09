# Instrucciones de trabajo del repositorio

## Antes de trabajar

1. Leer `README.md`, `coordinacion/RUTAS.md`, `coordinacion/PROTOCOLO.md` y `coordinacion/TABLERO.md`.
2. Revisar `git status` y conservar los cambios previos del usuario.
3. Consultar la guía vigente de `guias/` para la semana correspondiente. S5 tiene guía propia; no sustituirla por la consigna del integrador.
4. Identificar la tarea y el rol aplicable. Las definiciones de `.claude/agents/` describen responsabilidades; sus nombres de herramientas y modelos corresponden a Claude y no obligan a usar ese runtime.
5. Leer `.claude/CLAUDE.md`, `.claude/CONTEXTO_ACTUAL.md` y los intercambios de `.claude/intercambios/` relacionados con la tarea. Esta entrada es compartida por las IA de todos los compañeros.

## Forma de trabajo de las IA (ahorro de tokens y continuidad)

1. **Claude orquesta y revisa; el trabajo pesado lo hace Antigravity CLI (`agy`).** Delegar en `agy` la implementación, refactorizaciones, búsquedas amplias, redacción extensa y ejecución de pruebas, en modo no interactivo y con un encargo autocontenido (archivos, criterio de terminado y qué informar):

   ```bash
   agy -p "<encargo autocontenido>" --mode accept-edits --sandbox --settings '{"permissions":{"allow":["command(*)"]}}' --print-timeout 0
   ```

   Sin el `--settings` anterior, `agy -p` no puede pedir permiso para ejecutar comandos (pruebas, ruff) y termina sin hacer nada; `--sandbox` restringe la terminal. El encargo debe prohibir commits y limitar los archivos que se pueden tocar.

   Claude revisa siempre el resultado (diff, pruebas, enlaces) antes de darlo por bueno. Si `agy` no está instalado (`agy --version` falla), responde con error de cuota o se queda sin uso, Claude delega en sus **subagentes con modelos más baratos** (`model: "haiku"` para búsquedas y lecturas, `"sonnet"` para implementación y redacción) y reserva el modelo principal para decisiones de diseño y la revisión final.
2. **Usar subagentes baratos para ahorrar tokens.** Toda tarea de lectura, búsqueda o mecánica se delega a un subagente de modelo inferior; el contexto principal recibe solo la conclusión, no el volcado de archivos.
3. **Consultar el grafo de conocimiento de graphify antes de explorar el código.** Leer `graphify-out/GRAPH_REPORT.md` (nodos centrales, comunidades) y usar `graphify query "<pregunta>"`, `graphify path "A" "B"` o `graphify explain "X"` en lugar de leer carpetas completas. Tras cambios de código, actualizarlo con `graphify update .` (sin coste de LLM). `graphify-out/` no se versiona; quien no lo tenga lo genera con `pip install graphifyy` y `graphify update .`.
4. **Registrar el avance para el siguiente chat.** Mantener [`.claude/AVANCE_SESION.md`](.claude/AVANCE_SESION.md) durante la sesión (no solo al final): tarea y rama, qué se hizo, decisiones, comandos de verificación con su resultado, pendientes y el siguiente paso concreto. Un chat nuevo debe poder continuar leyendo ese archivo, el tablero y el contexto. Al cerrar la tarea, el detalle pasa al informe de `coordinacion/informes/` y el archivo se reinicia dejando el enlace al informe.
5. **Skills disponibles.** Las skills de `.claude/skills/` (proceso de ingeniería de [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)) y las de documentos (docx, pdf, xlsx, pptx) se usan cuando la tarea coincide: por ejemplo, la de Word/PDF para exportar entregables, la de rendimiento para optimizar el despliegue y la de revisión de código antes de un PR.

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

