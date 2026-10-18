# Diagramas

Responsable: agente `diagramador`. Solicitudes: `coordinacion/solicitudes/DIAG-###.md`.

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
| 01 | Procesos AS-IS / TO-BE (síntesis) | `src/integrador/diagramas.py` | sí | sí | S6 |
| 02 | Modelo de proceso (10 elementos) | `src/integrador/diagramas.py` | sí | sí | S6 |
| 03 | C4 contexto | `src/integrador/diagramas.py` | sí | sí | S6 |
| 04 | C4 contenedores | `src/integrador/diagramas.py` | sí | sí | S6 |
| 05 | C4 componentes | `src/integrador/diagramas.py` | sí | sí | S6 |
| 06 | Casos de uso PMV | `src/integrador/diagramas.py` (alternativa PlantUML: `src/Casos_de_uso_PMV.puml`) | sí | sí | S6 |
| 07 | Despliegue | `src/integrador/diagramas.py` | sí | sí | S6 |
| 08 | Modelo de datos | `src/integrador/diagramas.py` | sí | sí | S6 |
| 09 | Secuencia de registro | `src/integrador/diagramas.py` | sí | sí | S6 |
| 70 | S9 Cadena de trazabilidad integrada (problema → valor, por pilar) | `src/70_s9_cadena_trazabilidad.dot` (Graphviz) | sí | sí | S9 |
| 71 | S9 Árbol GQM (G-01..G-03, Q1.1..Q3.2, M1.1..M3.2 y M1.3) | `src/71_s9_arbol_gqm.dot` (Graphviz) | sí | sí | S9 |
| 72 | S9 Vista hexagonal de v2.0.0-inc2 (puertos y adaptadores reales) | `src/72_s9_hexagonal_v20.dot` (Graphviz) | sí | sí | S9 |

Las figuras de S1 (`entregables/semana-01/img/image1..11.png`) y S2 (`entregables/semana-02/img/image1.png`) son imágenes raster sin fuente editable; si se rehacen, pasarán a este catálogo.

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

Graphviz (diagramas 70 a 72, Semana 9; requiere `dot`):

```bash
cd diagramas/src
for n in 70_s9_cadena_trazabilidad 71_s9_arbol_gqm 72_s9_hexagonal_v20; do
  dot -Tpng -Gdpi=150 $n.dot -o ../png/$n.png && dot -Tsvg $n.dot -o ../svg/$n.svg
done
```
