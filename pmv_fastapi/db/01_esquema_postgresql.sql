-- =====================================================================
-- Esquema de datos — PostgreSQL 14+ (versión 2.0.0-inc2)
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
-- Para actualizar una base 1.x existente use db/02_migracion_v2_0.sql.
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

-- Vista de apoyo para el seguimiento (HU-04): último control por niño.
CREATE OR REPLACE VIEW v_ultimo_control AS
SELECT DISTINCT ON (e.nino_id)
       e.nino_id, e.fecha, e.hemoglobina_ajustada, e.clasificacion
FROM evaluacion_hemoglobina e
ORDER BY e.nino_id, e.fecha DESC, e.creado_en DESC;
