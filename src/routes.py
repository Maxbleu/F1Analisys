from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from analisys._init_ import track_dominance_analisys, top_speed_analisys, lap_time_average_analisys, team_performace_analisys, \
    lap_time_distribution_analisys, fastest_laps_analisys, race_position_evolution_analisys, fastest_drivers_compound_analisys, \
    comparative_lap_time_analisys, braking_analisys, throttle_analisys, long_runs_analisys, optimal_lap_impact_analisys

from utils._init_ import convert_img_to_bytes, save_img, get_info_drivers

router = APIRouter(prefix="/api")

@router.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@router.get("/{type_event}/top_speed/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_top_speed(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    top_speed_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/{type_event}/braking/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_braking(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    braking_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/{type_event}/throttle/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_throttle(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    throttle_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/{type_event}/lap_time_average/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_lap_time_average(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    lap_time_average_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/{type_event}/team_performace/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_team_performace(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    team_performace_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/official/lap_time_distribution/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_lap_time_distribution(
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    lap_time_distribution_analisys(year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

#   REVISAR EL ERROR VUELTAS RAPIDAS EN AGUA http://localhost:8000/official/fastest_laps/2024/15/FP3
@router.get("/{type_event}/fastest_laps/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_fastest_laps(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    fastest_laps_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/official/race_position_evolution/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_race_position_evolution(
    year: int, 
    event: int, 
    session: str, 
    convert_to_bytes: bool = False
    ):

    type_event = "official"
    race_position_evolution_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/{type_event}/fastest_drivers_compound/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_fastest_drivers_compound(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    fastest_drivers_compound_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/{type_event}/track_dominance/{year}/{event}/{session}", tags=["Oficial sessions"])
@router.get("/{type_event}/track_dominance/{year}/{event}/{session}/compare/{pilotos_info:path}", tags=["Oficial sessions"])
def get_track_dominance(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    pilotos_info: str = None,
    convert_to_bytes: bool = False
    ):

    vueltas_pilotos_dict = get_info_drivers(pilotos_info)
    track_dominance_analisys(type_event, year, event, session, vueltas_pilotos_dict)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/{type_event}/comparative_lap_time/{year}/{event}/{session}", tags=["Oficial sessions"])
@router.get("/{type_event}/comparative_lap_time/{year}/{event}/{session}/compare/{pilotos_info:path}", tags=["Oficial sessions"])
def get_comparative_lap_time(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    pilotos_info: str = None,
    convert_to_bytes : bool = False
    ):

    vueltas_pilotos_dict = get_info_drivers(pilotos_info)
    comparative_lap_time_analisys(type_event, year, event, session, vueltas_pilotos_dict)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/{type_event}/long_runs/{year}/{event}/{session}/compare/{pilotos_info:path}", tags=["Oficial sessions"])
def get_long_runs(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    pilotos_info: str = None,
    indexing: str = "index",
    threshold: float = 1.05,
    convert_to_bytes: bool = False
    ):

    vueltas_pilotos_dict = get_info_drivers(pilotos_info)
    long_runs_analisys(type_event, year, event, session, threshold, vueltas_pilotos_dict, indexing)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing

@router.get("/official/optimal_lap_impact/{year}/{event}/{session}", tags=["Oficial sessions"])
def get_optimal_lap_impact(
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    optimal_lap_impact_analisys("official", year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img()
    return return_thing