# Curso: Procesos de Software — 2026-20

**Ejes 3 y 4: Actividades del proceso de software · Planificación y seguimiento de proyectos**

## Entregable Semanas 3 y 4 — Actividades, planificación y seguimiento del proceso

**Proyecto:** Sistema Inteligente para Detección Temprana de Anemia Infantil en Zonas Rurales de Junín

## Equipo de proyecto

| Integrante | Rol en el proyecto |
| :---- | :---- |
| Porras Veli Ricardo | Ingeniero de Proceso |
| Auqui Huincho Tania | Ingeniero de Desarrollo y Prototipado |
| Huamani Rodriguez Jean Piero | Ingeniero de Calidad y Mejora del Proceso |

---

# 0. Punto de partida: continuidad desde las Guías 1 y 2

La Guía 1 estableció el problema organizacional, los actores, el proceso AS-IS, las brechas, el proceso TO-BE, la intervención del software y los indicadores de valor. La Guía 2 derivó de ese TO-BE las características del proyecto, comparó modelos, y seleccionó el **modelo iterativo-incremental gestionado con Scrum, con prácticas DevOps y MLOps**.

Esta guía convierte ese modelo en un **proceso ejecutable**: actividades concretas, secuencia, responsables, productos de trabajo, planificación en 8 sprints, mecanismos de seguimiento e indicadores que permitan controlar la entrega incremental de valor.

**Cadena de derivación completa:**

```
Problema organizacional (anemia infantil en Junín)
  ↓ Guía 1
Proceso TO-BE con 6 puntos de intervención del software
  ↓ Guía 2
Modelo iterativo-incremental + Scrum + DevOps + MLOps
  ↓ Esta guía
Actividades → Secuencia → Responsables → Productos de trabajo
  ↓
Planificación (8 sprints × 2 semanas) → Ejecución → Seguimiento
  ↓
Incrementos funcionales → Resultados → Valor organizacional
```

---

# 1. Características del proyecto (resumen desde Guía 2)

| Factor | Nivel | Relevancia para esta guía |
| :---- | :---- | :---- |
| Incertidumbre de requisitos | Alto | Las actividades de requisitos se repiten en cada sprint con refinamiento progresivo |
| Complejidad técnica | Alto | Las actividades de diseño e implementación requieren spikes técnicos dedicados |
| Riesgo tecnológico | Alto | Pruebas de sincronización offline son actividad obligatoria en cada sprint |
| Necesidad de retroalimentación | Alto | Revisión formal con personal de salud al final de cada sprint es actividad crítica |
| Necesidad de automatización | Alto | Pipeline CI/CD como actividad de infraestructura en Sprint 1; MLOps desde Sprint 5 |
| Dependencia de datos | Alto | Validación y limpieza de datos históricos del HIS como actividad previa al incremento 5 |

**Las tres características determinantes** siguen siendo las establecidas en la Guía 2:
1. Incertidumbre del componente de IA → requiere actividades de experimentación versionadas
2. Riesgo del entorno rural (conectividad intermitente) → requiere actividades de prueba offline en cada sprint
3. Necesidad de validación con personal de salud → la revisión de sprint es una actividad no negociable

---

# 2. Modelo de proceso seleccionado (desde Guía 2)

| Nivel | Elemento | Función |
| :---- | :---- | :---- |
| Modelo de ciclo de vida | Iterativo e incremental | Base del proceso: 8 sprints de 2 semanas, cada uno produce un incremento funcional |
| Marco de gestión | Scrum | Organiza la iteración: backlog, sprint planning, daily, review y retrospectiva |
| Prácticas de ingeniería | DevOps | Automatizan build, pruebas (incluida offline) y despliegue |
| Prácticas de datos y modelo | MLOps | Gobiernan el ciclo del modelo predictivo desde el Sprint 5 |

> **Nota**: El modelo de ciclo de vida determina la secuencia y naturaleza de las actividades. Las actividades no son una lista genérica; derivan directamente de las necesidades del proyecto y del modelo seleccionado.

---

# 3. Actividades del proceso (Actividad 1 de la guía)

Las actividades se clasifican en **actividades de cada sprint** (se ejecutan en todos los ciclos) y **actividades específicas por incremento**.

## 3.1 Actividades de cada sprint (ciclo repetible)

| Actividad | Propósito | Entrada | Producto de trabajo | Salida |
| :---- | :---- | :---- | :---- | :---- |
| Sprint Planning | Seleccionar y desglosar las historias del incremento | Backlog priorizado, velocidad del equipo | Sprint Backlog con criterios de aceptación | Plan del sprint en GitHub Projects |
| Refinamiento de requisitos | Detallar, estimar y aceptar historias de usuario | Épicas del Product Backlog | Historias de usuario con criterios INVEST | Backlog refinado |
| Análisis y diseño | Definir la solución técnica del sprint | Historias aceptadas, arquitectura base | Diagrama de flujo del incremento, modelo de datos delta | Diseño revisado por el equipo |
| Implementación | Desarrollar la funcionalidad planificada | Diseño del sprint | Código fuente en repositorio | Pull request aprobado |
| Pruebas unitarias e integración | Verificar comportamiento del código | Código implementado, suite de pruebas | Reporte de pruebas, cobertura | Build verde en CI/CD |
| Prueba de sincronización offline | Verificar registro y sincronización sin conexión | Módulo offline implementado | Reporte de prueba offline | Confirmación de robustez ante desconexión |
| Code review y análisis estático | Controlar calidad del código | Pull request | Hallazgos de SonarCloud | Código aprobado sin deuda crítica |
| Integración continua (CI) | Construir, probar y empaquetar automáticamente | Código integrado | Artefacto de build, reportes CI | Pipeline verde o acción correctiva |
| Revisión del sprint (Review) | Validar el incremento con el personal de salud | Incremento funcional | Acta de revisión, retroalimentación registrada | Backlog actualizado según feedback |
| Retrospectiva | Mejorar el proceso del equipo | Métricas del sprint, observaciones | Plan de mejora del siguiente sprint | Ajustes al proceso documentados |
| Actualización del plan | Reestimar y replanificar si hubo desviaciones | Burndown, métricas de velocidad | Plan actualizado | Backlog y cronograma actualizados |

## 3.2 Actividades específicas por fase

| Actividad | Sprint(s) | Propósito | Producto |
| :---- | :---- | :---- | :---- |
| Definición de arquitectura base | 1 | Establecer la arquitectura del sistema para todos los incrementos | Documento de arquitectura, diagrama de componentes |
| Configuración de pipeline CI/CD | 1 | Automatizar el proceso de build, prueba y despliegue desde el inicio | Pipeline operativo en GitHub Actions |
| Diseño de esquema de base de datos | 1 | Modelar el esquema inicial de PostgreSQL y SQLite local | Modelo entidad-relación (ER) |
| Configuración del ambiente offline | 2-3 | Implementar SQLite local y mecanismo de sincronización | Módulo offline funcional |
| Integración con API de WhatsApp | 4 | Conectar notificaciones al servicio externo | Módulo de notificaciones integrado |
| Validación y limpieza de datos HIS | 4-5 | Preparar datos históricos para el entrenamiento del modelo | Dataset limpio y versionado en MLflow |
| Experimentación y selección de algoritmo | 5 | Comparar Random Forest vs. Gradient Boosting sobre datos reales | Experimentos versionados, algoritmo seleccionado |
| Entrenamiento y evaluación del modelo | 5 | Entrenar, validar y registrar el modelo predictivo | Artefacto del modelo en MLflow, reporte de precisión |
| Pipeline MLOps | 5-6 | Automatizar el ciclo de datos, entrenamiento, publicación y monitoreo | Pipeline MLOps operativo |
| Monitoreo y reentrenamiento | 6+ | Detectar degradación del modelo y reentrenar | Modelo actualizado, reporte de monitoreo por zona |
| Despliegue a posta piloto | Fin de cada incremento | Entregar el software al ambiente de producción de la posta seleccionada | Versión ejecutable en producción |
| Capacitación incremental | Fin de cada incremento | Habilitar al personal para usar la nueva funcionalidad | Material de capacitación, sesión ejecutada |

## 3.3 Preguntas orientadoras respondidas

1. **¿Qué actividades son indispensables?** Sprint Planning, implementación, pruebas (incluida offline), revisión con el usuario y despliegue. Sin ellas no hay entrega funcional ni validación.
2. **¿Qué actividades están relacionadas con los riesgos principales?** La prueba de sincronización offline (riesgo de conectividad), la validación de datos HIS (riesgo de calidad de datos), y la revisión de sprint (riesgo de baja adopción).
3. **¿Qué actividades generan evidencia de calidad?** Code review + SonarCloud, pruebas unitarias/integración, reporte de prueba offline, y la revisión de sprint con acta firmada.
4. **¿Qué actividades se repiten en cada incremento?** Todas las del ciclo repetible (sección 3.1).
5. **¿Qué actividades podrían automatizarse?** Build, pruebas unitarias, análisis estático (DevOps); ingesta de datos, entrenamiento, publicación del modelo y monitoreo (MLOps).

---

# 4. Organización y flujo de actividades (Actividad 2 de la guía)

El flujo específico del proyecto combina el ciclo Scrum con el subciclo MLOps, adaptado al contexto de salud rural:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CICLO PRINCIPAL (cada Sprint)                     │
│                                                                       │
│  TO-BE / Backlog ──► Sprint Planning ──► Refinamiento de Requisitos  │
│                                ↓                                      │
│                        Análisis y Diseño                              │
│                                ↓                                      │
│                       Implementación ◄──────────────────────┐        │
│                                ↓                            │        │
│                  Pruebas Unitarias + Integración            │        │
│                                ↓                            │        │
│                 Prueba Sincronización Offline                │        │
│                                ↓                            │        │
│                  Code Review + SonarCloud                   │        │
│                                ↓                            │        │
│              CI/CD ──► Build ──► Test ──► Package           │        │
│                                ↓                            │        │
│             Despliegue a Posta Piloto                        │        │
│                                ↓                            │        │
│      Revisión con Personal de Salud ─── NO aprobado ────────┘        │
│                ↓ APROBADO                                             │
│         Medición de indicadores                                       │
│                ↓                                                      │
│           Retrospectiva ──► Plan de mejora                            │
│                ↓                                                      │
│        Siguiente Incremento                                           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│       SUBCICLO MLOPS (activo desde Sprint 5)        │
│                                                     │
│  Datos HIS ──► Limpieza ──► Versionado (MLflow)    │
│                    ↓                                │
│       Experimentación (RF vs. GBM)                 │
│                    ↓                                │
│    Entrenamiento ──► Evaluación ──► Registro        │
│                    ↓                                │
│   Publicación del artefacto ──► Pipeline CI/CD      │
│                    ↓                                │
│         Monitoreo desempeño por zona               │
│                    ↓                                │
│   ¿Precisión < umbral? ──► Reentrenamiento         │
└─────────────────────────────────────────────────────┘
```

> **Pregunta orientadora respondida:** Las actividades reflejan el modelo iterativo-incremental + Scrum + DevOps + MLOps seleccionado. No son un proceso tradicional secuencial: todas las actividades de desarrollo se repiten en cada sprint, la revisión con el usuario es obligatoria, y el subciclo MLOps opera en paralelo desde el sprint 5.

> **📌 UML — Diagrama de Actividad (Flujo del proceso):** Este flujo debe representarse como un **Diagrama de Actividad UML** en PowerDesigner, mostrando el swimlane del equipo de desarrollo, del personal de salud (revisión) y del sistema MLOps. Ver instrucciones en Sección 13.

---

# 5. Responsabilidades (Actividad 3 de la guía)

| Actividad | Responsable | Participantes | Revisor/Aprobador | Evidencia |
| :---- | :---- | :---- | :---- | :---- |
| Sprint Planning | Porras V. (Ing. Proceso) | Todo el equipo | Product Owner (representante posta) | Sprint Backlog en GitHub Projects |
| Refinamiento de requisitos | Porras V. | Auqui H., personal de salud | Porras V. | Historias de usuario aceptadas |
| Análisis y diseño | Auqui H. (Ing. Desarrollo) | Porras V., Huamani R. | Huamani R. | Diagrama de diseño revisado |
| Implementación | Auqui H. | Auqui H. | Huamani R. (code review) | Pull request aprobado |
| Pruebas unitarias e integración | Huamani R. (Ing. Calidad) | Auqui H. | Huamani R. | Reporte de pruebas, cobertura ≥ 80 % |
| Prueba sincronización offline | Huamani R. | Auqui H. | Porras V. | Reporte de prueba offline |
| Code review + análisis estático | Huamani R. | Todo el equipo | Porras V. | Reporte SonarCloud sin issues críticos |
| CI/CD (build + test + deploy) | Auqui H. | GitHub Actions (automatizado) | Huamani R. | Pipeline verde, log de despliegue |
| Revisión del sprint | Porras V. | Todo el equipo + personal de salud | Personal de salud / microred | Acta de revisión firmada |
| Retrospectiva | Porras V. | Todo el equipo | Porras V. | Plan de mejora documentado |
| Experimentación y modelo (MLOps) | Auqui H. | Huamani R. | Porras V. | Experimentos en MLflow, reporte de precisión |
| Monitoreo del modelo | Huamani R. | Auqui H. | Porras V. | Reporte de desempeño por zona |
| Capacitación incremental | Porras V. | Auqui H. | Personal de salud | Lista de asistencia, material entregado |

> **Pregunta orientadora respondida:** Si una actividad no tiene responsable definido, nadie la asume, la evidencia no se genera y el criterio de terminación nunca se verifica. En proyectos distribuidos en zonas rurales esto es especialmente crítico: la prueba de sincronización offline sin responsable puede pasar desapercibida hasta el despliegue real.

---

# 6. Productos de trabajo y criterios de terminación (Actividad 4 de la guía)

| Actividad | Producto de trabajo | Criterio de terminación | Evidencia objetiva |
| :---- | :---- | :---- | :---- |
| Refinamiento de requisitos | Historias de usuario (formato: Como… quiero… para…) | Todas las historias del sprint tienen criterios de aceptación definidos y el equipo las estimó | Historias en estado "Ready" en GitHub Projects |
| Análisis y diseño | Diagrama de diseño del incremento, modelo de datos delta | Diseño revisado por los tres integrantes y sin observaciones pendientes | Comentarios resueltos en el PR de diseño |
| Implementación | Código fuente en rama de feature | Funcionalidad implementada, sin errores de compilación, PR aprobado por al menos un revisor | PR merged a la rama principal |
| Pruebas unitarias | Suite de pruebas con Pytest | Cobertura ≥ 80 % del código nuevo; todos los casos críticos cubiertos; 0 pruebas fallidas | Reporte de cobertura en CI/CD |
| Prueba de sincronización offline | Reporte de prueba offline (escenario: 15 min sin conexión, reconexión, verificación de integridad) | Todos los registros capturados sin conexión se sincronizaron sin duplicados ni pérdida | Reporte firmado por Huamani R. |
| Code review + SonarCloud | Reporte de análisis estático | 0 issues de severidad Blocker o Critical; deuda técnica < 1 día | Dashboard SonarCloud |
| Integración continua | Build pasado, artefacto generado | Pipeline completo sin errores; todos los stages verdes | Log de GitHub Actions |
| Despliegue a posta piloto | Versión ejecutable instalada en dispositivo piloto | Sistema accesible y funcional en el dispositivo de la posta; se ejecutó el smoke test | Captura de pantalla del smoke test |
| Revisión del sprint | Acta de revisión con retroalimentación del personal de salud | Personal de salud aceptó formalmente el incremento o registró observaciones a atender | Acta firmada con fecha |
| Retrospectiva | Plan de mejora del siguiente sprint | Al menos dos mejoras concretas identificadas y asignadas a un responsable | Documento de retrospectiva en repositorio |
| Experimentación (MLops) | Experimentos registrados en MLflow | Al menos dos algoritmos comparados; métricas de precisión, recall y F1 registradas por experimento | Dashboard MLflow con ≥ 2 experimentos |
| Modelo predictivo | Artefacto del modelo registrado | Precisión ≥ umbral definido con personal clínico; validación cruzada ejecutada | Reporte de evaluación en MLflow |

> **Pregunta clave respondida:** La terminación se demuestra con **evidencia objetiva** (reportes, capturas, actas, dashboards), no con la afirmación verbal del equipo. En un contexto clínico, la prueba de sincronización offline debe documentarse con el escenario exacto ejecutado y el resultado verificado.

---

# 7. Relación de actividades con incrementos de software (Actividad 5 de la guía)

| Inc. | Funcionalidad | Actividades principales | Resultado esperado | Valor generado | Indicador |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | Registro nominal validado y expediente digital | Requisitos, diseño arquitectónico, modelo ER, implementación del registro, pruebas unitarias, prueba offline, CI/CD, despliegue piloto, revisión | Registro único y confiable de cada niño en zona sin conexión | Elimina el triple registro manual y sus errores | Registros sin error crítico ÷ evaluados × 100 |
| 2 | Agenda automática según NTS 134 y alertas internas | Refinamiento de agenda, implementación de reglas NTS, prueba de generación automática, revisión con enfermera | Controles programados y vencidos visibles en la aplicación | Mayor oportunidad en la atención | Cobertura oportuna de controles (%) |
| 3 | Funcionamiento offline y sincronización robusta | Diseño del protocolo de sincronización, implementación SQLite + resolución de conflictos, prueba extendida offline, revisión en zona rural | Registro sin pérdida de datos en zonas sin cobertura | Continuidad del servicio en el ámbito rural | Registros sincronizados ÷ pendientes × 100 |
| 4 | Notificaciones por WhatsApp y reporte de barreras | Integración API WhatsApp Business, módulo de barreras, prueba de entrega de mensajes, revisión con familias | Familias informadas y barreras reportadas a tiempo | Menor pérdida de seguimiento | Mensajes entregados y leídos ÷ enviados × 100 |
| 5 | Modelo predictivo y priorización de la agenda | Validación datos HIS, experimentación MLflow, entrenamiento, evaluación con personal clínico, integración modelo-agenda, pipeline MLOps | Casos de alto riesgo priorizados en la agenda | Uso más eficiente del personal disponible | Precisión = casos confirmados ÷ señalados × 100 |
| 6 | Tablero de gestión territorial e indicadores | Diseño del tablero, implementación de reportes por microred, integración con datos reales, revisión con microred y MINSA | Supervisión en tiempo real por microred y MINSA | Decisiones territoriales basadas en evidencia | Indicadores de cobertura y resultado actualizados |

---

# 8. Descomposición del proyecto (Actividad 6 de la guía)

## 8.1 Estructura del trabajo (WBS conceptual)

```
SISTEMA DE DETECCIÓN TEMPRANA DE ANEMIA — JUNÍN
├── INC-1: Registro nominal y expediente digital
│   ├── HIST-1.1: Registrar nuevo niño en el sistema
│   ├── HIST-1.2: Consultar y actualizar expediente
│   ├── HIST-1.3: Validar datos requeridos (hemoglobina, edad, zona)
│   ├── HIST-1.4: Listar niños en seguimiento activo
│   └── HIST-1.5: Generar reporte de registros del periodo
├── INC-2: Agenda automática y alertas
│   ├── HIST-2.1: Generar agenda de controles según NTS 134
│   ├── HIST-2.2: Identificar controles vencidos
│   ├── HIST-2.3: Visualizar agenda del personal de salud
│   └── HIST-2.4: Registrar asistencia a control
├── INC-3: Modo offline y sincronización
│   ├── HIST-3.1: Registrar datos sin conexión a internet
│   ├── HIST-3.2: Sincronizar datos al recuperar conexión
│   ├── HIST-3.3: Detectar y resolver conflictos de sincronización
│   └── HIST-3.4: Ver estado de sincronización pendiente
├── INC-4: Notificaciones WhatsApp y barreras
│   ├── HIST-4.1: Enviar recordatorio de control a la familia
│   ├── HIST-4.2: Registrar respuesta de confirmación
│   ├── HIST-4.3: Registrar barreras reportadas por la familia
│   └── HIST-4.4: Alertar al personal sobre barreras críticas
├── INC-5: Modelo predictivo y priorización
│   ├── HIST-5.1: Mostrar lista de niños priorizados por riesgo
│   ├── HIST-5.2: Visualizar factores de riesgo de un niño
│   ├── HIST-5.3: Validar predicción con criterio clínico
│   └── HIST-5.4: Reentrenar modelo con nuevos datos
└── INC-6: Tablero de gestión territorial
    ├── HIST-6.1: Ver indicadores de cobertura por posta
    ├── HIST-6.2: Ver distribución de riesgo por zona
    ├── HIST-6.3: Exportar reporte para MINSA
    └── HIST-6.4: Comparar indicadores entre periodos
```

## 8.2 Descomposición en tareas del Incremento 1 (detallado)

| Incremento | Funcionalidad | Historia/elemento | Tarea | Prioridad |
| :---- | :---- | :---- | :---- | :---- |
| 1 | Registro nominal | HIST-1.1: Registrar nuevo niño | T1: Diseñar formulario de registro | Alta |
| 1 | Registro nominal | HIST-1.1: Registrar nuevo niño | T2: Implementar API de registro (backend) | Alta |
| 1 | Registro nominal | HIST-1.1: Registrar nuevo niño | T3: Implementar interfaz de registro (frontend) | Alta |
| 1 | Registro nominal | HIST-1.1: Registrar nuevo niño | T4: Prueba unitaria de validación de datos | Alta |
| 1 | Registro nominal | HIST-1.2: Consultar expediente | T5: Implementar búsqueda y visualización | Media |
| 1 | Registro nominal | HIST-1.3: Validar datos | T6: Reglas de validación (hemoglobina, edad, zona) | Alta |
| 1 | Arquitectura | Infraestructura base | T7: Configurar PostgreSQL + SQLite local | Alta |
| 1 | Arquitectura | Infraestructura base | T8: Configurar pipeline GitHub Actions | Alta |
| 1 | Arquitectura | Infraestructura base | T9: Configurar SonarCloud | Media |
| 1 | Pruebas | Suite inicial | T10: Configurar Pytest + cobertura | Alta |

---

# 9. Priorización del trabajo (Actividad 7 de la guía)

Se utiliza una **Matriz de Priorización Ponderada** con los siguientes criterios y pesos:

- **Valor para el usuario/organización (30 %)**: impacto directo en el proceso de atención
- **Reducción de riesgo (25 %)**: el incremento mitiga uno de los tres riesgos determinantes
- **Dependencia técnica (20 %)**: otros incrementos dependen de este
- **Complejidad de implementación (15 %)**: inverso; más complejo = menor prioridad en criterio puro
- **Factibilidad de validación (10 %)**: facilidad de obtener retroalimentación del usuario

Escala: 1 = muy bajo · 2 = bajo · 3 = medio · 4 = alto · 5 = muy alto

| Funcionalidad | Valor (30%) | Riesgo (25%) | Dependencia (20%) | Complejidad inv. (15%) | Validación (10%) | **Total ponderado** | Prioridad |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| INC-1 Registro nominal | 5 → 1,50 | 4 → 1,00 | 5 → 1,00 | 4 → 0,60 | 5 → 0,50 | **4,60** | 1° |
| INC-3 Offline y sincronización | 5 → 1,50 | 5 → 1,25 | 4 → 0,80 | 3 → 0,45 | 4 → 0,40 | **4,40** | 2° |
| INC-2 Agenda automática | 5 → 1,50 | 3 → 0,75 | 4 → 0,80 | 4 → 0,60 | 5 → 0,50 | **4,15** | 3° |
| INC-4 WhatsApp y barreras | 4 → 1,20 | 3 → 0,75 | 3 → 0,60 | 3 → 0,45 | 4 → 0,40 | **3,40** | 4° |
| INC-5 Modelo predictivo | 5 → 1,50 | 4 → 1,00 | 2 → 0,40 | 1 → 0,15 | 3 → 0,30 | **3,35** | 5° |
| INC-6 Tablero territorial | 4 → 1,20 | 2 → 0,50 | 1 → 0,20 | 3 → 0,45 | 4 → 0,40 | **2,75** | 6° |

**Lectura de la matriz:** INC-1 lidera porque tiene el mayor valor, la mayor dependencia técnica (los INC-3 y INC-5 necesitan datos registrados) y es el más fácil de validar con la posta. INC-3 (offline) sube al 2° lugar por el alto riesgo del entorno rural: sin conectividad robusta, todos los demás incrementos pierden valor en campo. INC-5 (modelo predictivo) tiene valor alto pero baja dependencia inversa (no es requisito de nadie más) y complejidad muy alta, por lo que se planifica al final.

> **Pregunta orientadora respondida:** Debe desarrollarse primero lo que genera mayor valor Y reduce mayor riesgo, y que además sea prerequisito de otros incrementos. Desarrollar primero lo "más fácil" crea una ilusión de avance: si al final el offline no funciona, todos los incrementos anteriores son inútiles en campo.

> **📌 UML — Diagrama de Casos de Uso:** Para el INC-1, conviene incluir un **Diagrama de Casos de Uso UML** que muestre los actores (Enfermera/técnico de posta, Agente comunitario, sistema HIS) y sus casos de uso asociados (Registrar niño, Consultar expediente, Validar datos). Ver instrucciones en Sección 13.

---

# 10. Estimación del trabajo (Actividad 8 de la guía)

## 10.1 Técnica de estimación

Se utiliza **Story Points** con la secuencia de Fibonacci (1, 2, 3, 5, 8, 13) para el Product Backlog completo, y **horas estimadas** para el primer incremento (Sprint 1-2), que es el más detallado.

**Velocidad asumida inicial:** 20 story points por sprint (equipo de 3 integrantes, sprint de 2 semanas).  
Esta velocidad se ajustará después del Sprint 1 con datos reales.

## 10.2 Estimación del Product Backlog (Story Points)

| Incremento | Historia | SP | Complejidad | Nivel de incertidumbre |
| :---- | :---- | :---- | :---- | :---- |
| INC-1 | HIST-1.1 Registrar nuevo niño | 5 | Media | Bajo |
| INC-1 | HIST-1.2 Consultar/actualizar expediente | 3 | Media | Bajo |
| INC-1 | HIST-1.3 Validar datos requeridos | 3 | Media | Bajo |
| INC-1 | HIST-1.4 Listar niños en seguimiento | 2 | Baja | Bajo |
| INC-1 | HIST-1.5 Reporte del periodo | 3 | Media | Bajo |
| INC-1 | Infraestructura base + CI/CD | 5 | Media | Medio |
| **INC-1 Total** | | **21 SP** | | |
| INC-2 | HIST-2.1 a 2.4 | 18 | Media-Alta | Bajo |
| INC-3 | HIST-3.1 a 3.4 (sincronización offline) | 21 | Alta | Alto |
| INC-4 | HIST-4.1 a 4.4 (WhatsApp) | 16 | Media | Medio |
| INC-5 | HIST-5.1 a 5.4 (IA + MLOps) | 34 | Muy Alta | Muy Alto |
| INC-6 | HIST-6.1 a 6.4 (tablero) | 15 | Media | Bajo |
| **TOTAL PROYECTO** | | **~125 SP** | | |

## 10.3 Estimación en horas — Sprint 1 (INC-1, semanas 3-4)

| Tarea | Responsable | Estimación (horas) | Unidad | Complejidad | Incertidumbre |
| :---- | :---- | :---- | :---- | :---- | :---- |
| T7: Configurar PostgreSQL + SQLite | Auqui H. | 6 | Horas | Media | Bajo |
| T8: Configurar GitHub Actions | Auqui H. | 4 | Horas | Media | Bajo |
| T9: Configurar SonarCloud | Huamani R. | 2 | Horas | Baja | Bajo |
| T10: Configurar Pytest + cobertura | Huamani R. | 2 | Horas | Baja | Bajo |
| T1: Diseñar formulario de registro | Auqui H. (Figma) | 4 | Horas | Media | Bajo |
| T2: API de registro (backend) | Auqui H. | 8 | Horas | Media | Bajo |
| T3: Interfaz de registro (frontend) | Auqui H. | 8 | Horas | Media | Bajo |
| T4: Pruebas unitarias validación | Huamani R. | 4 | Horas | Media | Bajo |
| T5: Búsqueda y visualización | Auqui H. | 6 | Horas | Media | Bajo |
| T6: Reglas de validación | Auqui H. | 4 | Horas | Media | Bajo |
| Sprint Planning | Porras V. | 2 | Horas | — | — |
| Revisión de sprint (Review) | Porras V. | 3 | Horas | — | — |
| Retrospectiva | Porras V. | 1 | Horas | — | — |
| **Total Sprint 1** | | **54 horas** | | | |

> **Pregunta clave respondida:** Los elementos con mayor incertidumbre en estimación son: (1) la sincronización offline (INC-3, SP=21), porque el comportamiento de resolución de conflictos en campo es impredecible; (2) el modelo predictivo (INC-5, SP=34), porque la precisión depende de la calidad de datos HIS que aún no se ha validado. Se controlarán con spikes técnicos de 1 semana antes de iniciar cada incremento.

---

# 11. Plan del proyecto (Actividad 9 de la guía)

## 11.1 Calendario de 8 sprints (inicio: 20 agosto 2026)

| Sprint | Semanas | Fechas | Incremento | Funcionalidad principal |
| :---- | :---- | :---- | :---- | :---- |
| Sprint 1 | S3-S4 | 01-14 sep 2026 | INC-1 (parte 1) | Arquitectura base, CI/CD, registro nominal (HIST-1.1, 1.3) |
| Sprint 2 | S5-S6 | 15-28 sep 2026 | INC-1 (parte 2) | Expediente completo, reporte (HIST-1.2, 1.4, 1.5) — **Hito H1** |
| Sprint 3 | S7-S8 | 29 sep-12 oct 2026 | INC-2 | Agenda automática NTS 134 y alertas internas — **Hito H2** |
| Sprint 4 | S9-S10 | 13-26 oct 2026 | INC-3 | Modo offline y sincronización robusta — **Hito H3** |
| Sprint 5 | S11-S12 | 27 oct-09 nov 2026 | INC-4 | Notificaciones WhatsApp y barreras — **Hito H4** |
| Sprint 6 | S13-S14 | 10-23 nov 2026 | INC-5 (datos+modelo) | Validación datos HIS, experimentación, entrenamiento — **Hito H5** |
| Sprint 7 | S15-S16 | 24 nov-07 dic 2026 | INC-5 (integración) + INC-6 | Integración modelo-agenda, inicio tablero — **Hito H6** |
| Sprint 8 | S17-S18 | 08-21 dic 2026 | INC-6 completo | Tablero territorial completo, MVP operativo — **Hito H7** |

## 11.2 Plan detallado del Sprint 1

| ID | Actividad | Incremento | Responsable | Inicio | Fin | Dependencia | Entregable |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| A01 | Sprint Planning Sprint 1 | INC-1 | Porras V. | 01-sep | 01-sep | — | Sprint Backlog |
| A02 | Configurar PostgreSQL + SQLite | INC-1 | Auqui H. | 01-sep | 02-sep | A01 | BD configurada |
| A03 | Configurar GitHub Actions (CI/CD) | INC-1 | Auqui H. | 01-sep | 02-sep | A01 | Pipeline operativo |
| A04 | Configurar SonarCloud | INC-1 | Huamani R. | 02-sep | 02-sep | A03 | Dashboard SonarCloud |
| A05 | Configurar Pytest + cobertura | INC-1 | Huamani R. | 02-sep | 02-sep | A03 | Suite configurada |
| A06 | Diseñar formulario de registro (Figma) | INC-1 | Auqui H. | 02-sep | 03-sep | A01 | Prototipo Figma |
| A07 | Implementar API de registro (backend) | INC-1 | Auqui H. | 03-sep | 07-sep | A02, A06 | Endpoints REST |
| A08 | Implementar interfaz de registro | INC-1 | Auqui H. | 07-sep | 10-sep | A06, A07 | Pantalla funcional |
| A09 | Reglas de validación (hemoglobina, edad, zona) | INC-1 | Auqui H. | 07-sep | 09-sep | A07 | Validaciones implementadas |
| A10 | Pruebas unitarias de validación | INC-1 | Huamani R. | 09-sep | 11-sep | A09 | Suite de pruebas verde |
| A11 | Búsqueda y visualización de expediente | INC-1 | Auqui H. | 10-sep | 12-sep | A08 | Pantalla de consulta |
| A12 | Code review + análisis SonarCloud | INC-1 | Huamani R. | 12-sep | 12-sep | A10, A11 | PR aprobado |
| A13 | Despliegue a posta piloto | INC-1 | Auqui H. | 12-sep | 13-sep | A12 | Sistema en producción |
| A14 | Revisión del sprint con personal de salud | INC-1 | Porras V. | 13-sep | 13-sep | A13 | Acta de revisión |
| A15 | Retrospectiva | INC-1 | Porras V. | 14-sep | 14-sep | A14 | Plan de mejora |

> **Herramienta:** GitHub Projects con tablero Kanban (columnas: Backlog → En progreso → En revisión → Listo). Microsoft Project para el cronograma Gantt de los 8 sprints (ver sección de instrucciones UML).

> **📌 UML — Diagrama de Secuencia:** Para la A07 (API de registro), conviene un **Diagrama de Secuencia UML** que muestre la interacción entre el actor (enfermera), la interfaz (frontend), el API (backend), la base de datos (PostgreSQL/SQLite) y el sistema de validación. Ver instrucciones en Sección 13.

---

# 12. Dependencias y riesgos de planificación (Actividad 10 de la guía)

| Actividad | Depende de | Tipo de dependencia | Riesgo | Acción |
| :---- | :---- | :---- | :---- | :---- |
| INC-2 (agenda automática) | INC-1 completado | Técnica: la agenda requiere registros nominales existentes | Si INC-1 se retrasa, INC-2 no puede iniciar | Scrum: INC-1 tiene prioridad absoluta en Sprint 1-2 |
| INC-3 (offline y sincronización) | INC-1 completado | Técnica: la sincronización requiere el esquema de datos del registro | Conflictos de sincronización complejos pueden extender INC-3 | Spike técnico de 2 días al inicio del Sprint 4 |
| INC-5 (modelo predictivo) | INC-1 + INC-3 completados y datos HIS disponibles | Técnica + datos: el modelo requiere datos nominales confiables y sincronizados | Calidad de datos HIS insuficiente puede posponer INC-5 | Validación de datos HIS en paralelo durante Sprints 4-5; criterio explícito de postergación |
| INC-5 (modelo) | API de WhatsApp Business aprobada | Externa: requiere cuenta de negocios aprobada | La aprobación puede tardar 4-6 semanas | Iniciar solicitud desde Sprint 3 |
| Revisión del sprint | Disponibilidad del personal de salud de la posta | Organizacional: acceso físico o remoto al personal | Distancia y carga asistencial pueden dificultar la asistencia | Sesiones breves (30 min), opción remota por videoconferencia |
| Entrenamiento del modelo | Datos HIS limpios y versionados | Datos: el pipeline MLOps requiere datos de entrada válidos | Datos insuficientes = modelo con precisión insuficiente | Criterio mínimo: ≥ 500 registros con hemoglobina, edad y resultado de seguimiento |

**Cadena de dependencias crítica del componente IA:**
```
Datos HIS disponibles (validación desde Sprint 4)
  ↓
Limpieza y versionado (Sprint 5, semana 1)
  ↓
Experimentación (Sprint 6, semana 1)
  ↓
Entrenamiento y evaluación (Sprint 6, semana 2)
  ↓
Integración modelo-agenda (Sprint 7)
  ↓
Prueba funcional de priorización (Sprint 7, semana 2)
```

> **Pregunta orientadora respondida:** La actividad que puede retrasar más el valor es la **validación de datos HIS** (prerequisito de INC-5). Si los datos son de baja calidad, el modelo no puede entrenarse, y INC-5 se pospone. Sin embargo, INC-1 a INC-4 siguen siendo valiosos por sí mismos, por lo que el retraso no bloquea el valor total del sistema.

> **📌 UML — Diagrama de Componentes:** Para representar las dependencias técnicas entre módulos del sistema, corresponde un **Diagrama de Componentes UML** que muestre el módulo de registro, el módulo de agenda, el módulo offline/sincronización, la API de WhatsApp, el pipeline MLOps y sus interfaces. Ver instrucciones en Sección 13.

---

# 13. Hitos y entregas (Actividad 11 de la guía)

| Hito | Condición para alcanzarlo | Entregable | Fecha planificada | Evidencia |
| :---- | :---- | :---- | :---- | :---- |
| H0 | Arquitectura base definida y pipeline CI/CD operativo | Documento de arquitectura + pipeline verde | 02-sep-2026 | Diagrama de componentes aprobado; log de Actions |
| H1 | INC-1 completo: registro nominal validado y expediente digital aceptado por posta | Sistema de registro en producción, acta de aceptación | 28-sep-2026 | Acta firmada; capturas; reporte SonarCloud |
| H2 | INC-2 completo: agenda automática funcional, revisión con enfermera | Agenda automática en producción | 12-oct-2026 | Acta de revisión; métricas de cobertura oportuna |
| H3 | INC-3 completo: modo offline y sincronización sin pérdida de datos en prueba de campo | Módulo offline en producción | 26-oct-2026 | Reporte de prueba offline en campo |
| H4 | INC-4 completo: notificaciones WhatsApp enviadas y barreras registradas | Módulo de WhatsApp en producción | 09-nov-2026 | Métricas de entrega de mensajes |
| H5 | Datos HIS validados y modelo predictivo entrenado con precisión ≥ umbral clínico | Artefacto del modelo en MLflow | 23-nov-2026 | Reporte de precisión validado con personal clínico |
| H6 | INC-5 integrado y priorización visible en la agenda del personal | Sistema de priorización en producción | 07-dic-2026 | Acta de validación clínica |
| H7 | INC-6 completo: MVP operativo con tablero territorial, todos los incrementos integrados | MVP completo en producción | 21-dic-2026 | Acta de aceptación final; indicadores de valor medidos |

> **Pregunta clave respondida:** Los hitos demuestran **generación de resultados y valor**, no solo avance de actividades. H1, por ejemplo, no dice "completar el código del registro" sino "sistema de registro aceptado por la posta": eso requiere que el personal de salud lo haya revisado y validado.

---

# 14. Seguimiento del proyecto (Actividad 12 de la guía)

## 14.1 Mecanismo de seguimiento

El seguimiento sigue el ciclo:

```
Planificado (Sprint Backlog)
  ↓
Ejecutado (Daily Scrum + commits en GitHub)
  ↓
Medición (burndown chart + dashboard indicadores)
  ↓
Comparación (planificado vs. real en revisión de sprint)
  ↓
Desviación identificada
  ↓
Acción correctiva (replanificación del backlog o del sprint)
  ↓
Actualización del plan
```

## 14.2 Matriz de seguimiento (ejemplo Sprint 1)

| Elemento | Planificado | Real (ejemplo) | Desviación | Causa | Acción |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Historias completadas | 6 historias | 5 historias | -1 historia | T3 (frontend) tomó 2 días más de lo estimado | Mover HIST-1.5 al Sprint 2; reducir alcance del reporte |
| Story Points entregados | 21 SP | 16 SP | -5 SP | Configuración de SQLite más compleja en dispositivos Android | Registrar en retrospectiva; ajustar velocidad a 16 SP para Sprint 2 |
| Horas utilizadas | 54 horas | 58 horas | +4 horas | Problemas de compatibilidad en el pipeline CI/CD | Documentar la solución; el pipeline ya está estable |
| Pruebas pasadas | 100% | 95% | -5% | 2 casos de prueba de validación fallaron | Corrección inmediata; las pruebas pasan antes del despliegue |
| Revisión del sprint | Aprobada | Observaciones registradas | — | El personal pidió incluir el peso corporal en el registro | Añadir HIST-1.6 al backlog del Sprint 2 |

---

# 15. Indicadores del proceso (Actividad 13 de la guía)

| Indicador | Fórmula/criterio | Meta | Frecuencia | Fuente | Responsable |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Avance** | Historias completadas ÷ planificadas × 100 | ≥ 80 % por sprint | Al final de cada sprint | GitHub Projects | Porras V. |
| **Velocidad del equipo** | Story points entregados por sprint | ≥ 80 % de lo planificado en sprint actual | Al final de cada sprint | GitHub Projects | Porras V. |
| **Cumplimiento de hitos** | Hitos alcanzados en fecha ÷ total × 100 | 100 % | Por hito | Plan del proyecto | Porras V. |
| **Calidad de código** | Issues SonarCloud Blocker/Critical | 0 Blocker, 0 Critical | Por build (CI/CD) | Dashboard SonarCloud | Huamani R. |
| **Cobertura de pruebas** | Líneas cubiertas ÷ total × 100 | ≥ 80 % del código nuevo | Por sprint | Reporte Pytest en CI | Huamani R. |
| **Tasa de defectos** | Defectos encontrados en revisión ÷ historias entregadas | < 1 defecto mayor por historia | Por sprint | Acta de revisión | Huamani R. |
| **Frecuencia de despliegue** | Despliegues exitosos por sprint | ≥ 1 despliegue exitoso por sprint | Por sprint | Log GitHub Actions | Auqui H. |
| **Tiempo de recuperación** | Tiempo entre fallo en producción y restauración | < 4 horas | Ante cada incidente | Log de incidentes | Auqui H. |
| **Adopción del incremento** | Porcentaje de personal de posta que usa la funcionalidad 2 semanas después del despliegue | ≥ 70 % | 2 semanas post-despliegue | Registro de sesiones del sistema | Porras V. |
| **Precisión del modelo (desde INC-5)** | Casos confirmados por personal clínico ÷ señalados por el modelo × 100 | ≥ 75 % | Por reentrenamiento | MLflow dashboard | Auqui H. |
| **Valor: cobertura oportuna** | Controles realizados en fecha ÷ programados × 100 | Aumentar 15 % respecto a línea base AS-IS | Por incremento de agenda | HIS / sistema propio | Porras V. |
| **Valor: pérdida de seguimiento** | Niños sin control en 60 días ÷ total activos × 100 | Reducir 20 % respecto a AS-IS | Mensual | Sistema / HIS | Porras V. |

> **Pregunta orientadora respondida:** Los indicadores que demuestran generación de **valor** (no solo consumo de recursos) son: adopción del incremento, cobertura oportuna de controles y pérdida de seguimiento. Si estos mejoran, el proceso está contribuyendo al resultado de salud esperado. Los demás son indicadores del proceso de desarrollo que permiten anticipar problemas.

---

# 16. Control de desviaciones (Actividad 14 de la guía)

## 16.1 Tipos de desviación y umbral de acción

| Tipo de desviación | Umbral para acción correctiva | Tipo de acción |
| :---- | :---- | :---- |
| Historias completadas < 60 % del sprint | Inmediata | Descope del sprint; mover historias al siguiente |
| Hito retrasado > 1 semana | Inmediata | Replanificación; evaluación de impacto en cadena |
| Cobertura de pruebas < 70 % | Corrección antes del despliegue | No desplegar hasta alcanzar el umbral |
| Defecto bloqueante en producción | Inmediata | Hotfix en < 4 horas; análisis de causa raíz |
| Calidad de datos HIS < umbral mínimo | Antes del Sprint 6 | Posponer INC-5; comunicar a la microred |
| Precisión del modelo < 70 % | Tras evaluación con personal clínico | Reentrenamiento con datos adicionales; revisión de variables |

## 16.2 Matriz de control de desviaciones

| Desviación | Causa | Impacto | Decisión | Responsable | Nueva fecha |
| :---- | :---- | :---- | :---- | :---- | :---- |
| INC-3 (offline) requiere +1 sprint | Conflictos de sincronización más complejos de lo estimado | Retrasa INC-4 en 2 semanas | Extender Sprint 4 a 3 semanas o iniciar INC-4 en paralelo con INC-3 parte 2 | Porras V. | Revisar en Sprint 4, semana 2 |
| API de WhatsApp no aprobada | Proceso de aprobación de Meta excede 6 semanas | INC-4 no puede completarse en Sprint 5 | Usar SMS como canal alternativo; INC-4 entrega con SMS, WhatsApp en cuando se apruebe | Auqui H. | Sprint 5 continúa con SMS |
| Datos HIS insuficientes (< 500 registros) | Sistema HIS de la microred no tiene datos históricos suficientes | INC-5 no puede ejecutarse con calidad | Posponer INC-5 a Sprint 8; usar INC-1 para generar datos nominales suficientes antes de entrenar | Porras V. | Evaluar en Sprint 6, semana 1 |

> **Pregunta clave respondida:** Una desviación requiere **solo seguimiento** si el impacto se absorbe dentro del sprint actual sin afectar hitos. Requiere **modificar el plan** cuando afecta la cadena de dependencias (retrasando un incremento posterior) o cuando el valor prometido al usuario no puede entregarse en la fecha acordada.

---

# 17. Simulación de reunión de seguimiento — Sprint 1, día 7 (Actividad 15 de la guía)

**Fecha simulada:** 08 de septiembre de 2026 (mitad del Sprint 1)  
**Participantes:** Porras V. (Proceso), Auqui H. (Desarrollo), Huamani R. (Calidad)

**1. ¿Qué estaba planificado al día 7?**
- Infraestructura completa (A01-A05): ✅ Completada
- Diseño del formulario en Figma (A06): ✅ Completada
- API de registro, backend (A07): 🔄 En progreso (60 % completada)
- Reglas de validación (A09): 🔄 En progreso (30 % completada)

**2. ¿Qué se completó?**
- La configuración de la infraestructura (PostgreSQL, GitHub Actions, SonarCloud, Pytest) está completa y operativa. El pipeline CI/CD ejecutó su primer build verde el día 3.
- El prototipo en Figma del formulario de registro fue aprobado informalmente por el equipo.
- 3 de los 10 endpoints del API de registro están implementados y probados.

**3. ¿Qué está pendiente?**
- API de registro: 7 endpoints restantes
- Reglas de validación: criterios de hemoglobina por edad y altitud pendientes (requieren verificar NTS 134 para los valores exactos)
- Interfaz de registro (frontend): no iniciada aún
- Búsqueda y visualización del expediente (A11): no iniciada

**4. ¿Qué está retrasado?**
- La API de registro está 2 días atrasada respecto al plan. Se estimó completarla al día 5; actualmente va al 60 %.

**5. ¿Qué problemas aparecieron?**
- Los valores exactos de umbrales de hemoglobina por rango etario y por nivel de altitud en la NTS 134 tienen versiones distintas entre el documento original y una circular del MINSA 2024. Huamani R. identificó la discrepancia revisando el documento oficial.
- La configuración de SQLite en dispositivos Android con versión 9 o inferior presentó un problema de compatibilidad con la librería de cifrado seleccionada.

**6. ¿Qué riesgos se materializaron?**
- **Riesgo: ambigüedad en los requisitos clínicos.** La discrepancia en los umbrales de hemoglobina es un riesgo de requisitos, no técnico. Requiere consultar directamente a la microred.

**7. ¿Qué decisiones deben tomarse?**
- Porras V. coordinará con la enfermera de la posta piloto esta semana para confirmar qué circular aplica en Junín. Se bloqueará la implementación de las reglas de validación hasta tener la confirmación (máximo 2 días).
- Auqui H. reemplazará la librería de cifrado para SQLite por una versión compatible con Android 9+ (disponible, tarea de 2 horas).

**8. ¿Qué actividades deben replanificarse?**
- El frente de API de registro se reorganiza: los 7 endpoints restantes se distribuyen en días 8-11 (en lugar de 6-10).
- Dada la extensión, HIST-1.5 (reporte del periodo) se moverá al Sprint 2.

**9. ¿Qué incremento será entregado al final del Sprint 1?**
- HIST-1.1 (registro), HIST-1.2 (consulta), HIST-1.3 (validación) y HIST-1.4 (lista de niños). HIST-1.5 se mueve al Sprint 2.

**10. ¿Qué valor se espera generar?**
- Al final del Sprint 1, el personal de la posta piloto podrá registrar a cada niño una sola vez en el sistema, con validación de datos críticos, consultable desde el mismo dispositivo. Eso elimina el triple registro manual para los nuevos ingresos.

---

# 18. Trazabilidad del proceso (Actividad 16 de la guía)

| Elemento | Evidencia del proyecto |
| :---- | :---- |
| **Problema** | Discontinuidad en la prevención, medición, registro y seguimiento de la anemia infantil en zonas rurales de Junín |
| **Brecha** | Triple registro con errores; agenda manual sin recordatorios; barreras ocultas hasta el abandono; sin anticipación del riesgo; conectividad intermitente |
| **Necesidad de software** | Registro nominal validado, agenda NTS 134, operación offline, notificación por WhatsApp, priorización predictiva y tablero de indicadores |
| **Característica del proyecto** | Alta incertidumbre en IA; riesgo tecnológico del entorno rural (offline); necesidad de validación con personal de salud |
| **Modelo de proceso** | Iterativo-incremental gestionado con Scrum, DevOps para entrega, MLOps para el modelo |
| **Actividad del proceso** | Sprint Planning → Requisitos → Análisis/Diseño → Implementación → Pruebas (incluida offline) → CI/CD → Revisión → Retrospectiva |
| **Producto de trabajo** | Sprint Backlog; código fuente en GitHub; reportes de prueba; actas de revisión; artefacto del modelo en MLflow |
| **Responsable** | Porras V. (proceso y coordinación); Auqui H. (desarrollo y MLOps); Huamani R. (calidad y pruebas) |
| **Planificación** | 8 sprints de 2 semanas (01 sep – 21 dic 2026); backlog de ~125 SP; velocidad inicial 20 SP/sprint |
| **Incremento** | Registro nominal → Agenda automática → Offline → WhatsApp → Modelo predictivo → Tablero territorial |
| **Resultado** | Atención más oportuna, seguimiento continuo, priorización explicable, comunicación efectiva con las familias |
| **Indicador** | Cobertura oportuna de controles, pérdida de seguimiento, precisión del modelo, adopción del sistema |
| **Valor** | Protección de la salud del niño: menor pérdida de seguimiento, mayor recuperación documentada, mejor uso de recursos limitados |

---

# 19. Caso de decisión (Actividad 17 de la guía)

*Situación planteada: Un equipo desarrolla una plataforma inteligente para apoyar la gestión de emergencias municipales. Los requisitos cambian con la retroalimentación, hay integración con múltiples sistemas, componentes de IA, datos cambiantes, entregas progresivas, recursos limitados, funcionalidades críticas y necesidad de validación temprana. Después de dos semanas, una funcionalidad prioritaria presenta problemas de integración y requiere el doble del esfuerzo estimado.*

**1. ¿Qué actividad del proceso debería permitir detectar el problema?**
El seguimiento diario (Daily Scrum) debería haberlo detectado desde el día 2 o 3 del sprint, cuando el esfuerzo real comenzara a superar lo planificado. El burndown chart lo haría visible de forma gráfica al tercer o cuarto día.

**2. ¿Qué indicador evidenciaría la desviación?**
La velocidad del sprint: si al día 7 (mitad del sprint) solo se completó el 20 % de las historias cuando debería ir en el 50 %, la desviación es evidente. También el indicador de horas acumuladas vs. estimadas.

**3. ¿Qué impacto tendría sobre el plan?**
Si la funcionalidad requiere el doble del esfuerzo, el sprint no puede completar todo lo planificado. Hay que escoger: reducir el alcance del sprint o extenderlo (lo cual rompería el ritmo de los sprints).

**4. ¿Debe modificarse el cronograma?**
No necesariamente el cronograma general, pero sí el alcance del sprint actual. En Scrum, la respuesta natural es reducir el scope del sprint y mover las historias no completadas al siguiente backlog, preservando la cadencia.

**5. ¿Debe modificarse la prioridad de otras funcionalidades?**
Solo si la funcionalidad con problemas es prerequisito de otras funcionalidades planificadas para el siguiente sprint. En ese caso, sí se reconsideran las prioridades del backlog.

**6. ¿Qué riesgo se ha materializado?**
El riesgo de **subestimación por complejidad técnica no prevista**, específicamente en la integración entre sistemas heterogéneos. Este riesgo debería haber estado registrado en la matriz de riesgos del proyecto.

**7. ¿Qué decisión debería tomar el equipo?**
(a) Completar la funcionalidad con el doble del esfuerzo, reduciendo el alcance del sprint; (b) Particionar la funcionalidad en una parte básica (entregable en el sprint) y una parte avanzada (para el siguiente); (c) Si la integración es un bloqueante técnico no resoluble en el sprint, hacer un spike técnico y reprogramar la historia.

**8. ¿Cómo mantener la entrega de valor?**
Entregando las historias de menor complejidad que sí son completables, aunque la funcionalidad problemática quede parcial. El valor parcial es mejor que ningún valor.

**9. ¿Qué evidencia debe registrarse?**
El problema de integración, el esfuerzo real vs. estimado, la decisión tomada, el impacto en el cronograma y las lecciones aprendidas. Todo documentado en la retrospectiva y en el plan de riesgos actualizado.

**10. ¿Qué aprendizaje debería incorporarse al siguiente incremento?**
Incluir un **spike técnico de integración** de 1-2 días al inicio de cualquier sprint que involucre integración con sistemas externos. Ese spike produce evidencia técnica que permite estimar con mayor precisión antes de comprometer el alcance del sprint completo.

---

# 20. Reto de aplicación — Plan ejecutable del Incremento 1 (Actividad 22 de la guía)

## A. Objetivo del incremento
Resolver la necesidad de registro nominal confiable: que cada niño en seguimiento por anemia infantil tenga un expediente digital único, con datos validados y consultable, funcionando en la posta piloto.

## B. Funcionalidades
- HIST-1.1: Registrar nuevo niño con datos clínicos básicos (nombre, DNI, fecha de nacimiento, hemoglobina, peso, zona)
- HIST-1.2: Consultar y actualizar el expediente de un niño
- HIST-1.3: Validar datos requeridos según NTS 134 (umbrales de hemoglobina por edad y altitud)
- HIST-1.4: Listar niños en seguimiento activo con estado de control

## C. Actividades del proceso
Sprint Planning → Arquitectura base y CI/CD → Diseño UI (Figma) → API backend → Interfaz frontend → Reglas de validación → Pruebas unitarias (Pytest) → Code review (SonarCloud) → Integración continua (GitHub Actions) → Despliegue a posta piloto → Revisión con personal de salud → Retrospectiva

## D. Responsables
- **Porras V.**: Sprint Planning, coordinación con posta, revisión de sprint, retrospectiva
- **Auqui H.**: Diseño Figma, implementación backend y frontend, configuración CI/CD
- **Huamani R.**: Pruebas unitarias, code review, configuración SonarCloud

## E. Estimación
- Total: 21 story points / 54 horas
- Sprint 1 (01-14 sep 2026): HIST-1.1, 1.2, 1.3, 1.4 + infraestructura base
- Sprint 2 (15-28 sep 2026): HIST-1.5 (reporte) + ajustes de la revisión

## F. Dependencias
- Confirmación de umbrales NTS 134 con personal de la microred (prerequisito para HIST-1.3)
- Dispositivo Android disponible en la posta piloto para el despliegue (prerequisito para el smoke test)
- Acceso al repositorio GitHub y cuentas de SonarCloud configuradas (prerequisito para CI/CD)

## G. Riesgos
| Riesgo | Probabilidad | Impacto | Mitigación |
| :---- | :---- | :---- | :---- |
| Ambigüedad en umbrales NTS 134 | Media | Alto | Consultar a la microred antes del Sprint 1, día 3 |
| Incompatibilidad SQLite en Android antiguo | Baja | Medio | Probar en Android 9 desde el día 1 |
| No disponibilidad del personal de la posta para la revisión | Media | Alto | Agendar la revisión al inicio del sprint; tener opción remota |

## H. Indicadores de avance
- Story points completados ÷ planificados × 100 (meta ≥ 80 %)
- Cobertura de pruebas ≥ 80 %
- Pipeline CI/CD verde en todos los builds
- 0 issues Blocker/Critical en SonarCloud

## I. Criterios de aceptación
- El personal de salud de la posta puede registrar a un niño nuevo en menos de 3 minutos
- Los datos se almacenan correctamente en la base de datos y son consultables
- El sistema rechaza datos fuera del rango clínico válido con un mensaje comprensible
- La revisión de sprint concluye con acta firmada de aceptación

## J. Valor generado
El personal de la posta elimina el triple registro manual (historia clínica + tarjeta de control + digitación HIS) para los nuevos ingresos. La información queda centralizada, sin duplicados, con validación automática de errores críticos. Esto genera datos más confiables que en el futuro alimentarán el modelo predictivo.

---

# 21. Preguntas de análisis (Actividad 24 de la guía)

1. **¿Qué actividades son críticas para el éxito del proyecto?** Las pruebas de sincronización offline (sin ellas el sistema falla en campo), la revisión de sprint con el personal de salud (sin validación clínica el sistema no se adopta), y la validación de datos HIS (sin datos limpios el modelo no puede entrenarse).

2. **¿Por qué esas actividades son necesarias según el modelo seleccionado?** El modelo iterativo-incremental con Scrum exige que cada sprint entregue un incremento funcional y validado: eso requiere pruebas y revisión. DevOps exige que el despliegue sea automatizado y seguro: eso requiere CI/CD. MLOps exige que el ciclo del modelo sea controlado: eso requiere la validación de datos.

3. **¿Qué actividades deben repetirse en cada incremento?** Sprint Planning, refinamiento de requisitos, análisis y diseño, implementación, pruebas (unitarias + offline), code review, CI/CD, revisión con el usuario y retrospectiva.

4. **¿Qué productos de trabajo permiten demostrar que una actividad fue realizada?** Código en el repositorio (implementación), reporte de pruebas (testing), log del pipeline (CI/CD), acta de revisión (revisión de sprint), dashboard SonarCloud (calidad), experimentos en MLflow (modelo).

5. **¿Cómo se determinará objetivamente que una actividad está terminada?** Con los criterios de terminación de la sección 6: cobertura ≥ 80 %, 0 issues Blocker, acta firmada, PR aprobado. No hay "casi terminado" en los criterios.

6. **¿Cómo se priorizaron las funcionalidades?** Con la Matriz de Priorización Ponderada (sección 9): valor para el usuario (30 %), reducción de riesgo (25 %), dependencia técnica (20 %), complejidad inversa (15 %) y validación (10 %).

7. **¿Qué elementos presentan mayor incertidumbre en la estimación?** INC-3 (sincronización offline, 21 SP) por la complejidad de los conflictos en campo, e INC-5 (modelo predictivo, 34 SP) por la dependencia de la calidad de datos HIS.

8. **¿Qué dependencias pueden afectar el cronograma?** La validación de datos HIS (prerequisito de INC-5), la aprobación de la API de WhatsApp Business (prerequisito de INC-4) y la disponibilidad del personal de salud para las revisiones de sprint.

9. **¿Qué indicadores controlarán el avance?** Velocity del sprint, cumplimiento de hitos, cobertura de pruebas, frecuencia de despliegue y adopción del incremento por el personal de la posta.

10. **¿Cómo se identificarán las desviaciones?** A través del burndown chart diario, el daily Scrum, y la comparación planificado vs. real al final de cada sprint en la revisión.

11. **¿Qué acciones ante un retraso?** Reducir el scope del sprint (mover historias al siguiente backlog), investigar la causa raíz, ajustar la estimación de velocidad y documentar en la retrospectiva.

12. **¿Cómo incorporar cambios sin perder el control?** Añadiendo los cambios al Product Backlog (no al sprint en curso), priorizándolos con los criterios de la sección 9, y planificándolos formalmente en el siguiente Sprint Planning.

13. **¿Cómo se relacionan las actividades con los incrementos?** Cada incremento activa el ciclo completo de actividades (sección 3.1). Las actividades específicas por incremento (sección 3.2) añaden actividades adicionales según la naturaleza de la funcionalidad.

14. **¿Cómo demuestra la planificación que contribuye a generar valor?** Los hitos (sección 13) están definidos en términos de resultados para el usuario, no solo de actividades completadas. Los indicadores de valor (cobertura oportuna, pérdida de seguimiento) se miden desde el primer incremento en producción.

15. **¿Qué cambiarían después de analizar los resultados del seguimiento?** La velocidad asumida de 20 SP/sprint se ajustará con los datos reales del Sprint 1. Si INC-3 (offline) es más complejo de lo estimado, se considerará extender el sprint o reducir el alcance, con evidencia del burndown chart.

---

# 22. Fuentes

- Guía de Trabajo Semana 3 y 4 – Ejes 3 y 4: Actividades del proceso de software y Planificación y seguimiento (documento del curso, 2026-20).
- Entregable Semana 2 del equipo: modelo de proceso seleccionado, incrementos, riesgos y trazabilidad.
- Entregable Semana 1 del equipo: proceso TO-BE, brechas e indicadores del proyecto.
- NTS N.° 134-MINSA/2017/DGIESP. https://bvs.minsa.gob.pe/local/MINSA/4190.pdf
- Schwaber, K. y Sutherland, J. (2020). *The Scrum Guide*. Scrum.org.
- Kim, G., Humble, J., Debois, P. y Willis, J. (2016). *The DevOps Handbook*. IT Revolution Press.

---

*Fin del Entregable Semanas 3 y 4 — v1*
