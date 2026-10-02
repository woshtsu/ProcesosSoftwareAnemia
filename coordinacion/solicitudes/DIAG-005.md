# DIAG-005 — Clases del dominio de la visión TO-BE (Semana 1, anexo)

- **Estado:** RESUELTA
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-002
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Baja

## Tipo de diagrama

- [x] UML clases / modelo de dominio

## Requisito que cubre

- **Guía:** `guias/S1_Guia_trabajo_semana_1.md` — no es requisito explícito; contenido sustantivo del equipo que se conserva en anexo.
- **Entregable destino:** `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` — Anexo B.2, Figura 11.
- **Motivo:** la figura actual (`entregables/semana-01/img/image11.png`, 400×505 px) es ilegible; la fuente original era Mermaid (v4) y debe pasar a PlantUML.
- **No confundir** con `08_modelo_datos` (esquema SQLite real del PMV). Este es el modelo conceptual de la visión; debe transcribirse **tal cual**, sin ajustarlo al código.

## Contenido requerido

Transcribir exactamente estas 8 clases (atributos públicos `+`, tipos tal como están):

- **Nino**: `DNI: String`, `nombres: String`, `fechaNacimiento: Date`, `tipoNacimiento: String`, `altitudResidencia: Float`; `calcularEdadMeses()`.
- **Expediente**: `numeroHistoria: String`, `fechaApertura: Date`, `dniMadre: String`; `abrirExpediente()`.
- **Dosaje**: `fecha: Date`, `resultadoHb: Float`, `hemoglobinaAjustada: Float`, `tipoDosaje: String`; `evaluarAnemia()`.
- **Tratamiento**: `fechaInicio: Date`, `tipoSuplemento: String`, `duracionMeses: Int`, `porcentajeAdherencia: Float`; `actualizarAdherencia()`.
- **ControlProgramado**: `fechaProgramada: Date`, `estado: String`, `tipo: String`; `generarAlerta()`.
- **VisitaDomiciliaria**: `fechaVisita: Date`, `hallazgos: String`, `barrerasIdentificadas: String`; `registrarVisitaOffline()`.
- **ModeloPredictivoIA** (color distinto, componente de IA): `scoreRiesgo: Float`, `variablesClave: String`; `calcularScore()`.
- **NotificacionWhatsApp** (color distinto, integración externa): `numeroCelular: String`, `mensaje: String`, `estadoRespuesta: String`; `enviarMensaje()`, `procesarRespuesta()`.

Asociaciones (con rol y multiplicidad):
- Nino "1" — "1" Expediente : posee
- Expediente "1" — "*" Dosaje : registra
- Expediente "1" — "*" Tratamiento : contiene
- Tratamiento "1" — "*" ControlProgramado : genera
- Nino "1" — "*" VisitaDomiciliaria : recibe
- ControlProgramado "1" — "1" NotificacionWhatsApp : dispara
- Nino "1" — "1" ModeloPredictivoIA : evaluadoPor

## Fuentes de verdad

- `archivo/versiones-anteriores/semana-01/Entregable_Semana1_Anemia_Junin_v4.md` §9.2 (Mermaid `classDiagram`).
- `entregables/semana-01/img/image11.png`.

## Nombre de archivo sugerido

`14_s1_clases_dominio_vision` → `diagramas/src/14_s1_clases_dominio_vision.puml`, `diagramas/png/14_s1_clases_dominio_vision.png`, `diagramas/svg/14_s1_clases_dominio_vision.svg`.

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4.
- [ ] 8 clases, atributos, métodos y 7 asociaciones exactamente como arriba.
- [ ] Registrado en `diagramas/README.md`.

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** 2026-10-01
- **Resultado:** RESUELTA (cierre administrativo del sincronizador, 2026-10-01: existen fuente `diagramas/src/14_s1_clases_dominio_vision.puml`, `diagramas/png/14_s1_clases_dominio_vision.png` y `diagramas/svg/14_s1_clases_dominio_vision.svg`; la verificación del contenido frente al entregable corresponde a revisor-documental / inspector-guia)
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 11. Diagrama de clases del dominio de la visión TO-BE (elaboración propia).](../../diagramas/svg/14_s1_clases_dominio_vision.svg)`
- **Notas:**
