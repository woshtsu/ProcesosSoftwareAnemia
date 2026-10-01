# ADR-004 — Reglas clínicas parametrizadas en el dominio

**Contexto.** La clasificación de anemia depende de la edad y del ajuste de hemoglobina por altitud. Un error en esta regla tiene impacto clínico. El plan S3-S4 registra como dependencia la confirmación de umbrales con la microred.

**Decisión.** Puntos de corte y ecuación de ajuste por altitud (OMS 2024) centralizados en `app/domain/reglas_clinicas.py`. Menores de 6 meses se marcan `NO_APLICA` (evaluación clínica). El sistema calcula y muestra; **no diagnostica ni prescribe**: la decisión sigue siendo profesional.

**Consecuencias.** (+) Pruebas de valores límite para cada punto de corte. (+) Si la norma cambia, se modifica un solo módulo. (−) Los parámetros deben ser validados por la microred antes del uso clínico real (registrado como condición del H1).
