@echo off
setlocal enabledelayedexpansion
cd /d "D:\Workspace\IngenieriaWeb\Grupal\semana6\ProcesosSoftwareAnemia"

set PLANTUML="herramientas\plantuml\plantuml.jar"
set SRCDIR=diagramas\src
set PNGDIR=diagramas\png
set SVGDIR=diagramas\svg

echo Generando diagramas PlantUML...

REM Fuentes PlantUML (50-57, 64 y 68 de matplotlib: ver README; 58, 64 y variantes _16x9 son .py)
for %%F in (
  50_s6_as_is_vs_to_be.puml
  51_s6_ciclo_vida_tailoring.puml
  52_s6_c4_contexto_fastapi.puml
  53_s6_c4_contenedores_fastapi.puml
  54_s6_c4_componentes_fastapi.puml
  55_s6_modelo_datos_postgresql.puml
  56_s6_paquetes_hexagonal_fastapi.puml
  57_s6_secuencia_registro_hu01.puml
  68_s6_roadmap_incrementos.puml
) do (
  echo Procesando %%F...
  java -jar !PLANTUML! -o ..\png !SRCDIR!\%%F
  java -jar !PLANTUML! -svg -o ..\svg !SRCDIR!\%%F
)

echo.
echo Generacion completada.
echo Archivos PNG en: !PNGDIR!
echo Archivos SVG en: !SVGDIR!

pause
