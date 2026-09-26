# DIAG-003 — Cadena de valor del proceso TO-BE (Semana 1)

- **Estado:** EN CURSO
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-002
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Media

## Tipo de diagrama

- [x] Otro: cadena de valor / flujo de valor horizontal (PlantUML de actividades en horizontal o rectángulos enlazados).

## Requisito que cubre

- **Guía:** `guias/S1_Guia_trabajo_semana_1.md` — §9 Actividad 6: "Construya una cadena de valor equivalente: **Entrada → Actividad → Resultado → Decisión → Acción → Valor**" y la relación "Actividad mejorada → mejor resultado → valor organizacional".
- **Entregable destino:** `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` — §7 "Valor organizacional", Figura 8.
- **Motivo:** la figura actual (`entregables/semana-01/img/image9.png`, 620×98 px) es ilegible.

## Contenido requerido

Flujo de izquierda a derecha; cada caja lleva arriba la etapa en mayúsculas y abajo el contenido:

1. **ENTRADA** — "Datos del niño registrados en la posta o en la visita domiciliaria (con o sin conexión)".
2. **ACTIVIDAD** — "Motor de reglas identifica controles pendientes y el modelo predictivo estima el riesgo de abandono" (resaltar como apoyo del software).
3. **RESULTADO** — "Agenda priorizada y alertas con nivel de riesgo para el personal y el agente comunitario".
4. **DECISIÓN** (rombo) — "¿El caso requiere intervención domiciliaria?" (decisión del profesional).
5. **ACCIÓN** — dos ramas:
   - "Riesgo alto" → "Visita domiciliaria y gestión de la barrera".
   - "Rutinario" → "Atención y tamizaje estándar según esquema normativo".
   - Ambas con nota: "Aviso previo a la familia por WhatsApp".
6. Ambas ramas convergen en "Registro de seguimiento interconectado".
7. **VALOR** — "Atención continua y oportuna; recuperación confirmada del niño dentro del plazo clínico esperado" (resaltado en verde).

Debajo de la cadena, una franja de indicadores (texto pequeño) alineada con cada etapa:
- Entrada → "Registros que superan validaciones"; Actividad → "Precisión del modelo"; Resultado → "Cumplimiento de visitas priorizadas"; Acción → "Cobertura oportuna de controles"; Valor → "Pérdida de seguimiento / Recuperación documentada al año".

Título: "Cadena de valor del proceso TO-BE: Entrada → Actividad → Resultado → Decisión → Acción → Valor".

## Fuentes de verdad

- `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` §7 (cadena explicada) y §8 (Tabla de indicadores).
- `archivo/versiones-anteriores/semana-01/Entregable_Semana1_Anemia_Junin_v4.md` §7 (Mermaid original).

## Nombre de archivo sugerido

`12_s1_cadena_valor` → `diagramas/src/12_s1_cadena_valor.puml`, `diagramas/png/12_s1_cadena_valor.png`, `diagramas/svg/12_s1_cadena_valor.svg`.

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4 (el ancho no debe forzar texto menor de 8 pt; se admite partir en dos filas).
- [ ] Texto en español, sin tildes rotas.
- [ ] Aparecen las 6 etapas con su rótulo exacto.
- [ ] Registrado en `diagramas/README.md`.

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** AAAA-MM-DD
- **Resultado:** RESUELTA | RECHAZADA
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 8. Cadena de valor del proceso TO-BE (elaboración propia).](../../diagramas/svg/12_s1_cadena_valor.svg)`
- **Notas:**
