"""Cliente servidor de la API de Supabase Auth. Nunca utiliza service_role."""

from urllib.parse import urlsplit

import httpx

from app.domain.model.autenticacion import AutenticacionNoDisponible, Sesion, SesionInvalida, UsuarioAutenticado
from app.ports.outbound.proveedor_identidad import ProveedorIdentidad


class SupabaseAuth(ProveedorIdentidad):
    def __init__(self, url: str, public_key: str, transport=None):
        self.url = url.rstrip("/")
        self.public_key = public_key
        self.transport = transport
        parsed = urlsplit(self.url)
        self.configurado = bool(
            parsed.scheme == "https"
            and parsed.hostname
            and not parsed.username
            and not parsed.password
            and not parsed.query
            and not parsed.fragment
            and public_key
        )
        self._client: httpx.AsyncClient | None = None

    def _obtener_cliente(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10, transport=self.transport)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    async def _peticion(self, method: str, path: str, token: str = "", **kwargs):
        if not self.configurado:
            raise AutenticacionNoDisponible
        headers = {"apikey": self.public_key}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            client = self._obtener_cliente()
            response = await client.request(method, f"{self.url}/auth/v1/{path}", headers=headers, **kwargs)
            if response.status_code in (400, 401, 403, 422):
                raise SesionInvalida
            if not response.is_success:
                raise AutenticacionNoDisponible
            return response.json() if response.content else {}
        except (httpx.HTTPError, ValueError) as exc:
            raise AutenticacionNoDisponible from exc

    @staticmethod
    def _usuario(data) -> UsuarioAutenticado:
        if not isinstance(data, dict) or not data.get("id") or not data.get("email"):
            raise SesionInvalida
        if not data.get("email_confirmed_at") or data.get("is_anonymous"):
            raise SesionInvalida
        return UsuarioAutenticado(str(data["id"]), str(data["email"]))

    def _sesion(self, data) -> Sesion:
        try:
            usuario = self._usuario(data["user"])
            access, refresh = data["access_token"], data["refresh_token"]
            duration = int(data["expires_in"])
            if (
                not isinstance(access, str)
                or not access
                or not isinstance(refresh, str)
                or not refresh
                or duration <= 0
            ):
                raise ValueError
            return Sesion(usuario, access, refresh, duration)
        except (KeyError, TypeError, ValueError) as exc:
            raise AutenticacionNoDisponible from exc

    async def iniciar(self, email: str, password: str) -> Sesion:
        data = await self._peticion(
            "POST", "token", params={"grant_type": "password"}, json={"email": email, "password": password}
        )
        return self._sesion(data)

    async def renovar(self, refresh_token: str) -> Sesion:
        data = await self._peticion(
            "POST", "token", params={"grant_type": "refresh_token"}, json={"refresh_token": refresh_token}
        )
        return self._sesion(data)

    async def usuario(self, access_token: str) -> UsuarioAutenticado:
        return self._usuario(await self._peticion("GET", "user", token=access_token))

    async def salir(self, access_token: str) -> None:
        await self._peticion("POST", "logout", token=access_token, params={"scope": "local"})
