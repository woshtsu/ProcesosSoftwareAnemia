# Herramientas

## Diagramas (`herramientas/diagramas/`)

Generador: `herramientas/diagramas/generar_diagramas.py` compila `diagramas/src/**/NN_*.puml`
(PlantUML local) y ejecuta `diagramas/src/**/NN_*.py` (matplotlib), y escribe
`diagramas/png/NN_*.png` (200 dpi por defecto) y `diagramas/svg/NN_*.svg`.

```bash
python herramientas/diagramas/generar_diagramas.py          # todos
python herramientas/diagramas/generar_diagramas.py 10 12    # solo los que empiezan por 10 o 12
python herramientas/diagramas/generar_diagramas.py --dpi 300
```

### Requisitos

1. **Java 17+** en el `PATH` (o variable `JAVA`).
2. **PlantUML** en `herramientas/plantuml/plantuml.jar` (no se versiona: está en `.gitignore`).
   Descárgalo solo de Maven Central (fuente oficial) y verifica el SHA-1:

   ```bash
   V=1.2026.8
   B=https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/$V
   mkdir -p herramientas/plantuml
   curl -fL -o herramientas/plantuml/plantuml.jar $B/plantuml-$V.jar
   curl -fs $B/plantuml-$V.jar.sha1      # debe coincidir con:
   sha1sum herramientas/plantuml/plantuml.jar
   ```

   Versión usada: `1.2026.8` (SHA-1 `7245f09f29981a673db313cca54f7838931f2887`).
   Alternativa oficial: https://github.com/plantuml/plantuml/releases
3. **Graphviz no es necesario**: el tema común (`diagramas/src/_tema.puml`) activa
   `!pragma layout smetana` (motor de disposición interno de PlantUML).
4. **Python 3** para el generador. Los diagramas generados con matplotlib usan el entorno
   `herramientas/.venv` (no versionado):

   ```bash
   python -m venv herramientas/.venv
   herramientas/.venv/Scripts/python -m pip install matplotlib    # Windows
   ```

No se usan servidores PlantUML en línea: todo el contenido se procesa localmente.
