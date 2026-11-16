"""Ejecuta entregables/semana-13/exportar_pdf_s13.py en Linux usando Google Chrome en lugar de Edge.
Uso: python3 exportar_s13_linux.py <raiz_repo> [destino] [pdca|scm ...]"""
import sys, runpy, pathlib
raiz=pathlib.Path(sys.argv[1]); destino=sys.argv[2] if len(sys.argv)>2 and sys.argv[2] not in ("pdca","scm") else None
args=[a for a in sys.argv[2:] if a in ("pdca","scm")]
import playwright.sync_api as sa
orig=sa.sync_playwright
class P:
    def __enter__(self):
        self.cm=orig(); self.p=self.cm.__enter__()
        launch=self.p.chromium.launch
        def l(**kw):
            kw.pop("channel",None); kw["executable_path"]="/usr/bin/google-chrome"; return launch(**kw)
        self.p.chromium.launch=l; return self.p
    def __exit__(self,*a): return self.cm.__exit__(*a)
sa.sync_playwright=lambda: P()
g={}
sys.argv=["exportar_pdf_s13.py"]+args
mod=runpy.run_path(str(raiz/"entregables/semana-13/exportar_pdf_s13.py"),run_name="t026")
if destino: mod["DESTINO"]=pathlib.Path(destino); mod["main"].__globals__["DESTINO"]=pathlib.Path(destino)
mod["main"]()
