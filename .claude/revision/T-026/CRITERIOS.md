# T-026 — Criterios de la revisión y decisiones transversales

- **Revisor:** Jean Piero Huamani Rodriguez (rol `revisor-documental`), con Claude como asistente.
- **Fecha:** 15/11/2026 · **Rama:** `docs/t026-revision` (desde `develop` 250fdf5).
- **Encargo:** [`.claude/intercambios/T-026_porras_revision-entregables.md`](../../intercambios/T-026_porras_revision-entregables.md).
- **Forma de trabajo:** `agy` no está instalado en el equipo del revisor; la lectura y el cotejo se delegaron en subagentes `haiku` y las correcciones en subagentes `sonnet`. Claude revisó cada resultado y tomó las decisiones de esta página.

## Escala

- **Cumple / Parcial / No cumple** por requisito `R-xx` (archivos de [`requisitos/`](requisitos/)).
- **Severidad del hallazgo:** alta (afecta un requisito de la guía, una cifra central o datos personales), media (contradicción o error verificable que no cambia la nota), baja (forma, residuos, referencias).
- **Estado del hallazgo:** `Cerrado` (corregido y verificado con captura después), `Pendiente justificado` (necesita decisión del equipo, del docente o del Leader; no cuenta como cumplido) y `Descartado` (no es defecto; se explica por qué).

## Decisiones transversales

| ID | Decisión | Motivo |
| --- | --- | --- |
| D-01 | Las afirmaciones que eran ciertas en la fecha de entrega de cada semana no se actualizan al estado actual del proyecto. | Cada entregable es una instantánea ya calificada (encargo, regla 7). Ejemplo: S2 dice que la CI estaba «planificada» (25/09); el `ci.yml` es posterior. Solo se corrige lo que era falso o contradictorio en su propia fecha. |
| D-02 | Los códigos de estudiante en las carátulas se mantienen. | Las plantillas de las guías piden «códigos» de los integrantes (p. ej., guía S6 §II); no son datos sensibles en un informe académico. Sí se retiran correos personales y datos de terceros. |
| D-03 | Donde la carátula no indica la unidad del sílabo, se añade una línea «Unidad del sílabo: …» sin cambiar nada más. | Implicación del sílabo (`SILABO_RESUMEN.md` §7). Es una adición que no altera el sentido. |
| D-04 | Los exportados son derivados: si el `.md` cambió después de exportar, se regenera el exportado con su script. La versión anterior queda en el historial de Git (se cita el commit). | `exportados/README.md`: «ante cualquier diferencia manda el `.md`». Encargo, paso 6. |
| D-05 | El cuadro PDCA de S13 usa dominios del proceso de gestión de la configuración en lugar de los 12 dominios de la plantilla. | Lo pidió el docente en sus observaciones a S13 (T-025, `informes/2026-11-14_orquestador_T-025.md`). No es hallazgo. |
| D-06 | El dominio 4 del PDCA (revisión por pares) se cierra en el «Paso final» del encargo, con la aprobación de esta misma PR. | Encargo T-026, «Paso final». |
| D-07 | No se modifican `pmv_fastapi/` ni `guias/`. Lo que exija tocarlos queda como pendiente justificado y se consulta al Leader. | Encargo, reglas. Las guías son insumos del docente de solo lectura. |
| D-08 | Si un entregable tiene tabla de control de cambios, cada corrección añade una fila «15/11/2026 · T-026 · H-###». | Encargo, regla 7. |
| D-09 | Las capturas se toman con `capturar.py` (PyMuPDF para PDF; Chrome sin interfaz con Playwright para Markdown y HTML; salida de terminal renderizada para comprobaciones de Git o de archivos). En el equipo del revisor no hay Edge en Linux; el resultado es equivalente. | Encargo, paso 5. |
| D-10 | Las cifras de los entregables se comprueban contra las evidencias del propio repositorio; lo que no se pueda comprobar se marca «no verificable» y no se cambia. | AGENTS.md: no inventar resultados. |

## Herramientas usadas

- Capturas: `capturar.py pdf|md|html|cmd` (copia en [`herramientas/capturar.py`](herramientas/capturar.py)).
- Exportación en Linux: [`herramientas/ejecutar_exportador.py`](herramientas/ejecutar_exportador.py) ejecuta los scripts del repositorio con Google Chrome y fuentes métricamente equivalentes a Arial/Consolas ([`herramientas/fonts-win.conf`](herramientas/fonts-win.conf)).
- Exportador genérico nuevo: `.claude/herramientas/conversion/exportar_md.py` (generaliza `exportar_s9.py`).
- Enlaces: [`herramientas/enlaces.py`](herramientas/enlaces.py) (0 enlaces rotos al iniciar).
