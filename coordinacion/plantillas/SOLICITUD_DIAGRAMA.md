# DIAG-### — <Nombre del diagrama>

- **Estado:** ABIERTA  <!-- ABIERTA | EN CURSO | RESUELTA | RECHAZADA -->
- **Solicitante:** <agente>
- **Destino:** diagramador
- **Tarea relacionada:** T-###
- **Fecha de apertura:** AAAA-MM-DD
- **Prioridad:** Alta | Media | Baja

## Tipo de diagrama

<!-- Marcar uno -->
- [ ] BPMN / flujo de proceso (AS-IS / TO-BE, carriles)
- [ ] UML casos de uso
- [ ] UML clases / modelo de dominio
- [ ] UML secuencia
- [ ] UML actividad
- [ ] UML componentes / despliegue
- [ ] C4 (contexto / contenedores / componentes)
- [ ] Modelo de datos (ER)
- [ ] Gantt / cronograma / WBS
- [ ] Otro: ____

## Requisito que cubre

- **Guía:** `guias/...` — sección / actividad: ...
- **Entregable destino:** `entregables/semana-XX/....md` — sección: ...

## Contenido requerido

<Elementos, actores, pasos, relaciones que DEBEN aparecer. Ser exhaustivo; el diagramador no inventa contenido de dominio.>

## Fuentes de verdad

- `<ruta del documento/código de donde sale el contenido>`

## Nombre de archivo sugerido

`NN_nombre_descriptivo` → se producirán:
- `diagramas/src/NN_nombre_descriptivo.puml` (o `.py`)
- `diagramas/png/NN_nombre_descriptivo.png`
- `diagramas/svg/NN_nombre_descriptivo.svg`

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4
- [ ] Texto en español, sin tildes rotas
- [ ] Coherente con el texto del entregable y con el código (si aplica)
- [ ] <otros>

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** AAAA-MM-DD
- **Resultado:** RESUELTA | RECHAZADA
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura N. <leyenda>](../../diagramas/svg/NN_nombre.svg)`
- **Notas:**
