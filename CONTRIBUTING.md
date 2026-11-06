# Gestión de la configuración: cómo proponer e integrar cambios

Convención del equipo para ramas, commits, etiquetas y versiones de «Anemia Junín». Se adoptó el 06/11/2026 (guía de laboratorio S13, gestión de la configuración con GitHub) y corrige el hallazgo H5 del informe CMMI: «no hay convención escrita de commits, ramas y etiquetas».

## 1. Flujo de un cambio

1. **Solicitud.** Todo cambio de requisito, corrección o mejora se registra como *issue* con la plantilla «Solicitud de Cambio (RFC)» (`.github/ISSUE_TEMPLATE/change_request.md`). Entra con las etiquetas `change-request` y `pendiente-evaluacion`.
2. **Evaluación.** El Leader / Software Architect evalúa el impacto (alcance, esfuerzo y riesgo) y cambia la etiqueta a `aprobado` o `rechazado`. Un RFC rechazado se cierra con el motivo.
3. **Rama.** El cambio aprobado se trabaja en una rama propia (sección 2), nunca directamente en `main`.
4. **Pull request.** La PR usa la plantilla `.github/PULL_REQUEST_TEMPLATE.md`, enlaza el *issue* con `Closes #N` y completa la lista de la DoD.
5. **Revisión.** Otro integrante revisa y aprueba (*Approve*). El CI (`.github/workflows/ci.yml`) debe estar en verde.
6. **Integración y versión.** Se integra la PR. Al cerrar un incremento se crea la etiqueta y el *release* (sección 4).

## 2. Ramas (GitFlow)

| Rama | Uso | Recibe cambios de |
| --- | --- | --- |
| `main` | Línea base estable; es lo que se despliega en Render | `release/*` y `hotfix/*` |
| `develop` | Integración del incremento en curso | `feature/*`, `docs/*` |
| `feature/<id>-<descripcion>` | Una historia o RFC. Ej.: `feature/hist-5.1-modelo-predictivo` | sale de `develop` |
| `docs/<entrega>` | Entregables e informes. Ej.: `docs/s13-informe` | sale de `develop` (o de `main` mientras dure la transición) |
| `release/vX.Y-IncN` | Estabilización del incremento antes de liberarlo | sale de `develop`; se integra en `main` y `develop` |
| `hotfix/<descripcion>` | Corrección urgente en producción | sale de `main`; se integra en `main` y `develop` |

Transición: los incrementos 1 a 4 se integraron directamente en `main`. `develop` existe desde el 06/11/2026 y se usa a partir del Incremento 5.

## 3. Mensajes de commit

Formato: `tipo(ámbito): descripción en presente`, en español, de 72 caracteres como máximo en la primera línea.

| Tipo | Cuándo |
| --- | --- |
| `feat` | Funcionalidad nueva para el usuario |
| `fix` | Corrección de un defecto |
| `test` | Pruebas nuevas o corregidas |
| `refactor` | Cambio interno sin cambiar el comportamiento |
| `docs` | Documentación, entregables e informes |
| `ci` | Flujos de GitHub Actions y despliegue |
| `chore` | Dependencias, configuración y mantenimiento |

Ejemplos: `feat(recordatorios): reintentar por SMS si WhatsApp falla`, `fix(sincronizacion): serializar operaciones concurrentes`, `docs(s13): informe integrador corregido`.

El cuerpo del commit explica el porqué y referencia el *issue* (`Refs #N` o `Closes #N`).

## 4. Etiquetas y releases

- Etiqueta semántica por incremento: `vMAYOR.MENOR-IncN` (`v1.0-PMV`, `v2.0-Inc2`, `v3.0-Inc3`, `v4.0-Inc4`). Un hito intermedio usa `vX.Y.Z-incN-avance` y su *release* se marca como *pre-release*.
- Cada etiqueta tiene su *release* en GitHub con notas en tres bloques: novedades (historias), calidad (pruebas y cobertura) y limitaciones. El detalle técnico va en `pmv_fastapi/CHANGELOG.md`.
- La versión de la API (`pmv_fastapi/app/main.py`, campo `version`) coincide con la etiqueta (`4.0.0-inc4` para `v4.0-Inc4`).

| Etiqueta | Release |
| --- | --- |
| `v1.0-PMV` | [Producto Mínimo Viable (Incremento 1)](https://github.com/woshtsu/ProcesosSoftwareAnemia/releases/tag/v1.0-PMV) |
| `v1.5.0-inc2-avance` | [Incremento 2 al 50 % (pre-release)](https://github.com/woshtsu/ProcesosSoftwareAnemia/releases/tag/v1.5.0-inc2-avance) |
| `v2.0-Inc2` | [Agenda, alertas y asistencia (Incremento 2)](https://github.com/woshtsu/ProcesosSoftwareAnemia/releases/tag/v2.0-Inc2) |
| `v3.0-Inc3` | [Registro sin conexión, sincronización y visitas (Incremento 3)](https://github.com/woshtsu/ProcesosSoftwareAnemia/releases/tag/v3.0-Inc3) |
| `v4.0-Inc4` | [Recordatorios por WhatsApp y barreras de acceso (Incremento 4)](https://github.com/woshtsu/ProcesosSoftwareAnemia/releases/tag/v4.0-Inc4) |

## 5. Protección de ramas

Configuración prevista para `main` y `develop` en **Settings → Branches** (la aplica el propietario del repositorio):

1. *Require a pull request before merging*, con al menos 1 aprobación.
2. *Dismiss stale pull request approvals when new commits are pushed*.
3. *Require status checks to pass before merging*: trabajo `calidad-y-pruebas` del CI.
