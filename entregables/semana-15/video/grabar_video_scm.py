"""Graba el video de la Unidad IV (gestión de configuración) del proyecto Anemia Junín.

Composición final (~5 min, 1920x1080):
  1. Portada (generada).
  2. Tramo del software en producción: 4 cortes del video del 09/11/2026
     (entregables/semana-12/video/demo_anemia_junin_v4.mp4).
  3. Recorrido SCM por las páginas públicas del repositorio en GitHub (grabado aquí
     con Playwright + Edge sin interfaz; no necesita iniciar sesión).
  4. Cierre (generado).

Uso (desde la raíz del repositorio):
    pmv_fastapi/.venv/Scripts/python.exe entregables/semana-15/video/grabar_video_scm.py

Salida: entregables/semana-15/video/Porras-Auqui-Huamani-video-unidad-IV.mp4 y
tiempos_escenas.json (para el guion de locución del Anexo C).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
TMP = AQUI / "_tmp"
REPO = "https://github.com/woshtsu/ProcesosSoftwareAnemia"
VIDEO_SW = RAIZ / "entregables/semana-12/video/demo_anemia_junin_v4.mp4"
SALIDA = AQUI / "Porras-Auqui-Huamani-video-unidad-IV.mp4"
W, H = 1920, 1080
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Cortes del video del software (inicio, duración en s) según GUION_LOCUCION.md de S12.
CORTES_SW = [
    ("PMV · validación y registro con ajuste por altitud", 16, 27),
    ("Incremento 2 · agenda normativa del niño", 107, 11),
    ("Incremento 3 · registro sin conexión", 165, 17),
    ("Incremento 4 · alerta por barreras críticas", 283, 20),
]

# Escenas SCM: (rótulo, leyenda, url, segundos, desplazamiento total en px)
ESCENAS = [
    ("3.4.1 Administración del cambio", "Solicitudes de cambio (RFC) registradas en GitHub Issues con la plantilla change_request.md y su etiqueta de evaluación.",
     f"{REPO}/issues?q=label%3Achange-request", 9, 300),
    ("3.4.1 Administración del cambio", "RFC #18: módulo afectado, impacto, riesgo y criterios de aceptación; el Leader la evaluó con la etiqueta «aprobado».",
     f"{REPO}/issues/18", 14, 900),
    ("3.4.1 Administración del cambio", "Plantilla de solicitud de cambio versionada en .github/ISSUE_TEMPLATE/change_request.md.",
     f"{REPO}/blob/main/.github/ISSUE_TEMPLATE/change_request.md", 8, 500),
    ("3.4.1 Revisión por pares", "PR #36: plantilla con Definición de Terminado, vínculo al cambio y revisión «Approved» de un par antes de integrar en develop.",
     f"{REPO}/pull/36", 16, 1100),
    ("3.4.1 Revisión por pares", "Historial de pull requests: todo cambio entra por PR; desde el ruleset, develop y main exigen 1 aprobación.",
     f"{REPO}/pulls?q=is%3Apr", 9, 500),
    ("3.4.2 Gestión de versiones · GitFlow", "Solo quedan main (producción) y develop (integración); 17 ramas integradas se limpiaron con una etiqueta de respaldo.",
     f"{REPO}/branches/all", 8, 0),
    ("3.4.2 Gestión de versiones · GitFlow", "PR #31: release de develop a main, después de integrar T-024 (#29) y T-025 (#30) en develop.",
     f"{REPO}/pull/31", 11, 700),
    ("3.4.2 Gestión de versiones · SemVer", "Etiquetas semánticas por incremento: v1.0-PMV, v2.0-Inc2, v3.0-Inc3, v4.0-Inc4 y el parche v4.0.1.",
     f"{REPO}/tags", 8, 300),
    ("3.4.2 GitHub Releases", "Release v4.0.1 (PATCH): notas de versión y artefacto reportes-calidad con 690 pruebas y 99,46 % de cobertura.",
     f"{REPO}/releases/tag/v4.0.1", 14, 800),
    ("3.4.3 Construcción del sistema · CI/CD", "GitHub Actions: cada PR ejecuta Ruff, pruebas unitarias, de integración, de arquitectura y E2E, y construye la imagen Docker.",
     f"{REPO}/actions", 9, 300),
    ("3.4.3 Construcción del sistema · CI/CD", "PR #29: el pipeline detectó un error de formato (Ruff) y bloqueó el cambio hasta corregirlo…",
     f"{REPO}/actions/runs/43675155453", 8, 0),
    ("3.4.3 Construcción del sistema · CI/CD", "…y tras la corrección pasó en verde: calidad-y-pruebas e imagen; producción solo se ejecuta en main.",
     f"{REPO}/actions/runs/43675249154", 8, 0),
    ("3.4.3 Construcción del sistema · CI/CD", "ci.yml: disparadores con filtro de rutas (solo cambios del software) y trabajos encadenados hasta el despliegue en Render.",
     f"{REPO}/blob/main/.github/workflows/ci.yml", 12, 1400),
]

BANDA_JS = """([rotulo, leyenda]) => {
  for (const id of ['__banda', '__leyenda']) document.getElementById(id)?.remove();
  const b = document.createElement('div'); b.id = '__banda';
  b.textContent = 'Anemia Junín · Unidad IV · ' + rotulo;
  Object.assign(b.style, {position:'fixed', top:'0', left:'0', right:'0', zIndex:2147483647, background:'#1F3864',
    color:'#fff', font:'600 22px Segoe UI, Arial', padding:'10px 24px', boxShadow:'0 2px 6px rgba(0,0,0,.3)'});
  const l = document.createElement('div'); l.id = '__leyenda'; l.textContent = leyenda;
  Object.assign(l.style, {position:'fixed', bottom:'24px', left:'50%', transform:'translateX(-50%)', maxWidth:'1500px',
    zIndex:2147483647, background:'rgba(17,24,39,.88)', color:'#fff', font:'500 24px Segoe UI, Arial',
    padding:'14px 26px', borderRadius:'10px', textAlign:'center', lineHeight:'1.35'});
  document.body.append(b, l);
}"""

TARJETA = """<html><body style="margin:0;width:1920px;height:1080px;display:flex;align-items:center;justify-content:center;
background:linear-gradient(135deg,#1F3864,#2E75B6);font-family:Segoe UI,Arial;color:#fff">
<div style="text-align:center;max-width:1500px">{contenido}</div></body></html>"""

PORTADA = TARJETA.format(contenido="""
<div style="font-size:30px;opacity:.85">Universidad Continental · Procesos de Software (ASUC01702) · 2026-20</div>
<div style="font-size:72px;font-weight:700;margin:28px 0 12px">Anemia Junín</div>
<div style="font-size:40px">Unidad IV · Gestión de configuración de software</div>
<div style="font-size:28px;margin-top:36px;opacity:.9">Software en producción (v4.0.1) · cambios, versiones y construcción con la suite de GitHub</div>
<div style="font-size:26px;margin-top:40px;opacity:.85">Porras Veli, Ricardo · Auqui Huincho, Tania Tifani · Huamani Rodriguez, Jean Piero</div>""")

CIERRE = TARJETA.format(contenido="""
<div style="font-size:52px;font-weight:700;margin-bottom:30px">Trazabilidad de la configuración</div>
<div style="font-size:34px;line-height:1.7">Cambio (RFC en Issues) → Rama (GitFlow) → Pull request revisada por un par<br>
→ CI en verde → Etiqueta SemVer → Release con artefactos → Despliegue en Render</div>
<div style="font-size:26px;margin-top:40px;opacity:.85">github.com/woshtsu/ProcesosSoftwareAnemia</div>""")


def ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    base = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    for p in base.glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"):
        return str(p)
    sys.exit("No se encontró ffmpeg.")


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-2000:])
        sys.exit(f"Falló: {' '.join(cmd[:4])}…")


def grabar_web(nav, nombre: str, accion) -> Path:
    """Graba una sesión de navegador a webm y devuelve la ruta."""
    ctx = nav.new_context(viewport={"width": W, "height": H}, record_video_dir=str(TMP / nombre),
                          record_video_size={"width": W, "height": H}, locale="es-PE", device_scale_factor=1)
    pg = ctx.new_page()
    accion(pg)
    video = pg.video
    ctx.close()
    return Path(video.path())


def escenas_scm(pg) -> None:
    tiempos = []
    t0 = time.monotonic()
    for rotulo, leyenda, url, seg, despl in ESCENAS:
        pg.goto(url, wait_until="domcontentloaded", timeout=60_000)
        try:
            pg.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:  # noqa: BLE001 - GitHub mantiene conexiones abiertas
            pass
        pg.evaluate(BANDA_JS, [rotulo, leyenda])
        inicio = time.monotonic() - t0
        pasos = max(1, int(seg * 4))
        for i in range(pasos):
            if despl:
                pg.mouse.wheel(0, despl / pasos)
            pg.wait_for_timeout(250)
        tiempos.append({"rotulo": rotulo, "leyenda": leyenda, "url": url,
                        "inicio_s": round(inicio, 1), "duracion_s": round(time.monotonic() - t0 - inicio, 1)})
    (TMP / "tiempos_scm.json").write_text(json.dumps(tiempos, ensure_ascii=False, indent=1), encoding="utf-8")


def tarjeta(html: str, segundos: int):
    def accion(pg):
        pg.set_content(html)
        pg.wait_for_timeout(segundos * 1000)
    return accion


def main() -> None:
    ff = ffmpeg()
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    with sync_playwright() as p:
        nav = p.chromium.launch(channel="msedge", headless=True)
        w_portada = grabar_web(nav, "portada", tarjeta(PORTADA, 9))
        w_scm = grabar_web(nav, "scm", escenas_scm)
        w_cierre = grabar_web(nav, "cierre", tarjeta(CIERRE, 9))
        nav.close()

    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p"
    partes = []

    def norm(entrada: Path, salida: Path, extra: list[str] | None = None, recorte_inicial: float = 0.0) -> None:
        cmd = [ff, "-y"] + (["-ss", str(recorte_inicial)] if recorte_inicial else []) + ["-i", str(entrada)] + (extra or []) + [
            "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(salida)]
        run(cmd)

    # Las grabaciones de Playwright empiezan con ~0,5 s en blanco: se recortan.
    norm(w_portada, TMP / "p1.mp4", recorte_inicial=0.6)
    partes.append(TMP / "p1.mp4")
    for i, (_, ini, dur) in enumerate(CORTES_SW):
        out = TMP / f"sw{i}.mp4"
        run([ff, "-y", "-ss", str(ini), "-t", str(dur), "-i", str(VIDEO_SW), "-vf", vf, "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(out)])
        partes.append(out)
    norm(w_scm, TMP / "p3.mp4", recorte_inicial=0.6)
    partes.append(TMP / "p3.mp4")
    norm(w_cierre, TMP / "p4.mp4", recorte_inicial=0.6)
    partes.append(TMP / "p4.mp4")

    lista = TMP / "lista.txt"
    lista.write_text("".join(f"file '{p.as_posix()}'\n" for p in partes), encoding="utf-8")
    run([ff, "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", "-movflags", "+faststart", str(SALIDA)])

    # Tiempos absolutos de cada escena para el guion.
    def dur(path: Path) -> float:
        probe = Path(ff).with_name("ffprobe" + Path(ff).suffix)
        r = subprocess.run([str(probe), "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(path)], capture_output=True, text=True)
        return float(r.stdout.strip())

    t = 0.0
    linea = [{"parte": "Portada", "inicio_s": 0.0, "duracion_s": round(dur(partes[0]), 1)}]
    t += dur(partes[0])
    for (rot, _, _), pth in zip(CORTES_SW, partes[1:5]):
        d = dur(pth)
        linea.append({"parte": "Software · " + rot, "inicio_s": round(t, 1), "duracion_s": round(d, 1)})
        t += d
    base_scm = t
    for e in json.loads((TMP / "tiempos_scm.json").read_text(encoding="utf-8")):
        linea.append({"parte": e["rotulo"], "leyenda": e["leyenda"], "url": e["url"],
                      "inicio_s": round(base_scm + max(0.0, e["inicio_s"] - 0.6), 1), "duracion_s": e["duracion_s"]})
    t += dur(partes[5])
    linea.append({"parte": "Cierre: trazabilidad", "inicio_s": round(t, 1), "duracion_s": round(dur(partes[6]), 1)})
    total = dur(SALIDA)
    (AQUI / "tiempos_escenas.json").write_text(json.dumps({"duracion_total_s": round(total, 1), "escenas": linea},
                                                         ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK {SALIDA.name}  {total:.1f} s  ({SALIDA.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
