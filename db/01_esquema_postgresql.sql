-- =====================================================================
-- Esquema de datos del PMV (Incremento 1) — PostgreSQL 14+
-- Sistema de Detección Temprana de Anemia Infantil — Junín
-- Las restricciones CHECK repiten las reglas de plausibilidad del dominio
-- (defensa en profundidad: la base rechaza datos imposibles aunque se
-- carguen fuera de la API).
-- =====================================================================

CREATE TABLE IF NOT EXISTS nino (
    id               VARCHAR(36)  PRIMARY KEY,
    dni              VARCHAR(8)   NOT NULL UNIQUE CHECK (dni ~ '^[0-9]{8}$'),
    nombres          VARCHAR(80)  NOT NULL,
    apellidos        VARCHAR(80)  NOT NULL,
    sexo             VARCHAR(1)   NOT NULL CHECK (sexo IN ('F', 'M')),
    fecha_nacimiento DATE         NOT NULL,
    establecimiento  VARCHAR(120) NOT NULL,
    distrito         VARCHAR(80)  NOT NULL,
    comunidad        VARCHAR(80)  NOT NULL,
    altitud_m        DOUBLE PRECISION NOT NULL CHECK (altitud_m BETWEEN 0 AND 5000),
    tutor_nombre     VARCHAR(120) NOT NULL,
    tutor_celular    VARCHAR(9)   CHECK (tutor_celular IS NULL OR tutor_celular ~ '^9[0-9]{8}$'),
    estado           VARCHAR(10)  NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'ALTA')),
    registrado_por   VARCHAR(60)  NOT NULL,
    creado_en        TIMESTAMPTZ  NOT NULL,
    actualizado_en   TIMESTAMPTZ  NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_nino_comunidad ON nino (comunidad);
CREATE INDEX IF NOT EXISTS ix_nino_estado    ON nino (estado);

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
    peso_kg               DOUBLE PRECISION NOT NULL CHECK (peso_kg BETWEEN 1.5 AND 30),
    talla_cm              DOUBLE PRECISION NOT NULL CHECK (talla_cm BETWEEN 40 AND 125),
    registrado_por        VARCHAR(60) NOT NULL,
    creado_en             TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_eval_nino  ON evaluacion_hemoglobina (nino_id);
CREATE INDEX IF NOT EXISTS ix_eval_fecha ON evaluacion_hemoglobina (fecha);

-- Vista de apoyo para el seguimiento (HU-04): último control por niño.
CREATE OR REPLACE VIEW v_ultimo_control AS
SELECT DISTINCT ON (e.nino_id)
       e.nino_id, e.fecha, e.hemoglobina_ajustada, e.clasificacion
FROM evaluacion_hemoglobina e
ORDER BY e.nino_id, e.fecha DESC, e.creado_en DESC;
