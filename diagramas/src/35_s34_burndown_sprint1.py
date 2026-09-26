"""DIAG-105. Burndown simulado según Tabla 27 S3-4; 2026-09-25."""
from pathlib import Path
import argparse
import subprocess
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib.colors import HexColor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--png', required=True)
    parser.add_argument('--svg', required=True)
    parser.add_argument('--dpi', type=int, default=180)
    args = parser.parse_args()
    d = Drawing(780, 470)
    ink, blue = HexColor('#263B50'), HexColor('#246782')
    def text(x, y, value, size=12):
        d.add(String(x, y, value, fontName='Helvetica', fontSize=size, fillColor=ink))
    text(45, 443, 'Burndown del Sprint 1', 22)
    text(45, 419, '01 al 14 de septiembre de 2026', 12)
    x = lambda day: 70 + day * 45
    y = lambda value: 92 + value * 20
    for value in range(0, 14, 2):
        d.add(Line(70,y(value),700,y(value),strokeColor=HexColor('#DCE3E8')))
        text(40,y(value)-4,str(value))
    real = [13,13,13,13,13,8,8,8,8,8,8,8,5,5,0]
    for day in range(15):
        text(x(day)-5,72,str(day),10)
        if day:
            d.add(Line(x(day-1),y(13-13*(day-1)/14),x(day),y(13-13*day/14),
                       strokeColor=HexColor('#8997A4'),strokeDashArray=[5,3],strokeWidth=2))
            d.add(Line(x(day-1),y(real[day-1]),x(day),y(real[day-1]),strokeColor=blue,strokeWidth=3))
            d.add(Line(x(day),y(real[day-1]),x(day),y(real[day]),strokeColor=blue,strokeWidth=3))
    text(50,382,'Puntos de historia pendientes')
    text(545,382,'Ideal: gris / Simulado: azul',10)
    text(245,275,'D5 Habilitadores -5',11)
    text(320,224,'D7 A05 retrasada',11)
    text(320,210,'Reunión simulada',11)
    text(555,203,'D12 HIST-1.3 -3',11)
    text(555,189,'Un día tarde',10)
    text(525,120,'D14 HIST-1.1 -5',11)
    text(345,49,'Día del sprint',12)
    text(45,20,'Escenario simulado de la Actividad 15; no son mediciones del equipo.',11)
    svg, png = Path(args.svg), Path(args.png)
    svg.parent.mkdir(parents=True,exist_ok=True)
    png.parent.mkdir(parents=True,exist_ok=True)
    renderSVG.drawToFile(d,str(svg))
    build=Path(__file__).resolve().parents[1]/'_build'/'cierre'
    build.mkdir(parents=True,exist_ok=True)
    pdf=build/'burndown.pdf'
    renderPDF.drawToFile(d,str(pdf))
    poppler=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
    subprocess.run([str(poppler),'-png','-singlefile','-r',str(args.dpi),str(pdf),str(png.with_suffix(''))],check=True)


if __name__ == '__main__':
    main()
