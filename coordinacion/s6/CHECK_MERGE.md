# CHECK_MERGE — S6-07 Guardian Merge

**Fecha:** 2026-10-02  
**Rama:** `feature/s6-integrador-final`  
**HEAD:** `ff33fe3` (4 commits sobre `origin/main`)  
**origin/main:** `0c9e302` (PMV v1.0)  
**Ejecutado por:** GUARDIAN-MERGE

---

## Resumen ejecutivo

**VEREDICTO: APTO CON OBSERVACIONES**

0 conflictos (`git merge-tree`), 0 commits por detrás de `origin/main`, CI válido y sin secretos. El umbral de 5 MB usado en una primera pasada era interno: GitHub solo rechaza archivos de más de 100 MB y avisa desde 50 MB. Los exportados (PDF 7,4 MB, DOCX 6,0 MB, PPTX 2,3 MB, PDF 2,1 MB) son entregables que el README manda subir al aula y deben seguir versionados.

Observaciones:
1. Binarios de varios MB en `exportados/semana-06/`: aceptables.
2. El tag `v1.0-PMV` no es alcanzable desde `main`; el merge no lo cambia.
3. El CI aún no se ha ejecutado en GitHub.

---

## Verificaciones detalladas

### 1. Estado local (✓ OK)
```bash
$ git status --porcelain
# (sin salida - árbol limpio)

$ git branch --show-current
feature/s6-integrador-final
```
**Resultado:** Árbol limpio, rama correcta.

---

### 2. Fetch y referencias remotas (✓ OK)
```bash
$ git fetch origin --prune --tags
# (silencioso - sin cambios)
```
**Resultado:** Fetch exitoso, referencias actualizadas.

---

### 3. Divergencia respecto de origin/main (✓ OK)
```bash
$ git rev-list --left-right --count origin/main...HEAD
0	4
```
**Resultado:** 
- origin/main está 0 commits adelante de HEAD
- HEAD (feature/s6-integrador-final) está **4 commits adelante** de origin/main
- Commits nuevos:
  - `8ea87e6`: S6: correcciones de la inspección v2 (N-01…N-14)
  - `fdc50c5`: S6: cierre del informe integrador
  - `807d3dc`: S6: requisitos, datos del PMV FastAPI, agentes y protocolo
- Sin cambios en origin/main desde el branch point (OK)

---

### 4. Simulación del merge (✓ OK - sin conflictos)
```bash
$ git merge-tree --write-tree --name-only origin/main HEAD
36a9a66d541bad19ddbe72f54c711fa35b563842
Exit code: 0
```
**Resultado:** 
- **Sin conflictos** (exit code = 0)
- Árbol de merge válido: `36a9a66d541bad19ddbe72f54c711fa35b563842`
- El merge automático tendría éxito

---

### 5. Archivos: tamaño, binarios, secretos (OK con observación)

#### 5.1. Archivos de varios MB (aceptables)
```
exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf        | 7,4 MB
exportados/semana-06/Informe_Integrador_Anemia_Junin.docx       | 6,0 MB
exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pptx  | 2,3 MB
exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pdf   | 2,1 MB
```
**Resultado:** ninguno se acerca a los 50 MB (aviso de GitHub) ni a los 100 MB (rechazo). Son entregables del aula: se mantienen versionados; no se quitan ni se ignoran.

#### 5.2. Archivos problemáticos (.venv, __pycache__, etc.)
```bash
$ git diff origin/main...HEAD --name-only | grep -E '(\.venv|__pycache__|\.pytest_cache|\.ruff_cache|\.coverage|htmlcov|\.db|\.sqlite|plantuml.*\.jar|_build/)'
# (sin salida)
```
**Resultado:** ✓ Ningún archivo `.venv`, `__pycache__`, `.db`, `plantuml.jar` o caché. OK.

#### 5.3. Secretos (✓ OK - solo valores documentados)
```bash
$ git diff origin/main...HEAD | grep -nEi '(api[_-]?key|secret|token|password|passwd|BEGIN (RSA|OPENSSH|EC) PRIVATE|ghp_|sk_|AKIA)' | head -20
# Coincidencias encontradas (todas documentadas/ejemplos):
- "cambiar_en_staging" → placeholder en docker-compose.yml (DOCUMENTADO)
- "postgres" → credencial de prueba en CI (DOCUMENTADO)
- ${{ secrets.SONAR_TOKEN }} → referencia a GitHub Actions secrets (OK)
```
**Resultado:** ✓ Sin secretos reales. Solo credenciales de prueba documentadas.

#### 5.4. Archivos .env versionados
```bash
$ git diff origin/main...HEAD --name-only | grep -E '\.env'
# (sin salida)
```
**Resultado:** ✓ Ningún `.env` versionado.

---

### 6. .gitignore (OK)

#### 6.1. Contenido actual
```
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.ruff_cache/
diagramas/_build/
~$*
*.tmp
.DS_Store
Thumbs.db
herramientas/plantuml/*.jar
herramientas/.venv/
*.log
htmlcov/
.coverage
.coverage.*
*.db
*.sqlite
*.sqlite3
```

#### 6.2. Resultado
`.gitignore` cubre cachés, entornos, bases locales y el JAR de PlantUML. **No se agrega `exportados/`**: son entregables que deben versionarse.

---

### 7. Validez del YAML en CI (✓ OK)
```bash
$ python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('YAML válido')"
YAML válido
```
**Resultado:** 
- ✓ Sintaxis YAML correcta
- Archivo: `.github/workflows/ci.yml` en la raíz (GitHub Actions lo detectará)
- Rutas referenciadas existen:
  - `pmv_fastapi/requirements-dev.txt` ✓
  - `pmv_fastapi/pyproject.toml` ✓
  - `pmv_fastapi/sonar-project.properties` ✓

---

### 8. Tags y riesgos (ℹ️ INFORMATIVO - riesgo sin resolver)

```bash
$ git tag -l
v1.0-PMV

$ git ls-remote --tags origin | grep 'v1\.0-PMV'
6a17c636335a69c709c60a61cf5465e74b7b7e41	refs/tags/v1.0-PMV
9ce90c318c5c56383456d5860fb5a8a655035c80	refs/tags/v1.0-PMV^{}

$ git merge-base --is-ancestor 9ce90c3 origin/main
# Exit code: 1 (NO es alcanzable)
```

**Resultado:** 
- **v1.0-PMV apunta a `9ce90c3`** (rama `entrega-s5-s7`, no alcanzable desde `origin/main` en `0c9e302`)
- Este commit NO es antecesor de `origin/main`
- **Impacto del merge:** El merge de `feature/s6-integrador-final` en `origin/main` NO mueve el tag (tag sigue apuntando a `9ce90c3`)
- **Recomendación (inspector):** Mantener `v1.0-PMV` como está (versión del PMV del sprint 5); considerar usar `v1.1-integrador` para el incremento S6 si se requiere un tag para esta versión.

---

## Archivos del diff (170+ cambios)

**Categorías de cambios:**
- **Nuevos agentes:** `guardian-merge.md`, `sincronizador.md`, `redactor-informe-integrador.md`, etc.
- **Diagramas S6:** 50–68 en PNG/SVG/PUML (nuevos diagramas de arquitectura PMV FastAPI)
- **Documentación S6:** `coordinacion/s6/REQUISITOS_S6.md`, `PROTOCOLO_S6.md`, `DATOS_PMV_FASTAPI.md`, `INSPECCION_S6.md`, etc.
- **Informe integrador:** `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` (actualizado)
- **Presentación:** `entregables/semana-06-integrador/presentacion/Presentacion_Integrador_Anemia_Junin.md` + `generar_presentacion.py`
- **Exportados:** DOCX, PDF, PPTX (~18 MB en total, entregables)
- **Herramientas:** `herramientas/conversion/exportar_s6.py`, `exportar_s6.ps1`
- **CI:** `.github/workflows/ci.yml` (YAML + tests)
- **Reorganización:** Movimiento de `diagramador.md` y `orquestador.md` a `archivo/agentes-anteriores/`

---

## Comandos para el push y el PR (no ejecutados)

```bash
git push -u origin feature/s6-integrador-final

gh pr create --base main --head feature/s6-integrador-final   --title "S6: Integrador Anemia Junín (informe, presentación, arquitectura PMV FastAPI)"   --body-file coordinacion/s6/PR_BODY.md
```

El cuerpo del PR está en `coordinacion/s6/PR_BODY.md` (incluye «Pendientes manuales», que remite a `coordinacion/s6/PASOS_MANUALES.md`).

---

## Recomendaciones finales

1. Tras el push, esperar a que el CI corra en GitHub y revisar Ruff, pruebas y cobertura.
2. Dejar `v1.0-PMV` sin cambios; opcionalmente crear `v1.1-integrador` tras el merge.
3. Completar los pendientes manuales (`PASOS_MANUALES.md`) y reexportar antes de la entrega final.

---

## Checklist del inspector

- [x] Merge-tree simulado: sin conflictos
- [x] Commits por detrás de origin/main: 0
- [x] Binarios de varios MB: aceptables (entregables, < 50 MB)
- [x] .venv, __pycache__, .db: ninguno
- [x] Secretos: ninguno
- [x] YAML CI: válido (aún sin ejecutar en GitHub)
- [x] Tag v1.0-PMV: no alcanzable desde main, sin cambio por el merge

---

**Generado por:** GUARDIAN-MERGE; veredicto revisado el 2026-10-02.
