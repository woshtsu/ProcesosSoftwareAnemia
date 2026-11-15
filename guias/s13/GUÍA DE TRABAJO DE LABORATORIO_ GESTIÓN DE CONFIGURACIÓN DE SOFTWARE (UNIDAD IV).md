### GUÍA DE TRABAJO DE LABORATORIO: GESTIÓN DE CONFIGURACIÓN DE SOFTWARE (UNIDAD IV)

**Universidad Continental**

**Facultad de Ingeniería de Sistemas e Informática**

**Asignatura:** Procesos de Software (Código: ASUC01702)

**Ciclo / Nivel:** Noveno Ciclo (IX Período - Electivo de Especialidad)

**Unidad IV:** Gestión de Configuración de Software

**Duración:** 16 Horas Académicas

#### 1. MARCO OPERATIVO Y ALINEACIÓN AL SÍLABO

La Gestión de Configuración de Software (Software Configuration Management - SCM) es la disciplina de la ingeniería de software responsable de identificar, organizar, controlar y rastrear la evolución de los productos de trabajo ( *Work Products* ) a lo largo del ciclo de vida del desarrollo. La Unidad IV del sílabo se compone de cuatro ejes temáticos fundamentales:

1. **Administración del Cambio (Change Management):** Canalización formal, evaluación de impacto y aprobación de modificaciones en los requisitos o artefactos del sistema.
2. **Gestión de Versiones y Entregas (Version & Release Management):** Control del historial del código, aislamiento de características y etiquetado de versiones estables.
3. **Construcción del Sistema (System Building):** Compilación automatizada, verificación de dependencias e integración continua.
4. **Herramientas de Proceso de Ingeniería de Software:** Operacionalización de las prácticas de SCM mediante la suite gratuita de GitHub.

La suite gratuita de GitHub (GitHub Free y GitHub Student Developer Pack) proporciona las capacidades necesarias para implementar SCM sin costos de licenciamiento, incluyendo repositorios privados ilimitados, tableros de gestión, automatización de integración continua y publicación de versiones.

#### 2. OBJETIVOS Y PRODUCTOS ESPERADOS

##### Objetivos de Aprendizaje

* **Objetivo General:** Aplicar las técnicas de Gestión de Configuración de Software (SCM) y la mejora continua en el proyecto de asignatura utilizando la suite gratuita de GitHub.
* **Objetivos Específicos:**
* Estructurar el control de cambios mediante plantillas estandarizadas e inspección por pares ( *Code Review* ).
* Configurar políticas de protección de código y estrategias de ramificación profesional ( *GitFlow* ).
* Automatizar la integración continua ( *CI/CD* ) y auditar la calidad antes de la consolidación del código.
* Publicar liberaciones de software empaquetadas ( *Releases* ) con etiquetado semántico ( *SemVer* ).

##### Entregables del Laboratorio

1. Repositorio institucional en GitHub estructurado con reglas de protección de ramas ( *Branch Protection Rules* ).
2. Plantillas de Solicitud de Cambio (.github/ISSUE\_TEMPLATE/change\_request.md) y de Reclasificación de Código (.github/PULL\_REQUEST\_TEMPLATE.md).
3. Registro y solución trazable de solicitudes de cambio mediante Issues y Pull Requests.
4. Pipeline de Integración Continua activo en GitHub Actions.
5. Publicación oficial del Producto Mínimo Viable (PMV) e incrementos posteriores en GitHub Releases (v1.0-PMV, v2.0-Inc2).

#### 3. RESUMEN EJECUTIVO DE LOS EJES TEMÁTICOS DE LA UNIDAD IV

##### Eje Temático 1: Administración del Cambio

El control de cambios impide que las modificaciones no autorizadas degraden la calidad de la línea base ( *Baseline* ). Cada cambio propuesto debe registrarse como una Solicitud de Cambio (RFC), evaluar su impacto en esfuerzo y riesgo, y ser aprobado formalmente mediante un Pull Request (PR) que requiera la revisión obligatoria de código ( *Code Review* ) por parte del arquitecto o líder de calidad.

##### Eje Temático 2: Gestión de Versiones y Entregas

Utiliza la estrategia de ramificación **GitFlow** para aislar el trabajo concurrente del equipo:

* **Rama** **main** **:** Representa la línea base de producción. Solo recibe integraciones probadas desde ramas de liberación.
* **Rama** **develop** **:** Línea base de integración para el trabajo diario del equipo.
* **Ramas** **feature/**\* **:** Ramas temporales creadas para desarrollar una Historia de Usuario o cambio específico.
* **Ramas** **release/**\* **:** Ramas de estabilización previas a la publicación oficial.

Las entregas de software se identifican mediante **Versionamiento Semántico (SemVer)** siguiendo la estructura vMAJOR.MINOR.PATCH (por ejemplo, v1.0.0-PMV).

##### Eje Temático 3 y 4: Construcción del Sistema y Suite Gratuita de GitHub

La construcción del sistema se automatiza mediante **GitHub Actions** . Ante cada Pull Request enviado hacia la rama develop o main, el pipeline ejecuta de forma autónoma la compilación, las pruebas unitarias y el análisis estático de código, bloqueando la fusión si se detectan fallas o vulnerabilidades.

#### 4. GUÍA DE ACTIVIDADES PRÁCTICAS PASO A PASO CON EVIDENCIAS VISUALES

##### ACTIVIDAD 1: Configuración de la Línea Base y Registro de Cambios (Eje 1)

El equipo debe estandarizar el ingreso de Solicitudes de Cambio (RFC) en el repositorio GitHub evitando modificaciones arbitrarias en el código.

###### Paso 1.1: Creación de la Plantilla de Solicitud de Cambio

En la ruta .github/ISSUE\_TEMPLATE/change\_request.md del repositorio, cree la siguiente plantilla:

---

name: "Solicitud de Cambio (RFC)"

about: "Propuesta formal de modificación de requisitos, corrección o mejora"

title: "[RFC] "

labels: "change-request, pendiente-evaluacion"

---

### 1. DESCRIPCIÓN DEL CAMBIO SOLICITADO

- \*\*Módulo / Componente Afectado:\*\* [Ej. Módulo de Autenticación / API REST]

- \*\*Tipo de Cambio:\*\* Corrección de Defecto / Cambio de Requisito / Refactorización

- \*\*Justificación:\*\* [Explicar por qué el cambio genera valor a la organización]

### 2. ANÁLISIS DE IMPACTO

- \*\*Impacto en Tiempo / Esfuerzo:\*\* [Estimación en horas o Puntos de Historia]

- \*\*Nivel de Riesgo:\*\* [Bajo / Medio / Alto]

### 3. CRITERIOS DE ACEPTACIÓN

- Pruebas unitarias actualizadas y ejecutadas sin errores.

###### Paso 1.2: Registro de Cambio en GitHub Issues

Registre un Issue real en GitHub aplicando la plantilla de Solicitud de Cambio.

**EVIDENCIA VISUAL OBLIGATORIA (CAPTURA DE PANTALLA 1)**

**Ubicación en el Informe:** Registro del Issue de Solicitud de Cambio en GitHub.

**Descripción:** Captura de pantalla de la interfaz de GitHub Issues mostrando la Solicitud de Cambio (RFC) creada con su número asignado (por ejemplo, #12), etiquetas ( *labels* ) y análisis de impacto.

**Archivo de Evidencia:** /docs/evidencias/actividad1\_issue\_change\_request.png

##### ACTIVIDAD 2: Control de Cambios, Branch Protection y Code Review (Eje 1 y 4)

Configure las reglas de protección de ramas en GitHub para impedir commits directos sobre la línea base.

###### Paso 2.1: Configuración de Reglas de Protección

Acceda a **Settings ➔ Branches ➔ Add Branch Protection Rule** para la rama main y develop, y active:

1. **Require a pull request before merging:** Exige que todo cambio ingrese por PR.
2. **Require approvals:** Requiere al menos 1 aprobación previa de un par o revisor.
3. **Require status checks to pass before merging:** Exige que los tests automatizados pasen antes de fusionar.

**EVIDENCIA VISUAL OBLIGATORIA (CAPTURA DE PANTALLA 2)**

**Ubicación en el Informe:** Configuración de Branch Protection Rules en GitHub.

**Descripción:** Captura de pantalla del panel de administración de GitHub mostrando las casillas activadas para exigir Pull Requests y aprobaciones obligatorias en la rama main.

**Archivo de Evidencia:** /docs/evidencias/actividad2\_branch\_protection\_rules.png

###### Paso 2.2: Creación de Plantilla de Pull Request e Inspección de Código

Cree el archivo .github/PULL\_REQUEST\_TEMPLATE.md para estandarizar las revisiones:

## DESCRIPCIÓN DEL CAMBIO

- \*\*Resumen:\*\* [Breve explicación de las modificaciones de código]

- \*\*Fixes Issue:\*\* Closes # [Número del Issue de la Solicitud de Cambio]

## CHECKLIST DE CRITERIOS DE TERMINACIÓN (Definition of Done)

- Código compilado sin errores.

- Pruebas unitarias aprobadas con cobertura >= 80%.

- Estructura conforme a Arquitectura Hexagonal (/src/domain/ desacoplado).

**EVIDENCIA VISUAL OBLIGATORIA (CAPTURA DE PANTALLA 3)**

**Ubicación en el Informe:** Aprobación de Pull Request y Code Review.

**Descripción:** Captura de pantalla de un Pull Request en GitHub mostrando la revisión aprobada por un integrante del equipo, la verificación verde de los checks automatizados y la vinculación con el Issue correspondiente.

**Archivo de Evidencia:** /docs/evidencias/actividad2\_pull\_request\_code\_review.png

##### ACTIVIDAD 3: Estrategia de Ramificación GitFlow (Eje 2)

Implemente la estrategia GitFlow aislando el trabajo en ramas independientes por cada Historia de Usuario.

###### Paso 3.1: Ejecución de Comandos de Ramificación

# Crear y posicionarse en la rama de integración develop

git checkout -b develop

git push origin develop

# Crear rama temporal para una Historia de Usuario o Cambio

git checkout -b feature/hu01-registro-usuario develop

# Realizar modificaciones con commits semánticos

git commit -m "feat(auth): implementa formulario de registro y validaciones"

# Publicar la rama en el repositorio remoto

git push origin feature/hu01-registro-usuario

**EVIDENCIA VISUAL OBLIGATORIA (CAPTURA DE PANTALLA 4)**

**Ubicación en el Informe:** Red de Ramas y Commits en GitHub Insights.

**Descripción:** Captura de pantalla del gráfico de red ( *Network Graph* ) en GitHub Repository Insights mostrando las ramas main, develop y las ramas feature/\* derivándose e integrándose adecuadamente.

**Archivo de Evidencia:** /docs/evidencias/actividad3\_gitflow\_network\_graph.png

##### ACTIVIDAD 4: Automatización CI/CD con GitHub Actions (Eje 3 y 4)

Configure un flujo automatizado de integración continua que valide cada cambio propuesto.

###### Paso 4.1: Archivo de Workflow de GitHub Actions

En la ruta .github/workflows/ci.yml, agregue la siguiente especificación:

name: Continuous Integration Pipeline

on:

pull\_request:

branches: [ develop, main ]

jobs:

build-and-test:

runs-on: ubuntu-latest

steps:

- name: Checkout del Código

uses: actions/checkout@v4

- name: Configurar Entorno Node.js / Python / Java

uses: actions/setup-node@v4

with:

node-version: '20'

- name: Instalación de Dependencias

run: npm ci

- name: Ejecución de Pruebas Unitarias

run: npm test

- name: Verificación de Linter y Estándares

run: npm run lint

**EVIDENCIA VISUAL OBLIGATORIA (CAPTURA DE PANTALLA 5)**

**Ubicación en el Informe:** Ejecución Exitosa de Pipeline en GitHub Actions.

**Descripción:** Captura de pantalla de la pestaña *Actions* de GitHub mostrando la ejecución completa del pipeline con verificación verde ( *Passed* ) para compilación y pruebas unitarias.

**Archivo de Evidencia:** /docs/evidencias/actividad4\_github\_actions\_pipeline.png

##### ACTIVIDAD 5: Versionamiento Semántico y GitHub Releases (Eje 2)

Empaquete los incrementos validados del software utilizando versionamiento semántico y etiquetado de Git.

###### Paso 5.1: Comandos de Etiquetado Semántico

# Cambiar a la rama main actualizada

git checkout main

git pull origin main

# Crear etiqueta firmada para el Producto Mínimo Viable (PMV)

git tag -a v1.0-PMV -m "Liberación del Producto Mínimo Viable (PMV) - Incremento 1"

# Enviar la etiqueta a GitHub

git push origin v1.0-PMV

###### Paso 5.2: Publicación Oficial del Release en GitHub

Acceda a **GitHub ➔ Releases ➔ Draft a new release** , seleccione la etiqueta v1.0-PMV y complete las notas de la entrega ( *Release Notes* ).

**EVIDENCIA VISUAL OBLIGATORIA (CAPTURA DE PANTALLA 6)**

**Ubicación en el Informe:** Publicación Oficial de Release en GitHub.

**Descripción:** Captura de pantalla de la sección *Releases* en GitHub mostrando la versión v1.0-PMV publicada, con su descripción de cambios, tag asociado y archivos adjuntos (compilados/Docker).

**Archivo de Evidencia:** /docs/evidencias/actividad5\_github\_release\_v1\_0.png

#### 5. MATRIZ DE TRAZABILIDAD SCM UNIFICADA

La trazabilidad bidireccional garantiza que cada artefacto publicado en una versión responda a una solicitud de cambio formalmente aprobada y probada:

TABLA 1: MATRIZ UNIFICADA DE TRAZABILIDAD SCM (GESTIÓN DE CONFIGURACIÓN)

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| ID Solicitud de Cambio / Requisito | Issue en GitHub | Rama Git Creada (Estrategia GitFlow) | Pull Request & Code Review | Tag Semántico / Release | Artefacto Generado / Despliegue |
| **Requisito PMV (Autenticación)** | Issue #01 | feature/hu01-auth | PR #04 (Aprobado por @tech\_lead) | v1.0-PMV | Contenedor Docker api:v1.0 / Staging |
| **Requisito PMV (Ingesta REST)** | Issue #02 | feature/hu02-ingest | PR #05 (Aprobado por @qa\_lead) | v1.0-PMV | Contenedor Docker api:v1.0 / Staging |
| **Solicitud de Cambio MFA (#12)** | Issue #12 | feature/mfa-login | PR #13 (Aprobado por @tech\_lead) | v2.0-Inc2 | Contenedor Docker api:v2.0 / Staging |
| **Parche Expiración JWT (#15)** | Issue #15 | hotfix/jwt-expiry | PR #16 (Aprobado por @qa\_lead) | v2.0.1-Patch | Imagen Parchada api:v2.0.1 / Producción |
| **Requisito Inc. 3 (Reportes)** | Issue #20 | feature/hu06-reports | PR #22 (Aprobado por @architect) | v3.0-Inc3 | Release Final app-v3.0.zip / Producción |

#### 6. RÚBRICA DE EVALUACIÓN DE LA GUÍA DE LABORATORIO (20 PUNTOS)

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Criterio de Evaluación | Excelente (100% Puntaje) | Bueno (75% Puntaje) | Básico (50% Puntaje) | Inicial (25% Puntaje) | Puntaje Máximo |
| **1. Administración del Cambio en GitHub (Eje Temático 1)** | Implementa plantillas institucionales de Issues/PRs, audita solicitudes de cambio (RFC), exige revisiones de código (Code Review) por pares y aplica reglas de protección de ramas (Branch Protection Rules). | Implementa solicitudes de cambio en GitHub Issues, configura plantillas de PRs y ejecuta revisiones de código entre pares. | Configura solicitudes de cambio de forma incompleta o sin aplicar reglas de protección de ramas en GitHub. | No registra solicitudes de cambio ni utiliza las herramientas de administración del cambio en GitHub. | **5.0 Puntos** |
| **2. Estrategia de Ramificación y Control SCM (Eje Temático 2)** | Define y ejecuta con rigor la estrategia de ramificación **GitFlow** (main, develop, feature/\*), demostrando trazabilidad completa entre ramas e Historias de Usuario. | Aplica una estrategia de ramificación organizada en Git con separación de ramas principales y de trabajo. | Muestra un uso desordenado de ramas en Git con commits directos sobre la rama principal (main). | Todo el desarrollo se realiza en una sola rama sin control de configuración ni aislamiento. | **5.0 Puntos** |
| **3. Gestión de Versiones, Tags y Releases en GitHub (Eje Temático 2)** | Etiqueta semánticamente los incrementos (v1.0-PMV, v2.0-Inc2), publica los **GitHub Releases** con Release Notes completas y adjunta los artefactos compilados. | Aplica etiquetas semánticas (Git Tags) para los incrementos y publica las entregas (Releases) en GitHub con notas descriptivas. | Aplica etiquetas de versión incompletas o publica releases sin notas de entrega ni artefactos. | No realiza etiquetado semántico de versiones ni publica entregas (Releases) en la plataforma GitHub. | **5.0 Puntos** |
| **4. Trazabilidad Integrada y Repositorio GitHub** | Construye la matriz de trazabilidad unificada SCM (Cambio ➔ Issue ➔ Rama ➔ PR ➔ Tag ➔ Release) y presenta el repositorio GitHub perfectamente estructurado. | Construye la matriz de trazabilidad de configuración y presenta un repositorio organizado con historial activo. | Presenta trazabilidad parcial con desconexión entre solicitudes de cambio y versiones liberadas. | Entregable desorganizado, sin matriz de trazabilidad ni enlaces válidos a la Suite de GitHub. | **5.0 Puntos** |

**Puntaje Máximo:** 20 puntos