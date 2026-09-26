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
