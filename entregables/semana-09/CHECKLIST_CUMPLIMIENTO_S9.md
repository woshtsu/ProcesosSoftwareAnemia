# Checklist de cumplimiento — Semana 9 (evaluación GQM) — estado final, tercera auditoría (18/10/2026)

- **Guía:** `guias/S9-PSW-GUÍA DE TRABAJO.md` (7 actividades con sus matrices, estructura III de 8 secciones, rúbrica IV de 5 criterios × 4 puntos) y las 6 aclaraciones del cliente.
- **Entregable auditado:** `entregables/semana-09/Entregable_Semana9_Anemia_Junin.md` (1 516 líneas; 29 023 palabras; 52 tablas; 55 figuras; Anexos A a G), fechado el 18/10/2026. Se evalúa `v1.0-PMV` (Inc. 1) y `v2.0.0-inc2` (Inc. 2 **completo**: RF-06 a RF-09, 18/18 SP), con el hito `v1.5.0-inc2-avance` como punto intermedio.
- **Alcance de la tercera auditoría:** cierre del Inc. 2 (fichas y capturas reales de RF-08 y RF-09), incorporación del dataset real de la DIRESA Junín (línea base AS-IS real, importación con seudónimos `DJ-NNNNN`, muestra de 500 niños, `FECHA_REFERENCIA` 30/06/2024, altitud INEI), métricas recalculadas (`resumen_gqm.json` con `valor_inc2` = v2.0) y sección «Historias de usuario» del `README.md` raíz.
- **Evidencias contrastadas (solo lectura):** `entregables/semana-09/evidencias_capturas/`, `entregables/semana-09/metricas/` (datos, salidas, gráficos), `pmv_fastapi/` (v2.0.0-inc2 en el árbol de trabajo), `Dataset/` (CSV crudo), `herramientas/gqm/` y `herramientas/dataset/`.
- **Revisor:** revisor documental y auditor de cumplimiento independiente (no participó en la redacción). **Rondas:** primera revisión y segunda pasada 16/10/2026; tercera auditoría 18/10/2026.
- **Verificaciones ejecutadas por el auditor en esta ronda:** `pytest -q -p no:cacheprovider` en `pmv_fastapi` = **328 passed**; `pytest tests/e2e` = **15 passed**; `ruff check .` = **All checks passed**; `ruff format --check .` = 95 archivos con formato correcto; 18 pruebas de arquitectura (`tests/arquitectura`) en verde; script de enlaces, imágenes, anclas y numeración: **58 enlaces/imágenes locales y 0 rotos; 44 anclas del índice y 0 faltantes; 52 tablas y 55 figuras consecutivas, todas citadas en el texto**; comparación de las 6 matrices con la guía, encabezado por encabezado: **idénticas**.
- **Regla de higiene de términos (comprobada):** no aparecen el nombre del asistente de IA, el nombre de su proveedor ni rutas absolutas del contenedor en el informe, este checklist, el `README.md` raíz, `metricas/`, `evidencias_capturas/` (md, json, py) ni `pmv_fastapi/` (sin `.git` ni `__pycache__`). La única coincidencia está en las líneas 42 y 89 del `README.md` raíz y es el nombre real de una carpeta de definiciones de agentes del repositorio (no una mención al asistente); no debe renombrarse.
- **Resultado:** 73 requisitos (67 de la guía + 6 aclaraciones): **72 CUMPLE y 1 «CUMPLE al publicar»** (E-12, etiqueta `v2.0-Inc2`). Cumplimiento ponderado con la regla acordada (CUMPLE = 1; CUMPLE al publicar = 1 porque procedimiento y evidencia existen; PARCIAL = 0,5; NO = 0): **100,0 %**. Si se contara hoy el ítem E-12 como 0,5: **99,3 %**. Hallazgos nuevos de esta ronda: **1 mayor, 6 menores y 4 de estilo; ninguno crítico**; ninguno incumple un requisito de la guía.
- **Puntaje probable de rúbrica: 20 / 20, condicionado** a que el equipo cree y publique la etiqueta `v2.0-Inc2` (Anexo B) antes de la exposición. Sin la etiqueta el criterio 2 podría quedar en 3/4 (19/20) porque la guía pide el enlace a esa etiqueta. Detalle en la Parte C.

> Convención: CUMPLE = el requisito está presente y verificado; CUMPLE al publicar = el documento tiene el procedimiento y la evidencia, y solo falta un acto del equipo en GitHub (no es incumplimiento del documento); CUMPLE PARCIAL = presente con una carencia concreta; NO CUMPLE = ausente. «Ubicación en guía» es la actividad, matriz o sección de la guía; «Sección del entregable» es la del informe actual (numeración nueva de tablas y figuras).

## Parte A. Checklist ítem por ítem de la guía

### A.1 Actividades 1 a 7 (matrices, preguntas y métricas)

| ID | Requisito de la guía | Ubicación en guía | Sección del entregable | Estado | Evidencia / observación |
| --- | --- | --- | --- | --- | --- |
| A1-01 | 3 objetivos GQM (G-01, G-02, G-03) | Act. 1 | §3.1, Tabla 8 | **CUMPLE** | Los tres goals coinciden con la Matriz 1.1 de la guía. |
| A1-02 | Cada objetivo con la estructura formal de 5 elementos (Objeto, Propósito, Enfoque de Calidad, Punto de Vista, Contexto) | Act. 1; rúbrica 1 | §3.1.1 a 3.1.3 | **CUMPLE** | Plantilla de la sesión S9 («Analizar / con el propósito de / con respecto a / desde el punto de vista de / en el contexto de»). |
| A1-03 | Matriz 1.1 con las 7 columnas exactas | Matriz 1.1 | Tabla 8 | **CUMPLE** | Encabezados idénticos a la guía (comprobado por script). |
| A1-04 | G-01 Producto (Arquitectura): estructura de código en GitHub, desacoplamiento, mantenibilidad, Arquitecto de Software | Matriz 1.1 | Tabla 8, §3.1.1 | **CUMPLE** | |
| A1-05 | G-02 Producto (Pruebas): Inc. 1 e Inc. 2, estabilidad funcional, cobertura y tasa de fallas, QA/Testers | Matriz 1.1 | Tabla 8, §3.1.2 | **CUMPLE** | |
| A1-06 | G-03 Proceso y Producto (Valor): efectividad, valor e impacto, Usuario Final / Product Owner | Matriz 1.1 | Tabla 8, §3.1.3 | **CUMPLE** | Declara que el punto de vista del Product Owner es simulado y que no hubo piloto. |
| A2-01 | Q1.1 (dominio aislado de frameworks) | Act. 2 | Tabla 9 | **CUMPLE** | Texto literal de la guía + «por qué importa» + métrica. |
| A2-02 | Q1.2 (puertos y adaptadores en módulos independientes) | Act. 2 | Tabla 9 | **CUMPLE** | |
| A2-03 | Q2.1 (% de RF con evidencias fotográficas aprobadas) | Act. 2 | Tabla 10 | **CUMPLE** | |
| A2-04 | Q2.2 (densidad de defectos entre PMV e Inc. 2) | Act. 2 | Tabla 10 | **CUMPLE** | M2.2 = 1,4 → 0,25 con la meta ≤ 0,2 **no cumplida** declarada; lectura alternativa 7/9 = 0,78 y «escapados a producción» 0/4 visibles junto a la principal. |
| A2-05 | Q3.1 (reducción de brechas AS-IS) | Act. 2 | Tabla 11 | **CUMPLE** | |
| A2-06 | Q3.2 (tiempos de respuesta, disponibilidad y satisfacción por incremento) | Act. 2 | Tabla 11 | **CUMPLE** | El índice M3.2 incluye solo V1 a V3; V4 a V6 se informan aparte (Tablas 7, 12, 34 y 38). |
| A2-07 | Árbol de preguntas Goal-Question-Metric visible | Act. 2; sesión S9 | Figura 2 (diagrama 71) | **CUMPLE** | Q1.3 y M1.3 rotuladas como complementarias. |
| A3-01 | Matriz 3.1 con las 8 columnas exactas | Matriz 3.1 | Tabla 12 | **CUMPLE** | Encabezados idénticos (comprobado por script). |
| A3-02 | M1.1 Índice de Contaminación del Dominio, metas 0,0 % / 0,0 % | Matriz 3.1 | Tabla 12; §4.3 | **CUMPLE** | 0 % en v1.0, v1.5 y v2.0 (0/8, 0/19, 0/32 importaciones externas; `m11_contaminacion.json`). |
| A3-03 | M1.2 Cohesión de Módulos Hexagonales, metas 100 % / 100 % | Matriz 3.1 | Tabla 12; §4.2 | **CUMPLE** | 40,0 % → 100,0 % (2/5 → 5/5 componentes), criterio estricto y laxo explicados. |
| A3-04 | M2.1 Cobertura Funcional con Capturas, metas 100 % / 100 % | Matriz 3.1 | Tabla 12; §5.5 | **CUMPLE** | 5/5 en el Inc. 1 y 4/4 en el Inc. 2 (9/9 RF con captura de resultado). |
| A3-05 | M2.2 Tasa de Defectos Funcionales, metas ≤ 1,0 / ≤ 0,2 Def/RF | Matriz 3.1 | Tabla 12; Tablas 29-30 | **CUMPLE** | Fuente declarada (registros DEF en lugar de GitHub Issues) justificada; DEF-09 hallado por E2E antes de liberar cuenta como defecto del incremento. |
| A3-06 | M3.1 Cobertura de Brechas Resueltas, metas ≥ 60 % / ≥ 90 % | Matriz 3.1 | Tabla 12; Tablas 36-37 | **CUMPLE** | 25,0 % → 33,3 % (estricta 16,7 % en ambas; sensibilidades 41,7 / 41,7 / 50,0 %; sobre brechas comprometidas 100 % y 75 %); metas no cumplidas, con causa y acción. |
| A3-07 | M3.2 Índice de Impacto en Valor, metas mejora ≥ 50 % / ≥ 80 % | Matriz 3.1 | Tabla 12; §6.5; Tabla 52 | **CUMPLE** | 57,6 % → 100,0 % con V1 a V3 y salvedad explícita sobre V4 a V6. |
| A3-08 | Fórmula, método de extracción y fuente de datos reales y trazables a un script y a un JSON | Act. 3; aclaración 4 | Tabla 12 | **CUMPLE** | Cada fila cita script y `datos/*.json`; todos existen (se abrieron `m21`, `m22`, `m31`, `m32_*`, `resumen_gqm`, `exploratorias_inc2_final`, `importacion_*`). |
| A3-09 | Metas no cumplidas analizadas (M1.2 Inc. 1, M2.2 Inc. 1 e Inc. 2, M3.1 ambos) | Act. 3, 7 | §4.5, §5.5, §6.4 | **CUMPLE** | Cada incumplimiento tiene causa raíz y acción; la propuesta de metas acumuladas de M3.1 se rotula «no aprobada». |
| A4-01 | Estructura hexagonal descrita y equivalencia `/src` de la guía con `app/` (Python/FastAPI) | Act. 4 | §4.1, Tabla 13; Figuras 3 a 6; Anexo G.2 | **CUMPLE** | Árboles de v1.0 y v1.5 correctos; vista de puertos y adaptadores de v2.0 (diagrama 72) con los módulos reales. |
| A4-02 | Matriz 4.1 con las 4 columnas exactas | Matriz 4.1 | Tablas 14 y 15 | **CUMPLE** | Una matriz por versión; encabezados idénticos. |
| A4-03 | Fila Núcleo de Dominio | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | v2.0: 67 importaciones, 33 estándar, 34 internas, 0 externas; 32 clases. |
| A4-04 | Fila Puertos de Entrada | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | No Conforme en Inc. 1; Conforme en Inc. 2: los 9 `Protocol` con archivo y línea **verificados uno por uno contra el código**. |
| A4-05 | Fila Puertos de Salida | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | `Reloj` (`reloj.py:7`) y `RepositorioNinos` (`repositorio_ninos.py:14`, 13 métodos) verificados. |
| A4-06 | Fila Adaptadores de Entrada | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | `api.py:19` a `api.py:26` importan 8 de los 9 puertos (verificado; `ImportarDataset` lo usa la línea de comandos). |
| A4-07 | Fila Adaptadores de Salida | Matriz 4.1 | Tablas 14-15 | **CUMPLE** | `memoria.py:13` y `sqlalchemy_repo.py:239` verificados; SQLAlchemy solo en `sqlalchemy_repo.py:7, 24, 25`. Observación de estilo R3-08 sobre la columna «Ruta». |
| A4-08 | Reporte de desacoplamiento del dominio (cero contaminación) con evidencia cuantitativa | Act. 4; Sec. III-4 | §4.3, Tablas 16-17 | **CUMPLE** | M1.1 y M1.3 (violaciones 1 → 0); 18 pruebas de arquitectura vigilan la regla (ejecutadas). |
| A4-09 | Auditoría evidenciada en la carpeta y el repositorio GitHub | Act. 4; rúbrica 2 | §4.1; Figuras 3-4; Tabla 15; Anexo B | **CUMPLE** | Capturas de GitHub de `v1.0-PMV/app` y de `v1.5.0-inc2-avance/pmv_fastapi/app` (la segunda abierta con Read: URL visible, commit «Inc. 2 avance 50 %…»). La captura de `v2.0-Inc2` figura como paso 4 de la lista previa a la exposición (ver E-12). |
| A4-10 | Decisiones de arquitectura documentadas (ADR del Inc. 2) | Act. 4 (mantenibilidad) | §4.4; Tabla 51 | **CUMPLE** | ADR-007 a ADR-010 con contexto, decisión y consecuencias; los cuatro archivos existen en `pmv_fastapi/docs/adr/`. |
| A5-01 | Ficha 5.1 por RF del Incremento 1 (RF-01 a RF-05) | Act. 5; ficha modelo | Tablas 19-23 | **CUMPLE** | 5 fichas. |
| A5-02 | Ficha 5.1 por RF del Incremento 2 (RF-06 a RF-09) | Act. 5 | Tablas 24-27 | **CUMPLE** | 4 fichas ejecutadas; RF-08 y RF-09 ya no son «planificadas». |
| A5-03 | Campos de la ficha: proyecto, incremento, código RF/HU, nombre, criterio Dado-Cuando-Entonces, ID caso de prueba, tipo, resultado esperado, evidencias, evaluación, fecha, evaluador | Ficha 5.1 | Tablas 19-27 | **CUMPLE** | Todos presentes más tiempos medidos y resultado observado. Los criterios de RF-08 y RF-09 coinciden con los del `README.md` raíz. |
| A5-04 | Capturas de entrada y de resultado del software en ejecución por RF (mínimo 2) | Ficha 5.1; rúbrica 3 | Figuras 7-38 | **CUMPLE** | 32 capturas de fichas (RF-01: 2; RF-02: 6; RF-03: 3; RF-04: 3; RF-05: 4; RF-06: 3; RF-07: 3; RF-08: 3; RF-09: 5). Las de RF-06 y RF-07 son del hito v1.5 (declarado en §5.2 y Tabla 28; ambos RF siguen en verde en v2.0). |
| A5-05 | Archivo de imagen indicado en cada captura | Ficha 5.1 | Cada «Captura N» | **CUMPLE** | 55 imágenes referenciadas, 0 faltantes; 44 PNG en `evidencias_capturas/`. |
| A5-06 | Evaluación [APROBADO], fecha, evaluador (QA Lead) | Ficha 5.1 | Tablas 19-27 | **CUMPLE** | Evaluador nominado con «firma pendiente» y aclaración de que APROBADO es resultado automatizado (ver pendiente 4). |
| A5-07 | Matriz 5.2 con las 6 columnas exactas | Matriz 5.2 | Tabla 28 | **CUMPLE** | Encabezados idénticos (comprobado por script). |
| A5-08 | Matriz 5.2 cubre todos los RF de los Incrementos 1 y 2 | Matriz 5.2; rúbrica 3 | Tabla 28 | **CUMPLE** | Los 9 RF con ID de caso, archivo de captura de resultado existente y estado Aprobado. |
| A5-09 | Capturas claras y legibles que permiten verificar la ejecución | Rúbrica 3 | Figuras 7-41 | **CUMPLE** | 9 capturas nuevas abiertas con Read (ver Parte D); texto legible, pie «Evidencia S9» con hora y URL. Observaciones residuales: campos de fecha en formato mm/dd (H-08, declarado en §5.0 nota 1) y capturas JSON/CSV de RF-05 poco informativas (H-19). |
| A5-10 | Q2.1 y Q2.2 respondidas con la métrica | Act. 2 | §5.5 | **CUMPLE** | |
| A5-11 | Evidencia con datos reales (dataset DIRESA Junín) y contraste con registros del sistema | Aclaración 2 (capturas reales) | §5.1.1; Figuras 39-41 | **CUMPLE** | Expediente DJ-04505, alertas de la muestra y registro SISTEMA 79000003; sin DNI ni nombres de personas reales; coinciden con `resultados_inc2final.json`. |
| A6-01 | Matriz 6.1 con las 5 columnas exactas | Matriz 6.1 | Tabla 31 | **CUMPLE** | Encabezados idénticos (comprobado por script). |
| A6-02 | Trazabilidad por brecha B1 a B6 (resueltas y no resueltas) | Act. 6; rúbrica 4 | Tablas 31 y 36 | **CUMPLE** | 6 filas; B3, B4 y B5 declaradas «no resueltas aún», B2 y B6 parciales. |
| A6-03 | Indicadores cuantitativos de valor con línea base AS-IS y fuente | Act. 6; Q3.2 | Tablas 34, 35, 52; §6.3 | **CUMPLE** | V1 a V6 con fuente en JSON. |
| A6-04 | Q3.1 y Q3.2 respondidas | Act. 2 | §6.8 | **CUMPLE** | |
| A6-05 | Distinción entre valor medido y valor que exige piloto | Act. 6; aclaración 3 | Tabla 39; §6.7 | **CUMPLE** | Explícito: «vencido» significa «sin registro en la base importada, no no realizado»; V6 es proxy y el SUS está pendiente. |
| A6-06 | Línea base AS-IS **real** con fuente y método | Act. 6 | §6.2; Tabla 32; Figuras 43-45 | **CUMPLE** | Todos los indicadores se recalcularon desde el CSV crudo y coinciden (ver Parte D). |
| A6-07 | Importación del dataset sin datos personales (seudónimos, fecha de referencia, altitud) | Aclaración 2; ADR-009 | §6.2; Tabla 33; Tabla 46 | **CUMPLE** | Códigos `DJ-NNNNN`, sin DNI ni nombres, reloj fijo 30/06/2024, altitud de la capital provincial declarada como aproximación; cifras de `importacion_muestra500.json` e `importacion_completa.json` coinciden. |
| A7-01 | Matriz 7.1 con las 5 columnas exactas | Matriz 7.1 | Tabla 40 | **CUMPLE** | Encabezados idénticos (comprobado por script). |
| A7-02 | Filas M1.1, M2.2 y M3.1 de la guía con valor real, variación, causa raíz y acción | Matriz 7.1 | Tabla 40 | **CUMPLE** | Más M1.2, M1.3, M2.1, M3.1 complementaria y estricta, M2.2 alternativa, M3.2, V4 y V5. |
| A7-03 | Variaciones porcentuales correctas | Matriz 7.1 | Tabla 40 | **CUMPLE** | Recalculadas (p. ej., V4 +365,7 %, v1.5 → v2.0 +33,6 %; M2.2 −82,1 %). |
| A7-04 | Plan de mejora continua PDCA | Act. 7 | §7.3, Tabla 41 | **CUMPLE** | Acciones con Plan, Do, Check, Act, responsable y fecha. |
| A7-05 | Diagnóstico comparativo (evolución del proceso) por pilar | Act. 7; rúbrica 5 | §7.2.1 a 7.2.3; §7.4 | **CUMPLE** | |

### A.2 Estructura III del entregable (8 secciones) y anexos

| ID | Requisito de la guía | Ubicación en guía | Sección del entregable | Estado | Evidencia / observación |
| --- | --- | --- | --- | --- | --- |
| E-01 | Sección 1. Carátula e integrantes del equipo (Noveno Ciclo) | Sec. III | §1, Tablas 1-3 | **CUMPLE** | Tabla 1 con fecha 18/10/2026; mapa de exposición por pilares (Tabla 3). |
| E-02 | Sección 2. Resumen ejecutivo y objetivos de evaluación GQM | Sec. III | §2, Tablas 4-7 | **CUMPLE** | Cierre del Inc. 2 con 4/4 historias y 18/18 SP; salvedades de M2.2, M3.1 y M3.2. |
| E-03 | Sección 3. Matriz de objetivos, preguntas y métricas | Sec. III | §3, Tablas 8-12 | **CUMPLE** | |
| E-04 | Sección 4. Auditoría de arquitectura hexagonal en GitHub | Sec. III | §4.1 a 4.5 | **CUMPLE** | |
| E-05 | Sección 5. Fichas de pruebas con capturas para cada RF de Inc. 1 y 2 | Sec. III | §5.1 a 5.5 | **CUMPLE** | Los 9 RF con ficha, captura de resultado y pruebas (antes PARCIAL; resuelto). |
| E-06 | Sección 6. Evaluación de entrega de valor al usuario final | Sec. III | §6.1 a 6.8 | **CUMPLE** | |
| E-07 | Sección 7. Comparativa GQM y plan de mejora continua | Sec. III | §7.1 a 7.4 | **CUMPLE** | |
| E-08 | Sección 8. Anexos | Sec. III | §8, Anexos A-G | **CUMPLE** | |
| E-09 | Numeración y títulos de las 8 secciones en el orden de la guía | Sec. III | Encabezados `##` | **CUMPLE** | |
| E-10 | Anexo: carpeta `/evidencias_capturas/` organizada por RF | Sec. III-8 | Anexo A, Tabla 42 | **CUMPLE** | La Tabla 42 coincide con el contenido real (carpetas `RF-01/` a `RF-09/`, `arquitectura/`, `datos_reales/`, raíz). |
| E-11 | Anexo: enlace al repositorio GitHub con la etiqueta `v1.0-PMV` | Sec. III-8 | Anexo B | **CUMPLE** | Etiqueta existente y enlazada. |
| E-12 | Anexo: enlace al repositorio con la etiqueta `v2.0-Inc2` | Sec. III-8 | Anexo B; Tabla 1; Tabla 15 | **CUMPLE al publicar** | La etiqueta aún no existe: la crea el equipo con los comandos del Anexo B (commit, `git tag -a v2.0-Inc2`, `push`). El documento ya trae el procedimiento exacto, la dirección esperada (`.../tree/v2.0-Inc2/pmv_fastapi/app`), la lista previa a la exposición y el estado real («mientras no exista en GitHub, la versión evaluada está en el árbol de trabajo de la rama»). No se cuenta como incumplimiento del documento; pasa a CUMPLE al ejecutar el acto y añadir la captura (ver pendiente 1). |

**Matrices de la guía con columnas exactas (comprobado por script, encabezado por encabezado, en esta ronda):** Matriz 1.1 = Tabla 8 (7 columnas), Matriz 3.1 = Tabla 12 (8), Matriz 4.1 = Tablas 14 y 15 (4), Matriz 5.2 = Tabla 28 (6), Matriz 6.1 = Tabla 31 (5) y Matriz 7.1 = Tabla 40 (5): **ninguna alterada**. Solo cambia el número de filas (ampliación legítima: M1.3 complementaria, nueve RF, lecturas alternativas).

**Metas por métrica (Inc. 1 / Inc. 2) frente a lo medido (v2.0 completo):**

| Métrica | Meta guía Inc. 1 / Inc. 2 | Medido Inc. 1 / Inc. 2 | ¿Cumple Inc. 1 / Inc. 2? | Análisis de la meta no cumplida |
| --- | --- | --- | --- | --- |
| M1.1 | 0,0 % / 0,0 % | 0,0 % / 0,0 % | Sí / Sí | — |
| M1.2 | 100 % / 100 % | 40,0 % / 100,0 % | No / Sí | §4.5 y Tabla 40: faltaban puertos de entrada, el puerto de salida estaba dentro de `application` y el adaptador HTTP importaba una clase concreta; acción ADR-008. |
| M2.1 | 100 % / 100 % | 100,0 % / 100,0 % | Sí / Sí | 9/9 RF con captura y prueba; 48/48 criterios Dado-Cuando-Entonces en verde. |
| M2.2 | ≤ 1,0 / ≤ 0,2 Def/RF | 1,4 / 0,25 (escapados 0/4; alternativa 7/9 = 0,78) | No / **No** | §5.5: DEF-09 (RF-08) lo halló el E2E antes de liberar y cuenta; la meta del Inc. 2 no se cumple y el informe lo dice (honestidad correcta). |
| M3.1 | ≥ 60 % / ≥ 90 % | 25,0 % / 33,3 % (estricta 16,7 % / 16,7 %) | No / No | §6.4: el plan reparte 6 brechas en 6 incrementos; B2 en 0,5 (faltan recordatorios, INC-4) y B3 en 0. |
| M3.2 | mejora ≥ 50 % / ≥ 80 % | 57,6 % / 100,0 % (solo V1 a V3) | Sí / Sí | §6.5: V4 empeora (175 → 610 → 815 ms) y queda fuera del índice, con la salvedad en Tablas 7 y 12. |

## Parte B. Verificación de las 6 aclaraciones del cliente

| ID | Aclaración | Dónde se verifica | Estado | Evidencia del auditor |
| --- | --- | --- | --- | --- |
| B-01 | Separación clara de los 3 pilares técnicos (arquitectura hexagonal / pruebas Inc. 1 y 2 / entrega de valor) | Tabla 3; etiquetas «[Pilar N]» en §3 a §7; Tabla 41 con columna Pilar | **CUMPLE** | Cada pilar tiene goal, preguntas, métricas, sección, diagnóstico y acciones. El cuerpo es largo (H-17 / R3-11). |
| B-02 | Actividad 5 con capturas REALES del software ejecutado para cada RF | Figuras 7-41; `evidencias_capturas/`; `capturar_evidencias.py` | **CUMPLE** | 9 PNG nuevos abiertos (RF-08: 2; RF-09: 3; `datos_reales/`: 3; GitHub v1.5: 1): PWA real v2.0 con pie «Evidencia S9», hora (17/10/2026 20:55) y URL local; las cifras de las fichas coinciden con lo visible y con `resultados_inc2final.json`. |
| B-03 | Avance del Inc. 2 antes del informe, con trazabilidad a entregables previos | §2.1, Tablas 5-6; Tabla 4 | **CUMPLE** | Ahora el Inc. 2 está completo: la API de v2.0 tiene **15 rutas** (12 en v1.5, 9 en v1.0), con `GET /api/agenda`, `POST /api/ninos/{id}/controles/{codigo}/asistencia` y `GET /api/ninos/{id}/asistencias` verificadas con `openapi()`; 328 + 15 pruebas en verde. |
| B-04 | Métricas con cálculo REAL, cada valor rastreable a JSON o salida | Tablas 7, 12, 29-40; `metricas/datos/`, `salidas/` | **CUMPLE** | Parte D: 34 filas de cifras contra su JSON, salida, código o CSV crudo; ninguna discrepancia numérica. |
| B-05 | El documento se puede exponer dividido en los 3 pilares | Tabla 3; Anexo E, Tabla 43 | **CUMPLE** | Mapa y guion de ~5 min por pilar con figuras y pregunta probable del docente. |
| B-06 | Uso coherente del material complementario (sesión GQM) | §3.1.1-3.1.3; Figura 2; Anexo F | **CUMPLE** | Plantilla de la sesión; Anexo F con Basili et al., Sánchez-Seco et al., Hernández et al., IEEE SWEBOK, Sommerville, Pressman, INEI y DIRESA Junín. |

## Parte C. Autoevaluación con la rúbrica (20 puntos)

| Criterio | Puntaje probable | Justificación | Qué falta para el máximo |
| --- | --- | --- | --- |
| 1. Formulación del Modelo GQM (Act. 1, 2 y 3) | **4 / 4** | 3 goals con los 5 elementos de Basili, 6 preguntas literales (+ Q1.3 complementaria), 6 métricas con fórmula, script, fuente y metas Inc. 1 / Inc. 2; producto (G-01, G-02) separado de proceso y valor (G-03). | Nada. |
| 2. Auditoría de Arquitectura Hexagonal en GitHub (Act. 4) | **4 / 4 con la etiqueta publicada; 3 / 4 si no existe `v2.0-Inc2` el día de la exposición** | Matriz 4.1 por versión con archivo y línea verificados contra el código; M1.1 = 0,0 %; M1.3 y 18 pruebas de arquitectura; capturas de GitHub de `v1.0-PMV` y de `v1.5.0-inc2-avance`. La guía pide el enlace a `v2.0-Inc2`, que el equipo crea. | Ejecutar los comandos del Anexo B, capturar `tree/v2.0-Inc2/pmv_fastapi/app` y reemplazar «la publicará» por «publicada» en la Tabla 15 y en la Tabla 1. |
| 3. Pruebas Funcionales con Capturas por RF (Act. 5) | **4 / 4** | 9 fichas con 32 capturas reales, Matriz 5.2 con columnas exactas y los 9 RF, 328 + 15 pruebas, cobertura 100 %, 48/48 criterios, 72 exploratorias, 9 defectos registrados. Las capturas de RF-06 y RF-07 son del hito v1.5 (declarado) y las de RF-08 y RF-09 de la v2.0. | Nada obligatorio (opcional: regenerar RF-06 y RF-07 sobre v2.0 con la muestra real). |
| 4. Evaluación de Entrega de Valor al Usuario (Act. 6) | **4 / 4** | Matriz 6.1 con las 6 brechas; línea base AS-IS real recalculada desde el CSV; V1 a V6; M3.1 con lectura principal, complementaria, sensibilidades y estricta; no sobredeclara (piloto y SUS pendientes). | Nada. |
| 5. Comparativa GQM y Mejora Continua (Act. 7) | **4 / 4** | Matriz 7.1 con variaciones recalculadas, causa raíz y acción; diagnóstico por pilar; plan PDCA; lecciones. Reconoce que M2.2 y M3.1 no alcanzan la meta. | Nada. |

**Total probable: 20 / 20, condicionado a publicar la etiqueta `v2.0-Inc2`** (si no existe: 19 / 20). Las metas no cumplidas (M2.2 = 0,25 frente a ≤ 0,2; M3.1 = 33,3 % frente a ≥ 90 %) **no restan puntos**: la rúbrica evalúa la formulación, la evidencia y el análisis, y el informe los declara y analiza.

## Parte D. Auditoría de veracidad: cifras verificadas

**Método.** Cada cifra se contrastó con su fuente primaria (JSON de `metricas/datos/`, salida cruda, código, CSV crudo o ejecución propia) y, cuando procedía, se recalculó de forma independiente.

| N.º | Cifra del informe | Ubicación | Fuente / recálculo del auditor | Resultado |
| --- | --- | --- | --- | --- |
| D-01 | 328 pruebas por defecto en verde (v2.0) | Tablas 18, 45; §5.4 | `pytest -q -p no:cacheprovider` ejecutado: 328 passed | Coincide |
| D-02 | 15 pruebas E2E (v2.0) | Tabla 18 | `pytest tests/e2e` ejecutado: 15 passed | Coincide |
| D-03 | `ruff check` limpio; 95 archivos con formato | Tabla 18 | `ruff check .` = All checks passed; `ruff format --check .` = 95 archivos | Coincide |
| D-04 | 18 pruebas de arquitectura | §4.3 | `tests/arquitectura/test_dependencias.py` (18 casos, incluidas en las 328) | Coincide |
| D-05 | Cobertura 100 % (1 700 sentencias, 264 ramas) | Tabla 18 | `metricas/salidas/v2.0/` | Coincide |
| D-06 | M2.2: Inc. 1 = 1,4 (7/5); Inc. 2 = 0,25 (1/4); avance 0,0 (0/2) | Tablas 7, 30, 40 | `m22_defectos.json`: `inc1.tasa_def_por_rf` 1,4 (n=7, n_rf=5); `inc2.tasa_def_por_rf` 0,25 (n=1, n_rf=4); `inc2_avance` 0,0 (0/2); `cumple.Inc.2` = false | Coincide |
| D-07 | M2.2 alternativas: escapados 0/4; todos los funcionales 7/9 = 0,78 | Tabla 30 | `m22_defectos.json` (variantes); 7/9 = 0,7778 | Coincide |
| D-08 | M3.1: 25,0 → 33,3 %; estricta 16,7 %; sensibilidades 41,7 / 41,7 / 50,0 %; sobre comprometidas 100 % y 75 % | Tablas 36-37 | `m31_brechas.json`: 1,5/6 = 25,0; 2,0/6 = 33,3; 1/6 = 16,7; 2,5/6 = 41,7; 3,0/6 = 50,0; 1,5/2 = 75,0 | Coincide |
| D-09 | M2.1 = 100 % (4/4 en el Inc. 2); criterios 17/17, 33/33, 48/48 | Tablas 7, 18 | `m21_cobertura_rf.json`: v1.0 5 RF y 17/17; v1.5 7 RF y 33/33; v2.0 9 RF y 48/48 | Coincide |
| D-10 | M1.1 0/8, 0/19, 0/32; M1.2 40 → 100 %; M1.3 1 → 0 | Tablas 7, 16-17 | `resumen_gqm.json` y `m11/m12/m13` | Coincide |
| D-11 | p95 agregado V4: 175 → 610 → 815 ms; +365,7 %; +33,6 % | Tablas 34, 38, 40 | `m32_carga.json` (promedio de 2 corridas: 190/160, 660/560, 790/840); (815−175)/175 = 365,7 %; (815−610)/610 = 33,6 % | Coincide |
| D-12 | p95 por endpoint (p. ej., `GET /api/ninos` 270 / 745 / 1 045 ms) | Tabla 38 | `m32_carga.json` (escenarios) | Coincide |
| D-13 | V5 disponibilidad 100 % (856/856 sondas); V6 48/48 | Tabla 34 | `m32_disponibilidad.json` y `m21` | Coincide |
| D-14 | Valores de la Tabla 7 y de la Tabla 40 | Tablas 7, 40 | `resumen_gqm.json` (`valor_inc2` = v2.0) | Coincide |
| D-15 | Línea base AS-IS: 12 486 diagnósticos; `num_doc` con 8 754 valores distintos | Tabla 32; §6.2 | Recalculado desde el CSV crudo con un script propio | Coincide |
| D-16 | Control registrado al mes / 3 meses / 6 meses: 67,1 % / 54,7 % / 46,3 % (70,2 / 63,8 / 66,1 % con seguimiento posible) | Tablas 32, 35 | Recalculado desde el CSV crudo; `asis_dataset_diresa.json` | Coincide |
| D-17 | Brecha territorial: 6 meses 57,3 % en Huancayo (4 194 diagnósticos) a 79,2 % en Tarma | §6.2 | Recalculado desde el CSV crudo | Coincide |
| D-18 | Importación de la muestra: 12 486 filas, 11 686 con evaluación utilizable, 500 niños, 1 290 evaluaciones (309 + 286 + 242 + 453) | Tabla 33 | `importacion_muestra500.json`; la suma de tipos da 1 290 | Coincide |
| D-19 | Importación completa: 11 686 niños, 29 712 evaluaciones (7 584 + 6 174 + 5 377 + 10 577), 800 omitidos | Tabla 33 | `importacion_completa.json`; la suma da 29 712 | Coincide |
| D-20 | Concordancia severidad HIS vs. sistema: 64,1 % (288/449) y 65,8 % (6 916/10 503) | Tabla 33 | `importacion_*.json`; 288/449 = 64,14 %; 6 916/10 503 = 65,85 % | Coincide |
| D-21 | 1 638 controles vencidos de 419 niños (83,8 %); ALTA 1 543, MEDIA 71, BAJA 24; 27 por vencer en 7 días | Tabla 35; Figura 40 | `m32_dataset_real.json`; 1 543 + 71 + 24 = 1 638; 419/500 = 83,8 %; captura `DJ_alertas_muestra_real.png` | Coincide |
| D-22 | Oráculo independiente: F1 = 1,000 (TP 419, FP 0, FN 0, TN 81); 1 638/1 638 por control | Tabla 35 | `m32_dataset_real.json` (`oraculo`) | Coincide |
| D-23 | Vencidos por tipo: 1 212 por edad y 426 de tratamiento; C1M/C3M/C6M 182/152/92 | Tabla 35 | `m32_dataset_real.json` | Coincide |
| D-24 | Tiempos con 500 niños: agenda mediana 68,0 ms (p95 73,6), alertas 87,6 ms (p95 118,3) | Tabla 35 | `m32_dataset_real.json` (`tiempos_respuesta_500_ninos_ms`) | Coincide |
| D-25 | 27 exploratorias del cierre, todas OK (RF-08 y RF-09); 45 + 27 = 72 | §5.4; Anexo G.4 | `exploratorias_inc2_final.json`: 27 casos, 27 OK; `exploratorias_inc2.json`: 45 | Coincide |
| D-26 | API: 9 → 12 → 15 rutas; nuevas `GET /api/agenda`, `POST …/asistencia`, `GET …/asistencias` | §2.1; Tabla 5 | `m31_brechas.json` (`hechos_verificados`) y `app.openapi()` (15 rutas) | Coincide |
| D-27 | Captura RF-08 paso 2: 19 controles de 17 niños; 7 cumplidos, 10 pendientes, 2 vencidos; por día 3/2/9/5 | Tabla 26; Figura 32 | Imagen abierta; `resultados_inc2final.json`; 1 + 1 + 3 + 2 = 7 cumplidos | Coincide |
| D-28 | Captura RF-08 paso 3: filtro «LA ESPERANZA», 4 controles de 3 niños, 1 vencido | Tabla 26; Figura 33 | Imagen abierta y JSON | Coincide |
| D-29 | Captura RF-09 paso 2: C1M del 17/06/2024 «Cumplido (asistió)», DJ-00481; 90 ms | Tabla 27; Figura 35 | Imagen abierta; JSON | Coincide |
| D-30 | Captura RF-09 paso 3b: filtro RIO TAMBO + MEDIA, 11 alertas, marca «Inasistencia registrada»; MEDIA 72 / BAJA 23 (frente a 71 / 24 antes) | Tabla 27; Figura 37 | Imagen abierta; JSON; el cambio 71 → 72 y 24 → 23 prueba la subida BAJA → MEDIA | Coincide |
| D-31 | Captura RF-09 paso 4: 409 «El control DHx del 2024-05-24 ya tiene una asistencia registrada.»; 54 ms | Tabla 27; Figura 38 | Imagen abierta; JSON | Coincide |
| D-32 | Datos reales: expediente DJ-04505 (202 ms; HIS «Moderada» frente a «Sin anemia» del sistema), alertas 562 ms, registro SISTEMA 79000003 con 10 controles pendientes | §5.1.1; Figuras 39-41 | Tres imágenes abiertas; JSON | Coincide |
| D-33 | GitHub `v1.5.0-inc2-avance/pmv_fastapi/app`: commit «Inc. 2 avance 50 %…» | Figura 4; Anexo B | Imagen abierta (URL visible). La publicación en GitHub no se puede verificar desde el contenedor (sin acceso) ni la etiqueta en `git tag` local | Coincide con la imagen; sin verificación remota |
| D-34 | README raíz «Historias de usuario»: 9 historias y sus 15 endpoints | `README.md` líneas 11-34 | `app.openapi()`: los endpoints citados existen; criterios de HU-01 a HU-05 y HIST-2.1 a 2.4 equivalentes a los de las Tablas 19-27 | Coincide (ver R3-03 a R3-05 por otras líneas del README) |

**Capturas nuevas abiertas con Read (9):** `RF08_inc2final_paso2_resultado.png`, `RF08_inc2final_paso3_resultado_filtro_establecimiento.png`, `RF09_inc2final_paso2_asistio.png`, `RF09_inc2final_paso3b_alerta_prioridad_elevada.png`, `RF09_inc2final_paso4_409_segundo_registro.png`, `DJ_alertas_muestra_real.png`, `DJ_expediente_DJ-04505.png`, `SISTEMA_expediente_79000003.png` y `github_v1.5.0-inc2-avance_app.png`. No se abrieron `RF08_inc2final_paso1_entrada.png`, `RF09_inc2final_paso1_entrada.png` ni `RF09_inc2final_paso3_no_asistio.png`; sus resultados se contrastaron con `resultados_inc2final.json`.

**Observaciones de lectura (no son errores).** (1) «Controles vencidos visibles = 100 %» se mide frente a un oráculo que aplica la misma regla; el informe lo declara y delimita su alcance («verifica el cálculo de la agenda sobre datos reales, no la importación del CSV»). (2) El AS-IS «0 % estructural» de visibilidad de vencidos es un supuesto declarado, no una medición. (3) La altitud usada es la de la capital provincial (aproximación declarada).

## Parte E. Hallazgos por severidad

### E.1 Seguimiento de los hallazgos anteriores (H-01 a H-22 y N-01 a N-08)

| N.º | Severidad original | Resumen | Estado en la tercera auditoría | Verificación |
| --- | --- | --- | --- | --- |
| **H-01** | MAYOR | Evidencia de GitHub de v1.5 y etiqueta `v2.0-Inc2` | **CUMPLE al publicar** | v1.5 publicada con capturas (Figuras 3-4); `v2.0-Inc2` la crea el equipo (Anexo B). Ver E-12. |
| **H-02** | MAYOR | M2.2 del Inc. 2 solo por atribución | **RESUELTO** | M2.2 = 0,25 con DEF-09 contado; alternativas visibles; meta no cumplida declarada. |
| **H-03** | MAYOR | Índice M3.2 sin V4 a V6 | **RESUELTO** | Salvedad en Tablas 7 y 12; V4 a V6 en Tablas 34 y 38. |
| **H-04** a **H-07**, **H-09** a **H-12**, **H-14** a **H-16**, **H-18**, **H-20** a **H-22** | MENOR y ESTILO | Redacciones, fechas, citas, anexos, CHANGELOG, encabezados | **RESUELTOS** | Verificados en rondas anteriores y sin regresión. H-16 (RF-08 y RF-09 sin ficha): ahora fichas ejecutadas con 8 capturas. |
| **H-08** | MENOR | Campos de fecha mm/dd en las capturas | **PARCIAL** | Declarado en §5.0 nota 1; las capturas nuevas de RF-08 también lo muestran (05/30/2024). Opcional. |
| **H-13** | MENOR | Rutas absolutas y v1.0 fuera del repositorio | **PARCIAL** | Persiste el problema de la variable relativa `GQM_RAIZ_V10` (ver R3-02, antes N-02). |
| **H-17** | MENOR | Longitud y repetición | **PARCIAL** | 29 023 palabras (21 650 en la ronda anterior); crecimiento justificado por el cierre y el dataset real (R3-11). |
| **H-19** | ESTILO | Capturas JSON y CSV de RF-05 poco informativas | **ABIERTO** | Sin cambios; declarado en la Figura 24. Opcional. |
| **N-01** | MENOR | Hora de los árboles (14:17) | **RESUELTO** | Ya no figura en §4.1. |
| **N-02** | MENOR | `GQM_RAIZ_V10` relativa y `tar -C` sin `mkdir` en el Anexo C | **ABIERTO** | Verificado de nuevo: ver R3-02. |
| **N-03** | MENOR | Remisión «Anexo G.4 (Tabla 41)» | **RESUELTO** | Ahora «Anexo G.3 (Tabla 45); … Anexo G.4». |
| **N-04** | MENOR | `ArchivosComplementarios/` fuera del `git add` | **RESUELTO en lo esencial** | Ya es una mención en el Anexo F, no un enlace; la carpeta está excluida con `.git/info/exclude`. Opcional: añadir «(material de la sesión; no incluido en el repositorio)». |
| **N-05**, **N-06**, **N-07** | ESTILO | Tabla 4 y 5 de S6; «V7» en `instrumento_SUS.md`; comas en el Anexo G | **RESUELTOS** | §6.1 dice «del informe integrador de S6»; `instrumento_SUS.md` dice «Indicador complementario de V6»; Anexo G con comas. |
| **N-08** | ESTILO | Extensión del documento | **ABIERTO (opcional)** | Ver R3-11. |

### E.2 Hallazgos abiertos y nuevos (con corrección exacta)

No hay hallazgos **CRÍTICOS** ni incumplimientos de la guía. Orden: mayor, menor, estilo.

**MAYOR (1)**

| N.º | Ubicación exacta | Problema | Corrección |
| --- | --- | --- | --- |
| **R3-01** | `exportados/semana-09/Entregable_Semana9_Anemia_Junin.pdf` y `.docx` (generados el 17/10/2026 00:54); fila S9 de la tabla «Entregables por semana» del `README.md` raíz | El PDF y el DOCX son de la versión anterior del informe (hito al 50 %; el PDF aún contiene «PLANIFICADA — NO EJECUTADA» en las fichas de RF-08 y RF-09). El `.md` es del 18/10/2026 01:24 y el README remite a esos archivos. Si se entrega el PDF, contradice el informe y no incluye RF-08, RF-09 ni el dataset real. | Tras la última edición del `.md`, ejecutar desde la raíz `python herramientas/conversion/exportar_s9.py` (requiere pandoc y Playwright con Chromium), comprobar que el PDF contiene «v2.0.0-inc2», las Figuras 31 a 46 y no contiene «PLANIFICADA»; confirmar que las fechas de modificación de `.pdf` y `.docx` son posteriores a la del `.md`. |

**MENOR (6)**

| N.º | Ubicación exacta | Problema | Texto actual → texto propuesto |
| --- | --- | --- | --- |
| **R3-02** (antes N-02, H-13) | Anexo C, primer bloque `bash`, líneas `export PY=python GQM_RAIZ_V10=…` y `git archive … \| tar -x -C ../v15_export` | (a) La variable relativa se resuelve desde el directorio de ejecución: tras `cd herramientas/gqm` apunta a `herramientas/inc1_v1.0_PMV`, que no existe (comprobado con `comun.py`: sin variable resuelve a `../inc1_v1.0_PMV` respecto del repositorio y existe). El comentario «relativa a la raíz» es falso. (b) `tar -x -C ../v15_export` falla con «Cannot open: No such file or directory» si la carpeta no existe (comprobado). | **Actual:** `export PY=python GQM_RAIZ_V10=../inc1_v1.0_PMV   # v1.0 se busca por omisión en ../inc1_v1.0_PMV; la ruta debe ser absoluta o relativa a la raíz` → **Nuevo:** `export PY=python   # v1.0 y v1.5 se buscan por omisión en ../inc1_v1.0_PMV y ../v15_export/pmv_fastapi (junto al repositorio); para otra ruta use una ruta ABSOLUTA, p. ej. export GQM_RAIZ_V10="$(cd .. && pwd)/inc1_v1.0_PMV"` y **Actual:** `git archive v1.5.0-inc2-avance pmv_fastapi \| tar -x -C ../v15_export` → **Nuevo:** `mkdir -p ../v15_export && git archive v1.5.0-inc2-avance pmv_fastapi \| tar -x -C ../v15_export` |
| **R3-03** | `README.md` raíz, fila S9 de «Entregables por semana» | Texto de la versión al 50 %: no refleja el Inc. 2 completo ni el procedimiento actual. | **Actual:** `…entrega de valor (con avance del 50 % del Inc. 2)` y `En revisión (T-011); pendiente publicar rama/tag del Inc. 2` → **Nuevo:** `…entrega de valor (Inc. 2 completo `v2.0.0-inc2` y dataset real de la DIRESA Junín)` y `En revisión (T-011); pendiente que el equipo cree el tag `v2.0-Inc2` (Anexo B del entregable)` |
| **R3-04** | `README.md` raíz, párrafo «Datos» (línea 34): «carpeta [`Dataset/`](Dataset/)»; Anexo B del informe | `Dataset/` está sin versionar (`git status`: `??`) y el Anexo B dice que su publicación la decide el equipo («datos de terceros»), mientras el README la llama «dataset público» y la enlaza: tras publicar el enlace da 404 en GitHub. | **Actual:** `dataset público «Niños menores de 36 meses…» (DIRESA Junín, fuente HIS; carpeta [`Dataset/`](Dataset/))` → **Nuevo (si no se versiona):** `dataset «Niños menores de 36 meses…» (DIRESA Junín, fuente HIS; carpeta local `Dataset/`, no versionada: se obtiene de la fuente y se coloca en esa ruta)`; **o bien** añadir `Dataset/` al `git add` del Anexo B y unificar el término («público» o «de terceros») en el README y en el Anexo B. |
| **R3-05** | `README.md` raíz, bloque «Estructura del repositorio» (líneas 38-61) | El árbol omite `pmv_fastapi/` (el software evaluado), `herramientas/` y `Dataset/`, y describe `anemia_junin/` como «software PMV (Python/Flask…)», mientras la sección «Historias de usuario», justo encima, remite a `pmv_fastapi/`. | **Actual:** `├── anemia_junin/                software PMV (Python/Flask, arquitectura hexagonal)` → **Nuevo:** `├── pmv_fastapi/                 software evaluado: PMV e Inc. 2 (FastAPI, arquitectura hexagonal)` + `├── herramientas/                scripts GQM, dataset, conversión y diagramas` + `├── Dataset/                     CSV de la DIRESA Junín (local)` + `├── anemia_junin/                primer prototipo (Flask); histórico` |
| **R3-06** | Informe, Anexo B, bloque «Comandos para publicar el cierre», dos líneas `git push https://Huamani1569@github.com/…` | Inconsistente con el bloque anterior (`git push origin …`) y deja un nombre de usuario personal en el informe. | **Actual:** `git push https://Huamani1569@github.com/woshtsu/ProcesosSoftwareAnemia.git feature/inc2-agenda-alertas` y `… v2.0-Inc2` → **Nuevo:** `git push origin feature/inc2-agenda-alertas` y `git push origin v2.0-Inc2` (si la autenticación exige esa cuenta, configurarla en el remoto con `git remote set-url origin …` fuera del informe). |
| **R3-07** | Informe, §5.0 nota 1; Figuras 7, 8, 21, 22, 25, 28 a 30 y las nuevas 31 a 33 (campos de fecha) | (= H-08) Formato mm/dd/aaaa en los campos de fecha; declarado, no corregido. | Opcional: en `capturar_evidencias.py` fijar `locale="es-PE"` y `timezone_id="America/Lima"`, regenerar y actualizar horas en §5.0, §5.3, Anexo G.1 e `INDICE.md`. |

**ESTILO (4)**

| N.º | Ubicación exacta | Problema | Texto actual → texto propuesto |
| --- | --- | --- | --- |
| **R3-08** | Informe, Tabla 15, fila «Adaptadores Salida», columna «Ruta en Repositorio GitHub» | La ruta indica `…/adapters/outbound/persistence/`, pero la columna de evidencia cita también `reloj_sistema.py` y `reloj_fijo.py`, que están en `…/adapters/outbound/`, fuera de `persistence/`. | **Actual:** `` `pmv_fastapi/app/adapters/outbound/persistence/` `` → **Nuevo:** `` `pmv_fastapi/app/adapters/outbound/` (con `persistence/`, `reloj_sistema.py` y `reloj_fijo.py`) `` |
| **R3-09** | `evidencias_capturas/INDICE.md` | No lista `arquitectura/github_v1.0-PMV_app.png` ni `arquitectura/github_v1.5.0-inc2-avance_app.png` (sí figuran en la Tabla 42 del informe), ni los dos CSV de RF-05. | Añadir dos filas con archivo, URL de GitHub y fecha de captura, o una línea «Capturas manuales de GitHub: ver Figuras 3 y 4 y `resultados_github.json`». |
| **R3-10** | Informe, Anexo F, entrada de la sesión: `` `ArchivosComplementarios/Semana09_S1.pdf` `` | (= N-04) La carpeta no se versiona; quien abra el repositorio no la encuentra. | **Actual:** `(presentación de la sesión; `ArchivosComplementarios/Semana09_S1.pdf`)` → **Nuevo:** `(presentación de la sesión; material del curso, no incluido en el repositorio)` |
| **R3-11** | Documento completo (29 023 palabras; = H-17, N-08, H-19) | El informe creció un 34 % respecto de la ronda anterior (cierre del Inc. 2, dataset real, 55 figuras). Para una exposición de 15 minutos se apoya en el Anexo E; es cuestión de lectura, no de cumplimiento. Las capturas JSON y CSV de RF-05 siguen siendo poco informativas. | Opcional: mover las Tablas 16 y 17 y el detalle de las exploratorias de §5.4 al Anexo G; regenerar las capturas de RF-05 con «Pretty-print» y el CSV abierto en una hoja de cálculo. |

## Parte F. Porcentaje global de cumplimiento

| Bloque | Requisitos | CUMPLE | CUMPLE al publicar | PARCIAL | NO CUMPLE | Cumplimiento ponderado |
| --- | --- | --- | --- | --- | --- | --- |
| A.1 Actividades 1 a 7 | 55 | 55 | 0 | 0 | 0 | 100,0 % |
| A.2 Estructura III y anexos | 12 | 11 | 1 | 0 | 0 | 100,0 % (91,7 % + 8,3 % condicionado) |
| **Subtotal guía (A.1 + A.2)** | **67** | **66** | **1** | **0** | **0** | **100,0 %** |
| B. Aclaraciones del cliente | 6 | 6 | 0 | 0 | 0 | 100,0 % |
| **Total (guía + aclaraciones)** | **73** | **72** | **1** | **0** | **0** | **100,0 %** |

**Cumplimiento global: 100,0 %** con la regla acordada («CUMPLE al publicar» cuenta como CUMPLE, porque el procedimiento y la evidencia están en el documento). **Estricto hoy** (E-12 como 0,5): **99,3 %** (72,5/73). Evolución: primera revisión 95,7 %; segunda pasada 97,1 %; 97,8 % tras publicar el hito; tercera auditoría 100,0 %. El 100 % es de **requisitos de la guía**: los hallazgos R3-01 a R3-11 son de calidad de entrega (uno mayor, de exportación) y no incumplen requisito alguno; R3-01 debe corregirse antes de entregar el PDF.

## Pendientes del equipo antes de la exposición

Acciones que no se pudieron hacer desde el contenedor (sin acceso a GitHub ni permiso para commits o etiquetas) o que dependen de personas.

| N.º | Pendiente | Responsable propuesto (informe) | Fecha | Hallazgo o ítem que cierra |
| --- | --- | --- | --- | --- |
| 1 | **Crear y publicar `v2.0-Inc2`:** revisar `git status`, ejecutar los comandos del bloque «Comandos para publicar el cierre del Incremento 2» del Anexo B (commit, `git tag -a v2.0-Inc2`, push de la rama y de la etiqueta), abrir `tree/v2.0-Inc2/pmv_fastapi/app`, capturarla con la URL visible junto a las Figuras 3 y 4 y cambiar «la publicará» por «publicada» en las Tablas 1 y 15, en §4.1 y en el Anexo B. | Porras V. y Auqui H. | Antes de la exposición | **E-12, H-01, A4-09; criterio 2 de la rúbrica** |
| 2 | Regenerar el PDF y el DOCX con `python herramientas/conversion/exportar_s9.py` **después** de la última edición del informe y revisar imágenes y saltos de página. | Porras V. | Antes de entregar | **R3-01** |
| 3 | Aplicar las correcciones R3-02 a R3-06 y R3-08 a R3-10 (texto exacto en E.2); en particular R3-02 antes de que alguien reproduzca el Anexo C. | Porras V. (integración) | Antes de entregar | R3-02 a R3-10 |
| 4 | Decidir si `Dataset/` se versiona (datos de terceros frente a «dataset público») y alinear el README raíz y el Anexo B. | Equipo | Antes de publicar | R3-04 |
| 5 | Firmar las 9 fichas ejecutadas como QA Lead («firma pendiente» en las Tablas 19 a 27) o dejar constancia de que la ejecución es automatizada. | Huamani R. | Antes de la exposición | A5-06 |
| 6 | Aplicar el instrumento SUS (≥ 5 respondientes por versión: Product Owner y personal de salud) y reportar el valor; hasta entonces el informe lo declara «pendiente». | Porras V. | 30/10/2026 | V6 como proxy (Tabla 34) |
| 7 | Confirmar por escrito con los tres integrantes y el docente el reparto de expositores y responsabilidades (hoy «propuesta del equipo») y ensayar los tres bloques de 5 minutos con el Anexo E. | Equipo | Antes de la exposición | Tablas 2 y 43 |
| 8 | Validar con la microred los parámetros de la agenda (`ESQUEMA_AGENDA_V1`) y el valor con el Product Owner real; mientras tanto el informe lo declara referencial y simulado. | Equipo con el Product Owner | Sprint 4 | Tablas 35 y 46 |
| 9 | Ejecutar las acciones PDCA que atacan las metas no cumplidas: perfilar y corregir la regresión del p95 (V4: 175 → 815 ms), reforzar la exploración de entradas límite en la DoD (M2.2) y planificar recordatorios a la familia (B2) y registro de barreras (B3) para M3.1. | Auqui H. y Huamani R. | Según Tabla 41 | Tabla 41 |
| 10 | Opcional: regenerar las capturas con `locale="es-PE"`, mejorar las de RF-05 y decidir si se acorta el cuerpo del informe. | Huamani R. y Porras V. | Antes de entregar | R3-07, R3-11 |
