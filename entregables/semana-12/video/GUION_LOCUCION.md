# Guion de locución — video demo Anemia Junín v4.0-Inc4

Video: [`demo_anemia_junin_v4.mp4`](demo_anemia_junin_v4.mp4) (5:59, 1920x1080, sin audio). Grabado el 09/11/2026 sobre producción (<https://softwareanemia-virginia.onrender.com>) con datos sintéticos «DEMO», que se eliminan de la base después de la grabación.

## Indicaciones para la locución y edición

- **Rótulo azul bajo las pestañas:** indica la parte (PMV · Incremento 1, Incremento 2, 3, 4). La leyenda inferior resume el paso; puedes leerla o parafrasearla.
- **Tiempos:** son aproximados (±3 s). El objetivo final es de 4:50 a 5:10: recorta los tiempos muertos marcados «recortar» (esperas del servidor en Render) y la escena final.
- **Aviso de Edge «¿Quieres traducir la página?»** en GitHub (desde ~5:03): recórtalo o tápalo con un recuadro.
- **No decir** que se envían mensajes reales: los recordatorios son SIMULADOS. Los niños con código DJ-xxxxx son del dataset abierto de DIRESA Junín, seudonimizados; los «DEMO» son sintéticos.
- **Fecha de referencia 30/06/2024:** producción trabaja con la fecha de corte del dataset; por eso las fechas del video son de 2024. Puede mencionarse una vez.
- La barra de tareas y el reloj quedan visibles a propósito (evidencia de grabación real). Exporta en MP4 H.264, 1080p o 720p.

## Guion por tramos

| Tiempo | Parte · paso | Locución sugerida |
| --- | --- | --- |
| 0:00–0:16 | Portada | Presentación: «Anemia Junín, versión 4.0. Sistema web progresivo para el seguimiento de la anemia infantil en postas rurales de Junín. Mostraremos el PMV y los incrementos 2, 3 y 4 en el servidor de producción, con datos sintéticos marcados DEMO.» |
| 0:16–0:30 | PMV · RF-03 Validación | «El sistema valida antes de guardar: un DNI de 3 dígitos o una hemoglobina de 25 g/dL se rechazan con un mensaje por campo; no se guarda nada.» |
| 0:30–0:43 | PMV · RF-01 Registro | «Corregimos los datos y registramos a la niña. El sistema ajusta la hemoglobina por la altitud de 3 720 m y clasifica automáticamente: anemia moderada. Clasifica, no diagnostica ni prescribe.» |
| 0:43–0:58 | PMV · RF-02 Expediente | «Se crea un expediente digital único. Registramos un nuevo control y la evolución de la hemoglobina ajustada queda visible.» |
| 0:58–1:34 | PMV · RF-04 Seguimiento | «Seguimiento: niños priorizados por gravedad y días sin control; filtramos los registros DEMO.» (Tramo con espera del servidor: recortar.) |
| 1:34–1:47 | PMV · RF-05 Reporte | «Reporte del periodo por clasificación y comunidad, exportable a CSV.» |
| 1:47–1:58 | Inc. 2 · RF-06 Agenda del niño | «Incremento 2: cada niño tiene su agenda de controles según su edad y tratamiento; aquí un control de tratamiento vencido.» |
| 1:58–2:11 | Inc. 2 · RF-09 Inasistencia | «Registramos que no asistió y el motivo: enfermedad del niño. La alerta conserva la marca de inasistencia.» |
| 2:11–2:45 | Inc. 2 · RF-08 Agenda del personal | «Agenda del personal: controles por día en un rango de hasta 31 días; si se pide más, el sistema lo indica.» (Tiene espera: recortar.) |
| 2:45–3:02 | Inc. 3 · HIST-3.1 Sin conexión | «Incremento 3: sin conexión, el registro se guarda en una cola local del dispositivo y el indicador muestra los pendientes.» |
| 3:02–3:23 | Inc. 3 · HIST-3.4 / 3.2 Sincronización | «Vemos los pendientes y su antigüedad. Al reconectar se sincronizan; el identificador de operación evita duplicados.» |
| 3:23–3:57 | Inc. 3 · VIS-3.5 Visitas | «Visitas domiciliarias priorizadas por un puntaje explicable, con su desglose. Los pesos son una propuesta aún no validada con la microred.» (Tiene espera: recortar.) |
| 3:57–4:11 | Inc. 4 · HIST-4.1 Recordatorios | «Incremento 4: recordatorios al tutor. En esta versión el envío es SIMULADO: no sale ningún mensaje real por WhatsApp ni SMS.» |
| 4:11–4:25 | Inc. 4 · HIST-4.2 Respuesta del tutor | «Registramos la respuesta del tutor: no puede asistir, por rechazo al tratamiento.» |
| 4:25–4:43 | Inc. 4 · HIST-4.3 Barrera | «Registramos una barrera de acceso del niño; también funciona sin conexión.» |
| 4:43–5:03 | Inc. 4 · HIST-4.4 Barreras críticas | «Las barreras críticas generan una alerta priorizada para el personal de salud.» |
| 5:03–5:55 | Calidad y arquitectura | «El código sigue una arquitectura hexagonal: dominio, puertos, adaptadores y aplicación; integración continua en GitHub Actions y versiones etiquetadas de v1.0 a v4.0. Limitaciones: envío real no probado, proveedor de identidad simulado y validación en una posta pendiente.» (Recortar a ~25 s; tapar el aviso «¿Traducir?» de la esquina superior derecha.) |
