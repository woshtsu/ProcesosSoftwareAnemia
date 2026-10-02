# Pasos manuales S6: lo que solo una persona puede hacer

- **Elaborado por:** inspector-guia (S6-06), 2026-10-01. **Versión 2** (reinspección sobre el commit `fdc50c5`): el trabajo ya está confirmado en git; los PDF y el DOCX existen de forma provisional; la ilegibilidad de las figuras en las diapositivas (N-01 de `INSPECCION_S6.md`) la corrigen los agentes, no las personas. Actualizar tras cada nueva inspección.
- **Raíz del repositorio (variable usada en los comandos):** `D:\Workspace\IngenieriaWeb\Grupal\semana6\ProcesosSoftwareAnemia`.
- **Shell:** los comandos están en PowerShell (Windows 11). Abre PowerShell y ejecuta primero:

```powershell
$R = "D:\Workspace\IngenieriaWeb\Grupal\semana6\ProcesosSoftwareAnemia"
Set-Location $R
git branch --show-current          # debe imprimir: feature/s6-integrador-final
```

- **Convención:** `[COMPLETAR…]` es el marcador que hay que reemplazar. Para ubicarlo: `Select-String -Path "$R\entregables\semana-06-integrador\Informe_Integrador_Anemia_Junin.md" -Pattern "COMPLETAR"` (17 líneas hoy; la misma cantidad aparece en el PDF y el DOCX provisionales).
- **Orden recomendado:** 1 → 2 → 5 → 6 (datos) en un solo rato; 3 (push) antes de 7; 8 → 9 → 11 (Docker y E2E); 10; después las correcciones automáticas de `INSPECCION_S6.md` §4; luego 12 y 13; 14 a 16 al final; 17 y 18 antes de la exposición.
- **Regla:** no se inventa ningún dato. Si un dato no existe, se declara su ausencia (cada paso indica cómo).

## Índice

| N.° | Paso | Responsable sugerido | Tiempo | Requisitos |
| --- | --- | --- | --- | --- |
| 1 | Datos de portada: códigos, docente y fecha | Los tres | 10 min | R-08, R-09 |
| 2 | Confirmar el mapeo de roles | Los tres | 10 min | R-08 |
| 3 | Commit, push y captura de GitHub Actions en verde | Tania Auqui | 30-60 min | R-78, R-21, R-86 |
| 4 | Horas reales por integrante y sprint | Ricardo Porras | 20 min | R-82 |
| 5 | Acta de aceptación y Product Owner | Ricardo Porras | 1 a 3 días (coordinación) | R-20, R-21, R-34, R-63 |
| 6 | Confirmar la justificación del cambio Flask → FastAPI | Los tres | 15 min | R-26, R-37 |
| 7 | Activar SonarCloud (o decidir no usarlo) | Jean Piero Huamani | 30 min | R-32 |
| 8 | Instalar Docker Desktop y levantar el staging | Tania Auqui | 45 min | R-33, R-62, R-86 |
| 9 | Captura de `/api/salud` y de la aplicación en staging | Tania Auqui | 10 min | R-33, R-86 |
| 10 | Duración y enlace del video de demostración | Tania Auqui | 15 min | R-34, R-60, R-91 |
| 11 | Instalar Chromium de Playwright y ejecutar las E2E | Jean Piero Huamani | 20 min | R-31 |
| 12 | Generar el PDF de las diapositivas | Ricardo Porras | 15 min | R-02 |
| 13 | Exportar el informe a PDF y verificar marcadores | Ricardo Porras | 30 min | R-01 |
| 14 | Decidir si el tag `v1.0-PMV` se mueve o se agrega otro | Los tres (decisión) | 10 min | R-80 |
| 15 | Subir los entregables al aula virtual | Ricardo Porras | 15 min | R-01 a R-03 |
| 16 | Pull request y merge a `main` | Quien tenga permisos de merge | 15 min | R-78, R-80 |
| 17 | Ensayo cronometrado de 7 minutos | Los tres | 1 h | R-04, R-90, R-87 |
| 18 | Preparar la defensa individual (5 min por persona) | Los tres | 1,5 h | R-88 |

---

## 1. Datos de portada: códigos de alumno, docente y fecha

- **Archivo y sección:** `entregables\semana-06-integrador\Informe_Integrador_Anemia_Junin.md`, portada: l.10 (fecha), l.11 (docente), l.20-22 (códigos).
- **Pasos:**
  1. Reúne los tres códigos de alumno (del carné o del aula virtual) y el nombre completo del docente tal como figura en el aula virtual.
  2. Decide la fecha de entrega con el formato `DD/MM/AAAA` (la que fije el aula virtual, no la de redacción).
  3. Abre el archivo en un editor y reemplaza:
     - l.10: `[COMPLETAR: fecha de entrega en formato DD/MM/AAAA]` por, por ejemplo, `05/10/2026` (usa la fecha real).
     - l.11: `[COMPLETAR: apellidos y nombres del docente de la asignatura]` por `Apellidos, Nombres`.
     - l.20, l.21, l.22: cada `[COMPLETAR: código de alumno]` por el código de la persona de esa fila (Porras, Auqui, Huamani).
  4. Guarda el archivo.
- **Verificación:**

```powershell
Select-String -Path "$R\entregables\semana-06-integrador\Informe_Integrador_Anemia_Junin.md" -Pattern "COMPLETAR" | Where-Object { $_.LineNumber -le 25 }
# No debe imprimir nada para las líneas 10, 11, 20, 21 y 22
```

## 2. Confirmar el mapeo de los 4 roles de la plantilla a 3 personas

- **Archivo y sección:** mismo informe, l.35 y Tabla 2 (l.28-33). Además `README.md` l.23 (dice «Ingeniera» mientras el informe l.21 dice «Ingeniero»).
- **Pasos:**
  1. Lean la Tabla 2 en equipo. Confirmen que Porras cubre Leader y Process (con Auqui como arquitecta y Huamani como QA) y que Auqui cubre Backend y Frontend.
  2. Si algo no es así, corrijan las celdas de la Tabla 2 y la Tabla 11 (RAE) para que no se contradigan.
  3. Borren la línea 35 completa: `[COMPLETAR: el equipo debe confirmar o corregir este mapeo de roles antes de exportar el informe.]`
  4. Unifiquen el género del rol «Ingeniero/a de Desarrollo y Prototipado» en el informe l.21, en `README.md` l.23 y en `GUION_EXPOSICION.md` (tabla §1).
- **Verificación:** `Select-String -Path "$R\entregables\semana-06-integrador\Informe_Integrador_Anemia_Junin.md" -Pattern "mapeo de roles"` no debe devolver la línea de `[COMPLETAR]`.

## 3. Commit, push y captura de GitHub Actions en verde

- **Por qué:** el commit local `fdc50c5` ya incluye `.github/workflows/ci.yml` (raíz) y los entregables S6, pero la rama no está empujada; hasta que corra en GitHub no hay evidencia de CI en verde (DATOS C-02). **Estado v2:** el commit está hecho; falta el push (sub-pasos 5 a 9).
- **Pasos:**
  1. Revisa lo que se va a confirmar:

```powershell
git -C $R status --short
```

  2. En v2 el árbol debe estar limpio (`git status --short` sin salida). Solo habrá cambios si los agentes o ustedes editaron algo después de `fdc50c5`.
  3. Espera a que los agentes terminen las correcciones N-01 a N-06 y N-09 de `INSPECCION_S6.md` §3 (opcional: puedes empujar antes solo para obtener el CI en verde, y de nuevo después).
  4. Si hay cambios posteriores a `fdc50c5`, crea un commit nuevo (lo hace el `sincronizador` si está disponible; si lo haces tú):

```powershell
git -C $R add .github coordinacion entregables exportados diagramas pmv_fastapi README.md
git -C $R commit -m "S6: informe integrador, presentación, figuras y CI en la raíz"
```

  5. Empuja la rama (solo la persona con acceso de escritura al repositorio `woshtsu/ProcesosSoftwareAnemia`):

```powershell
git -C $R push -u origin feature/s6-integrador-final
```

  6. En el navegador: `https://github.com/woshtsu/ProcesosSoftwareAnemia/actions` → workflow **CI — PMV Anemia Junín** → abre la última ejecución de la rama `feature/s6-integrador-final`.
  7. Espera el check verde en el job `calidad-y-pruebas`. Si falla, abre el paso rojo, copia el error y repórtalo a `desarrollador` (DEV-###).
  8. Toma la captura de la página de la ejecución (con la fecha, la rama y los pasos en verde). Guárdala como `pmv_fastapi\docs\evidencias\capturas\09_ci_github_actions_verde.png`.
  9. Copia el enlace de la ejecución (barra de direcciones).
- **Dónde pegar el resultado:**
  - Informe l.277 (Tabla 12, fila Integración): reemplaza `[COMPLETAR: captura o enlace de una ejecución en verde en GitHub Actions]` por el enlace.
  - Informe l.583: reemplaza el `[COMPLETAR: captura o enlace de la ejecución en verde en Actions tras el push…]` por el enlace y, si quieres, una figura `![Figura 34. Ejecución en verde de GitHub Actions](../../pmv_fastapi/docs/evidencias/capturas/09_ci_github_actions_verde.png)` (renumera las figuras siguientes o ponla como «Figura 33b»).
  - Informe Tabla 18 (l.382), fila del pipeline: cambia «falta evidencia de una ejecución en verde» por «verificado: ejecución en verde del DD/MM/2026».
- **Verificación:** la página de Actions muestra un círculo verde; `git -C $R ls-remote --heads origin feature/s6-integrador-final` devuelve un hash.

## 4. Horas reales por integrante y sprint

- **Archivo y sección:** informe l.323 (§2.3, tras la Tabla 14) y Tabla 18 (l.384, fila «Horas reales no registradas»).
- **Pasos:**
  1. Cada integrante estima honestamente sus horas reales en cada sprint (revisando commits, reuniones y el calendario). Si no pueden reconstruirlas con confianza, **no se inventan**.
  2. Si hay datos, agrega bajo la Tabla 14 una tabla `Integrante | Sprint 1 (h) | Sprint 2 (h) | Total` y una línea «Fuente: declaración de los integrantes, estimada a partir de commits y reuniones».
  3. Si no hay datos, reemplaza el `[COMPLETAR: horas reales …]` de l.323 por: «Las horas reales no se registraron durante el Incremento 1; el indicador de desviación de esfuerzo (Tabla 17) no es calculable y queda como mejora para el INC-2.»
- **Verificación:** `Select-String … -Pattern "horas reales"` ya no encuentra un `[COMPLETAR` en esa línea.

## 5. Acta de aceptación del usuario final y Product Owner

- **Dónde afecta:** informe l.242 (acta de revisión), l.263 (nombre y cargo del Product Owner), l.280 (Tabla 12, revisión del sprint), l.617 (aceptación del usuario) y la diapositiva 5 (`Presentacion_Integrador.md` l.122 con el texto visible «pendiente de acta (ver anexo)», y las notas l.126 y l.133). En v2 el texto visible ya no tiene `[COMPLETAR]`, pero remite a un anexo que no existe: si no hay acta, el agente lo cambia (N-03); si la hay, se guarda en `anexos\`.
- **Opción A (hay aceptación):**
  1. Haz una demostración corta del PMV (puede ser con el video o en vivo) a una persona designada: enfermera o técnica de una posta, la microred o un Product Owner del curso.
  2. Pídele que verifique los criterios Dado-Cuando-Entonces de HU-01 a HU-05 (están en `pmv_fastapi\README.md`).
  3. Redacta el acta de una página: fecha, nombre, cargo, historias revisadas, observaciones y firma o correo de conformidad. Guarda el PDF en `entregables\semana-06-integrador\anexos\Acta_aceptacion_INC1.pdf` (nombre sugerido).
  4. En el informe: reemplaza los cuatro `[COMPLETAR]` por el nombre, cargo y fecha, y cita el anexo. En la diapositiva 5 reemplaza `Aceptación del usuario: pendiente de acta (ver anexo)` por `Aceptación: <nombre>, <fecha> (acta en anexo)`.
- **Opción B (no hay aceptación; es lo más probable):**
  1. Reemplaza l.617 por: «Aceptación del usuario final: pendiente. El incremento se declara verificado técnicamente (pruebas automatizadas, cobertura y demostración con datos sintéticos).»
  2. Reemplaza l.242 y l.280 por «Revisión de sprint con el equipo; la aceptación externa queda pendiente» y l.263 por «Product Owner: rol previsto, sin designar en el Incremento 1».
  3. En la diapositiva 5 el texto visible debe decir `Aceptación del usuario: pendiente (verificado técnicamente)` (pedírselo a `disenador-diapositivas`, N-03).
- **Verificación:** `Select-String -Path "$R\entregables\semana-06-integrador\*.md","$R\entregables\semana-06-integrador\presentacion\*.md" -Pattern "COMPLETAR"` no muestra las líneas de acta ni del PO.

## 6. Confirmar la justificación del cambio de Flask a FastAPI

- **Archivo y sección:** informe l.424 (§3.1) y l.651 (§5, lección 3). Fuente de la propuesta: DATOS §16.
- **Pasos:**
  1. Lean la justificación propuesta: integridad con PostgreSQL, contrato OpenAPI nativo y despliegue en contenedores con CI.
  2. Si es cierta, borren las frases `[COMPLETAR: el equipo debe confirmar …]` de l.424 y l.651.
  3. Si el motivo real fue otro (por ejemplo, requisito del curso o de la guía S5), reescriban la frase con el motivo verdadero.
- **Verificación:** no quedan `[COMPLETAR` en l.424 ni l.651.

## 7. Activar SonarCloud (o decidir no usarlo)

- **Archivos:** `pmv_fastapi\sonar-project.properties` l.2 (`sonar.organization=REEMPLAZAR_ORGANIZACION`), `.github\workflows\ci.yml` (paso «Análisis SonarCloud») e informe l.551.
- **Opción A: activarlo.**
  1. Entra a `https://sonarcloud.io` e inicia sesión con tu cuenta de GitHub (acción de la persona; no se delega).
  2. Crea o elige una organización (por ejemplo, tu usuario de GitHub) e **importa** el repositorio `woshtsu/ProcesosSoftwareAnemia`.
  3. En *Administration* → *Analysis Method* desactiva «Automatic Analysis» (se usa el CI).
  4. Anota la **clave de la organización** (Organization key) y genera un token en *My Account* → *Security* → *Generate Token*.
  5. En GitHub: repositorio → *Settings* → *Secrets and variables* → *Actions*.
     - Pestaña *Secrets* → *New repository secret*: nombre `SONAR_TOKEN`, valor = el token.
     - Pestaña *Variables* → *New repository variable*: nombre `SONAR_ORGANIZATION`, valor = la clave de la organización.
  6. Edita `pmv_fastapi\sonar-project.properties` l.2: `sonar.organization=<clave de la organización>` (el mismo valor).
  7. Haz commit y push (paso 3). En Actions, el paso «Análisis SonarCloud» ya no se omite.
  8. Cuando termine, en SonarCloud abre el proyecto `anemia-junin-pmv` y captura el *Quality Gate* y las métricas. Guárdala como `pmv_fastapi\docs\evidencias\capturas\10_sonarcloud_quality_gate.png`.
  9. En el informe l.551 reemplaza el `[COMPLETAR: crear o seleccionar la organización …]` por el resultado (estado del Quality Gate, bugs, vulnerabilidades, cobertura) con la captura, y ajusta Tabla 18 (l.383) a «Cerrado».
- **Opción B: no usarlo.** Elimina el `[COMPLETAR…]` de l.551 y deja «SonarCloud queda preparado y no se activa en el Incremento 1; el análisis estático obligatorio es Ruff (0 hallazgos)». Retira el paso de SonarCloud de la lista de entregables del discurso (la diapositiva 4 ya dice «Ruff 0»).
- **Verificación:** captura del Quality Gate o declaración B; `Select-String … -Pattern "REEMPLAZAR_ORGANIZACION"` solo debe aparecer si se eligió B.

## 8. Instalar Docker Desktop y levantar el staging

- **Prerrequisitos:** Windows 11 con virtualización activada en la BIOS y WSL 2. La instalación requiere permisos de administrador y probablemente reiniciar.
- **Pasos:**
  1. Descarga Docker Desktop desde `https://www.docker.com/products/docker-desktop/` (o ejecuta `winget install -e --id Docker.DockerDesktop` en un PowerShell con permisos de administrador) y completa el instalador. Acepta el uso de WSL 2 si lo pide.
  2. Reinicia si el instalador lo solicita. Abre *Docker Desktop* y espera el estado «Engine running».
  3. Verifica en PowerShell:

```powershell
docker --version
docker compose version
```

  4. Levanta el staging (desde `pmv_fastapi`; la contraseña es un valor de prueba, no uses una real):

```powershell
Set-Location "$R\pmv_fastapi"
$env:POSTGRES_PASSWORD = "clave_staging_local"
docker compose up -d --build
docker compose ps
```

  5. Espera a que `db` esté `healthy` y `api` `running` (1 a 3 minutos la primera vez).
  6. Carga los datos sintéticos:

```powershell
docker compose exec api python -m scripts.cargar_datos_prueba
```

  7. Abre `http://localhost:8000` y `http://localhost:8000/docs` en el navegador.
  8. Al terminar la demostración: `docker compose down` (`-v` borra el volumen de datos).
- **Verificación:** `docker compose ps` muestra `api` y `db` en estado `Up`/`healthy`; `Invoke-RestMethod http://localhost:8000/api/salud` devuelve `estado = ok`.
- **Si falla:** `docker compose logs api` y `docker compose logs db`; reporta a `desarrollador`.

## 9. Captura de `/api/salud` y de la aplicación en staging

- **Pasos:**
  1. Con el staging arriba (paso 8), abre `http://localhost:8000/api/salud` en el navegador; debe mostrar `{"estado":"ok"}`.
  2. Captura la pantalla incluyendo la URL y guarda como `pmv_fastapi\docs\evidencias\capturas\11_staging_api_salud.png`.
  3. Captura también `docker compose ps` en la terminal como `12_staging_compose_ps.png`.
- **Dónde pegar:** informe l.583: reemplaza `[COMPLETAR: staging con docker compose up -d --build y captura de GET /api/salud…]` por una frase «Staging verificado el DD/MM/2026: `GET /api/salud` responde 200» y agrega las dos figuras. Diapositiva 5: la línea «Staging: Docker Compose (API + PostgreSQL 16) + CI» ya es correcta; cambia en las notas «Preferible en vivo» por el estado real.
- **Verificación:** los dos PNG existen y el `[COMPLETAR]` de l.583 desapareció.

## 10. Duración y enlace del video de demostración

- **Archivo:** `pmv_fastapi\docs\evidencias\demo_pmv.mp4` (1 640 388 bytes). La consigna pide un video corto o demo en vivo de 2 minutos.
- **Pasos:**
  1. Abre el video en un reproductor y anota la duración exacta (`mm:ss`). O en PowerShell:

```powershell
$f = Get-Item "$R\pmv_fastapi\docs\evidencias\demo_pmv.mp4"; $f.Length
(New-Object -ComObject Shell.Application).NameSpace($f.DirectoryName).GetDetailsOf((New-Object -ComObject Shell.Application).NameSpace($f.DirectoryName).ParseName($f.Name), 27)
```

  2. Si dura más de 2 minutos, recórtalo o regrábalo: `Set-Location "$R\pmv_fastapi"; .\.venv\Scripts\python -m scripts.grabar_demo` (requiere la app levantada y Chromium de Playwright; ver pasos 8 y 11).
  3. Si el aula virtual exige un enlace, sube el archivo a una carpeta compartida (Drive o OneDrive) con permiso «cualquiera con el enlace puede ver» y copia el enlace.
  4. Reemplaza en el informe l.615 `[COMPLETAR: duración del video …]` por «Duración: mm:ss. Enlace: <URL>» y en la diapositiva 5 (notas l.125 y guion l.50) `[COMPLETAR]` por la duración.
  5. Comprueba que el video muestra HU-01 a HU-03 como mínimo y el reporte (HU-05).
- **Verificación:** `Select-String … -Pattern "duración del video"` sin resultados; el video abre en otro equipo.

## 11. Instalar Chromium de Playwright y ejecutar las E2E

- **Por qué:** el 01/10 las 4 E2E no se ejecutaron (falta `chromium_headless_shell-1194`). Hoy la cifra «77/77» está declarada, no reproducida (DATOS §17).
- **Pasos:**

```powershell
Set-Location "$R\pmv_fastapi"
.\.venv\Scripts\python -m playwright install chromium     # descarga unos 150 MB
.\.venv\Scripts\python -m pytest tests/e2e -m e2e --no-cov -v
.\.venv\Scripts\python -m pytest --cov=app                 # suite por defecto: 73 pruebas
```

- **Resultado esperado:** `4 passed` en E2E y `73 passed` con cobertura de aproximadamente 99 %.
- **Dónde dejar la evidencia:** guarda la salida en `pmv_fastapi\docs\evidencias\e2e_2026-10-XX.txt` (`... | Tee-Object`) y actualiza `verificacion_s6_2026-10-01.md` (o pide a `desarrollador` que lo haga). Después, en el informe Tabla 24 (l.511-513) cambia «según el tag» por «reproducido el DD/10/2026: 4 de 4» y ajusta l.515 y DATOS §17 (marca [D] → [V]). Entonces la afirmación «77/77 en verde» es reproducida y las figuras 59, 62 y 64 pueden mostrarla.
- **Verificación:** `4 passed`. Si fallan, no cambies las cifras: repórtalo a `desarrollador`.

## 12. Generar el PDF de las diapositivas

- **Estado v2:** el PDF ya existe (`exportados\semana-06\Presentacion_Integrador_Anemia_Junin.pdf`, 7 páginas, exportado con PowerPoint). Es provisional: debe regenerarse cuando los agentes corrijan la legibilidad de las figuras (N-01) y los textos (N-03, N-04, N-09). Hacerlo una sola vez, al final.

- **Archivo origen:** `exportados\semana-06\Presentacion_Integrador_Anemia_Junin.pptx` (7 diapositivas). Hazlo **después** de que `disenador-diapositivas` regenere el PPTX con las figuras corregidas.
- **Pasos (opción PowerPoint, la más simple):**
  1. Abre el PPTX en PowerPoint.
  2. Revisa a pantalla completa (F5) cada diapositiva: texto legible, figuras sin cortes, sin banner amarillo y sin glifos vacíos.
  3. *Archivo* → *Exportar* → *Crear documento PDF/XPS* → Opciones: «Diapositivas» (no «Documento»). Nombre: `Presentacion_Integrador_Anemia_Junin.pdf`. Carpeta: `D:\Workspace\IngenieriaWeb\Grupal\semana6\ProcesosSoftwareAnemia\exportados\semana-06\`.
  4. (Opción LibreOffice si lo tienes) `soffice --headless --convert-to pdf --outdir "$R\exportados\semana-06" "$R\exportados\semana-06\Presentacion_Integrador_Anemia_Junin.pptx"`.
  5. Nombre unificado: `Presentacion_Integrador_Anemia_Junin.pptx` y `.pdf` (PROTOCOLO_S6 y RUTAS ya lo reflejan).
- **Verificación:** el PDF tiene exactamente 7 páginas: `herramientas\.venv\Scripts\python -c "import pypdf; print(len(pypdf.PdfReader(r'D:\Workspace\IngenieriaWeb\Grupal\semana6\ProcesosSoftwareAnemia\exportados\semana-06\Presentacion_Integrador_Anemia_Junin.pdf').pages))"` (si no tienes `pypdf`, ábrelo y cuenta).

## 13. Exportar el informe a PDF y verificar marcadores

- **Estado v2:** `exportados\semana-06\Informe_Integrador_Anemia_Junin.pdf` (50 páginas) y `.docx` ya existen de forma provisional (S6-05 sin informe). Contienen 18 `COMPLETAR`, formato Letter, el título de metadatos `_temp` (N-12) y la captura 07 duplicada en las págs. 43-44 (N-14). Las 35 figuras sí están embebidas (verificado). Hay que **reexportarlos** una vez resueltos los pasos 1 a 7, 9 y 10; este paso pasa a ser «reexportar y verificar».

- **Cuándo:** solo después de los pasos 1 a 7, 9 y 10 y de las correcciones automáticas (`INSPECCION_S6.md` §4).
- **Pasos:**
  1. Verifica que no quedan marcadores:

```powershell
Select-String -Path "$R\entregables\semana-06-integrador\Informe_Integrador_Anemia_Junin.md" -Pattern "COMPLETAR|PENDIENTE|CARGA_CIERRE|pendiente -->|TODO"
# Debe imprimir nada
```

  2. Pide a `conversor-entregas` la tarea S6-05 (PDF y DOCX en `exportados\semana-06\`).
  3. Abre el PDF y revisa: portada completa (fecha, docente, códigos), 35 figuras visibles (ninguna en blanco; la captura 07 no debe repetirse), tablas sin cortes, índice y tablas numeradas.
- **Verificación:** existen `exportados\semana-06\Informe_Integrador_Anemia_Junin.pdf` y `.docx`; el PDF no contiene la cadena `COMPLETAR`.

## 14. Decidir si el tag `v1.0-PMV` se mueve a `main`

- **Situación (C-01):** `v1.0-PMV` apunta a 9ce90c3 (rama `entrega-s5-s7`), no alcanzable desde `main`; el código es idéntico al de `main:pmv_fastapi/`. El informe l.677 lo documenta. **Recomendación: no mover el tag**; es una referencia ya entregada y el informe lo explica.
- **Alternativa segura (no destructiva):** crear un tag adicional en `main` cuando el PR esté fusionado (paso 16), por ejemplo `v1.1-integrador`:

```powershell
git -C $R checkout main
git -C $R pull
git -C $R tag -a v1.1-integrador -m "Entrega integradora S6: informe, presentación y PMV en pmv_fastapi/"
git -C $R push origin v1.1-integrador
```

  Después agrega esa fila a la Tabla 31 del informe (l.666) y al README raíz.
- **Opción «mover el tag» (NO recomendada, destructiva):** exige reescribir un tag público que otras personas (el docente) pueden haber clonado, y el commit `main` no contiene `pmv_fastapi` en la raíz como el tag. Si aun así el equipo y el docente lo deciden:

```powershell
git -C $R tag -f -a v1.0-PMV <commit-en-main> -m "PMV / Incremento 1: HU-01 a HU-05, 77 pruebas, cobertura 99 %"
git -C $R push --force origin v1.0-PMV      # ADVERTENCIA: reemplaza el tag remoto; irreversible para quien ya lo descargó
```

  **Advertencia:** el push forzado del tag cambia lo que vean quienes abran el enlace del informe; el informe (l.666 y l.677) y el README deberán reescribirse porque dejarán de ser ciertos. Ningún agente puede hacerlo: lo ejecuta una persona con permisos.
- **Verificación:** `git -C $R ls-remote --tags origin` muestra los tags esperados; el enlace `https://github.com/woshtsu/ProcesosSoftwareAnemia/tree/v1.0-PMV` abre.

## 15. Subir los entregables al aula virtual

- **Qué se sube (3 entregables):**
  1. `exportados\semana-06\Informe_Integrador_Anemia_Junin.pdf`.
  2. `exportados\semana-06\Presentacion_Integrador_Anemia_Junin.pptx` (y el `.pdf` como respaldo si el aula lo admite).
  3. Enlace del repositorio con el tag: `https://github.com/woshtsu/ProcesosSoftwareAnemia` y `https://github.com/woshtsu/ProcesosSoftwareAnemia/tree/v1.0-PMV` (agrega el tag adicional del paso 14 si lo crearon).
- **Pasos:**
  1. Entra al aula virtual de Procesos de Software (ASUC01702), tarea «Informe Integrador».
  2. Adjunta el PDF del informe y el PPTX; pega el enlace del repositorio en el cuadro de texto o en el campo de enlace.
  3. Verifica que el repositorio es visible para el docente (si es privado, agrégalo como colaborador).
  4. Envía **una sola vez** por grupo (confirma si lo hace un representante).
  5. Descarga el comprobante o captura la pantalla de entrega.
- **Verificación:** comprobante de entrega con fecha y hora; abre los archivos subidos y comprueba que son los finales.

## 16. Pull request y merge a `main`

- **Previo:** el `guardian-merge` debe haber emitido `coordinacion\s6\CHECK_MERGE.md` con «APTO PARA PR» (S6-07). Solo el usuario con permisos hace push, PR y merge.
- **Pasos:**
  1. En GitHub, abre *Pull requests* → *New pull request*: base `main`, compare `feature/s6-integrador-final`.
  2. Título sugerido: «S6: integrador final (informe, presentación, figuras y CI en la raíz)». Verifica que el CI del PR esté en verde.
  3. Revisa los archivos cambiados (no deben aparecer `.venv`, `node_modules` ni archivos grandes) y fusiona (*Squash and merge* o *Merge*, según acuerden).
  4. Tras el merge, `imagen-staging` corre en `main`: verifica que termine en verde.
- **Verificación:** `git -C $R log origin/main --oneline -3` incluye el commit de S6.

## 17. Ensayo cronometrado de 7 minutos

- **Material:** `entregables\semana-06-integrador\presentacion\GUION_EXPOSICION.md` y el PPTX con las notas del orador.
- **Pasos:**
  1. Confirmen quién expone cada diapositiva (propuesta: Porras 1, 2 y 7; Auqui 3 y 5; Huamani 4 y 6). Si cambian el reparto, actualicen la tabla §1 del guion y borren el `[COMPLETAR]` de l.5.
  2. Preparen el equipo de la exposición: staging levantado (paso 8) y el video abierto en una pestaña como respaldo (paso 10).
  3. Cronometren un ensayo completo con las diapositivas en pantalla completa. Meta: **7:00 como máximo**: 1:05, 1:05, 1:05, 1:05, 1:25, 0:40 y 0:35.
  4. Si se pasan, recorten la diapositiva 5 (demo o video), no las demás.
  5. Repitan al menos tres veces, la última sin leer el guion. Graben una de ellas y cronometren con el teléfono.
  6. Ensayen la falla de la demo: cambiar al video (plan B) en menos de 10 segundos.
  7. Marquen en la lista del guion §4 («Lista de verificación antes de exponer») cada casilla lograda.
- **Verificación:** tres ensayos consecutivos <= 7:00 con el reparto final; el equipo y el video funcionan en el equipo con el que se expondrá.

## 18. Preparar la defensa individual (5 minutos por integrante)

- **Material:** guion §3 (preguntas por proceso, arquitectura/repositorio y pruebas) e informe §2 a §4.
- **Pasos para cada integrante (los tres, sin excepción: C8 evalúa a cada uno):**
  1. Lee las 20 preguntas de `GUION_EXPOSICION.md` §3 y responde en voz alta sin mirar las respuestas; compáralas.
  2. Recorre el repositorio con el compañero: `pmv_fastapi\app\domain`, `application`, `adapters`, `tests`, `db`, `docs\adr`, `docs\evidencias`.
  3. Ejecuta tú mismo, una vez, estos comandos y explica el resultado:

```powershell
Set-Location "$R\pmv_fastapi"
.\.venv\Scripts\python -m pytest --cov=app           # 73 pruebas, cobertura aproximada del 99 %
.\.venv\Scripts\python -m ruff check .               # 0 hallazgos
```

  4. Prepara tres respuestas propias sobre: (a) por qué hexagonal y no microservicios; (b) cómo se descubrió y corrigió DEF-01 y DEF-02; (c) qué falta del PMV (autenticación, cola sin conexión, aceptación del usuario, SonarCloud sin activar).
  5. Prepara respuestas honestas a las preguntas incómodas: «¿Cuántas pruebas ejecutaron realmente?» (77 declaradas en el tag; 73 reproducidas el 01/10 más las E2E si hicieron el paso 11); «¿Por qué cambiaron de Flask a FastAPI?» (paso 6); «¿Hay usuario final?» (paso 5).
  6. Simulen preguntas cruzadas: cada uno pregunta a otro integrante algo que no sea de su diapositiva.
- **Verificación:** cada integrante responde 5 preguntas al azar en menos de 5 minutos sin leer.
