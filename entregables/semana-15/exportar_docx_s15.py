"""Exporta el informe de la Unidad IV a Word (estilo institucional) y a PDF.

Estilo: el de la plantilla `plantilla_estilo_unidad_iv.docx` (Calibri, carátula centrada en verdes
1F4E3D/2E7D32, títulos con línea inferior, tablas con cabecera verde y filas alternas,
encabezado con el nombre del informe y pie «Página X de Y»).

Uso (desde la raíz del repositorio, Windows con Microsoft Word y pandoc):
    pmv_fastapi/.venv/Scripts/python.exe entregables/semana-15/exportar_docx_s15.py

Salida: exportados/semana-15/Porras-Auqui-Huamani-informe-unidad-IV.docx y .pdf
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
ORIGEN = AQUI / "Informe_Unidad_IV_Anemia_Junin.md"
PLANTILLA = AQUI / "plantilla_estilo_unidad_iv.docx"
SALIDA = RAIZ / "exportados" / "semana-15"
NOMBRE = "Porras-Auqui-Huamani-informe-unidad-IV"
PANDOC = shutil.which("pandoc") or str(Path.home() / "AppData/Local/Pandoc/pandoc.exe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SALTO = '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```'

CARATULA = r"""
::: {custom-style="Portada Texto"}
![](img/logo_uc.png){width=6.6cm}
:::

::: {custom-style="Portada Institucion"}
Universidad Continental
:::

::: {custom-style="Portada Escuela"}
Escuela Académico Profesional de Ingeniería de Sistemas e Informática
:::

::: {custom-style="Portada Texto"}
![](img/banner_curso.png){width=8.8cm}
:::

::: {custom-style="Portada Curso"}
Procesos de Software (ASUC01702) · Informe final de la Unidad IV (semanas 13–15)
:::

::: {custom-style="Portada Titulo"}
Diseño, adaptación, evaluación e implementación del proceso de software con entrega de valor: sistema para la detección temprana y el seguimiento de la anemia infantil en zonas rurales de Junín («Anemia Junín»)
:::

::: {custom-style="Portada Subtitulo"}
Informe académico integrador (Unidades I a IV, versión v4.0.1) – 26 de noviembre de 2026
:::

::: {custom-style="Portada Etiqueta"}
Integrantes
:::

::: {custom-style="Portada Texto"}
Porras Veli, Ricardo (76659572) – Leader / Software Architect
:::

::: {custom-style="Portada Texto"}
Auqui Huincho, Tania Tifani (75280128) – Backend & Data Engineer y Frontend & Mobile Developer
:::

::: {custom-style="Portada Texto"}
Huamani Rodriguez, Jean Piero (72156889) – Process Analyst & QA Lead
:::

::: {custom-style="Portada Texto"}
Amaru (Claude de Anthropic) – asistente de IA para desarrollo, pruebas, evidencias y documentación, bajo supervisión del equipo
:::

::: {custom-style="Portada Etiqueta"}
Docente
:::

::: {custom-style="Portada Texto"}
Jorge Alfredo Guevara Jiménez
:::

::: {custom-style="Portada Etiqueta"}
NRC
:::

::: {custom-style="Portada Texto"}
30173
:::

::: {custom-style="Portada Nota"}
Huancayo – Perú, 2026-20
:::
"""

INDICE = r"""
```{=openxml}
<w:p><w:pPr><w:spacing w:before="240" w:after="160"/></w:pPr><w:r><w:rPr><w:b/><w:color w:val="1F4E3D"/><w:sz w:val="32"/></w:rPr><w:t>Índice</w:t></w:r></w:p>
<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>(Índice: se actualiza al exportar)</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>
```
"""


def preparar_md() -> Path:
    t = ORIGEN.read_text(encoding="utf-8")
    # 1) Carátula: el bloque de texto inicial pasa a la carátula con estilos.
    i = t.find("```text")
    j = t.find("```", i + 7) + 3
    titulo = t[: i].strip()
    assert titulo.startswith("# "), "se esperaba el título del informe antes de la carátula"
    resto = t[j:]
    # 2) Índice general manual -> índice automático de Word.
    a = resto.find("## ÍNDICE GENERAL")
    b = resto.find("## ÍNDICE DE TABLAS")
    if a != -1 and b != -1:
        resto = resto[:a] + SALTO + "\n" + INDICE + "\n" + SALTO + "\n\n" + resto[b:]
    t = CARATULA + "\n" + SALTO + "\n" + resto
    # 3) Saltos de página HTML -> nativos.
    t = t.replace('<div style="page-break-after: always;"></div>', SALTO)
    # 4) SVG -> PNG (Word/pandoc no convierte SVG sin rsvg-convert).
    t = t.replace("ingenieria_inversa/img/dependencias_paquetes.svg", "ingenieria_inversa/img/dependencias_paquetes.png")
    t = re.sub(r"((?:\.\./)+)(?:\.claude/)?diagramas/svg/([\w\-]+)\.svg", r"\1.claude/diagramas/png/\2.png", t)
    # 5) Leyendas con su estilo.
    def leyenda(m: re.Match) -> str:
        estilo = "Leyenda Tabla" if m.group(1) == "Tabla" else "Leyenda Figura"
        return f'::: {{custom-style="{estilo}"}}\n{m.group(0)}\n:::'
    t = re.sub(r"^\*\*(Tabla|Figura) \d+\.\*\*.*$", leyenda, t, flags=re.M)
    # 6) Los títulos de nivel 1 empiezan en página nueva (como en la plantilla).
    t = re.sub(r"^(## )(?!ÍNDICE DE FIGURAS)", lambda m: SALTO + "\n\n" + m.group(1), t, flags=re.M)
    tmp = AQUI / "_s15_word.md"
    tmp.write_text(t, encoding="utf-8")
    return tmp


TABLA_CAB = "1F4E3D"
TABLA_ALT = "EEF5F0"
BORDE = "C9D6CE"


def estilizar_tablas(docx: Path) -> None:
    """Cabecera verde con texto blanco, filas alternas y bordes suaves (como la plantilla)."""
    with zipfile.ZipFile(docx) as z:
        archivos = {n: z.read(n) for n in z.namelist()}
    xml = archivos["word/document.xml"].decode("utf-8")

    def tabla(m: re.Match) -> str:
        tbl = m.group(0)
        bordes = ("<w:tblBorders>" + "".join(
            f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="{BORDE}"/>'
            for b in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>")
        tbl = re.sub(r"<w:tblBorders>.*?</w:tblBorders>", "", tbl, flags=re.S)
        tbl = tbl.replace("</w:tblPr>", bordes + "</w:tblPr>", 1)
        # Texto de celdas alineado a la izquierda (el justificado deja huecos en columnas angostas).
        tbl = re.sub(r"<w:jc w:val=\"both\"/>", '<w:jc w:val="left"/>', tbl)
        tbl = re.sub(r"<w:p>(?!<w:pPr>)", '<w:p><w:pPr><w:jc w:val="left"/></w:pPr>', tbl)
        def _jc(m: re.Match) -> str:
            ppr = m.group(0)
            if "<w:jc " in ppr:
                return ppr
            # Orden del esquema: jc va antes de rPr dentro de pPr.
            if "<w:rPr>" in ppr:
                return ppr.replace("<w:rPr>", '<w:jc w:val="left"/><w:rPr>', 1)
            return ppr.replace("</w:pPr>", '<w:jc w:val="left"/></w:pPr>', 1)
        tbl = re.sub(r"<w:pPr>.*?</w:pPr>", _jc, tbl, flags=re.S)
        filas = re.findall(r"<w:tr[ >].*?</w:tr>", tbl, flags=re.S)
        for n, fila in enumerate(filas):
            nueva = re.sub(r"<w:shd [^>]*/>", "", fila)
            relleno = TABLA_CAB if n == 0 else (TABLA_ALT if n % 2 == 0 else None)
            if relleno:
                shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{relleno}"/>'
                nueva = re.sub(r"<w:tcPr>", "<w:tcPr>" + shd, nueva)
                nueva = re.sub(r"<w:tc>(?!<w:tcPr>)", "<w:tc><w:tcPr>" + shd + "</w:tcPr>", nueva)
            if n == 0:
                nueva = re.sub(r"<w:rPr>", '<w:rPr><w:b/><w:color w:val="FFFFFF"/>', nueva)
                nueva = re.sub(r"<w:r>(?!<w:rPr>)", '<w:r><w:rPr><w:b/><w:color w:val="FFFFFF"/></w:rPr>', nueva)
            tbl = tbl.replace(fila, nueva, 1)
        return tbl

    xml = re.sub(r"<w:tbl>.*?</w:tbl>", tabla, xml, flags=re.S)
    archivos["word/document.xml"] = xml.encode("utf-8")
    tmp = docx.with_suffix(".tmp.docx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n, d in archivos.items():
            z.writestr(n, d)
    os.replace(tmp, docx)


def word_a_pdf(docx: Path, pdf: Path) -> None:
    """Actualiza el índice y los campos con Word y exporta a PDF."""
    import win32com.client  # type: ignore

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(str(docx))
        for toc in doc.TablesOfContents:
            toc.Update()
        doc.Fields.Update()
        doc.Save()
        doc.ExportAsFixedFormat(str(pdf), 17, OpenAfterExport=False, OptimizeFor=0,
                                CreateBookmarks=1, DocStructureTags=True)
        doc.Close(False)
    finally:
        word.Quit()


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    md = preparar_md()
    docx = SALIDA / f"{NOMBRE}.docx"
    try:
        subprocess.run([PANDOC, md.name, "-f", "markdown-implicit_figures+raw_attribute+fenced_divs",
                        "-o", str(docx), "--reference-doc", str(PLANTILLA), "--resource-path=.",
                        "--metadata", "lang=es-PE"], cwd=AQUI, check=True)
    finally:
        md.unlink(missing_ok=True)
    estilizar_tablas(docx)
    pdf = SALIDA / f"{NOMBRE}.pdf"
    word_a_pdf(docx.resolve(), pdf.resolve())
    print(f"OK {docx.name} ({docx.stat().st_size / 1e6:.1f} MB) y {pdf.name} ({pdf.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
