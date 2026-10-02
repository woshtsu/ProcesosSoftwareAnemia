"""Utilidades comunes para figuras matplotlib de S6 (cajas, flechas, CLI --png/--svg/--dpi).
Coordenadas en pulgadas, origen arriba-izquierda. Avisa si un texto desborda su caja."""
import argparse, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

RAIZ = Path(__file__).resolve().parents[2]
TINTA, SUAVE, BORDE = "#1F2D3D", "#4A5A6A", "#34506B"
plt.rcParams["font.family"] = ["Arial", "DejaVu Sans"]


def nuevo(w, h):
    fig = plt.figure(figsize=(w, h), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis("off")
    ax._cajas = []
    return fig, ax


def caja(ax, x, y, w, h, texto, fc="#E6EEF7", ec=BORDE, fs=12, dash=False, bold=False,
         color=TINTA, ha="center", lw=1.6, titulo=None, tfs=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08",
                                fc=fc, ec=ec, lw=lw, ls=(0, (5, 3)) if dash else "-"))
    tx = x + w / 2 if ha == "center" else x + 0.12
    t = None
    if titulo:
        tt = ax.text(tx, y + 0.1, titulo, ha=ha, va="top", fontsize=tfs or fs, fontweight="bold", color=color)
        ax._cajas.append((tt, x, y, w, h))
        t = ax.text(tx, y + 0.1 + (tfs or fs) * 1.35 / 72 * (titulo.count("\n") + 1) + 0.05, texto,
                    ha=ha, va="top", fontsize=fs, color=color, linespacing=1.25)
    else:
        t = ax.text(tx, y + h / 2, texto, ha=ha, va="center", fontsize=fs,
                    fontweight="bold" if bold else "normal", color=color, linespacing=1.25)
    ax._cajas.append((t, x, y, w, h))
    return t


def flecha(ax, p, q, dash=False, color=BORDE, lw=1.8, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=16, lw=lw, color=color,
                                 ls=(0, (5, 3)) if dash else "-", connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=0, shrinkB=0))


def texto(ax, x, y, s, fs=12, **kw):
    kw.setdefault("color", TINTA); kw.setdefault("va", "center"); kw.setdefault("ha", "center")
    return ax.text(x, y, s, fontsize=fs, **kw)


def verificar(fig, ax, nombre):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    mal = 0
    for t, x, y, w, h in ax._cajas:
        bb = t.get_window_extent(r)
        (x0, y1), (x1, y0) = inv.transform((bb.x0, bb.y0)), inv.transform((bb.x1, bb.y1))
        if x0 < x + 0.02 or x1 > x + w - 0.02 or y0 < y or y1 > y + h:
            mal += 1
            print(f"  AVISO {nombre}: desborda '{t.get_text()[:40]!r}' ({x0:.2f}-{x1:.2f} vs {x:.2f}-{x+w:.2f}; {y0:.2f}-{y1:.2f} vs {y:.2f}-{y+h:.2f})")
    return mal


def guardar(fig, ax, nombre):
    ap = argparse.ArgumentParser()
    ap.add_argument("--png"); ap.add_argument("--svg"); ap.add_argument("--dpi", type=int, default=200)
    a = ap.parse_args()
    verificar(fig, ax, nombre)
    png = a.png or str(RAIZ / "diagramas" / "png" / f"{nombre}.png")
    svg = a.svg or str(RAIZ / "diagramas" / "svg" / f"{nombre}.svg")
    fig.savefig(png, dpi=a.dpi, facecolor="white")
    fig.savefig(svg, format="svg", facecolor="white")
    print("ok", nombre)
