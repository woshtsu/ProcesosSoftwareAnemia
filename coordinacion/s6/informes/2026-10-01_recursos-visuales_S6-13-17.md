# Informe recursos-visuales: tareas S6-13 a S6-17 (2026-10-01)

Rama `feature/s6-integrador-final`. Sin commits. Fuentes en `diagramas/src/`; PNG a 200 dpi (la 65 a 150 dpi por el peso de las capturas) y SVG con el mismo nombre. PlantUML local (smetana) y matplotlib de `herramientas/.venv`.

| Error | Figura | Valor final |
| --- | --- | --- |
| E-01 | 59, 64 | Sin «77/77 en verde». 59: 62 + 11 + 4 = 77 declaradas en el tag; 62 + 11 = 73 reproducidas el 01/10/2026; E2E sin reproducir; carga en recuadro aparte «no cuenta en el total». 64: «77 declaradas (62+11+4); 73 reproducidas el 01/10/2026» |
| E-02 | 62 | Seis barras EP-1.T 5, HU-01 5, HU-03 3, HU-02 3, HU-04 2, HU-05 3 = 21; cuadro «77 declaradas; 73 reproducidas» |
| E-03 | 63 | Completado acumulado 5, 10, 13, 16, 18, 21 (termina en 21); sin serie ideal artificial |
| E-04 | 63 | Sin «01-28 Sep» ni git log como serie. Título «planificado vs completado por HU/tarea»; pie: entrega 30/09 frente al hito H1 del 28/09 (+2 días) |
| E-05 | 67 | Cinco factores en Alto con los textos de la Tabla 7 |
| E-06 | 51 | Alt. 1 4,75; Alt. 2 3,85 Kanban + DevOps + DataOps; Alt. 3 2,95 Incremental + Espiral sin automatización; descartados Cascada 8/30 y Scrum 27/30 (Tabla 8) |
| E-07 | 50 | Seis brechas B1-B6 y mejoras M1-M6 con INC-1, INC-2, INC-4, INC-3, INC-5 e INC-3/INC-6 (Tabla 5) |
| E-08 | 68 | INC-2 agenda y alertas; INC-3 sin conexión y sincronización (Sprint 4, H3); INC-4 mensajería y barreras (Sprint 5, H4); INC-5 datos y modelo; INC-6 tablero territorial (Sprints 7-8); hitos H0 a H7 (Tablas 15 y 16) |
| E-09 | 55 | `v_ultimo_control`: vista simple, no materializada, `DISTINCT ON` (verificado en el SQL) |
| E-10 | 66 | ADR-002 «PWA con borrador local (el registro requiere conexión)»; cola sin conexión en INC-3; cabecera sin solape. 64 también dice «PWA con borrador local» |
| E-11 | 61 | Coma decimal (2 170 → 2 336; 36,74 → 39,56); anotación «Reporte: 2 200 ms a 74 ms (97 % menos latencia p95 en ese endpoint)» sin solapes |
| E-12 | 50-58, 64, 68 | Eliminado `skinparam padding` en las 11 fuentes: sin banner (comprobado en los SVG). Glifos «✓», «━» quitados (50, 64, 68, 62, 63). 58 rehecha compacta, 3443x933 (aprox. 3,7:1), texto de 15 pt. 65 con panel HU-04 (`04_seguimiento.png`) |

Otros cambios: fuente Calibri sustituida por Arial; scripts Python con rutas relativas al archivo; 60 sin cambios de datos.

## No se pudo o no se hizo

- La 58 no llega a 16:9 exacto: smetana ignora los enlaces ocultos; es horizontal y legible, pero más ancha (aprox. 3,7:1).
- En las 50 y 68 el motor smetana pone el TO-BE a la izquierda del AS-IS en la 50, y la 68 es una columna vertical alta; son legibles pero no ideales para diapositiva.
- La 60 no se tocó (cifra «641 sentencias» es la declarada; la reproducida fue 548) y su leyenda roza la última barra.
- 52, 53, 54 y 56 solo se regeneraron (banner fuera); en la 57 se quitaron además las comillas de los mensajes y el aviso «This position is ignored: BOTTOM» (nota inferior pasada a footer); no se rediseñaron.
- No se tocaron los .md de entregables ni la presentación: el informe y las diapositivas deben cambiar sus textos de la Fig. 13 (S6-18) y regenerar el PPTX (S6-19).
