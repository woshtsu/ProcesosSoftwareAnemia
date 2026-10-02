# Informe S6-04: diseñador de diapositivas

- **Fecha:** 2026-10-01
- **Rama:** `feature/s6-integrador-final`
- **Estado:** EN REVISIÓN

## Producido

| Producto | Ruta |
| --- | --- |
| Fuente Marp (7 diapositivas, notas con tiempos) | `entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md` |
| Guion de 7:00 y preguntas de defensa | `entregables/semana-06-integrador/presentacion/GUION_EXPOSICION.md` |
| Script reproducible (python-pptx) | `entregables/semana-06-integrador/presentacion/generar_presentacion.py` |
| PPTX (7 diapositivas, con notas) | `exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pptx` |

## Diapositivas

1. Del triple registro al expediente único (50 + indicador 3 → 1, 1:05, Porras V.)
2. Tailoring: híbrido, no Cascada (51 + 67, 4,75 vs. 3,85 vs. 2,95, rechazo de Cascada 8/30 y Scrum puro, 1:05, Porras V.)
3. Arquitectura: monolito hexagonal + API REST (53 C4 N2 + 66 ADR/NFR, 1:05, Auqui H.)
4. Pruebas: evidencia objetiva de calidad (59 + 60 + 61, 1:05, Huamani R.)
5. Demo: HU-01 a HU-05 operativas (65 collage + 58 despliegue, 1:25, Auqui H.)
6. Tablero: proceso, producto y valor (62 + 63, 0:40, Huamani R.)
7. Trazabilidad integral y cierre (64 + 68, 0:35, Porras V.)

## Requisitos

R-40 a R-43, R-45 a R-48, R-50 a R-53, R-55 a R-58, R-60 a R-62, R-65 a R-68 y R-70 a R-73 cubiertos con contenido y figura. Pitches R-44, R-49, R-54, R-59, R-64, R-69 y R-74 en las notas, reducidos al 70 % (R-90, C-06; suma 7:00). R-75: exactamente 7 diapositivas verificadas con python-pptx; menos de 40 palabras visibles por diapositiva, texto de 20 pt o más.

Parciales o pendientes:

- R-63 (aceptación con el usuario final): no hay acta; consta como [COMPLETAR] visible en la diapositiva 5.
- R-60 (video de 2 min): se muestra el collage y se cita `demo_pmv.mp4`; el video no se incrusta (duración sin verificar).
- R-62: staging con Docker Compose; no hay nube (declarado).
- PDF: pendiente (marp-cli requiere descargar paquetes npm).
- Revisión visual del PPTX no hecha (no hay LibreOffice ni PowerPoint en el entorno); solo se comprobó que las imágenes caben en la diapositiva.

## Imágenes

Todas existían al generar: 50, 51, 53, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67 y 68 (PNG en `diagramas/png/`). No quedó ninguna pendiente. No se creó ninguna VIS nueva.

## Regenerar

```bash
herramientas/.venv/Scripts/python entregables/semana-06-integrador/presentacion/generar_presentacion.py
```

Se instaló `python-pptx` en `herramientas/.venv` (ya ignorado por `.gitignore`). Alternativa con Marp (PDF; descarga paquetes): `npx @marp-team/marp-cli Presentacion_Integrador.md --pdf --allow-local-files`.

## Observaciones

- 77 pruebas son las declaradas en el tag; el 01/10 se reprodujeron 73 (62 + 11). Está dicho en la diapositiva 4 y en las notas.
- Los SP del tablero del PMV difieren de S3-4 (C-10): se usan 13 + 8 = 21 de S3-4.
- La asignación de expositores es una propuesta [COMPLETAR].
- El diseño `herramientas/conversion/generar_presentacion.py` del agente se sustituyó por la ruta indicada en la tarea (carpeta `presentacion/`); `herramientas/README.md` debe recoger la línea (sincronizador).
- Sugerencia: crear el PDF con marp-cli cuando el usuario lo autorice.

## [COMPLETAR] abiertos

Aceptación del usuario final (diapositiva 5), duración del video, captura de CI en verde (solo guion), reparto definitivo de expositores.
