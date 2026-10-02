# Herramientas de Conversión: Informe S6

Script reproducible para convertir el Informe Integrador S6 de Markdown a DOCX y PDF.

## Requisitos

- Python 3.14+
- Entorno virtual en `herramientas\.venv` con:
  - `pypandoc_binary` (1.17+)
  - `pypdf` (para validación)
- Microsoft Edge (para renderizado de PDF)
- Microsoft PowerPoint (opcional, para PPTX→PDF)

## Instalación

```powershell
# En la raíz del repositorio
cd herramientas\.venv\Scripts

# Instalar herramientas
.\pip install pypandoc_binary pypdf

# Opcional: PowerPoint COM (solo si PowerPoint está instalado)
# (No requiere pip install; es una librería COM del sistema)
```

## Uso

### Generar DOCX y PDF

```powershell
# Desde la raíz del repositorio
.\herramientas\.venv\Scripts\python.exe .\herramientas\conversion\exportar_s6.py
```

**Salida esperada:**

```
=== CONVERSOR S6: MD -> DOCX + PDF ===
Repo: D:\Workspace\...\ProcesosSoftwareAnemia

[1/5] Copiando Informe a directorio temporal...
[2/5] Reemplazando referencias SVG -> PNG...
[3/5] Generando DOCX...
  DOCX generado: ...\exportados\semana-06\Informe_Integrador_Anemia_Junin.docx
[4/5] Generando PDF (HTML + Edge)...
  HTML intermedio generado: ...\diagramas\_build\conversion\Informe_temp.html
  Inyectando CSS personalizado (A4, límites de imagen)...
  CSS inyectado correctamente
  Ejecutando: C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --headless --disable-gpu...
  PDF generado: ...\exportados\semana-06\Informe_Integrador_Anemia_Junin.pdf
[5/5] Validando archivos...

=== ÉXITO ===
DOCX: ...\exportados\semana-06\Informe_Integrador_Anemia_Junin.docx (5.7 MB)
PDF:  ...\exportados\semana-06\Informe_Integrador_Anemia_Junin.pdf (7.1 MB)
PDF pages: 51
```

**Cambios en la versión 2026-10-02:**

- PDF en **A4** (595 x 842 pt) con márgenes de 2,5 cm y título en los metadatos
  («Informe Académico Integrador — Anemia infantil Junín») (N-12).
- CSS inyectado en el HTML de pandoc (revisado tras el control de calidad del sincronizador):
  - `body` sin el límite de 36em de la plantilla de pandoc: se usa todo el ancho útil de A4.
  - `img { max-width: 100%; max-height: 16cm }`: las figuras anchas (C4, matrices) ocupan el
    ancho completo y ninguna supera la página, de modo que no se parten ni se duplican (N-14).
  - `page-break-inside: avoid` **solo** en `figure`, `tr` e `img`; las tablas largas pueden
    continuar en la página siguiente (antes dejaban páginas con solo el rótulo «Tabla n»).
  - `table { display: table; table-layout: fixed }`: la plantilla de pandoc ponía
    `display: block; overflow-x: auto`, que en impresión **recortaba** columnas
    (la Tabla 30 de 8 columnas mostraba solo 4).
  - Títulos y rótulos de tabla con `break-after: avoid`.
- Resultado: 75 → **51 páginas**; páginas con menos del 30 % de su altura ocupada: 11 → 7
  (todas son fin de sección o una figura alta que pasa a la página siguiente); 35 imágenes.

### Convertir Presentación PPTX a PDF

Script `pptx_a_pdf.ps1` (PowerPoint COM, `SaveAs` con formato 32 = PDF). Abre el PPTX en
solo lectura y sin ventana, y cierra la presentación y PowerPoint (`Quit()`) en un bloque
`finally`, también si la conversión falla. Requiere Microsoft PowerPoint; no instala nada.

```powershell
# Desde la raíz del repositorio (rutas por defecto: exportados/semana-06/Presentacion_Integrador_Anemia_Junin.*)
powershell -ExecutionPolicy Bypass -File .\herramientas\conversion\pptx_a_pdf.ps1

# Otras rutas
powershell -ExecutionPolicy Bypass -File .\herramientas\conversion\pptx_a_pdf.ps1 -Pptx ruta.pptx -Pdf ruta.pdf
```

Salida esperada: `PDF generado: ...\Presentacion_Integrador_Anemia_Junin.pdf (2.0 MB)` y código de salida 0
(7 páginas de 960 x 540 pt).

### Validar PDF generado

```powershell
.\herramientas\.venv\Scripts\python.exe -c "
from pypdf import PdfReader

reader = PdfReader('exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf')
print(f'Pages: {len(reader.pages)}')

# Buscar marcadores problemáticos
all_text = ''.join(p.extract_text() for p in reader.pages)
completar_count = all_text.count('[COMPLETAR')
print(f'[COMPLETAR] occurrences: {completar_count}')

if completar_count > 0:
    print('ADVERTENCIA: El PDF contiene [COMPLETAR] que debe completarse en el MD fuente')
"
```

## Archivos generados

| Archivo | Ruta | Tamaño | Notas |
| --- | --- | --- | --- |
| `Informe_Integrador_Anemia_Junin.docx` | `exportados/semana-06/` | 5.7 MB | Editable en Microsoft Word; 35 imágenes |
| `Informe_Integrador_Anemia_Junin.pdf` | `exportados/semana-06/` | 7.1 MB | **A4**, 51 páginas, 35 figuras, 31 tablas; sin imagen duplicada ni columnas recortadas |
| `Presentacion_Integrador_Anemia_Junin.pdf` | `exportados/semana-06/` | 2.0 MB | 7 diapositivas, 960x540 pt, 31 imágenes |

## Archivos intermedios (regenerables)

Los siguientes archivos se crean durante la conversión y se limpian automáticamente:

- `diagramas/_build/conversion/Informe_Integrador_Anemia_Junin_temp.md` — Copia temporal con rutas PNG
- `diagramas/_build/conversion/Informe_temp.html` — HTML intermedio para renderizado

## Proceso técnico

### 1. Conversión MD → DOCX

```
Input: entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md
  ↓
1. Copiar a diagramas/_build/conversion/
2. Reemplazar SVG → PNG (Word no renderiza SVG bien)
3. pandoc --toc --resource-path=.;../..
  ↓
Output: exportados/semana-06/Informe_Integrador_Anemia_Junin.docx
```

### 2. Conversión MD → PDF

```
Input: entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md
  ↓
1. Copiar a diagramas/_build/conversion/
2. Reemplazar SVG → PNG
3. pandoc --standalone --embed-resources → HTML
4. Microsoft Edge headless --print-to-pdf
  ↓
Output: exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf
```

### 3. Conversión PPTX → PDF

```
Input: exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pptx
  ↓
PowerPoint COM → SaveAs(format=32)
  ↓
Output: exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pdf
```

## Troubleshooting

### "pypandoc_binary not found"

```powershell
cd herramientas\.venv\Scripts
.\pip install pypandoc_binary
```

### "Microsoft Edge not found"

El script buscará en las rutas estándar:
- `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
- `C:\Program Files\Microsoft\Edge\Application\msedge.exe`

Si Edge no está instalado, instálalo desde https://www.microsoft.com/edge

### PDF vacío o sin contenido

Verifica que:
1. El MD fuente es válido y contiene imágenes relativas a `diagramas/png/`
2. Las imágenes PNG existen en `diagramas/png/`
3. Edge puede renderizar HTML (prueba navegando a `file:///<ruta>/Informe_temp.html`)

### "[COMPLETAR] aparece en el PDF"

El MD fuente aún contiene marcadores `[COMPLETAR]`. Complétalos en:
- `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md`

Luego regenera los documentos ejecutando el script nuevamente.

## Validación de calidad

Después de generar los archivos, verifica:

```powershell
# 1. Número de páginas
.\herramientas\.venv\Scripts\python.exe -c "
from pypdf import PdfReader
reader = PdfReader('exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf')
print(f'Total pages: {len(reader.pages)}')
"

# 2. Búsqueda de marcadores problemáticos
.\herramientas\.venv\Scripts\python.exe -c "
from pypdf import PdfReader
reader = PdfReader('exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf')
text = ''.join(p.extract_text() for p in reader.pages)
print(f'[COMPLETAR]: {text.count(\"[COMPLETAR\")}')
print(f'[PENDIENTE]: {text.count(\"[PENDIENTE\")}')
print(f'CARGA_CIERRE: {text.count(\"CARGA_CIERRE\")}')
"

# 3. Tamaños de archivo
ls -lh exportados/semana-06/*.pdf, exportados/semana-06/*.docx
```

## Scripts relacionados

- `entregables/semana-06-integrador/presentacion/generar_presentacion.py` — Genera PPTX desde Marp
- `diagramas/src/integrador/*.py` — Generadores de figuras S6
- `herramientas/conversion/pptx_a_pdf.ps1` — PPTX → PDF de la presentación con PowerPoint COM
- `coordinacion/s6/informes/2026-10-01_conversor-entregas_s6-05.md` — Informe de ejecución

---

**Última actualización:** 2026-10-02  
**Ejecutor:** conversor-entregas (Claude Haiku 4.5)  
**Cambios:** N-12 (A4 y metadatos) y N-14 (sin duplicado de captura 07) resueltos; CSS revisado por el sincronizador (51 páginas, tablas sin recorte) y `pptx_a_pdf.ps1` incorporado
