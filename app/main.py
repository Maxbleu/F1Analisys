import os, uvicorn
from .api import router
from fastapi import FastAPI
from dotenv import load_dotenv
from .middleware import AuthMiddleware, CheckAnalisysMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

load_dotenv(os.getenv("ENV_FILE", ".env"))
app = FastAPI(title="F1Analisys API Server")

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.include_router(router,prefix="/api")
app.mount("/temp", StaticFiles(directory=os.environ["TEMP_PATH_DIRECTORY"]), name="temp")

app.add_middleware(CheckAnalisysMiddleware)
app.add_middleware(AuthMiddleware)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)