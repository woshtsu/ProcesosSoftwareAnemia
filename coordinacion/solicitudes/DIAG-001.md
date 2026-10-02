# DIAG-001 — Proceso AS-IS por carriles (Semana 1)

- **Estado:** RESUELTA
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-002
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Alta

## Tipo de diagrama

- [x] BPMN / flujo de proceso (AS-IS / TO-BE, carriles) — se sugiere diagrama de actividades UML con particiones (swimlanes) en PlantUML.

## Requisito que cubre

- **Guía:** `guias/S1_Guia_trabajo_semana_1.md` — §5 Actividad 2 "Modelar el proceso AS-IS": debe identificar **inicio, actividades principales, decisiones, actores, problemas y fin**, y **no incorporar todavía la solución propuesta**.
- **Entregable destino:** `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` — §3 "Proceso AS-IS", Figura 2.
- **Motivo:** la figura actual (`entregables/semana-01/img/image2.png`, 620×326 px, sin fuente editable) es ilegible a tamaño A4. Se rehace desde fuente PlantUML. El contenido de referencia también está en el Mermaid de la v4 (`archivo/versiones-anteriores/semana-01/Entregable_Semana1_Anemia_Junin_v4.md`, §3).

## Contenido requerido

**Carriles (5, en este orden de arriba abajo):** Familia / cuidador · Personal de salud (enfermera, médico, técnico) · Agente comunitario (actor social) · Gestión territorial (red / microred) · MINSA.
**No debe existir carril "Sistema"** ni ninguna actividad automatizada (regla de la guía).

**Flujo (actividad → carril):**

1. (Familia) **Inicio** → "Acude al establecimiento con el niño (control, campaña, padrón o iniciativa propia)".
2. (Personal) "Registra datos del niño" → "Verifica antecedentes y controles pendientes (tarjeta / historia clínica)".
3. (Personal) Decisión **D1 ¿Corresponde control según edad?** — No → "Deriva según motivo de atención" → **Fin**. Sí → "Realiza control según edad".
4. (Personal) Decisión **D2 ¿Corresponde tamizaje?** — No → "Control regular y próxima cita" (se une al paso 6-No). Sí → "Realiza tamizaje de hemoglobina" → "Interpreta resultado con ajuste por altitud" → "Registra resultado".
5. (Personal) Decisión **D3 ¿Presenta anemia?**
6. D3 = No → (Personal) "Indica suplementación preventiva y próximo control (cita calculada a mano)" → (Familia) "Recibe indicaciones y cita" → **Fin**.
7. D3 = Sí → (Personal) "Diagnostica anemia e inicia tratamiento (sulfato ferroso o hierro polimaltosado, mínimo 6 meses)" → "Registra tratamiento y fecha de inicio en historia clínica, tarjeta de control y HIS (triple registro)" → "Brinda orientación a la familia".
8. (Familia) "Administra el suplemento en casa".
9. (Agente comunitario) "Realiza visita domiciliaria semanal" → "Verifica consumo del suplemento" → "Registra en papel y reporta barreras de forma verbal".
10. (Personal) "Realiza seguimiento periódico (controles y tamizajes de control)" → Decisión **D4 ¿Paciente recuperado?** — Sí → "Registra recuperación y cierra el caso" → **Fin**. No → "Reevalúa, refuerza tratamiento y refiere" (vuelve a 8 o sale hacia referencia).
11. (Gestión territorial) "Consolida información de los establecimientos (con demora)" → "Visualiza indicadores con retraso" → "Coordina circuito de referencia cuando corresponde" → "Genera reporte para el MINSA".
12. (MINSA) "Recibe información consolidada" → "Supervisa el cumplimiento del seguimiento" → "Analiza estadísticas e indicadores de cobertura" → "Evalúa desempeño del proceso" → **Fin**.

**Notas de problema** (nota adosada a la actividad indicada, estilo "PROBLEMA", color de alerta):

| ID | Actividad a la que se adosa | Texto de la nota |
| --- | --- | --- |
| P1 | Indica suplementación preventiva y próximo control | Agendamiento manual, sin recordatorios |
| P2 | Diagnostica anemia e inicia tratamiento | Débil trazabilidad de la adherencia |
| P3 | Registra … (triple registro) | Errores de digitación, duplicidad y demora |
| P4 | Administra el suplemento en casa | Barreras ocultas; abandono silencioso |
| P5 | Realiza visita domiciliaria semanal | Capacidad limitada; carga manual en papel y sin conexión |
| P6 | Realiza seguimiento periódico | Controles atrasados y pérdida de pacientes |
| P7 | Registra recuperación y cierra el caso | Cierre no siempre documentado en el HIS |
| P8 | Reevalúa, refuerza tratamiento y refiere | Circuito de referencia no trazable |
| P9 | Visualiza indicadores con retraso | Indicadores incompletos y tardíos |

Título del diagrama: "Proceso AS-IS — Seguimiento de la anemia infantil en establecimientos rurales de Junín".

## Fuentes de verdad

- `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` §3 (descripción del flujo en 9 pasos y lista de problemas).
- `entregables/semana-01/anexos/Entrevista.md`.
- `entregables/semana-01/img/image2.png` (versión raster anterior, solo referencia visual).
- `archivo/versiones-anteriores/semana-01/Entregable_Semana1_Anemia_Junin_v4.md` §3 (Mermaid original).

## Nombre de archivo sugerido

`10_s1_proceso_as_is` → se producirán:
- `diagramas/src/10_s1_proceso_as_is.puml`
- `diagramas/png/10_s1_proceso_as_is.png`
- `diagramas/svg/10_s1_proceso_as_is.svg`

Enlace ya insertado en el entregable: `![Figura 2. ...](../../diagramas/svg/10_s1_proceso_as_is.svg)`.

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4 (orientación horizontal admisible).
- [ ] Texto en español, sin tildes rotas.
- [ ] Aparecen explícitamente: Inicio, 4 decisiones (D1–D4), 5 carriles, 9 notas de problema, Fin (al menos uno por rama).
- [ ] No aparece ningún carril ni actividad de software.
- [ ] Registrado en el catálogo `diagramas/README.md` (usado en S1).

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** 2026-10-01
- **Resultado:** RESUELTA (cierre administrativo del sincronizador, 2026-10-01: existen fuente `diagramas/src/10_s1_proceso_as_is.puml`, `diagramas/png/10_s1_proceso_as_is.png` y `diagramas/svg/10_s1_proceso_as_is.svg`; la verificación del contenido frente al entregable corresponde a revisor-documental / inspector-guia)
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 2. Proceso AS-IS por carriles de actor, con las notas de problema asociadas a cada actividad (elaboración propia).](../../diagramas/svg/10_s1_proceso_as_is.svg)`
- **Notas:**
