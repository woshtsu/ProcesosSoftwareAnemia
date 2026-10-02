# Informe de salida: redactor-informe-integrador, S6-03

- **Agente:** redactor-informe-integrador
- **Fecha:** 2026-10-01
- **Tareas atendidas:** S6-03
- **Estado final:** PARCIAL (informe completo; quedan datos humanos y 7 SVG de `recursos-visuales`)

## Resumen

Se reescribió `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` con el orden, la numeración y los títulos de la consigna (portada y secciones 1 a 6), sobre el PMV oficial `pmv_fastapi/` (FastAPI y PostgreSQL). Flask se menciona solo como antecedente técnico, sin cifras. El resumen tiene 285 palabras. Hay 31 tablas y 35 figuras numeradas de forma continua.

## Archivos creados y modificados

| Acción | Ruta | Nota |
| --- | --- | --- |
| modificado | `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` | Reescritura completa. La versión anterior ya estaba archivada en `archivo/versiones-anteriores/semana-06-integrador/` |
| creado | `entregables/semana-06-integrador/CHECKLIST_CUMPLIMIENTO_S6_INFORME.md` | 31 CUMPLE, 6 PARCIAL y 2 [COMPLETAR] de 39 requisitos |
| modificado | `coordinacion/s6/TABLERO_S6.md` | Solo la fila S6-03: EN REVISIÓN y nota |
| creado | `coordinacion/s6/informes/2026-10-01_redactor-informe-integrador_S6-03.md` | Este informe |

## Verificación realizada

- Resumen: 285 palabras (`wc -w` sobre la sección 1).
- `grep` de `CARGA_CIERRE`, `[PENDIENTE`, `266`, `96,69`, `api/v1`, `Waitress` y "tag pendiente": sin coincidencias. La palabra "Flask" aparece 3 veces, solo como antecedente (resumen, §3.1 y lección 3).
- Matriz de trazabilidad: 8 columnas exactas y 8 filas (5 del PMV y 3 de INC-n).
- Conclusiones: 3. Lecciones: 3. Siguiente incremento: INC-2.
- Enlaces a imágenes: se comprobó que existen todos salvo 7 SVG (ver pendientes).
- Cifras: todas salen de `DATOS_PMV_FASTAPI.md` (incluida la reproducción del §17) y `CONTEXTO_PROCESOS_S1_S5.md`, o de los entregables S1, S2 y S3-4.

## Decisiones de redacción

- C-01: se afirma que el tag existe y que su código es idéntico a `main:pmv_fastapi/`; no se afirma que esté en `main`.
- C-02: el pipeline se cita en `.github/workflows/ci.yml`; se declara que antes estaba en una subcarpeta que GitHub no ejecuta y que no hay evidencia de una ejecución en verde.
- C-04: Ruff como análisis obligatorio; SonarCloud preparado, sin análisis ejecutado.
- C-10: se usó el reparto de S3-4 §10 (13 + 8 puntos).
- Los CP citados son los rangos de los docstrings de las pruebas; no se atribuyó un CP concreto a una prueba individual.
- Desviación registrada: el hito H1 era el 28/09/2026 y las fusiones y el tag son del 30/09/2026 (historial git).
- Las matrices de S3-4 se redactaron originalmente para el prototipo; las tareas T01 a T16 se vincularon con los artefactos equivalentes del PMV.

## Datos humanos faltantes ([COMPLETAR]; para el `inspector-guia` y `PASOS_MANUALES.md`)

1. Fecha de entrega (portada).
2. Docente (portada).
3. Códigos de alumno de los tres integrantes (Tabla 1).
4. Confirmación del mapeo de 4 roles a 3 personas (Tabla 2).
5. Acta de revisión del Incremento 1 (§2.3 y §3.4).
6. Nombre y cargo del Product Owner o usuario que acepta (§2.3, RAE).
7. Horas reales por integrante y sprint (§2.3).
8. Captura o enlace de una ejecución en verde en GitHub Actions (§2.3 y §3.4).
9. Activación de SonarCloud: organización, `SONAR_TOKEN`, análisis y captura (§3.3).
10. Ejecución de staging con Docker Compose y captura de `/api/salud` (§3.4).
11. Duración del video y enlace público opcional (§3.4).
12. Acta o correo de aceptación del usuario final (§3.4).
13. Confirmación de la justificación del cambio de Flask a FastAPI (§3.1 y §5).

## Pendientes y riesgos

- Faltan estos SVG de destino, ya enlazados en el informe: `67_s6_matriz_factores.svg` (VIS-015), `66_s6_adr_nfr.svg` (VIS-014), `59_s6_piramide_pruebas.svg` (VIS-007), `60_s6_cobertura.svg` (VIS-008), `61_s6_carga_p95.svg` (VIS-009), `62_s6_tablero_metricas.svg` (VIS-010) y `63_s6_burnup_inc1.svg` (VIS-011). Hay que repetir la comprobación de enlaces cuando `recursos-visuales` termine.
- La Figura 13 (VIS-011) tiene un pie genérico («avance real… a partir del historial git»). Si `recursos-visuales` entrega «planificado frente a completado por HU» porque todas las fusiones son del mismo día, ajustar el pie. En el historial, las 8 fusiones a `develop` son del 30/09/2026.
- No se creó ninguna VIS-017. VIS-013 (collage) no se usa en el informe: se incrustan las capturas 01 a 08 una por una.
- Las matrices de S3-4 y S5 siguen describiendo el prototipo (decisión S6-11 del usuario).
- Los marcadores `[COMPLETAR]` son visibles: deben resolverse o pasar a pasos manuales antes de exportar.
