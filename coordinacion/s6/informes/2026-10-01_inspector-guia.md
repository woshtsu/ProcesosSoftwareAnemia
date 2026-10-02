# Informe de trabajo: inspector-guia, S6-06

- **Fecha:** 2026-10-01
- **Rama:** `feature/s6-integrador-final` (commit base 807d3dc; trabajo sin confirmar)
- **Salidas:** `coordinacion/s6/INSPECCION_S6.md`, `coordinacion/s6/PASOS_MANUALES.md`; tablero actualizado (S6-06 en revisión; nuevas tareas S6-13 a S6-20).

## Resultado

- **Veredicto: NO LISTO PARA ENTREGAR.**
- Global: 42 CUMPLE, 28 PARCIAL, 12 NO CUMPLE y 9 MANUAL de 91 (46,2 % CUMPLE; 61,5 % ponderado).
- Por bloque (CUMPLE / total): A 2/5; B 2/4; C 16/30; D 18/36; E 2/5; F 0/8; G 2/3.

## Qué se inspeccionó

Informe completo (679 líneas) y su checklist; `Presentacion_Integrador.md`; `GUION_EXPOSICION.md`; PPTX con python-pptx (7 diapositivas, 16 imágenes, notas de 156 a 254 palabras por diapositiva); 19 PNG `50` a `68`; README raíz y de `pmv_fastapi`; `.github/workflows/ci.yml`; tag con `git ls-remote`; enlaces locales (0 rotos reales); marcadores prohibidos (0); resumen de 285 palabras.

## Hallazgos clave

- 12 hallazgos en figuras (E-01 a E-12); los principales: «77/77 en verde» en las figuras 59 y 64 (solo 73 reproducidas); tablero con 21/21 SP y barras que suman 16; burnup que termina en 16 con rótulo «21 SP» y período «01-28 Sep» cuando todos los commits del tag son del 30/09; matriz de factores con niveles distintos a la Tabla 7; ciclo de vida con alternativas y «Scrum 3/5» que contradicen las Tablas 8 y 9; hojas de ruta e AS-IS/TO-BE con incrementos distintos a las Tablas 5, 15 y 16.
- La mezcla «p95 310 → 58» con «reporte 2 200 → 74» no se confirmó: aparecen siempre rotuladas por separado.
- Faltan PDF/DOCX del informe y PDF de las diapositivas; `.github/` y los entregables S6 no están confirmados en git; README raíz desactualizado respecto del CI; banner de PlantUML y glifos vacíos en las figuras.

## Limitaciones

No se renderizó el PPTX (sin PowerPoint/LibreOffice disponible en la inspección): la legibilidad se estimó por tamaño de imagen en pulgadas y por lectura de los PNG. Se recomienda una revisión visual a pantalla completa (PASOS_MANUALES 12).
