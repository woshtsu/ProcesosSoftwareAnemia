"""Ejecuta un exportador del repositorio (que usa Playwright o busca Chrome/Edge en rutas de Windows)
en Linux con /usr/bin/google-chrome y fuentes métricamente equivalentes a las de Windows.
Uso: FONTCONFIG_FILE=/home/claude/t026/fonts-win.conf python3 ejecutar_exportador.py <script.py> [args...]
"""
import sys, runpy, os
os.environ.setdefault("NAVEGADOR", "/usr/bin/google-chrome")
os.environ.setdefault("FONTCONFIG_FILE", "/home/claude/t026/fonts-win.conf")
import playwright.sync_api as sa
orig = sa.sync_playwright
class P:
    def __enter__(self):
        self.cm = orig(); self.p = self.cm.__enter__()
        launch = self.p.chromium.launch
        def l(*a, **kw):
            kw.pop("channel", None); kw["executable_path"] = "/usr/bin/google-chrome"; return launch(*a, **kw)
        self.p.chromium.launch = l; return self.p
    def __exit__(self, *a): return self.cm.__exit__(*a)
sa.sync_playwright = lambda: P()
script = sys.argv[1]; sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
