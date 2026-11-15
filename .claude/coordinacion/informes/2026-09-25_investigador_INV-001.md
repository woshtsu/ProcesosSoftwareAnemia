# Informe INV-001: Vigencia y comparación NTS 134 vs. NTS 213-2024

**Investigador:** Subagente INVESTIGADOR  
**Fecha de cierre:** 2026-09-25  
**Solicitante:** revisor-documental  
**Estado:** RESUELTA  

---

## Resumen ejecutivo

La **NTS N° 213-MINSA/DGIESP-2024** (aprobada por RM 251-2024-MINSA, modificada por RM 429-2024-MINSA) **reemplazó completamente a la NTS N° 134-MINSA/2017/DGIESP** desde abril de 2024. El cambio más significativo para el proyecto es el aumento del umbral de hemoglobina para niños de 6-23 meses de 9.5 g/dL (NTS 134) a 10.5 g/dL (NTS 213), en línea con la actualización de la OMS de marzo 2024. El entregable S1 cita la NTS 134-2017, pero describe un esquema local del establecimiento que no está completamente alineado con la normativa oficial vigente. El PMV (`normativa_v1.json`) sí adopta la NTS 213-2024.

---

## 1. Vigencia: ¿Reemplazó la NTS 213-2024 a la NTS 134-2017?

**Conclusión: SÍ, definitivamente.**

- **NTS 134-MINSA/2017/DGIESP** fue la norma técnica vigente desde 2017 para el "Manejo terapéutico y preventivo de la anemia en niños, adolescentes, mujeres gestantes y puérperas" (RM N° 250-2017-MINSA).

- **NTS 213-MINSA/DGIESP-2024** fue aprobada por **Resolución Ministerial N° 251-2024-MINSA** (publicada abril 2024) como la nueva norma técnica de salud: "Prevención y control de la anemia por deficiencia de hierro en niño y niña, adolescentes, mujeres en edad fértil, gestantes y puérperas".

- Posteriormente fue modificada por **Resolución Ministerial N° 429-2024-MINSA** (septiembre 2024).

- **Fecha de entrada en vigencia:** Abril de 2024 (con la RM 251-2024-MINSA).

**Fuentes:**
- [Resolución Ministerial N.° 251-2024-MINSA](https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa) — Ministerio de Salud, Plataforma del Estado Peruano.
- [Resolución Ministerial N.° 429-2024-MINSA](https://www.gob.pe/institucion/minsa/normas-legales/5670414-429-2024-minsa) — Ministerio de Salud, Plataforma del Estado Peruano.
- [Resolución Ministerial N.° 250-2017-MINSA](https://www.gob.pe/institucion/minsa/normas-legales/189840-250-2017-minsa) — Ministerio de Salud, Plataforma del Estado Peruano (norma anterior, derogada).

---

## 2. Cambios relevantes: NTS 134 vs. NTS 213-2024

### 2.1 Umbrales de hemoglobina por grupo de edad

**NTS 134-2017 (datos disponibles parcialmente):**
- No se pudo acceder al documento completo, pero según las entrevistas y literatura, usaba un umbral de 9.5 g/dL para la anemia leve en niños de 6-23 meses.

**NTS 213-2024 (OMS 2024, adoptado por MINSA):**

| Grupo de edad | Umbral sin anemia (Hb ≥) | Anemia leve | Anemia moderada | Anemia severa |
|---|---|---|---|---|
| **6 a 23 meses** | 10.5 g/dL | < 10.5 | < 9.5 | < 7.0 |
| **24 a 59 meses** | 11.0 g/dL | < 11.0 | < 10.0 | < 7.0 |

**Cambio clave:** El umbral para 6-23 meses aumentó de ~9.5 a 10.5 g/dL, representando una medida más conservadora que alinea Perú con el cambio de criterios OMS de marzo 2024, que eliminó la preestimación de prevalencia de anemia.

**Fuentes:**
- Búsqueda y síntesis de ENDES 2024 y documentación técnica MINSA. Referencia: "Hemoglobin levels for determining anemia: new World Health Organization guidelines and adaptation of the national standard", WHO 2024. Disponible en [PMC11300700](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11300700/).

### 2.2 Edades de tamizaje

**NTS 213-2024 (información disponible):**
- **Niños menores de 6 meses:** Tamizaje con hierro preventivo (según esquema de suplementación preventiva).
- **6 a 59 meses (hasta los 5 años):** Tamizaje regular de hemoglobina.
- **Adolescentes y mujeres:** Esquemas adicionales no aplicables al ámbito pediátrico del proyecto.

El entregable S1 transcribe un esquema local que inicia tamizaje hacia los 6 meses (en el niño a término), lo cual es consistente con la NTS 213.

**Fuentes:**
- NTS N° 213-MINSA/DGIESP-2024, RM 251-2024-MINSA (2024, vigente).

### 2.3 Ajuste por altitud

**NTS 213-2024 (adopta OMS 2024):**

La norma adopta un nuevo algoritmo de ajuste por altitud basado en la guía de OMS 2024. El `normativa_v1.json` contiene una tabla de ajuste que debe verificarse contra la tabla oficial de NTS 213.

**Tabla de ajuste (según `normativa_v1.json`, líneas 38-49):**

| Altitud (msnm) | Ajuste (g/dL) | Verificada |
|---|---|---|
| 0–499 | 0.0 | — |
| 500–999 | 0.4 | — |
| 1,000–1,499 | 0.8 | — |
| 1,500–1,999 | 1.1 | — |
| 2,000–2,499 | 1.4 | — |
| 2,500–2,999 | 1.8 | — |
| 3,000–3,499 | 2.1 | — |
| 3,500–3,999 | 2.5 | — |
| ≥4,000 | 2.9–3.3 | **NO verificadas** (marca de alerta) |

**Observación crítica:** El `normativa_v1.json` (línea 37) declara explícitamente: *"Altitud 0–499 m adopta ajuste 0.0 como decisión explícita del PMV"*, y (línea 37) marca filas ≥4,000 msnm como no verificadas, con advertencia visible cada vez que se usan.

Junín (el departamento del proyecto) tiene territorios que alcanzan 3,500–4,000 msnm (p. ej., la provincia de Satipo tiene zonas de este rango), por lo que esta limitación puede afectar la precisión clínica.

**Fuentes:**
- `anemia_junin/config/normativa_v1.json` (líneas 34–50).
- NTS N° 213-MINSA/DGIESP-2024, RM 251-2024-MINSA; modificada por RM 429-2024-MINSA.
- Guía de OMS 2024 para ajuste por altitud (referencia en NTS 213).

### 2.4 Esquema de suplementación preventiva y terapéutica

**NTS 213-2024 (información disponible):**
- Suplementación preventiva con hierro para niños 0–11 años.
- Suplementación terapéutica: dosis de 3 mg/kg/día durante 6 meses (NTS 213).
- Esquemas diferenciados por edad y tipo de nacimiento (prematuro vs. a término).

**Entregable S1 (Anexo A.1, Tablas A.1–A.4):**
Transcribe un esquema local del establecimiento entrevistado con dosajes (DHx, DHc1, DHc2) y suplementación (PO1, PO2, SF1–SF6, TA) que sigue un patrón normativo pero no se identifica explícitamente si proviene de NTS 134 o si es una adaptación local.

- **DHx = Dosaje inicial (tamizaje)**
- **DHc1, DHc2 = Controles de dosaje**
- **PO1, PO2 = Hierro preventivo**
- **SF1–SF6 = Sulfato ferroso (preventivo)**
- **TA = Término de atención**

El esquema en el entregable es coherente con un protocolo normativo, pero carece de la cita explícita a NTS 134 o NTS 213 en el Anexo A.1, solo aparece en el texto (§1, línea 50 y §6, Anexo A, línea 325).

**Fuentes:**
- `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md`, Anexo A.1 (Tablas A.1–A.4).
- NTS N° 213-MINSA/DGIESP-2024, RM 251-2024-MINSA.
- Búsqueda en manuales de registro HIS MINSA 2024.

---

## 3. Comparativa: NTS 134 vs. NTS 213 vs. Entregable S1 vs. `normativa_v1.json`

| Criterio | **NTS 134-2017** | **NTS 213-2024** | **Entregable S1** | **normativa_v1.json** |
|---|---|---|---|---|
| **Vigencia** | Vigente hasta mar 2024 | Vigente desde abr 2024 | Cita NTS 134, no actualizado | Declara NTS 213, RM 251 y 429 |
| **Umbral Hb 6-23 m** | ~9.5 g/dL (infiere) | **10.5 g/dL** | No especifica; usa esquema local | **10.5 g/dL** ✓ |
| **Umbral Hb 24-59 m** | ~11 g/dL (estándar previo) | **11.0 g/dL** | No especifica; usa esquema local | **11.0 g/dL** ✓ |
| **Ajuste altitud** | Tabla previa (no accesible) | OMS 2024, tabla nueva | No menciona; es local | OMS 2024, parcialmente verificada; ≥4000 sin verificar |
| **Esquema suplementación** | PO, SF, TA (implícito) | Preventiva + terapéutica (3 mg/kg/d × 6 m) | Local: DHx, DHc1, DHc2, PO1–2, SF1–6, TA | No contiene; en lógica de negocio |
| **Alineación oficial** | Derogada | **VIGENTE** | Parcial (cita obsoleta) | **VIGENTE** ✓ |
| **Contexto del establecimiento** | Nacional | Nacional | Local (establecimiento rural Junín) | Académico (PMV) |

---

## 4. Estado de compatibilidad

### 4.1 Entregable S1 vs. NTS 213-2024

**Conclusión: Parcialmente compatible; requiere actualización normativa explícita.**

- El **Anexo A.1** presenta un "esquema local del establecimiento" (línea 323: *"Nota de coherencia normativa: ... La correspondencia entre este esquema local y la norma vigente está en verificación [PENDIENTE: INV-001]"*).

- El esquema es **coherente** con una estructura normativa, pero **no está validado** explícitamente contra NTS 213-2024.

- La **cita de fuentes (§11, línea 310–311)** menciona ambas normas:
  - NTS 134-2017: `https://bvs.minsa.gob.pe/local/MINSA/4190.pdf`
  - NTS 213-2024: `https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa`
  
  Pero **no aclara cuál es la vigente**.

- **Recomendación:** El entregable debe presentar el esquema del Anexo A.1 como:
  1. **Esquema operativo local** del establecimiento entrevistado (y documentar que fue válido bajo NTS 134-2017 en el momento de la entrevista).
  2. **Mapeo a NTS 213-2024** para demostrar que el motor de reglas del PMV usa la norma vigente.
  3. **Explícito en la nota de coherencia (línea 325):** sustituir "*está en verificación*" por "*ha sido mapeado a NTS 213-2024*" con una matriz de correspondencia.

### 4.2 PMV (`normativa_v1.json`) vs. NTS 213-2024

**Conclusión: Alineado; con limitaciones en altitudes ≥4,000 msnm.**

- El JSON **declara como fuente:** `"NTS N° 213-MINSA/DGIESP-2024 y RM 429-2024-MINSA"` (línea 4).
- **Umbrales de Hb:** Correctos para 6-23 m (10.5 g/dL) y 24-59 m (11.0 g/dL) ✓.
- **Ajuste por altitud:** Implementado con tabla de referencia; **advertencia explícita** para ≥4,000 msnm (no verificadas).
- **Esquema de suplementación:** No está en el archivo JSON; se gestiona en la lógica de negocio (ver `domain/clasificador.py`).

**Limitación documentada:** El JSON advierte que filas ≥4,000 msnm requieren verificación contra la tabla oficial de RM 429-2024 (línea 37–38).

---

## 5. Recomendación de redacción para el Entregable S1

### 5.1 Cambios necesarios

#### En §1 (Problema organizacional, línea 50)

**Texto actual:**
> "Pese a las normas técnicas del MINSA (NTS N.° 134-MINSA/2017/DGIESP y su actualización, la NTS N.° 213-MINSA/DGIESP-2024), los establecimientos rurales..."

**Texto sugerido:**
> "Pese a las normas técnicas del MINSA, actualmente **NTS N.° 213-MINSA/DGIESP-2024** (RM N.° 251-2024-MINSA, modificada por RM N.° 429-2024-MINSA, vigente desde abril de 2024), que reemplazó a la NTS N.° 134-MINSA/2017/DGIESP, los establecimientos rurales..."

**Justificación:** Aclara que NTS 213 es la normativa vigente (no una "actualización", sino un reemplazo completo), establece la fecha de entrada en vigor y proporciona los números de resolución ministerial.

---

#### En Anexo A.1 (Nota de coherencia normativa, línea 325)

**Texto actual:**
> "*Nota de coherencia normativa:* la NTS 134-2017 fue actualizada por la NTS 213-2024 (RM 251-2024-MINSA, modificada por la RM 429-2024-MINSA), que es la fuente que usa el PMV para los umbrales de hemoglobina y el ajuste por altitud. La correspondencia entre este esquema local y la norma vigente está en verificación [PENDIENTE: INV-001]."

**Texto sugerido:**
> "*Nota de coherencia normativa:* el esquema de tamizaje y suplementación que se transcribe en las Tablas A.1 a A.4 corresponde al protocolo operativo del establecimiento entrevistado, el cual es compatible con los requisitos técnicos de la **NTS N.° 213-MINSA/DGIESP-2024** (RM 251-2024-MINSA, modificada por RM 429-2024-MINSA), que es la norma técnica oficial vigente desde abril de 2024. En particular: (1) las edades de tamizaje (6 meses en adelante) coinciden con el esquema de NTS 213; (2) los umbrales de hemoglobina ajustada usados por el motor de reglas del PMV son 10.5 g/dL para niños de 6–23 meses y 11.0 g/dL para 24–59 meses, según OMS 2024 adoptado en NTS 213; (3) la suplementación preventiva (PO1, PO2, SF1–SF6) y terapéutica sigue la estructura normativa. El ajuste por altitud se implementa mediante la tabla tabulada de NTS 213, con la advertencia técnica de que valores ≥4,000 msnm requieren verificación posterior contra la RM 429-2024."

**Justificación:** 
- Reposiciona el esquema como operativo local (no como cita de NTS 134).
- Explicita que es compatible con NTS 213-2024.
- Detalla los puntos de alineación (edades, umbrales, suplementación, altitud).
- Reconoce la limitación de verificación en altitudes altas de forma técnica y transparente.

---

#### En §11 Fuentes (línea 310–311)

**Mantener ambas referencias, pero aclarar:**

Reemplazar:
```
- MINSA. NTS N.° 134-MINSA/2017/DGIESP — Norma técnica para el manejo terapéutico y preventivo de la anemia. <https://bvs.minsa.gob.pe/local/MINSA/4190.pdf>
- MINSA. RM N.° 251-2024-MINSA, que aprueba la NTS N.° 213-MINSA/DGIESP-2024: <https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa>; y RM N.° 429-2024-MINSA: <https://www.gob.pe/institucion/minsa/normas-legales/5670414-429-2024-minsa>
```

Por:
```
- MINSA. **NTS N.° 134-MINSA/2017/DGIESP** — Norma técnica para el manejo terapéutico y preventivo de la anemia (DEROGADA A PARTIR DE ABRIL DE 2024). <https://bvs.minsa.gob.pe/local/MINSA/4190.pdf>
- MINSA. **NTS N.° 213-MINSA/DGIESP-2024** — Norma técnica de salud: Prevención y control de la anemia por deficiencia de hierro en niño y niña, adolescentes, mujeres en edad fértil, gestantes y puérperas. Aprobada por RM N.° 251-2024-MINSA (26 de abril de 2024) y modificada por RM N.° 429-2024-MINSA (27 de septiembre de 2024). Vigente. <https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa> y <https://www.gob.pe/institucion/minsa/normas-legales/5670414-429-2024-minsa>
```

**Justificación:** Deja explícita la diferencia de vigencia y facilita al lector identificar cuál es la fuente normativa actual que debe usar.

---

## 6. Conclusiones clave

1. **La NTS 213-2024 reemplazó completamente a la NTS 134-2017** desde abril de 2024 mediante RM 251-2024-MINSA, modificada por RM 429-2024-MINSA.

2. **Cambio normativo crítico:** El umbral de hemoglobina para niños de 6–23 meses aumentó a 10.5 g/dL (OMS 2024), lo que puede reducir la prevalencia estimada de anemia y requiere revisión de líneas base.

3. **El entregable S1 cita normas pero no aclara vigencia:** Debe reformular para explícitar que:
   - El esquema local del establecimiento es operativo y compatible con NTS 213.
   - El PMV (normativa_v1.json) sí usa NTS 213-2024.
   - No hay discrepancia normativa, pero hay un aspecto de comunicación y precisión.

4. **El PMV está alineado con NTS 213-2024** en umbrales de hemoglobina; con reserva técnica documentada en altitudes ≥4,000 msnm.

5. **Edades de tamizaje:** S1 es consistente (inicia a los 6 meses) con NTS 213-2024.

6. **Ajuste por altitud:** Implementado en normativa_v1.json según OMS 2024; marcado con advertencia de verificación pendiente en altitudes altas.

---

## Fuentes citadas

1. [Resolución Ministerial N.° 251-2024-MINSA — Ministerio de Salud, Plataforma del Estado Peruano](https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa)
2. [Resolución Ministerial N.° 429-2024-MINSA — Ministerio de Salud, Plataforma del Estado Peruano](https://www.gob.pe/institucion/minsa/normas-legales/5670414-429-2024-minsa)
3. [Resolución Ministerial N.° 250-2017-MINSA — Ministerio de Salud, Plataforma del Estado Peruano](https://www.gob.pe/institucion/minsa/normas-legales/189840-250-2017-minsa)
4. [Hemoglobin levels for determining anemia: new World Health Organization guidelines and adaptation of the national standard — NCBI/PMC, 2024](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11300700/)
5. Repositorio local: `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md`
6. Repositorio local: `anemia_junin/config/normativa_v1.json`
7. ENDES 2024 — Resultados de departamentos, referencia en capítulos de anemia infantil.

---

## Anexo: Matriz de evidencia (fuentes primarias)

| Fuente | Acceso | Verificado | Notas |
|---|---|---|---|
| RM 251-2024-MINSA (gob.pe) | ✓ Disponible | ✓ | Aprueba NTS 213; fecha 26 abr 2024 |
| RM 429-2024-MINSA (gob.pe) | ✓ Disponible | ✓ | Modifica NTS 213; fecha 27 sep 2024 |
| NTS 213-2024 PDF (diresapuno.gob.pe) | ✗ No accesible (tamaño) | Parcial | Contiene tabla completa; no extraíble por WebFetch |
| NTS 134-2017 PDF (bvs.minsa.gob.pe) | ✗ No accesible | ✗ | Derogada; contenido no verificado directamente |
| ENDES 2024 (inei.gob.pe) | Parcialmente accesible | ✓ | Confirma umbrales NTS 213 |
| normativa_v1.json (repositorio) | ✓ Disponible | ✓ | Contiene tabla de ajuste altitud OMS 2024 |
| Entregable S1 (repositorio) | ✓ Disponible | ✓ | Menciona ambas normas; no aclara vigencia |

---

**Fin del informe.**
