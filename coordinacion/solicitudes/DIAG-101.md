# DIAG-101 — WBS del proyecto (Semanas 3-4)

- **Estado:** RESUELTA  <!-- ABIERTA | EN CURSO | RESUELTA | RECHAZADA -->
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-004
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Alta

## Tipo de diagrama

- [ ] BPMN / flujo de proceso (AS-IS / TO-BE, carriles)
- [ ] UML casos de uso
- [ ] UML clases / modelo de dominio
- [ ] UML secuencia
- [ ] UML actividad
- [ ] UML componentes / despliegue
- [ ] C4 (contexto / contenedores / componentes)
- [ ] Modelo de datos (ER)
- [x] Gantt / cronograma / WBS
- [ ] Otro: ____

## Requisito que cubre

- **Guía:** `guias/S3-4_Guia_trabajo_semanas_3_y_4.md` — Actividad 6 (§10): descomposición «Proyecto → Entregables → Incrementos → Épicas/funcionalidades → Historias de usuario → Tareas». Consigna S6 §2.3: «Descomposición del Trabajo (WBS): Épicas ➔ Historias de Usuario ➔ Tareas del Incremento 1».
- **Entregable destino:** `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` — §8.2, Figura 2 (marcador `<!-- DIAG-101 pendiente -->`).

## Contenido requerido

Árbol jerárquico (estilo organigrama WBS, de arriba hacia abajo; PlantUML `@startwbs` es adecuado). Texto exacto:

- **Nivel 1 — P:** «Sistema de detección temprana de anemia infantil — Junín»
  - **Nivel 2 — E1:** «Documentación del proceso (S1-S6)»
  - **Nivel 2 — E3:** «Evidencias de calidad y valor (pruebas, actas, indicadores)»
  - **Nivel 2 — E2:** «Producto de software»
    - **Nivel 3 — INC-1 (PMV):** «Registro nominal validado y expediente digital» — **resaltar (color de énfasis): incremento prioritario**
      - **Épica EP-1.T Habilitadores técnicos**
        - «Arquitectura y persistencia»: T01 ADR-001/002; T02 Esquema y migración 001
        - «Entorno de calidad»: T03 pytest, cobertura ≥ 80 %, ruff, prueba de arquitectura
        - «Demostración»: T16 Datos sintéticos y demostración local (Waitress)
      - **Épica EP-1.B Validación y clasificación**
        - «HIST-1.3 (HU-03) Validar datos y clasificar Hb»: T04 Normativa JSON + proveedor; T05 Validadores; T06 Clasificador; T07 Pruebas de valores límite
      - **Épica EP-1.A Registro y expediente**
        - «HIST-1.1 (HU-01) Registrar niño»: T08 Caso de uso + repositorios + transacción; T09 `POST /api/v1/ninos` + OpenAPI; T10 Formulario web; T11 Pruebas de persistencia y API
        - «HIST-1.2 (HU-02) Expediente y dosajes»: T12 Consultar, actualizar, agregar dosaje
      - **Épica EP-1.C Seguimiento y reporte**
        - «HIST-1.4 (HU-04) Listado en seguimiento»: T13 Listado 6-59 meses, orden por severidad, filtros
        - «HIST-1.5 (HU-05) Reporte del periodo»: T14 Reporte e indicador de aceptación
        - «Pruebas Sprint 2»: T15 Pruebas de integración API/persistencia
    - **Nivel 3 — INC-2:** «Agenda automática y alertas» → HIST-2.1 Generar agenda; HIST-2.2 Controles vencidos; HIST-2.3 Agenda del personal; HIST-2.4 Registrar asistencia
    - **Nivel 3 — INC-3:** «Sin conexión y sincronización» → HIST-3.1 Registrar sin conexión; HIST-3.2 Sincronizar; HIST-3.3 Resolver conflictos; HIST-3.4 Ver pendientes
    - **Nivel 3 — INC-4:** «WhatsApp y barreras» → HIST-4.1 Recordatorio; HIST-4.2 Confirmación; HIST-4.3 Barreras; HIST-4.4 Alertar barreras críticas
    - **Nivel 3 — INC-5:** «Modelo predictivo» → HIST-5.1 Lista priorizada; HIST-5.2 Factores de riesgo; HIST-5.3 Validación clínica; HIST-5.4 Reentrenar
    - **Nivel 3 — INC-6:** «Tablero territorial» → HIST-6.1 Cobertura por posta; HIST-6.2 Distribución por zona; HIST-6.3 Exportar para MINSA; HIST-6.4 Comparar periodos
    - **Nivel 3 — Backlog técnico:** BT-01 CI GitHub Actions; BT-02 SonarCloud; BT-03 Pruebas E2E y carga; BT-05 PostgreSQL + sincronización; BT-06 Cuentas y roles; BT-07 Despliegue en posta; BT-08 Medición tiempo de registro; BT-09 Bandas de altitud no verificadas

Si el árbol resulta muy ancho para A4, se admite orientación horizontal (izquierda → derecha) o mostrar INC-2..INC-6 colapsados con sus HIST en una sola caja por incremento.

## Fuentes de verdad

- `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` Tablas 11, 12 y 13.

## Nombre de archivo sugerido

`31_s34_wbs_proyecto` → `diagramas/src/31_s34_wbs_proyecto.puml`, `diagramas/png/31_s34_wbs_proyecto.png`, `diagramas/svg/31_s34_wbs_proyecto.svg`

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4
- [ ] Texto en español, sin tildes rotas
- [ ] Los seis niveles de la guía están presentes y rotulados (Proyecto, Entregable, Incremento, Épica, Historia, Tarea)
- [ ] INC-1 resaltado y con las tareas T01-T16; coherente con las Tablas 11-13

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** 2026-10-01
- **Resultado:** RESUELTA (cierre administrativo del sincronizador, 2026-10-01: existen fuente `diagramas/src/31_s34_wbs_proyecto.puml`, `diagramas/png/31_s34_wbs_proyecto.png` y `diagramas/svg/31_s34_wbs_proyecto.svg`; la verificación del contenido frente al entregable corresponde a revisor-documental / inspector-guia)
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 2. Estructura de descomposición del trabajo (WBS) del proyecto: entregables, incrementos, épicas, historias y tareas del Incremento 1 (elaboración propia).](../../diagramas/svg/31_s34_wbs_proyecto.svg)`
- **Notas:**
