## Forma de trabajo obligatoria (se carga en cada sesión)

Antes de actuar, leer `AGENTS.md` (sección «Forma de trabajo de las IA») y `.claude/AVANCE_SESION.md`.

- **Claude orquesta y revisa; `agy` (Antigravity CLI) hace el trabajo pesado.** Toda implementación, refactorización, adaptación de scripts, redacción extensa o búsqueda amplia se delega a `agy` con un encargo autocontenido (archivos, criterio de terminado, prohibido hacer commits):

  ```bash
  agy -p "<encargo>" --mode accept-edits --sandbox --settings '{"permissions":{"allow":["command(*)"]}}' --print-timeout 0
  ```

- Claude **siempre revisa** lo que entrega `agy` (diff, pruebas, mediciones) antes de darlo por bueno.
- Si `agy` no está instalado, falla o se quedó sin cuota, delegar en subagentes baratos (`haiku` para leer y buscar, `sonnet` para implementar) y decirlo.
- **Si Claude hace una tarea directamente, debe indicar en su respuesta por qué no la delegó** (p. ej., cambio de una línea, tarea interactiva con el usuario, `agy` no disponible).
- Registrar el avance en `.claude/AVANCE_SESION.md` durante la sesión.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
