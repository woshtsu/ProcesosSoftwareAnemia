from _fig import *

def construir(corto):
    if corto:
        W, H, fs, tfs = 11, 6.19, 17, 17
    else:
        W, H, fs, tfs = 10, 5.4, 13.5, 13.5
    fig, ax = nuevo(W, H)
    texto(ax, W / 2, 0.3, "Despliegue en staging con Docker Compose y canal de integración continua",
          fs=tfs + 1.5, fontweight="bold")
    m, g = 0.25, (0.7 if corto else 0.6)
    bw = (W - 2 * m - 2 * g) / 3
    xs = [m + i * (bw + g) for i in range(3)]
    y1, h1 = (1.0, 1.9) if corto else (1.0, 1.7)
    y2, h2 = (3.75, 1.6) if corto else (3.45, 1.4)
    ax.add_patch(plt.Rectangle((0.1, y1 - 0.38), W - 0.2, h1 + 0.5, fc="#FBF3DF", ec="#B08A2E", lw=1.2))
    texto(ax, 0.25, y1 - 0.2, "GitHub Actions: flujo de integración continua (ci.yml)", fs=fs - 1, fontweight="bold", ha="left")
    ax.add_patch(plt.Rectangle((0.1, y2 - 0.38), W - 0.2, h2 + 0.5, fc="#F1F3F5", ec=BORDE, lw=1.2))
    texto(ax, 0.25, y2 - 0.2, "Host de staging: Docker Compose", fs=fs - 1, fontweight="bold", ha="left")
    if corto:
        caja(ax, xs[0], y1, bw, h1, "push o PR a main,\ndevelop o feature/**", "#FFFFFF", fs=fs, titulo="Disparador")
        caja(ax, xs[1], y1, bw, h1, "1. ruff\n2. pytest + cobertura\n3. PostgreSQL 16\n4. E2E Playwright\n5. SonarCloud*", "#E4F1EA", fs=fs - 1, titulo="Job calidad-y-pruebas", ha="left")
        caja(ax, xs[2], y1, bw, h1, "docker build\nsolo en main, tras\nel job anterior", "#E4F1EA", fs=fs, titulo="Job imagen-staging")
        caja(ax, xs[0], y2, bw, h2, "(PC o Android)", "#FFFFFF", fs=fs, titulo="Usuario")
        caja(ax, xs[1], y2, bw, h2, "Python 3.11, Uvicorn :8000\nHEALTHCHECK /api/salud", "#E6EEF7", fs=fs - 1, titulo="Contenedor api")
        caja(ax, xs[2], y2, bw, h2, "PostgreSQL 16\nVolumen datos_pg", "#C9DAEC", fs=fs, titulo="Contenedor db")
    else:
        caja(ax, xs[0], y1, bw, h1, "push o PR a main,\ndevelop o feature/**", "#FFFFFF", fs=fs, titulo="Disparador")
        caja(ax, xs[1], y1, bw, h1, "1. ruff (lint y formato)\n2. pytest + cobertura (SQLite)\n3. Integración PostgreSQL 16\n4. E2E con Playwright\n5. Artefactos y SonarCloud*", "#E4F1EA", fs=fs - 1, titulo="Job calidad-y-pruebas", ha="left")
        caja(ax, xs[2], y1, bw, h1, "docker build\nanemia-junin-pmv:sha\nsolo en main, tras el\njob anterior", "#E4F1EA", fs=fs, titulo="Job imagen-staging")
        caja(ax, xs[0], y2, bw, h2, "(PC o Android)", "#FFFFFF", fs=fs, titulo="Usuario")
        caja(ax, xs[1], y2, bw, h2, "python:3.11-slim\nUvicorn :8000, sin root\nHEALTHCHECK /api/salud", "#E6EEF7", fs=fs - 1, titulo="Contenedor api")
        caja(ax, xs[2], y2, bw, h2, "postgres:16-alpine\nVolumen datos_pg\nHEALTHCHECK pg_isready", "#C9DAEC", fs=fs - 1, titulo="Contenedor db")
    for i in range(2):
        flecha(ax, (xs[i] + bw, y1 + h1 / 2), (xs[i + 1], y1 + h1 / 2))
    texto(ax, xs[1] + bw + g / 2, y1 + h1 / 2 - 0.22, "si pasa", fs=fs - 5)
    # staging: usuario -> api -> db ; imagen del job2 hacia api
    flecha(ax, (xs[0] + bw, y2 + h2 / 2), (xs[1], y2 + h2 / 2))
    texto(ax, xs[0] + bw + g / 2, y2 + h2 / 2 - 0.22, "HTTP", fs=fs - 5)
    flecha(ax, (xs[1] + bw, y2 + h2 / 2), (xs[2], y2 + h2 / 2))
    texto(ax, xs[1] + bw + g / 2, y2 + h2 / 2 - 0.22, "SQL", fs=fs - 5)
    texto(ax, W / 2, H - 0.22, "*SonarCloud solo si hay SONAR_TOKEN. Fuente: elaboración propia (Tabla 28).",
          fs=11 if corto else 9.5, color=SUAVE)
    return fig, ax
