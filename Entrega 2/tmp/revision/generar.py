from pathlib import Path
from copy import deepcopy
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from contenido import REPORT,AUDIT
from diagramas import build,PDFDIR
import pypdfium2 as pdfium
import json

OUT=Path('output/entregable_integrador'); OUT.mkdir(parents=True,exist_ok=True)
for name,f in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/f)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic')
S={
 'title':ParagraphStyle('title',fontName='Arial-Bold',fontSize=18,leading=23,spaceAfter=17,textColor=colors.black),
 'h':ParagraphStyle('h',fontName='Arial-Bold',fontSize=11.5,leading=15,spaceBefore=8,spaceAfter=7,textColor=colors.black),
 'p':ParagraphStyle('p',fontName='Arial',fontSize=10.2,leading=14.3,spaceAfter=10),
 'cell':ParagraphStyle('cell',fontName='Arial',fontSize=9,leading=12),
 'head':ParagraphStyle('head',fontName='Arial-Bold',fontSize=9,leading=12,textColor=colors.white),
 'caption':ParagraphStyle('caption',fontName='Arial-Italic',fontSize=8.6,leading=11.5,spaceBefore=7,spaceAfter=12),
 'note':ParagraphStyle('note',fontName='Arial',fontSize=9.6,leading=13.2,spaceAfter=11,backColor=colors.HexColor('#EDF3F7'),borderPadding=8),
}
def para(s,style='p'):return Paragraph(escape(s).replace('\n','<br/>'),S[style])
DIAGRAMS=build()
def footer(c,d):
 c.saveState(); c.setFont('Arial',8);c.setFillColor(colors.HexColor('#5C6975'))
 c.drawString(45,25,'Anemia Junín · Procesos de Software · Revisión 25/09/2026')
 c.drawRightString(A4[0]-45,25,str(d.page));c.restoreState()
def make(pages,name):
 story=[]; md=[]
 for index,(title,blocks) in enumerate(pages):
  if index:story.append(PageBreak())
  story.append(para(title,'title')); md += ['# '+title,'']
  for block in blocks:
   k=block[0]
   if k in ('p','h','note'):
    story.append(para(block[1],k));md += [('## ' if k=='h' else '> ' if k=='note' else '')+block[1],'']
   elif k=='table':
    _,head,rows,widths=block
    widths=widths or [505/len(head)]*len(head)
    # Normalize authoring widths to printable area.
    widths=[v*505/sum(widths) for v in widths]
    cells=[[para(v,'head') for v in head]]+[[para(v,'cell') for v in r] for r in rows]
    tab=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#244863')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F6F8')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#244863')),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#D7E0E6'))]))
    story.extend([tab,Spacer(1,12)])
    md += ['| '+' | '.join(head)+' |','| '+' | '.join(['---']*len(head))+' |']
    md += ['| '+' | '.join(v.replace('\n','<br>') for v in r)+' |' for r in rows];md+=['']
   elif k=='fig':
    _,n,cap,mh=block; draw=deepcopy(DIAGRAMS[n]); scale=min(505/draw.width,mh/draw.height)
    draw.scale(scale,scale);draw.width*=scale;draw.height*=scale
    story.append(KeepTogether([draw,para(cap,'caption')]))
    md += [f'![{cap}](diagramas/{n}.svg)','',cap,'']
 doc=SimpleDocTemplate(str(OUT/(name+'.pdf')),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=45,bottomMargin=45,title=pages[0][0],author='Equipo de proyecto Anemia Junín',pageCompression=1)
 doc.build(story,onFirstPage=footer,onLaterPages=footer)
 (OUT/(name+'.md')).write_text('\n'.join(md),encoding='utf-8')
 pdf=pdfium.PdfDocument(str(OUT/(name+'.pdf')))
 qa=Path('tmp/revision/qa')/name;qa.mkdir(parents=True,exist_ok=True)
 for i in range(len(pdf)):
  pdf[i].render(scale=1.4).to_pil().save(qa/f'page-{i+1:02}.png')
 print(name,'expected',len(pages),'actual',len(pdf))

make(REPORT,'Informe_Integrador_Anemia_Junin_revision')
make(AUDIT,'Revision_Cumplimiento_y_Trazabilidad')
for n in DIAGRAMS:
 pdf=pdfium.PdfDocument(str(PDFDIR/(n+'.pdf')))
 pdf[0].render(scale=1.5).to_pil().save(OUT/'diagramas'/(n+'.png'))
