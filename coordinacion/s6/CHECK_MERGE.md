# CHECK_MERGE — S6-07 Guardian Merge

**Fecha:** 2026-10-02  
**Rama:** `feature/s6-integrador-final`  
**HEAD:** `8ea87e6` (S6: correcciones de la inspección v2)  
**origin/main:** `0c9e302` (PMV v1.0)  
**Ejecutado por:** GUARDIAN-MERGE (Haiku 4.5)

---

## Resumen ejecutivo

**VEREDICTO: NO APTO PARA PR** (por archivos > 5 MB)

Se detectaron 2 archivos que exceden el límite de 5 MB cada uno, lo que es BLOQUEANTE. Estos son PDF y DOCX exportados (`exportados/semana-06/`), destinados a evidencia del trabajo realizado. Recomendación: antes de hacer merge, el equipo debe decidir si incluirlos o agregarlos a `.gitignore`.

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
0	3
```
**Resultado:** 
- origin/main está 0 commits adelante de HEAD
- HEAD (feature/s6-integrador-final) está **3 commits adelante** de origin/main
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

### 5. Archivos: tamaño, binarios, secretos (⚠️ BLOQUEANTE - archivos > 5 MB)

#### 5.1. Archivos > 1 MB (nuevos/modificados)
```
exportados/semana-06/Informe_Integrador_Anemia_Junin.docx   | 5 MB    | BLOQUEANTE (> 5 MB)
exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf    | 7 MB    | BLOQUEANTE (> 5 MB)
exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pdf | 1 MB  | ADVERTENCIA (> 1 MB)
exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pptx | 2 MB | ADVERTENCIA (> 1 MB)
```

**Resultado:** 
- **DOS ARCHIVOS BLOQUEANTE** (`docx` de 5 MB y `pdf` de 7 MB)
- Dos ADVERTENCIA adicionales (1–2 MB)
- Total en `exportados/semana-06/`: ~15 MB
- **Recomendación:** 
  1. Si son evidencia destinada a versionar: agregar regla en `.gitignore` para `exportados/` con excepción explícita (p. ej. `!exportados/semana-06/`). Esto documenta la intención.
  2. Si NO son necesarios en el repo: removerlos (`git rm --cached`) y agregarles a `.gitignore`.
  3. Alternativa: usar Git LFS (Large File Storage) para archivos binarios > 100 MB (no implementado en este proyecto).

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

### 6. .gitignore (⚠️ ADVERTENCIA - cobertura incompleta)

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
**ADVERTENCIA:** `.gitignore` NO cubre:
- `exportados/` (archivos PDF, PPTX, DOCX de salida)
- Potencialmente: `datos/` (datos de prueba), `_build/` a nivel raíz
- Archivos como `.env.local`, `.vscode/`, `.idea/`

**Recomendación:** Agregar:
```
# Artefactos exportados (PDFs, PPTXs, DOCXs)
exportados/
# O si solo se ignora raíz: 
# exportados/*.pdf
# exportados/*.pptx
# exportados/*.docx

# Datos locales de prueba
datos/
```

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
- **Exportados:** DOCX, PDF, PPTX (~15 MB, BLOQUEANTE)
- **Herramientas:** `herramientas/conversion/exportar_s6.py`, `exportar_s6.ps1`
- **CI:** `.github/workflows/ci.yml` (YAML + tests)
- **Reorganización:** Movimiento de `diagramador.md` y `orquestador.md` a `archivo/agentes-anteriores/`

---

## Comandos para el merge (NO EJECUTAR AÚN)

Cuando se resuelva el problema de archivos > 5 MB, ejecutar:

```bash
# 1. Push de la rama (desde el equipo)
git push -u origin feature/s6-integrador-final

# 2. Abrir PR hacia main (con gh CLI)
gh pr create --base main --head feature/s6-integrador-final \
  --title "S6: Integrador Anemia Junín (informe, presentación, arquitectura PMV FastAPI)" \
  --body "
## Resumen

Incremento S6 del proyecto Anemia Junín:

- Entrega del **Informe Integrador** (PMV FastAPI, arquitectura hexagonal, CI/CD, pruebas, cobertura 99 %, carga P95)
- **Presentación** (68 diapositivas: procesos, ciclo de vida, C4, NFR, matriz de factores, roadmap)
- **Documentación**: protocolo S6, requisitos, datos del PMV, contexto procesos S1–S5, inspección, pasos manuales
- **Diagramas S6** (13 nuevos: C4 FastAPI, despliegue Docker, píramide de pruebas, burnup, flujo trazabilidad, roadmap)
- **CI/CD**: GitHub Actions en raíz (`.github/workflows/ci.yml`), pipeline con Ruff + pytest (80 %) + cobertura + Docker
- **Agentes**: 9 agentes de coordinación (sincronizador, inspector-guía, redactor-informe-integrador, etc.)
- **Herramientas**: scripts de exportación (exportar_s6.py, pptx_a_pdf.ps1)

## Plan de prueba

- [ ] CI en verde (push en GitHub)
- [ ] Descargar los PDFs y PPTX para verificar calidad visual y metadatos
- [ ] Revisar el informe integrador (75 páginas, A4, 35 figuras)
- [ ] Revisar la presentación (68 diapositivas, variantes 16:9 y medias)
- [ ] Verificar que los diagramas PNG/SVG de los .md renderizan correctamente

🤖 Generated with [Claude Code](https://claude.com/claude-code)
"
```

---

## Recomendaciones finales

1. **Inmediato (BLOQUEANTE):**
   - [ ] Resolver archivos > 5 MB en `exportados/semana-06/`:
     - **Opción A:** Remover con `git rm --cached` y agregar `exportados/` a `.gitignore`
     - **Opción B:** Mantener si son "entregables finales", pero documentar en un README (`exportados/README.md`)
     - **Opción C:** Usar rama de "artefactos" o wiki de GitHub para alojamiento alternativo

2. **Antes del push:**
   - [ ] Complementar `.gitignore` con `exportados/`, `datos/` y otras rutas no cubiertas
   - [ ] Verificar que el usuario puede hacer push a origin/feature/s6-integrador-final (permisos)
   - [ ] Confirmar que origin/main es el target correcto (no feature/s6-integrador-final)

3. **Después del PR:**
   - [ ] Esperar a que GitHub Actions (CI) corra en verde
   - [ ] Revisar el reporte de cobertura y Ruff en el workflow
   - [ ] Antes de mergear a main, pedir approval de al menos 1 revisor (si hay reglas de rama protegida)

4. **Tags:**
   - [ ] Dejar v1.0-PMV sin cambios (sigue apuntando a S5)
   - [ ] Crear v1.1-integrador tras mergar S6 (opcional, si la política lo requiere)

---

## Checklist del inspector

- [x] Merge-tree simulado: **sin conflictos**
- [x] Archivos > 5 MB: **2 detectados (BLOQUEANTE)**
- [x] .venv, __pycache__, .db: **ninguno**
- [x] Secretos: **ninguno (solo ejemplos documentados)**
- [x] YAML CI: **válido**
- [x] .gitignore: **incompleto (ADVERTENCIA)**
- [x] Tags: **informativo (v1.0-PMV en rama no alcanzable)**
- [x] README de diagramas y herramientas: **existente**

---

**Generado por:** GUARDIAN-MERGE (Claude Haiku 4.5)  
**Hora:** 2026-10-02 (git-merge-analysis)
