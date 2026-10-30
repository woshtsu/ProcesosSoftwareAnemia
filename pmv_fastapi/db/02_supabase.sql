-- Ejecutar DESPUÉS de 01_esquema_postgresql.sql (o de la migración correspondiente) en el SQL Editor de Supabase.
-- La aplicación accede mediante PostgreSQL desde el backend, no por Data API.
BEGIN;
ALTER TABLE public.nino ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evaluacion_hemoglobina ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.asistencia_control ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.visita_domiciliaria ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.operacion_sincronizada ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conflicto_sincronizacion ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recordatorio ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.barrera ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.nino, public.evaluacion_hemoglobina,
    public.asistencia_control, public.visita_domiciliaria, public.operacion_sincronizada,
    public.conflicto_sincronizacion, public.recordatorio, public.barrera, public.v_ultimo_control
    FROM anon, authenticated;
COMMIT;
-- No se crean políticas públicas. La conexión inicial del backend usa postgres.
-- Esto protege Data API, no sustituye autenticación en la API FastAPI.
