# Verificación S2 y Guía de Diagramas UML — PowerDesigner 16.x
## Proyecto: Sistema de Detección Temprana de Anemia Infantil — Junín
### Curso: Procesos de Software 2026-20

---

# PARTE 1 — Verificación del Entregable S2 vs. Guía S2

## Resultado general: 23/24 ítems ✅

| Categoría | Total | ✅ Cumplidos | ⚠️ Parciales | ❌ No cumplidos |
|---|---|---|---|---|
| Actividades 1–10 | 10 | 9 | 1 (Act. 5 — imagen del proceso) | 0 |
| Preguntas de análisis (sección 12) | 10 | 10 | 0 | 0 |
| Reto de aplicación / defensa 5 min (sección 13) | 4 | 4 | 0 | 0 |
| **Total** | **24** | **23** | **1** | **0** |

---

## Detalle por actividad

| Act. | Sección del entregable | ¿Cumple? | Observación |
|---|---|---|---|
| **1** Características del proyecto — 12 factores con Nivel/Evidencia | Sección 1 | ✅ Sí (alto) | Los 12 factores están cubiertos; la columna de evidencia está integrada en "Situación" en lugar de columna separada — diferencia formal, no de contenido. Agrega la pregunta de las 3 características determinantes. |
| **2** Factores de selección — mín. 6 factores con importancia y justificación | Sección 2 | ✅ Sí | 8 factores (supera el mínimo), todos con importancia "Alta" y justificación técnica específica al proyecto. |
| **3** Comparación de modelos — 7 enfoques con escala 1–5 y pregunta orientadora | Sección 3 | ✅ Sí (muy alto) | Los 7 enfoques, escala correcta, pregunta respondida explícitamente, aclaración de categorías (modelo/marco/práctica) que va más allá de lo pedido. |
| **4** Modelo seleccionado — matriz ponderada con 3 alternativas, 8 criterios, pesos y justificación 7-puntos | Secciones 4, 4.1 y 5 | ✅ Sí (excelente) | Matriz completa con pesos justificados, lectura crítica de la matriz, justificación en 7 sub-puntos exactos. |
| **5** Representar gráficamente el modelo con 10 elementos | Sección 6 — imagen Figure 1 | ⚠️ Parcial | La imagen existe en base64 en el `.md` y la descripción textual cubre los 10 elementos. **Riesgo pendiente**: verificar que el diagrama sea legible en el DOCX/PDF renderizado. La imagen debería ser un diagrama UML formal (ver Sección 2.2 de esta guía). |
| **6** Entregas de valor — tabla Incremento/Funcionalidad/Resultado/Valor/Indicador | Sección 7 | ✅ Sí (excelente) | 6 incrementos (supera el ejemplo de 5), cada uno con indicador cuantitativo propio y nota justificando el orden. |
| **7** Riesgos — mín. 5 riesgos con causa, impacto y mecanismo de control | Sección 8 | ✅ Sí (excelente) | 7 riesgos (supera el mínimo), específicos del proyecto incluyendo sesgo del modelo y baja adopción. |
| **8** Herramientas — tabla Necesidad/Herramienta/Actividad y pregunta orientadora | Secciones 9 y 9.1 | ✅ Sí (sobresaliente) | 10 herramientas + 3 matrices comparativas ponderadas de herramientas críticas. Excede ampliamente lo requerido. |
| **9** Trazabilidad — cadena completa de 10 eslabones | Sección 10 | ✅ Sí (excelente) | Los 10 elementos exactos con contenido específico al proyecto. |
| **10** Caso de decisión — 10 preguntas de plataforma de salud con IA | Sección 11 | ✅ Sí (excelente) | Las 10 preguntas respondidas, técnicas y contextualizadas al dominio de salud. |
| **P1–P10** Preguntas de análisis | Sección 12 | ✅ Todas (10/10) | Argumentación técnica con vínculo específico al proyecto en cada respuesta. |
| **Reto** Defensa 5 min — 4 preguntas | Sección 13 | ✅ Todas (4/4) | **Observación:** La pregunta 3 (¿por qué elegimos este modelo?) es demasiado extensa para una exposición de 2 minutos. Para presentación oral, condensar a 3-4 ideas clave. |

---

## Única observación de mejora

> **Actividad 5 — Diagrama del proceso:** Reemplazar la imagen embebida en base64 por un **Diagrama de Actividades UML** creado en PowerDesigner (ver instrucciones en Sección 2.2 de esta guía). Un diagrama UML formal supera el criterio "Excelente" de la rúbrica al demostrar conocimiento de herramientas normadas de modelado.

---
---

# PARTE 2 — Guía de Diagramas UML en PowerDesigner 16.x

## Mapa de diagramas: qué hacer, dónde y cuándo

| Diagrama | Tipo UML | Entregable | Sección | Prioridad |
|---|---|---|---|---|
| D1 | Casos de uso | S2 | §1 Características | 🔴 Alta |
| D2 | Actividades (swimlanes) | S2 | §6 Representación del proceso | 🔴 Alta |
| D3 | Secuencia | S2 y S3-S4 | §6 S2 / §11 Plan S3-S4 | 🔴 Alta |
| D4 | Despliegue | S2 | §9 Herramientas | 🔴 Alta |
| D5 | Componentes | S2 y S3-S4 | §7 Incrementos | 🟡 Media |
| D6 | Estados | S2 | §8 Riesgos | 🟡 Media |
| D7 | Clases (dominio) | S2 y S3-S4 | §10 Trazabilidad | 🟡 Media |

---

## D1 — Diagrama de Casos de Uso

**Dónde:** Entregable S2, Sección 1 (Características del proyecto)  
**Por qué:** Formaliza la relación entre actores y funcionalidades del sistema, haciendo explícito el alcance del software que la tabla de características solo describe narrativamente.

### Instrucciones en PowerDesigner 16.x

1. `File → New → Use Case Diagram`
2. En **Toolbox** (panel derecho), seleccionar la paleta **Use Case**
3. **Crear actores** (botón `Actor` en toolbox o `Insert → Actor`):

| Actor | Estereotipo | Descripción |
|---|---|---|
| Enfermera/Técnica de Posta | `«primary»` | Registra evaluaciones, agenda controles, consulta priorización |
| Agente Comunitario de Salud (ACS) | `«primary»` | Registra en modo offline, reporta barreras |
| Familia/Tutor del niño | `«primary»` | Recibe notificaciones, confirma asistencia |
| Sistema HIS | `«external system»` | Provee datos históricos al pipeline MLOps |
| API WhatsApp Business | `«external system»` | Recibe y envía mensajes de recordatorio |
| Microred de Salud | `«supervisor»` | Consulta tablero de gestión territorial |
| MINSA | `«supervisor»` | Exporta reportes nacionales |

4. **Crear casos de uso** (botón `Use Case` en toolbox, elipse con nombre):

```
Registrar evaluación nutricional y hemoglobina
Consultar expediente digital del niño
Programar control según NTS 134
Recibir alerta de control vencido
Registrar datos en modo offline
Sincronizar datos al recuperar conectividad
Enviar recordatorio por WhatsApp a la familia
Registrar barrera de acceso (pasaje, distancia)
Consultar priorización de casos por riesgo
Ver tablero de gestión territorial
Ejecutar reentrenamiento del modelo predictivo
```

5. **Relaciones `<<include>>`** (línea punteada con flecha y estereotipo):
   - "Registrar evaluación" → `<<include>>` → "Validar datos contra NTS 134"
   - "Consultar priorización de riesgo" → `<<include>>` → "Ejecutar modelo predictivo"

6. **Relaciones `<<extend>>`**:
   - "Registrar datos en modo offline" → `<<extend>>` → "Registrar evaluación nutricional" (condición: sin conectividad)
   - "Enviar recordatorio alternativo por SMS" → `<<extend>>` → "Enviar recordatorio por WhatsApp" (condición: API no disponible)

7. **Asociaciones actor–caso de uso** (línea sólida sin flecha):
   - Enfermera/Técnica ↔ Registrar evaluación, Consultar expediente, Programar control, Recibir alerta, Consultar priorización
   - ACS ↔ Registrar modo offline, Reportar barrera
   - Familia ↔ (recibe notificaciones — puede modelarse como actor pasivo)
   - HIS ↔ Ejecutar reentrenamiento (proveedor de datos)
   - API WhatsApp ↔ Enviar recordatorio
   - Microred, MINSA ↔ Ver tablero

8. **Rectángulo de sistema** (`Insert → System Boundary`): encuadrar todos los casos de uso dentro de un rectángulo etiquetado "Sistema de Detección Temprana de Anemia Infantil"

9. **Exportar:** `File → Export → To Image (PNG/SVG)` para insertar en el documento

---

## D2 — Diagrama de Actividades con Swimlanes

**Dónde:** Entregable S2, Sección 6 (Representación del proceso) — **reemplaza la imagen base64 actual**  
**Por qué:** La guía pide explícitamente un diagrama con los 10 elementos del proceso (entrada, planificación, desarrollo, integración, pruebas, retroalimentación, entrega, medición, mejora, siguiente incremento). El diagrama de actividades UML con swimlanes modela el ciclo Scrum y el subciclo MLOps en paralelo, con nodos de decisión y fork/join.

### Instrucciones en PowerDesigner 16.x

1. `File → New → Activity Diagram` (UML 2.0)
2. **Crear swimlanes** (`Insert → Swimlane` o arrastrar desde toolbox):
   - Swimlane 1: **Equipo de Desarrollo** (izquierda)
   - Swimlane 2: **Personal de Salud / Posta** (centro)
   - Swimlane 3: **Pipeline MLOps** (derecha, activo desde Sprint 5)

3. **Nodo inicial** (círculo negro relleno) en Swimlane 1: "TO-BE de Semana 1 / Backlog priorizado"

4. **Actividades en Swimlane 1** (rectángulos con esquinas redondeadas):

```
[Swimlane 1 — Equipo de Desarrollo]
● Inicio
↓
Sprint Planning (seleccionar historias del incremento)
↓
Refinamiento de requisitos (historias con criterios INVEST)
↓
Análisis y Diseño (diagrama del incremento, modelo ER delta)
↓
Implementación (código en rama feature)
↓
Pruebas unitarias + integración (Pytest, cobertura ≥ 80%)
↓
Prueba de sincronización offline (15 min sin conexión)
↓
Code Review + SonarCloud (0 Blocker/Critical)
↓
CI/CD: Build → Test → Package (GitHub Actions)
↓
Despliegue a Posta Piloto
```

5. **Actividades en Swimlane 2 — Personal de Salud**:
```
Revisión del Incremento (acta de aceptación)
  ↓ (rombo de decisión)
¿Aprobado?
  → NO → (vuelve a Implementación — línea punteada de retorno)
  → SÍ → continúa
```

6. **Actividades que continúan en Swimlane 1**:
```
Medición de indicadores (burndown, cobertura de controles)
↓
Retrospectiva (plan de mejora)
↓
(Rombo de decisión): ¿Último sprint del incremento?
  → NO → Sprint Planning (siguiente sprint del mismo incremento)
  → SÍ → Siguiente Incremento / Fin
```

7. **Fork/Join para MLOps** (Swimlane 3, activo desde el Sprint 5):
   - **Fork** (barra horizontal gruesa) después de "Implementación": bifurca hacia Swimlane 3
   - En Swimlane 3:
     ```
     Ingesta de datos HIS
     ↓
     Limpieza y validación (pipeline MLOps)
     ↓
     (Rombo): ¿Datos suficientes (≥ 500 registros)?
       → NO → Posponer incremento (estado Pospuesto)
       → SÍ → Experimentación (RF vs. GBM en Colab)
     ↓
     Entrenamiento del modelo
     ↓
     Evaluación (precisión ≥ umbral clínico)
     ↓
     Publicación del artefacto (MLflow Registry)
     ↓
     Monitoreo de desempeño por zona
     ↓
     (Rombo): ¿Precisión degradada?
       → SÍ → Reentrenamiento
       → NO → Continúa monitoreo
     ```
   - **Join** (barra gruesa) que une el resultado del pipeline MLOps con el "Despliegue a Posta Piloto" del ciclo principal

8. **Nodo final** (círculo negro con anillo): "MVP completo en producción — todos los postas"

9. **Exportar** como PNG a 300 DPI para insertar en el documento Word/PDF

---

## D3 — Diagrama de Secuencia

**Dónde:**
- Entregable S2, Sección 6 (complemento del diagrama de actividades)
- Entregable S3-S4, Sección 11 (Plan del proyecto — flujo de interacción del Sprint 1)

**Por qué:** Modela el intercambio temporal de mensajes entre actores y componentes del sistema distribuido (offline → nube → API externa). Crítico para demostrar que la arquitectura offline-first con sincronización está correctamente diseñada.

### Instrucciones en PowerDesigner 16.x

1. `File → New → Sequence Diagram` (UML 2.0)
2. **Crear lifelines** (líneas de vida — rectángulos en la cabecera con línea punteada hacia abajo):

| Lifeline | Estereotipo | Descripción |
|---|---|---|
| `:Enfermera` | `actor` | Usuario primario (personal de posta) |
| `:AppMovil` | `boundary` | Aplicación móvil (Android/iOS) con SQLite |
| `:SincronizadorOffline` | `control` | Servicio de reconciliación de datos |
| `:APIBackend` | `control` | Servidor central (FastAPI/Django) |
| `:BaseDatosPostgres` | `entity` | Repositorio central en la nube |
| `:ServicioMLOps` | `control` | Endpoint del modelo predictivo (MLflow) |
| `:WhatsAppBusinessAPI` | `external` | Sistema externo de mensajería |

3. **Mensajes (flechas horizontales sólidas = síncronos, punteadas = asíncronos o retorno)**:

**Bloque 1 — Registro offline (fragmento `alt`)**:
```
Enfermera →→ AppMovil: registrarEvaluacion(niño_id, hemoglobina, peso, fecha)
AppMovil → AppMovil: guardarLocal(SQLite, marca_tiempo_captura)
AppMovil -->> Enfermera: confirmacionLocal()
```
*(Insertar fragmento `alt`: condición `[sin conexión]` para el bloque anterior)*

**Bloque 2 — Sincronización al recuperar conexión**:
```
AppMovil → SincronizadorOffline: iniciarSincronizacion(registros_pendientes)
SincronizadorOffline → APIBackend: enviarLoteRegistros(lote, marca_tiempo)
APIBackend → BaseDatosPostgres: insertarConResolucionConflictos(lote)
BaseDatosPostgres -->> APIBackend: confirmacion(ids_insertados)
APIBackend -->> SincronizadorOffline: acuseRecibo(ids_confirmados)
SincronizadorOffline → AppMovil: marcarSincronizado(ids)
AppMovil -->> Enfermera: sincronizacionCompleta()
```

**Bloque 3 — Priorización predictiva**:
```
Enfermera →→ AppMovil: consultarAgendaPriorizada()
AppMovil → APIBackend: getPriorizacion(lista_ninos)
APIBackend → ServicioMLOps: predecirRiesgo(features[hemoglobina, edad, altitud, adherencia])
ServicioMLOps -->> APIBackend: retornarRiesgo(score, nivel, explicacion)
APIBackend -->> AppMovil: agendaOrdenadaPorRiesgo(lista_priorizada)
AppMovil -->> Enfermera: mostrarAgenda(lista_priorizada)
```

**Bloque 4 — Notificación WhatsApp (fragmento `opt`)**:
```
APIBackend → WhatsAppBusinessAPI: enviarRecordatorio(phone, template_id, fecha_control)
WhatsAppBusinessAPI -->> APIBackend: webhook(estado: entregado/leido/fallido)
```
*(Fragmento `opt [WhatsApp no disponible]`: APIBackend → SMS Gateway)*

4. **Insertar fragmentos combinados** (`Insert → Combined Fragment`):
   - `alt`: "sin conexión" / "con conexión" para el bloque 1-2
   - `opt`: "WhatsApp no disponible" para el bloque 4
   - `loop [hasta sincronizar todos los registros pendientes]` alrededor del bloque 2

5. **Notas** (rectángulo con esquina doblada): agregar nota en la marca_tiempo del bloque 2: "La resolución de conflictos usa marca de tiempo de captura; prevalece el registro más reciente de la misma evaluación"

---

## D4 — Diagrama de Despliegue

**Dónde:** Entregable S2, Sección 9 (Herramientas de soporte)  
**Por qué:** Muestra dónde corre cada componente del sistema y cómo se comunican, siendo crítico para un sistema offline/cloud híbrido en zonas rurales.

### Instrucciones en PowerDesigner 16.x

1. `File → New → Deployment Diagram` (UML 2.0)
2. **Crear nodos** (`Insert → Node`):

| Nodo | Estereotipo | Contenido |
|---|---|---|
| `DispositivoMovilPosta` | `«device»` | AppMovil.apk + SQLite.db |
| `ServidorCloud` | `«server»` | APIBackend + PostgreSQL + ServicioMLOps |
| `PlatafomrCI_CD` | `«server»` | GitHub Actions runner |
| `PlatafomrMLOps` | `«server»` | Google Colab + MLflow |
| `WhatsAppBusinessAPI` | `«external system»` | Servicio externo Meta |
| `HIS_MINSA` | `«external system»` | Sistema legado de información de salud |

3. **Artefactos dentro de cada nodo** (`Insert → Artifact` dentro del nodo):
   - `DispositivoMovilPosta`: `AppMovil.apk`, `SQLite.db`
   - `ServidorCloud`: `APIBackend`, `PostgreSQL`, `ModeloPredictivo.pkl`
   - `PlatafomrCI_CD`: `pipeline_build_test_deploy.yml`
   - `PlatafomrMLOps`: `ExperimentosNotebook.ipynb`, `ModeloRegistrado.pkl`

4. **Relaciones de comunicación** (`Insert → Communication Path`):

| Origen | Destino | Protocolo / Estereotipo |
|---|---|---|
| `DispositivoMovilPosta` | `ServidorCloud` | `HTTPS/REST + JWT` · `«intermittent»` (conectividad variable) |
| `PlatafomrCI_CD` | `ServidorCloud` | `SSH/Docker deploy` |
| `PlatafomrMLOps` | `ServidorCloud` | `MLflow Model Registry pull` |
| `ServidorCloud` | `WhatsAppBusinessAPI` | `HTTPS/REST webhook` |
| `HIS_MINSA` | `PlatafomrMLOps` | `API REST / CSV export periódico` |

5. **Nota importante**: en el enlace `DispositivoMovilPosta → ServidorCloud`, agregar nota: "La sincronización solo ocurre cuando hay cobertura 3G/4G. El dispositivo opera en modo offline hasta recuperar conexión."

---

## D5 — Diagrama de Componentes

**Dónde:** Entregable S2, Sección 7 (Entregas incrementales) / Entregable S3-S4, Sección 12 (Dependencias)  
**Por qué:** Muestra cómo los módulos del software se ensamblan progresivamente por incremento y cuáles son sus dependencias, formalizando la trazabilidad técnica entre incrementos.

### Instrucciones en PowerDesigner 16.x

1. `File → New → Component Diagram` (UML 2.0)
2. **Crear componentes** (`Insert → Component`):

| Componente | Incremento | Interfaces ofrecidas | Depende de |
|---|---|---|---|
| `RegistroNominal` | INC-1 | `IRegistroEvaluacion`, `IExpedienteDigital` | `BaseDatosPostgres` |
| `AgendaAutomatica` | INC-2 | `IAgendaNTS134`, `IAlertaControl` | `IRegistroEvaluacion` |
| `SincronizacionOffline` | INC-3 | `ISyncConflict` | `SQLiteLocal`, `IAPIBackend` |
| `NotificadorWhatsApp` | INC-4 | `IEnvioMensaje` | `IAgendaNTS134`, `«external» WhatsAppBusinessAPI` |
| `ModeloPredictivo` | INC-5 | `IPredecirRiesgo` | `IRegistroEvaluacion`, `ISyncConflict`, `PipelineMLOps` |
| `TableroBIGestion` | INC-6 | `IDashboardMicrored` | Todas las interfaces anteriores |
| `«external» HIS` | — | `IConectorHIS` | — |

3. **Interfaces** (`Insert → Provided Interface` / `Required Interface`):
   - Línea con círculo al final = interfaz ofrecida (lollipop)
   - Línea con semicírculo = interfaz requerida (socket)
   - Conectar socket de un componente con el lollipop del que lo provee

4. **Marcar incrementos activos**: usar color de fondo o `«active in Sprint N»` como nota para distinguir qué componentes existen en cada incremento.

---

## D6 — Diagrama de Estados (Ciclo de vida del modelo predictivo)

**Dónde:** Entregable S2, Sección 8 (Riesgos — riesgo de degradación del modelo)  
**Por qué:** El riesgo de degradación/sesgo del modelo ML implica un ciclo de estados con transiciones controladas. El diagrama de estados UML modela exactamente este gobierno del modelo.

### Instrucciones en PowerDesigner 16.x

1. `File → New → State Machine Diagram` (UML 2.0)
2. **Nodo inicial** (círculo negro relleno): `[*]`
3. **Estados** (`Insert → State`):

| Estado | Acciones internas |
|---|---|
| `EntrenamientoInicial` | entry: cargar datos HIS validados; do: ejecutar pipeline Colab |
| `Pospuesto` | entry: notificar a equipo; do: esperar datos del RegistroNominal |
| `EnProduccion` | entry: publicar endpoint MLflow; do: servir predicciones |
| `BajoMonitoreo` | do: evaluar precisión desagregada por zona y grupo etario |
| `AlertaDegradacion` | entry: notificar al equipo de MLOps |
| `Reentrenamiento` | do: pipeline con datos actualizados + nuevas zonas |
| `Deprecado` | entry: retirar endpoint; do: registrar motivo |

4. **Transiciones** (`Insert → Transition` — flecha entre estados con evento/condición/acción):

```
[*] → EntrenamientoInicial
EntrenamientoInicial → EnProduccion [evaluación aprobada: precisión ≥ umbral clínico]
EntrenamientoInicial → Pospuesto [datos insuficientes: < 500 registros HIS limpios]
Pospuesto → EntrenamientoInicial [datos suficientes disponibles]
EnProduccion → BajoMonitoreo [monitoreoSemanalEjecutado]
BajoMonitoreo → EnProduccion [precisión ≥ umbral AND sin sesgo detectado]
BajoMonitoreo → AlertaDegradacion [precisión < umbral OR sesgo detectado en zona]
AlertaDegradacion → Reentrenamiento [aprobación del equipo MLOps]
Reentrenamiento → EnProduccion [evaluación aprobada]
Reentrenamiento → AlertaDegradacion [evaluación fallida — primer intento]
AlertaDegradacion → Deprecado [segundo ciclo de evaluación fallida]
Deprecado → [*]
```

5. **Guardia conditions** en formato `[condición]` sobre cada transición
6. **Eventos clave**: `monitoreoSemanalEjecutado`, `umbralesPrecisionViolados`, `nuevaZonaIncorporada`, `validacionClinicaFallida`

---

## D7 — Diagrama de Clases (Vista de dominio)

**Dónde:** Entregable S2, Sección 10 (Trazabilidad) / Entregable S3-S4, Sección 18 (Trazabilidad ampliada)  
**Por qué:** Formaliza las entidades del dominio que el sistema administra, haciendo trazable por qué los incrementos 1–3 son prerequisito del 5 (los datos que genera INC-1 alimentan el modelo de INC-5).

### Instrucciones en PowerDesigner 16.x

1. `File → New → Class Diagram` (UML 2.0, modo análisis — no es diagrama de código)
2. **Crear clases** (`Insert → Class`):

**Clase `Niño`**
```
- id_niño: String {PK}
- nombres: String
- apellidos: String
- fecha_nacimiento: Date
- DNI: String
- zona_rural: String
- altitud_msnm: Integer
```

**Clase `EvaluacionNutricional`**
```
- id_eval: String {PK}
- fecha: Date
- hemoglobina_g_dl: Decimal
- peso_kg: Decimal
- talla_cm: Decimal
- clasificacion_anemia: Enum {normal, leve, moderada, severa}
- registrado_offline: Boolean
- sincronizado: Boolean
```

**Clase `ControlProgramado`**
```
- id_control: String {PK}
- fecha_programada: Date
- fecha_realizada: Date [0..1]
- tipo_control: String
- estado: Enum {pendiente, realizado, vencido}
```

**Clase `AgendaNTS134`**
```
- id_regla: String {PK}
- edad_min_meses: Integer
- edad_max_meses: Integer
- frecuencia_dias: Integer
- tipo_suplemento: String
```

**Clase `PersonalSalud`**
```
- id_personal: String {PK}
- nombre: String
- rol: Enum {enfermera, tecnico_posta, ACS}
- posta_id: String {FK}
```

**Clase `PostaRural`**
```
- id_posta: String {PK}
- nombre: String
- distrito: String
- latitud: Decimal
- longitud: Decimal
- tiene_cobertura_movil: Boolean
```

**Clase `NotificacionWhatsApp`**
```
- id_notif: String {PK}
- phone_familia: String
- template_id: String
- estado_entrega: Enum {enviado, leido, fallido}
- fecha_envio: DateTime
```

**Clase `PrediccionRiesgo`**
```
- id_prediccion: String {PK}
- score_riesgo: Decimal [0..1]
- nivel: Enum {alto, medio, bajo}
- features_usadas: String[]
- version_modelo: String
- fecha: DateTime
```

**Clase `ModeloPredictivo`**
```
- version: String {PK}
- algoritmo: Enum {RandomForest, GradientBoosting}
- precision_global: Decimal
- precision_por_zona: Map<String, Decimal>
- fecha_entrenamiento: DateTime
- estado: Enum {en_produccion, en_reentrenamiento, deprecado}
```

**Clase `BarreraAcceso`**
```
- id_barrera: String {PK}
- tipo: Enum {pasaje, distancia, trabajo, enfermedad, otro}
- descripcion: String [0..1]
- fecha_reporte: Date
```

3. **Relaciones** (`Insert → Association` / `Generalization` / `Dependency`):

| Origen | Tipo | Destino | Multiplicidad | Descripción |
|---|---|---|---|---|
| `Niño` | Association | `EvaluacionNutricional` | 1 — 0..* | Un niño tiene muchas evaluaciones |
| `Niño` | Association | `ControlProgramado` | 1 — 0..* | Un niño tiene muchos controles programados |
| `Niño` | Association | `PrediccionRiesgo` | 1 — 0..* | Un niño tiene muchas predicciones |
| `Niño` | Association | `BarreraAcceso` | 1 — 0..* | Un niño puede tener barreras reportadas |
| `PersonalSalud` | Association | `EvaluacionNutricional` | 1 — 0..* | Un profesional registra muchas evaluaciones |
| `PersonalSalud` | Association | `PostaRural` | 0..* — 1 | Muchos profesionales pertenecen a una posta |
| `PostaRural` | Association | `MicredSalud` | 0..* — 1 | Muchas postas pertenecen a una microred |
| `ControlProgramado` | Dependency | `AgendaNTS134` | | El control se genera según la regla NTS |
| `ControlProgramado` | Association | `NotificacionWhatsApp` | 1 — 0..1 | Un control puede tener una notificación |
| `ModeloPredictivo` | Dependency | `EvaluacionNutricional` | | El modelo se entrena con datos de evaluaciones |

4. **Nota de dominio** (caja de texto): "Este es un diagrama de análisis del dominio, no de implementación. Las clases representan entidades del negocio de salud, no tablas de base de datos ni clases de código."

---

## Resumen de instrucciones de exportación (todos los diagramas)

| Paso | Instrucción en PowerDesigner 16.x |
|---|---|
| **Exportar como imagen** | `File → Export → To Image → PNG` · Resolución: 300 DPI mínimo para documentos impresos |
| **Exportar como SVG** | `File → Export → To Image → SVG` · Recomendado para documentos Word editables |
| **Exportar XMI** | `File → Export → XMI` · Para intercambio con otras herramientas UML |
| **Guardar el modelo** | `File → Save → *.pdm` (modelo PowerDesigner) · Mantener el archivo fuente |
| **Insertar en Word** | En Word: `Insertar → Imagen → Desde archivo` · Ajustar tamaño sin perder legibilidad (mín. 12cm de ancho para diagramas de secuencia y actividades) |
| **Título de figura** | Usar leyenda: "Figura N. [Tipo de diagrama] — [Descripción específica al proyecto]. Elaboración propia." |

---

## Orden recomendado de elaboración

Para el entregable de **esta semana (S3-S4)** y el de la semana pasada (S2):

1. **D7 Clases** primero: define el vocabulario del dominio que todos los demás diagramas usan
2. **D1 Casos de uso**: alcance funcional del sistema por actor
3. **D2 Actividades**: flujo del proceso (reemplaza la imagen base64 del S2)
4. **D4 Despliegue**: arquitectura física del sistema híbrido offline/cloud
5. **D3 Secuencia**: flujo detallado del registro offline → sincronización → priorización
6. **D5 Componentes**: arquitectura de módulos por incremento (útil para S3-S4)
7. **D6 Estados**: ciclo de vida del modelo predictivo (útil para S3-S4, Sección de Riesgos)

---

*Guía generada para el Entregable Semanas 3 y 4 — Curso Procesos de Software 2026-20*
