-- =====================================================================
-- Esquema de datos — PostgreSQL 14+ (versión 4.0.0-inc4)
-- Sistema de Detección Temprana de Anemia Infantil — Junín
-- Las restricciones CHECK repiten las reglas de plausibilidad del dominio
-- (defensa en profundidad: la base rechaza datos imposibles aunque se
-- carguen fuera de la API).
--
-- Origen de los datos (ADR-009): los niños registrados desde el sistema
-- (origen 'SISTEMA') exigen DNI, nombres, apellidos, sexo y tutor; los del
-- dataset anonimizado de la DIRESA Junín ('DATASET_DIRESA_JUNIN') son
-- seudónimos con código propio y esos campos pueden ser NULL. UNIQUE(dni)
-- admite varios NULL en PostgreSQL, por lo que solo se valida el DNI cuando existe.
-- Para actualizar una base 1.x existente use db/02_migracion_v2_0.sql; desde la 2.0 use db/03_migracion_v3_0.sql y desde
-- la 3.0 use db/04_migracion_v4_0.sql.
-- =====================================================================

CREATE TABLE IF NOT EXISTS nino (
    id               VARCHAR(36)  PRIMARY KEY,
    dni              VARCHAR(8)   UNIQUE CHECK (dni IS NULL OR dni ~ '^[0-9]{8}$'),
    nombres          VARCHAR(80),
    apellidos        VARCHAR(80),
    sexo             VARCHAR(1)   CHECK (sexo IS NULL OR sexo IN ('F', 'M')),
    fecha_nacimiento DATE         NOT NULL,
    establecimiento  VARCHAR(120) NOT NULL,
    distrito         VARCHAR(80)  NOT NULL,
    comunidad        VARCHAR(80)  NOT NULL,
    altitud_m        DOUBLE PRECISION NOT NULL CHECK (altitud_m BETWEEN 0 AND 5000),
    tutor_nombre     VARCHAR(120),
    tutor_celular    VARCHAR(9)   CHECK (tutor_celular IS NULL OR tutor_celular ~ '^9[0-9]{8}$'),
    estado           VARCHAR(10)  NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'ALTA')),
    origen           VARCHAR(24)  NOT NULL DEFAULT 'SISTEMA'
                     CONSTRAINT ck_nino_origen CHECK (origen IN ('SISTEMA', 'DATASET_DIRESA_JUNIN')),
    codigo_origen    VARCHAR(20)  UNIQUE,
    red              VARCHAR(80),
    microred         VARCHAR(80),
    provincia        VARCHAR(80),
    registrado_por   VARCHAR(60)  NOT NULL,
    creado_en        TIMESTAMPTZ  NOT NULL,
    actualizado_en   TIMESTAMPTZ  NOT NULL,
    CONSTRAINT ck_nino_sistema_completo CHECK (
        origen <> 'SISTEMA' OR (dni IS NOT NULL AND nombres IS NOT NULL AND apellidos IS NOT NULL
                                AND sexo IS NOT NULL AND tutor_nombre IS NOT NULL)),
    CONSTRAINT ck_nino_dataset_codigo CHECK (origen <> 'DATASET_DIRESA_JUNIN' OR codigo_origen IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS ix_nino_comunidad ON nino (comunidad);
CREATE INDEX IF NOT EXISTS ix_nino_estado    ON nino (estado);
CREATE INDEX IF NOT EXISTS ix_nino_origen    ON nino (origen);

-- peso_kg y talla_cm son NULL solo en las evaluaciones importadas (el dataset no las registra);
-- clasificacion_origen conserva la severidad que registró el HIS (LEV, MOD, SEV) en la evaluación de diagnóstico.
CREATE TABLE IF NOT EXISTS evaluacion_hemoglobina (
    id                    VARCHAR(36) PRIMARY KEY,
    nino_id               VARCHAR(36) NOT NULL REFERENCES nino (id) ON DELETE CASCADE,
    fecha                 DATE        NOT NULL,
    edad_meses            INTEGER     NOT NULL CHECK (edad_meses BETWEEN 0 AND 59),
    hemoglobina_observada DOUBLE PRECISION NOT NULL CHECK (hemoglobina_observada BETWEEN 3 AND 20),
    altitud_m             DOUBLE PRECISION NOT NULL,
    hemoglobina_ajustada  DOUBLE PRECISION NOT NULL,
    clasificacion         VARCHAR(12) NOT NULL
                          CHECK (clasificacion IN ('SIN_ANEMIA', 'LEVE', 'MODERADA', 'SEVERA', 'NO_APLICA')),
    clasificacion_origen  VARCHAR(12),
    peso_kg               DOUBLE PRECISION CHECK (peso_kg IS NULL OR peso_kg BETWEEN 1.5 AND 30),
    talla_cm              DOUBLE PRECISION CHECK (talla_cm IS NULL OR talla_cm BETWEEN 40 AND 125),
    registrado_por        VARCHAR(60) NOT NULL,
    creado_en             TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_eval_nino  ON evaluacion_hemoglobina (nino_id);
CREATE INDEX IF NOT EXISTS ix_eval_fecha ON evaluacion_hemoglobina (fecha);

-- HIST-2.4 (ADR-010): asistencia a un control programado. El control se identifica por
-- (nino_id, codigo_control, fecha_programada); la agenda sigue calculándose en el dominio.
CREATE TABLE IF NOT EXISTS asistencia_control (
    id               VARCHAR(36) PRIMARY KEY,
    nino_id          VARCHAR(36) NOT NULL REFERENCES nino (id) ON DELETE CASCADE,
    codigo_control   VARCHAR(10) NOT NULL,
    fecha_programada DATE        NOT NULL,
    estado           VARCHAR(12) NOT NULL CHECK (estado IN ('ASISTIO', 'NO_ASISTIO')),
    motivo           VARCHAR(200),
    evaluacion_id    VARCHAR(36) REFERENCES evaluacion_hemoglobina (id) ON DELETE SET NULL,
    registrado_por   VARCHAR(60) NOT NULL,
    creado_en        TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_asistencia_control UNIQUE (nino_id, codigo_control, fecha_programada),
    CONSTRAINT ck_asistencia_motivo CHECK (estado = 'ASISTIO' OR motivo IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS ix_asistencia_nino ON asistencia_control (nino_id);

-- VIS-3.5: a lo sumo una visita por niño y por día; solo una visita REALIZADA puede decir si consume el suplemento.
CREATE TABLE IF NOT EXISTS visita_domiciliaria (
    id                 VARCHAR(36) PRIMARY KEY,
    nino_id            VARCHAR(36) NOT NULL REFERENCES nino (id) ON DELETE CASCADE,
    fecha              DATE        NOT NULL,
    resultado          VARCHAR(14) NOT NULL
                       CONSTRAINT ck_visita_resultado CHECK (resultado IN ('REALIZADA', 'NO_ENCONTRADO', 'RECHAZADA')),
    consume_suplemento VARCHAR(12) NOT NULL
                       CONSTRAINT ck_visita_consumo CHECK (consume_suplemento IN ('SI', 'NO', 'DESCONOCIDO')),
    observaciones      VARCHAR(500),
    registrado_por     VARCHAR(60) NOT NULL,
    creado_en          TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_visita_nino_fecha UNIQUE (nino_id, fecha),
    CONSTRAINT ck_visita_suplemento CHECK (resultado = 'REALIZADA' OR consume_suplemento = 'DESCONOCIDO')
);
CREATE INDEX IF NOT EXISTS ix_visita_domiciliaria_nino_id ON visita_domiciliaria (nino_id);

-- HIST-3.2: la clave primaria id_operacion (UUID generado en el dispositivo) hace idempotente la sincronización.
-- id_cliente guarda el id temporal de un niño registrado sin conexión para resolver las operaciones posteriores.
CREATE TABLE IF NOT EXISTS operacion_sincronizada (
    id_operacion   VARCHAR(36) PRIMARY KEY,
    tipo           VARCHAR(24) NOT NULL,
    id_dispositivo VARCHAR(60) NOT NULL,
    resultado      VARCHAR(12) NOT NULL
                   CONSTRAINT ck_operacion_resultado CHECK (resultado IN ('APLICADA', 'DUPLICADA', 'CONFLICTO', 'RESUELTA')),
    id_recurso     VARCHAR(36),
    id_cliente     VARCHAR(60),
    fecha_local    TIMESTAMPTZ,
    recibida_en    TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_operacion_cliente ON operacion_sincronizada (id_dispositivo, id_cliente);

-- HIST-3.3: operación que chocó con un dato distinto del servidor; nunca se sobrescribe a ciegas.
CREATE TABLE IF NOT EXISTS conflicto_sincronizacion (
    id              VARCHAR(36) PRIMARY KEY,
    id_operacion    VARCHAR(36) NOT NULL UNIQUE REFERENCES operacion_sincronizada (id_operacion) ON DELETE CASCADE,
    tipo            VARCHAR(24) NOT NULL,
    motivo          VARCHAR(400) NOT NULL,
    nino_id         VARCHAR(36) NOT NULL REFERENCES nino (id) ON DELETE CASCADE,
    id_recurso      VARCHAR(36) NOT NULL,
    datos_cliente   JSONB       NOT NULL,
    datos_servidor  JSONB       NOT NULL,
    estado          VARCHAR(10) NOT NULL DEFAULT 'PENDIENTE'
                    CONSTRAINT ck_conflicto_estado CHECK (estado IN ('PENDIENTE', 'RESUELTO')),
    resolucion      VARCHAR(20)
                    CONSTRAINT ck_conflicto_resolucion CHECK (
                        resolucion IS NULL OR resolucion IN ('CONSERVAR_SERVIDOR', 'APLICAR_CLIENTE', 'DESCARTAR')),
    registrado_por  VARCHAR(60) NOT NULL,
    creado_en       TIMESTAMPTZ NOT NULL,
    resuelto_en     TIMESTAMPTZ,
    resuelto_por    VARCHAR(60)
);
CREATE INDEX IF NOT EXISTS ix_conflicto_sincronizacion_nino_id ON conflicto_sincronizacion (nino_id);
CREATE INDEX IF NOT EXISTS ix_conflicto_sincronizacion_estado ON conflicto_sincronizacion (estado);

-- HIST-4.1 y HIST-4.2 (ADR-014): recordatorio de un control por mensajería. Único por (niño, control, tipo); el control
-- es (codigo_control, fecha_programada) como en asistencia_control. destino es el celular del tutor (9 dígitos).
CREATE TABLE IF NOT EXISTS recordatorio (
    id                 VARCHAR(36)  PRIMARY KEY,
    nino_id            VARCHAR(36)  NOT NULL REFERENCES nino (id) ON DELETE CASCADE,
    codigo_control     VARCHAR(10)  NOT NULL,
    fecha_programada   DATE         NOT NULL,
    tipo               VARCHAR(12)  NOT NULL
                       CONSTRAINT ck_recordatorio_tipo CHECK (tipo IN ('PROXIMO', 'CITA_DEL_DIA', 'VENCIDO')),
    canal              VARCHAR(10)  NOT NULL
                       CONSTRAINT ck_recordatorio_canal CHECK (canal IN ('SIMULADO', 'WHATSAPP', 'SMS')),
    estado             VARCHAR(16)  NOT NULL
                       CONSTRAINT ck_recordatorio_estado CHECK (
                           estado IN ('ENVIADO_SIMULADO', 'ENVIADO', 'ENTREGADO', 'LEIDO', 'FALLIDO')),
    destino            VARCHAR(9)   NOT NULL,
    mensaje            VARCHAR(500) NOT NULL,
    id_externo         VARCHAR(100),
    detalle            VARCHAR(300),
    intentos           INTEGER      NOT NULL DEFAULT 1,
    generado_por       VARCHAR(60)  NOT NULL,
    creado_en          TIMESTAMPTZ  NOT NULL,
    enviado_en         TIMESTAMPTZ,
    actualizado_en     TIMESTAMPTZ  NOT NULL,
    respuesta          VARCHAR(12)
                       CONSTRAINT ck_recordatorio_respuesta CHECK (
                           respuesta IS NULL OR respuesta IN ('CONFIRMA', 'NO_PUEDE', 'REPROGRAMAR')),
    fecha_reprogramada DATE,
    respondido_en      TIMESTAMPTZ,
    respondido_por     VARCHAR(60),
    origen_respuesta   VARCHAR(10)
                       CONSTRAINT ck_recordatorio_origen CHECK (
                           origen_respuesta IS NULL OR origen_respuesta IN ('PERSONAL', 'WHATSAPP')),
    CONSTRAINT uq_recordatorio_control_tipo UNIQUE (nino_id, codigo_control, fecha_programada, tipo),
    CONSTRAINT ck_recordatorio_respondido CHECK (respuesta IS NULL OR respondido_en IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS ix_recordatorio_nino_id ON recordatorio (nino_id);
CREATE INDEX IF NOT EXISTS ix_recordatorio_estado ON recordatorio (estado);
CREATE INDEX IF NOT EXISTS ix_recordatorio_destino ON recordatorio (destino);
CREATE INDEX IF NOT EXISTS ix_recordatorio_id_externo ON recordatorio (id_externo);

-- HIST-4.3 (ADR-014): obstáculo para cumplir el tratamiento o los controles; no se repite (niño, tipo, fecha, fuente).
-- Con el tipo OTRA el detalle es obligatorio. recordatorio_id enlaza la barrera que nació de una respuesta NO_PUEDE.
CREATE TABLE IF NOT EXISTS barrera (
    id              VARCHAR(36)  PRIMARY KEY,
    nino_id         VARCHAR(36)  NOT NULL REFERENCES nino (id) ON DELETE CASCADE,
    tipo            VARCHAR(30)  NOT NULL
                    CONSTRAINT ck_barrera_tipo CHECK (
                        tipo IN ('TRANSPORTE', 'ECONOMICA', 'OLVIDO', 'TRABAJO_CUIDADOR', 'DISTANCIA_CLIMA',
                                 'EFECTOS_ADVERSOS_SUPLEMENTO', 'RECHAZO_TRATAMIENTO', 'OTRA')),
    detalle         VARCHAR(200),
    fuente          VARCHAR(24)  NOT NULL
                    CONSTRAINT ck_barrera_fuente CHECK (
                        fuente IN ('PERSONAL', 'RESPUESTA_RECORDATORIO', 'INASISTENCIA', 'VISITA')),
    fecha           DATE         NOT NULL,
    recordatorio_id VARCHAR(36)  REFERENCES recordatorio (id) ON DELETE SET NULL,
    registrado_por  VARCHAR(60)  NOT NULL,
    creado_en       TIMESTAMPTZ  NOT NULL,
    CONSTRAINT uq_barrera_nino_tipo_fecha_fuente UNIQUE (nino_id, tipo, fecha, fuente),
    CONSTRAINT ck_barrera_otra_detalle CHECK (tipo <> 'OTRA' OR detalle IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS ix_barrera_nino_id ON barrera (nino_id);
CREATE INDEX IF NOT EXISTS ix_barrera_fecha ON barrera (fecha);

-- Vista de apoyo para el seguimiento (HU-04): último control por niño.
CREATE OR REPLACE VIEW v_ultimo_control AS
SELECT DISTINCT ON (e.nino_id)
       e.nino_id, e.fecha, e.hemoglobina_ajustada, e.clasificacion
FROM evaluacion_hemoglobina e
ORDER BY e.nino_id, e.fecha DESC, e.creado_en DESC;
