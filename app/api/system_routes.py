from fastapi import APIRouter, Response
from app.utils import remove_all_temp_plots

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.delete("/temp/remove")
async def delete_temp_plots():
    remove_all_temp_plots()
    return Response(content="Deletion complete")
