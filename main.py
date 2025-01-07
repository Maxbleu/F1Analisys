from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from analisys._init_ import analisys_track_dominance

from utils._init_ import convert_img_to_bytes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/analisys/track_dominance/{year}/{round}/{session}")
def get_track_dominance(year: int, round: int, session: str):

    analisys_track_dominance(year, round, session)
    img_base64 = convert_img_to_bytes()
    return {"image": f"data:image/png;base64,{img_base64}"}



"""if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)"""