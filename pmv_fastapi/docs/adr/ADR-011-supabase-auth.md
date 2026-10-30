# ADR-011: Supabase Auth y sesiones en el servidor

- Fecha: 2026-10-23
- Estado: implementado localmente; primer acceso remoto pendiente de crear una cuenta autorizada.

## Contexto

El selector `X-Usuario` del prototipo identifica registros de prueba, pero no autentica. El usuario solicita empezar la migración a Supabase por el login, manteniendo la persistencia actual durante esta primera etapa.

## Decisión

Autenticación con correo y contraseña mediante la API de Supabase Auth desde el servidor. El adaptador de salida implementa `ProveedorIdentidad`; `ServicioSesion` implementa el puerto de entrada `GestionarSesiones`. El adaptador HTTP traduce las sesiones a cookies y protege las rutas clínicas de `/api/`, incluidos reportes CSV. El dominio permanece independiente de FastAPI, HTTPX y Supabase.

Los tokens se almacenan en cookies HttpOnly, SameSite=Strict y Secure por defecto, con ruta `/api`. El navegador no recibe tokens en JSON ni los guarda en localStorage. `/api/auth/session` recupera la identidad o renueva la sesión; el cliente serializa las renovaciones dentro de la pestaña y reintenta una petición tras un 401. No se confía en decodificar un JWT sin verificar: se consulta `/auth/v1/user`. Las mutaciones exigen `X-CSRF-Protection: 1` y rechazan un Origin ajeno. No se habilita CORS entre orígenes.

La auditoría utiliza el UUID de Supabase; se ignora `X-Usuario` en modo autenticado. El selector queda disponible únicamente con `AUTH_MODE=demo`, que debe activarse explícitamente para las demostraciones sintéticas y las pruebas históricas. Sin configuración, el modo predeterminado es Supabase y el acceso clínico permanece bloqueado.

No se permite autorregistro desde la interfaz. El administrador debe desactivar las nuevas inscripciones públicas en Supabase y provisionar usuarios confirmados desde el panel. En esta fase todos los usuarios confirmados del proyecto tienen acceso a todas las funciones; los roles y el aislamiento por establecimiento quedan pendientes.

## Consecuencias

- No requiere `service_role`, secreto JWT ni contraseña de PostgreSQL para autenticar.
- La configuración `.env` se carga con `uvicorn --env-file .env`; permanece ignorada por Git.
- En desarrollo HTTP local se usa `AUTH_COOKIE_SECURE=false`; en despliegue HTTPS debe ser `true`.
- Verificar la identidad exige conexión al proveedor y añade una llamada externa por petición clínica. Una indisponibilidad responde 503; nunca permite acceso anónimo.
- El cierre revoca la sesión local en Supabase cuando está disponible y borra las cookies incluso si el proveedor falla. Un access token ya emitido puede seguir válido hasta su expiración según Supabase; no se promete revocación instantánea de copias externas.
- Las renovaciones simultáneas entre distintas pestañas dependen de la ventana de reutilización de refresh tokens de Supabase. No se modifica su configuración.
- Los borradores clínicos en localStorage se limitan a la demo; al entrar en modo autenticado se elimina el borrador anterior.
- Esta decisión no migra las tablas ni implementa RLS. La próxima etapa deberá diseñar autorización por establecimiento y acceso de PostgreSQL antes de exponer datos clínicos reales.

## Fuentes

- [Password-based Auth](https://supabase.com/docs/guides/auth/passwords)
- [User sessions](https://supabase.com/docs/guides/auth/sessions)
- [API keys](https://supabase.com/docs/guides/getting-started/api-keys)
- [Contrato oficial de Supabase Auth](https://github.com/supabase/auth/blob/master/openapi.yaml)
