"""Exporta el entregable S11 (Markdown) a PDF.

Uso (desde cualquier carpeta):
    python herramientas/conversion/exportar_s11.py

Dependencias:
- Python 3.11 o superior y el paquete `markdown` (`pip install markdown`).
- Google Chrome o Microsoft Edge (se busca en las rutas habituales de Windows). Para usar otro
  navegador, definir la variable de entorno NAVEGADOR con la ruta del ejecutable.

Proceso: Markdown -> HTML autocontenido (imágenes incrustadas en base64, leyendas de figura y
numeración de página) en `diagramas/_build/conversion_s11/` (ignorado por Git) -> PDF A4 en
`exportados/semana-11/` mediante la impresión sin interfaz del navegador. El PDF contiene marcas de
tiempo del navegador, por lo que dos ejecuciones no dan archivos idénticos byte a byte.
"""

import base64
import mimetypes
import os
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "entregables" / "semana-11" / "Entregable_Semana11_Anemia_Junin.md"
SALIDA = RAIZ / "exportados" / "semana-11"
TMP = RAIZ / "diagramas" / "_build" / "conversion_s11"
NOMBRE = "Entregable_Semana11_Anemia_Junin"

NAVEGADORES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

CSS = """
@page { size: A4; margin: 1.8cm 1.8cm 2cm;
        @bottom-right { content: "Página " counter(page) " de " counter(pages); font-size: 8pt; color: #666; } }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; line-height: 1.4; color: #1a1a1a; }
h1 { font-size: 18pt; color: #1F4E79; } h2 { font-size: 14pt; color: #1F4E79; border-bottom: 1px solid #1F4E79; }
h3 { font-size: 12pt; color: #1F4E79; } h4 { font-size: 11pt; color: #1F4E79; }
h1, h2, h3, h4, p:has(+ table), p:has(+ pre), p:has(> strong:only-child) { break-after: avoid; }
h4 + table { break-inside: avoid; }
table { width: 100%; border-collapse: collapse; font-size: 8.3pt; margin: 6px 0; }
th { background: #1F4E79; color: #fff; } th, td { border: 1px solid #9fb3c8; padding: 3px 4px; vertical-align: top; }
tr { break-inside: avoid; }
figure { margin: 6px 0 10px; break-inside: avoid; }
img { max-width: 100%; max-height: 11cm; display: block; margin: 4px auto; }
img.alta { max-height: 21cm; }
figcaption { font-size: 9pt; text-align: center; font-style: italic; margin-top: 2px; color: #333; }
pre { background: #f4f6f8; border: 1px solid #d0d7de; padding: 6px 8px; break-inside: avoid; }
pre, code { font-size: 8pt; white-space: pre-wrap; }
.nb { white-space: nowrap; }
hr { border: 0; border-top: 1px solid #ccc; }
"""


def tamano_png(ruta: Path) -> tuple[int, int]:
    with ruta.open("rb") as f:
        cabecera = f.read(24)
    return struct.unpack(">II", cabecera[16:24])


def incrustar(html: str) -> str:
    def _img(m: re.Match) -> str:
        ruta = (ORIGEN.parent / m.group(2)).resolve()
        if not ruta.is_file():
            raise FileNotFoundError(f"Imagen no encontrada: {m.group(2)}")
        tipo = mimetypes.guess_type(ruta.name)[0] or "image/png"
        datos = base64.b64encode(ruta.read_bytes()).decode()
        clase = ""
        if tipo == "image/png":
            ancho, alto = tamano_png(ruta)
            if alto / ancho > 1.2:
                clase = ' class="alta"'
        return f'<img{clase}{m.group(1)}src="data:{tipo};base64,{datos}"'

    return re.sub(r'<img([^>]*?)src="(?!https?:|data:)([^"]+)"', _img, html)


def leyendas(html: str) -> str:
    return re.sub(
        r'<p>(<img alt="([^"]*)"[^>]*>)</p>',
        r"<figure>\1<figcaption>\2</figcaption></figure>",
        html,
    )


def sin_cortes_en_identificadores(html: str) -> str:
    """Evita que «RF-01», «HIST-2.3» o «H4» se partan entre líneas; no toca etiquetas ni atributos."""
    patron = re.compile(r"\b((?:RF|HIST|HU|DEF|CP|ADR)-\d+(?:\.\d+)?|H\d)\b")

    def _texto(m: re.Match) -> str:
        return ">" + patron.sub(r'<span class="nb">\1</span>', m.group(1)) + "<"

    return re.sub(r">([^<>]+)<", _texto, html)


def cortes_en_codigo(html: str) -> str:
    """Permite cortar rutas largas en «/», «_» y «.» dentro de `code`, en lugar de a mitad de palabra."""

    def _code(m: re.Match) -> str:
        return "<code>" + re.sub(r"([/_.])", r"\1<wbr>", m.group(1)) + "</code>"

    return re.sub(r"<code>([^<]*)</code>", _code, html)


def buscar_navegador() -> str | None:
    elegido = os.environ.get("NAVEGADOR")
    if elegido:
        return elegido if Path(elegido).exists() else None
    return next((n for n in NAVEGADORES if Path(n).exists()), None)


def main() -> int:
    navegador = buscar_navegador()
    if navegador is None:
        print("No se encontró Chrome ni Edge; defina la variable NAVEGADOR con la ruta del ejecutable.")
        return 1
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    SALIDA.mkdir(parents=True, exist_ok=True)
    cuerpo = markdown.markdown(ORIGEN.read_text(encoding="utf-8"), extensions=["tables", "fenced_code", "sane_lists"])
    cuerpo = cortes_en_codigo(sin_cortes_en_identificadores(incrustar(leyendas(cuerpo))))
    html = (
        f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{NOMBRE}</title>'
        f"<style>{CSS}</style></head><body>{cuerpo}</body></html>"
    )
    pagina = TMP / f"{NOMBRE}.html"
    pagina.write_text(html, encoding="utf-8")
    pdf = SALIDA / f"{NOMBRE}.pdf"
    pdf.unlink(missing_ok=True)
    subprocess.run(  # noqa: S603
        [navegador, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", pagina.as_uri()],
        check=True,
        timeout=180,
    )
    if not pdf.is_file() or pdf.stat().st_size < 10_000:
        print("El navegador no generó un PDF válido.")
        return 1
    print(f"PDF generado: {pdf} ({pdf.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
