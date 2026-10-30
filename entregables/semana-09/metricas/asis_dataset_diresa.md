# Línea base AS-IS del seguimiento de anemia (dataset DIRESA Junín)

Generado por `herramientas/dataset/analisis_asis.py` a partir de `Dataset/Niños_menores_de_36_meses_con_dx_de_anemia_en_la_Región_ Junín.csv` (HIS, diagnósticos del 14/01/2022 al 21/06/2024). Fecha de corte usada: 30/06/2024. Datos completos y fórmulas en `datos/asis_dataset_diresa.json`. Los porcentajes llevan un decimal; entre paréntesis, numerador/denominador.

## 1. Perfil del dataset

- Filas: **12 486**. Nacimientos: 17/07/2021 a 09/05/2024.
- Cobertura: 9 provincias, 9 redes, 41 microredes, 121 distritos (nombres distintos; 124 pares provincia–distrito), 443 establecimientos (nombres distintos; 449 combinaciones red–microred–nombre).
- Edad al diagnóstico (meses cumplidos): mediana 12,0, cuartiles 6,0–14,0.
- Grupos de edad: <6 m 7,5 % (931); 6–11 m 38,6 % (4823); 12–23 m 48,3 % (6029); 24–35 m 5,6 % (703).
- Severidad HIS: LEV 64,1 % (8001); MOD 33,6 % (4199); SIN DATO 1,6 % (205); SEV 0,6 % (81).
- Seguro (código numérico sin tabla de códigos en el diccionario): `1,` 92,7 %; `2,` 4,0 %; `0,` 2,0 %; `1, 2,` 0,4 %; `3,` 0,3 %; con ≥2 códigos: 0,6 % (79/12 486).

| Provincia | Diagnosticados | % |
|---|---:|---:|
| HUANCAYO | 4 194 | 33,6 |
| SATIPO | 3 797 | 30,4 |
| CHANCHAMAYO | 1 829 | 14,6 |
| CHUPACA | 660 | 5,3 |
| CONCEPCION | 592 | 4,7 |
| JAUJA | 573 | 4,6 |
| TARMA | 459 | 3,7 |
| YAULI | 220 | 1,8 |
| JUNIN | 162 | 1,3 |

| Red | Diagnosticados | % |
|---|---:|---:|
| VALLE DEL MANTARO | 4 709 | 37,7 |
| SATIPO | 2 816 | 22,6 |
| PICHANAKI | 1 263 | 10,1 |
| SAN MARTIN DE PANGOA | 981 | 7,9 |
| JAUJA | 762 | 6,1 |
| RED DE SALUD CHUPACA | 737 | 5,9 |
| CHANCHAMAYO | 590 | 4,7 |
| TARMA | 455 | 3,6 |
| JUNIN | 173 | 1,4 |

## 2. Calidad del dato

- **num_doc no utilizable**: 8 754 valores distintos para 12 486 filas; en notación científica 100,0 % (12 486/12 486); filas con num_doc repetido 49,4 % (6 167/12 486); máximo 24 filas con el mismo valor.
- Posibles duplicados: 33 filas idénticas en todas las columnas (excedentes sobre la primera aparición); 549 filas comparten num_doc, fecha de nacimiento y fecha de diagnóstico con otra.
- Nulos por columna (%): seguro 0,0, fecha_nac 0,0, fecha_dx 0,0, valor_lab_dx 1,6, fecha_dosaje_dx 7,4, hb_dx 15,3, fecha_dosaje_mes 32,9, hb 39,3, fecha_dosaje_3_meses 45,3, hb_tresmeses 50,6, fecha_dosaje_6_meses 53,7, hb_seismeses 56,9, fecha_recup 53,1, recup 0,0, fecha_supT1 7,9, fecha_supT2 26,6, fecha_supT3 39,6, fecha_supT4 50,4, fecha_supT5 59,0, fecha_supT6 99,8, fecha_ta 25,3, Red 0,0, MicroRed 0,0, Nombre_Establecimiento 0,0, Provincia 0,0, Distrito 0,0.
- **Severidad vs hb_dx.** Criterio A (cribado simple, sin altitud): severidad LEV/MOD/SEV registrada con Hb observada ≥ 13,0 g/dL. Es una cota gruesa: en provincias de altura puede ser un falso positivo, porque la severidad se asigna con Hb ajustada. Resultado: 5,9 % (628/10 577) con severidad y Hb ≥ 13; en LEV 8,3 % (568/6 867) (máximo 17,2 g/dL); en provincias bajas (Satipo, Chanchamayo), donde el ajuste es casi nulo, LEV con Hb ≥ 13: 0,1 % (4/3 506); SEV con Hb ≥ 11: 10,5 % (6/57). La mediana de hb_dx de los casos LEV sube con la altitud (≈10,4 g/dL en Satipo/Chanchamayo frente a ≈13,6 en Junín): la severidad del HIS se asigna con Hb AJUSTADA por altitud y hb_dx es la Hb OBSERVADA. Por eso 'LEV con Hb ≥ 13' no es necesariamente un error, pero sí un valor que un usuario o un sistema sin el ajuste interpretaría como no anémico.
- Criterio B (exploratorio, con altitud): concordancia con la severidad esperada 78,2 % (8 212/10 503); Hb ajustada ≥ 11 pese a tener severidad: 8,0 % (840/10 503). Hb ajustada = hb_dx − ajuste OMS 2011 según altitud de la capital provincial (INEI 2014); umbrales: SIN ANEMIA ≥ 11,0; LEV 10,0–10,9; MOD 7,0–9,9; SEV < 7,0. Es aproximado (altitud de la capital, no del establecimiento; tabla de ajuste referencial a contrastar con la NTS vigente).
- Fechas incoherentes: dosaje del dx antes del dx 0; recuperación antes del dx 0; nacimiento después del dx 0; controles antes del dx 0; entregas antes del dx 0; fin de tratamiento antes del dx 0; fechas posteriores al corte 0; edad fuera de 0–35 m 0; entregas no monótonas 0; recup/fecha_recup contradictorios 0. Es decir, el orden temporal básico es consistente.
- Rasgos de registro: fecha_supT1 = fecha_dx en 100,0 % (11 505/11 505); fecha_ta = fecha_dx en 33,1 % (3 084/9 330); fecha_dosaje_dx = fecha_dx en 100,0 % (11 567/11 567).
- Hb fuera de 3–20 g/dL: 2 valores (hb_dx: <3 = 0, >20 = 0, hb: <3 = 1, >20 = 0, hb_tresmeses: <3 = 0, >20 = 0, hb_seismeses: <3 = 1, >20 = 0).
- Fecha de dosaje sin valor de Hb: dx 8,6 % (990/11 567); mes 9,5 % (794/8 379); 3 m 9,7 % (662/6 836); 6 m 7,0 % (405/5 783).
- Recuperación documentada con Hb a 6 m < 11 g/dL observada: 4,8 % (212/4 413) (la Hb observada ya sería anemia aun sin ajustar).

## 3. Indicadores de proceso AS-IS (global)

«Seg. posible» = solo diagnosticados con `fecha_dx + plazo + 30 d ≤ 30/06/2024` (plazos: 30, 90 y 180 días).

| Indicador | Valor (n/N) | Fórmula |
|---|---|---|
| Control de Hb al mes | 67,1 % (8 379/12 486) | fecha_dosaje al mes registrada ÷ diagnosticados |
| Control al mes, seg. posible | 70,2 % (8 213/11 702) | control al mes ÷ diagnosticados con fecha_dx ≤ 01/05/2024 (plazo 30 d + holgura 30 d antes del corte) |
| Control de Hb a los 3 meses | 54,7 % (6 836/12 486) | fecha_dosaje a los 3 meses registrada ÷ diagnosticados |
| Control a los 3 meses, seg. posible | 63,8 % (6 652/10 419) | control a los 3 meses ÷ diagnosticados con fecha_dx ≤ 02/03/2024 (plazo 90 d + holgura 30 d antes del corte) |
| Control de Hb a los 6 meses | 46,3 % (5 783/12 486) | fecha_dosaje a los 6 meses registrada ÷ diagnosticados |
| Control a los 6 meses, seg. posible | 66,1 % (5 646/8 540) | control a los 6 meses ÷ diagnosticados con fecha_dx ≤ 03/12/2023 (plazo 180 d + holgura 30 d antes del corte) |
| Control a los 6 meses, sin holgura (sensibilidad) | 63,6 % (5 783/9 090) | idem con fecha_dx ≤ 02/01/2024 (sin holgura; sensibilidad) |
| Control al mes con Hb | 60,7 % (7 585/12 486) | control al mes con fecha y Hb ÷ diagnosticados |
| Control a los 3 meses con Hb | 49,4 % (6 174/12 486) | control a los 3 meses con fecha y Hb ÷ diagnosticados |
| Control a los 6 meses con Hb | 43,1 % (5 378/12 486) | control a los 6 meses con fecha y Hb ÷ diagnosticados |
| Los tres controles | 29,5 % (3 682/12 486) | con los 3 dosajes (mes, 3 m, 6 m) ÷ diagnosticados |
| Los tres controles, seg. posible | 41,9 % (3 577/8 540) | los 3 dosajes ÷ dx con seguimiento de 6 m posible |
| Ningún control | 17,9 % (2 237/12 486) | sin dosaje a 1, 3 ni 6 meses ÷ diagnosticados |
| Ningún control, seg. posible | 12,3 % (1 050/8 540) | sin ningún dosaje ÷ dx con seguimiento de 6 m posible |
| Pérdida de seguimiento a 6 meses | 53,7 % (6 703/12 486) | sin dosaje a los 6 meses ÷ diagnosticados (= 100 − control 6 m) |
| Pérdida de seguimiento a 6 meses, seg. posible | 33,9 % (2 894/8 540) | sin dosaje a 6 m ÷ dx con seguimiento de 6 m posible |
| Recuperación documentada | 46,9 % (5 859/12 486) | recup=1 (con fecha_recup) ÷ diagnosticados |
| Recuperación, seg. 6 m posible | 66,5 % (5 682/8 540) | recup=1 ÷ dx con fecha_dx ≤ 03/12/2023 |
| Recuperación, ≥ 1 año de seguimiento | 69,2 % (3 724/5 383) | recup=1 ÷ dx con fecha_dx ≤ 01/07/2023 (≥ 1 año de seguimiento) |
| Recuperados sobre control de cierre (6 m) | 81,8 % (4 731/5 783) | recup=1 con dosaje a 6 m ÷ con dosaje a 6 m (control de cierre; Tabla 8 de S1) |
| Suplementación ≥ 5 entregas | 41,0 % (5 115/12 486) | ≥5 fechas fecha_supT1..T6 registradas ÷ diagnosticados |
| ≥ 5 entregas, seg. posible | 51,0 % (4 957/9 726) | ≥5 entregas ÷ dx con fecha_dx ≤ 01/02/2024 (5.ª entrega esperada a ~120 d + holgura) |
| Sin ninguna entrega | 7,9 % (981/12 486) | 0 entregas registradas ÷ diagnosticados |
| Fin de tratamiento (fecha_ta) registrado | 74,7 % (9 330/12 486) | fecha_ta registrada ÷ diagnosticados |
| Fin de tratamiento registrado, seg. 6 m posible | 81,7 % (6 974/8 540) | fecha_ta registrada ÷ dx con seguimiento de 6 m posible |
| Sin Hb al diagnóstico | 15,3 % (1 909/12 486) | sin hb_dx ÷ diagnosticados |

**Demora respecto de la fecha esperada (solo controles realizados; días, positivo = tarde):**

| Control | N | Mediana | P90 | Mín–máx | % con retraso > 0 |
|---|---:|---:|---:|---|---:|
| Al mes (esperado dx + 30 d) | 8 379 | 1,0 | 6,0 | -1,0 a 28,0 | 59,4 |
| A los 3 meses (esperado dx + 90 d) | 6 836 | 2,0 | 11,5 | -3,0 a 29,0 | 85,1 |
| A los 6 meses (esperado dx + 180 d) | 5 783 | 4,0 | 16,0 | -2,0 a 29,0 | 95,7 |

Como el dataset solo contiene dosajes dentro de ventana, la demora de los controles realizados es pequeña por construcción; la brecha real está en los controles que no constan, no en el retraso de los que sí constan.

Recuperación: mediana 184,0 días desde el diagnóstico (p90 305,0, n = 5 859).
Tiempo dx → primera suplementación: mediana 0,0 d, p90 0,0 d; el 100,0 % de las primeras entregas consta el mismo día del dx; sin primera entrega: 7,9 % (981/12 486).

**Distribución del n.º de entregas (fecha_supT1..T6):**

| Entregas | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| % | 7,9 | 18,7 | 13,0 | 10,9 | 8,6 | 40,7 | 0,2 |

Media: 3,2 entregas por niño.

## 4. Desagregación

Valores en %. «seg. posible» y «seg. 6 m» usan la regla de seguimiento posible (columnas completas, con n/N, en el JSON).

### Por provincia

| Provincia | N | Control 1 m | Control 3 m | Control 6 m | Control 6 m (seg. posible) | Recup. | Recup. (seg. 6 m) | ≥5 entregas | 0 entregas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HUANCAYO | 4 194 | 66,5 | 51,5 | 40,2 | 57,3 | 42,3 | 59,8 | 34,6 | 9,9 |
| SATIPO | 3 797 | 68,6 | 57,9 | 50,1 | 71,6 | 47,5 | 67,5 | 48,2 | 5,8 |
| CHANCHAMAYO | 1 829 | 64,3 | 52,8 | 51,4 | 74,6 | 51,0 | 74,0 | 36,9 | 6,3 |
| CHUPACA | 660 | 69,4 | 58,2 | 43,9 | 60,4 | 49,7 | 67,7 | 44,5 | 7,1 |
| CONCEPCION | 592 | 63,5 | 49,5 | 40,4 | 57,7 | 41,0 | 57,7 | 34,3 | 10,0 |
| JAUJA | 573 | 72,1 | 64,4 | 51,8 | 73,6 | 54,1 | 76,2 | 47,5 | 8,7 |
| TARMA | 459 | 73,6 | 63,0 | 53,6 | 79,2 | 57,7 | 86,2 | 53,6 | 3,3 |
| YAULI | 220 | 58,2 | 46,4 | 41,8 | 57,9 | 42,7 | 57,2 | 30,0 | 17,3 |
| JUNIN | 162 | 59,9 | 45,7 | 54,9 | 72,1 | 66,0 | 85,2 | 48,1 | 14,2 |

### Por severidad (HIS)

| Severidad | N | Control 1 m | Control 3 m | Control 6 m | Control 6 m (seg. posible) | Recup. | Recup. (seg. 6 m) | ≥5 entregas | 0 entregas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LEV | 8 001 | 67,9 | 55,7 | 47,9 | 67,5 | 48,8 | 68,5 | 42,4 | 6,5 |
| MOD | 4 199 | 67,8 | 54,8 | 44,9 | 65,1 | 44,9 | 64,4 | 39,9 | 7,0 |
| SEV | 81 | 59,3 | 46,9 | 30,9 | 58,1 | 33,3 | 51,2 | 29,6 | 21,0 |
| SIN DATO | 205 | 25,4 | 22,0 | 18,0 | 30,3 | 20,0 | 32,0 | 10,2 | 71,7 |

### Por trimestre de diagnóstico (efecto de la censura)

| Trimestre | N | Control 1 m | Control 3 m | Control 6 m | Recup. |
|---|---:|---:|---:|---:|---:|
| 2022Q1 | 282 | 33,7 | 67,4 | 69,5 | 71,6 |
| 2022Q2 | 375 | 80,0 | 70,9 | 51,7 | 58,7 |
| 2022Q3 | 1 070 | 42,1 | 48,5 | 67,5 | 69,4 |
| 2022Q4 | 713 | 70,4 | 61,7 | 62,4 | 68,6 |
| 2023Q1 | 1 374 | 65,7 | 59,2 | 66,0 | 69,9 |
| 2023Q2 | 1 539 | 71,0 | 63,2 | 66,6 | 70,9 |
| 2023Q3 | 1 807 | 77,3 | 67,8 | 69,2 | 67,0 |
| 2023Q4 | 1 891 | 75,9 | 66,2 | 55,2 | 46,6 |
| 2024Q1 | 2 015 | 77,4 | 57,5 | 0,0 | 2,4 |
| 2024Q2 | 1 420 | 45,3 | 0,0 | 0,0 | 0,9 |

Los dos o tres últimos trimestres tienen valores bajos en control a 6 meses y recuperación porque aún no habían cumplido el plazo: por eso la cifra bruta subestima el desempeño real y se reporta además la variante con seguimiento posible.

## 5. Brecha que ataca el Incremento 2

| Indicador de la Tabla 8 de S1 | Indicador AS-IS de este análisis | Relación con el Inc. 2 |
|---|---|---|
| Cobertura oportuna de medición/control (proceso) | control_mes / control_3m / control_6m (global y con seguimiento posible) | Línea base del indicador de valor V2/V3 «controles programados y vencidos visibles»: hoy no existe agenda normativa; el control depende de que el niño vuelva y alguien lo registre. |
| Demora de controles vencidos (proceso) | demora_mes / demora_3m / demora_6m (mediana y p90 de días respecto de la fecha esperada) | Solo mide los controles que SÍ se hicieron; los vencidos nunca atendidos no tienen demora observable (sesgo de supervivencia). El Inc. 2 muestra los vencidos con su demora actual. |
| Pérdida de seguimiento (valor) | perdida_seguimiento_6m y sin_ningun_control (global y con seguimiento posible) | Línea base del indicador de pérdida de seguimiento de S1 (y S3-4): niños sin cierre a 6 meses; el Inc. 2 la ataca con alertas y agenda del personal. |
| Recuperación documentada al año (resultado) | recuperacion_documentada, recuperacion_con_seguimiento_6m/12m, recuperados_sobre_control_cierre | Resultado clínico de referencia; no es atribuible solo al sistema, se usa como contexto. |

Lectura: sobre los diagnosticados con seguimiento posible, el control a los 6 meses consta en 66,1 % (5 646/8 540) y 12,3 % (1 050/8 540) no tiene ningún control; esa es la población de niños «vencidos» que el Inc. 2 busca hacer visible (agenda normativa, controles vencidos y alertas).

## 6. Advertencias metodológicas

- El dataset solo contiene niños CON diagnóstico de anemia: no hay población total ni sanos, por lo que no se puede calcular prevalencia ni cobertura de tamizaje.
- Solo constan dosajes dentro de la ventana de cada control (1.º: 29–58 d; 3.º: 87–119 d; 6.º: 178–209 d desde el dx). Un control fuera de ventana, o no registrado en el HIS, aparece como «no realizado»: el indicador mide control registrado en ventana, no asistencia real.
- Censura por corte: los diagnósticos recientes (hasta 21/06/2024) no han tenido tiempo de cumplir los controles. Por eso se reportan dos lecturas: sobre todos los diagnosticados (cifra bruta, penalizada) y sobre quienes tenían seguimiento posible (cifra más justa).
- La fecha esperada de cada control (dx + 30/90/180 d) y la holgura de 30 d son supuestos operativos de este análisis, coherentes con el rango observado de las fechas; deben contrastarse con la norma técnica vigente.
- num_doc no es confiable (notación científica, no único): no hay identificación del niño; puede haber repeticiones del mismo niño en filas distintas (varios diagnósticos o duplicados). No se intentó reidentificar a nadie.
- La severidad del HIS parece asignarse con Hb ajustada por altitud, mientras hb_dx es la observada; la concordancia calculada con la altitud de la capital provincial es una aproximación.
- fecha_supT1 coincide con fecha_dx en el 100 % de los casos y fecha_ta coincide con fecha_dx en una parte de los registros: el tiempo dx→primera suplementación no mide demora real y fecha_ta debe usarse con cautela.
- Una entrega no registrada puede ser entrega no hecha o registro faltante; el dataset no distingue ambas cosas.
- El dataset no incluye adherencia real (consumo), visitas domiciliarias, referencias ni motivos de abandono.

_Fuente: DIRESA Junín, HIS, dataset “Niños menores de 36 meses con dx de anemia en la Región Junín” (2022–2024); elaboración propia._
