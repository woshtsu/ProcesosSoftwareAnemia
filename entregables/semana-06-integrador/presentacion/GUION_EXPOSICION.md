# Guion de exposición grupal: 7 minutos y 7 diapositivas

- **Fuente de las diapositivas:** `Presentacion_Integrador.md` (Marp). Las notas del orador de cada diapositiva contienen el detalle del pitch.
- **Duración:** los pitches de la consigna suman 10 min (1,5 + 1,5 + 1,5 + 1,5 + 2,0 + 1,0 + 1,0) y la exposición dura 7 min. Se reduce al 70 %: **1:05 · 1:05 · 1:05 · 1:05 · 1:25 · 0:40 · 0:35 = 7:00**.
- **Expositores:** la asignación por rol es una **propuesta**; el equipo decide ([COMPLETAR: confirmar quién expone cada diapositiva]). Los tres integrantes deben dominar todo el material, porque la defensa individual (C8) pregunta a cada uno por el repositorio, la arquitectura y las pruebas.

## 1. Cronograma de la exposición

| Diap. | Tema | Tiempo | Acumulado | Expone (propuesta) | Rol del informe |
| --- | --- | --- | --- | --- | --- |
| 1 | Problema AS-IS vs. TO-BE, cadena de valor e indicador 3 → 1 | 1:05 | 1:05 | Porras Veli, Ricardo | Ingeniero de Proceso |
| 2 | Tailoring: matriz de factores, ciclo adaptado, rechazo de Cascada | 1:05 | 2:10 | Porras Veli, Ricardo | Ingeniero de Proceso |
| 3 | Arquitectura: C4 nivel 2, ADR ➔ NFR, protocolos | 1:05 | 3:15 | Auqui Huincho, Tania | Ingeniera de Desarrollo y Prototipado |
| 4 | Pruebas: pirámide, cobertura, carga, DoD | 1:05 | 4:20 | Huamani Rodriguez, Jean Piero | Ingeniero de Calidad y Mejora |
| 5 | Demo operativa (en vivo en staging; respaldo: video) | 1:25 | 5:45 | Auqui Huincho, Tania (apoyo: Huamani R.) | Ingeniera de Desarrollo y Prototipado |
| 6 | Tablero de métricas: proceso, producto, valor | 0:40 | 6:25 | Huamani Rodriguez, Jean Piero | Ingeniero de Calidad y Mejora |
| 7 | Trazabilidad, conclusiones e INC-2 | 0:35 | 7:00 | Porras Veli, Ricardo | Ingeniero de Proceso |

Reparto de tiempo propuesto: Porras V. 2:45, Auqui H. 2:30, Huamani R. 1:45.

## 2. Guion por diapositiva (texto para decir en voz alta)

### Diapositiva 1 (0:00 a 1:05), Porras V.

"En Junín, el seguimiento de la anemia infantil se pierde porque el proceso es reactivo: se registra tres veces a mano (historia clínica, tarjeta de control y digitación en el HIS), la agenda se calcula a mano y las barreras familiares se descubren cuando el niño ya abandonó. Son las brechas B1 a B6. Nuestra propuesta es un proceso preventivo: la cadena de valor es datos, software, decisión e impacto. El software no diagnostica; deja el dato validado para que el profesional decida a tiempo. El Incremento 1 ataca la brecha B1, y el indicador de valor que ya podemos sostener es pasar de tres registros manuales por evaluación a un expediente digital único. Es un resultado de diseño con datos sintéticos; no afirmamos tiempos de respuesta que no medimos."

### Diapositiva 2 (1:05 a 2:10), Porras V.

"Cinco factores del proyecto están en nivel alto: incertidumbre, complejidad, riesgo, integración y datos o IA. Con una matriz ponderada de ocho criterios, el enfoque híbrido (iterativo-incremental, con Scrum y prácticas DevOps, y MLOps diferido al incremento 5) obtuvo 4,75, frente a 3,85 de Kanban con DevOps y 2,95 del enfoque tradicional. Rechazamos la Cascada pura, que suma 8 de 30 en la comparación: congela requisitos al inicio y valida al final, y nuestros requisitos de IA y de conectividad no están cerrados. También rechazamos Scrum puro: sin ingeniería continua, es decir pruebas, análisis estático e imagen en integración continua, no hay evidencia por sprint. Lo ajustamos a tres personas: sprints de dos semanas y una matriz RAE de tres roles."

### Diapositiva 3 (2:10 a 3:15), Auqui H.

"Esta es la vista C4 de contenedores: una PWA, la API FastAPI con núcleo hexagonal y PostgreSQL 16, con SQLite en desarrollo. No hay API gateway, microservicios ni caché de servidor, y lo decimos a propósito: el ADR-001 descarta microservicios porque con tres personas y un incremento sería distribución prematura; el hexágono deja puertos para evolucionar. Tres ADR cubren los requisitos no funcionales: el ADR-003, PostgreSQL con UNIQUE en el DNI, llaves foráneas y CHECK, protege la integridad y la concurrencia; el ADR-006, consultas por lotes, bajó la latencia p95 del reporte de 2 200 a 74 milisegundos; el ADR-002, PWA con borrador local, da disponibilidad de la interfaz con red intermitente. El protocolo es REST con JSON y OpenAPI 3.1; descartamos WebSockets y gRPC porque el incremento 1 no necesita tiempo real."

### Diapositiva 4 (3:15 a 4:20), Huamani R.

"La pirámide tiene 62 pruebas unitarias en la base, que corren en menos de un segundo sin base de datos, 11 de integración y API, y 4 E2E con Playwright: 62 más 11 más 4 son 77 pruebas automatizadas declaradas en el tag, y el 1 de octubre reprodujimos 73. La carga es una verificación aparte y no cuenta como prueba. La cobertura es de 99 % con ramas; el umbral de nuestra Definition of Done es 80 %. En carga, con Locust, 50 usuarios durante 60 segundos, el p95 agregado bajó de 310 a 58 milisegundos tras corregir DEF-01, con 39,6 solicitudes por segundo y cero fallos. La DoD se cumple: cobertura sobre 80 %, Ruff con cero hallazgos y suite en verde. Con transparencia: de esas 77, el 1 de octubre reprodujimos 73 (unitarias y de integración), con 99,07 % y Ruff en cero; las E2E, PostgreSQL y la carga se reportan según el tag. SonarCloud está preparado, pero no ejecutado."

### Diapositiva 5 (4:20 a 5:45), Auqui H. con apoyo de Huamani R.

Demo en vivo en staging (preferible) o video de respaldo `pmv_fastapi/docs/evidencias/demo_pmv.mp4`.

1. 0:00 "El PMV entrega las cinco historias; la consigna exige HU-01 a HU-03."
2. 0:10 Registrar un niño sintético; mostrar la vista previa de la hemoglobina ajustada y su clasificación (HU-01 y HU-03).
3. 0:30 Enviar un dato inválido; mostrar el mensaje por campo (HU-03).
4. 0:45 Abrir el expediente, el listado de seguimiento y un nuevo control (HU-02 y HU-04).
5. 1:00 Mostrar el reporte del periodo en JSON o CSV (HU-05) y `/docs` (OpenAPI).
6. 1:10 "Staging con Docker Compose, API y PostgreSQL 16, con integración continua; no hay despliegue en la nube. Aún no tenemos acta de aceptación de un usuario final: el incremento está verificado técnicamente y pendiente de aceptación." [COMPLETAR: acta o correo de aceptación, si se logra antes de la defensa]

Plan B: si la demo en vivo falla, reproducir el video (duración [COMPLETAR]) y mostrar la captura 07 (vista móvil).

### Diapositiva 6 (5:45 a 6:25), Huamani R.

"En proceso: el incremento 1 planificó 21 puntos en dos sprints y entregó las cinco historias, 21 de 21; la entrega fue el 30/09, dos días después del hito H1 del 28/09, desviación registrada en la retrospectiva. En producto: dos defectos mayores, ambos cerrados, dan 2,0 defectos por KLOC con cero abiertos, y la cobertura es del 99 %. En valor, lo único medido es el paso de 3 a 1 registros por evaluación, con datos sintéticos; la reducción de pérdida de seguimiento exige una posta, una línea base y los incrementos siguientes."

### Diapositiva 7 (6:25 a 7:00), Porras V.

"La trazabilidad une la brecha B1 con el registro único, el modelo híbrido, los ADR 001, 003, 004 y 005, los casos de prueba y las historias HU-01 a HU-05, hasta el indicador 3 a 1. Tres conclusiones: el modelo híbrido entregó el incremento completo con trazabilidad extremo a extremo; la cobertura sola no habría revelado DEF-01 ni DEF-02, los encontraron la carga y el E2E; y demostramos valor técnico, no impacto asistencial. El siguiente incremento es INC-2: agenda automática y alertas, en el sprint 3, para la Unidad III. Gracias."

## 3. Defensa oral individual (5 min por integrante): preguntas probables

Las respuestas son breves y salen del informe y del repositorio. Cada integrante debe poder responder cualquiera de ellas (criterio C8) y usar la jerga técnica con precisión (criterio C7).

### Proceso y tailoring (C7)

| Pregunta | Respuesta breve |
| --- | --- |
| ¿Por qué descartaron la Cascada? | Suma 8/30 en la comparación; exige congelar requisitos al inicio y validar al final, pero la IA, la mensajería y el modo sin conexión no están cerrados y el feedback del personal es frecuente (Informe §2.2). |
| ¿Por qué no Scrum puro? | Scrum es un marco de gestión y no define cómo automatizar la entrega. Sin DevOps (pruebas, Ruff, imagen en CI) no hay evidencia por sprint. |
| ¿Qué es el tailoring que hicieron? | Ajustar el enfoque al contexto: equipo de 3, Scrum liviano de sprints de dos semanas, matriz RAE de tres roles, DevOps con pruebas y CI, y MLOps diferido a INC-5 por falta de datos (Informe §3.1, Tabla 20). |
| ¿Cómo se calculó el 4,75? | Matriz de ocho criterios ponderados (15 % adaptabilidad, riesgos, entrega incremental y retroalimentación; 10 % integración, automatización, datos/IA y participación del usuario). Alt. 1 = 4,75; Alt. 2 = 3,85; Alt. 3 = 2,95. |
| ¿Cómo mostraron el avance real? | Planificado frente a completado: 21 SP planificados en dos sprints (13 + 8) y 21/21 completados. No se muestra una serie diaria, porque todos los commits del tag son del 30/09; el burndown de S3-4 es simulado y se rotula así. Hubo +2 días respecto del hito H1 (28 a 30/09). |
| ¿Qué valor midieron realmente? | Solo 3 registros por evaluación → 1 (por diseño, con datos sintéticos). La pérdida de seguimiento requiere INC-2, línea base y una posta. |

### Arquitectura y repositorio (C7 y C8)

| Pregunta | Respuesta breve |
| --- | --- |
| ¿Por qué un monolito y no microservicios, gateway o caché? | ADR-001: equipo de 3 y un incremento; el núcleo hexagonal (dominio, aplicación con puertos `RepositorioNinos` y `Reloj`, adaptadores) permite evolucionar. La única caché es la de interfaz (service worker). |
| Explique la arquitectura hexagonal en su código. | `app/domain` sin frameworks (entidades, reglas clínicas, errores); `app/application` con `ServicioExpediente` y puertos; `adapters/entrada/http` (FastAPI y DTO Pydantic) y `adapters/salida/persistencia` (`sqlalchemy_repo.py` y `memoria.py`); `main.py` compone con `crear_app`. |
| ¿Cómo garantizan que no haya dos niños con el mismo DNI? | ADR-003: `UNIQUE(dni)` en PostgreSQL con CHECK de 8 dígitos; la API responde 409 ante un duplicado. La base repite las reglas del dominio (defensa en profundidad). |
| ¿Por qué REST y no WebSockets o gRPC? | ADR-005: el INC-1 no necesita tiempo real; REST/JSON con OpenAPI 3.1 da interoperabilidad y errores por campo en español. |
| ¿Cuál fue el defecto más importante y cómo se corrigió? | DEF-01: N+1 en `GET /api/reportes/periodo`, p95 de 2 200 ms con 50 usuarios; consultas por lotes (ADR-006, rama `fix/def-01-reporte-n-mas-1`); p95 de 74 ms. DEF-02: conteo en UTC perdía registros posteriores a las 19:00; corregido con zona UTC-5 y CP-16. |
| ¿Dónde está el código, el tag y cómo se despliega? | Repositorio woshtsu/ProcesosSoftwareAnemia; PMV en `pmv_fastapi/`; tag `v1.0-PMV` (commit 9ce90c3, rama `entrega-s5-s7`; mismo código que `main`); `docker compose up -d --build` y `python -m scripts.cargar_datos_prueba`. |
| ¿Qué limitaciones tiene el PMV? | Sin autenticación (solo `X-Usuario`), registro definitivo con conexión (cola sin conexión en INC-3), puntos de corte por confirmar con la microred, datos sintéticos, zona horaria fija UTC-5, sin despliegue en la nube. |

### Pruebas y calidad (C7 y C8)

| Pregunta | Respuesta breve |
| --- | --- |
| ¿Cuántas pruebas hay y de qué tipo? | 62 unitarias (24 reglas clínicas, 24 entidades, 14 casos de uso), 11 de integración y API, 4 E2E con Playwright y 1 escenario Locust; 62 + 11 + 4 = 77 declaradas en el tag; 73 reproducidas el 01/10 (sin E2E). La carga es una verificación aparte y no cuenta como prueba. |
| ¿Qué significa 99 % de cobertura? | Pytest-cov con ramas: 641 sentencias con 2 sin cubrir y 98 ramas con 4 parciales; en la reproducción del 01/10, 99,07 %. El umbral de la DoD es 80 %. |
| ¿Cómo hicieron la prueba de carga y qué mostró? | Locust, `PersonalPosta`, 50 usuarios, 60 s: p95 agregado 310 → 58 ms, 39,6 req/s, 0 fallos. No mide conectividad rural. |
| ¿Cuál es su Definition of Done? | Criterios Dado–Cuando–Entonces con prueba automatizada, 0 fallidas, cobertura ≥ 80 %, Ruff 0, funcionalidad en interfaz y API, contrato OpenAPI actualizado. |
| ¿Usan SonarQube/SonarCloud? | Está preparado (`sonar-project.properties`, paso condicionado a `SONAR_TOKEN`), pero sin organización real ni análisis ejecutado; el análisis estático obligatorio es Ruff. |
| ¿Hay evidencia de CI en verde? | El pipeline está en `.github/workflows/ci.yml` (raíz). Falta la captura de una ejecución en verde en GitHub Actions: [COMPLETAR]. |
| ¿Se validó con un usuario final? | No hay acta de aceptación. El incremento está verificado técnicamente y pendiente de aceptación ([COMPLETAR] si se consigue antes de la defensa). |

## 4. Lista de verificación antes de exponer

- [ ] Ensayo cronometrado: 7:00 como máximo; si se excede, recortar la diapositiva 5 (video o demo) y no las demás.
- [ ] Staging levantado o video listo en el equipo de exposición (respaldo).
- [ ] PPTX abierto con notas del orador y PDF de respaldo.
- [ ] Cada integrante lee el informe (§2 a §4) y repasa las tablas de preguntas.
- [ ] Resolver los [COMPLETAR] visibles: aceptación del usuario final (diapositiva 5) y, si procede, el reparto de expositores.
