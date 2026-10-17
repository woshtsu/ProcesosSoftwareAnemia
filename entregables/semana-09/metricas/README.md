# Métricas GQM de la semana 9 (Procesos de Software)

Evaluación GQM del avance del Proyecto «Anemia Junín» con datos 100 % sintéticos. Compara el **Incremento 1** (v1.0-PMV, copia de trabajo creada con `git worktree add ../inc1_v1.0_PMV v1.0-PMV`) con el **avance del Incremento 2** (v1.5.0-inc2-avance, `pmv_fastapi/`). Fecha de las mediciones: 16/10/2026 (hora de Perú). Cada número del informe sale de una ejecución real guardada en `datos/` o `salidas/`.

## Resultado en una tabla (de `datos/resumen_gqm.json`)

| Métrica | Inc. 1 | Inc. 2 (avance) | Meta Inc. 1 / Inc. 2 | ¿Cumple? (Inc. 1 / Inc. 2) |
|---|---|---|---|---|
| M1.1 Contaminación del dominio | 0,0 % | 0,0 % | 0 % / 0 % | Sí / Sí |
| M1.2 Conformidad hexagonal (estricta) | 40,0 % (laxa 60,0 %) | 100,0 % | 100 % / 100 % | No / Sí |
| M2.1 RF con captura aprobada | 100,0 % (5/5) | 100,0 % (2/2 entregados); 50,0 % (2/4 del alcance total) | 100 % / 100 % | Sí / Sí (sobre lo entregado) |
| M2.2 Defectos funcionales por RF | 1,4 Def/RF (7/5) | 0,0 Def/RF (0/2) | ≤ 1,0 / ≤ 0,2 | No / Sí |
| M3.1 Brechas resueltas (de 6) | 25,0 % | 33,3 % | ≥ 60 % / ≥ 90 % | No / No |
| M3.2 Índice de impacto en valor | 57,6 % | 100,0 % | ≥ 50 % / ≥ 80 % | Sí / Sí |

La variación porcentual y las variantes (laxa, solo detectados antes de liberar, brechas comprometidas en el plan, etc.) están en `datos/resumen_gqm.json`.

## Scripts (`herramientas/gqm/`)

| Script | Qué hace | Salida |
|---|---|---|
| `comun.py` | Rutas de cada versión, capas hexagonales, conteo de líneas (KLOC) y análisis de importaciones por AST. | (biblioteca) |
| `m11_contaminacion.py` | M1.1: importaciones de librerías externas en el dominio / clases del dominio. | `datos/m11_contaminacion.json` |
| `m12_conformidad.py` | M1.2: conformidad de los 5 componentes hexagonales (ubicación y contenido). Informa criterio estricto y laxo. | `datos/m12_conformidad.json` |
| `m13_acoplamiento.py` | Complemento: acoplamiento eferente/aferente por capa y violaciones de la regla de dependencia. | `datos/m13_acoplamiento.json` |
| `m21_cobertura_rf.py` | Cobertura de RF por pruebas automatizadas y criterios Dado-Cuando-Entonces; ejecuta las pruebas de cada versión. | `datos/m21_cobertura_rf.json`, `salidas/*/m21_criterios_dce.*` |
| `generar_dataset.py` | Dataset sintético B150 (150 niños, semilla 20261016, con casos frontera). | `datos/dataset_B150.json` |
| `oraculo_agenda.py` | Oráculo independiente de la agenda normativa (verdad de referencia de V2 y V3). | (biblioteca) |
| `servidor.sh` | Arranca/detiene uvicorn (un proceso, sin `--reload`, SQLite) de cada versión. | — |
| `cargar_dataset_api.py` | Carga el mismo dataset en cualquier versión usando solo la API pública. | — |
| `m32_valor.py` | Indicadores V1, V2, V3 por HTTP contra servidores reales. | `datos/m32_v1.0_B150.json`, `datos/m32_v1.5_B150.json` |
| `locust_comun.py`, `locust_v15_agenda.py` | Perfiles de carga: mix común del Inc. 1 y mix ampliado con agenda y alertas. | — |
| `sonda_salud.py` | Sonda `GET /api/salud` cada 1 s; disponibilidad = respuestas 200 en < 2 s / sondas. | CSV/JSON en `salidas/carga/` |
| `ejecutar_carga.py` | Orquesta la carga comparativa (base nueva, mismo dataset, sonda en paralelo, 2 repeticiones) y la sesión de disponibilidad de 10 min; resume. | `datos/m32_carga.json`, `datos/m32_disponibilidad.json`, `salidas/carga/*` |
| `exploratorias_inc2.py` | 45 pruebas exploratorias de caja negra sobre agenda y alertas (y entradas límite heredadas). | `datos/exploratorias_inc2.json`, `exploratorias_inc2.md`, `salidas/exploratorias_inc2_resultado*.txt` |
| `m22_defectos.py` | M2.2: clasifica DEF-01..08 (funcional / no funcional, RF afectado), calcula Def/RF y densidad por KLOC. | `datos/m22_defectos.json` |
| `m31_brechas.py` | M3.1: puntúa B1..B6 por versión, verificando los hechos en el código y en las mediciones. | `datos/m31_brechas.json` |
| `m32_indice_valor.py` | M3.2: índice de impacto en valor (V1..V3 con línea base AS-IS; V4..V6 como calidad de servicio). | `datos/m32_indice_valor.json` |
| `resumen_gqm.py` | Consolida las seis métricas con meta, cumplimiento y variación. | `datos/resumen_gqm.json` |
| `graficos_gqm.py` | Genera los seis gráficos (PNG 150 dpi y SVG). | `graficos/g1..g6_*.png/.svg` |
| `ejecutar_pruebas.sh` | ruff + pytest con cobertura + E2E Playwright de una versión; guarda las salidas crudas. | `salidas/v1.0/`, `salidas/v1.5/` |

## Cómo reproducir todo

Desde la raíz del repositorio, con `PY=python`, `GQM_RAIZ_V10=../inc1_v1.0_PMV` (ruta de v1.0, por defecto `../inc1_v1.0_PMV`) y, si se usan los E2E, `PLAYWRIGHT_BROWSERS_PATH` apuntando al directorio de navegadores de Playwright (bloques en bash; en Windows usar WSL o adaptar a PowerShell):

```bash
git worktree add ../inc1_v1.0_PMV v1.0-PMV      # copia de v1.0 (alternativa: git archive v1.0-PMV)
export PY=python GQM_RAIZ_V10=../inc1_v1.0_PMV
cd herramientas/gqm
bash ejecutar_pruebas.sh v1.0 && bash ejecutar_pruebas.sh v1.5     # ruff, pytest, cobertura, E2E
$PY m11_contaminacion.py; $PY m12_conformidad.py; $PY m13_acoplamiento.py; $PY m21_cobertura_rf.py
# dataset B150 ya generado: $PY generar_dataset.py --n 150 --semilla 20261016 --salida ../../entregables/semana-09/metricas/datos/dataset_B150.json
# V1..V3 (m32_valor.py): ver su cabecera; requiere un servidor de cada versión con el dataset cargado
$PY ejecutar_carga.py --repeticiones 2                # carga comparativa + sondas (≈ 8 min)
$PY ejecutar_carga.py --sesion-disponibilidad 10      # sesión de 10 min sin carga, ambas versiones en paralelo
# exploratorias: servidor v1.5 con dataset B150 cargado y su base SQLite
$PY exploratorias_inc2.py --base http://127.0.0.1:8321 --db <ruta.sqlite>
$PY m22_defectos.py; $PY m31_brechas.py; $PY m32_indice_valor.py; $PY resumen_gqm.py; $PY graficos_gqm.py
```

## Condiciones de la prueba de carga (Q3.2)

50 usuarios, subida de 10 usuarios/s, 60 s, Locust headless; uvicorn sin `--reload`, un proceso; SQLite nueva en cada corrida; el mismo dataset B150 cargado solo por la API (`cargar_dataset_api.py`) en ambas versiones; 2 repeticiones por escenario (`datos/m32_carga.json` guarda cada corrida y el promedio). Escenarios: `v10_comun` (v1.0, mix del Inc. 1), `v15_comun` (v1.5, el mismo mix y pesos) y `v15_agenda` (v1.5 con agenda y alertas). Las tareas y los pesos de `locust_comun.py` son los de `tests/rendimiento/locustfile.py` de v1.0; solo cambia la generación del DNI (contador determinista, para evitar 409 por colisión). La máquina tiene 2 CPU que comparten servidor, Locust y sonda: las cifras sirven para comparar versiones bajo las mismas condiciones, no como capacidad absoluta.

## Dónde está cada salida

- `datos/`: resultados calculados (JSON). `datos/resumen_gqm.json` es el consolidado.
- `salidas/v1.0/`, `salidas/v1.5/`: salidas crudas de ruff, pytest, cobertura y E2E.
- `salidas/carga/`: CSV de Locust (`<escenario>_r<k>_stats.csv`, `_stats_history.csv`, `_failures.csv`), consola, registro del servidor y sondas (`*_sonda.csv/.json`, `sesion_*`).
- `salidas/exploratorias_inc2_resultado.txt`: corrida final de las exploratorias; `_corrida1.txt` y `_corrida2.txt` conservan las anteriores.
- `graficos/`: g1 comparativa GQM, g2 conformidad hexagonal, g3 p95 por endpoint, g4 detección de vencidos, g5 brechas, g6 defectos.
- `instrumento_SUS.md`: instrumento del SUS real con usuarios (**pendiente de aplicar**; V6 es solo un proxy).
- Defectos: `pmv_fastapi/docs/evidencias/registro_defectos.md` (DEF-01, DEF-02) y `registro_defectos_inc2.md` (DEF-03 a DEF-08).
