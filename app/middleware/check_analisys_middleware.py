from fastapi import Request
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils import get_request_data, get_path_temp_plot, exists_plot_in_temp
import os
import logging

logger = logging.getLogger(__name__)

class CheckAnalisysMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(("/temp", "/docs", "/openapi.json", "/redoc")):
            return await call_next(request)
        if not request.url.path.startswith("/api/analisys/"):
            return await call_next(request)
        try:
            type_event, analisys, year, event, session = get_request_data(request=request)
            file_path = get_path_temp_plot(type_event, analisys, year, event, session)
            if exists_plot_in_temp(file_path):
                logger.info(f"Devolviendo archivo cacheado: {file_path}")
                return FileResponse(file_path, media_type="image/png")
        except Exception as e:
            logger.error(f"Error en CheckAnalisysMiddleware: {e}", exc_info=True)
            pass
        return await call_next(request)