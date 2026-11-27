"""Capturas de evidencia T-026 (antes/después).
Uso:
  capturar.py pdf  <archivo.pdf> "<texto>" <salida.png> [pagina]
  capturar.py md   <archivo.md>  "<texto>" <salida.png>
  capturar.py html <archivo.html> "<texto>" <salida.png>
  capturar.py cmd  "<comando shell>" <salida.png> [titulo]   (salida de terminal como imagen)
El texto se resalta con un recuadro rojo; si no aparece, el script falla (código 2).
"""
import sys, subprocess, tempfile, os, html as H, pathlib
modo=sys.argv[1]
MARG=140
def pdf(f,txt,out,pag=None):
    import pymupdf
    d=pymupdf.open(f)
    pages=[int(pag)-1] if pag else range(len(d))
    for i in pages:
        p=d[i]; r=p.search_for(txt)
        if r:
            a=r[0]
            for x in r[1:]:
                if abs(x.y0-a.y0)<40: a|=x
            shape=p.new_shape(); shape.draw_rect(a+(-3,-3,3,3)); shape.finish(color=(0.85,0,0),width=1.6); shape.commit()
            clip=pymupdf.Rect(p.rect.x0, max(0,a.y0-MARG), p.rect.x1, min(p.rect.y1,a.y1+MARG))
            pix=p.get_pixmap(clip=clip,dpi=150); pix.save(out)
            print(f"OK pág. {i+1} -> {out}"); return
    print("NO ENCONTRADO:",txt); sys.exit(2)
def navegar(url,txt,out):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path="/usr/bin/google-chrome",headless=True)
        pg=b.new_page(viewport={"width":1100,"height":900})
        pg.goto(url,wait_until="load")
        js="""(t)=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
          while(n=w.nextNode()){if(n.parentElement.closest('#t026hdr'))continue;const i=n.textContent.indexOf(t);if(i>=0){const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+t.length);
          const rc=r.getBoundingClientRect();const m=document.createElement('div');
          Object.assign(m.style,{position:'absolute',left:(rc.left+scrollX-4)+'px',top:(rc.top+scrollY-3)+'px',width:(rc.width+8)+'px',height:(rc.height+6)+'px',border:'2px solid #d00',zIndex:99999,pointerEvents:'none'});
          document.body.appendChild(m);return [rc.top+scrollY,rc.height];}}return null;}"""
        res=pg.evaluate(js,txt)
        if not res:
            # búsqueda normalizada (espacios)
            print("NO ENCONTRADO:",txt); b.close(); sys.exit(2)
        top,h=res
        H_=pg.evaluate("document.documentElement.scrollHeight")
        pg.set_viewport_size({"width":1100,"height":int(min(H_,max(900,top+h+400)))})
        y=max(0,top-180); hh=min(h+360,H_-y)
        pg.screenshot(path=out,clip={"x":0,"y":y,"width":1100,"height":hh},full_page=True)
        b.close(); print("OK ->",out)
def md(f,txt,out):
    f=os.path.abspath(f); d=os.path.dirname(f)
    tmp=os.path.join(d,".t026_tmp_render.html")
    css="<style>body{font-family:'DejaVu Sans',Arial,sans-serif;font-size:14px;max-width:1040px;margin:20px auto;padding:0 20px}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:3px 6px}img{max-width:100%}</style>"
    body=subprocess.run(["pandoc",f,"-f","gfm","-t","html","--wrap=none"],capture_output=True,text=True,check=True).stdout
    hdr=f"<div id='t026hdr' style='background:#eef;padding:4px 8px;font:12px monospace'>Fuente: {H.escape(os.path.relpath(f,'/home/claude/procesossoftwareanemia'))}</div>"
    open(tmp,"w",encoding="utf-8").write("<meta charset=utf-8>"+css+hdr+body)
    try: navegar(pathlib.Path(tmp).as_uri(),txt,out)
    finally: os.remove(tmp)
def cmd(c,out,tit=None):
    r=subprocess.run(c,shell=True,capture_output=True,text=True,cwd="/home/claude/procesossoftwareanemia")
    s=f"$ {c}\n{r.stdout}{r.stderr}"
    tmp=tempfile.mktemp(suffix=".html")
    open(tmp,"w").write(f"<meta charset=utf-8><body style='margin:0;background:#1e1e1e'><div style='color:#9cdcfe;font:13px DejaVu Sans Mono;padding:6px 10px;background:#333'>{H.escape(tit or 'Terminal — repositorio ProcesosSoftwareAnemia')}</div><pre style='color:#ddd;font:13px/1.35 DejaVu Sans Mono;padding:10px;margin:0;white-space:pre-wrap'>{H.escape(s)}</pre>")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path="/usr/bin/google-chrome",headless=True)
        pg=b.new_page(viewport={"width":1100,"height":200}); pg.goto("file://"+tmp)
        pg.screenshot(path=out,full_page=True); b.close()
    os.remove(tmp); print("OK ->",out)
if modo=="pdf": pdf(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5] if len(sys.argv)>5 else None)
elif modo=="md": md(sys.argv[2],sys.argv[3],sys.argv[4])
elif modo=="html": navegar(pathlib.Path(os.path.abspath(sys.argv[2])).as_uri(),sys.argv[3],sys.argv[4])
elif modo=="cmd": cmd(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else None)
