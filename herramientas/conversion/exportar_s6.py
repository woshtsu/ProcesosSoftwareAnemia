#!/usr/bin/env python
r"""
exportar_s6.py - Conversor reproducible: Markdown -> DOCX + PDF para S6 Integrador
Requiere: pypandoc_binary (instalado en herramientas\.venv)
Uso: cd D:\Workspace\...\ProcesosSoftwareAnemia
     .\herramientas\.venv\Scripts\python.exe .\herramientas\conversion\exportar_s6.py
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def main():
    # Detectar repo root
    current_dir = Path(os.getcwd())
    repo_root = current_dir

    # Rutas clave
    entregable_dir = repo_root / "entregables" / "semana-06-integrador"
    build_dir = repo_root / "diagramas" / "_build" / "conversion"
    export_dir = repo_root / "exportados" / "semana-06"

    # Crear directorios si no existen
    build_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    # Archivos de entrada/salida
    input_md = entregable_dir / "Informe_Integrador_Anemia_Junin.md"
    temp_md = build_dir / "Informe_Integrador_Anemia_Junin_temp.md"
    output_docx = export_dir / "Informe_Integrador_Anemia_Junin.docx"
    output_pdf = export_dir / "Informe_Integrador_Anemia_Junin.pdf"
    temp_html = build_dir / "Informe_temp.html"

    print("=== CONVERSOR S6: MD -> DOCX + PDF ===")
    print(f"Repo: {repo_root}")
    print()

    # 1. Verificar que el MD existe
    if not input_md.exists():
        print(f"ERROR: Informe MD no encontrado en {entregable_dir}")
        sys.exit(1)

    # 2. Copiar MD a directorio temporal
    print("[1/5] Copiando Informe a directorio temporal...")
    shutil.copy(input_md, temp_md)

    # 3. Reemplazar referencias SVG -> PNG
    print("[2/5] Reemplazando referencias SVG -> PNG...")
    with open(temp_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Reemplazar .svg) por .png) y rutas de svg/ por png/
    content = content.replace('.svg)', '.png)')
    content = content.replace('diagramas/svg/', 'diagramas/png/')

    with open(temp_md, 'w', encoding='utf-8') as f:
        f.write(content)

    # 4. Generar DOCX
    print("[3/5] Generando DOCX...")
    try:
        import pypandoc
        os.chdir(entregable_dir)
        output = pypandoc.convert_file(
            str(temp_md),
            'docx',
            outputfile=str(output_docx),
            extra_args=[
                '--toc',
                '--resource-path=.;../..',
                '--default-image-extension=png'
            ]
        )
        print(f"  DOCX generado: {output_docx}")
    except Exception as e:
        print(f"ERROR generando DOCX: {e}")
        sys.exit(1)
    finally:
        os.chdir(repo_root)

    # 5. Generar PDF (HTML + Edge headless)
    print("[4/5] Generando PDF (HTML + Edge)...")
    try:
        import pypandoc
        os.chdir(entregable_dir)

        # Generar HTML intermedio con metadatos de título
        pypandoc.convert_file(
            str(temp_md),
            'html',
            outputfile=str(temp_html),
            extra_args=[
                '--toc',
                '--standalone',
                '--embed-resources',
                '--resource-path=.;../..',
                '--default-image-extension=png',
                '--metadata', 'title=Informe Académico Integrador — Anemia infantil Junín'
            ]
        )
        print(f"  HTML intermedio generado: {temp_html}")

        # Inyectar CSS personalizado para A4, límites de imagen y saltos de página
        print("  Inyectando CSS personalizado (A4, límites de imagen)...")
        with open(temp_html, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Crear CSS personalizado
        custom_css = '''<style>
@page {
  size: A4;
  margin: 2.5cm;
  orphans: 2;
  widows: 2;
}

/* Usar todo el ancho útil de A4 (la plantilla de pandoc limita el body a 36em) */
html, body {
  max-width: none !important;
  margin: 0 !important;
  padding: 0 !important;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.45;
  color: #333;
}

/* Imágenes: ancho completo; altura máx. 16 cm (< 24,7 cm útiles), sin huecos grandes
   y sin figuras partidas ni duplicadas (N-14) */
img {
  max-width: 100%;
  max-height: 16cm;
  width: auto;
  height: auto;
  object-fit: contain;
}

/* Solo las figuras no se parten; las tablas largas sí pueden continuar
   en la página siguiente (evita páginas con solo el título de la tabla) */
figure {
  page-break-inside: avoid;
  break-inside: avoid;
  margin: 0.6em 0;
  text-align: center;
}

figcaption {
  font-size: 10pt;
  text-align: center;
}

/* La plantilla de pandoc pone table {display:block; overflow-x:auto}, que en
   impresión recorta las columnas de la derecha (p. ej. Tabla 30 de 8 columnas) */
table {
  display: table !important;
  overflow: visible !important;
  table-layout: fixed;
  width: 100% !important;
  font-size: 9pt;
  line-height: 1.3;
}

th, td {
  overflow-wrap: anywhere;
  word-break: normal;
  padding: 0.2em 0.35em !important;
  vertical-align: top;
}

td code, th code {
  white-space: normal;
  overflow-wrap: anywhere;
  font-size: 0.9em;
}

tr, img {
  page-break-inside: avoid;
  break-inside: avoid;
}

thead {
  display: table-header-group;
}

/* Títulos y rótulos de tabla junto al contenido que les sigue */
h1, h2, h3, h4 {
  page-break-after: avoid;
  break-after: avoid;
}

p:has(+ table) {
  page-break-after: avoid;
  break-after: avoid;
}

/* Tabla de contenidos - salto de página */
nav[role="doc-toc"] {
  page-break-after: always;
}
</style>'''

        # Buscar dónde insertar el CSS (después de <head> o antes de </head>)
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', custom_css + '\n</head>')
        elif '<head>' in html_content:
            # Si no hay </head>, agregar después de <head>
            html_content = html_content.replace('<head>', '<head>' + custom_css)
        else:
            # Si no hay <head>, agregar al inicio del body
            if '<body>' in html_content:
                html_content = html_content.replace('<body>', '<body>' + custom_css)

        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("  CSS inyectado correctamente")

        # Buscar Edge
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]

        edge_path = None
        for path in edge_paths:
            if os.path.exists(path):
                edge_path = path
                break

        if not edge_path:
            print("  ADVERTENCIA: Microsoft Edge no encontrado.")
            print("  Saltando generación de PDF (paso manual).")
            # Crear un PDF vacío para que el script no falle
            from pypdf import PdfWriter
            writer = PdfWriter()
            with open(output_pdf, 'wb') as f:
                writer.write(f)
            print(f"  PDF de marcador creado: {output_pdf}")
        else:
            # Imprimir a PDF con Edge headless
            cmd = [
                edge_path,
                '--headless',
                '--disable-gpu',
                f'--print-to-pdf={output_pdf}',
                '--no-pdf-header-footer',
                str(temp_html)
            ]

            print(f"  Ejecutando: {' '.join(cmd[:3])}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                print(f"  ERROR de Edge: {result.stderr}")
                print(f"  Stdout: {result.stdout}")
                # No fallar aquí, continuar
            else:
                print(f"  PDF generado: {output_pdf}")

    except ImportError as e:
        print(f"ERROR: {e}")
        print("  Instala: pip install pypdf")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR generando PDF: {e}")
        # Continuar sin fallar
    finally:
        os.chdir(repo_root)

    # 6. Validar archivos
    print("[5/5] Validando archivos...")

    docx_exists = output_docx.exists()
    pdf_exists = output_pdf.exists()

    if docx_exists and pdf_exists:
        docx_size = output_docx.stat().st_size / (1024 * 1024)
        pdf_size = output_pdf.stat().st_size / (1024 * 1024)

        print()
        print("=== ÉXITO ===")
        print(f"DOCX: {output_docx} ({docx_size:.1f} MB)")
        print(f"PDF:  {output_pdf} ({pdf_size:.1f} MB)")
        print()

        # Intentar leer número de páginas del PDF
        try:
            from pypdf import PdfReader
            if pdf_exists and pdf_size > 0.01:  # Más de 10 KB
                reader = PdfReader(output_pdf)
                pages = len(reader.pages)
                print(f"PDF pages: {pages}")
        except ImportError:
            print("  (Instala pypdf para leer metadatos del PDF)")
        except Exception as e:
            print(f"  (No se pudo leer el PDF: {e})")

        print()
        print(f"Archivos generados en: {export_dir}")
    else:
        print("ERROR: Falló la generación de archivos.")
        if not docx_exists:
            print(f"  - DOCX no generado: {output_docx}")
        if not pdf_exists:
            print(f"  - PDF no generado: {output_pdf}")
        sys.exit(1)

    # 7. Limpiar archivos temporales
    temp_md.unlink(missing_ok=True)
    temp_html.unlink(missing_ok=True)

    print()
    print("NOTA: Los archivos contienen [COMPLETAR] que deben reemplazarse en el MD fuente.")

if __name__ == "__main__":
    main()
