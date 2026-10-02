# Informe recursos-visuales, 2026-10-02: variantes 53/59/61 y pies de figura

Creados (fuente .py, PNG a 200 dpi, SVG): `53_s6_c4_contenedores_fastapi_16x9` (11 x 6,19 in), `59_s6_piramide_pruebas_media` y `61_s6_carga_p95_media` (5,4 x 6 in). Texto de 16 pt o más; cifras idénticas a las originales (62/11/4 = 77, 73 reproducidas, carga aparte; p95 310 → 58 ms, 39,56 req/s, 0 % de errores). La 53 está en matplotlib (no PlantUML) para controlar el lienzo; se omiten las etiquetas de las flechas del original.

Pies: 59 (§3.3, Tablas 23 y 24), 61 (Tabla 26), 62 (Tablas 14, 23, 24 y 26), 63 (Tablas 14 y 16), 65 (Tabla 29), 66 (Tabla 21), 67 (Tabla 7). Originales regenerados; la 62 también perdió «scripts/cargar_datos_prueba.py».

Presentación: solo cambiaron las rutas de imagen de D3 y D4; PPTX regenerado: 7 diapositivas, 29 a 38 palabras visibles.

Legibilidad (PowerPoint COM sobre copia, 1920x1080): D3 legible, aunque la figura ocupa 63,6 % del ancho y el texto de las cajas queda de unos 15 px; D4 legible (cifras y etiquetas), cada figura ocupa solo 27 % del ancho por el límite `h:340`.
Sugerencia (no aplicada, se pidió cambiar solo rutas): subir `h:` a ~480 en D3 y ~420 en D4 para ampliar las figuras.

## Ampliación (aplicación de la sugerencia)
Con el texto inferior de D3 y D4 el alto útil es de ~4,6 in, así que `h:` por sí solo no basta; se rehicieron los lienzos: 53 `_16x9` a 11 x 4,3 in (panorámico), 59 `_media` a 5,4 x 4 in y 61 `_media` a 5,9 x 4 in (mismas cifras, texto de 16 pt o más). Md: D3 `h:480`; D4 `h:420`. Resultado en el PPTX: D3 89,2 % del ancho; D4 41,3 % (pirámide) y 42,2 % (carga); 7 diapositivas, 29 a 38 palabras. Render COM: todo se lee.
