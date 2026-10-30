-- =====================================================================
-- Migración de la 3.0.0-inc3 a la 4.0.0-inc4 — PostgreSQL 14+
-- Ejecutar una sola vez:  psql -d anemia -f db/04_migracion_v4_0.sql
-- Solo agrega tablas (no toca datos existentes): recordatorios de control por mensajería y respuesta del tutor
-- (HIST-4.1 y HIST-4.2) y barreras de acceso al tratamiento (HIST-4.3 y HIST-4.4), ADR-014.
-- Es repetible: usa IF NOT EXISTS. Una base nueva se crea directamente con db/01_esquema_postgresql.sql.
-- En Supabase, ejecutar después db/02_supabase.sql (activa RLS y revoca el acceso de la Data API a las tablas nuevas).
-- =====================================================================

BEGIN;

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

COMMIT;
