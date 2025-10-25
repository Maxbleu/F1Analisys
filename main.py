from fastapi import FastAPI
from src.routes import router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI(title="F1Analisys API Server")
app.mount("/temp", StaticFiles(directory="temp"), name="temp")
app.include_router(router)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")