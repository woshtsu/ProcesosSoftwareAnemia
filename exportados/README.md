# Exportados

PDF y DOCX generados por el agente `conversor-entregas` a partir de los `.md` vigentes de `entregables/`, listos para subir al aula virtual.

Estructura: `exportados/semana-XX/<NombreEntregable>.pdf|.docx` (mismo nombre base que el `.md`). Son derivados: ante cualquier diferencia manda el `.md`.

## Índice (revisado en T-026, 15/11/2026)

| Semana | Exportado | Fuente | Cómo se regenera |
| --- | --- | --- | --- |
| S5 | `semana-05/Entregable_Semana5_Anemia_Junin.pdf` y `.docx` | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` | `.claude/herramientas/conversion/exportar_md.py` |
| S5 | `semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf` | — (documento original de la Actividad 5, entregado por el equipo) | No se regenera: es histórico y no coincide con el `.md` vigente (49 pruebas y `unittest` frente a 266 pruebas y `pytest`). |
| S6 | `semana-06-integrador/Informe_Integrador_Anemia_Junin.pdf` y `.docx` | `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` | `.claude/herramientas/conversion/exportar_s6.py` |
| S6 | `semana-06-integrador/Presentacion_Integrador_Anemia_Junin.pptx` y `.pdf` | `entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md` | `entregables/semana-06-integrador/presentacion/generar_presentacion.py` |
| S9 | `semana-09/Entregable_Semana9_Anemia_Junin.pdf` y `.docx` | `entregables/semana-09/Entregable_Semana9_Anemia_Junin.md` | `.claude/herramientas/conversion/exportar_s9.py` |
| S11 | `semana-11/Entregable_Semana11_Anemia_Junin.pdf` | `entregables/semana-11/Entregable_Semana11_Anemia_Junin.md` | `.claude/herramientas/conversion/exportar_s11.py` |
| Feria | `feria/Proyecto_Feria_Anemia_Junin.pdf` | `entregables/semana-11/feria/Proyecto_Feria_Anemia_Junin.md` | `.claude/herramientas/conversion/exportar_feria.py` |
| S12 | `semana-12/Informe_Integrador_S12_Anemia_Junin.pdf` y `.docx` | `entregables/semana-12/Informe_Integrador_S12_Anemia_Junin.md` | `.claude/herramientas/conversion/exportar_md.py` |
| S12 | `semana-12/Correcciones_S12_observaciones_docente.docx` | `entregables/semana-12/correcciones/Correcciones_S12_observaciones_docente.md` | `exportar_md.py … --solo-docx` |
| S13 | `semana-13/Porras-Auqui-Huamani-PDCA-mejora.pdf` | `entregables/semana-13/pdca/PDCA_gestion_configuracion.html` | `entregables/semana-13/exportar_pdf_s13.py pdca` |
| S13 | `semana-13/Porras-Auqui-Huamani-Informe-SCM-Lab13.pdf` | `entregables/semana-13/laboratorio-scm/Informe_SCM_Lab13.html` | `entregables/semana-13/exportar_pdf_s13.py scm` |
| S13 | `semana-13/Informe_Integrador_S13_Anemia_Junin.docx` y `.pdf` | `entregables/semana-13/Informe_Integrador_S13_Anemia_Junin.md` | El DOCX se generó fuera del repositorio; las correcciones posteriores se aplican al `.md` y al `.docx`, y el PDF se obtiene del DOCX con LibreOffice (`soffice --headless --convert-to pdf`). |

S1, S2, S3-4 y S10 no tienen exportado en el repositorio. Las versiones anteriores de cada exportado quedan en el historial de Git.
