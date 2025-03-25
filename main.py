from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from analisys._init_ import track_dominance_analisys
from analisys._init_ import top_speed_analisys
from analisys._init_ import lap_time_average_analisys
from analisys._init_ import team_performace_analisys
from analisys._init_ import lap_time_distribution_analisys
from analisys._init_ import fastest_laps_analisys
from analisys._init_ import race_position_evolution_analisys
from analisys._init_ import fastest_drivers_compound_analisys
from analisys._init_ import comparative_lap_time_analisys
from analisys._init_ import braking_analisys
from analisys._init_ import throttle_analisys

from utils._init_ import convert_img_to_bytes
from utils._init_ import save_img

app = FastAPI()

app.mount("/temp", StaticFiles(directory="temp"), name="temp")

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/pretest/track_dominance/{year}/{test_number}/{session_number}", tags=["Pretesting sessions"])
@app.get("/official/track_dominance/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_track_dominance(
    year: int, 
    round: int = None,
    session: str = None, 
    test_number: int = None,
    session_number: int = None,
    convert_to_bytes: bool = False
    ):

    track_dominance_analisys(year, round, session, test_number, session_number)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@app.get("/pretest/top_speed/{year}/{test_number}/{session_number}", tags=["Pretesting sessions"])
@app.get("/official/top_speed/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_top_speed(
    year: int, 
    round: int = None, 
    session: str = None,
    test_number: int = None,
    session_number: int = None,
    convert_to_bytes: bool = False
    ):

    top_speed_analisys(year, round, session, test_number, session_number)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@app.get("/pretest/braking/{year}/{test_number}/{session_number}", tags=["Pretesting sessions"])
@app.get("/official/braking/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_braking(
    year: int, 
    round: int = None, 
    session: str = None,
    test_number: int = None,
    session_number: int = None,
    convert_to_bytes: bool = False
    ):

    braking_analisys(year, round, session, test_number, session_number)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@app.get("/pretest/throttle/{year}/{test_number}/{session_number}", tags=["Pretesting sessions"])
@app.get("/official/throttle/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_throttle(
    year: int, 
    round: int = None, 
    session: str = None,
    test_number: int = None,
    session_number: int = None,
    convert_to_bytes: bool = False
    ):

    throttle_analisys(year, round, session, test_number, session_number)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@app.get("/pretest/lap_time_average/{year}/{test_number}/{session_number}", tags=["Pretesting sessions"])
@app.get("/official/lap_time_average/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_lap_time_average(
    year: int, 
    round: int = None, 
    session: str = None,
    test_number: int = None,
    session_number: int = None, 
    convert_to_bytes: bool = False
    ):

    lap_time_average_analisys(year, round, session, test_number, session_number)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@app.get("/pretest/team_performace/{year}/{test_number}/{session_number}", tags=["Pretesting sessions"])
@app.get("/official/team_performace/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_team_performace(
    year: int, 
    round: int = None,
    session: str = None,
    test_number: int = None,
    session_number: int = None, 
    convert_to_bytes: bool = False
    ):

    team_performace_analisys(year, round, session, test_number, session_number)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@app.get("/official/lap_time_distribution/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_lap_time_distribution(
    year: int, 
    round: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    lap_time_distribution_analisys(year, round, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

#   REVISAR EL ERROR VUELTAS RAPIDAS EN AGUA http://localhost:8000/official/fastest_laps/2024/15/FP3
@app.get("/pretest/fastest_laps/{year}/{test_number}/{session_number}", tags=["Pretesting sessions"])
@app.get("/official/fastest_laps/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_fastest_laps(
    year: int, 
    round: int = None, 
    session: str = None,
    test_number: int = None,
    session_number: int = None,
    convert_to_bytes: bool = False
    ):

    fastest_laps_analisys(year, round, session, test_number, session_number)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

#   AÑADIR TABLA DE STINTS EN LA DERECHA O IZQUIERDA DE LA GRAFICA
@app.get("/official/race_position_evolution/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_race_position_evolution(
    year: int, 
    round: int, 
    session: str, 
    convert_to_bytes: bool = False
    ):

    race_position_evolution_analisys(year, round, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@app.get("/pretest/fastest_drivers_compound/{year}/{test_number}/{session_number}", tags=["Pretesting sessions"])
@app.get("/official/fastest_drivers_compound/{year}/{round}/{session}", tags=["Oficial sessions"])
def get_fastest_drivers_compound(
    year: int, 
    round: int = None,
    session: str = None,
    test_number: int = None,
    session_number: int = None,
    convert_to_bytes: bool = False
    ):

    fastest_drivers_compound_analisys(year, round, session, test_number, session_number)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@app.get("/pretest/comparative_lap_time/{year}/{test_number}/{session_number}/compare/{piloto1}/{vuelta_piloto1}/vs/{piloto2}/{vuelta_piloto2}", tags=["Pretesting sessions"])
@app.get("/official/comparative_lap_time/{year}/{round}/{session}/compare/{piloto1}/{vuelta_piloto1}/vs/{piloto2}/{vuelta_piloto2}", tags=["Oficial sessions"])
def get_comparative_lap_time(
    year: int,
    round: int = None,
    session: str = None,
    test_number: int = None,
    session_number: int = None,
    piloto1: str = None,
    vuelta_piloto1: int = None,
    piloto2: str = None,
    vuelta_piloto2: int = None,
    convert_to_bytes : bool = False
    ):

    vueltas_pilotos = {
        piloto1: vuelta_piloto1,
        piloto2: vuelta_piloto2
    }
    comparative_lap_time_analisys(year, round, session, test_number, session_number, vueltas_pilotos)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing