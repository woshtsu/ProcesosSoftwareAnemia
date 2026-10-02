# Informe de trabajo: inspector-guia, S6-06 (reinspección, versión 2)

- **Fecha:** 2026-10-01
- **Rama y commit:** `feature/s6-integrador-final`, `fdc50c5` (árbol limpio, sin push)
- **Salidas:** `coordinacion/s6/INSPECCION_S6.md` (v2), `coordinacion/s6/PASOS_MANUALES.md` (actualizado), `coordinacion/s6/TABLERO_S6.md` (S6-06 EN REVISIÓN; nuevas S6-21 a S6-24). No se tocó ningún entregable, figura ni código.

## Resultado

- **Veredicto: NO LISTO PARA ENTREGAR.**
- v1 -> v2: 42 -> 61 CUMPLE de 91 (46,2 % -> 67,0 %; ponderado 61,5 % -> 75,3 %). Quedan 15 PARCIAL, 0 NO CUMPLE (eran 12) y 15 MANUAL.
- Por bloque (CUMPLE/total, v1 -> v2): A 2/5 -> 3/5; B 2/4 -> 2/4; C 16/30 -> 25/30; D 18/36 -> 25/36; E 2/5 -> 3/5; F 0/8 -> 1/8; G 2/3 -> 2/3.
- E-01 a E-12: los 12 están resueltos (las 19 figuras se leyeron como imagen). Residuo del E-12: la figura 58 es compacta pero aún pequeña.
- Cifras cruzadas (informe, diapositivas, notas, guion y figuras) contra DATOS §17: sin discrepancias.

## Verificaciones nuevas

- **PPTX renderizado con PowerPoint COM sobre una copia** (sin tocar el original): se vieron las 7 diapositivas. 7 diapositivas, 40/29/34/38/38/34/39 palabras visibles, imágenes y notas OK.
- **Hallazgo principal (N-01):** en D1, D3, D4, D5 y D7 las figuras quedan en 3 a 6 pt equivalentes, con grandes zonas vacías; D2 y D6 son aceptables. El PDF de las diapositivas (7 páginas, exportado con PowerPoint) hereda el defecto.
- **PDF del informe:** 50 páginas (Letter), todas las secciones, 0 marcadores prohibidos, 18 `COMPLETAR` (datos humanos). **Figuras: están embebidas las 35** (rótulos Figura 1 a 35 presentes y una imagen por figura). **No son 12:** la afirmación del conversor es incorrecta. Hay 36 imágenes porque la captura 07 se imprime duplicada (págs. 43 y 44, mismo objeto) (N-14). El DOCX tiene 35 imágenes y 32 tablas.

## Errores restantes corregibles por agentes (priorizados)

1. **N-01** (disenador-diapositivas con recursos-visuales): `Presentacion_Integrador.md` l.37, 57, 77, 97, 118 y 161 y `generar_presentacion.py`. Una figura dominante por diapositiva a >= 80 % del ancho; versiones horizontales de la 50 y de la 64; D4 con 59 + 61; D5 solo el collage; D7 sin la 68 o en horizontal; regenerar PPTX y PDF.
2. **N-02:** fig. 58 en dos filas (unos 5,5 pt en A4).
3. **N-03:** D5 l.122 dice «ver anexo» y no existe ningún anexo del acta.
4. **N-04:** «Ingeniero» para Tania en `GUION_EXPOSICION.md` l.13 y 15 y en `Presentacion_Integrador.md` l.84 (el informe y el README dicen «Ingeniera»).
5. **N-05:** rutas internas `coordinacion/s6/...` y `pmv_fastapi/.github/...` dentro de las figuras 51, 52, 53, 55, 58 y 64.
6. **N-06:** la fig. 64 no muestra la matriz de 8 columnas ni una fila ejemplo (R-71) y su layout es confuso.
7. **N-07:** el título de la fig. 60 mezcla 548 reproducidas con porcentajes por módulo del tag (641).
8. **N-08:** informe l.510 (Tabla 24) cita README y tag como evidencia de «reproducido».
9. **N-09:** guion l.54 «hito H1 cumplido con dos días de retraso»; nota C-10 interna en las notas de D6.
10. **N-10, N-11:** fig. 52 con líneas discontinuas para lo futuro; archivar los dos anexos viejos del 25/09.
11. **N-12, N-14 (conversor-entregas):** reexportar al final con título de metadatos, A4, portada ajustada y la captura 07 sin duplicar.

## Lo que queda MANUAL (15 requisitos)

Portada (códigos, docente, fecha, mapeo de roles); acta o declaración de aceptación y Product Owner; horas reales; motivo Flask -> FastAPI; SonarCloud; push y CI en verde; staging, `/api/salud` y E2E; duración del video; decisión del tag; ensayo de 7 min y defensa individual; reexportación final. Pasos 1 a 18 en `PASOS_MANUALES.md`.

## Nota estimada (orientativa)

- Informe /8 tal como está: **6,9** (rango 6,5 a 7,25).
- Total /20: unos **15** hoy, **16** con las correcciones de agentes y unos **18** (17 a 19,5) si además se completan los pasos manuales. Con los manuales, el informe sube a unos 7,7.

## Limitaciones

El DOCX no se pudo renderizar (sin Word); las 7 diapositivas sí se vieron como imagen. No se ejecutó ningún comando de git que modifique el repositorio.
