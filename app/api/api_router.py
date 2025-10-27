from fastapi import APIRouter, Depends
from .analisys_routes import router as analisys_router
from .system_routes import router as system_router

router = APIRouter()

router.include_router(analisys_router,prefix="/analisys",tags=["Analisys"])
router.include_router(system_router,prefix="/system",tags=["System"])