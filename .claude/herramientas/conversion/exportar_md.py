"""Exporta cualquier entregable Markdown a DOCX y PDF (generalización de exportar_s9.py, T-026).

Uso (desde la raíz del repositorio):
    python .claude/herramientas/conversion/exportar_md.py <entregable.md> <carpeta_salida> ["Título"] [--solo-pdf|--solo-docx]

Ejemplo:
    python .claude/herramientas/conversion/exportar_md.py entregables/semana-05/Entregable_Semana5_Anemia_Junin.md exportados/semana-05

Requisitos: pandoc en el PATH y Playwright con Chromium (para el PDF).
- Copia el .md a un temporal, cambia las referencias SVG de .claude/diagramas/ por su PNG
  (Word no siempre renderiza SVG) y los saltos de página HTML por saltos nativos.
- DOCX: pandoc con índice de contenidos.
- PDF: pandoc -> HTML autocontenido + CSS A4 -> Chromium (print to PDF).
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
_ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
_OPC = {a for a in sys.argv[1:] if a.startswith("--")}
if len(_ARGS) < 2:
    sys.exit(__doc__)
ORIGEN = (Path.cwd() / _ARGS[0]).resolve()
SALIDA = (Path.cwd() / _ARGS[1]).resolve()
NOMBRE = ORIGEN.stem
TITULO = _ARGS[2] if len(_ARGS) > 2 else NOMBRE.replace("_", " ")
TMP = RAIZ / ".claude" / "diagramas" / "_build" / f"conversion_{NOMBRE}"

CSS = """
@page { size: A4; margin: 2.2cm 2cm; }
body { max-width: none; font-family: 'Segoe UI', 'DejaVu Sans', Arial, sans-serif; font-size: 10pt;
       line-height: 1.4; color: #1a1a1a; padding: 0; margin: 0; }
h1 { font-size: 18pt; color: #1F4E79; } h2 { font-size: 14pt; color: #1F4E79; border-bottom: 1px solid #1F4E79; }
h3 { font-size: 12pt; color: #1F4E79; } h4 { font-size: 11pt; }
h1, h2, h3, h4, p > strong:only-child { break-after: avoid; }
table { display: table; table-layout: auto; width: 100%; border-collapse: collapse; font-size: 8.3pt;
        overflow: visible; }
th { background: #1F4E79; color: #fff; } th, td { border: 1px solid #9fb3c8; padding: 3px 4px; vertical-align: top; }
tr, img, figure { page-break-inside: avoid; }
img { max-width: 100%; max-height: 17cm; display: block; margin: 4px auto; }
figure { margin: 8px 0; } figcaption { font-size: 8.5pt; color: #444; text-align: center; }
pre, code { font-size: 8pt; white-space: pre-wrap; word-break: break-word; }
blockquote { border-left: 3px solid #1F4E79; margin-left: 0; padding-left: 10px; color: #222; }
.salto { page-break-after: always; }
"""


def preparar() -> Path:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    texto = ORIGEN.read_text(encoding="utf-8")
    texto = re.sub(r"((?:\.\./)+)(?:\.claude/)?diagramas/svg/([\w\-]+)\.svg", r"\1.claude/diagramas/png/\2.png", texto)
    texto = re.sub(r"metricas/graficos/([\w\-]+)\.svg", r"metricas/graficos/\1.png", texto)
    # Enlaces relativos a archivos (no imágenes) -> URL del repositorio en GitHub, para que funcionen en DOCX/PDF.
    base = "https://github.com/woshtsu/ProcesosSoftwareAnemia/blob/main/"

    def _abs(m: re.Match) -> str:
        destino_rel = (ORIGEN.parent / m.group(2)).resolve().relative_to(RAIZ).as_posix()
        return f"[{m.group(1)}]({base}{destino_rel})"

    texto = re.sub(r"(?<!!)\[([^\]]+)\]\((?!https?:|#|mailto:)([^)\s]+)\)", _abs, texto)
    destino = ORIGEN.parent / f"_{NOMBRE}_exportar.md"
    destino.write_text(texto, encoding="utf-8")
    return destino


def docx(md: Path) -> Path:
    texto = md.read_text(encoding="utf-8")
    salto = '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```'
    texto = texto.replace('<div style="page-break-after: always;"></div>', salto)
    md_docx = md.with_name(md.stem + "_docx.md")
    md_docx.write_text(texto, encoding="utf-8")
    out = SALIDA / f"{NOMBRE}.docx"
    subprocess.run(
        ["pandoc", md_docx.name, "-f", "markdown+raw_attribute", "-o", str(out), "--toc", "--toc-depth=2",
         "--metadata", f"pagetitle={TITULO}", "--resource-path=."],
        cwd=md.parent, check=True)
    md_docx.unlink()
    return out


def pdf(md: Path) -> Path:
    texto = md.read_text(encoding="utf-8").replace(
        '<div style="page-break-after: always;"></div>', '<div class="salto"></div>')
    md_html = md.with_name(md.stem + "_html.md")
    md_html.write_text(texto, encoding="utf-8")
    css = TMP / "s9.css"
    css.write_text(CSS, encoding="utf-8")
    html = TMP / f"{NOMBRE}.html"
    subprocess.run(
        ["pandoc", md_html.name, "-s", "--embed-resources", "--css", str(css), "-o", str(html),
         "--metadata", f"pagetitle={TITULO}", "--resource-path=.", "-V", "lang=es"],
        cwd=md.parent, check=True)
    md_html.unlink()
    from playwright.sync_api import sync_playwright

    out = SALIDA / f"{NOMBRE}.pdf"
    with sync_playwright() as p:
        try:
            nav = p.chromium.launch()
        except Exception:  # sin Chromium de Playwright: usar Microsoft Edge instalado
            nav = p.chromium.launch(channel="msedge")
        pag = nav.new_page()
        pag.goto(html.as_uri())
        pag.wait_for_load_state("networkidle")
        pag.pdf(path=str(out), format="A4", print_background=True,
                margin={"top": "2cm", "bottom": "2cm", "left": "1.8cm", "right": "1.8cm"},
                display_header_footer=True, header_template="<span></span>",
                footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#666">'
                                f'Anemia Junín · {TITULO} · <span class="pageNumber"></span>/'
                                '<span class="totalPages"></span></div>')
        nav.close()
    return out


def main() -> int:
    SALIDA.mkdir(parents=True, exist_ok=True)
    md = preparar()
    try:
        d = None if "--solo-pdf" in _OPC else docx(md)
        p = None if "--solo-docx" in _OPC else pdf(md)
    finally:
        md.unlink(missing_ok=True)
    for f in (x for x in (d, p) if x):
        print(f"{f}  ({f.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
