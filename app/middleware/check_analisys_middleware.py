from fastapi import Request
from app.utils import get_request_data
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils import get_path_temp_plot, exists_plot_in_temp

class CheckAnalisysMiddleware(BaseHTTPMiddleware):
    """
    Middleware que verifica si el analisys existe
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesa la solicitud y verifica si el analisys existe
        """

        type_event, analisys, year, event, session = get_request_data(request=request)
        file_path = get_path_temp_plot(type_event, analisys, year, event, session)
        if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

        return await call_next(request)