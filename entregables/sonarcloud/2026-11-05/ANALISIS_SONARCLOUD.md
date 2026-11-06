# Análisis SonarCloud del repositorio (rama `main`, 05/11/2026)

**Proyecto SonarCloud:** `woshtsu_ProcesosSoftwareAnemia` (organización `woshtsu`, privado).
**Análisis:** 05/11/2026 21:46 (UTC-5), commit `0ef33d07` de `main`. Es el tercero del día; los anteriores fueron sobre `17e44f2f` y `9b71b6ed`.
**Fuente:** exportación completa enviada por un integrante del equipo. Está en la carpeta [`exportacion/`](exportacion/): JSON con la respuesta de la API, informe HTML y libro Excel con 10 hojas.
**Propósito:** documento de referencia para incorporar SonarCloud en las próximas entregas. Separa lo que afecta al software desplegado de lo que no y propone un plan de corrección. **No modifica** el informe S12 ya entregado.

---

## 1. Resumen ejecutivo

| Indicador | Valor | Lectura |
|---|---|---|
| Quality Gate | **Aprobado (OK)** | Solo evalúa el **código nuevo** desde el análisis de las 20:17 (fiabilidad A, seguridad A, mantenibilidad A, 100 % de *hotspots* revisados). No es un juicio sobre todo el repositorio. |
| Hallazgos abiertos | **129** | 56 bugs, 63 vulnerabilidades y 10 *code smells*; 7 bloqueantes, 11 críticos, 108 mayores y 3 menores. |
| Calificación de fiabilidad (código total) | **D** (4.0) | La explican los 54 bugs del frontend (`app.js`). |
| Calificación de seguridad (código total) | **E** (5.0) | La explican vulnerabilidades en **herramientas, scripts y el prototipo anterior**, no en el backend desplegado (sección 2). |
| Mantenibilidad | **A** (deuda 98 min, ratio 0,0 %) | |
| Duplicación | 0,7 % | 578 líneas duplicadas. |
| *Security hotspots* | 0 | |
| Esfuerzo estimado para todos los hallazgos | 2 213 min (≈ 37 h) | Estimación de Sonar; con el plan de la sección 6 se reduce mucho, porque gran parte se resuelve por configuración o justificación. |
| Cobertura | **No reportada** | El análisis automático no recibe `coverage.xml`. La cobertura medida por el CI (99,79 %, S10) no aparece en Sonar. |
| Riesgo de dependencias (SCA) | 1 bajo | `locust 2.46.6` (CVE-2026-111883). Solo está en `requirements-dev.txt` (pruebas de carga): **no** va en la imagen de producción. |

**Conclusión principal:**
- **Backend Python desplegado** (`pmv_fastapi/app/`: dominio, aplicación, puertos y adaptadores): **0 hallazgos**.
- **Frontend desplegado** (`app/web/`): 55 hallazgos de **fiabilidad y accesibilidad**, ninguno de seguridad.
- **Las 63 vulnerabilidades** están en código que **no se despliega**: herramientas de métricas, scripts de evidencias, prototipo Flask anterior, CI y Docker.
- **Criterio de la plantilla S12** («0 vulnerabilidades y 0 deudas técnicas críticas»): se cumple para el backend desplegado, pero **no para el repositorio completo**. En las próximas entregas debe decirse así, sin redondear.

---

## 2. Dónde están los hallazgos

| Área | Hallazgos | Bugs | Vulnerab. | *Smells* | Bloq. | Crít. | ¿Se despliega? |
|---|---:|---:|---:|---:|---:|---:|---|
| Frontend PWA (`pmv_fastapi/app/web/`) | 55 | 54 | 0 | 1 | 0 | 6 | **Sí** |
| Backend (`pmv_fastapi/app/**/*.py`) | **0** | 0 | 0 | 0 | 0 | 0 | **Sí** |
| Docker, compose y scripts (`pmv_fastapi/`) | 9 | 0 | 9 | 0 | 1 | 0 | Parcial (Dockerfile) |
| CI (`.github/workflows/ci.yml`) | 6 | 0 | 6 | 0 | 0 | 0 | No (pipeline) |
| Herramientas GQM y conversión (`herramientas/`) | 34 | 2 | 28 | 4 | 3 | 1 | No |
| Scripts de evidencias (`entregables/*/metricas/`) | 12 | 0 | 9 | 3 | 1 | 2 | No |
| Prototipo Flask anterior (`anemia_junin/`) | 12 | 0 | 10 | 2 | 2 | 2 | No (archivado) |
| Diagramas (`diagramas/src/`) | 1 | 0 | 1 | 0 | 0 | 0 | No |
| **Total** | **129** | **56** | **63** | **10** | **7** | **11** | |

El alcance del análisis también lo distorsiona: son 390 archivos y 75 953 líneas, de las cuales **39 611 (52 %) son JSON de evidencias** y solo 27 596 son Python.

---

## 3. Revisión de los 18 hallazgos bloqueantes y críticos

Revisados contra el fragmento de código que trae la exportación.
Veredictos:
- **Real:** hay que corregirlo.
- **Real-bajo:** es correcto, pero de impacto mínimo.
- **Aceptable:** contexto de prueba o local, a justificar en Sonar.
- **Legado:** está en el prototipo archivado.

| # | Sev. | Regla | Ubicación | Veredicto | Acción |
|---|---|---|---|---|---|
| 1 | Bloq. | `secrets:S6698` contraseña PostgreSQL | `pmv_fastapi/docker-compose.yml:19` | Real-bajo | El valor por defecto es el marcador `cambiar_en_staging`, no un secreto real. Aun así, conviene exigir la variable: `${POSTGRES_PASSWORD:?defina POSTGRES_PASSWORD}`. |
| 2–4 | Bloq. | `pythonsecurity:S2083` *path traversal* | `herramientas/gqm/comun.py:190`; `herramientas/conversion/exportar_s9.py:70, 84` | Aceptable | Scripts locales sin entrada externa. Validar que la ruta resuelta quede dentro del repositorio (`Path.resolve().is_relative_to(raiz)`). |
| 5 | Bloq. | `python:S2115` BD sin contraseña | `entregables/semana-10/metricas/caos_postgres.py:32` | Aceptable | Contenedor efímero del experimento de caos (S10). Tomar la clave de una variable de entorno. |
| 6 | Bloq. | `pythonsecurity:S3649` inyección SQL | `anemia_junin/.../sqlite/migraciones.py:69` | Legado | El SQL viene de archivos de migración del propio repositorio. Excluir el prototipo del análisis (sección 5). |
| 7 | Bloq. | `python:S3516` retorno invariante | `anemia_junin/.../unidad_de_trabajo.py:84` | Legado | Igual que el 6. |
| 8–11 | Crít. | `javascript:S930` argumento de más | `app/web/app.js:311, 312, 397, 398` | **Real-bajo** | `cargarBarrerasNino(ref)` recibe un segundo argumento (`nombre`) que ignora. No falla, pero está mal escrito: quitar el argumento. |
| 12–13 | Crít. | `javascript:S2871` `sort()` sin comparador | `app/web/app.js:624, 805` | **Real** | Los filtros de comunidad y establecimiento ordenan por código UTF-16: los nombres que empiezan con Á, É, Ñ… quedan después de la Z. Usar `.sort((a, b) => a.localeCompare(b, "es"))`. |
| 14–16 | Crít. | `python:S5443` directorio temporal público | `herramientas/gqm/ejecutar_carga.py:44`; `entregables/semana-10/metricas/caos_postgres.py:30`, `accesibilidad.py:25` | Aceptable | Herramientas locales. Usar `tempfile.mkdtemp()`. |
| 17 | Crít. | `python:S4502` CSRF desactivado | `anemia_junin/src/anemia_junin/bootstrap.py:122` | Legado | El sistema vigente (`pmv_fastapi`) sí exige la cabecera anti-CSRF (S10, OWASP A01). |
| 18 | Crít. | `python:S6890` `pytz` | `anemia_junin/.../consultar_reporte.py:7` | Legado | — |

---

## 4. Hallazgos mayores más frecuentes

| Regla | Cant. | Dónde | Veredicto y acción |
|---|---:|---|---|
| `javascript:S9383` promesas sin manejar | 44 | `app.js` (43), `sw.js` (1) | **Real (robustez).** Hay funciones `async` llamadas sin `await` ni `.catch` (`cargarVisitasNino`, `abrirExpediente`, `actualizarInsignia`…). Si una falla fuera de su `try`, el error no se muestra. Agregar un manejador común: `cargarX().catch(mostrarError)`. En `sw.js:38`, `cache.put(...)` dentro de `event.waitUntil` o con `.catch`. |
| `pythonsecurity:S8703/S8705/S8706/S8707` («flujos agénticos»: inyección de ruta, argumentos, conexión, SSRF) | 29 | `herramientas/gqm/*`, `entregables/semana-10/metricas/*` | **Mayormente falsos positivos para este uso.** Son scripts de línea de comandos que reciben URL, rutas y conexiones del propio equipo. Marcar como «Seguro» con justificación, o excluir esas carpetas. |
| `python:S2245` generador pseudoaleatorio | 10 | Datos sintéticos y `locust` | **Falso positivo.** `random` genera datos de prueba, no secretos. |
| `Web:InputWithoutLabelCheck` campo sin etiqueta | 4 | `index.html:129, 130, 137, 156` (buscadores y filtros) | **Real (accesibilidad).** Solo tienen `placeholder`. Axe lo acepta como nombre accesible y por eso S10 dio 0 violaciones, pero WCAG 3.3.2 recomienda etiqueta. Agregar `aria-label` o `<label class="sr-only">`. |
| `githubactions/docker:S8541`, `S8544` | 5 | `ci.yml:47, 104`; `Dockerfile:5` | Real-bajo (cadena de suministro). Fijar versiones con hashes (`pip install --require-hashes`) cuando haya archivo de bloqueo. |
| `githubactions:S7637` acción sin SHA | 1 | `ci.yml:80` (`sonarqube-scan-action@v5`) | **Real, fácil.** Fijar el SHA del commit de la acción. |
| `yaml:S2068` / `python:S2068` credenciales en código | 4 | `ci.yml:33, 58` (`postgres/postgres` del servicio efímero); `seguridad_http.py:91, 153` (contraseñas de prueba) | Aceptable: son valores de prueba, no de producción. Justificar en Sonar. |
| `Web:S6850` encabezado vacío | 1 | `index.html:308` (`<h2 id="modal-titulo">`) | Real-bajo. Se llena por JS; dejar un texto por defecto. |
| `text:S8565` sin archivo de bloqueo | 1 | Raíz | Real-bajo. Igual que S8541/S8544. |

---

## 5. Configuración: el análisis no es el del CI

| Situación encontrada | Consecuencia | Recomendación |
|---|---|---|
| El proyecto en SonarCloud usa el **análisis automático** sobre **todo el repositorio**. | Entran el prototipo archivado, las herramientas y 39 611 líneas de JSON de evidencias, que bajan las calificaciones. | Pasar al análisis desde CI: en SonarCloud, *Administration → Analysis Method*, **desactivar Automatic Analysis**. Sonar no permite usar ambos a la vez. |
| `pmv_fastapi/sonar-project.properties` tiene `sonar.projectKey=anemia-junin-pmv` y `sonar.organization=REEMPLAZAR_ORGANIZACION`. | El paso «Análisis SonarCloud» del CI apunta a un proyecto que no existe. Solo se ejecuta si el *secret* `SONAR_TOKEN` está definido. | Cambiar a `sonar.projectKey=woshtsu_ProcesosSoftwareAnemia` y `sonar.organization=woshtsu`, y crear el *secret* `SONAR_TOKEN` en GitHub. |
| El mismo archivo tiene `sonar.exclusions=app/web/**`. | Al pasar al CI se **dejaría de analizar el frontend**, que es justo donde están los 55 hallazgos del código desplegado. | **Quitar** esa exclusión. |
| El CI ya genera `coverage.xml` (`pytest --cov=app --cov-report=xml`) y lo guarda como artefacto. | Con el análisis automático la cobertura no llega a Sonar. | Con el análisis por CI la cobertura aparece sola (`sonar.python.coverage.reportPaths=coverage.xml`). |

Con `projectBaseDir: pmv_fastapi` y `sonar.sources=app`, el análisis cubriría solo el software que se despliega. Eso es lo que piden las guías S10 y S12.

---

## 6. Plan de corrección priorizado (para la próxima entrega)

| Prioridad | Acción | Hallazgos que cierra | Esfuerzo |
|---|---|---:|---|
| P1 | Quitar el argumento de más en las 4 llamadas a `cargarBarrerasNino`; usar `localeCompare("es")` en los 2 `sort()`; `aria-label` en 4 campos y texto por defecto en `#modal-titulo`. | 11 (6 críticos) | ≤ 1 h |
| P1 | Exigir `POSTGRES_PASSWORD` en `docker-compose.yml`; fijar el SHA de `sonarqube-scan-action`. | 2 (1 bloqueante) | 15 min |
| P2 | Manejar las promesas en `app.js` y `sw.js` con un `.catch` común que muestre el error en la interfaz. | 44 | 2–3 h |
| P3 | Corregir la configuración de Sonar (sección 5) y volver a analizar desde CI. | Saca del alcance los 74 hallazgos fuera de `pmv_fastapi/app` (herramientas, evidencias, prototipo, diagramas, CI y Docker) | 30 min |
| P4 | Aunque queden fuera del análisis, revisar a mano Dockerfile, compose y CI (sección 4), y justificar en Sonar los falsos positivos y valores de prueba que sigan visibles («Seguro» / «No se corregirá», con comentario). | Resto | 30 min |
| P4 | Archivo de bloqueo con hashes para `pip` (CI y Dockerfile). | 3–4 | 1–2 h |

**Meta verificable:** después de P1 a P3, nuevo análisis de `main` con **0 vulnerabilidades, 0 bloqueantes y 0 críticos** en el alcance desplegado, calificaciones A y cobertura visible en Sonar. Así se cumple el criterio de la plantilla S12 con evidencia.

> Estas correcciones tocan código de producción. Deben hacerse en una rama `fix/sonarcloud-*` con PR, CI en verde y revisión del QA Lead, como el resto del proyecto.

---

## 7. Cómo usarlo en las próximas entregas

- **Atributo S y «+» (seguridad) de FURPS+, como en S10:** citar la tabla de la sección 2. El backend desplegado tiene 0 hallazgos; las vulnerabilidades del repositorio están fuera del código desplegado; el frontend tiene 55 hallazgos de fiabilidad y accesibilidad.
- **CMMI, áreas PQA y VER (S11):** el análisis estático continuo es evidencia de aseguramiento de calidad. La brecha de la sección 5 (configuración) es un hallazgo de proceso con acción correctiva.
- **Criterio «0 vulnerabilidades» (S12):** declararlo como **parcialmente cumplido**, con el plan de la sección 6 y, cuando se ejecute, la captura del nuevo análisis.
- **Evidencias sugeridas para capturar en SonarCloud:**
  - pantalla *Overview* de `main` con el Quality Gate;
  - pestaña *Issues* filtrada por `pmv_fastapi/app`;
  - historial (*Activity*) antes y después de las correcciones.

**Texto sugerido para «Limitaciones»:**

> El análisis SonarCloud del 05/11/2026 (commit `0ef33d07`) aprobó el Quality Gate del código nuevo y no reporta hallazgos en el backend desplegado. Sobre el repositorio completo registra 129 hallazgos: 63 vulnerabilidades, todas en herramientas, scripts de evidencias, CI y el prototipo anterior, y 55 hallazgos de fiabilidad y accesibilidad en el frontend. El análisis automático incluye código que no se despliega y no recibe la cobertura del CI. Se planificó migrar al análisis desde CI y corregir los hallazgos del frontend.

---

## 8. Archivos

| Archivo | Contenido |
|---|---|
| [`exportacion/sonarcloud_informe.html`](exportacion/sonarcloud_informe.html) | Informe navegable (abrir en el navegador). |
| [`exportacion/sonarcloud_hallazgos.xlsx`](exportacion/sonarcloud_hallazgos.xlsx) | Hojas: Resumen, Hallazgos, Reglas, Guía de reglas, Código, Dependencias, Ubicaciones, Métricas, Análisis y Alcance. |
| [`exportacion/sonarcloud_completo.json`](exportacion/sonarcloud_completo.json) | Respuesta íntegra de la API (129 hallazgos, reglas, contexto de código, métricas, Quality Gate y SCA). Sin tokens ni credenciales: se revisó antes de versionarla. |

**Limitaciones de la exportación** (declaradas por la propia herramienta):
- No incluye hallazgos de otras ramas ni de PR.
- No incluye hallazgos borrados por la retención de Sonar.
- Los fragmentos de código corresponden a la versión analizada de `main`.
