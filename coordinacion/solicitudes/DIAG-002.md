# DIAG-002 — Proceso TO-BE por carriles con intervención del software (Semana 1)

- **Estado:** RESUELTA
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-002
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Alta

## Tipo de diagrama

- [x] BPMN / flujo de proceso (AS-IS / TO-BE, carriles) — diagrama de actividades UML con particiones en PlantUML.

## Requisito que cubre

- **Guía:** `guias/S1_Guia_trabajo_semana_1.md` — §7 Actividad 4 "Diseñar el proceso TO-BE": incorporar **únicamente las mejoras que resuelven las brechas**; el diagrama debe mostrar **1) entrada de información, 2) actividades mejoradas, 3) decisiones, 4) intervención del software, 5) resultado, 6) generación de valor**. También apoya §8 Actividad 5 (dónde interviene el software).
- **Entregable destino:** `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` — §5 "Proceso TO-BE", Figura 7.
- **Motivo:** la figura actual (`entregables/semana-01/img/image7.png`, 620×331 px) es ilegible y no rotula de forma explícita "Resultado" y "Valor".

## Contenido requerido

**Carriles (6):** Familia / cuidador · Personal de salud · **Sistema (App/Web + motor de reglas NTS + modelo predictivo + WhatsApp)** · Agente comunitario · Gestión territorial · MINSA.

**Marcas obligatorias:** cada actividad del carril Sistema lleva una etiqueta de mejora `M1…M6` que referencia la brecha que resuelve (`B1…B6`, ver tabla). Las decisiones clínicas quedan en el carril Personal de salud (nota: "El modelo no diagnostica ni prescribe").

| Mejora | Resuelve brecha | Actividad del sistema |
| --- | --- | --- |
| M1 | B1 Triple registro | Registro nominal único validado y deduplicado |
| M2 | B2 Agenda manual | Genera plan y agenda de controles según esquema normativo (edad y tipo de nacimiento) |
| M3 | B3 Barreras ocultas | Envía recordatorio por WhatsApp y recibe confirmación o reporte de barrera |
| M4 | B4 Capacidad limitada del agente | Prioriza visitas y ofrece formulario estructurado de visita |
| M5 | B5 Sin anticipación del riesgo | Modelo predictivo estima riesgo de abandono (score 0-100, explicable) y ordena la agenda |
| M6 | B6 Conectividad intermitente | Registro sin conexión y sincronización diferida; indicadores actualizados |

**Flujo:**

1. **Entrada de información** (rotular como tal): (Familia) Inicio "Acude al establecimiento o es contactada"; datos del niño, dosaje, respuestas de la familia y visitas.
2. (Personal) "Registra al niño en App/Web" → (Sistema) **M1** "Valida y deduplica registro nominal".
3. (Sistema) **M2** "Evalúa reglas normativas y propone controles pendientes" → (Personal) decisión **¿Corresponde tamizaje?** — No → "Control regular". Sí → (Personal) "Realiza dosaje de Hb" → (Sistema) **M6** "Registra online/offline y calcula Hb ajustada por altitud".
4. (Personal) decisión **¿Presenta anemia?** (decisión clínica) — No → "Indica suplementación preventiva"; Sí → "Diagnostica e indica tratamiento".
5. (Sistema) **M2** "Genera plan de tratamiento y agenda de controles" → **M5** "Estima riesgo de abandono y prioriza la agenda" → **M3** "Envía recordatorio por WhatsApp".
6. (Familia) "Confirma asistencia o reporta barrera" → (Sistema) "Registra barrera y alerta al agente comunitario".
7. (Personal / Agente) decisión **¿Requiere visita prioritaria?** — Sí → (Agente) **M4** "Registra visita en la app (sin conexión) y gestiona la barrera" → (Sistema) **M6** "Sincroniza al recuperar señal". No → continúa.
8. (Personal) "Realiza control agendado y seguimiento" → decisión **¿Recuperado según protocolo?** — Sí → "Cierre documentado del caso". No → "Referencia trazable (estados, responsable, alertas de atraso)".
9. (Sistema) "Actualiza indicadores en tiempo real" → (Gestión territorial) "Consulta tablero y prioriza supervisión y recursos" → (MINSA) "Supervisa cumplimiento y evalúa desempeño".
10. **Resultado** (rotular): "Seguimiento continuo y recuperación documentada del niño".
11. **Valor** (rotular): "Menor pérdida de seguimiento, atención oportuna y mejor uso del personal disponible" → **Fin**.

Leyenda: color distinto para actividades humanas, actividades del sistema (software) y las cajas de Resultado / Valor.

Título: "Proceso TO-BE — Seguimiento de la anemia infantil con apoyo del sistema".

## Fuentes de verdad

- `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` §4 (Tabla de brechas B1–B6), §5 (cambios respecto del AS-IS y Tabla "brecha → mejora"), §6 (aporte del software).
- `archivo/versiones-anteriores/semana-01/Entregable_Semana1_Anemia_Junin_v4.md` §5 (Mermaid original del TO-BE).
- `entregables/semana-01/img/image7.png` (referencia visual anterior).

## Nombre de archivo sugerido

`11_s1_proceso_to_be` → `diagramas/src/11_s1_proceso_to_be.puml`, `diagramas/png/11_s1_proceso_to_be.png`, `diagramas/svg/11_s1_proceso_to_be.svg`.

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4 (horizontal admisible).
- [ ] Texto en español, sin tildes rotas.
- [ ] Se identifican visualmente los 6 elementos exigidos por la guía (entrada, actividades mejoradas, decisiones, intervención del software, resultado, valor).
- [ ] Etiquetas M1–M6 presentes y coherentes con la tabla anterior.
- [ ] Registrado en `diagramas/README.md`.

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** 2026-10-01
- **Resultado:** RESUELTA (cierre administrativo del sincronizador, 2026-10-01: existen fuente `diagramas/src/11_s1_proceso_to_be.puml`, `diagramas/png/11_s1_proceso_to_be.png` y `diagramas/svg/11_s1_proceso_to_be.svg`; la verificación del contenido frente al entregable corresponde a revisor-documental / inspector-guia)
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 7. Proceso TO-BE por carriles de actor, con el carril Sistema y las mejoras M1-M6 (elaboración propia).](../../diagramas/svg/11_s1_proceso_to_be.svg)`
- **Notas:**
