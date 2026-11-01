# Capturas y evidencias pendientes — Informe integrador S12

Evidencias que el informe [`Informe_Integrador_S12_Anemia_Junin.md`](Informe_Integrador_S12_Anemia_Junin.md) necesita o menciona y que no existen en el repositorio. Ninguna se simuló ni se reemplazó por una imagen inventada.

## A. Capturas en producción (marcadores del informe)

Se toman sobre <https://softwareanemia.onrender.com> y se guardan en `evidencias/produccion/` con el nombre indicado. Verificado el 31/10/2026: `GET /api/salud` responde `{"estado":"ok","fecha_hoy":"2024-06-30","fecha_referencia":"2024-06-30"}` (reloj fijo del dataset: las agendas y los vencimientos se calculan al 30/06/2024) y `GET /openapi.json` declara la versión `4.0.0-inc4` con 29 rutas. En todas las capturas: no guardar registros nuevos, ocultar correos, tokens y cualquier dato personal, y usar solo datos sintéticos.

| N.º | Archivo destino | Captura (marcador del informe) | Dónde se usa |
| --- | --- | --- | --- |
| 1 | `evidencias/produccion/PROD_01_inc1_registro_clasificacion.png` | Pestaña «Registrar niño» con la vista previa de la clasificación (Hb 11,6 g/dL a 3 720 m: Hb ajustada 9,1 g/dL, «Anemia moderada») sin guardar, y pestaña «Reporte» del periodo | 3.6.4, cierre de las fichas del PMV (Incremento 1) |
| 2 | `evidencias/produccion/PROD_02_inc2_agenda_alertas.png` | Pestañas «Agenda» y «Alertas» (controles vencidos priorizados) con el aviso de fecha de referencia 30/06/2024 | 3.6.4, cierre de las fichas del Incremento 2 |
| 3 | `evidencias/produccion/PROD_03_inc3_sincronizacion_visitas.png` | Pestaña «Sincronización» («Al día», sin pendientes ni conflictos) y pestaña «Visitas» con puntaje y desglose | 3.6.4, cierre de las fichas del Incremento 3 |
| 4 | `evidencias/produccion/PROD_04_inc4_recordatorios_barreras.png` | Pestaña «Recordatorios» (mensajes SIMULADO o estado real del canal) y pestaña «Alertas» con barreras críticas | 3.6.4, cierre de las fichas del Incremento 4 |
| 5 | `evidencias/produccion/PROD_05_auth_inicio_sesion.png` | Pantalla de inicio de sesión y aplicación abierta con una cuenta de Supabase autorizada | 3.6.4, ficha AUTH |
| 6 | `evidencias/produccion/PROD_06_salud_openapi.png` | `/api/salud` con estado «ok» y fecha de referencia 30/06/2024, y `/openapi.json` con la versión `4.0.0-inc4` y 29 rutas | Anexo B y 3.6.3 (despliegue) |
| 7 | `evidencias/produccion/PROD_07_render_panel_live.png` | Panel de Render con el servicio en estado «Live» y el despliegue de `v4.0-Inc4` (requiere acceso al panel; ocultar variables de entorno) | Anexo B y 3.6.3 (despliegue) |

## B. Otras evidencias pendientes

| N.º | Captura o evidencia pendiente | Dónde se usa en el informe | Cómo obtenerla | Responsable sugerido |
| --- | --- | --- | --- | --- |
| 8 | PR #9 (documentación) abierto, con su estado y comprobaciones | Anexo B y eje 3.8 (CM) | Captura de la página del PR en GitHub | Cualquier integrante |
| 9 | Revisión formal «Approved» de un PR | Eje 3.8 (CM, VER) | Solicitar una revisión aprobada de otro integrante y capturar | Revisor distinto del autor |
| 10 | Ejecución en un teléfono real con red intermitente: cola de pendientes y sincronización | Ficha HIST-3.1b (3.6.4), marcador en el informe | Instalar la PWA en un teléfono, desconectar la red, registrar, reconectar; capturar pantalla del dispositivo | Integrante con teléfono Android |
| 11 | Recordatorio recibido por WhatsApp o SMS en el teléfono del tutor | Ficha HIST-4.1 (3.6.4), marcador en el informe | Requiere credenciales del proveedor; el envío real nunca se probó. Hasta entonces el informe lo declara como limitación | Líder, con cuenta del proveedor |
| 12 | Ejecución de SonarCloud o SonarQube con el informe de calidad | Eje 3.3 (DoD ítems 6 a 8) y eje 3.7 | Ejecutar el análisis con `sonar-project.properties` y capturar el panel | Analista de procesos y QA |
| 13 | Panel de Supabase Auth con política de contraseñas y MFA | Hallazgo H-12 (OWASP) | Capturar la configuración de Authentication en el proyecto | Integrante con acceso a Supabase |
| 14 | Prueba con lector de pantalla (NVDA o TalkBack) y cuestionario SUS | Eje 3.7.2 (WCAG, factor U) | Sesión con lector de pantalla sobre los flujos principales; aplicar SUS a usuarios de salud | Analista de procesos y QA |
| 15 | Evidencia de aceptación por usuarios del establecimiento de salud (acta o conformidad) | Eje 3.8 (VAL) y 4.2 | Acta firmada o correo de conformidad; sin datos personales | Líder |
| 16 | Actas de Scrum (planificación, revisión, retrospectiva) y horas reales por tarea | Eje 3.4 y eje 3.8 (ESTIM, PQA) | Recuperar de los registros del equipo o registrarlas desde ahora | Analista de procesos y QA |
| 17 | Enlace del video en Drive y grabación `video/demo_anemia_junin_v4.mp4` | Anexo A | Grabar con `video/GUION_DEMO.md`, subir a Drive y reemplazar `[pendiente: enlace de Drive]` | Todo el equipo |

## Datos de portada pendientes (no son capturas)

- `[pendiente: código de sección / NRC]`
- `[pendiente: DD/MM/AAAA]` (fecha de entrega)
- `[pendiente: enlace de Drive]` (Anexo A)
