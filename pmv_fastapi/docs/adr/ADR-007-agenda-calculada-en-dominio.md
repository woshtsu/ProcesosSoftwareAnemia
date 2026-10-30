# ADR-007 — Agenda de controles calculada en el dominio, sin tabla propia

> **Actualización (v2.0.0-inc2).** La agenda sigue calculándose en línea y sin tabla de controles; lo único que se persiste es el hecho de la asistencia (ADR-010, tabla `asistencia_control`), que la agenda consulta (regla 8). Por eso la afirmación «sin cambios de base de datos» de este ADR rige solo para la agenda de la versión 1.5; la migración a la 2.0 está en `db/02_migracion_v2_0.sql`.

**Contexto.** La brecha B2 del proceso es que la agenda de controles se calcula a mano: hay controles fuera de la ventana normativa y citas olvidadas. El Incremento 2 (HIST-2.1 y HIST-2.2) necesita saber, para cada niño activo, qué controles le tocan, cuáles cumplió, cuáles vencen pronto y cuáles ya vencieron. Los parámetros (meses de los dosajes, tolerancias de la ventana) los confirma la microred y pueden cambiar, igual que las reglas clínicas (ADR-004). El sistema **solo programa y vigila fechas; no diagnostica ni prescribe**.

**Decisión.** La agenda se **calcula en línea** a partir del expediente (fecha de nacimiento, estado y evaluaciones) y de la fecha de hoy, con una función pura del dominio, `app/domain/service/agenda.py::generar_agenda`. No se crea ninguna tabla (`db/01_esquema_postgresql.sql` no cambia): el estado de cada control se deriva siempre de los datos clínicos y nunca queda desactualizado. Los parámetros están agrupados y versionados en `ESQUEMA_AGENDA_V1` (versión `AGENDA-V1`, fuente en el docstring del módulo: esquema operativo del establecimiento, S1 Anexo A, Tablas A.3 y A.4, compatible con la NTS N.° 213-MINSA/DGIESP-2024).

Parámetros exactos de `ESQUEMA_AGENDA_V1`:

| Parámetro | Valor |
|---|---|
| Dosajes por edad (tipo `TAMIZAJE_EDAD`) | 6 DHx, 9 DHc1, 12 DHc2, 15 DHx, 18 DHc1, 21 DHc2, 24 DHx, 30 DHc1, 36 DHx, 39 DHc1, 48 DHx y 51 DHc1 (meses de edad) |
| Fecha programada | nacimiento + N meses calendario; si el día no existe se usa el último día del mes (31-ene + 1 mes = 28 o 29-feb) |
| Seguimiento del tratamiento (tipo `CONTROL_TRATAMIENTO`) | evaluación LEVE, MODERADA o SEVERA: C1M, C3M y C6M a +1, +3 y +6 meses de esa evaluación |
| Ventana de cumplimiento | de programada − 15 días a programada + 30 días (ambos extremos incluidos) |
| Próximo a vencer | `PENDIENTE` con fecha límite dentro de los 7 días siguientes (incluido el propio día límite) |
| Población | solo niños `ACTIVO` y solo controles con el niño de menos de 60 meses en la fecha programada |

Reglas de estado:

1. **CUMPLIDO**: hay una evaluación dentro de la ventana. Cada evaluación cumple como máximo un control y cada control usa una sola evaluación: se asignan primero los pares más cercanos; en empate gana el control más antiguo y, a igual fecha, el de tratamiento.
2. **PENDIENTE**: aún no se cumple y hoy ≤ fecha límite (programada + 30 d). Con `proximo = true` si la fecha límite está a 7 días o menos.
3. **VENCIDO**: hoy > programada + 30 d y no cumplido; `dias_vencido` cuenta los días desde la fecha límite (1 el primer día vencido).
4. **La agenda empieza cuando el niño entra al sistema**: solo se programan dosajes por edad con fecha ≥ fecha de la primera evaluación − 15 días. Así un niño registrado a los 14 meses no nace con controles «vencidos» de los 6, 9 y 12 meses.
5. **Episodios de anemia**: un episodio empieza con la primera evaluación con anemia; las evaluaciones posteriores con anemia dentro del episodio **no reinician** el calendario C1M/C3M/C6M. Se abre un episodio nuevo con una anemia posterior a una evaluación `SIN_ANEMIA` o posterior al fin de la ventana del C6M.
6. **Regla elegida para la recuperación**: si una evaluación posterior al diagnóstico es `SIN_ANEMIA`, los controles de tratamiento de ese episodio que **aún no habían vencido** y no se cumplieron pasan al estado `CERRADO_RECUPERADO` (no se exigen más y no cuentan como pendientes ni vencidos). Los controles que ya estaban vencidos antes de la recuperación siguen figurando como `VENCIDO` para conservar el historial fiel; el parámetro `cerrar_vencidos_al_recuperar` permite cerrarlos también si la microred lo decide.
7. Los niños con alta no tienen agenda (`aplica = false`).
8. **Asistencia registrada (HIST-2.4, ADR-010)**: si el personal registró que el niño asistió a un control con fecha programada ya llegada, ese control queda `CUMPLIDO` aunque no haya evaluación (`cumplido_por_asistencia`); si registró que no asistió, el control sigue `PENDIENTE` o `VENCIDO` con la marca `inasistencia_registrada` y, en las alertas, la prioridad sube un nivel.

Prioridad de las alertas (HIST-2.2, `app/domain/service/alertas.py`): `ALTA` si el control es de tratamiento, o la última clasificación es MODERADA o SEVERA, o el atraso supera 30 días; `MEDIA` de 8 a 30 días; `BAJA` hasta 7 días. El atraso se mide desde la fecha límite del control. Si hay inasistencia registrada, la prioridad sube un nivel (BAJA a MEDIA, MEDIA a ALTA).

**Alternativas descartadas.** (a) Tabla `control_programado` con un proceso periódico que la rellene y actualice estados: obliga a mantener la coherencia ante correcciones de evaluaciones, a agregar migraciones y a programar un job; se descartó para el piloto. (b) Calcular la agenda en SQL: duplicaría reglas clínicas fuera del dominio y las pruebas por valores frontera exigirían una base de datos.

**Consecuencias.** (+) Una sola fuente de verdad: la agenda nunca contradice los datos clínicos y una evaluación nueva cambia la agenda al instante. (+) Reglas probadas como funciones puras con valores frontera (−15/+30 días exactos, fin de mes, 59→60 meses, recuperación, una evaluación para un solo control). (+) Cambiar el esquema normativo es agregar un `ESQUEMA_AGENDA_V2`. (+) Sin cambios de base de datos ni migración. (−) El costo es lineal en el número de niños activos en cada consulta de alertas: con 1 000 niños activos en SQLite (una sola consulta por lotes, sin N+1; ADR-006) se midieron 185 ms para listar las alertas y 245 ms para el resumen. Criterio de revisión: si hay más de 2 000 niños activos o el p95 de las alertas supera 300 ms se materializará la agenda en una tabla. (−) El historial de «cuándo se generó una alerta» no se conserva; HIST-2.4 (asistencia) decidió persistir solo el hecho de la asistencia, no las citas (ADR-010). (−) Un control vencido sigue vencido aunque el niño regrese después de su ventana (una evaluación fuera de la ventana no «rescata» el control; sí cumple el control vigente de su momento); con HIST-2.4 el personal puede registrar la asistencia (el control queda cumplido) o la inasistencia (el control sigue vencido, más prioritario); la alerta desaparece si el niño asiste, se evalúa o pasa a alta.
