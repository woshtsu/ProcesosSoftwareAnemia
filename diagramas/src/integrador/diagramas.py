from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle, Ellipse
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from pathlib import Path
import math

# Rutas canonicas (ver coordinacion/RUTAS.md). ROOT = raiz del repositorio.
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'diagramas'/'svg'; OUT.mkdir(parents=True,exist_ok=True)
PNGDIR=ROOT/'diagramas'/'png'; PNGDIR.mkdir(parents=True,exist_ok=True)
PDFDIR=ROOT/'diagramas'/'_build'/'pdf'; PDFDIR.mkdir(parents=True,exist_ok=True)
INK=HexColor('#17324D'); BLUE=HexColor('#EAF2FA'); GREEN=HexColor('#E8F3EF'); GRAY=HexColor('#F1F3F5')

class Diagram:
 def __init__(self,name,h=600):
  self.name=name; self.h=h; self.d=Drawing(740,h)
  self.d.add(Rect(0,0,740,h,fillColor=white,strokeColor=None))
 def text(self,x,y,text,size=16,bold=False,anchor='middle',color=INK,bg=False):
  for i,line in enumerate(text.split('\n')):
   if bg:
    width=stringWidth(line,'Helvetica-Bold' if bold else 'Helvetica',size)
    left=x-width/2 if anchor=='middle' else x
    self.d.add(Rect(left-2,self.h-y-i*(size*1.22)-3,width+4,size+5,fillColor=white,strokeColor=None))
   self.d.add(String(x,self.h-y-i*(size*1.22),line,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,textAnchor=anchor,fillColor=color))
 def box(self,x,y,w,h,text,fill=BLUE,size=16,dash=False):
  self.d.add(Rect(x,self.h-y-h,w,h,rx=6,ry=6,fillColor=fill,strokeColor=INK,strokeWidth=1.2,strokeDashArray=[6,4] if dash else None))
  lines=text.count('\n')+1; self.text(x+w/2,y+(h-lines*size*1.22)/2+size,text,size)
 def frame(self,x,y,w,h,label,dash=True):
  self.d.add(Rect(x,self.h-y-h,w,h,fillColor=None,strokeColor=INK,strokeWidth=1.1,strokeDashArray=[6,4] if dash else None))
  self.text(x+12,y+23,label,15,True,'start')
 def edge(self,pts,label='',pos=None,dash=False,arrow=True,size=13,filled=False):
  for (x,y),(a,b) in zip(pts,pts[1:]):
   self.d.add(Line(x,self.h-y,a,self.h-b,strokeColor=INK,strokeWidth=1.35,strokeDashArray=[5,4] if dash else None))
  if arrow:
   (a,b),(x,y)=pts[-2:]; ang=math.atan2(y-b,x-a); r=9
   coords=[x-r*math.cos(ang-.45),self.h-(y-r*math.sin(ang-.45)),x,self.h-y,x-r*math.cos(ang+.45),self.h-(y-r*math.sin(ang+.45))]
   self.d.add(Polygon(coords,fillColor=INK if filled else None,strokeColor=INK,strokeWidth=1.35))
  if label and pos: self.text(*pos,label,size)
 def actor(self,x,y,label):
  self.d.add(Circle(x,self.h-y,12,fillColor=white,strokeColor=INK,strokeWidth=1.5))
  self.edge([(x,y+12),(x,y+50)],arrow=False); self.edge([(x-23,y+26),(x+23,y+26)],arrow=False)
  self.edge([(x,y+50),(x-22,y+77)],arrow=False); self.edge([(x,y+50),(x+22,y+77)],arrow=False)
  self.text(x,y+100,label,15)
 def oval(self,x,y,rx,ry,label,size=16):
  self.d.add(Ellipse(x,self.h-y,rx,ry,fillColor=BLUE,strokeColor=INK,strokeWidth=1.1))
  self.text(x,y-(label.count('\n'))*size*.6+size*.32,label,size)
 def save(self):
  renderSVG.drawToFile(self.d,str(OUT/(self.name+'.svg')))
  renderPDF.drawToFile(self.d,str(PDFDIR/(self.name+'.pdf')))
  return self.d

def build():
 ds={}
 a=Diagram('01_procesos_as_is_to_be',650)
 a.text(170,26,'AS-IS',22,True); a.text(555,26,'TO-BE',22,True)
 a.text(170,54,'Síntesis del entregable S1',14); a.text(555,54,'Propuesta por incrementos',14)
 left=['Familia acude a la posta','Personal mide y registra\nen soportes manuales','Personal transcribe\ny consolida información','Personal programa controles\ny busca inasistencias','Seguimiento reactivo\ny consolidación tardía']
 right=['Familia acude a la posta','INC-1 Personal captura datos\nSistema valida y guarda','INC-2 Agenda controles\nINC-3 Sincroniza registros','INC-4 Comunica recordatorios\ny registra barreras','INC-5 Prioriza con apoyo IA\nINC-6 Consolida indicadores']
 for i in range(5):
  y=83+i*101
  a.box(25,y,290,70,left[i],GRAY); a.box(410,y,305,70,right[i],GREEN if i<2 else GRAY)
  if i<4:
   a.edge([(170,y+70),(170,y+101)]); a.edge([(562,y+70),(562,y+101)])
 a.text(370,615,'La atención y decisión clínica permanecen a cargo del personal de salud.',15)
 ds[a.name]=a.save()

 a=Diagram('02_modelo_proceso',640)
 labels=['1 Entrada\nTO-BE y backlog','2 Planificación\nHistorias y tareas','3 Desarrollo\nDiseño y código','4 Integración\nRevisión y build','5 Pruebas\nEvidencias y DoD','6 Retroalimentación\nRevisión del incremento','7 Entrega\nVersión de pruebas','8 Medición\nProducto y resultado','9 Mejora\nRetrospectiva','10 Repetición\nSiguiente sprint']
 coords=[]
 for i,l in enumerate(labels):
  row=i//2; col=i%2 if row%2==0 else 1-i%2; x=60+col*390; y=35+row*111; coords.append((x,y))
  a.box(x,y,230,76,l,size=17)
 for i in range(9):
  x,y=coords[i]; xx,yy=coords[i+1]
  if y==yy: a.edge([(x+230 if xx>x else x,y+38),(xx if xx>x else xx+230,yy+38)])
  else: a.edge([(x+115,y+76),(xx+115,yy)])
 a.edge([(680,517),(719,517),(719,73),(680,73)])
 a.text(370,602,'Si fallan pruebas o aceptación, corregir y volver a verificar antes de entregar.',14)
 a.text(370,623,'MLOps se activa en INC-5; la sincronización distribuida se prueba desde INC-3.',14)
 ds[a.name]=a.save()

 a=Diagram('03_c4_contexto',420)
 a.box(20,70,220,100,'Personal de salud\n[Persona]\nRegistra y consulta',GRAY)
 a.box(20,265,220,100,'Coordinador del proyecto\n[Persona]\nConsulta calidad del dato',GRAY,15)
 a.box(425,145,285,145,'PMV Anemia Junín\n[Sistema de software]\nRegistro nominal validado\ny expediente digital',GREEN,17)
 a.edge([(240,120),(330,120),(330,183),(425,183)],'Registra y consulta',(338,98))
 a.edge([(240,315),(330,315),(330,252),(425,252)],'Solicita reporte',(337,343))
 a.text(370,400,'Alcance INC-1. No hay interacción externa con HIS, WhatsApp o IA en esta vista.',14)
 ds[a.name]=a.save()

 a=Diagram('04_c4_contenedores',550)
 a.box(25,35,225,92,'Personal de salud\ny coordinador\n[Personas]',GRAY)
 a.frame(285,15,425,475,'Sistema PMV Anemia Junín')
 a.box(345,125,305,135,'Aplicación web y API\n[Contenedor: Python / Flask]\nHTML con Jinja2 y REST/JSON\nEjecuta los casos de uso',GREEN,17)
 a.box(345,360,305,90,'Base de datos del PMV\n[Almacén: archivo SQLite]\nExpedientes, dosajes e intentos',BLUE,16)
 a.edge([(250,80),(300,80),(300,177),(345,177)],'Navegador\nHTTP local',(190,207),size=15)
 a.edge([(497,260),(497,360)],'Lee y escribe mediante\nsqlite3 / SQL en proceso',(610,303),size=14)
 a.text(370,523,'Jinja2 y REST comparten el mismo proceso. SQLite no es un servidor de red.',15)
 ds[a.name]=a.save()

 a=Diagram('05_c4_componentes',790)
 a.frame(15,20,710,665,'Contenedor aplicación web y API del PMV')
 a.box(55,75,275,95,'Adaptador Web\n[Flask / Jinja2]\nFormularios y vistas',size=17)
 a.box(410,75,275,95,'Adaptador REST\n[Flask / JSON]\nOperaciones de API',size=17)
 a.box(220,265,300,100,'Servicio de expedientes\n[Python / aplicación]\nOrquesta casos de uso',GREEN,17)
 a.edge([(190,170),(190,210),(300,210),(300,265)],'GestionExpedientes',(166,235))
 a.edge([(547,170),(547,210),(440,210),(440,265)],'GestionExpedientes',(578,235))
 a.box(30,480,210,110,'Persistencia SQLite\n[Python / sqlite3]\nExpedientes, dosajes\ne intentos',size=16)
 a.box(270,480,210,110,'Reglas de dominio\n[Python puro]\nValida y clasifica\nsin acceso a E/S',GREEN,16)
 a.box(510,480,200,110,'Normativa y reloj\n[Python / JSON]\nConfiguración y\nfecha de referencia',size=16)
 a.edge([(270,365),(270,402),(135,402),(135,480)],'NinoRepositorio',(135,385))
 a.edge([(370,365),(370,480)],'Evalúa',(409,451))
 a.edge([(470,365),(470,402),(610,402),(610,480)],'ProveedorNormativa\nReloj',(610,374),size=12)
 a.box(30,700,210,65,'Archivo SQLite\n[Almacén externo al proceso]',GRAY,13)
 a.edge([(135,590),(135,700)],'SQL / sqlite3',(202,647))
 a.text(470,635,'Flechas: llamadas durante la ejecución.',14)
 a.text(470,656,'El servicio usa puertos; bootstrap inyecta adaptadores.',12)
 a.text(470,728,'Dependencias de código: adaptadores hacia puertos del núcleo.',12)
 a.text(470,750,'Esta vista no convierte cada componente en un microservicio.',12)
 ds[a.name]=a.save()

 a=Diagram('06_casos_de_uso',760)
 a.frame(175,15,550,660,'Sistema PMV Anemia Junín',dash=False)
 a.actor(66,197,'Personal\nde salud')
 a.actor(66,555,'Coordinador')
 ys=[92,188,284,380,476]
 labs=['UC-01 Registrar niño','UC-02 Consultar\nexpediente','UC-03 Actualizar\nexpediente','UC-04 Registrar dosaje','UC-05 Listar y filtrar\nseguimiento']
 for y,l in zip(ys,labs):
  a.oval(340,y,135,32,l,15)
  a.edge([(90,235),(205,y)],arrow=False)
 a.oval(340,605,135,34,'UC-06 Generar reporte\ndel periodo',15)
 a.edge([(90,593),(205,605)],arrow=False)
 a.oval(608,284,98,45,'UC-07 Validar\ndatos de entrada',14)
 a.edge([(470,92),(608,92),(608,239)],'«include»',(650,170),dash=True)
 a.edge([(475,284),(510,284)],'«include»',(493,262),dash=True,size=11)
 a.edge([(470,380),(608,380),(608,329)],'«include»',(657,366),dash=True)
 a.text(370,706,'Asociación sólida sin flecha: actor participante. Include: comportamiento obligatorio.',13)
 a.text(370,729,'Los actores representan roles de uso; este modelo no acredita control de acceso.',13)
 ds[a.name]=a.save()

 a=Diagram('07_despliegue',500)
 a.frame(25,30,690,420,'Equipo de demostración local [dispositivo]')
 a.box(70,90,225,100,'Navegador web\n[Entorno de ejecución]\nFormularios y consultas',GRAY,16)
 a.box(415,90,260,100,'Proceso Python\n[Flask / Werkzeug]\nAplicación web y API',GREEN,17)
 a.edge([(295,140),(415,140)],'HTTP\nlocalhost:8000',(355,100),size=13)
 a.box(420,315,250,80,'data/pmv.db\n[Artefacto SQLite]',size=17)
 a.box(65,315,285,80,'config/norma_nts213_2024.json\n[Artefacto de configuración]',size=14)
 a.edge([(545,190),(545,315)],'SQL / sqlite3',(606,260))
 a.edge([(463,190),(463,240),(207,240),(207,315)],'Lee configuración',(296,229))
 a.text(370,477,'Topología local documentada. Puerto y rutas deben contrastarse con el repositorio.',14)
 ds[a.name]=a.save()

 a=Diagram('08_modelo_datos',570)
 a.box(20,50,300,225,'nino\nPK id\nUK dni\nnombres y apellidos\nfecha_nacimiento, sexo\npeso_kg, distrito, altitud_msnm\ncuidador, activo\ncreado_en, actualizado_en',BLUE,16)
 a.box(420,50,300,255,'dosaje_hemoglobina\nPK id\nFK nino_id\nfecha_dosaje\nhb_observada, hb_ajustada\naltitud_msnm, ajuste_altitud\nclasificacion, norma_version\nadvertencias, creado_en',GREEN,16)
 a.edge([(320,160),(420,160)],arrow=False)
 a.text(339,148,'1',16,True); a.text(394,148,'0..*',16,True)
 a.box(220,375,300,130,'intento_registro\nPK id / ocurrido_en\ntipo / resultado / codigos_error\nSin datos personales',GRAY,16)
 a.text(370,543,'Modelo conceptual basado en la Figura 4 del avance. Restricciones pendientes de DDL.',14)
 ds[a.name]=a.save()

 a=Diagram('09_secuencia_registro',690)
 xs=[70,260,450,650]
 heads=['Personal','Entrada Web/API','Servicio','Repositorio SQLite']
 for x,h in zip(xs,heads):
  a.box(x-67,20,134,55,h,GRAY,13)
  a.edge([(x,75),(x,650)],dash=True,arrow=False)
 a.edge([(70,115),(260,115)],'1 Enviar datos',(165,103),filled=True)
 a.edge([(260,166),(450,166)],'2 Solicitar registro',(355,154),filled=True)
 a.edge([(450,210),(485,210),(485,237),(450,237)],arrow=True,filled=True)
 a.text(590,221,'3 Validar con dominio',13,bg=True)
 a.frame(18,272,705,360,'alt',dash=False)
 a.text(34,320,'[datos inválidos]',13,True,'start',bg=True)
 a.edge([(450,351),(260,351)],'Errores por campo',(355,338),dash=True)
 a.edge([(260,390),(70,390)],'Formulario con errores / API 400',(170,378),dash=True,size=11)
 a.edge([(18,419),(723,419)],dash=True,arrow=False)
 a.text(34,446,'[datos válidos y DNI nuevo]',13,True,'start',bg=True)
 a.edge([(450,478),(650,478)],'4 Guardar expediente',(550,466),filled=True)
 a.edge([(650,523),(450,523)],'5 Confirmación',(550,511),dash=True)
 a.edge([(450,559),(260,559)],'6 Resultado',(355,547),dash=True)
 a.edge([(260,610),(70,610)],'7 Confirmación UI / API 201',(170,598),dash=True,size=11)
 a.text(370,680,'Alternativa adicional: DNI duplicado produce conflicto 409. No se crea otro expediente.',13)
 ds[a.name]=a.save()
 return ds

if __name__=='__main__': build()
