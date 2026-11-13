# Intercambios entre compañeros y sus IA

Canal compartido de preguntas, propuestas, respuestas y traspasos. Leer primero la [entrada común](../CLAUDE.md) y el [protocolo](../coordinacion/PROTOCOLO.md). Los estados oficiales de tareas siguen en el [tablero](../coordinacion/TABLERO.md).

## Escribir un mensaje

1. Copiar [INTERCAMBIO.md](../plantillas/INTERCAMBIO.md) a un archivo con patrón `T-###_<autor>_<tema>.md` en esta carpeta. Usar nombre de autor y tema en minúsculas, sin espacios ni tildes. Para una respuesta usar otro tema o sufijo que no exista; no sobrescribir mensajes.
2. Completar fecha y zona horaria, integrante autor, asistente, destinatario, tarea, rama y commit base. Diferenciar observado, propuesta y pendiente. Incluir rutas y comprobaciones que permitan reproducir lo descrito.
3. Enlazar el mensaje desde la nota de la tarea si requiere coordinación. Si solicita un entregable de otro rol o una ruta nueva, abrir además la solicitud formal correspondiente en `.claude/coordinacion/solicitudes/`.
4. Responder en un archivo propio, enlazando el mensaje original. Si cambia una decisión o un estado, actualizar su fuente canónica: tablero, ADR, solicitud o informe. No considerar aprobada una propuesta sin evidencia de la decisión del responsable.
5. Para compartir el mensaje en otro equipo se necesita publicarlo en una rama y que el destinatario incorpore esa versión, siguiendo la autorización Git de su sesión. No hay notificaciones ni sincronización automática.

## Retomar conversaciones

Buscar por el ID `T-###`, revisar la rama y el commit citados y seguir los enlaces entre mensajes. La fecha o la presencia de un archivo no prueban que la otra persona esté trabajando en ese momento. Antes de editar archivos compartidos, revisar quién tiene la tarea en curso y acordar el reparto. Si se integra una versión antigua de un mensaje, preservar los aportes de ambos autores.

Esta carpeta empieza con las instrucciones y la plantilla. No se han inventado mensajes, respuestas, compromisos ni aprobaciones de otros integrantes.
