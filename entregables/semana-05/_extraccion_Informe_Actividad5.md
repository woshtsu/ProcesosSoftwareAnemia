# Extracción de texto: Informe Actividad 5 — PMV Anemia Junín

> Texto extraído automáticamente con pypdf desde `Informe_Actividad5_PMV_AnemiaJunin.pdf` (12 páginas), modo *layout* (tablas alineadas en bloques de texto).
> Es material de TRABAJO/BASE, no un entregable. Figuras y parte del formato se pierden; ante dudas, consultar el PDF original.

## Página 1

```text
                                                     UNIVERSIDAD CONTINENTAL
                                       Facultad de Ingeniería · Procesos de Software (ASUC01702)

                            INFORME TÉCNICO — ACTIVIDAD 5

                                Ejecución de los Procesos Principales para el Primer Incremento (PMV)

                 Sistema Inteligente para Detección Temprana de Anemia Infantil
                                                   en Zonas Rurales de Junín

                        Enfoque de arquitectura hexagonal (puertos y adaptadores) aplicado al Incremento 1



 Integrante                                                       Rol en el proyecto
 Porras Veli, Ricardo                                             Ingeniero de Proceso

 Auqui Huincho, Tania                                             Ingeniero de Desarrollo y Prototipado
 Huamani Rodriguez, Jean Piero                                    Ingeniero de Calidad y Mejora del Proceso



 Ciclo académico                                  2026-20 · IX ciclo
 Unidad                                           II — Implementación del proceso de software

 Incremento entregado                             Incremento 1: registro nominal validado y expediente digital
 Modelo de proceso                                Iterativo-incremental · Scrum · DevOps (base para MLOps en incrementos posteriores)

 Arquitectura                                     Hexagonal (puertos y adaptadores) — ver Sección 2

 Repositorio                                      Estructura hexagonal con pruebas automatizadas (ver README.md del código fuente)



  Ambiente de pruebas. Todas las evidencias de este informe (capturas, pruebas, reporte) usan datos SINTÉTICOS
  generados por tools/sembrar_datos.py. Ningún dato corresponde a una persona real. La clasificación de anemia que muestra
  el sistema es referencial: no diagnostica ni reemplaza el criterio del profesional de salud.
```

## Página 2

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)

1. Delimitación de Requisitos del PMV — Matriz 1.1
El alcance del Incremento 1 se fijó en las Guías de las Semanas 1-2 y 3-4 (Matriz de Priorización Ponderada, Sección 9; INC-1 con
la puntuación más alta: 4.60/5) y se ejecuta aquí en código real. Las cinco historias cubren el ciclo completo del registro nominal:
crear, consultar/actualizar, validar en el punto de captura, listar en seguimiento y reportar el periodo.

 ID                   Historia de usuario (Como… quiero…                     Prioridad        Criterios de aceptación                        Producto de
                      para…)                                                                  (Given-When-Then)                              trabajo
 HIST-1.1             Como personal de salud de la posta,                    Alta /           Dado que ingreso datos válidos,                Código fuente +
 (HU-01)              quiero registrar a un niño nuevo con sus               Medio            cuando presiono «Guardar»,                     CP-08, CP-08b,
                      datos clínicos básicos (DNI, nombres,                                   entonces el expediente se crea, se             CP-20, CP-22,
                      fecha de nacimiento, sexo, peso, distrito,                              calcula la alerta visual si hay                CP-26
                      altitud, y opcionalmente un dosaje de                                   dosaje, y el DNI queda protegido
                      hemoglobina) para iniciar su expediente                                 contra duplicados (409).
                      digital.
 HIST-1.2             Como personal de salud, quiero consultar               Alta /           Dado un DNI existente, cuando lo               Código fuente +
 (HU-02)              el expediente de un niño por DNI,                      Medio            consulto, entonces veo sus datos y             CP-10, CP-11,
                      actualizar sus datos editables (peso,                                   todos sus dosajes ordenados;                   CP-12, CP-23,
                      distrito, altitud, cuidador) y registrar                                cuando actualizo un campo                      CP-28b
                      nuevos dosajes, para mantener su                                        editable, el cambio se guarda sin
                      seguimiento al día sin perder el historial.                             tocar la identidad del niño ni los
                                                                                              dosajes previos.

 HIST-1.3             Como sistema, quiero validar cada dato                 Alta / Alto      Dado que un dato está fuera de                 Código fuente +
 (HU-03)              ingresado (DNI de 8 dígitos, nombres,                                   rango o mal formado, cuando se                 CP-01 a CP-07,
                      fechas coherentes, peso 1-30 kg,                                        procesa el formulario o la API,                CP-09b, CP-13,
                      hemoglobina 2,0-25,0 g/dL con un                                        entonces se rechaza (400) con un               CP-13b, CP-21,
                      decimal, altitud 0-4999 msnm, celular de                                código y mensaje comprensible por              CP-27
                      9 dígitos) para que ningún registro                                     campo, y no se guarda nada.
                      incompleto o imposible entre a la base de
                      datos.

 HIST-1.4             Como personal de salud, quiero ver la                  Alta /           Dado que existen niños con                     Código fuente +
 (HU-04)              lista de niños en seguimiento activo (6 a              Medio            distintas clasificaciones, cuando              CP-14, CP-14b,
                      59 meses) ordenada por severidad de su                                  abro la lista, entonces los más                CP-24, CP-28
                      última clasificación, con filtros por                                   severos aparecen primero, con una
                      distrito, clasificación y texto, para                                   alerta visual (semáforo) con texto
                      priorizar la atención del día.                                          además de color.

 HIST-1.5             Como coordinador del proyecto, quiero                  Media /          Dado un rango de fechas, cuando                Código fuente +
                      un reporte del periodo con niños y                     Bajo             genero el reporte, entonces veo los            CP-15, CP-24,
                      dosajes registrados, distribución por                                   conteos, la distribución y el                  CP-28b, CP-32
                      clasificación y distrito, y el indicador «%                             indicador de calidad calculado a
                      de registros sin error crítico», para                                   partir de la traza de intentos (sin
                      verificar la calidad del dato desde el                                  datos personales).
                      primer incremento.
Las cinco historias corresponden 1 a 1 con las HIST-1.1 a HIST-1.5 del WBS definido en la Guía de las Semanas 3-4 (Sección 8.1) y con la fila
«Incremento 1» de la Matriz de Actividad-Incremento (Sección 7 de esa guía): registro nominal validado -> reduce duplicidad y errores del registro
manual -> indicador «registros sin error crítico ÷ evaluados × 100».






























Procesos de Software (ASUC01702) · 2026-20Página 2
```

## Página 3

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)
2. Diseño Arquitectónico y Estructura de Datos — Matriz 2.1

 Componente del              Descripción técnica del PMV                             Producto de trabajo                   Criterio de terminación
 diseño                                                                              esperado                              (DoD)

 Arquitectura de             Arquitectura hexagonal (puertos y                       Diagrama de paquetes y                Revisado por el equipo y
 software                    adaptadores). El núcleo (domain +                       diagrama de despliegue                VERIFICADO
                             application) no importa Flask ni SQLite; los            (Figuras 1 y 3)                       AUTOMÁTICAMENTE:
                             adaptadores de entrada (REST, Web) y de                                                       tests/test_arquitectura.py
                             salida (SQLite, JSON de norma, reloj)                                                         recorre el AST del código y
                             dependen del núcleo, nunca al revés.                                                          falla el build si
                                                                                                                           domain/application llegan a
                                                                                                                           importar Flask, sqlite3 o un
                                                                                                                           adaptador.
 Modelo de datos             Esquema relacional portable (SQLite en el               Script DDL (db/schema.sql)            Script ejecutado
                             PMV; sintaxis compatible con PostgreSQL                 y diagrama entidad-relación           satisfactoriamente: CP-16 a
                             para la migración del Incremento 3): nino,              (Figura 4)                            CP-19 y CP-32 lo verifican
                             dosaje_hemoglobina y intento_registro                                                         contra SQLite real (49
                             (trazabilidad de calidad, sin datos                                                           pruebas en verde, ver
                             personales).                                                                                  Sección 4).

 Contratos de API /          5 endpoints REST/JSON bajo /api/v1: alta,               Especificación OpenAPI 3.0            Contrato validado
 interfaz                    consulta, actualización parcial, registro de            (docs/openapi.yaml)                   automáticamente: CP-25
                             dosaje y listado con filtros, más el reporte del                                              compara, ruta por ruta, el
                             periodo.                                                                                      YAML contra las rutas Flask
                                                                                                                           realmente registradas.

2.1 Diagrama de paquetes (capas hexagonales)
El diagrama se genera con tools/diagramas.py, que antes de dibujar recorre el árbol de sintaxis (AST) del código y comprueba que
cada flecha de dependencia mostrada exista de verdad como import, y que ninguna de las dependencias prohibidas por la regla
hexagonal aparezca (por ejemplo, que domain nunca importe adapters). Si el código cambiara y el dibujo quedara desactualizado, la
generación del diagrama fallaría en vez de mostrar información incorrecta.








































Procesos de Software (ASUC01702) · 2026-20Página 3
```

## Página 4

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)
   Figura 1. Diagrama de paquetes: domain (núcleo) <- application (casos de uso y puertos) <- adapters.inbound / adapters.outbound, ensamblados por
                                                                                 bootstrap.
2.2 Vista conceptual: puertos y adaptadores





































 Figura 2. El núcleo (hexágono) define los puertos GestionExpedientes (entrada) y NinoRepositorio / ProveedorNormativa / Reloj (salida) como interfaces
                                     Python (typing.Protocol); los adaptadores los implementan sin que el núcleo los conozca.
2.3 Diagrama de despliegue
El ambiente de pruebas es un único proceso Python (Flask/Werkzeug) que sirve la API REST y la interfaz web, y persiste en un
archivo SQLite. El diagrama marca en línea discontinua los puntos de extensión ya previstos por el diseño hexagonal para
incrementos futuros (PostgreSQL central en el Incremento 3, WhatsApp Business API en el Incremento 4): se conectarían como
nuevos adaptadores, sin tocar el núcleo.




















                                                Figura 3. Diagrama de despliegue del ambiente de pruebas del PMV.



Procesos de Software (ASUC01702) · 2026-20Página 4
```

## Página 5

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)
2.4 Modelo de datos (entidad-relación)
























   Figura 4. Modelo entidad-relación de db/schema.sql, con las restricciones CHECK que protegen la integridad del dato incluso si el dominio tuviera un
                                                                    defecto (verificado por CP-18).

Nota de trazabilidad normativa. La tabla de ajuste de hemoglobina por altitud y los cortes de clasificación por grupo etario no
están escritos en el código: viven en config/norma_nts213_2024.json, versionados con la fuente oficial (RM 251-2024/MINSA, que
aprueba la NTS N.° 213-MINSA/DGIESP-2024 y deroga la NTS 134-2017 citada en la guía de la asignatura; modificada por RM
429-2024/MINSA). Las dos bandas de altitud por encima de 4000 msnm quedan marcadas como «no verificadas» en el archivo, y el
sistema muestra una advertencia explícita cada vez que se usan (ver Figura 6), en vez de asumir silenciosamente que el valor es
correcto.

Anexo A. Construcción e Implementación del Código — Matriz 3.1

El código fuente completo se entrega en el repositorio del PMV (ver estructura y README.md del entregable de código). Esta
matriz resume, por componente, la tecnología, la convención de ramas Git prevista para el flujo Scrum/DevOps del proyecto (Guía
de las Semanas 3-4, Sección 11.2) y el criterio de terminación verificado en este incremento.

 Módulo /                      Lenguaje /                  Estrategia de ramificación          Producto de trabajo              Criterio de terminación
 componente                    framework                   (Git)                                                                (DoD)

 Núcleo (domain +              Python 3.12 ·               feature/hu01-registro-nino,         Módulos domain/ y                0 issues de análisis
 application)                  biblioteca estándar         feature/hu02-consulta-expe          application/                     estático propio
                               (sin frameworks)            diente,                                                              (tools/lint.py) y 0
                                                           feature/hu03-validaciones                                            dependencias de
                                                                                                                                Flask/SQLite verificado
                                                                                                                                por AST (CP-30).

 Adaptadores de                Flask 3 (Blueprints)        feature/hu01-api-registro,          pmv_anemia/adapters/inb          Contrato OpenAPI
 entrada (API + Web)           + Jinja2                    feature/hu04-listado-web            ound/ + plantillas HTML          validado contra las rutas
                                                                                                                                reales (CP-25); UI
                                                                                                                                responsiva probada en
                                                                                                                                420 px (Figura 9).

 Persistencia (Base de         SQLite 3 (esquema           feature/hu01-esquema-sqlit          db/schema.sql +                  Script ejecutado y
 Datos)                        portable a                  e                                   pmv_anemia/adapters/out          poblado con 24 registros
                               PostgreSQL)                                                     bound/sqlite_repo.py             sintéticos
                                                                                                                                (tools/sembrar_datos.py)
                                                                                                                                ; restricciones CHECK
                                                                                                                                verificadas incluso sin
                                                                                                                                pasar por el dominio
                                                                                                                                (CP-18).

 Calidad y                     unittest (stdlib) ·         —                                   tools/lint.py,                   49 pruebas en verde,
 automatización                linter y medidor de                                             tools/cobertura.py, tests/       95.8% de cobertura de
                               cobertura propios                                                                                líneas, 0 hallazgos del
                               (stdlib)                                                                                         análisis estático (Sección
                                                                                                                                3).
En este PMV, ejecutado en un ambiente sin conexión a paquetes externos, la suite de pruebas corre con unittest de la biblioteca estándar en lugar
de Pytest, y el análisis estático y la cobertura se implementaron también sin dependencias externas (tools/lint.py, tools/cobertura.py). El

Procesos de Software (ASUC01702) · 2026-20Página 5
```

## Página 6

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)
README.md documenta cómo ejecutar la suite equivalente con Pytest, pytest-cov y Ruff (declarados en requirements-dev.txt) cuando el entorno de
CI (GitHub Actions, .github/workflows/ci.yml) sí tiene acceso a PyPI.
3. Evidencia de Pruebas e Integración del PMV — Matriz 4.1

 49 casos de prueba                       95.8% de cobertura de líneas             0 hallazgos del análisis estático        25.8 ms de latencia máxima
 automatizados, en verde                  (1038/1083)                                                                       observada (umbral: 2000 ms)


La suite cubre las cinco capas del sistema: dominio (reglas de negocio puras), casos de uso (con dos repositorios intercambiables:
memoria y SQLite, para probar que ambos cumplen el mismo puerto), integración SQLite real, API REST y UI web, más una
prueba de rendimiento y una prueba arquitectónica que falla si se viola la regla de dependencia hexagonal.

 ID caso(s)              Escenario de prueba evaluado                         Tipo de prueba            Resultado esperado vs.           Criterio de
                                                                                                        real                             terminación (DoD)
 CP-01 a CP-07           Validación de dominio: DNI, fechas y                 Unitaria                  7/7 exitosos                     100 % de las
                         edad, rango/formato de hemoglobina,                                                                             pruebas de dominio
                         ajuste por altitud, clasificación por grupo                                                                     ejecutadas y en
                         etario, actualización de solo los campos                                                                        verde.
                         editables.

 CP-08 a CP-15           Casos de uso completos (registrar,                   Integración               16/16 exitosos (8                Mismo
                         duplicado, consultar, actualizar, nuevo                                        historias × 2                    comportamiento con
                         dosaje, menor no evaluable, banda no                                           repositorios)                    ambos adaptadores
                         verificada, listado con filtros, reporte) —                                                                     de salida
                         ejecutados dos veces, contra repositorio                                                                        (cumplimiento real
                         en memoria y contra SQLite real.                                                                                del puerto
                                                                                                                                         NinoRepositorio).
 CP-16 a CP-19,          DDL idempotente, persistencia entre                  Integración               5/5 exitosos                     El esquema protege
 CP-32                   reinicios, restricciones CHECK de la BD,             (SQLite real)                                              la integridad incluso
                         adaptadores conformes a los puertos                                                                             si el dominio tuviera
                         (Protocol), traza sin datos personales.                                                                         un defecto.
 CP-20 a CP-25           API REST: alta (201), validación (400),              Integración               6/6 exitosos                     El YAML publicado
                         duplicado (409), consulta/actualización,             (HTTP, cliente de                                          coincide
                         listado y reporte, y el contrato OpenAPI             prueba)                                                    exactamente con lo
                         contra las rutas Flask reales.                                                                                  implementado.

 CP-26 a CP-29           UI web: formulario válido con alerta                 Sistema / UI              4/4 exitosos, todas las          Cero defectos
                         visual, formulario con errores que                                             operaciones < 2 s                bloqueantes;
                         conserva los datos, semáforo con texto                                                                          notificación visual
                         (no solo color), rendimiento registrando y                                                                      inmediata.
                         consultando 60 niños.

 CP-30, CP-31            Regla de dependencia hexagonal:                      Arquitectónica            2/2 exitosos                     La arquitectura
                         domain/application no importan Flask ni              (análisis estático                                         declarada es la
                         sqlite3; adaptadores de entrada no                   vía AST)                                                   arquitectura real,
                         conocen los de salida.                                                                                          verificado
                                                                                                                                         automáticamente en
                                                                                                                                         cada build.

Ejecución completa: python -W error -m unittest discover -s tests -t . -v -> «Ran 49 tests … OK» (0 fallos, 0 errores, advertencias tratadas como
error). Cobertura de líneas medida con tools/cobertura.py: 95.8% (1038 de 1083 líneas ejecutables), por encima del 80% definido como meta en la
Guía de las Semanas 3-4.

3.1 Capturas de la ejecución (evidencia visual)
























Procesos de Software (ASUC01702) · 2026-20Página 6
```

## Página 7

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)






















































          Figura 5. Lista de niños en seguimiento activo (HIST-1.4): ordenada por severidad, con alerta visual con texto además de color y filtros por
                                                                                 distrito/clasificación/texto.

























Procesos de Software (ASUC01702) · 2026-20Página 7
```

## Página 8

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)












































    Figura 6. Formulario de registro (HIST-1.1/1.3) rechazando datos inválidos: DNI de 7 dígitos, celular sin el formato esperado y hemoglobina fuera de
                                              rango, cada uno con su mensaje y código de error; los datos válidos se conservan.






































Procesos de Software (ASUC01702) · 2026-20Página 8
```

## Página 9

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)





















































    Figura 7. Expediente de un niño en Junín (4107 msnm, HIST-1.2): muestra la advertencia de banda de altitud no verificada descrita en la Sección 2.4.



























Procesos de Software (ASUC01702) · 2026-20Página 9
```

## Página 10

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)














































      Figura 8. Reporte del periodo (HIST-1.5): indicador «% de registros sin error crítico» calculado a partir de la traza de intentos, sin exponer datos
                                                                                          personales.



































Procesos de Software (ASUC01702) · 2026-20Página 10
```

## Página 11

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)





































































        Figura 9. El mismo formulario de registro en un ancho de 420 px, verificando que la interfaz es utilizable desde un celular en la posta piloto.

4. Demostración del Despliegue y Entrega de Valor — Matriz 5.1



Procesos de Software (ASUC01702) · 2026-20Página 11
```

## Página 12

```text
Sistema de Detección Temprana de Anemia Infantil — JunínActividad 5 · Incremento 1 (PMV)

 Incremento                  Funcionalidad operativa                      Resultado directo para el usuario            Indicador de valor / operativo
 liberado                    entregada                                                                                 asociado

 Incremento 1 (PMV)          Registro nominal validado, consulta          El personal de la posta registra a           Registros sin error crítico ÷
                             y actualización de expediente,               cada niño una sola vez, con                  evaluados × 100. En la
                             listado de seguimiento con                   validación automática de errores             demostración con datos
                             semáforo referencial, y reporte del          críticos, consultable desde el mismo         sintéticos: 24 aceptados de 28
                             periodo con indicador de calidad             dispositivo — elimina el triple              evaluados = 85,7 % (Figura 8).
                             del dato.                                    registro manual (historia clínica +
                                                                          tarjeta de control + digitación HIS)
                                                                          descrito en la Guía de la Semana 1.
El despliegue se demuestra en un ambiente de pruebas real (no una simulación): un servidor Flask ejecutando el código del
repositorio, con una base de datos SQLite poblada por tools/sembrar_datos.py (24 niños sintéticos con distintas clasificaciones y
distritos, más 3 intentos inválidos para poblar el indicador de calidad), y verificado con un smoke test HTTP que ejercita cada
endpoint contra el servidor levantado.

 Verificación de despliegue          Acción ejecutada                           Resultado esperado                               Estado

 Arranque del servidor               python run.py (con datos                   Responde en /api/v1/salud                        Cumple
                                     sembrados)
 Registro válido (HU-01)             POST /api/v1/ninos con datos               201 Created + alerta visual                      Cumple
                                     correctos

 Rechazo de duplicado                POST /api/v1/ninos con DNI                 409 Conflict                                     Cumple
                                     existente

 Rechazo de datos inválidos          POST /api/v1/ninos con DNI y Hb            400 con errores por campo                        Cumple
 (HU-03)                             inválidos
 Consulta y actualización            GET y PATCH /api/v1/ninos/<dni>            200 con los datos actualizados                   Cumple
 (HU-02)
 Listado y filtros (HU-04)           GET /api/v1/ninos y                        200 con el listado esperado                      Cumple
                                     ?clasificacion=SEVERA

 Reporte del periodo                 GET /api/v1/reportes/registros             200 con el indicador de calidad                  Cumple
 (HU-05)

 Interfaz web                        GET /, /ninos/nuevo, /ninos/<dni>          200, contenido esperado presente                 Cumple

Smoke test completo: python tools/smoke_test.py -> 13 verificaciones, 0 fallos, latencia máxima 25.8 ms (umbral definido: 2000 ms) ->
RESULTADO: APROBADO. El script es reutilizable contra cualquier URL (incluida una futura posta piloto) y no depende de datos hardcodeados
más allá del DNI de prueba «90099999», que crea si no existe.
4.1 Reproducibilidad de la demostración
Todo lo mostrado en este informe (Secciones 3 y 4) se regenera con un único comando: python tools/generar_evidencias.py. El
script ejecuta el linter, corre la suite de pruebas en modo detallado, mide la cobertura, siembra una base de datos temporal, levanta
un servidor real, toma las capturas de pantalla y corre el smoke test contra ese servidor — nada en este informe fue redactado a
mano ni copiado de una ejecución anterior.

5. Conclusiones y siguiente incremento

El Incremento 1 (registro nominal validado y expediente digital) queda completo y desplegable: arquitectura hexagonal
implementada y verificada automáticamente (no solo documentada), cinco historias de usuario con sus criterios de aceptación
cumplidos, esquema de datos ejecutado con restricciones reales, contrato de API validado contra el código, y una demostración de
despliegue reproducible con un solo comando.
Siguiendo el plan de la Guía de las Semanas 3-4 (Sección 11.1), HIST-1.5 (reporte del periodo) se había planificado para el Sprint 2;
en esta actividad se adelantó e implementó junto con el resto del incremento, por lo que el Sprint 2 puede concentrarse íntegramente
en los ajustes que surjan de la revisión con personal de salud. El siguiente incremento (INC-2: agenda automática según NTS
134/213 y alertas internas) puede apoyarse directamente en el puerto NinoRepositorio y en el esquema de datos ya construidos, sin
modificar el núcleo del Incremento 1.

  Limitación declarada. Dos bandas de altitud (4000-4499 y 4500-4999 msnm) de la tabla de ajuste de hemoglobina están
  marcadas como «no verificadas» en config/norma_nts213_2024.json y generan una advertencia visible en el sistema (Figura
  7) en vez de presentarse como un hecho confirmado. Se recomienda contrastarlas con la Tabla 1 modificada por la RM
  429-2024/MINSA antes de un uso clínico real, tal como señala la Sección 12 de la Guía de las Semanas 3-4 sobre la
  validación de criterios clínicos con la microred.






Procesos de Software (ASUC01702) · 2026-20Página 12
```
