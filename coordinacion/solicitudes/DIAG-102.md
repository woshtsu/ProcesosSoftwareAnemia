# DIAG-102 — Diagrama de Gantt del Incremento 1 (Semanas 3-4)

- **Estado:** EN CURSO  <!-- ABIERTA | EN CURSO | RESUELTA | RECHAZADA -->
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-004
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Alta

## Tipo de diagrama

- [x] Gantt / cronograma / WBS

## Requisito que cubre

- **Guía:** `guias/S3-4_Guia_trabajo_semanas_3_y_4.md` — Actividad 9 (§13), Producto: «Elaborar un cronograma o tablero de planificación que permita visualizar el trabajo». Producto esperado: «Elaboración de un cronograma o tablero de planificación»; «Identificación de dependencias y ruta crítica».
- **Entregable destino:** `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` — §11.2, Figura 3 (marcador `<!-- DIAG-102 pendiente -->`).

## Contenido requerido

Gantt diario del **01-sep-2026 al 28-sep-2026** (PlantUML `@startgantt` sirve; `Project starts 2026-09-01`, días calendario, **sin** cerrar fines de semana). Dos separadores: «Sprint 1 (01-14 sep)» y «Sprint 2 (15-28 sep)». Barras con dependencias (flechas fin→inicio). **Barras de la ruta crítica en rojo** (o color de énfasis); las demás en gris/azul. Etiqueta de responsable al lado de cada barra.

| ID | Actividad (texto de la barra) | Responsable | Inicio | Fin | Depende de | Crítica |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Sprint Planning S1 | Porras V. | 2026-09-01 | 2026-09-01 | — | Sí |
| A02 | Arquitectura hexagonal y ADR | Auqui H. | 2026-09-02 | 2026-09-03 | A01 | Sí |
| A03 | Esquema de datos y migración 001 | Auqui H. | 2026-09-04 | 2026-09-05 | A02 | No (holgura 4 d) |
| A04 | Entorno de calidad (pytest, cobertura, ruff) | Huamani R. | 2026-09-02 | 2026-09-03 | A01 | No (holgura 6 d) |
| A05 | Normativa JSON y proveedor | Auqui H. | 2026-09-02 | 2026-09-03 | A01 | No (holgura 4 d) |
| A06 | Validadores de dominio (HIST-1.3) | Auqui H. | 2026-09-04 | 2026-09-07 | A02 | Sí |
| A07 | Clasificador de Hb (HIST-1.3) | Auqui H. | 2026-09-08 | 2026-09-09 | A05, A06 | Sí |
| A08 | Pruebas de valores límite | Huamani R. | 2026-09-10 | 2026-09-11 | A04, A07 | No (holgura 1 d) |
| A09 | Registro: caso de uso y repositorios (HIST-1.1) | Auqui H. | 2026-09-10 | 2026-09-11 | A03, A07 | Sí |
| A10 | API POST/GET /ninos + OpenAPI | Auqui H. | 2026-09-12 | 2026-09-12 | A09 | Sí |
| A11 | Formulario web de registro | Auqui H. | 2026-09-12 | 2026-09-12 | A09 | Sí |
| A12 | Pruebas persistencia/API y revisión de código | Huamani R. | 2026-09-13 | 2026-09-13 | A08, A10, A11 | Sí |
| A13 | Revisión y retrospectiva S1 | Porras V. | 2026-09-14 | 2026-09-14 | A12 | Sí |
| A14 | Sprint Planning S2 | Porras V. | 2026-09-15 | 2026-09-15 | A13 | Sí |
| A15 | Expediente y dosajes (HIST-1.2) | Auqui H. | 2026-09-16 | 2026-09-19 | A14 | Sí |
| A16 | Listado en seguimiento (HIST-1.4) | Auqui H. | 2026-09-20 | 2026-09-21 | A15 | No (holgura 1 d) |
| A17 | Reporte del periodo (HIST-1.5) | Auqui H. | 2026-09-20 | 2026-09-22 | A15 | Sí |
| A18 | Pruebas de integración, cobertura y ruff S2 | Huamani R. | 2026-09-23 | 2026-09-24 | A16, A17 | Sí |
| A19 | Datos sintéticos y demostración local | Auqui H. | 2026-09-25 | 2026-09-25 | A18 | Sí |
| A20 | Revisión de aceptación con personal de salud | Porras V. | 2026-09-26 | 2026-09-27 | A19 | Sí |
| A21 | Retrospectiva y actualización del plan | Porras V. | 2026-09-28 | 2026-09-28 | A20 | Sí |

Hitos (rombos): **H0** «Arquitectura base y entorno de calidad» el 2026-09-05 (tras A03/A04); **H1** «INC-1 (PMV) aceptado» el 2026-09-28 (tras A21).

Nota: A10 y A11 son paralelas y ambas críticas (misma fecha, holgura 0).

## Fuentes de verdad

- `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` Tabla 22 (plan de trabajo), Tabla 24 (holguras), Tabla 25 (hitos).

## Nombre de archivo sugerido

`32_s34_gantt_incremento1` → `diagramas/src/32_s34_gantt_incremento1.puml`, `diagramas/png/32_s34_gantt_incremento1.png`, `diagramas/svg/32_s34_gantt_incremento1.svg`

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4 (se admite apaisado)
- [ ] Texto en español, sin tildes rotas
- [ ] Fechas y dependencias idénticas a la tabla anterior
- [ ] Ruta crítica diferenciada por color y con leyenda
- [ ] Hitos H0 y H1 visibles

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** AAAA-MM-DD
- **Resultado:** RESUELTA | RECHAZADA
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 3. Diagrama de Gantt del Incremento 1 (actividades A01 a A21, del 01 al 28 de septiembre de 2026) con la ruta crítica resaltada (elaboración propia).](../../diagramas/svg/32_s34_gantt_incremento1.svg)`
- **Notas:**
