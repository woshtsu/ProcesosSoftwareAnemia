# T-026 — Checklist final de la revisión integral

- **Revisor:** Jean Piero Huamani Rodriguez (`revisor-documental`), con Claude como asistente · **Fecha:** 15/11/2026 · **Rama:** `docs/t026-revision`
- **Detalle:** [`HALLAZGOS.md`](HALLAZGOS.md) (118 hallazgos con capturas antes y después), [`requisitos/`](requisitos/) (cotejo `R-xx` por semana) y [`CRITERIOS.md`](CRITERIOS.md) (decisiones D-01 a D-10).
- **Visto bueno ✅** solo si se cumplen todos los requisitos aplicables y no queda ningún hallazgo abierto. Un pendiente justificado cuenta como abierto.
- **Verificación independiente:** un verificador que no participó en las correcciones comprobó los 82 hallazgos cerrados contra la fuente y el exportado; encontró 2 fallos (H-065 y H-105), que se corrigieron y se volvieron a comprobar.

## Por semana

| Semana | Requisitos cumplidos / total (inicio → fin) | Hallazgos abiertos / cerrados | Abiertos (pendientes justificados) | Visto bueno |
| --- | --- | --- | --- | --- |
| S1 | 15/18 → **16/18** | 3 / 4 | H-005, H-006, H-007 | ❌ |
| S2 | 24/28 → **26/28** | 0 / 5 | — (R-05 y S-2 siguen parciales por decisión del equipo) | ❌ |
| S3-4 | 49/53 → **49/53** | 3 / 5 | H-045, H-046, H-047 | ❌ |
| S5 | 18/28 → **22/28** | 2 / 7 | H-066, H-067 | ❌ |
| S6 | 25/39 (borrador de develop) → **37/39** (cierre del 02/10 restaurado) | 2 / 6 | H-086, H-087 | ❌ |
| S9 | 21/26 → **24/26** | 3 / 12 | H-100 (dato `num_doc` en `pmv_fastapi/`), H-113, H-114 | ❌ |
| S10 | 16/37 → **20/37** | 4 / 7 | H-126, H-127, H-128, H-129 | ❌ |
| S11 (incluye feria) | 24/35 → **26/35** | 7 / 10 | H-150 a H-156 | ❌ |
| S12 | 27/41 → **29/41** | 4 / 9 | H-166, H-170, H-171, H-173 | ❌ |
| S13 (lab 30, PDCA 5 aplicables, sílabo 2) | 18/37 → **23/37** | 6 / 15 | H-181, H-194, H-195, H-196, H-199, H-200 (el dominio 4 del PDCA quedó «Verificado» el 16/11 con la PR #36) | ❌ |
| Transversales | — | 1 / 3 | H-220 (rúbrica S16 vacía en `guias/`) | ❌ |
| S14 y S16 (análisis de brechas, sin entregable) | S14 cubre 15/43 y S16 2/15 | — | Ver [`requisitos/S14-S16.md`](requisitos/S14-S16.md) | n/a |
| **Total S1-S13** | **237/342 (69,3 %) → 272/342 (79,5 %)** | **35 / 83** | | |

## Por exportado

| Exportado | Fuente | Coherente con la fuente | Hallazgos abiertos / cerrados | Visto bueno |
| --- | --- | --- | --- | --- |
| `exportados/semana-05/Entregable_Semana5_Anemia_Junin.pdf` y `.docx` (nuevos) | `entregables/semana-05/…md` | Sí | 0 / 1 (H-065) | ✅ |
| `exportados/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf` | Original histórico de la Actividad 5 | No aplica: se declara histórico en `exportados/README.md` | 0 / 1 (H-222) | ✅ |
| `exportados/semana-06-integrador/Informe_Integrador_Anemia_Junin.pdf` y `.docx` | `entregables/semana-06-integrador/…md` | Sí (regenerados con `exportar_s6.py`) | 0 / 5 (H-080 a H-084) | ✅ |
| `exportados/semana-06-integrador/Presentacion_Integrador_Anemia_Junin.pptx` y `.pdf` | `presentacion/Presentacion_Integrador.md` | Sí (7 diapositivas, 7:00) | 0 / 1 (H-081) | ✅ |
| `exportados/semana-09/Entregable_Semana9_Anemia_Junin.pdf` y `.docx` | `entregables/semana-09/…md` | Sí | 0 / 5 (H-101 a H-103, H-105, H-111) | ✅ |
| `exportados/semana-11/Entregable_Semana11_Anemia_Junin.pdf` | `entregables/semana-11/…md` | Sí (antes era la versión del 30/10) | 0 / 1 (H-140) | ✅ |
| `exportados/feria/Proyecto_Feria_Anemia_Junin.pdf` | `entregables/semana-11/feria/…md` | Sí | 0 / 2 (H-144, H-145) | ✅ |
| `exportados/semana-12/Informe_Integrador_S12_Anemia_Junin.pdf` y `.docx` (nuevos) | `entregables/semana-12/…md` | Sí | 0 / 1 (H-160) | ✅ |
| `exportados/semana-12/Correcciones_S12_observaciones_docente.docx` | `entregables/semana-12/correcciones/…md` | Sí | 0 / 1 (H-161) | ✅ |
| `exportados/semana-13/Porras-Auqui-Huamani-PDCA-mejora.pdf` | `entregables/semana-13/pdca/PDCA_gestion_configuracion.html` | Sí (regenerado con el dominio 4 «Verificado», E-22 y E-23) | 0 / 1 (H-223) | ✅ |
| `exportados/semana-13/Porras-Auqui-Huamani-Informe-SCM-Lab13.pdf` | `entregables/semana-13/laboratorio-scm/Informe_SCM_Lab13.html` | Sí (regenerado con las Figuras 15a y 15b) | 0 / 1 (H-223) | ✅ |
| `exportados/semana-13/Informe_Integrador_S13_Anemia_Junin.pdf` y `.docx` | `entregables/semana-13/…md` | Sí | 0 / 3 (H-183, H-184, H-190) | ✅ |
| **Total exportados** | | **12/12 coherentes** | | **12/12 ✅** |

## Porcentaje global

- Requisitos de las guías y del sílabo (S1-S13): **79,5 %** (272 de 342; al inicio 69,3 %).
- Exportados con visto bueno: **12 de 12** (100 %).
- **Global (requisitos + exportados): 80,2 %** (284 de 354).
- Hallazgos: 118 en total; **83 cerrados** (70,3 %) y **35 pendientes justificados**.

## Qué falta para el 100 %

1. **Paso final del dominio 4: hecho.** La PR #35 se integró sin aprobación (H-223); la PR #36 fue aprobada por Porras V. el 16/11 a las 17:13 e integrada con esa aprobación. El PDCA (dominio 4 «Verificado», E-22 y E-23) y el informe del laboratorio 13 (Figuras 15a y 15b) se actualizaron y sus PDF se regeneraron en la PR `docs/t026-dominio4-evidencia`.
2. **Decisiones del Leader:** columna `num_doc` del dataset en `pmv_fastapi/datos/` (H-100), regla `required_status_checks` en el ruleset (H-181), `--cov-fail-under=80` en `ci.yml` (H-199), adjuntos de las releases (H-195), rúbrica S16 vacía en `guias/` (H-220) y, si se quiere, reescribir el historial de Git para retirar los correos y la imagen PROD_05 originales.
3. **Trabajo del equipo:** mediciones que no se hicieron (S10: WCAG 1.1.1, 500 usuarios, vulnerabilidad Alta abierta; S9: SUS e impacto), recorte y locución del video S12 (H-166), acta H1 y horas reales de S3-4, registro de defectos de S5, captura de GitHub Actions para S6, elementos de S11 (matriz de puertos, convención de commits, PDCA, bibliografía), criterio 4 de la autoevaluación del laboratorio (H-194).
4. **Confirmaciones del docente:** «proyecto aplicado en la empresa» y extensión de S1, modalidad, NRC/sección de la carátula S12, evaluación del proceso en S10, rúbricas del aula virtual.

**Revisión al 100 %: no.** Todo lo que podía corregirse sin decisión del equipo, del docente o del Leader está corregido y verificado; el paso final del dominio 4 está hecho y quedan 35 pendientes justificados que dependen del equipo, del docente o del Leader.
