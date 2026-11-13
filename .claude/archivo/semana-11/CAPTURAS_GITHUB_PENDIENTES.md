# Capturas de GitHub — Semana 11 (actualización al 30/10/2026: v4.0-Inc4)

> **Estado: completadas (30/10/2026).** Las 13 capturas están en `entregables/semana-11/evidencias/github/` y figuran como Figuras 54 a 66 de `Entregable_Semana11_Anemia_Junin.md` (sección 6.5); este archivo conserva la lista y lo que cada una sostiene. Las que superaban 300 KB se cuantizaron a 256 colores; `GH_tablero_t019_t020.png` se redujo además al 80 % de su tamaño.

## Cómo tomarlas

1. Iniciar sesión en GitHub con una cuenta con acceso al repositorio y abrir la URL de la fila. Cuando la URL lleva `#Lx-Ly`, GitHub resalta ese rango: la captura debe mostrar la ruta, el selector de rama y los números de línea.
2. Los números de línea se midieron en la rama `docs/s12-integrador`; `pmv_fastapi/` y `.github/` son idénticos a los de `main` tras la fusión de la PR #8 (`c870a7e`). `coordinacion/TABLERO.md` sí puede diferir entre ramas: comprobar que las filas T-019 y T-020 coincidan y ajustar el rango.
3. Guardar cada PNG en `entregables/semana-11/evidencias/github/` con el nombre de la última columna. Optimizar a 256 colores y menos de 300 KB (por ejemplo, con Pillow: `Image.open(p).convert("RGB").quantize(256).save(p, optimize=True)`). No incluir tokens, correos ni datos personales.
4. Si una página muestra algo distinto de lo esperado (por ejemplo, no existe un tablero de Projects o `main` no tiene reglas de protección), tomar igualmente la captura —la ausencia también es evidencia— y ajustar el texto de la figura y la calificación asociada.

## Lista de capturas

| N.° figura | URL completa | Líneas | Rama | Qué debe verse | PNG de destino |
| --- | --- | --- | --- | --- | --- |
| 54 | https://github.com/woshtsu/ProcesosSoftwareAnemia/pull/8 | — | `main` | La PR #8 en estado Merged (de `feature/inc3-sin-conexion` hacia `main`), la aprobación del revisor woshtsu en la línea de tiempo y el commit de fusión `c870a7e`. **Sostiene el cambio de PQA de Nivel 1 a 2** | `evidencias/github/GH_pr8_conversacion.png` |
| 55 | https://github.com/woshtsu/ProcesosSoftwareAnemia/pull/8/checks | — | `main` | Los checks de la PR #8 (`calidad-y-pruebas` e `imagen`) en verde | `evidencias/github/GH_pr8_checks.png` |
| 56 | https://github.com/woshtsu/ProcesosSoftwareAnemia/actions/workflows/ci.yml?query=branch%3Amain | — | `main` | La ejecución #16 en `main` con estado Success y los tres jobs (`calidad-y-pruebas`, `imagen`, `produccion`) en verde, con su duración | `evidencias/github/GH_actions_run16_main.png` |
| 57 | https://github.com/woshtsu/ProcesosSoftwareAnemia/actions/workflows/ci.yml (abrir la ejecución #16 y el job `produccion`) | — | `main` | El paso «Verificar esquema sin modificar producción y solicitar despliegue» en verde y la línea final «Render aceptó la solicitud del commit probado…» (sin mostrar secretos ni URL del *hook*) | `evidencias/github/GH_actions_run16_produccion.png` |
| 58 | https://github.com/woshtsu/ProcesosSoftwareAnemia/commits/main | — | `main` | El historial de `main` con los commits de código de la PR #8 (`e920820` a `e6886e2`), su fusión (`c870a7e`) y los dos commits directos «add guia S10» y «add guia s12» | `evidencias/github/GH_commits_main.png` |
| 59 | https://github.com/woshtsu/ProcesosSoftwareAnemia/pulls?q=is%3Apr+is%3Aclosed | — | — | Las pull requests #1, #2, #4, #6, #7 y #8 con su estado, autor y quién las fusionó | `evidencias/github/GH_prs_cerradas.png` |
| 60 | https://github.com/woshtsu/ProcesosSoftwareAnemia/projects | — | — | El tablero de GitHub Projects con sus columnas e historias, o la lista vacía si no existe | `evidencias/github/GH_projects.png` |
| 61 | https://github.com/woshtsu/ProcesosSoftwareAnemia/tree/main/.github | — | `main` | El contenido de `.github/`: solo `workflows/`, sin `pull_request_template.md` | `evidencias/github/GH_dir_github_main.png` |
| 62 | https://github.com/woshtsu/ProcesosSoftwareAnemia/blob/main/.github/workflows/ci.yml#L93-L148 | L93-L148 | `main` | El job `produccion`: las consultas SELECT de esquema (L131-L135) sobre `nino`, `asistencia_control`, `evaluacion_hemoglobina` y `v_ultimo_control` (ninguna sobre `visita_domiciliaria`, `operacion_sincronizada`, `conflicto_sincronizacion`, `recordatorio` ni `barrera`) y el mensaje «esto no certifica el despliegue final» (L148) | `evidencias/github/GH_ci_produccion_lineas.png` |
| 63 | https://github.com/woshtsu/ProcesosSoftwareAnemia/blob/main/pmv_fastapi/sonar-project.properties#L2 | L2 | `main` | `sonar.organization=REEMPLAZAR_ORGANIZACION` (SonarCloud sin organización) | `evidencias/github/GH_sonar_organizacion.png` |
| 64 | https://github.com/woshtsu/ProcesosSoftwareAnemia/blob/main/pmv_fastapi/app/web/app.js#L264-L271 | L264-L271 | `main` | DNI (L264), sexo (L267) y celular (L271) del expediente interpolados sin `esc()` (la línea 634 del mismo archivo, con el celular en la tabla de seguimiento, queda fuera del rango) | `evidencias/github/GH_app_js_sin_esc.png` |
| 65 | https://github.com/woshtsu/ProcesosSoftwareAnemia/blob/main/coordinacion/TABLERO.md#L30-L31 | L30-L31 | `main` | Las filas T-019 y T-020 con estado EN REVISIÓN y sus pendientes | `evidencias/github/GH_tablero_t019_t020.png` |
| 66 | https://github.com/woshtsu/ProcesosSoftwareAnemia/settings/branches | — | — | Las reglas de protección de `main` (revisión obligatoria y checks requeridos) o la ausencia de reglas | `evidencias/github/GH_proteccion_main.png` |

## Qué calificación depende de cada captura (resultado)

| Capturas | Afirmación del informe | Resultado al 30/10/2026 |
| --- | --- | --- |
| 54 y 55 | PQA pasa de Nivel 1 a 2 | **No se cumple:** la PR #8 está Merged con 6 checks, pero sin revisión «Approved»; PQA se mantiene en Nivel 1 |
| 56 y 57 | El CI de `main` quedó en verde (ejecución #16) y `produccion` solicitó el despliegue | Confirmado: #16 en verde (3 min 21 s); #6, #8, #9 y #10 en rojo; H7 «Mitigado» y acción 8 «Cumplida» |
| 58 y 59 | Conteo de PR y commits de `main` | 8 PR cerradas (7 fusionadas, la #3 sin fusionar); la PR #8 entró como un solo commit *squash*; 2 commits directos; #6 y #7 se fusionaron con checks en rojo. Conteos de la Tabla 5 (CM) y de H5 ajustados |
| 60 y 65 | Seguimiento de PLAN | Sin GitHub Projects; seguimiento solo en `TABLERO.md` |
| 61 | No existe plantilla de PR | Confirmado |
| 62 | El job `produccion` de `main` verifica solo el esquema 2.0 (H9) | Confirmado en `main` (L131 a L135); la rama de trabajo ya lo amplía (acción 9, «Parcial») |
| 63 | SonarCloud sin organización | Confirmado (`REEMPLAZAR_ORGANIZACION`) |
| 64 | `esc()` ausente en el expediente | Confirmado en L264, L267, L269 y L271 |
| 66 | Protección de `main` | `settings/branches` devuelve 404: **no verificable** |
