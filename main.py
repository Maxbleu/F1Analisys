import fastf1

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from analisys._init_ import analisys_track_dominance
from analisys._init_ import analisys_top_speed
from analisys._init_ import analisys_lap_time_average

from utils._init_ import convert_img_to_bytes
from enums.process_state import ProcessState

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints:
#   TRACK DOMINANCE ¡OK!
#   TOP SPEED ¡OK!
#   LAP TIME AVERAGE
#   QUALIFYING RESULTS
#   RACE RESULTS
#   RACE PACE
#   TEAM PERFORMANCE

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/analisys/track_dominance/{year}/{round}/{session}", tags=["Análisis"])
def get_track_dominance(year: int, round: int, session: str):

    result = analisys_track_dominance(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )

    img_base64 = convert_img_to_bytes()
    return {"image": f"data:image/png;base64,{img_base64}"}

@app.get("/analisys/top_speed/{year}/{round}/{session}", tags=["Análisis"])
def get_top_speed(year: int, round: int, session: str):

    result = analisys_top_speed(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )

    img_base64 = convert_img_to_bytes()
    return {"image": f"data:image/png;base64,{img_base64}"}

@app.get("/analisys/lap_time_average/{year}/{round}/{session}", tags=["Análisis"])
def get_lap_time_average(year: int, round: int, session: str):

    result = analisys_lap_time_average(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )

    img_base64 = convert_img_to_bytes()
    return {"image": f"data:image/png;base64,{img_base64}"}