from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from analisys._init_ import analisys_track_dominance
from analisys._init_ import analisys_top_speed
from analisys._init_ import analisys_lap_time_average
from analisys._init_ import analisys_team_performace
from analisys._init_ import analisys_race_pace
from analisys._init_ import analisys_fastest_laps
from analisys._init_ import analisys_race_position_evolution
from analisys._init_ import analisys_fastest_drivers_compound

from utils._init_ import convert_img_to_bytes
from utils._init_ import save_img

from enums.process_state import ProcessState

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/temp", StaticFiles(directory="temp"), name="temp")

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/analisys/track_dominance/{year}/{round}/{session}", tags=["Análisis sesiones"])
def get_track_dominance(year: int, round: int, session: str, convert_img: bool = True):

    result = analisys_track_dominance(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )

    return_thing = convert_img_to_bytes() if convert_img else save_img()
    return return_thing

@app.get("/analisys/top_speed/{year}/{round}/{session}", tags=["Análisis sesiones"])
def get_top_speed(year: int, round: int, session: str, convert_img: bool = True):

    result = analisys_top_speed(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )

    return_thing = convert_img_to_bytes() if convert_img else save_img()
    return return_thing

@app.get("/analisys/lap_time_average/{year}/{round}/{session}", tags=["Análisis sesiones"])
def get_lap_time_average(year: int, round: int, session: str, convert_img: bool = True):

    result = analisys_lap_time_average(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )

    return_thing = convert_img_to_bytes() if convert_img else save_img()
    return return_thing

@app.get("/analisys/team_performace/{year}/{round}/{session}", tags=["Análisis sesiones"])
def get_team_performace(year: int, round: int, session: str, convert_img: bool = True):

    result = analisys_team_performace(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )

    return_thing = convert_img_to_bytes() if convert_img else save_img()
    return return_thing

@app.get("/analisys/race_pace/{year}/{round}/{session}", tags=["Análisis sesiones"])
def get_race_pace(year: int, round: int, session: str, convert_img: bool = True):

    result = analisys_race_pace(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )
    return_thing = convert_img_to_bytes() if convert_img else save_img()
    return return_thing

#   REVISAR EL ERROR VUELTAS RAPIDAS EN AGUA http://localhost:8000/analisys/fastest_laps/2024/15/FP3
@app.get("/analisys/fastest_laps/{year}/{round}/{session}", tags=["Análisis sesiones"])
def get_fastest_laps(year: int, round: int, session: str, convert_img: bool = True):

    result = analisys_fastest_laps(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )
    return_thing = convert_img_to_bytes() if convert_img else save_img()
    return return_thing

#   AÑADIR TABLA DE STINTS EN LA DERECHA O IZQUIERDA DE LA GRAFICA
@app.get("/analisys/race_position_evolution/{year}/{round}/{session}", tags=["Análisis sesiones"])
def get_race_position_evolution(year: int, round: int, session: str, convert_img: bool = True):

    result = analisys_race_position_evolution(year, round, session)
    if result == ProcessState.FAILED.name or result == ProcessState.CANCELED.name:

        if result == ProcessState.FAILED.name: message = "La sesión de carrera no existe. Asegúrate de que el año, la ronda sean correctos."
        if result == ProcessState.CANCELED.name: message = "La sesión solicitada no es una carrera. Asegúrate de que seleccionaste una sesión de carrera."

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": message,
            }
        )

    return_thing = convert_img_to_bytes() if convert_img else save_img()
    return return_thing

@app.get("/analisys/fastest_drivers_compound/{year}/{round}/{session}", tags=["Análisis sesiones"])
def get_fastest_drivers_compound(year: int, round: int, session: str, convert_img: bool = True):

    result = analisys_fastest_drivers_compound(year, round, session)
    if result == ProcessState.FAILED.name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Sesión no encontrada.",
                "message": "La sesión solicitada no existe. Asegúrate de que el año, la ronda y la sesión sean correctos.",
            }
        )
    return_thing = convert_img_to_bytes() if convert_img else save_img()
    return return_thing
