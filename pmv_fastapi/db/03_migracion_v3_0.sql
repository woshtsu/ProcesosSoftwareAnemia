-- =====================================================================
-- Migración de la 2.0.0-inc2 a la 3.0.0-inc3 — PostgreSQL 14+
-- Ejecutar una sola vez:  psql -d anemia -f db/03_migracion_v3_0.sql
-- Solo agrega tablas (no toca datos existentes): visitas domiciliarias (VIS-3.5, ADR-013), bitácora de operaciones
-- sincronizadas (HIST-3.2) y conflictos de sincronización (HIST-3.3), ADR-012.
-- Es repetible: usa IF NOT EXISTS. Una base nueva se crea directamente con db/01_esquema_postgresql.sql.
-- En Supabase, ejecutar después db/02_supabase.sql (activa RLS y revoca el acceso de la Data API a las tablas nuevas).
-- =====================================================================

BEGIN;

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

COMMIT;
