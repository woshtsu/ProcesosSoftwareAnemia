# Informe T-023 — Cierre de la entrega de la semana 13

- **Responsable humano:** Huamani Rodriguez, Jean Piero (Process Analyst & QA Lead) · **Rol:** documentador y revisor
- **Rama / commit base:** `main` / `c41ae8d` · **Fecha:** 13/11/2026 · **Estado:** EN REVISIÓN
- **Entrega:** «S13. Entrega de informe y video — actualizado y corregido de Unidad III» (cierre 13/11/2026), PDCA y laboratorio 13 (gestión de la configuración)

## Resumen

Se corrigieron las tres observaciones del docente a la entrega de la semana 12 y se produjeron los otros dos entregables de la semana 13: el cuadro PDCA y el informe técnico del laboratorio de gestión de la configuración. El repositorio quedó con plantillas de cambio, convención de ramas y commits, rama `develop`, cinco *releases* y seis solicitudes de cambio (RFC). Los PDF y DOCX listos para el aula virtual están en `exportados/semana-13/`.

## Cambios

### 1. Informe integrador corregido (`entregables/semana-13/`)

| Observación del docente (S12) | Corrección | Dónde se verifica |
| --- | --- | --- |
| Citado numérico según ISO 690 | Citas `[n]` por orden de primera aparición ([1] a [21]); lista y cotejo en ISO 690 | Referencias y Anexo D |
| GQM con evidencias incompletas y la estructura de GitHub primero | Ficha por métrica (M1.1 a M3.2, V4 y V5) con fórmula, datos y dos capturas (medición y software en uso); GitHub pasa a 3.6.4 | 3.6.1 a 3.6.4 |
| CMMI sin evidencias de cronograma, diseño y pruebas | Ficha de evidencia por área (ESTIM, PLAN, TS, VER, VAL, CM, PQA) | 3.8 |

Además:

- Tabla de control de cambios al inicio, con las tres observaciones y las actualizaciones del equipo.
- Lecturas de la semana 13 en el marco teórico (2.5): revisión, verificación y validación [20], y ciclo PHVA [21].
- Diagramas de componentes y de datos regenerados del código de `v4.0-Inc4` por ingeniería inversa: `entregables/semana-13/ingenieria_inversa/generar_diagramas.py` (SQLAlchemy y `ast`). Hallazgo H10 mitigado.
- Captura de los *releases* en la ficha CM.
- Seguimiento PHVA del plan de mejora al 06/11/2026.
- Fila del INC-5 en la matriz de desviaciones y avance a la semana 13: la semana abre el Sprint 6 (INC-5, hito H5 el 23/11).
- Video regrabado sobre producción el 09/11 (Anexo A) y producción en Render Virginia, verificada el 12/11 con `4.0.0-inc4` y 29 rutas (Anexo B).
- Word con índice numerado (168 páginas) y PDF.

### 2. Cuadro PDCA (`entregables/semana-13/pdca/`)

- `Porras-Auqui-Huamani-PDCA-mejora.pdf` (fuente `PDCA_mejora.html`): diagnóstico del avance al inicio de la semana 13, los 12 dominios con hallazgo, acción, responsable, fechas, verificación, estandarización y estado, más el registro de seguimiento.
- Estado al 12/11/2026: 5 dominios verificados, 5 en proceso y 2 abiertos (UAT y póster).
- `PLANTILLA_ACTA_RETROALIMENTACION.md`: formato único de acta con usuarios.

### 3. Laboratorio 13: gestión de la configuración

- `entregables/semana-13/laboratorio-scm/Porras-Auqui-Huamani-Informe-SCM-Lab13.pdf`, con las secciones 1 a 7 de la guía.
- Matrices: RFC, auditoría de las PR #1 a #13, ramas por historia, *releases* y trazabilidad unificada.
- En el repositorio:
  - `.github/ISSUE_TEMPLATE/change_request.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `CONTRIBUTING.md` (GitFlow, commits, etiquetas) y README actualizado.
  - Rama `develop`.
  - Etiquetas `change-request`, `pendiente-evaluacion`, `aprobado`, `rechazado` e `implementado`.
  - RFC #14, #15 y #17 a #20; la #16 se cerró como duplicado de la #15.
  - *Releases* de `v1.0-PMV`, `v1.5.0-inc2-avance` (*pre-release*), `v2.0-Inc2`, `v3.0-Inc3` y `v4.0-Inc4`, con notas.

### 4. Corrección de una prueba E2E (PR #21)

`pmv_fastapi/tests/e2e/test_inc3_sin_conexion.py` (CP-303) reemplazaba la fecha del servidor por la del *runner* en UTC. Entre las 19:00 y las 24:00 de Lima eso enviaba una fecha futura y el servidor respondía 422. Se quitó la línea y la prueba usa la fecha del servidor.

### 5. Exportados (`exportados/semana-13/`)

| Archivo | Origen |
| --- | --- |
| `Informe_Integrador_S13_Anemia_Junin.docx` | Informe S13, imágenes comprimidas para el aula virtual (7,9 MB; el de `entregables/` pesa 12,5 MB) |
| `Informe_Integrador_S13_Anemia_Junin.pdf` | Ídem (7,1 MB; el de `entregables/` pesa 15 MB) |
| `Porras-Auqui-Huamani-PDCA-mejora.pdf` | Copia de `entregables/semana-13/pdca/` |
| `Porras-Auqui-Huamani-Informe-SCM-Lab13.pdf` | Copia de `entregables/semana-13/laboratorio-scm/` |

## Pull requests

| PR | Contenido | CI | Integración |
| --- | --- | --- | --- |
| #13 | Informe S12 v2, informe S13, plantillas SCM, PDCA y laboratorio | Pruebas e imagen en verde; Quality Gate de SonarCloud en rojo | `squash` por woshtsu, 06/11 (`e0f8760`) |
| #21 | Portada del informe SCM (SonarCloud) y corrección de CP-303 | Todo en verde | `squash` por woshtsu, 13/11 (`3c60dba`) |
| #26 | Informe S13 final en Word y PDF, video y producción en Virginia | Todo en verde | `squash` por woshtsu, 13/11 (`c41ae8d`) |

Ninguna de las tres tiene una revisión «Approve» registrada en GitHub, aunque las integró el propietario.

## Verificación

- Validador de OOXML sin errores en el Word.
- Render del PDF revisado página por página en las secciones nuevas.
- Citas en orden de primera aparición (1 a 21) verificadas con un script.
- Figuras (120) y tablas (46) renumeradas sin referencias rotas; las referencias externas a otros entregables se conservan.
- Pruebas re-ejecutadas el 06/11/2026: 660 aprobadas, cobertura 99,79 %, 28 E2E y Ruff sin observaciones.
- CI de las PR #21 y #26 en verde (`calidad-y-pruebas`, `imagen`, SonarCloud).
- Producción: `GET /api/salud` `ok` y `/openapi.json` `4.0.0-inc4` con 29 rutas (12/11/2026).

## Pendientes

1. **Entrega en el aula virtual (13/11):** la hace el equipo con los archivos de `exportados/semana-13/` y el enlace del video del Anexo A.
2. **Leader (Porras V.):**
   - Pasar las RFC #14, #15 y #17 a `aprobado` / `implementado` y evaluar las #18 a #20.
   - Activar la protección de `main` y `develop` (Settings → Branches), que solo puede hacer el propietario.
3. **Adjuntos de los *releases*:** los paquetes de despliegue y el contrato OpenAPI de cada versión están preparados fuera del repositorio. Hay que subirlos a mano en «Edit release → Attach binaries» (criterio 3 de la rúbrica del laboratorio).
4. **Video:** falta la locución y subirlo a Drive (T-022).
5. **PDCA abiertos:** UAT con acta firmada (dominios 7 y 11) y rediseño del póster (dominio 9).
6. **SonarCloud en `main`:** quedó en rojo con la PR #24 (archivos de `.claude/`); conviene revisarlo.
