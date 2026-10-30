"""Login y cookies de sesión; protección HTTP de los casos de uso clínicos."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, SecretStr

from app.domain.model.autenticacion import AutenticacionNoDisponible, Sesion, SesionInvalida
from app.ports.inbound.sesiones import GestionarSesiones

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])
ACCESS = "aj_access"
REFRESH = "aj_refresh"
PUBLICAS = {"/api/salud", "/api/auth/config", "/api/auth/login", "/api/auth/session", "/api/auth/logout"}


def sesiones_uc(request: Request) -> GestionarSesiones:
    return request.app.state.sesiones


class LoginEntrada(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: SecretStr = Field(min_length=1, max_length=1024)


def error(status: int, mensaje: str) -> JSONResponse:
    return JSONResponse(
        {"errores": [{"campo": "sesion", "mensaje": mensaje}]},
        status_code=status,
        headers={"Cache-Control": "no-store"},
    )


def borrar_cookies(response: Response, secure: bool):
    for name in (ACCESS, REFRESH):
        response.delete_cookie(name, path="/api", httponly=True, secure=secure, samesite="strict")


def guardar_cookies(response: Response, sesion: Sesion, secure: bool):
    for name, value, age in (
        (ACCESS, sesion.access_token, sesion.expires_in),
        (REFRESH, sesion.refresh_token, 60 * 60 * 24 * 7),
    ):
        response.set_cookie(name, value, max_age=age, path="/api", httponly=True, secure=secure, samesite="strict")
    response.headers["Cache-Control"] = "no-store"


def registrar_seguridad(app):
    @app.middleware("http")
    async def seguridad(request: Request, call_next):
        path = request.url.path.rstrip("/")
        if app.state.auth_mode == "supabase" and path.startswith("/api/"):
            # El encabezado personalizado exige una petición del mismo origen en navegadores.
            if request.method not in {"GET", "HEAD", "OPTIONS"}:
                origin = request.headers.get("origin")
                esperado = str(request.base_url).rstrip("/")
                if request.headers.get("X-CSRF-Protection") != "1" or (origin and origin != esperado):
                    return error(403, "Solicitud no permitida. Recargue la página e inténtelo de nuevo.")
            if path not in PUBLICAS:
                access = request.cookies.get(ACCESS)
                if not access:
                    return error(401, "Inicie sesión para continuar.")
                try:
                    request.state.usuario = await app.state.sesiones.usuario(access)
                except SesionInvalida:
                    return error(401, "Su sesión venció. Inicie sesión nuevamente.")
                except AutenticacionNoDisponible:
                    return error(503, "No se pudo verificar la sesión. Inténtelo nuevamente.")
        response = await call_next(request)
        if path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response


@router.get("/config")
def configuracion(request: Request):
    return {"modo": request.app.state.auth_mode, "configurado": request.app.state.auth_configurado}


@router.post("/login")
async def login(
    datos: LoginEntrada, request: Request, response: Response, sesiones: GestionarSesiones = Depends(sesiones_uc)
):
    if request.app.state.auth_mode == "demo":
        raise HTTPException(409, "El modo demo no utiliza credenciales.")
    try:
        sesion = await sesiones.iniciar(datos.email, datos.password.get_secret_value())
    except SesionInvalida:
        return error(401, "Correo o contraseña incorrectos, o correo sin confirmar.")
    except AutenticacionNoDisponible:
        return error(503, "El inicio de sesión no está disponible. Revise la configuración o intente más tarde.")
    guardar_cookies(response, sesion, request.app.state.cookie_secure)
    return {"usuario": asdict(sesion.usuario)}


@router.get("/session")
async def session(request: Request, response: Response, sesiones: GestionarSesiones = Depends(sesiones_uc)):
    if request.app.state.auth_mode == "demo":
        return {"modo": "demo", "usuario": None}
    try:
        access = request.cookies.get(ACCESS)
        if access:
            try:
                return {"usuario": asdict(await sesiones.usuario(access))}
            except SesionInvalida:
                pass
        refresh = request.cookies.get(REFRESH)
        if not refresh:
            raise SesionInvalida
        sesion = await sesiones.renovar(refresh)
        guardar_cookies(response, sesion, request.app.state.cookie_secure)
        return {"usuario": asdict(sesion.usuario)}
    except SesionInvalida:
        result = error(401, "Inicie sesión para continuar.")
        borrar_cookies(result, request.app.state.cookie_secure)
        return result
    except AutenticacionNoDisponible:
        return error(503, "No se pudo recuperar la sesión. Inténtelo nuevamente.")


@router.post("/logout")
async def logout(request: Request, sesiones: GestionarSesiones = Depends(sesiones_uc)):
    result = JSONResponse({"mensaje": "Sesión cerrada."}, headers={"Cache-Control": "no-store"})
    access = request.cookies.get(ACCESS)
    if access and request.app.state.auth_mode != "demo":
        try:
            await sesiones.salir(access)
        except SesionInvalida:
            pass
        except AutenticacionNoDisponible:
            result = error(503, "Sesión local cerrada. No se pudo confirmar el cierre en Supabase.")
    borrar_cookies(result, request.app.state.cookie_secure)
    return result
