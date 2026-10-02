# Contexto de procesos S1–S5: cifras y matrices clave

- **Elaborado por:** `sincronizador` el 2026-10-01.
- **Uso:** es la fuente resumida para las secciones 2 y 3.1 del informe y para las diapositivas 1, 2, 6 y 7. Antes de copiar una tabla completa, ir siempre al entregable citado. Las rutas son relativas a la raíz.

| Clave | Entregable |
| --- | --- |
| S1 | `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` |
| S2 | `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md` |
| S3-4 | `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` |
| S5 | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` (**describe Flask; usar solo su estructura de matrices, no sus cifras**) |

## S1. Enfoque de procesos (informe §2.1; diapositiva 1)

| Elemento | Dato clave | Ubicación |
| --- | --- | --- |
| Problema | El seguimiento de la anemia infantil rural en Junín se pierde: el "triple registro" (historia clínica, tarjeta de control y digitación en el HIS), la agenda manual, las barreras familiares ocultas, la capacidad limitada de visitas y la conectividad intermitente hacen que el proceso sea **reactivo**. Contexto: ENDES 2025, 39,0 % de anemia en niños de 6 a 35 meses en Junín (no es atribuible al sistema). Norma: NTS N.° 213-MINSA/DGIESP-2024, que derogó la NTS 134 | S1 §1 |
| Actores (6) | Niño o niña · familia/cuidador · personal de salud · agente comunitario · gestión territorial (redes/microredes) · MINSA. Tabla 2: necesidad y decisión de cada uno | S1 §2 |
| AS-IS | 9 actividades, decisiones D1–D4 (¿control por edad? ¿tamizaje? ¿anemia? ¿recuperado?) y problemas P1–P7. Diagrama `diagramas/svg/10_s1_proceso_as_is.svg` | S1 §3 |
| Brechas (6 ≥ 5) | **B1** triple registro sin registro nominal único · **B2** agenda manual sin recordatorios · **B3** barreras familiares ocultas hasta el abandono · **B4** visita domiciliaria en papel y sin conexión · **B5** sin anticipación del riesgo de abandono · **B6** conectividad intermitente y consolidación tardía | S1 §4, Tabla 3 |
| TO-BE | Mejoras M1–M6: M1 registro nominal único validado · M2 controles programados · M3 comunicación y confirmación · M4 visita estructurada y priorizada · M5 riesgo explicable · M6 captura local y sincronización. Diagrama `diagramas/svg/11_s1_proceso_to_be.svg` | S1 §5–6 |
| Cadena de valor | Entrada → Actividad → Resultado → Decisión → Acción → Valor (Tabla 7). Diagrama `diagramas/svg/12_s1_cadena_valor.svg` | S1 §7 |
| Indicadores (14) | Proceso 4 · Producto 5 · Resultado 2 · Valor 3 (Tabla 8). Sin metas: estas requieren línea base | S1 §8 |
| Indicador ya medible en el PMV | Triple registro → **expediente único** (3 → 1 registros por evaluación; `pmv_fastapi/docs/diagramas/tablero.py`) | — |

## S2. Selección del modelo (informe §2.2; diapositiva 2)

| Elemento | Dato clave | Ubicación |
| --- | --- | --- |
| Factores (8, todos de importancia Alta) | Cambios de requisitos · retroalimentación · riesgo · integración · entrega incremental · automatización · datos e IA · conectividad intermitente. Para la consigna hay que reetiquetarlos como **Incertidumbre, Complejidad, Riesgo, Integración y Datos/IA** (el integrador actual ya lo hace en §2.2) | S2 §2, Tabla 2 |
| Comparación (7 enfoques, escala 1–5, 6 criterios) | Cascada **8** · Incremental 18 · Espiral 21 · **Scrum 27** · Kanban 21 · **DevOps 26** · **MLOps/DataOps 26** | S2 §3, Tabla 3 |
| Decisión ponderada (8 criterios) | **Alt. 1, iterativo-incremental + Scrum + DevOps + MLOps: 4,75** · Alt. 2, Kanban + DevOps + DataOps: 3,85 · Alt. 3, tradicional Incremental + Espiral: 2,95 | S2 §4.1, Tabla 6 |
| Modelo seleccionado | Ciclo de vida iterativo-incremental; gestión con Scrum (sprints de 2 semanas); ingeniería DevOps; MLOps para el componente predictivo (desde INC-5) | S2 §4, Tabla 5 |
| Rechazo de Cascada | "Exige congelar requisitos al inicio y valida al final; incompatible con la incertidumbre" (Tabla 4). Scrum solo "no define cómo automatizar la entrega" | S2 §3, Tabla 4; §5.7 |
| Diagrama | `diagramas/svg/15_s2_modelo_proceso_aplicado.svg` | S2 §6 |
| Incrementos | INC-1 Registro · INC-2 Agenda · INC-3 Offline · INC-4 Mensajería · INC-5 Predicción · INC-6 Tablero | S2 §7 |

## S3-4. Actividades y planificación (informe §2.3; diapositiva 6)

| Elemento | Dato clave | Ubicación |
| --- | --- | --- |
| Actividades | De ciclo (por sprint) y por incremento, con entrada, producto y salida | S3-4 §3, §6 (productos de trabajo) |
| RAE | Tabla 6, con 14 actividades × (Ejecución, Participantes, Revisión, Aprobación, Evidencia). Ejecución: Porras V. (requisitos, evaluación, retrospectiva), Auqui H. (análisis, diseño, implementación, integración, despliegue) y Huamani R. (pruebas, prueba offline, monitoreo) | S3-4 §5 |
| DoD | Por actividad, en §7. DoD técnico: cobertura ≥ 80 %, pruebas en verde, ruff 0 y revisión | S3-4 §7 |
| WBS | Proyecto → Entregables → Incrementos → Épicas (EP-1.T habilitadores, EP-1.A registro/expediente, EP-1.B validación, EP-1.C seguimiento/reporte) → HIST-1.1 a 1.5 (= HU-01 a 05) → Tareas T01–T16. Diagrama `diagramas/svg/31_s34_wbs_proyecto.svg` | S3-4 §8.2 |
| Priorización ponderada | INC-1 4,60 · INC-3 4,40 · INC-2 4,15 · INC-4 3,40 · INC-5 3,35 · INC-6 2,75. Pesos: valor 30 %, riesgo 25 %, dependencia 20 %, complejidad inversa 15 % y validación 10 % | S3-4 §9 |
| Estimación | INC-1 = **21 SP** (Sprint 1: 13 SP / 69 h-p; Sprint 2: 8 SP / 44 h-p) = **113 h-p** estimadas | S3-4 §10 |
| Plan | 8 sprints de 2 semanas, del 01/09/2026 al 21/12/2026. Hitos H1–H7. Diagramas `diagramas/svg/32_s34_gantt_incremento1.svg`, `33_s34_cronograma_sprints_hitos.svg` y `34_s34_red_ruta_critica_inc1.svg` | S3-4 §11–12 |
| Seguimiento | Matriz de seguimiento y simulación de la reunión (Act. 15); 18 indicadores (Tabla 30) con metas: avance ≥ 90 %, historias ≥ 80 %, cobertura ≥ 80 %, ruff 0 y < 1 defecto mayor por historia | S3-4 §13–14 |
| Desviaciones | Registro de riesgos, tipos y umbral de acción, y matriz de control | S3-4 §15 |
| Burndown | `diagramas/svg/35_s34_burndown_sprint1.svg` (**serie simulada**: decirlo) | S3-4 §11 |
| Trazabilidad / valor | §16–17 | S3-4 |

## S5. Ejecución del Incremento 1 (informe §3.1; usar con el PMV FastAPI)

| Elemento | Dato reutilizable | Advertencia |
| --- | --- | --- |
| Matrices | 1.1 alcance · 2.1 diseño · 3.1 construcción · 4.1 registro de pruebas · 5.1 valor operativo | Su contenido describe Flask. Hay que rehacerlas con `DATOS_PMV_FASTAPI.md` |
| Categorización | Principales (requisitos, diseño, construcción, integración/pruebas, despliegue) · Soporte (documentación, configuración, verificación, revisión, resolución de problemas) · Organizacionales/gestión (planificación, infraestructura, coordinación, mejora) | Válida (integrador §3.1) |
| Tailoring | Restricciones: equipo de 3, alcance de INC-1, demo local, normativa variable, entorno de pruebas y usuario no disponible | Actualizar a FastAPI: monolito modular, PWA, PostgreSQL/SQLite, Docker y CI |

## Antecedente Flask (dato histórico, no es resultado del PMV)

- 266 pruebas pytest; cobertura 96,69 %.
- Demo sintética con 31/35 altas aceptadas (88,6 %).
- DEV-101 corregido con 24 regresiones.
- Fuente: el integrador actual §1 y §3.3 y `anemia_junin/docs/evidencias/`.
