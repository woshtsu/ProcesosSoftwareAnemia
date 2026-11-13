# Informe de salida — revisor-documental — T-018

- **Agente:** roles ejecutados secuencialmente (revisor-documental con apoyo de desarrollador para las comprobaciones)
- **Fecha:** 2026-10-30
- **Tareas / solicitudes atendidas:** T-018, ORQ-009
- **Estado final:** EN REVISIÓN

## Resumen

Se elaboró el informe técnico de la Semana 11 (evaluación CMMI-DEV del proceso y del producto) con las cinco actividades de la guía: selección de seis áreas de práctica, diagnóstico de capacidad (Nivel 1: ESTIM, PQA y VAL; Nivel 2: PLAN, CM y VER), auditoría de productos de trabajo, fichas de VER y VAL de los nueve RF con capturas, y análisis de causa raíz con plan de mejora.

## Archivos creados / modificados

| Acción | Ruta | Nota |
| --- | --- | --- |
| creado | `entregables/semana-11/Entregable_Semana11_Anemia_Junin.md` | Entregable vigente |
| creado | `coordinacion/solicitudes/ORQ-009.md` | Alta de la ruta |
| creado | `coordinacion/informes/2026-10-30_revisor-documental_T-018.md` | Este informe |
| modificado | `coordinacion/RUTAS.md`, `coordinacion/TABLERO.md` | Registro de ruta y tarea |

## Verificación realizada

- `git pull`: repositorio al día; estado inicial limpio salvo la guía S11 aportada por el usuario.
- Reproducido el 2026-10-30 en `pmv_fastapi/` (Python 3.14.6, entorno virtual fuera del repositorio): `ruff check` y `ruff format --check` sin hallazgos (103 archivos); `pytest --cov=app`: 349 aprobadas, cobertura 99,50 %; `exportar_openapi --verificar`: al día.
- Producción: `GET https://softwareanemia.onrender.com/api/salud` respondió HTTP 200.
- Los 18 enlaces e imágenes del entregable existen.

## No verificado

- Pruebas E2E (17): no reejecutadas; cifra heredada de T-015 y S9.
- Historial de GitHub Actions, tablero de GitHub Projects, aprobaciones de *pull requests* y estado en el panel de Render.
- Construcción de la imagen Docker (el daemon no estaba activo).
- SonarCloud: sin organización ni reporte.

## Pendientes

- Confirmar con el equipo responsables y fechas del plan de mejora (propuestos).
- Aceptación del usuario, SUS y firma de QA (no existen).
- Sin SonarQube/SonarCloud (organización sin definir), sin build de Docker y sin evidencia de GitHub Projects: siguen como pendientes declarados en el entregable.
- La guía pide solo PDF; DOCX no se generó (pandoc no instalado).
- Sin commits ni pushes.

## Revisión posterior (2026-10-30)

Tres revisores de solo lectura con el modelo Opus (documentaria, técnica y del PDF); la revisión técnica se pensó para Fable 5.1, que no estuvo disponible (requiere créditos), y se ejecutó con Opus. Se corrigieron en el Markdown fuente: contradicción sobre las E2E, referencias internas, fichas autocontenidas, cinco porqués (Tabla 11), estados del plan, CM/CI/PR, RF-02, `supabase_auth.py` y referencias. Se corrigió el script (leyendas de figura, numeración de página, capturas verticales, paginación, cortes en código) y se regeneró el PDF: 27 páginas, 18 leyendas, 352 fragmentos del Markdown encontrados en el PDF. Reportes exportados en `entregables/semana-11/anexos/`.
