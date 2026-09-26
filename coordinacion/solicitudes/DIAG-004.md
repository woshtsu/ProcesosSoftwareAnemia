# DIAG-004 — Casos de uso de la visión TO-BE (Semana 1, anexo)

- **Estado:** EN CURSO
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-002
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Baja

## Tipo de diagrama

- [x] UML casos de uso

## Requisito que cubre

- **Guía:** `guias/S1_Guia_trabajo_semana_1.md` — no es un requisito explícito; complementa §8 Actividad 5 (identificar dónde interviene el software). Se conserva porque es contenido sustantivo del equipo (v3/v4/v5).
- **Entregable destino:** `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` — Anexo B.1, Figura 10.
- **Motivo:** la figura actual (`entregables/semana-01/img/image10.png`, 470×423 px) es ilegible; la fuente original era Mermaid (v4) y debe pasar a PlantUML.
- **No confundir** con `06_casos_de_uso` (alcance del PMV INC-1). Este diagrama representa la **visión completa TO-BE** (INC-1 a INC-6).

## Contenido requerido

Frontera del sistema: "Sistema de seguimiento de anemia infantil (visión TO-BE)".

**Actores (5):** Personal de salud · Agente comunitario · Familia / cuidador · Gestión territorial · Sistema inteligente (IA / WhatsApp) — este último como actor secundario automatizado, ubicado a la derecha.

**Casos de uso (11) y asociaciones:**

| Caso de uso | Actor(es) asociados | Incremento (S2) |
| --- | --- | --- |
| CU01 Registrar expediente | Personal de salud | INC-1 |
| CU02 Consultar expediente | Personal de salud | INC-1 |
| CU03 Registrar dosaje | Personal de salud | INC-1 |
| CU04 Generar agenda de controles | Sistema inteligente | INC-2 |
| CU05 Estimar riesgo (IA) | Sistema inteligente | INC-5 |
| CU06 Enviar notificación WhatsApp | Sistema inteligente | INC-4 |
| CU07 Confirmar cita / reportar barrera | Familia / cuidador | INC-4 |
| CU08 Registrar visita domiciliaria | Agente comunitario | INC-3 |
| CU09 Gestionar referencia | Personal de salud | INC-6 |
| CU10 Consultar indicadores | Gestión territorial | INC-6 |
| CU11 Sincronizar offline | Agente comunitario | INC-3 |

**Relaciones:**
- CU04 `<<include>>` CU05 (la agenda se ordena según el riesgo estimado).
- CU04 `<<include>>` CU06 (la agenda dispara el recordatorio).
- CU11 `<<extend>>` CU01, CU03 y CU08 (condición: sin conectividad).

Opcional: rotular cada caso de uso con su incremento (INC-n) en texto pequeño.

## Fuentes de verdad

- `archivo/versiones-anteriores/semana-01/Entregable_Semana1_Anemia_Junin_v4.md` §9.1 (Mermaid y descripción).
- `entregables/semana-01/img/image10.png`.
- `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md` §7 (incrementos INC-1..INC-6).

## Nombre de archivo sugerido

`13_s1_casos_uso_vision` → `diagramas/src/13_s1_casos_uso_vision.puml`, `diagramas/png/13_s1_casos_uso_vision.png`, `diagramas/svg/13_s1_casos_uso_vision.svg`.

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4.
- [ ] Texto en español, sin tildes rotas.
- [ ] 5 actores, 11 casos de uso y las 5 relaciones include/extend indicadas.
- [ ] Registrado en `diagramas/README.md`.

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** AAAA-MM-DD
- **Resultado:** RESUELTA | RECHAZADA
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 10. Casos de uso de la visión TO-BE: 5 actores y 11 casos de uso (elaboración propia).](../../diagramas/svg/13_s1_casos_uso_vision.svg)`
- **Notas:**
