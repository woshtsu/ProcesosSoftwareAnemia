GUÍA DE TRABAJO SEMANA 5
(ADAPTADA): EJECUCIÓN DE LOS
PROCESOS PRINCIPALES PARA EL
PRIMER INCREMENTO (PMV)
Asignatura: Procesos de Software (Código: ASUC01702)
Nivel: 9.º período / Noveno ciclo (Electivo de Especialidad - Nivel Logrado)
Unidad II: Implementación del proceso de software
Resultado de Aprendizaje de la Unidad: Al finalizar la unidad, el estudiante será
capaz de adaptar los procesos del ciclo de vida del desarrollo de software con
consideraciones prácticas.
Ejes Temáticos Evaluados:
1. Categorías del proceso de software (Enfoque operativo en Procesos
Principales)
2. Modelos del ciclo de vida del software (Ejecución técnica del Primer
Incremento / Iteración / PMV)
1. OBJETIVO Y PRODUCTOS ESPERADOS
1.1 Objetivo General
Guiar al equipo de trabajo en la adaptación y ejecución operativa de los Procesos
Principales o Fundamentales del software (Especificación de Requisitos, Análisis y
Diseño, Implementación, Integración y Pruebas, y Despliegue), orientados de manera
directa a la construcción, verificación y entrega del Primer Incremento de Software /
Producto Mínimo Viable (PMV) del proyecto de asignatura.
1.2 Productos Esperados del Equipo (Entregables del PMV)
Cada equipo de trabajo deberá desarrollar y presentar los siguientes entregables
aplicados estrictamente al alcance del PMV de su solución tecnológica:
1. Especificación Operativa de Requisitos del PMV: Backlog del primer
incremento con Historias de Usuario priorizadas y Criterios de Aceptación
verificables.
2. Modelo de Diseño Arquitectónico del PMV: Diagrama de paquetes y
diagrama de despliegue de la arquitectura de software hexagonal y esquema de
datos simplificado para sostener las historias del incremento 1.
3. Construcción e Implementación del Código Fuente: Repositorio estructurado
con el código del PMV compilable y funcional.
4. Matriz de Pruebas e Integración del PMV: Registro de ejecuciones de casos
de prueba y reporte de Criterios de Terminación (Definition of Done).

5. Despliegue y Demostración Operativa: Versión ejecutable desplegada en
ambiente de pruebas demostrando la entrega funcional de valor.
2. CONEXIÓN METODOLÓGICA CON EL
PROYECTO DE ASIGNATURA
En la Unidad I se estableció la arquitectura de procesos y en las sesiones iniciales de la
Unidad II se definió la categorización de los procesos y el modelo de ciclo de vida
(tailoring). En esta guía adaptada para el noveno ciclo, el equipo debe ejecutar los
Procesos Principales para liberar el primer incremento funcional:
\[\text{Requisitos del PMV} \longrightarrow \text{Análisis/Diseño} \longrightarrow
\text{Implementación} \longrightarrow \text{Pruebas/Integración} \longrightarrow
\text{Despliegue del PMV}\]
Criterio de Rigor Profesional (IX Ciclo): Cada actividad del proceso principal debe
generar un Producto de Trabajo (Artifact) concreto y cumplir con su correspondiente
Criterio de Terminación (Definition of Done) antes de ser considerada completada.
3. CONCEPTOS CLAVE DEL PROCESO
PRINCIPAL APLICADOS AL PMV
• Especificación de Requisitos: Delimitación de las 3 a 5 historias de usuario
esenciales que constituyen el núcleo operativo del PMV sin incluir
características secundarias.
• Análisis y Diseño: Estructuración de la arquitectura, interfaces API y modelo de
datos indispensables para soportar la ejecución del primer incremento.
• Implementación (Construcción): Codificación del software en un repositorio
con control de versiones y políticas de ramificación.
• Integración y Pruebas (Validación): Verificación técnica continua para
certificar que el incremento carece de defectos críticos o bloqueantes.
• Despliegue: Disponibilización del software en un entorno ejecutable para
validar la generación inicial de valor organizacional.
4. ACTIVIDADES PRÁCTICAS A DESARROLLAR
EN EL PROYECTO
ACTIVIDAD 1: Delimitación y Especificación de Requisitos del PMV
(Proceso Principal: Requisitos)

Seleccione únicamente las Historias de Usuario clave que conforman el Primer
Incremento / PMV de su proyecto de asignatura.
Matriz 1.1: Alcance del Primer Incremento (PMV)
| Historia de Usuario  |     | Prioridad  | Criterios de       |              |
| -------------------- | --- | ---------- | ------------------ | ------------ |
| ID                   |     |            |                    | Producto de  |
| (Como... Quiero...   |     | (Valor /   | Aceptación (Given- |              |
| Historia             |     |            |                    | Trabajo      |
| Para...)             |     | Riesgo)    | When-Then)         |              |
Dado que ingreso datos
Ej. Como operador,
válidos, cuando
| quiero registrar la       |     |         |                          | Historias de  |
| ------------------------- | --- | ------- | ------------------------ | ------------- |
|                           |     | Alta /  | presiono guardar,        |               |
| HU-01  ficha del usuario  |     |         |                          | usuario       |
|                           |     | Medio   | entonces el registro se  |               |
| para iniciar su           |     |         |                          | priorizadas   |
almacena en la base de
seguimiento.
datos.
Dado que el sensor está
Ej. Como dispositivo,
activo, cuando se
| quiero transmitir      |     |              |                           | Documento de    |
| ---------------------- | --- | ------------ | ------------------------- | --------------- |
| HU-02                  |     | Alta / Alto  | sincroniza, entonces los  |                 |
| datos biométricos vía  |     |              |                           | especificación  |
datos se reciben sin
Bluetooth a la app.
pérdida.
| Ej. Como sistema,  |     |     | Dado que la lectura  |               |
| ------------------ | --- | --- | -------------------- | ------------- |
| quiero emitir una  |     |     | supera el umbral,    | Criterios de  |
HU-03  alerta básica visual  Alta / Alto  cuando se procesa,  aceptación
| ante lecturas  |     |     | entonces se muestra la  | aceptados  |
| -------------- | --- | --- | ----------------------- | ---------- |
| anómalas.      |     |     | notificación.           |            |

ACTIVIDAD 2: Diseño Arquitectónico y Estructuración Técnica
(Proceso Principal: Análisis y Diseño)
Diseñe los modelos y esquemas estrictamente necesarios para respaldar las historias del
PMV.
Matriz 2.1: Diseño del Incremento 1
Producto de
| Componente  | Descripción Técnica  |     |     | Criterio de  |
| ----------- | -------------------- | --- | --- | ------------ |
Trabajo
| del Diseño  | del PMV  |     |     | Terminación (DoD)  |
| ----------- | -------- | --- | --- | ------------------ |
Esperado
Ej. Patrón Hexagonal o
|               |                          |     | Diagrama de    | Revisado y aprobado  |
| ------------- | ------------------------ | --- | -------------- | -------------------- |
| Arquitectura  | capas desacopladas       |     |                |                      |
|               |                          |     | paquetes y de  | por el líder de      |
| de Software   | para conectar app móvil  |     |                |                      |
|               |                          |     | despliegue     | arquitectura.        |
y backend.
|     | Ej. Esquema relacional  |     | Script DDL o  | Script ejecutado  |
| --- | ----------------------- | --- | ------------- | ----------------- |
Modelo de
o colecciones NoSQL  diagrama entidad- satisfactoriamente en la
Datos
|                 | para usuarios y alertas.  |     | relación        | base de datos.            |
| --------------- | ------------------------- | --- | --------------- | ------------------------- |
|                 | Ej. Endpoints REST        |     | Especificación  |                           |
| Contratos de    |                           |     |                 | Contratos definidos y     |
|                 | JSON para la recepción    |     | OpenAPI /       |                           |
| API / Interfaz  |                           |     |                 | validados por el equipo.  |
|                 | de eventos de alerta.     |     | Swagger         |                           |

ACTIVIDAD 3: Construcción e Implementación del Código Fuente
(Proceso Principal: Implementación)
Desarrolle el código fuente de las historias de usuario del PMV aplicando estándares de
programación y control de versiones.
Matriz 3.1: Control de Construcción e Implementación
Criterio de
| Módulo /  | Lenguaje /  | Estrategia de  | Producto de  |     |
| --------- | ----------- | -------------- | ------------ | --- |
Terminación
| Componente  | Framework  | Ramificación (Git) Trabajo  |     |     |
| ----------- | ---------- | --------------------------- | --- | --- |
(DoD)
Código compilado
| Frontend /  | Ej. Flutter /  | feature/hu01-                    | Código fuente  |                      |
| ----------- | -------------- | -------------------------------- | -------------- | -------------------- |
|             |                | registro-usuario en repositorio  |                | sin advertencias ni  |
| App Móvil   | React Native   |                                  |                |                      |
errores.
|                | Ej. Node.js /  | feature/hu02- |              | Análisis estático de  |
| -------------- | -------------- | ------------- | ------------ | --------------------- |
| Backend / API  |                |               | Endpoints    |                       |
|                | Python         | conexion-     |              | código (linter)       |
| Services       |                | bluetooth     | ejecutables  |                       |
|                | FastAPI        |               |              | aprobado.             |
|                | Ej.            |               |              | Base de datos         |
|                |                | feature/hu03- | Scripts de   |                       |
| Base de Datos  | PostgreSQL /   |               |              | poblada con datos     |
alertas-base
migración
|     | MongoDB  |     |     | de prueba.  |
| --- | -------- | --- | --- | ----------- |

ACTIVIDAD 4: Verificación, Pruebas y Criterios de Terminación
(Proceso Principal: Pruebas e Integración)
Diseñe y ejecute casos de prueba para garantizar la calidad y estabilidad del PMV antes
de su demostración.
Matriz 4.1: Registro de Pruebas del PMV
Tipo de Prueba
|                          |     |                | Resultado     | Criterio de  |
| ------------------------ | --- | -------------- | ------------- | ------------ |
| ID Caso Escenario de     |     | (Unitaria /    |               |              |
|                          |     |                | Esperado vs.  | Terminación  |
| Prueba  Prueba Evaluado  |     | Integración /  |               |              |
|                          |     |                | Real          | (DoD)        |
UI)
| Validación de         |     |           | Formulario       | 100% de pruebas  |
| --------------------- | --- | --------- | ---------------- | ---------------- |
| CP-01  formulario de  |     | Unitaria  | rechaza campos   | unitarias        |
| registro de usuario.  |     |           | nulos / Exitoso  | ejecutadas.      |
Se extrae la
| Recepción y parseo  |     |     |     | Cobertura de  |
| ------------------- | --- | --- | --- | ------------- |
lectura
| CP-02  de datos de la  |     | Integración  |     | código en lógica  |
| ---------------------- | --- | ------------ | --- | ----------------- |
correctamente /
| pulsera/sensor.  |     |     |     | principal > 80%.  |
| ---------------- | --- | --- | --- | ----------------- |
Exitoso
Cero defectos
| Generación y  |     |     | Notificación  |     |
| ------------- | --- | --- | ------------- | --- |
críticos o
| CP-03  despliegue de alerta  |     | Sistema / UI  | aparece en < 2 s /  |     |
| ---------------------------- | --- | ------------- | ------------------- | --- |
bloqueantes
| visual en pantalla.  |     |     | Exitoso  |     |
| -------------------- | --- | --- | -------- | --- |
abiertos.

ACTIVIDAD 5: Despliegue y Demostración de Entrega de Valor (Proceso
Principal: Despliegue)
Despliegue el PMV en un entorno funcional (emulador, servidor local o nube) y
demuestre el valor operativo generado.
Matriz 5.1: Valor Operativo Generado por el PMV
Incremento  Funcionalidad  Resultado Directo  Indicador de Valor /
Liberado  Operativa Entregada  para el Usuario  Operativo Asociado
|     |     | Detección y  |     | Ej. Tiempo de  |
| --- | --- | ------------ | --- | -------------- |
Registro de usuario,
| Incremento 1  |     | visualización  |     | respuesta ante  |
| ------------- | --- | -------------- | --- | --------------- |
recepción de datos y
| (PMV)  |     | automática de eventos incidentes reducido de  |     |     |
| ------ | --- | --------------------------------------------- | --- | --- |
emisión de alerta básica.
|     |     | de riesgo.  |     | 2.5 h a 5 segundos.  |
| --- | --- | ----------- | --- | -------------------- |

5. ESTRUCTURA DEL ENTREGABLE GRUPAL
(INFORME + REPOSITORIO)
Cada equipo deberá subir a la plataforma virtual un paquete comprimido o enlace
institucional conteniendo la siguiente estructura:
1. INFORME TÉCNICO APLICADO (PDF):
   1.1 Carátula e Integrantes
   1.2 Delimitación de Requisitos del PMV (Matriz 1.1)
   1.3 Diseño Arquitectónico y Estructura de Datos (Matriz 2.1 y
Diagramas)
   1.4 Evidencia de Pruebas e Integración del PMV (Matriz 4.1 y
capturas)
   1.5 Demostración del Despliegue y Entrega de Valor (Matriz 5.1)
2. ENTREGABLE DE CÓDIGO FUENTE (GitHub / GitLab):
   2.1 Código fuente estructurado del PMV
   2.2 Archivo README.md con instrucciones de compilación y ejecución
   2.3 Scripts de base de datos y casos de prueba automatizados

6. RÚBRICA DE EVALUACIÓN PARA LA
SEMANA 5 (20 PUNTOS)
La evaluación se realizará aplicando criterios de rigor técnico para proyectos del noveno
ciclo:
| Criterio de  | Excelente (4  |                |                 |                 |
| ------------ | ------------- | -------------- | --------------- | --------------- |
|              |               | Bueno (3 pts)  | Básico (2 pts)  | Inicial (1 pt)  |
| Evaluación   | pts)          |                |                 |                 |
|              | Delimita las  |                | Presenta        | Define el       |
Delimita
| Especificación  | historias de  |     | historias de  | alcance del  |
| --------------- | ------------- | --- | ------------- | ------------ |
adecuadamente
| de Requisitos del usuario del  |     |     | usuario del  | PMV de forma  |
| ------------------------------ | --- | --- | ------------ | ------------- |
las historias de
| PMV  | PMV con rigor  |     | PMV de forma  | genérica sin  |
| ---- | -------------- | --- | ------------- | ------------- |
usuario del PMV
|     | técnico,  |     | incompleta o  | estructura de  |
| --- | --------- | --- | ------------- | -------------- |

|     | priorización       | y sus criterios de ambiguamente  |              | historias de  |
| --- | ------------------ | -------------------------------- | ------------ | ------------- |
|     | clara y criterios  | aceptación.                      | redactadas.  | usuario.      |
de aceptación
verificables.
Diseña y
|     | documenta los  |     | Presenta  |     |
| --- | -------------- | --- | --------- | --- |
Diseña la
|     | diagramas de  |     | diagramas de  | No presenta  |
| --- | ------------- | --- | ------------- | ------------ |
arquitectura del
| Diseño  | arquitectura,  |     | diseño  | evidencias de  |
| ------- | -------------- | --- | ------- | -------------- |
PMV con
| Arquitectónico  | modelos de  |     | incompletos o  | diseño  |
| --------------- | ----------- | --- | -------------- | ------- |
esquemas y
| del Incremento 1 datos y API  |     |     | desvinculados  | arquitectónico  |
| ----------------------------- | --- | --- | -------------- | --------------- |
modelos de
|     | necesarios para  |     | de las historias  | para el PMV.  |
| --- | ---------------- | --- | ----------------- | ------------- |
datos claros.
|     | sostener el  |     | del PMV.  |     |
| --- | ------------ | --- | --------- | --- |
PMV.
Implementa el
código del PMV
|     | en un  | Construye e  | El código  | El código  |
| --- | ------ | ------------ | ---------- | ---------- |
Construcción e  repositorio  integra el código presentado está  fuente no
Implementación  ordenado,  fuente del PMV  incompleto o no  corresponde al
del Código  siguiendo  funcional en el  compila  PMV o no fue
|     | patrones y  | repositorio.  | correctamente.  | entregado.  |
| --- | ----------- | ------------- | --------------- | ----------- |
estrategias de
ramificación.
Ejecuta casos de
|     | prueba  | Documenta la  | Presenta pruebas No demuestra  |     |
| --- | ------- | ------------- | ------------------------------ | --- |
Pruebas y  estructurados y  ejecución de  superficiales o  pruebas ni
Criterios de  demuestra el  casos de prueba  sin registro de  define criterios
Terminación  cumplimiento  y verifica la  evidencias  de terminación
| (DoD)  | riguroso del   | terminación de    | claras de   | para las      |
| ------ | -------------- | ----------------- | ----------- | ------------- |
|        | Definition of  | las actividades.  | ejecución.  | actividades.  |
Done.
|     | Despliega la  |               | Muestra una  |     |
| --- | ------------- | ------------- | ------------ | --- |
|     | versión       | Despliega el  | ejecución    |     |
El software no
|                | ejecutable del   | PMV de forma     | parcial del    |                   |
| -------------- | ---------------- | ---------------- | -------------- | ----------------- |
| Despliegue y   |                  |                  |                | es ejecutable ni  |
|                | PMV y            | funcional en un  | software con   |                   |
| Entrega de     |                  |                  |                | demuestra         |
|                | demuestra        | ambiente de      | fallos         |                   |
| Valor del PMV  |                  |                  |                | entrega de valor  |
|                | técnicamente el  | pruebas o        | operacionales  |                   |
inicial.
|     | impacto y valor  | emulador.  | durante la     |     |
| --- | ---------------- | ---------- | -------------- | --- |
|     | generado.        |            | demostración.  |     |
Puntaje Máximo: 20 puntos