# ADR-013 — Visita domiciliaria priorizada: puntaje explicable propuesto por el equipo

**Contexto.** La brecha B4 pide apoyar al personal a decidir a qué familias visitar primero: hay más niños con anemia que visitas posibles por semana. Ninguna norma del MINSA define un puntaje de prioridad; sí hay hechos que el sistema ya conoce (severidad, controles vencidos, inasistencias de RF-09) y uno nuevo (las visitas realizadas).

**Decisión.** Se agrega la **visita domiciliaria** como hecho persistido y una **lista priorizada** calculada en el dominio (`app/domain/service/visitas.py`) con un puntaje **determinista y explicable**, de 0 a 100, cuya composición se devuelve en cada respuesta. **Los pesos son una propuesta del equipo del proyecto, no una norma del MINSA**; deben validarse con la microred antes de usarse como criterio operativo y por eso están versionados en `PESOS_V1` (`VISITA-V1`), igual que `ESQUEMA_AGENDA_V1` (ADR-007).

Quién entra: solo **niños en tratamiento**, es decir, activos cuya **última evaluación tiene anemia**. Componentes (suman como máximo 100; con barreras críticas, 115):

| Componente | Máximo | Cómo se calcula |
|---|---|---|
| `SEVERIDAD` | 40 | Última evaluación: severa 40, moderada 25, leve 10. |
| `CONTROL_VENCIDO` | 30 | Proporcional a los días de atraso del control más vencido de la agenda (ADR-007), con tope de 60 días. |
| `INASISTENCIAS` | 15 | 5 puntos por cada inasistencia registrada (RF-09) con fecha programada en los últimos 90 días. |
| `ULTIMA_VISITA` | 15 | Proporcional a los días desde la última visita, con tope de 90 días; **sin ninguna visita, el máximo**. |
| `BARRERA_CRITICA` | 15 | Solo con alerta de barreras críticas (INC-4): 15 si la prioridad es ALTA, 8 si es MEDIA. |

**Actualización del Incremento 4 (`VISITA-V2`, ADR-014).** Se agrega un quinto componente, `BARRERA_CRITICA`, **solo** a los niños que tienen una alerta de barreras críticas (HIST-4.4): **15 puntos** si la alerta es de prioridad ALTA y **8** si es MEDIA (propuesta del equipo, igual que los demás pesos). Un niño sin barreras críticas no lleva el componente: su puntaje y su lista de componentes no cambian, así que el rango es de 0 a 100 sin barreras y de **0 a 115 con ellas** (máximo teórico: 100 + 15). Se eligió sumar en lugar de repartir el peso entre cinco componentes para no alterar el orden ya validado por el personal ni el puntaje de quienes no tienen barreras; el costo es un máximo variable, que la interfaz explica («hasta 115 si el niño tiene barreras críticas»). `PESOS_V1` se conserva como referencia; la versión vigente es `PESOS_V2` (`VISITA-V2`).

Desempate: mayor puntaje, luego más días de control vencido y luego código/nombre, para que el orden sea reproducible.

*Justificación de los pesos (hipótesis a validar).* La severidad pesa más porque define el riesgo clínico; el control vencido es la señal de que el niño salió del circuito de atención; las inasistencias confirman que la familia ya fue citada y no acudió (la misma lógica que sube la prioridad de la alerta en ADR-010); la última visita evita visitar siempre a los mismos y asegura que quien nunca fue visitado entre en la lista. Los topes (60 y 90 días) evitan que un solo componente domine sin límite.

Endpoints: `GET /api/visitas/priorizadas?establecimiento=&limite=` (límite de 1 a 200, 20 por defecto; 422 fuera de rango; la respuesta trae posición, niño, clasificación, días vencidos, inasistencias recientes, última visita, puntaje y `componentes[]` con descripción, valor observado, puntos y máximo), `POST /api/ninos/{id}/visitas` (201; 404; 409 si ya hay una visita ese día; 422 si la fecha es futura o anterior al nacimiento, el resultado es inválido, solo una visita `REALIZADA` puede indicar si consume el suplemento, o las observaciones superan 500 caracteres; `registrado_por` sale de la sesión) y `GET /api/ninos/{id}/visitas`. La visita también llega por la cola sin conexión (`REGISTRAR_VISITA`, ADR-012). Tabla `visita_domiciliaria` con `UNIQUE (nino_id, fecha)` y `CHECK` del resultado, del consumo y de su coherencia.

Interfaz: pestaña «Visitas» con la lista priorizada, el desglose del puntaje al pulsarlo y el formulario de visita; sección «Visitas domiciliarias» en el expediente.

**Alternativas descartadas.** (a) *Orden solo por severidad*: dejaría siempre arriba a los mismos y no reflejaría el abandono del seguimiento. (b) *Puntaje opaco o aprendido de datos*: no hay datos históricos de visitas para entrenarlo y el personal necesita ver por qué un niño está primero. (c) *Reutilizar la prioridad de las alertas (ALTA/MEDIA/BAJA)*: mide solo el atraso del control y no considera la severidad ni las visitas ya hechas. (d) *Presentar los pesos como norma*: no existe tal norma.

**Consecuencias.** (+) La lista es reproducible y auditable: el mismo estado produce el mismo orden. (+) Cambiar un peso es un cambio de una constante versionada, con pruebas de frontera. (+) La respuesta explica el puntaje; la interfaz lo muestra. (−) **Los pesos no están validados clínicamente**; son una hipótesis de trabajo y la lista apoya, no reemplaza, el criterio del personal. (−) No considera la distancia ni la geografía de las visitas (planificación de rutas), la edad del niño ni la adherencia declarada al suplemento; quedan como mejora futura. (−) El cálculo carga los niños en tratamiento del establecimiento; con el dataset completo hay que medir el tiempo de respuesta (límite máximo de 200 filas en la respuesta).
