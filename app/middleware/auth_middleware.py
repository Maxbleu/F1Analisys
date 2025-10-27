from app.auth import verify_token
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import HTTPAuthorizationCredentials

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticación que verifica el token Bearer
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesa la solicitud y verifica el token de autenticación
        """

        if not request.url.path.__contains__("system"):
            if request.url.path.__contains__("analisys"):
                request.state.authenticated = False
                request.state.is_analisys = True
            return await call_next(request)
        auth_header = request.headers.get("authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token no proporcionado"}
            )
        try:
            scheme, credentials = auth_header.split()
            if scheme.lower() != "bearer":
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Esquema de autenticación inválido"}
                )
            http_credentials = HTTPAuthorizationCredentials(
                scheme=scheme,
                credentials=credentials
            )
            request.state.user = await verify_token(http_credentials)
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Formato de Authorization inválido"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)}
            )
        return await call_next(request)