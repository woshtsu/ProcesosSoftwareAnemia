# Métricas GQM de la semana 9 (Procesos de Software)

Evaluación GQM del Proyecto «Anemia Junín». Compara tres versiones: el **Incremento 1** (v1.0-PMV, copia de trabajo creada con `git worktree add ../inc1_v1.0_PMV v1.0-PMV`), el **avance del Incremento 2** (v1.5.0-inc2-avance, hito intermedio al 50 %, exportado con `git archive HEAD pmv_fastapi` a `../v15_export/`) y el **cierre del Incremento 2** (v2.0.0-inc2, `pmv_fastapi/`). Las métricas de arquitectura, calidad y carga usan datos 100 % sintéticos (dataset B150); la línea base real y la verificación sobre datos reales usan el dataset anonimizado de la DIRESA Junín (ver más abajo). Fechas de las mediciones: 16/10/2026 (v1.0, v1.5) y 17/10/2026 (v2.0 y repetición de v1.0 en la misma sesión), hora de Perú. Cada número del informe sale de una ejecución real guardada en `datos/` o `salidas/`.

## Resultado en una tabla (de `datos/resumen_gqm.json`)

| Métrica | Inc. 1 (v1.0) | Avance v1.5 | Inc. 2 (v2.0, cierre) | Meta Inc. 1 / Inc. 2 | ¿Cumple? (Inc. 1 / avance / Inc. 2) | Variación Inc. 1 → Inc. 2 |
|---|---|---|---|---|---|---|
| M1.1 Contaminación del dominio | 0,0 % | 0,0 % | 0,0 % | 0 % / 0 % | Sí / Sí / Sí | n/a (base 0) |
| M1.2 Conformidad hexagonal (estricta) | 40,0 % (laxa 60,0 %) | 100,0 % | 100,0 % | 100 % / 100 % | No / Sí / Sí | +150,0 % |
| M2.1 RF con captura aprobada | 100,0 % (5/5) | 100,0 % (2/2 entregados; 50,0 % sobre las 4 RF del Inc. 2) | 100,0 % (4/4: RF-06 a RF-09) | 100 % / 100 % | Sí / Sí / Sí | 0,0 % |
| M2.2 Defectos funcionales por RF | 1,40 Def/RF (7/5) | 0,00 (0/2) | 0,25 Def/RF (1/4: DEF-09, RF-08, hallado por E2E antes de liberar) | ≤ 1,0 / ≤ 0,2 | No / Sí / **No** | −82,1 % |
| M3.1 Brechas resueltas (de 6) | 25,0 % | 33,3 % | 33,3 % | ≥ 60 % / ≥ 90 % | No / No / No | +33,3 % |
| M3.2 Índice de impacto en valor | 57,6 % | 100,0 % | 100,0 % | ≥ 50 % / ≥ 80 % | Sí / Sí / Sí | +73,5 % |

Lecturas que conviene no omitir:

- **M2.2 no cumple la meta ≤ 0,2** con la lectura principal (1/4 = 0,25, porque DEF-09 se cuenta aunque se detectó antes de liberar). La variante «solo escapados a producción» da 0/4 = 0,0 (la v2.0 aún no se libera); ambas están en `datos/m22_defectos.json` y en `datos/resumen_gqm.json`.
- **M3.1 no cumple (33,3 % frente a ≥ 90 %)**: B2 sigue en 0,5 (faltan los recordatorios a la familia, INC-4) y B3 en 0 (el motivo de inasistencia no es un registro de barreras). Sobre las brechas que el plan compromete hasta cada incremento (B1; B1 + B2) la cobertura es 100,0 % (Inc. 1) y 75,0 % (Inc. 2). Sensibilidad de B2/B3 en `datos/m31_brechas.json`.
- **M3.2**: el 100 % de V2 y V3 es sobre el dataset sintético B150 (mismo dataset y misma fecha de referencia en las tres versiones); no es una medición clínica. V4 a V6 (calidad de servicio) quedan fuera del índice.
- **Rendimiento (V4, fuera del índice)**: con el mismo mix de carga (50 usuarios, 60 s, B150) el p95 agregado de la v2.0 es 815 ms frente a 155 ms de la v1.0 medida en la misma sesión (610 ms en la v1.5, otra sesión); todos los endpoints quedan por debajo del umbral de 2 s, sin fallos y con disponibilidad de 856/856 sondas (100,0 %). Es un costo medible de calcular la agenda normativa en cada consulta (ver `datos/m32_carga.json`).
- La variación porcentual y las variantes (laxa, solo detectados antes de liberar, brechas comprometidas en el plan, etc.) están en `datos/resumen_gqm.json`.

### Pruebas de la v2.0 (de `salidas/v2.0/`)

ruff `check` sin observaciones y `format --check` sobre 95 archivos; pytest 328 en verde con cobertura de líneas y ramas del 100 % (1 700 líneas, 264 ramas); E2E Playwright 15 en verde; 48/48 criterios Dado-Cuando-Entonces verificados por prueba automatizada (`datos/m21_cobertura_rf.json`). Referencia: v1.0 con 73 pruebas, 99 % de cobertura y 4 E2E; v1.5 con 228 pruebas, 100 % de cobertura y 8 E2E.

### Línea base real de la DIRESA Junín (no entra en el índice)

`datos/m32_indice_valor.json`, sección `linea_base_real_DIRESA`, pone lado a lado (sin promediar) el **proceso actual**, calculado sobre el dataset completo (12 486 diagnósticos, corte 30/06/2024; `datos/asis_dataset_diresa.json`), y la **capacidad de la v2.0** sobre la muestra estratificada de 500 niños importada con `FECHA_REFERENCIA=2024-06-30` (`datos/m32_dataset_real.json`). Control de hemoglobina registrado: al mes 67,1 % bruto / 70,2 % con seguimiento posible; a los 3 meses 54,7 % / 63,8 %; a los 6 meses 46,3 % / 66,1 %; pérdida de seguimiento a 6 meses 53,7 % bruta / 33,9 % con seguimiento posible. Indicador «controles vencidos visibles para el personal»: 0 % en el proceso actual (no existe agenda ni lista de vencidos) frente a 100 % en la v2.0 (1 638 de 1 638 controles vencidos, 419 niños, concordancia 100 % con el oráculo independiente). Advertencias: el 0 % es estructural, no una medición sobre el dataset; el 100 % es capacidad de visualizar, no mejora clínica ni de asistencia; el oráculo recalcula la agenda desde los datos que guardó el sistema, no verifica la importación del CSV. Gráfico `graficos/g10_linea_base_vs_inc2.png`.

## Scripts (`.claude/herramientas/gqm/`)

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
| `m32_valor.py` | Indicadores V1, V2, V3 por HTTP contra servidores reales (v1.0, v1.5 y v2.0; la v2.0 con `FECHA_REFERENCIA` = fecha del dataset B150). | `datos/m32_v1.0_B150.json`, `m32_v1.5_B150.json`, `m32_v2.0_B150.json` |
| `m32_dataset_real.py` | M3.2 sobre la muestra de 500 niños del dataset real de la DIRESA Junín en la v2.0 (agenda por niño, vencidos detectados, concordancia con el oráculo, visibilidad en la agenda del personal, tiempos). | `datos/m32_dataset_real.json` |
| `locust_comun.py`, `locust_v15_agenda.py` | Perfiles de carga: mix común del Inc. 1 y mix ampliado con agenda y alertas (el de la v2.0 es `pmv_fastapi/tests/rendimiento/locustfile.py`). | — |
| `sonda_salud.py` | Sonda `GET /api/salud` cada 1 s; disponibilidad = respuestas 200 en < 2 s / sondas. | CSV/JSON en `salidas/carga/` |
| `ejecutar_carga.py` | Orquesta la carga comparativa (base nueva, mismo dataset, sonda en paralelo, 2 repeticiones; `--corridas escenario:n ...` para corridas puntuales) y la sesión de disponibilidad de 10 min (`--versiones-sesion`); resume. | `datos/m32_carga.json`, `datos/m32_disponibilidad.json`, `salidas/carga/*` |
| `exploratorias_inc2.py` | 45 pruebas exploratorias de caja negra sobre agenda y alertas (y entradas límite heredadas). | `datos/exploratorias_inc2.json`, `exploratorias_inc2.md`, `salidas/exploratorias_inc2_resultado*.txt` |
| `exploratorias_inc2_final.py` | 27 pruebas exploratorias de RF-08 (agenda del personal) y RF-09 (asistencia): 27 OK en la corrida final; la corrida 1 (25 OK, 2 errores de diseño de los casos) se conserva. | `datos/exploratorias_inc2_final.json`, `exploratorias_inc2_final.md`, `salidas/exploratorias_inc2_final_resultado*.txt` |
| `m22_defectos.py` | M2.2: clasifica DEF-01..09 (funcional / no funcional, RF afectado), calcula Def/RF y densidad por KLOC; Inc. 1, avance v1.5 y cierre. | `datos/m22_defectos.json` |
| `m31_brechas.py` | M3.1: puntúa B1..B6 por versión (v1.0, v1.5, v2.0), verificando los hechos en el código y en las mediciones; sensibilidad de B2 y B3. | `datos/m31_brechas.json` |
| `m32_indice_valor.py` | M3.2: índice de impacto en valor (V1..V3 con línea base AS-IS; V4..V6 como calidad de servicio) y sección `linea_base_real_DIRESA` (fuera del índice). | `datos/m32_indice_valor.json` |
| `resumen_gqm.py` | Consolida las seis métricas con meta, cumplimiento y variación en tres columnas: Inc. 1, avance v1.5 e Inc. 2 (v2.0, cierre); lee `evidencias_capturas/resultados_inc*.json`. | `datos/resumen_gqm.json` |
| `graficos_gqm.py` | Genera los gráficos g1 a g6 (Inc. 1 frente a Inc. 2, v1.5 como rombo gris) y g10 (línea base real frente a la v2.0) en PNG 150 dpi y SVG. | `graficos/g1..g6_*`, `g10_*` |
| `ejecutar_pruebas.sh` | ruff + pytest con cobertura + E2E Playwright de una versión (`v1.0`, `v1.5` o `v2.0`); guarda las salidas crudas. | `salidas/v1.0/`, `salidas/v1.5/`, `salidas/v2.0/` |

## Cómo reproducir todo

Desde la raíz del repositorio, con `PY=python`, `GQM_RAIZ_V10=../inc1_v1.0_PMV` (ruta de v1.0, por defecto `../inc1_v1.0_PMV`) y, si se usan los E2E, `PLAYWRIGHT_BROWSERS_PATH` apuntando al directorio de navegadores de Playwright (bloques en bash; en Windows usar WSL o adaptar a PowerShell):

```bash
git worktree add ../inc1_v1.0_PMV v1.0-PMV      # copia de v1.0 (alternativa: git archive v1.0-PMV)
export PY=python GQM_RAIZ_V10=../inc1_v1.0_PMV
cd .claude/herramientas/gqm
git -C . archive HEAD pmv_fastapi | tar -x -C ../v15_export      # copia de v1.5 (estado confirmado antes del cierre); GQM_RAIZ_V15 la cambia
export GQM_RAIZ_V15=../v15_export/pmv_fastapi
cd .claude/herramientas/gqm
for v in v1.0 v1.5 v2.0; do bash ejecutar_pruebas.sh $v; done      # ruff, pytest, cobertura, E2E (salidas/<v>/)
$PY m11_contaminacion.py; $PY m12_conformidad.py; $PY m13_acoplamiento.py; $PY m21_cobertura_rf.py
# dataset B150 ya generado: $PY generar_dataset.py --n 150 --semilla 20261016 --salida ../../entregables/semana-09/metricas/datos/dataset_B150.json
# V1..V3 (m32_valor.py): ver su cabecera; requiere un servidor de cada versión con el dataset cargado (v2.0 con FECHA_REFERENCIA=2026-10-16)
$PY ejecutar_carga.py --repeticiones 2                # carga comparativa + sondas (≈ 15 min con las tres versiones)
$PY ejecutar_carga.py --corridas v10_comun:3 v20_comun:1 v20_ampliado:1 v10_comun:4 v20_comun:2 v20_ampliado:2   # lo que se usó el 17/10/2026
$PY ejecutar_carga.py --sesion-disponibilidad 10 --versiones-sesion v2.0   # sesión de 10 min sin carga
# exploratorias: servidor con dataset B150 cargado y su base SQLite
$PY exploratorias_inc2.py --base http://127.0.0.1:8321 --db <ruta.sqlite>
$PY exploratorias_inc2_final.py --base http://127.0.0.1:8322 --db <ruta.sqlite>
# muestra real: desde pmv_fastapi, DATABASE_URL=sqlite:///<ruta.db> python -m scripts.importar_dataset_diresa --muestra 500 --semilla 2026 --reiniciar --con-registros-sistema 3 --reporte <ruta.json>
#               y servidor con FECHA_REFERENCIA=2024-06-30:  $PY m32_dataset_real.py --base http://127.0.0.1:8404 --reporte-importacion <ruta.json>
# capturas del cierre (RF-08, RF-09 y datos_reales/), desde entregables/semana-09/evidencias_capturas:  $PY capturar_evidencias.py --modo inc2final ; --modo indice
$PY m22_defectos.py; $PY m31_brechas.py; $PY m32_indice_valor.py; $PY resumen_gqm.py; $PY graficos_gqm.py
```

Para ejecutar `servidor.sh` y `ejecutar_carga.py` hace falta `PY` apuntando al intérprete con las dependencias (sin él `servidor.sh` usa `python` y el servidor puede no arrancar).

## Condiciones de la prueba de carga (Q3.2)

50 usuarios, subida de 10 usuarios/s, 60 s, Locust headless; uvicorn sin `--reload`, un proceso; SQLite nueva en cada corrida; el mismo dataset B150 cargado solo por la API (`cargar_dataset_api.py`) en ambas versiones; 2 repeticiones por escenario (`datos/m32_carga.json` guarda cada corrida y el promedio). Escenarios: `v10_comun` (v1.0, mix del Inc. 1), `v15_comun` (v1.5, el mismo mix y pesos), `v15_agenda` (v1.5 con agenda y alertas), `v20_comun` (v2.0, el mismo mix común) y `v20_ampliado` (v2.0 con su propio locustfile: agenda del niño, alertas, agenda del personal y asistencias). La v1.0 se repitió (corridas r3 y r4) en la misma sesión que la v2.0 (17/10/2026) para controlar el ruido de la máquina; v1.0 y v2.0 se comparan con esas corridas y la v1.5 (sesión del 16/10/2026) se muestra aparte. En la v2.0 el servidor corre con `FECHA_REFERENCIA=2026-10-16` (fecha para la que se generó B150) para que la agenda tenga la misma carga de trabajo que en las mediciones anteriores. La sonda `GET /api/salud` (cada 1 s) corre en todas las corridas y, además, hay una sesión de 10 min sin carga por versión. Las tareas y los pesos de `locust_comun.py` son los de `tests/rendimiento/locustfile.py` de v1.0; solo cambia la generación del DNI (contador determinista, para evitar 409 por colisión). La máquina tiene 2 CPU que comparten servidor, Locust y sonda: las cifras sirven para comparar versiones bajo las mismas condiciones, no como capacidad absoluta.

## Dónde está cada salida

- `datos/`: resultados calculados (JSON). `datos/resumen_gqm.json` es el consolidado.
- `salidas/v1.0/`, `salidas/v1.5/`, `salidas/v2.0/`: salidas crudas de ruff, pytest, cobertura y E2E.
- `salidas/carga/`: CSV de Locust (`<escenario>_r<k>_stats.csv`, `_stats_history.csv`, `_failures.csv`), consola, registro del servidor y sondas (`*_sonda.csv/.json`, `sesion_*`).
- `salidas/exploratorias_inc2_resultado.txt`: corrida final de las exploratorias; `_corrida1.txt` y `_corrida2.txt` conservan las anteriores.
- `salidas/exploratorias_inc2_final_resultado.txt`: corrida final de las 27 exploratorias de RF-08/RF-09; `_corrida1.txt` conserva la anterior.
- `graficos/`: g1 comparativa GQM, g2 conformidad hexagonal, g3 p95 por endpoint, g4 detección de vencidos, g5 brechas, g6 defectos (RF-01 a RF-09), g10 línea base real de la DIRESA Junín frente a la capacidad de la v2.0; g7 a g9 son del análisis AS-IS del dataset. Inc. 1 = v1.0, Inc. 2 = v2.0, con la v1.5 como rombo gris.
- `../evidencias_capturas/`: capturas reales por RF (`RF-01/` a `RF-09/`, `datos_reales/`) e `INDICE.md`; las del cierre se generan con `capturar_evidencias.py --modo inc2final` y `resultados_inc2final.json`.
- `instrumento_SUS.md`: instrumento del SUS real con usuarios (**pendiente de aplicar**; V6 es solo un proxy).
- Defectos: `pmv_fastapi/docs/evidencias/registro_defectos.md` (DEF-01, DEF-02) y `registro_defectos_inc2.md` (DEF-03 a DEF-09; DEF-09 es el único defecto funcional del código nuevo de RF-06 a RF-09, detectado por las pruebas E2E antes de liberar la v2.0).
