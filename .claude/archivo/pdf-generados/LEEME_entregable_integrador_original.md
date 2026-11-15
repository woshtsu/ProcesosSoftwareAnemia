# Material de revisión e integración

Empieza por `Revision_Cumplimiento_y_Trazabilidad.pdf`, especialmente las páginas 3 a 6. Detalla errores, ubicaciones y correcciones. Luego revisa `Informe_Integrador_Anemia_Junin_revision.pdf`, de 25 páginas, que organiza el contenido con la estructura de S6.

Los dos archivos `.md` del mismo nombre conservan el texto editable. La carpeta `diagramas` incluye nueve SVG vectoriales y nueve PNG, además del código PlantUML del caso de uso. Los SVG se pueden abrir en un navegador o importar en un editor vectorial. El PlantUML es una fuente alternativa, no requiere reemplazar el SVG ya renderizado.

`Prompts_y_guion_de_defensa.md` incluye prompts para contrastar los diagramas con el código y preparar la arquitectura futura, un guion de siete diapositivas y preguntas para ensayar la defensa. No se ha generado una presentación final ni un repositorio ficticio.

## Estado de entrega

La revisión documental está realizada. El informe integrado es una propuesta revisable, no una certificación de implementación ni una entrega académica cerrada. Las nuevas decisiones RAE, ADR, cambios de alcance y pruebas propuestas deben ser adoptadas por el equipo. Faltan datos de portada, repositorio, tag, contrato, scripts, reportes reproducibles, E2E, carga, aceptación del usuario y presentación.

Las cifras de pruebas y cobertura se atribuyen al avance del equipo. No se ejecutó el PMV porque sus archivos no estaban disponibles. No se fabricaron resultados, actas, fechas de aprobación ni evidencia clínica.

## Diagramas

1. Síntesis comparativa AS-IS y TO-BE.
2. Modelo de proceso con diez elementos y repetición.
3. C4 de contexto del PMV.
4. C4 de contenedores del PMV.
5. C4 de componentes de la aplicación.
6. Casos de uso UML del PMV.
7. Despliegue local de demostración.
8. Modelo conceptual de datos.
9. Secuencia conceptual de registro.

Los diagramas de arquitectura se basan en el sistema descrito en Actividad 5. Las vistas futuras de S1-S4 no se atribuyen a la implementación actual. Los originales de todas las semanas se conservan intactos.

## Fuentes editables de generación

La carpeta `fuentes` contiene `contenido.py`, `diagramas.py` y `generar.py`. Fueron generados con Python, ReportLab y pypdfium2 del runtime de documentos. El constructor usa fuentes Arial de Windows y rutas relativas a la carpeta original de trabajo. Para regenerar allí, ejecutar el Python del runtime con `output/entregable_integrador/fuentes/generar.py`. No son archivos del PMV: únicamente construyen estos documentos y figuras.
