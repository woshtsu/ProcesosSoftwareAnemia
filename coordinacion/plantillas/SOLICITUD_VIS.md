# VIS-### — <Nombre del recurso>

- **Estado:** ABIERTA   <!-- ABIERTA | EN CURSO | RESUELTA | RECHAZADA -->
- **Solicitante:** <agente>
- **Destino:** recursos-visuales
- **Tarea S6:** S6-##
- **Fecha:** AAAA-MM-DD
- **Prioridad:** Alta | Media | Baja
- **Uso:** Informe §x.y (Figura N) · Diapositiva N · Ambos
- **Requisitos que cubre:** R-xx, R-yy

## Tipo

- [ ] Diagrama (PlantUML)
- [ ] Gráfico de datos (matplotlib)
- [ ] Composición de imágenes

## Reutilizar / partir de

- <rutas existentes que revisar o adaptar>

## Contenido requerido (exhaustivo; no inventar)

- ...

## Datos / fuentes de verdad

- <archivo:líneas>

## Salida esperada

- `diagramas/src/NN_s6_nombre.(puml|py)`
- `diagramas/png/NN_s6_nombre.png`
- `diagramas/svg/NN_s6_nombre.svg`

## Criterios de aceptación

- [ ] Legible en A4 y en una diapositiva de 16:9 (texto de 10 pt o más en A4)
- [ ] Datos idénticos a la fuente; incluye título y la nota "Fuente: …"
- [ ] Generado sin servicios en línea (PlantUML local o matplotlib)

---

## Respuesta (la rellena recursos-visuales)

- **Fecha de cierre:**
- **Resultado:** RESUELTA | RECHAZADA
- **Rutas:**
- **Snippet para el informe:** `![Figura N. …](../../diagramas/svg/NN_s6_nombre.svg)`
- **Snippet para la diapositiva (Marp):** `![w:900](../../../diagramas/png/NN_s6_nombre.png)`
- **Notas:**
