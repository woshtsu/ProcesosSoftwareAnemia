# Informe del sincronizador: S6-25, control de calidad del PDF y cierre de la ronda N-01 a N-14

- **Fecha:** 2026-10-02
- **Rama:** `feature/s6-integrador-final` (commit local, sin push)
- **Entradas:** `exportados/semana-06/*.pdf`, `herramientas/conversion/exportar_s6.py`, informes del 2026-10-02 en `coordinacion/s6/informes/`, script temporal del conversor (`%TEMP%\regen_pdf_pptx.ps1`)

## 1. Control de calidad del PDF del informe

Método: se renderizaron con pypdfium2 (en `herramientas/.venv`) la portada, el índice y las páginas con figuras grandes (C4 16 a 18, paquetes y secuencia 19 y 20, pirámide 22, capturas 26 a 33, matriz 30 y figura 34, hoja de ruta 35) y se revisaron como imagen. Además, se midió en todas las páginas la fracción de altura útil ocupada (filas con tinta entre márgenes de 2,5 cm).

| Aspecto | Antes (CSS del conversor) | Después (S6-25) |
| --- | --- | --- |
| Páginas | 75 | **51** |
| Formato y metadatos | A4, título correcto | A4 (595 x 842 pt), título correcto |
| Imágenes (pypdf) | 35 | 35 (la captura 07 aparece una sola vez) |
| `[COMPLETAR]` en el PDF | 25 | 25 (todos del MD fuente; paso manual) |
| Páginas con < 30 % de su altura ocupada | 11; tres de ellas solo con el rótulo «Tabla 5/28/30» y el resto en blanco | 7; todas son fin de sección o el hueco antes de una figura alta que no cabe |
| Legibilidad de figuras | C4 N1 a N3 a unos 11 cm de ancho, ilegibles sin zoom; texto limitado a 36em de ancho | Figuras al ancho útil completo (16 cm), altura máxima de 16 cm; C4, matriz, pirámide y secuencia legibles a 100 % |
| Tablas | La Tabla 30 (8 columnas) se **recortaba** a 4 columnas; otras tablas anchas también perdían columnas | Las 8 columnas visibles, con ajuste de palabras |

Causas encontradas:

1. `img { max-height: 8cm }` reducía las figuras anchas y tampoco evitaba los huecos.
2. `table { page-break-inside: avoid }` empujaba cada tabla larga a la página siguiente y dejaba su rótulo solo.
3. La plantilla HTML de pandoc limita `body` a 36em y define `table { display: block; overflow-x: auto }`; al imprimir, eso recorta las columnas de la derecha.

Cambios en `herramientas/conversion/exportar_s6.py` (solo el CSS inyectado y el docstring en `r"""` para eliminar un `SyntaxWarning`):

- `html, body { max-width: none; margin: 0; padding: 0 }` y cuerpo de 11 pt.
- `img { max-width: 100%; max-height: 16cm }`. `page-break-inside: avoid` solo en `figure`, `tr` e `img`.
- `table { display: table; table-layout: fixed; width: 100% }` con `overflow-wrap: anywhere` en celdas y código; `thead` repetido.
- `break-after: avoid` en los títulos y en el párrafo que precede a una tabla (el rótulo «Tabla n»).

Regeneración: `herramientas\.venv\Scripts\python.exe herramientas\conversion\exportar_s6.py` → DOCX de 5,7 MB y PDF de 7,1 MB.

## 2. Script PPTX → PDF

El script temporal del conversor se incorporó como `herramientas/conversion/pptx_a_pdf.ps1`:

- tiene parámetros `-Pptx` y `-Pdf`, con las rutas de S6 por defecto relativas a la raíz;
- abre el PPTX en solo lectura y sin ventana;
- en `finally` ejecuta `Close()`, `Quit()` y libera los objetos COM;
- devuelve el código de salida 1 si falla;
- está guardado en UTF-8 con BOM para PowerShell 5.1.

Se ejecutó: generó un PDF de 2,0 MB con 7 páginas de 960 x 540 pt, y PowerPoint se cerró. Está documentado en `herramientas/conversion/README.md`. Con esto S6-21 queda HECHO.

## 3. Coordinación

- `TABLERO_S6.md`:
  - S6-05 con las cifras nuevas;
  - S6-21 HECHO;
  - S6-24 PARCIAL: solo falta la reexportación final (N-13);
  - fila nueva S6-25;
  - sección «Pendientes reales»: pasos manuales, reexportación final y merge.
- `coordinacion/TABLERO.md`: resumen S6 al 2026-10-02.
- `coordinacion/RUTAS.md`:
  - variantes `_16x9` y `_media`;
  - scripts de `herramientas/conversion/`;
  - paquetes del `.venv`;
  - estado de la inspección v2;
  - los 3 archivos que se suben al aula.
- `README.md` raíz:
  - fila S6 con su estado real;
  - nueva sección «Entrega S6: qué subir al aula virtual», con los 3 archivos y los enlaces al repositorio y al tag;
  - herramientas al 2026-10-02.

Observación para el inspector-guia: en `PASOS_MANUALES.md`, los pasos 12 (PDF de las diapositivas) y 13 (exportar el informe) ya los hicieron los agentes. El 13 se repite al reexportar después de completar los `[COMPLETAR]`.

## 4. Commit

Un solo commit en la rama, sin push. Se revisó que no entren:

- `.venv`;
- `plantuml.jar`;
- archivos `*.db` o `*.log`;
- `_build`;
- archivos de más de 10 MB.
