# Checklist de cumplimiento: Informe Integrador S6 (bloques B y C)

- **Consigna:** `guias/S6.CONSIGNA DE TRABAJO E INSTRUMENTO DE EVALUACIÓN INTEGRADOR.md`, §II.
- **Requisitos:** `coordinacion/s6/REQUISITOS_S6.md` (R-06 a R-39 y los criterios C1 a C4 de la rúbrica, R-81 a R-84).
- **Entregable:** `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md`.
- **Redactor:** redactor-informe-integrador (tarea S6-03).
- **Fecha:** 2026-10-01.
- **Leyenda:** CUMPLE = contenido completo y verificable; PARCIAL = falta evidencia o un recurso externo; [COMPLETAR] = depende de un dato humano que no se puede inventar. La decisión final es del `inspector-guia`.
- **Resultado:** 31 CUMPLE, 6 PARCIAL, 2 [COMPLETAR] de 39 requisitos evaluados.

## Matriz de requisitos

| ID | Requisito (resumen) | Estado | Evidencia (sección del informe) | Observación |
| --- | --- | --- | --- | --- |
| R-06 | Título y subtítulo textuales | CUMPLE | Portada | Textuales de la consigna |
| R-07 | Carrera, asignatura y proyecto | CUMPLE | Portada | Nombre de la solución según `pmv_fastapi/README.md` |
| R-08 | Integrantes con código y rol; mapeo de 4 roles a 3 personas | [COMPLETAR] | Portada, Tablas 1 y 2 | Rol unificado a «Ingeniera de Desarrollo y Prototipado» (coincide con el README). Faltan los códigos de alumno y la confirmación del mapeo de roles |
| R-09 | Fecha de entrega y docente | [COMPLETAR] | Portada | Dato del equipo |
| R-10 | Resumen de 300 palabras como máximo con los cinco elementos | CUMPLE | §1 | 285 palabras (`wc -w` sobre la sección) |
| R-11 | Diagnóstico y matriz de actores y necesidades | CUMPLE | §2.1, Tabla 3 | Seis actores |
| R-12 | AS-IS y al menos cinco brechas | CUMPLE | §2.1, Figuras 1 y 2, Tabla 4 | Seis brechas B1 a B6 |
| R-13 | TO-BE y matriz de intervención del software | CUMPLE | §2.1, Figura 3, Tabla 5 | Estado de cada mejora en el PMV |
| R-14 | Cadena de valor e indicadores de los cuatro tipos | CUMPLE | §2.1, Figura 4, Tabla 6 | Proceso, producto, resultado y valor, con su estado de medición |
| R-15 | Matriz de factores con los cinco nombres exigidos | CUMPLE | §2.2, Tabla 7, Figura 5 | Incertidumbre, Complejidad, Riesgo, Integración y Datos/IA |
| R-16 | Matriz de comparación con Cascada, Incremental, Scrum, DevOps y MLOps | CUMPLE | §2.2, Tabla 8 | Siete enfoques con totales |
| R-17 | Justificación y tailoring híbrido | CUMPLE | §2.2, Tabla 9 y texto | Matriz ponderada de 4,75, 3,85 y 2,95 |
| R-18 | Representación gráfica del modelo aplicado | CUMPLE | §2.2, Figuras 6 y 7 | VIS-002 y `15_s2_modelo_proceso_aplicado.svg` |
| R-19 | Matriz de actividades con entradas, productos y salidas | CUMPLE | §2.3, Tabla 10, Figura 8 | Artefactos del PMV |
| R-20 | Matriz RAE | CUMPLE | §2.3, Tabla 11 | La aprobación por el Product Owner es un rol previsto; nombre pendiente |
| R-21 | DoD por actividad | CUMPLE | §2.3, Tabla 12 | Evidencia del PMV por criterio |
| R-22 | WBS: épicas, historias y tareas | CUMPLE | §2.3, Figura 9, Tabla 13 | HU-01 a HU-05 igual a HIST-1.1 a 1.5 |
| R-23 | Estimación, priorización valor/riesgo y plan | CUMPLE | §2.3, Tablas 14 a 16, Figuras 10 y 11 | 21 puntos, 113 horas-persona estimadas; horas reales no registradas |
| R-24 | Seguimiento, control de desviaciones e indicadores de avance | PARCIAL | §2.3, Tablas 17 y 18, Figuras 12 a 14 | Texto y pie de la Fig. 13 corregidos (S6-18): planificado S3-4 frente a completado 21/21 SP, sin burnup real; pie de la Fig. 14 con 6 barras = 21 SP. Figuras 62 y 63 se regeneran aparte (E-02 a E-04); faltan horas reales (paso 4) |
| R-25 | Clasificación principales, soporte y organizacionales | CUMPLE | §3.1, Tabla 19 | Con evidencia del PMV |
| R-26 | Matriz de tailoring | CUMPLE | §3.1, Tabla 20 | Actualizada a FastAPI, PWA, PostgreSQL, Docker y CI |
| R-27 | ADR con atributos de calidad | CUMPLE | §3.2, Tabla 21, Figura 15 | ADR-001 a ADR-006; falta el SVG de VIS-014 |
| R-28 | C4 niveles 1, 2 y 3 | CUMPLE | §3.2, Figuras 16 a 18 | Del PMV FastAPI (VIS-003) |
| R-29 | Modelo de datos y contratos de API | CUMPLE | §3.2, Figura 21, Tabla 22 | Esquema PostgreSQL, nueve endpoints y `openapi.json` |
| R-30 | Pirámide de pruebas con los cuatro niveles y casos | CUMPLE | §3.3, Tabla 23, Figura 22 | 62, 11, 4 y 1 escenario de carga que no se suma; pie de la Fig. 22 corregido (la figura 59 se regenera aparte, E-01) |
| R-31 | Registro de ejecución y cobertura | CUMPLE | §3.3, Tablas 24 y 25 | 99,07 %; 77 declaradas (62+11+4) y 73 reproducidas; E2E, PostgreSQL y carga «según el tag; no reproducido el 01/10/2026»; la carga no cuenta como prueba. Pasar a «Reproducido» tras PASOS_MANUALES paso 11 |
| R-32 | Análisis estático y gestión de defectos | PARCIAL | §3.3, Tabla 27 | Ruff y defectos completos; SonarCloud preparado pero sin análisis ejecutado (C-04) |
| R-33 | Arquitectura del entorno de despliegue | PARCIAL | §3.4, Tabla 28, Figura 25 | Staging local con Docker Compose; sin nube y sin evidencia de ejecución en vivo ni de CI en verde |
| R-34 | Evidencia del incremento funcional | CUMPLE | §3.4, Tabla 29, Figuras 26 a 33 | Ocho capturas y `demo_pmv.mp4`; falta el acta de aceptación |
| R-35 | Matriz de trazabilidad de 8 columnas | CUMPLE | §4, Tabla 30, Figura 34 | Ocho filas; las filas 6 a 8 son INC-n |
| R-36 | Tres conclusiones técnicas | CUMPLE | §5 | Exactamente tres |
| R-37 | Tres lecciones aprendidas | CUMPLE | §5 | Exactamente tres |
| R-38 | Enlace al repositorio y al tag `v1.0-PMV` | CUMPLE | §6, Tabla 31 y nota | Commit 9ce90c3 con la nota C-01; no se afirma que esté en `main` |
| R-39 | README con compilación, despliegue y scripts de BD | CUMPLE | §6, Tabla 31 | `pmv_fastapi/README.md`, `db/01_esquema_postgresql.sql` y `scripts/` |
| R-81 | C1: fundamentación del proceso y modelo | CUMPLE | §2.1 y §2.2 | AS-IS, TO-BE, brechas, indicadores, justificación y tailoring |
| R-82 | C2: actividades y planificación | PARCIAL | §2.3 | Falta el registro de horas reales y el acta de revisión |
| R-83 | C3: categorización, arquitectura y pruebas | PARCIAL | §3.1 a §3.4 | Sonar sin ejecutar; despliegue solo local |
| R-84 | C4: trazabilidad y medición de valor | PARCIAL | §4 y §2.3 (tablero) | Valor medido solo en términos técnicos y con datos sintéticos; falta el SVG de VIS-010 |
| R-89 | El informe vale 8 puntos (C1 a C4) | CUMPLE | Todo el informe | Sin acción propia; referencia de la rúbrica |

## Pendientes con [COMPLETAR] en el informe

| N.° | Pendiente | Sección |
| --- | --- | --- |
| 1 | Fecha de entrega (paso 1) | Portada |
| 2 | Nombre del docente | Portada |
| 3 | Tres códigos de alumno | Portada, Tabla 1 |
| 4 | Confirmación del mapeo de roles | Portada, Tabla 2 |
| 5 | Acta de revisión del Incremento 1 (revisión del sprint) | §2.3 (actividades y DoD) y §3.4 |
| 6 | Nombre y cargo del Product Owner o usuario que acepta | §2.3 (RAE) |
| 7 | Horas reales por integrante y sprint | §2.3 |
| 8 | Captura o enlace de una ejecución en verde en GitHub Actions | §2.3 (DoD) y §3.4 |
| 9 | Activación de SonarCloud (organización, `SONAR_TOKEN`, análisis y captura) | §3.3 |
| 10 | Ejecución de staging con Docker Compose y captura de `/api/salud` | §3.4 |
| 11 | Duración del video y enlace público opcional | §3.4 |
| 12 | Acta o correo de aceptación del usuario | §3.4 |
| 13 | Confirmación de la justificación del cambio de Flask a FastAPI | §3.1 y §5 |

## Figuras que dependen de `recursos-visuales`

Al cierre de esta redacción faltaban estos SVG de destino (el informe ya los enlaza): `67_s6_matriz_factores.svg` (VIS-015), `66_s6_adr_nfr.svg` (VIS-014), `59_s6_piramide_pruebas.svg` (VIS-007), `60_s6_cobertura.svg` (VIS-008), `61_s6_carga_p95.svg` (VIS-009), `62_s6_tablero_metricas.svg` (VIS-010) y `63_s6_burnup_inc1.svg` (VIS-011). VIS-013 (collage) no se usa en el informe; las capturas se incrustan una por una.
