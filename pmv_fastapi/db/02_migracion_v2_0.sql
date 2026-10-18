-- =====================================================================
-- Migración de una base 1.x (PMV / avance del Incremento 2) a la 2.0.0-inc2 — PostgreSQL 14+
-- Ejecutar una sola vez:  psql -d anemia -f db/02_migracion_v2_0.sql
-- No borra datos: los niños existentes quedan con origen 'SISTEMA'.
-- (Una base nueva se crea directamente con db/01_esquema_postgresql.sql.)
-- =====================================================================

BEGIN;

-- Origen de los datos y metadatos del dataset (ADR-009)
ALTER TABLE nino ADD COLUMN IF NOT EXISTS origen VARCHAR(24) NOT NULL DEFAULT 'SISTEMA';
ALTER TABLE nino ADD COLUMN IF NOT EXISTS codigo_origen VARCHAR(20);
ALTER TABLE nino ADD COLUMN IF NOT EXISTS red VARCHAR(80);
ALTER TABLE nino ADD COLUMN IF NOT EXISTS microred VARCHAR(80);
ALTER TABLE nino ADD COLUMN IF NOT EXISTS provincia VARCHAR(80);

-- Los datos personales dejan de ser obligatorios en general; lo siguen siendo para origen 'SISTEMA'
ALTER TABLE nino ALTER COLUMN dni DROP NOT NULL;
ALTER TABLE nino ALTER COLUMN nombres DROP NOT NULL;
ALTER TABLE nino ALTER COLUMN apellidos DROP NOT NULL;
ALTER TABLE nino ALTER COLUMN sexo DROP NOT NULL;
ALTER TABLE nino ALTER COLUMN tutor_nombre DROP NOT NULL;

ALTER TABLE nino ADD CONSTRAINT ck_nino_origen CHECK (origen IN ('SISTEMA', 'DATASET_DIRESA_JUNIN'));
ALTER TABLE nino ADD CONSTRAINT ck_nino_sistema_completo CHECK (
    origen <> 'SISTEMA' OR (dni IS NOT NULL AND nombres IS NOT NULL AND apellidos IS NOT NULL
                            AND sexo IS NOT NULL AND tutor_nombre IS NOT NULL));
ALTER TABLE nino ADD CONSTRAINT ck_nino_dataset_codigo CHECK (origen <> 'DATASET_DIRESA_JUNIN' OR codigo_origen IS NOT NULL);
ALTER TABLE nino ADD CONSTRAINT uq_nino_codigo_origen UNIQUE (codigo_origen);
CREATE INDEX IF NOT EXISTS ix_nino_origen ON nino (origen);

-- Evaluaciones: peso y talla opcionales (solo las importadas no los traen) y severidad del HIS
ALTER TABLE evaluacion_hemoglobina ALTER COLUMN peso_kg DROP NOT NULL;
ALTER TABLE evaluacion_hemoglobina ALTER COLUMN talla_cm DROP NOT NULL;
ALTER TABLE evaluacion_hemoglobina ADD COLUMN IF NOT EXISTS clasificacion_origen VARCHAR(12);

-- HIST-2.4: asistencia a control (ADR-010)
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

COMMIT;
