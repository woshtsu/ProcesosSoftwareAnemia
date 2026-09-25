-- Migración 001: esquema inicial — PMV Anemia Junín
-- Ejecutar mediante migraciones.py; nunca a mano.
-- WAL, FK y wait timeout se configuran en la conexión.

-- Control de versiones de migraciones
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    aplicada_en TEXT    NOT NULL,   -- timestamp UTC ISO 8601
    descripcion TEXT    NOT NULL
);

-- Niños en seguimiento
CREATE TABLE IF NOT EXISTS ninos (
    id              TEXT    PRIMARY KEY,   -- UUID
    dni             TEXT    NOT NULL UNIQUE,
    nombres         TEXT    NOT NULL,
    apellidos       TEXT    NOT NULL,
    fecha_nacimiento TEXT   NOT NULL,      -- YYYY-MM-DD
    sexo            TEXT    NOT NULL CHECK (sexo IN ('F','M')),
    tipo_nacimiento TEXT    NOT NULL CHECK (tipo_nacimiento IN ('TERMINO','PREMATURO')),
    peso_g          INTEGER NOT NULL,      -- gramos
    distrito        TEXT    NOT NULL,
    altitud_msnm    INTEGER NOT NULL,
    cuidador        TEXT    NOT NULL,
    telefono        TEXT,                  -- NULL o 9 dígitos
    created_at      TEXT    NOT NULL,      -- UTC ISO 8601
    updated_at      TEXT    NOT NULL       -- UTC ISO 8601
);

CREATE INDEX IF NOT EXISTS idx_ninos_dni       ON ninos (dni);
CREATE INDEX IF NOT EXISTS idx_ninos_distrito  ON ninos (distrito);

-- Dosajes de hemoglobina (registro histórico inmutable)
CREATE TABLE IF NOT EXISTS dosajes (
    id                 TEXT    PRIMARY KEY,
    nino_id            TEXT    NOT NULL REFERENCES ninos(id),
    fecha_dosaje       TEXT    NOT NULL,    -- YYYY-MM-DD (fecha clínica)
    hb_observada_ddl   INTEGER NOT NULL,   -- décimas de g/dL
    altitud_msnm       INTEGER NOT NULL,
    ajuste_ddl         INTEGER NOT NULL,
    hb_ajustada_ddl    INTEGER NOT NULL,
    edad_meses         INTEGER NOT NULL,
    clasificacion      TEXT    NOT NULL,
    version_normativa  TEXT    NOT NULL,
    advertencias_json  TEXT    NOT NULL DEFAULT '[]',  -- JSON array
    created_at         TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_dosajes_nino_fecha
    ON dosajes (nino_id, fecha_dosaje, created_at);

-- Intentos de registro (auditoría; sin PII rechazada)
CREATE TABLE IF NOT EXISTS intentos_registro (
    id              TEXT    PRIMARY KEY,
    momento         TEXT    NOT NULL,      -- UTC ISO 8601
    operacion       TEXT    NOT NULL,      -- "CREAR_NINO"
    resultado       TEXT    NOT NULL CHECK (resultado IN ('ACEPTADO','RECHAZADO')),
    codigos_error   TEXT    NOT NULL DEFAULT '[]'  -- JSON array
);

CREATE INDEX IF NOT EXISTS idx_intentos_momento ON intentos_registro (momento);

-- Marcar esta migración como aplicada
INSERT OR IGNORE INTO schema_version (version, aplicada_en, descripcion)
VALUES (1, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), 'Esquema inicial: ninos, dosajes, intentos_registro');
