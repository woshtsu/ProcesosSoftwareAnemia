# Informe de salida — orquestador — T-010

- **Agente:** Codex, rol de orquestación y revisión
- **Fecha:** 2026-09-25 (America/Lima)
- **Tareas / solicitudes:** T-010, ORQ-001; nueva DEV-101
- **Estado final:** HECHO (revisión; no cierre de todos los entregables)
- **Base:** HEAD `67f2c01`, avance `b6c6db2`, reestructura `a441346`, más las guías reemplazadas por el usuario.

## Resumen

El avance técnico es sustancial y sus resultados principales se reprodujeron: 242 pruebas aprobadas, 96,66 % de cobertura y Ruff sin hallazgos. La coordinación quedó desactualizada respecto al código. El conjunto documental aún no está listo para entregar: faltan doce figuras SVG enlazadas, el Markdown de S5, la conciliación del integrador y las exportaciones/presentación finales. No hay base para certificar un porcentaje global del 90 %.

## Hallazgos priorizados

| Prioridad | Hallazgo y evidencia | Acción / tarea |
| --- | --- | --- |
| Alta | S1 enlaza 5 SVG inexistentes (10–14); S2 enlaza 15; S3–4 enlaza 30–35. Hay PNG y fuentes 10–12, pero eso no resuelve los enlaces SVG. | Completar DIAG-001..006 y DIAG-100..105; T-007. |
| Alta | El entregable vigente S5 en Markdown no existe. El PDF y su extracción describen unittest, 49 pruebas, herramientas `tools/` y una implementación sin frameworks; el código actual usa Flask, pytest y `scripts/`. | Crear S5 según su guía propia y evidencias actuales; T-005. |
| Alta | El resumen y la sección de pruebas del integrador conservan resultados de Actividad 5 (49 pruebas y 95,8 %) y pendientes técnicos ya parcialmente atendidos. | Conciliar S6 completo con código, evidencias y S1–S5; T-006. No sustituir números sin revisar sus tablas y contexto. |
| Alta | Entradas numéricas especiales provocan HTTP 500 en lugar de validación 400. Reproducido fuera de la suite. | DEV-101, con regresiones antes de liberar. |
| Media | El tablero decía que no había README, E2E ni carga, y marcaba INV-001 abierta aunque la solicitud está resuelta. T-002..004 figuraban HECHO con figuras pendientes. | Sincronizado en esta revisión; T-008 queda EN REVISIÓN hasta su cierre documental. |
| Media | Las nuevas guías rompían cinco enlaces del README y el mapa decía que S5 no tenía guía. | Corregidos README, RUTAS y entradas del tablero. |
| Media | No se encontraron exportaciones finales en `exportados/`, presentación de exactamente 7 diapositivas ni tag local `v1.0-PMV`. Portada del integrador conserva campos por completar. | T-006/T-009; preparar contenido antes de exportar. La ausencia de tag es local, no se consultó el remoto. |

## Guías actualizadas

Se compararon las copias actuales con `git show HEAD:guias/<ruta_anterior>`:

- **S1, S2 y S3–4:** contenido idéntico; cambió el nombre. No es necesario repetir sus revisiones solo por la descarga. Sí deben cerrarse las brechas que ya tenían.
- **S5:** incorporación nueva. Exige 3–5 historias esenciales, matrices 1.1 (alcance y Given-When-Then), 2.1 (diseño y DoD), 3.1 (construcción y ramas), 4.1 (pruebas y resultados) y 5.1 (valor operativo). También pide paquetes/despliegue hexagonal, datos, evidencia y demostración funcional. Estos requisitos deben gobernar T-005.
- **S6:** la copia Markdown no es textualmente idéntica a la extracción anterior. Se leyó su estructura y se conserva como fuente actual; no se atribuye toda diferencia de extracción a cambios de requisitos. Exige informe, presentación de exactamente 7 diapositivas y enlace al repositorio/tag. La consigna contiene una inconsistencia: anuncia 7 minutos, pero los tiempos individuales de las siete diapositivas suman 10; ajustar el guion al límite general o aclararlo con el docente antes de la defensa.

Las guías del usuario se conservaron sin renombrarlas ni editar su contenido. Las eliminaciones de archivos anteriores ya estaban presentes al empezar.

## Verificación realizada

Desde `anemia_junin/`, con el entorno virtual existente y **Python 3.13.7**:

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --cov --cov-report=term-missing -q
.\.venv\Scripts\python.exe -m ruff check . --no-cache
```

Resultado: **242 passed in 11.93s**, 1348 sentencias, 45 sin cubrir, **96,66 %**. Ruff: **All checks passed!** Se instaló PyYAML, dependencia ya declarada que faltaba en este entorno; jsonschema ya estaba instalada. No se cambiaron dependencias del proyecto.

Los primeros intentos dentro del aislamiento fallaron por permisos de carpetas temporales/cachés. La ejecución completa fuera de ese aislamiento terminó correctamente; esos errores de preparación no se atribuyen al programa.

La suite incluye E2E HTTP con servidor real y smoke test, pero no interacción con navegador. La prueba de carga guardada por Claude (20 usuarios/60 s) **no se reejecutó**. Tampoco se certificó visualmente cada figura ni se hizo una auditoría clínica de tablas normativas. Las bandas de altitud sin verificar permanecen como limitación explícita del PMV.

Comprobación de enlaces Markdown en README y entregables: antes de esta revisión, 5 enlaces a guías rotos y 12 imágenes SVG ausentes. Se corrigieron los enlaces a guías; las figuras quedan asignadas a T-007.

## Archivos creados / modificados

| Acción | Ruta | Propósito |
| --- | --- | --- |
| Modificado | `README.md` | Guías actuales, estado real e instrucciones de ejecución. |
| Modificado | `coordinacion/RUTAS.md` | Guía S5, nombres actuales y entrada de continuidad. |
| Modificado | `coordinacion/TABLERO.md` | Estados verificados, T-010 y seguimiento de hallazgos. |
| Creado | `AGENTS.md` | Instrucciones persistentes para respetar esta estructura. |
| Creado | `coordinacion/solicitudes/ORQ-001.md` | Alta de la ruta de instrucciones. |
| Creado | `coordinacion/solicitudes/DEV-101.md` | Defecto reproducible y criterios de corrección. |
| Creado | Este informe | Evidencia, límites y orden de continuación. |

## Orden de continuación

1. Resolver DEV-101 y responder los 11 puntos de DEV-100 con su estado real; cerrar informe de T-008.
2. Completar y revisar las figuras pendientes de T-007. Cerrar los checklists de S1–S3/4 al disponer de los artefactos.
3. Redactar S5 con la nueva guía, resultados reproducidos y distinción entre validación técnica y aceptación humana.
4. Conciliar el integrador, completar datos académicos y preparar las 7 diapositivas. No inventar validación del usuario ni impacto clínico.
5. Exportar y revisar visualmente PDF/DOCX; preparar el tag de entrega cuando corresponda.

No se modificó el código ni los entregables sustantivos durante esta revisión. No se crearon commits, tags ni pushes. Las definiciones de `.claude/agents/` se conservan y el trabajo futuro utiliza la misma estructura.
