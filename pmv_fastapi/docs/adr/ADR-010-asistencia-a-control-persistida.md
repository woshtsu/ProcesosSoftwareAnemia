# ADR-010 — Asistencia a un control: evento persistido que complementa la agenda calculada

**Contexto.** ADR-007 decidió calcular la agenda en línea y no persistirla, y dejó pendiente qué hacer con la asistencia (HIST-2.4, RF-09): sin ella, una familia que acudió sin que se evaluara al niño, o que avisó que no vendría, seguía apareciendo como alerta vencida y la única salida era el alta. Una asistencia o inasistencia es un **hecho que ocurrió y no se puede deducir** de las evaluaciones; por tanto sí debe guardarse.

**Decisión.** Se agrega la tabla `asistencia_control` y se mantiene calculada la agenda: la agenda sigue derivándose del expediente y **además** consulta las asistencias registradas.

Tabla (`db/01_esquema_postgresql.sql`; migración en `db/02_migracion_v2_0.sql`): `id`, `nino_id` (FK con `ON DELETE CASCADE`), `codigo_control`, `fecha_programada`, `estado` (`ASISTIO` | `NO_ASISTIO`), `motivo`, `evaluacion_id` (nulo; FK a la evaluación que cumplió el control, `ON DELETE SET NULL`), `registrado_por`, `creado_en`, con `UNIQUE (nino_id, codigo_control, fecha_programada)` y `CHECK` (`ck_asistencia_motivo`) que exige motivo cuando `estado = 'NO_ASISTIO'`. Un control se identifica por su código y su fecha programada.

Endpoints:

- `POST /api/ninos/{id}/controles/{codigo}/asistencia` con `{fecha_programada, estado, motivo?, evaluacion_id?}` y el encabezado `X-Usuario` (queda en `registrado_por`): 201 con la asistencia. 404 si el niño o el control no existen; 409 si el control ya tiene asistencia, ya está cumplido o fue cerrado por recuperación; 422 si la fecha programada es futura, el estado es inválido, la inasistencia no trae motivo (3 a 200 caracteres), se envía `evaluacion_id` con `NO_ASISTIO`, o la evaluación no es del niño o ya cumple otro control.
- `GET /api/ninos/{id}/asistencias`: asistencias del niño, por fecha programada.

Efecto en la agenda y las alertas (`app/domain/service/agenda.py`, regla 8 de ADR-007):

- **Asistió** → el control queda `CUMPLIDO` aunque no haya evaluación (`cumplido_por_asistencia = true`); si se vinculó una evaluación, esta cumple el control y deja de estar disponible para otros. Un control cumplido por asistencia deja de generar alerta.
- **No asistió** → el control **sigue** `PENDIENTE` o `VENCIDO` (no se cumplió) y se marca `inasistencia_registrada = true` con su `motivo_inasistencia`. En las alertas, la prioridad **sube un nivel** (BAJA a MEDIA, MEDIA a ALTA; ALTA se mantiene) porque la familia ya fue citada y no acudió. No se vuelve a registrar sobre el mismo control (409).
- Solo se registran controles con fecha programada menor o igual que hoy; los futuros se rechazan.

Interfaz: botones «Asistió» y «No asistió» en cada control pendiente o vencido, en la agenda del expediente y en la pestaña «Agenda», con una ventana (`modal-asistencia`) que pide el motivo de la inasistencia o permite vincular una evaluación; las inasistencias se muestran con la marca «Inasistencia registrada».

**Alternativas descartadas.** (a) Marcar la inasistencia como un campo del control: el control no existe en la base (se calcula). (b) Cerrar el control al registrar la inasistencia: la alerta desaparecería y se perdería la vigilancia, que es lo contrario de lo buscado. (c) Registrar la asistencia como una evaluación sin hemoglobina: contamina los datos clínicos y los reportes. (d) Permitir registrar controles futuros por adelantado: se confundiría con una cita; la agenda del personal ya muestra lo que viene.

**Consecuencias.** (+) La agenda sigue sin tabla de controles (ADR-007 se mantiene): solo se persiste el hecho. (+) La alerta distingue «vencido sin noticias» de «vencido con inasistencia registrada» y lo prioriza. (+) La `UNIQUE` evita duplicados aun con solicitudes simultáneas: de seis registros simultáneos del mismo control resulta un 201 y cinco 409 (CP-169). (−) Una asistencia queda vinculada al par (código, fecha programada): hoy las evaluaciones no se editan, de modo que la fecha de un control no cambia; si en el futuro se permitiera corregir evaluaciones, habría que decidir qué pasa con las asistencias de los controles que se muevan. (−) No hay anulación ni corrección de una asistencia registrada por error; se deja como backlog para el Incremento 3, junto con la autenticación por roles que dirá quién puede hacerlo.
