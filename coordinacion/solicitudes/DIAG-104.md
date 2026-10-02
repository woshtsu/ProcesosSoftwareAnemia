# DIAG-104 — Red de actividades y ruta crítica del Incremento 1 (Semanas 3-4)

- **Estado:** RESUELTA  <!-- ABIERTA | EN CURSO | RESUELTA | RECHAZADA -->
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-004
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Alta

## Tipo de diagrama

- [ ] Gantt / cronograma / WBS
- [x] Otro: red de actividades (diagrama de precedencias / PERT-CPM, actividad en el nodo)

## Requisito que cubre

- **Guía:** `guias/S3-4_Guia_trabajo_semanas_3_y_4.md` — Producto esperado «Identificación de dependencias y ruta crítica cuando corresponda»; Actividad 10 (§14) dependencias.
- **Entregable destino:** `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` — §11.4, Figura 5 (marcador `<!-- DIAG-104 pendiente -->`).

## Contenido requerido

Red de precedencias de izquierda a derecha, **una caja por actividad** con el formato:

```
| ID  | Dur (d) |
| Nombre corto   |
| Inicio – Fin | Holgura |
```

Flechas = dependencias fin→inicio. **Ruta crítica en rojo y trazo grueso**; resto en gris. Nodo «Inicio» antes de A01 y «Fin (H1)» después de A21. Separador visual entre Sprint 1 y Sprint 2.

| ID | Nombre corto | Dur (días) | Inicio | Fin | Predecesoras | Holgura | Crítica |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A01 | Sprint Planning S1 | 1 | 01-sep | 01-sep | — | 0 | Sí |
| A02 | Arquitectura y ADR | 2 | 02-sep | 03-sep | A01 | 0 | Sí |
| A03 | Esquema y migración | 2 | 04-sep | 05-sep | A02 | 4 | No |
| A04 | Entorno de calidad | 2 | 02-sep | 03-sep | A01 | 6 | No |
| A05 | Normativa JSON | 2 | 02-sep | 03-sep | A01 | 4 | No |
| A06 | Validadores | 4 | 04-sep | 07-sep | A02 | 0 | Sí |
| A07 | Clasificador Hb | 2 | 08-sep | 09-sep | A05, A06 | 0 | Sí |
| A08 | Pruebas valores límite | 2 | 10-sep | 11-sep | A04, A07 | 1 | No |
| A09 | Registro (caso de uso) | 2 | 10-sep | 11-sep | A03, A07 | 0 | Sí |
| A10 | API registro + OpenAPI | 1 | 12-sep | 12-sep | A09 | 0 | Sí |
| A11 | Formulario web | 1 | 12-sep | 12-sep | A09 | 0 | Sí |
| A12 | Pruebas S1 + revisión código | 1 | 13-sep | 13-sep | A08, A10, A11 | 0 | Sí |
| A13 | Revisión + retro S1 | 1 | 14-sep | 14-sep | A12 | 0 | Sí |
| A14 | Sprint Planning S2 | 1 | 15-sep | 15-sep | A13 | 0 | Sí |
| A15 | Expediente y dosajes | 4 | 16-sep | 19-sep | A14 | 0 | Sí |
| A16 | Listado en seguimiento | 2 | 20-sep | 21-sep | A15 | 1 | No |
| A17 | Reporte del periodo | 3 | 20-sep | 22-sep | A15 | 0 | Sí |
| A18 | Pruebas integración S2 | 2 | 23-sep | 24-sep | A16, A17 | 0 | Sí |
| A19 | Demostración local | 1 | 25-sep | 25-sep | A18 | 0 | Sí |
| A20 | Revisión de aceptación (H1) | 2 | 26-sep | 27-sep | A19 | 0 | Sí |
| A21 | Retro y actualización del plan | 1 | 28-sep | 28-sep | A20 | 0 | Sí |

**Ruta crítica (texto de la leyenda):** A01 → A02 → A06 → A07 → A09 → A10 / A11 → A12 → A13 → A14 → A15 → A17 → A18 → A19 → A20 → A21 = 28 días (01-28 sep 2026).

## Fuentes de verdad

- `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` Tabla 22 y Tabla 24, §11.4.

## Nombre de archivo sugerido

`34_s34_red_ruta_critica_inc1` → `diagramas/src/34_s34_red_ruta_critica_inc1.puml` (o `.py`), `diagramas/png/34_s34_red_ruta_critica_inc1.png`, `diagramas/svg/34_s34_red_ruta_critica_inc1.svg`

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4 (se admite apaisado)
- [ ] Texto en español, sin tildes rotas
- [ ] Holguras y duraciones idénticas a la tabla
- [ ] Ruta crítica diferenciada y leyenda con la duración total (28 días)

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** 2026-10-01
- **Resultado:** RESUELTA (cierre administrativo del sincronizador, 2026-10-01: existen fuente `diagramas/src/34_s34_red_ruta_critica_inc1.puml`, `diagramas/png/34_s34_red_ruta_critica_inc1.png` y `diagramas/svg/34_s34_red_ruta_critica_inc1.svg`; la verificación del contenido frente al entregable corresponde a revisor-documental / inspector-guia)
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 5. Red de actividades del Incremento 1 con la ruta crítica y las holguras (elaboración propia).](../../diagramas/svg/34_s34_red_ruta_critica_inc1.svg)`
- **Notas:**
