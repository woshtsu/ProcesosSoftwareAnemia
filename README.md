# Sistema de detección temprana y seguimiento de anemia infantil — Junín, Perú

Proyecto de la asignatura **Procesos de Software** (ASUC01702, Universidad Continental, ciclo 2026-20).

El problema organizacional: en las zonas rurales de Junín el tamizaje de hemoglobina, el tratamiento con hierro y el seguimiento de niños con anemia se pierden por falta de trazabilidad, baja adherencia, poca proactividad y conectividad limitada. El proyecto diseña el proceso TO-BE, selecciona y adapta un modelo de proceso de software (iterativo-incremental con Scrum y prácticas DevOps) y construye un **PMV** (Incremento 1: registro nominal validado y expediente digital) con arquitectura hexagonal en Python/Flask.

**Equipo:** Porras Veli, Ricardo (Ingeniero de Proceso) · Auqui Huincho, Tania (Ingeniero de Desarrollo y Prototipado) · Huamani Rodriguez, Jean Piero (Ingeniero de Calidad y Mejora del Proceso).

> Todos los datos del software son **sintéticos**. La clasificación de anemia que muestra el sistema es referencial y no reemplaza el criterio del profesional de salud.

## Estructura del repositorio

```
.
├── README.md                    este archivo
├── .claude/agents/              definiciones de los subagentes (Claude Code)
├── coordinacion/                canal de comunicación entre agentes
│   ├── TABLERO.md               tareas, estado y responsable
│   ├── RUTAS.md                 mapa canónico de rutas (fuente de verdad)
│   ├── PROTOCOLO.md             reglas de comunicación
│   ├── plantillas/              SOLICITUD, SOLICITUD_DIAGRAMA, INFORME, CHECKLIST_CUMPLIMIENTO
│   ├── solicitudes/             <PREFIJO>-###.md (DIAG, DOC, DEV, INV, CONV, ORQ)
│   └── informes/                informes de salida de cada agente
├── guias/                       guías y consigna del docente (solo lectura)
├── entregables/                 versión VIGENTE de cada entregable (.md)
│   ├── semana-01/               + img/, anexos/Entrevista.md
│   ├── semana-02/               + img/
│   ├── semana-03-04/
│   ├── semana-05/               PDF Actividad 5 + extracción de texto (entregable .md por crear)
│   └── semana-06-integrador/    + anexos/
├── diagramas/                   src/ (puml, py) · png/ · svg/ · README.md (catálogo)
├── anemia_junin/                software PMV (Python/Flask, arquitectura hexagonal)
├── exportados/                  PDF/DOCX generados para el aula virtual
└── archivo/                     histórico: versiones anteriores, PDFs generados, zip, material de revisión
```

El detalle de cada ruta está en [`coordinacion/RUTAS.md`](coordinacion/RUTAS.md).

## Entregables por semana

| Semana | Tema (según guía) | Guía | Entregable vigente | Estado |
| --- | --- | --- | --- | --- |
| S1 | Enfoque de procesos de la organización: problema, actores, AS-IS, brechas, TO-BE, aporte del software, cadena de valor, indicadores | [`guias/S1_…`](guias/S1_Guia_trabajo_semana_1.md) | [`Entregable_Semana1`](entregables/semana-01/Entregable_Semana1_Anemia_Junin.md) | Borrador v5 — pendiente revisión (T-002) |
| S2 | Selección y justificación del modelo de proceso de software, representación, incrementos, riesgos, herramientas | [`guias/S2_…`](guias/S2_Guia_trabajo_semana_2.md) | [`Entregable_Semana2`](entregables/semana-02/Entregable_Semana2_Anemia_Junin.md) | Borrador v2 — pendiente revisión (T-003) |
| S3-4 | Actividades, organización, responsabilidades, productos, WBS, priorización, estimación y plan del proyecto | [`guias/S3-4_…`](guias/S3-4_Guia_trabajo_semanas_3_y_4.md) | [`Entregable_Semana3y4`](entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md) | Borrador v1 — pendiente revisión y diagramas (T-004, T-007) |
| S5 | Ejecución del Incremento 1 (PMV): categorización y sastrería, arquitectura, pruebas, despliegue (consigna S6 §3.1-3.4) | consigna S6 §3.1-3.4 | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` — **por crear**; base: [PDF Actividad 5](entregables/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf), [extracción](entregables/semana-05/_extraccion_Informe_Actividad5.md) | Por crear (T-005) |
| S6 | Informe integrador de las Unidades I y II | [consigna PDF](guias/S6_Consigna_e_instrumento_evaluacion_integrador.pdf), [extracción](guias/S6_Consigna_integrador_extraccion.md) | [`Informe_Integrador`](entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md) | Propuesta de revisión — por actualizar (T-006) |

Las versiones anteriores están en `archivo/versiones-anteriores/`. El historial completo se conserva en git (`git log --follow <ruta>`).

## Agentes y comunicación

| Agente | Modelo | Rol |
| --- | --- | --- |
| `orquestador` | opus | Estructura, rutas, README, tablero, archivo, commits |
| `revisor-documental` | opus | Cumplimiento estricto al 100 % de cada guía, redacción, checklist de cumplimiento |
| `diagramador` | opus | Diagramas con PlantUML/Python → PNG + SVG, fuentes en `diagramas/src` |
| `desarrollador` | fable | PMV `anemia_junin/`: código, pruebas, evidencias, README de ejecución |
| `investigador` | haiku | Investigación y resúmenes con fuentes (solo lectura) |
| `conversor-entregas` | opus | Conversión .md → PDF/DOCX en `exportados/` |

Definiciones: `.claude/agents/<agente>.md`. Los agentes se comunican **solo por archivos** en `coordinacion/`:

1. Las tareas (`T-###`) se registran en [`coordinacion/TABLERO.md`](coordinacion/TABLERO.md).
2. Un agente que necesita algo de otro crea `coordinacion/solicitudes/<PREFIJO>-###.md` desde la plantilla (p. ej. el revisor pide un diagrama con `DIAG-001.md`). El prefijo indica quién atiende: `ORQ`, `DOC`, `DIAG`, `DEV`, `INV`, `CONV`.
3. El agente destino responde en la misma solicitud (rutas producidas) y la marca `RESUELTA`.
4. Al terminar, cada agente deja su informe en `coordinacion/informes/AAAA-MM-DD_<agente>_<tarea>.md` y actualiza el tablero.

Reglas completas: [`coordinacion/PROTOCOLO.md`](coordinacion/PROTOCOLO.md).

## Convertir Markdown a PDF / DOCX

Ejecutar desde la carpeta del entregable para que se resuelvan las imágenes relativas.

**Con pandoc** (instalar en Windows: `winget install --id JohnMacFarlane.Pandoc`; para PDF se necesita además un motor, p. ej. MiKTeX para `xelatex`):

```bash
cd entregables/semana-01
pandoc Entregable_Semana1_Anemia_Junin.md -o ../../exportados/semana-01/Entregable_Semana1_Anemia_Junin.docx --toc
pandoc Entregable_Semana1_Anemia_Junin.md -o ../../exportados/semana-01/Entregable_Semana1_Anemia_Junin.pdf \
  --pdf-engine=xelatex -V lang=es -V mainfont="Arial" -V geometry:margin=2.5cm --toc
```

Para DOCX conviene usar las versiones PNG de los diagramas (`diagramas/png/`), ya que Word no siempre renderiza SVG.

**Alternativa sin pandoc (Python):**

```bash
pip install markdown python-docx xhtml2pdf
# Markdown → HTML (markdown) → PDF (xhtml2pdf); DOCX con python-docx
```

El agente `conversor-entregas` automatiza ambos caminos y guarda los resultados en `exportados/semana-XX/`.

## Cómo ejecutar el software

> *Sección provisional: el agente `desarrollador` la completará tras verificar la ejecución (tarea T-008).*

Referencia rápida (sin verificar aún):

```bash
cd anemia_junin
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -e ".[dev]"
pytest                           # pruebas
```

Detalle de ejecución, datos sintéticos y arquitectura: `anemia_junin/README.md` (por crear).

## Herramientas disponibles en el equipo de trabajo (verificado 2026-09-25)

| Herramienta | Estado |
| --- | --- |
| Python 3.14.6 + pip 26.1 | Disponible (pypdf instalado) |
| Java (OpenJDK 17.0.19, Temurin) | Disponible |
| Git 2.54 | Disponible |
| PlantUML (`plantuml.jar`) | No instalado |
| Graphviz (`dot`) | No instalado |
| Pandoc | No instalado |
