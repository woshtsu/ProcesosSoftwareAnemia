"""Exporta a PDF los entregables HTML de la semana 13 (PDCA y laboratorio SCM).

Uso (desde la raíz del repositorio):
    pmv_fastapi/.venv/Scripts/python.exe entregables/semana-13/exportar_pdf_s13.py [pdca|scm]

Usa Microsoft Edge sin interfaz (Playwright) y respeta el ``@page`` de cada HTML.
Los PDF se escriben en ``exportados/semana-13/``.
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
DESTINO = RAIZ / "exportados" / "semana-13"

DOCUMENTOS = {
    "pdca": (AQUI / "pdca" / "PDCA_gestion_configuracion.html", "Porras-Auqui-Huamani-PDCA-mejora.pdf"),
    "scm": (AQUI / "laboratorio-scm" / "Informe_SCM_Lab13.html", "Porras-Auqui-Huamani-Informe-SCM-Lab13.pdf"),
}


def main() -> None:
    elegidos = sys.argv[1:] or list(DOCUMENTOS)
    DESTINO.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        nav = p.chromium.launch(channel="msedge", headless=True)
        pg = nav.new_page()
        for clave in elegidos:
            fuente, nombre = DOCUMENTOS[clave]
            pg.goto(fuente.as_uri(), wait_until="networkidle")
            pg.pdf(path=str(DESTINO / nombre), prefer_css_page_size=True, print_background=True,
                   display_header_footer=True, header_template="<span></span>",
                   footer_template='<div style="font-size:7pt;width:100%;text-align:center;color:#667085">'
                                   '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
            print(f"OK  {nombre}")
        nav.close()


if __name__ == "__main__":
    main()
