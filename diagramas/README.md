# Diagramas

Responsable: agente `recursos-visuales` (antes `diagramador`). Solicitudes: `coordinacion/solicitudes/DIAG-###.md` (S1–S5) y `coordinacion/s6/solicitudes/VIS-###.md` (S6).

## Estructura

```
diagramas/
├── src/                 fuentes versionadas (.puml, .py)
│   └── integrador/      generador ReportLab del informe integrador (diagramas.py, contenido.py, generar.py)
├── png/                 exportación raster (vista previa, DOCX)
├── svg/                 exportación vectorial (se incrusta en los .md)
└── _build/              intermedios regenerables (ignorado por git)
```

Convención: `NN_nombre_descriptivo.{puml|py,png,svg}` — el mismo nombre base en las tres carpetas.
Desde un entregable en `entregables/semana-XX/` se enlaza así: `![Figura N. Leyenda](../../diagramas/svg/NN_nombre.svg)`.

## Catálogo

| NN | Nombre | Fuente | PNG | SVG | Usado en |
| --- | --- | --- | --- | --- | --- |
| 01 | Procesos AS-IS / TO-BE (síntesis) | `src/integrador/diagramas.py` | sí | sí | Antecedente Flask; no se usa en S6 (C-05) |
| 02 | Modelo de proceso (10 elementos) | `src/integrador/diagramas.py` | sí | sí | Antecedente Flask; no se usa en S6 (C-05) |
| 03 | C4 contexto | `src/integrador/diagramas.py` | sí | sí | Antecedente Flask; no se usa en S6 (C-05) |
| 04 | C4 contenedores | `src/integrador/diagramas.py` | sí | sí | Antecedente Flask; no se usa en S6 (C-05) |
| 05 | C4 componentes | `src/integrador/diagramas.py` | sí | sí | Antecedente Flask; no se usa en S6 (C-05) |
| 06 | Casos de uso PMV | `src/integrador/diagramas.py` (alternativa PlantUML: `src/Casos_de_uso_PMV.puml`) | sí | sí | Antecedente Flask; no se usa en S6 (C-05) |
| 07 | Despliegue | `src/integrador/diagramas.py` | sí | sí | Antecedente Flask; no se usa en S6 (C-05) |
| 08 | Modelo de datos | `src/integrador/diagramas.py` | sí | sí | Antecedente Flask; no se usa en S6 (C-05) |
| 09 | Secuencia de registro | `src/integrador/diagramas.py` | sí | sí | Antecedente Flask; no se usa en S6 (C-05) |

Las figuras de S1 (`entregables/semana-01/img/image1..11.png`) y S2 (`entregables/semana-02/img/image1.png`) son imágenes raster sin fuente editable; si se rehacen, pasarán a este catálogo.

## Catálogo S6 (figuras 50–68_s6, PMV FastAPI)

Generadas por `recursos-visuales` (S6-09, corregidas en S6-13 a S6-17; la 60 ajustada por el sincronizador en S6-20). Informe: `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` (enlaza el SVG). Diapositivas: `entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md` y el PPTX `exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pptx` (usan el PNG).

| NN | Nombre | Tipo | Fuente | PNG | SVG | VIS | Usado en |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 50 | AS-IS reactivo vs. TO-BE preventivo (brechas B1–B6, mejoras M1–M6) | PlantUML | `src/50_s6_as_is_vs_to_be.puml` | `png/50_s6_as_is_vs_to_be.png` | `svg/50_s6_as_is_vs_to_be.svg` | VIS-001 | Informe Integrador Fig. 1; Diap. 1 |
| 51 | Ciclo de vida adaptado (tailoring) y alternativas (4,75 / 3,85 / 2,95) | PlantUML | `src/51_s6_ciclo_vida_tailoring.puml` | `png/51_s6_ciclo_vida_tailoring.png` | `svg/51_s6_ciclo_vida_tailoring.svg` | VIS-002 | Informe Integrador Fig. 6; Diap. 2 |
| 52 | C4 nivel 1: contexto del PMV FastAPI | PlantUML | `src/52_s6_c4_contexto_fastapi.puml` | `png/52_s6_c4_contexto_fastapi.png` | `svg/52_s6_c4_contexto_fastapi.svg` | VIS-003 | Informe Integrador Fig. 16 |
| 53 | C4 nivel 2: contenedores del PMV FastAPI | PlantUML | `src/53_s6_c4_contenedores_fastapi.puml` | `png/53_s6_c4_contenedores_fastapi.png` | `svg/53_s6_c4_contenedores_fastapi.svg` | VIS-003 | Informe Integrador Fig. 17; Diap. 3 |
| 54 | C4 nivel 3: componentes de la aplicación FastAPI | PlantUML | `src/54_s6_c4_componentes_fastapi.puml` | `png/54_s6_c4_componentes_fastapi.png` | `svg/54_s6_c4_componentes_fastapi.svg` | VIS-003 | Informe Integrador Fig. 18 |
| 55 | Modelo de datos PostgreSQL (`v_ultimo_control` como vista) | PlantUML | `src/55_s6_modelo_datos_postgresql.puml` | `png/55_s6_modelo_datos_postgresql.png` | `svg/55_s6_modelo_datos_postgresql.svg` | VIS-004 | Informe Integrador Fig. 21 |
| 56 | Paquetes y dependencias hexagonales | PlantUML | `src/56_s6_paquetes_hexagonal_fastapi.puml` | `png/56_s6_paquetes_hexagonal_fastapi.png` | `svg/56_s6_paquetes_hexagonal_fastapi.svg` | VIS-005 | Informe Integrador Fig. 19 |
| 57 | Secuencia de registro con vista previa (HU-01 y HU-03) | PlantUML | `src/57_s6_secuencia_registro_hu01.puml` | `png/57_s6_secuencia_registro_hu01.png` | `svg/57_s6_secuencia_registro_hu01.svg` | VIS-005 | Informe Integrador Fig. 20 |
| 58 | Despliegue Docker Compose (staging) y pipeline CI | matplotlib (dos filas, A4 y 16:9; sustituye al .puml) | `src/58_s6_despliegue_docker_ci.py` | `png/58_s6_despliegue_docker_ci.png` | `svg/58_s6_despliegue_docker_ci.svg` | VIS-006 | Informe Integrador Fig. 25; Diap. 5 |
| 59 | Pirámide de pruebas: 77 declaradas (62 + 11 + 4), 73 reproducidas; carga aparte | matplotlib | `src/59_s6_piramide_pruebas.py` | `png/59_s6_piramide_pruebas.png` | `svg/59_s6_piramide_pruebas.svg` | VIS-007 | Informe Integrador Fig. 22; Diap. 4 |
| 60 | Cobertura por módulo frente al umbral del 80 % (todo reproducido el 01/10/2026: 548 sentencias, 99,07 %) | matplotlib | `src/60_s6_cobertura.py` | `png/60_s6_cobertura.png` | `svg/60_s6_cobertura.svg` | VIS-008 | Informe Integrador Fig. 23; Diap. 4 |
| 61 | Carga: p95 y req/s antes y después de DEF-01 | matplotlib | `src/61_s6_carga_p95.py` | `png/61_s6_carga_p95.png` | `svg/61_s6_carga_p95.svg` | VIS-009 | Informe Integrador Fig. 24; Diap. 4 |
| 62 | Tablero integrado de métricas (21/21 SP, 77/73 pruebas) | matplotlib | `src/62_s6_tablero_metricas.py` | `png/62_s6_tablero_metricas.png` | `svg/62_s6_tablero_metricas.svg` | VIS-010 | Informe Integrador Fig. 14; Diap. 6 |
| 63 | Incremento 1: planificado vs. completado por HU/tarea (no es burnup temporal) | matplotlib | `src/63_s6_burnup_inc1.py` | `png/63_s6_burnup_inc1.png` | `svg/63_s6_burnup_inc1.svg` | VIS-011 | Informe Integrador Fig. 13; Diap. 6 |
| 64 | Matriz de trazabilidad (8 columnas de la consigna; filas 1 y 5 de la Tabla 30) | matplotlib (matriz de 8 columnas con 2 filas de ejemplo; sustituye al .puml) | `src/64_s6_flujo_trazabilidad.py` | `png/64_s6_flujo_trazabilidad.png` | `svg/64_s6_flujo_trazabilidad.svg` | VIS-012 | Informe Integrador Fig. 34; Diap. 7 |
| 65 | Collage de capturas de la demo (incluye HU-04) | matplotlib + Pillow | `src/65_s6_collage_demo.py` | `png/65_s6_collage_demo.png` | `svg/65_s6_collage_demo.svg` | VIS-013 | Diap. 5 (el informe incrusta las capturas 01–08 por separado) |
| 66 | ADR → atributos de calidad (NFR) | matplotlib | `src/66_s6_adr_nfr.py` | `png/66_s6_adr_nfr.png` | `svg/66_s6_adr_nfr.svg` | VIS-014 | Informe Integrador Fig. 15; Diap. 3 |
| 67 | Matriz de factores del proyecto (cinco en nivel Alto) | matplotlib | `src/67_s6_matriz_factores.py` | `png/67_s6_matriz_factores.png` | `svg/67_s6_matriz_factores.svg` | VIS-015 | Informe Integrador Fig. 5; Diap. 2 |
| 68 | Hoja de ruta de incrementos (INC-1 entregado; INC-2 siguiente) | PlantUML | `src/68_s6_roadmap_incrementos.puml` | `png/68_s6_roadmap_incrementos.png` | `svg/68_s6_roadmap_incrementos.svg` | VIS-016 | Informe Integrador Fig. 35; Diap. 7 |

Las figuras reutilizadas de S1–S3-4 (`10`–`15`, `30`–`35`) se listan en `coordinacion/s6/TABLERO_S6.md`.

### Versiones horizontales 16:9 para diapositivas (sufijo `_16x9`, PNG a 200 dpi + SVG)

Lienzo de 11 x 6,19 pulgadas (relación 16:9), texto de 16 a 19 pt: a >= 80 % del ancho de la diapositiva equivale a >= 14 pt. Los originales se conservan para el informe.

| N.º | Figura | Tipo | Fuente | PNG | SVG | Solicitud | Uso |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 50 | AS-IS vs. TO-BE (B1-B6 → M1-M6), 6 pares + indicador | matplotlib | `src/50_s6_as_is_vs_to_be_16x9.py` | `png/50_s6_as_is_vs_to_be_16x9.png` | `svg/50_s6_as_is_vs_to_be_16x9.svg` | S6-22 / N-01 | Diap. 1 |
| 58 | Despliegue Docker Compose + CI en dos filas | matplotlib | `src/58_s6_despliegue_docker_ci_16x9.py` | `png/58_s6_despliegue_docker_ci_16x9.png` | `svg/58_s6_despliegue_docker_ci_16x9.svg` | S6-22 / N-01 | Diap. 5 (opcional) |
| 64 | Trazabilidad: 8 tarjetas con la fila HU-01 | matplotlib | `src/64_s6_flujo_trazabilidad_16x9.py` | `png/64_s6_flujo_trazabilidad_16x9.png` | `svg/64_s6_flujo_trazabilidad_16x9.svg` | S6-22 / N-01 | Diap. 7 |
| 68 | Hoja de ruta de 8 sprints (INC-1 entregado, INC-2 siguiente) | matplotlib | `src/68_s6_roadmap_incrementos_16x9.py` | `png/68_s6_roadmap_incrementos_16x9.png` | `svg/68_s6_roadmap_incrementos_16x9.svg` | S6-22 / N-01 | Diap. 7 |
| 53 | C4 nivel 2 panorámico de 11 x 4,3 in (6 contenedores, relaciones sin etiquetas) | matplotlib | `src/53_s6_c4_contenedores_fastapi_16x9.py` | `png/53_s6_c4_contenedores_fastapi_16x9.png` | `svg/53_s6_c4_contenedores_fastapi_16x9.svg` | S6-22 | Diap. 3 |
| 59 | Pirámide `_media` (5,4 x 4 in): 62/11/4 = 77, 73 reproducidas, carga aparte | matplotlib | `src/59_s6_piramide_pruebas_media.py` | `png/59_s6_piramide_pruebas_media.png` | `svg/59_s6_piramide_pruebas_media.svg` | S6-22 | Diap. 4 (mitad izquierda) |
| 61 | Carga `_media` (5,9 x 4 in): p95 310 → 58 ms, 39,56 req/s, 0 % de errores | matplotlib | `src/61_s6_carga_p95_media.py` | `png/61_s6_carga_p95_media.png` | `svg/61_s6_carga_p95_media.svg` | S6-22 | Diap. 4 (mitad derecha) |

Pies de figura: las figuras 59, 61, 62, 63, 65, 66 y 67 (y sus variantes) citan «Fuente: elaboración propia (Tabla n / §n)» del informe, sin rutas internas.

Utilidades compartidas: `src/_fig.py` y `src/_fig58.py` (se excluyen del generador por el prefijo `_`). Regenerar: `herramientas/.venv/Scripts/python diagramas/src/<nombre>.py`.

## Regenerar

Generador del integrador (requiere `pip install reportlab pypdfium2` y fuentes Arial de Windows):

```bash
python diagramas/src/integrador/generar.py
```

Escribe SVG en `diagramas/svg/`, PNG en `diagramas/png/` y un borrador del informe en `diagramas/_build/integrador/` (no sobrescribe el entregable vigente).

PlantUML (requiere Java 17 + `plantuml.jar`; Graphviz opcional para algunos tipos):

```bash
java -jar plantuml.jar -tsvg -o ../svg diagramas/src/*.puml
java -jar plantuml.jar -tpng -o ../png diagramas/src/*.puml
```

Figuras S6 (desde la raíz del repositorio; `plantuml.jar` y `herramientas/.venv` son locales y no se versionan):

```bash
diagramas/generar_s6.bat                                        # PlantUML: 50-57 y 68 (layout smetana); 58 y 64 son matplotlib
herramientas/.venv/Scripts/python diagramas/src/60_s6_cobertura.py   # un gráfico matplotlib (59-63, 65-67)
```
