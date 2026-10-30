"""Genera la síntesis de feria desde su fuente Markdown y las capturas originales.

Uso desde la raíz: python herramientas/conversion/exportar_feria.py
Requiere ReportLab y Pillow. No modifica las evidencias de entrada.
"""

from io import BytesIO
from pathlib import Path
import re

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "entregables/feria/Proyecto_Feria_Anemia_Junin.md"
OUTPUT = ROOT / "exportados/feria/Proyecto_Feria_Anemia_Junin.pdf"
W, H = 595.276, 841.89
M, CW = 38, W - 76
NAVY = colors.HexColor("#173E58")
TEAL = colors.HexColor("#087E83")
INK = colors.HexColor("#263B49")
MUTED = colors.HexColor("#526575")
LIGHT = colors.HexColor("#E9F2F5")


def register_fonts():
    candidates = [
        (Path("C:/Windows/Fonts/segoeui.ttf"), Path("C:/Windows/Fonts/segoeuib.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("Body", str(regular)))
            pdfmetrics.registerFont(TTFont("BodyBold", str(bold)))
            pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyBold")
            return
    raise RuntimeError("Se necesita Segoe UI o DejaVu Sans para incrustar las fuentes.")


def sections():
    text = SOURCE.read_text(encoding="utf-8")
    result = {}
    for part in text.split("\n## ")[1:]:
        title, body = part.split("\n", 1)
        result[title.strip()] = body.strip()
    return result


def paragraph(c, text, y, size=10.1, leading=14.3, color=INK, x=M, width=CW):
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = text.replace("\n", " ")
    p = Paragraph(text, ParagraphStyle("body", fontName="Body", fontSize=size,
                  leading=leading, textColor=color, alignment=TA_LEFT))
    _, height = p.wrap(width, H)
    bottom = y - height
    if bottom < 47:
        raise ValueError(f"Contenido fuera del área útil: {text[:70]} (y={bottom})")
    p.drawOn(c, x, bottom)
    return bottom - 8


def heading(c, text, y):
    c.setFillColor(TEAL)
    c.setFont("BodyBold", 12)
    c.drawString(M, y - 12, text)
    return y - 23


def body(c, text, y, **kwargs):
    for para in text.split("\n\n"):
        if not para.startswith("![") and not para.startswith("["):
            y = paragraph(c, para, y, **kwargs)
    return y


def frame(c, page, label):
    c.setFillColor(TEAL)
    c.rect(0, H - 9, W, 9, fill=1, stroke=0)
    c.setFont("BodyBold", 8)
    c.setFillColor(TEAL)
    c.drawString(M, H - 33, "FERIA DE PROYECTOS 2026  /  SALUD Y TECNOLOGÍA")
    c.setStrokeColor(LIGHT)
    c.line(M, 38, W - M, 38)
    c.setFillColor(MUTED)
    c.setFont("Body", 8)
    c.drawString(M, 23, "Anemia Junín  |  Universidad Continental")
    c.drawRightString(W - M, 23, f"{label}  /  {page} de 3")


def title(c, text, y, size=24):
    c.setFillColor(NAVY)
    c.setFont("BodyBold", size)
    c.drawString(M, y, text)
    return y - 22


def screenshot(c, section, top, max_height, crop=None):
    match = re.search(r"!\[.*?\]\((.*?)\)", section)
    path = (SOURCE.parent / match.group(1)).resolve()
    with Image.open(path) as original:
        img = original.convert("RGB")
    if crop:
        img = img.crop(crop)
    scale = min(CW / img.width, max_height / img.height)
    iw, ih = img.width * scale, img.height * scale
    x, bottom = M + (CW - iw) / 2, top - ih
    if bottom < 47:
        raise ValueError("Captura fuera del área útil")
    stream = BytesIO()
    img.save(stream, format="PNG")
    stream.seek(0)
    c.setStrokeColor(colors.HexColor("#CCDCE4"))
    c.setLineWidth(0.5)
    c.rect(x - 0.5, bottom - 0.5, iw + 1, ih + 1, fill=0, stroke=1)
    c.drawImage(ImageReader(stream), x, bottom, width=iw, height=ih)
    return bottom - 13


def main():
    register_fonts()
    s = sections()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(W, H), pageCompression=1)
    c.setTitle("Anemia Junín | Feria de proyectos")
    c.setAuthor("Ricardo Porras Veli; Tania Tifani Auqui Huincho; Jean Piero Huamani Rodriguez")
    c.setSubject("Problemática, solución tecnológica, impacto y evidencias de funcionamiento")

    frame(c, 1, "EL PROYECTO")
    y = title(c, "Anemia Junín", 769, 32)
    y = paragraph(c, "Seguimiento oportuno de la anemia infantil en zonas rurales", y, size=12, leading=16)
    y = paragraph(c, "Ingeniería de Sistemas e Informática · Procesos de Software", y, size=8.6, leading=12, color=MUTED)
    y = paragraph(c, s["Equipo"], y, size=8.6, leading=12, color=MUTED) - 2
    y = body(c, s["Problemática"], heading(c, "01  La problemática", y))
    y = body(c, s["Solución tecnológica"], heading(c, "02  La solución tecnológica", y))
    y = heading(c, "En funcionamiento", y)
    # Recorte continuo del detalle superior, identificado en la leyenda.
    y = screenshot(c, s["Evidencia 1"], y, 248, crop=(0, 0, 1366, 700))
    body(c, s["Evidencia 1"], y, size=8.4, leading=11.3, color=MUTED)
    c.showPage()

    frame(c, 2, "ORGANIZACIÓN E IMPACTO")
    y = title(c, "De las fechas a la acción", 769)
    y = body(c, s["Evidencia 2"], y, size=10, leading=14)
    y = screenshot(c, s["Evidencia 2"], y - 2, 360) - 3
    y = body(c, s["Impacto demostrado"], heading(c, "03  Impacto demostrado en la evaluación", y))
    body(c, s["Impacto esperado"], heading(c, "Beneficio esperado en el establecimiento", y))
    c.showPage()

    frame(c, 3, "EVIDENCIAS Y RESPALDO")
    y = title(c, "Priorizar el seguimiento", 769)
    y = body(c, s["Evidencia 3"], y, size=10, leading=14)
    y = screenshot(c, s["Evidencia 3"], y - 1, 442)
    y = body(c, s["Verificación del funcionamiento"], heading(c, "04  Verificación del funcionamiento", y),
             size=9, leading=12.5)
    y = body(c, s["Fuentes y alcance"], heading(c, "Fuentes y alcance", y), size=7.9, leading=10.6, color=MUTED)
    paragraph(c, '<a href="https://github.com/woshtsu/ProcesosSoftwareAnemia" color="#087E83">'
              'Repositorio y evidencias: github.com/woshtsu/ProcesosSoftwareAnemia</a>',
              y, size=8, leading=11)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
