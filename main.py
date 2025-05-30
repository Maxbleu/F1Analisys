from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routes import router

app = FastAPI(title="F1Analisys API Server")
app.mount("/temp", StaticFiles(directory="temp"), name="temp")
app.include_router(router)