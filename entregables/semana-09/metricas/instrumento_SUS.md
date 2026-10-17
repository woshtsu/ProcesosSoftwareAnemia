# Instrumento de satisfacción del usuario: Escala de Usabilidad del Sistema (SUS)

**Indicador complementario de V6 (satisfacción real; M3.2, G-03 / Q3.2).** Estado: **pendiente de aplicación con el Product Owner y el personal de salud**. No se reporta ningún valor SUS en este corte porque no se ha aplicado el cuestionario a usuarios reales; cualquier número sería inventado.

- Sistema evaluado: Sistema de Detección Temprana de Anemia Infantil en Zonas Rurales de Junín (PMV, Incremento 1 v1.0-PMV y Incremento 2 avance v1.5.0-inc2-avance).
- Quién responde: personal de salud del establecimiento (enfermería, técnico, obstetra) y el Product Owner, después de usar el sistema en una tarea guiada (registrar un niño, abrir su expediente y su agenda, revisar la pestaña Alertas, generar el reporte del periodo). Mínimo recomendado: 5 respondientes por versión.
- Cuándo: al cierre de la revisión del hito del Incremento 2 y de nuevo al liberar el Incremento 2 completo. Aplicar el mismo cuestionario en ambas ocasiones para comparar.
- Datos del respondiente: rol, años de uso de computadora o celular, fecha. No se registran nombres ni DNI.

## Cuestionario (10 ítems, escala 1 a 5)

Escala para cada ítem: **1 = Totalmente en desacuerdo, 2 = En desacuerdo, 3 = Neutral, 4 = De acuerdo, 5 = Totalmente de acuerdo.**

| N.º | Ítem | Tipo |
|---|---|---|
| 1 | Creo que me gustaría usar este sistema con frecuencia. | Positivo |
| 2 | Encontré el sistema innecesariamente complejo. | Negativo |
| 3 | Pensé que el sistema era fácil de usar. | Positivo |
| 4 | Creo que necesitaría el apoyo de una persona con conocimientos técnicos para poder usar este sistema. | Negativo |
| 5 | Encontré que las diversas funciones del sistema estaban bien integradas. | Positivo |
| 6 | Pensé que había demasiada inconsistencia en el sistema. | Negativo |
| 7 | Imagino que la mayoría de las personas aprendería a usar este sistema muy rápidamente. | Positivo |
| 8 | Encontré el sistema muy incómodo de usar. | Negativo |
| 9 | Me sentí muy seguro(a) usando el sistema. | Positivo |
| 10 | Necesité aprender muchas cosas antes de poder empezar a usar este sistema. | Negativo |

Preguntas abiertas opcionales (no puntúan): ¿Qué fue lo más útil? ¿Qué cambiaría primero? ¿Qué le faltó para reemplazar la tarjeta de control en papel?

## Fórmula

Sea `r_i` la respuesta (1 a 5) al ítem `i`.

- Ítems impares (1, 3, 5, 7, 9): contribución `c_i = r_i - 1`.
- Ítems pares (2, 4, 6, 8, 10): contribución `c_i = 5 - r_i`.
- **Puntaje SUS individual** = `(c_1 + c_2 + ... + c_10) x 2,5`, con rango de 0 a 100.
- **Puntaje SUS de la versión** = promedio de los puntajes individuales de todos los respondientes (reportar también n, mínimo, máximo y desviación estándar).

Ejemplo ilustrativo (no son datos reales): respuestas 4, 2, 4, 2, 4, 2, 4, 2, 4, 2 dan `c = 3,3,3,3,3,3,3,3,3,3`, suma 30 y SUS = 30 x 2,5 = 75.

## Interpretación sugerida

| Puntaje SUS | Lectura |
|---|---|
| menor de 51 | Usabilidad deficiente |
| 51 a 67 | Por debajo del promedio |
| 68 | Promedio de la literatura (referencia) |
| 69 a 80 | Buena |
| mayor de 80 | Excelente |

Meta propuesta para el piloto: SUS >= 68 en el Incremento 1 y >= 80 en el Incremento 2 (a confirmar con el Product Owner; la guía S9 no fija una meta numérica de satisfacción).

## Plantilla de captura

| Respondiente | Rol | Versión | r1 | r2 | r3 | r4 | r5 | r6 | r7 | r8 | r9 | r10 | SUS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | | | | | | | | | | | | | |
| R2 | | | | | | | | | | | | | |
| R3 | | | | | | | | | | | | | |

Una hoja de cálculo calcula la columna SUS con `=((r1-1)+(5-r2)+(r3-1)+(5-r4)+(r5-1)+(5-r6)+(r7-1)+(5-r8)+(r9-1)+(5-r10))*2.5`.

## Indicador proxy medible hoy

Mientras no se aplique el SUS, el equipo reporta como indicador proxy el porcentaje de criterios de aceptación Dado-Cuando-Entonces por requerimiento que están verificados por pruebas automatizadas en verde. Ese proxy mide cumplimiento funcional, **no** satisfacción: ver `Entregable_Semana9_Anemia_Junin.md`, §6.5.

## Limitaciones

- Con pocos respondientes el SUS es orientativo; no permite inferencia estadística.
- El instrumento no sustituye la observación de uso real en el establecimiento (cronometrar la tarea, anotar errores y ayudas pedidas).
