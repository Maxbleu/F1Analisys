import threading
from fastapi import APIRouter, Request
from app.analisys import track_dominance_analisys, top_speed_analisys, lap_time_average_analisys, team_performace_analisys, \
    lap_time_distribution_analisys, fastest_laps_analisys, race_position_evolution_analisys, fastest_drivers_compound_analisys, \
    comparative_lap_time_analisys, braking_analisys, throttle_analisys, long_runs_analisys, optimal_lap_impact_analisys
from app.utils import get_info_drivers, get_return

router = APIRouter()

# Serializa el acceso al estado global de matplotlib pyplot para evitar data leaks
_pyplot_lock = threading.Lock()

@router.get("/{type_event}/top_speed/{year}/{event}/{session}")
def get_top_speed(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    with _pyplot_lock:
        top_speed_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/{type_event}/braking/{year}/{event}/{session}")
def get_braking(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    with _pyplot_lock:
        braking_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/{type_event}/throttle/{year}/{event}/{session}")
def get_throttle(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    with _pyplot_lock:
        throttle_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/{type_event}/lap_time_average/{year}/{event}/{session}")
def get_lap_time_average(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    with _pyplot_lock:
        lap_time_average_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/{type_event}/team_performace/{year}/{event}/{session}")
def get_team_performace(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    with _pyplot_lock:
        team_performace_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/official/lap_time_distribution/{year}/{event}/{session}")
def get_lap_time_distribution(
    request: Request,
    year: int,
    event: int = None,
    session: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    type_event = "official"
    with _pyplot_lock:
        lap_time_distribution_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

#   REVISAR EL ERROR VUELTAS RAPIDAS EN AGUA http://localhost:8000/official/fastest_laps/2024/15/FP3
@router.get("/{type_event}/fastest_laps/{year}/{event}/{session}")
def get_fastest_laps(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    with _pyplot_lock:
        fastest_laps_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/official/race_position_evolution/{year}/{event}/{session}")
def get_race_position_evolution(
    request: Request,
    year: int,
    event: int,
    session: str,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    type_event = "official"
    with _pyplot_lock:
        race_position_evolution_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/{type_event}/fastest_drivers_compound/{year}/{event}/{session}")
def get_fastest_drivers_compound(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    with _pyplot_lock:
        fastest_drivers_compound_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/{type_event}/track_dominance/{year}/{event}/{session}")
@router.get("/{type_event}/track_dominance/{year}/{event}/{session}/compare/{pilotos_info:path}")
def get_track_dominance(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    pilotos_info: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    vueltas_pilotos_dict = get_info_drivers(pilotos_info)
    with _pyplot_lock:
        track_dominance_analisys(type_event, year, event, session, vueltas_pilotos_dict)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/{type_event}/comparative_lap_time/{year}/{event}/{session}")
@router.get("/{type_event}/comparative_lap_time/{year}/{event}/{session}/compare/{pilotos_info:path}")
def get_comparative_lap_time(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    pilotos_info: str = None,
    convert_to_bytes : bool = False,
    get_url: bool = False
    ):

    vueltas_pilotos_dict = get_info_drivers(pilotos_info)
    with _pyplot_lock:
        comparative_lap_time_analisys(type_event, year, event, session, vueltas_pilotos_dict)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/{type_event}/long_runs/{year}/{event}/{session}/compare/{pilotos_info:path}")
def get_long_runs(
    request: Request,
    type_event: str,
    year: int,
    event: int = None,
    session: str = None,
    pilotos_info: str = None,
    indexing: str = "index",
    threshold: float = 1.05,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    vueltas_pilotos_dict = get_info_drivers(pilotos_info)
    with _pyplot_lock:
        long_runs_analisys(type_event, year, event, session, threshold, vueltas_pilotos_dict, indexing)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing

@router.get("/official/optimal_lap_impact/{year}/{event}/{session}")
def get_optimal_lap_impact(
    request: Request,
    year: int,
    event: int = None,
    session: str = None,
    convert_to_bytes: bool = False,
    get_url: bool = False
    ):

    type_event = "official"
    with _pyplot_lock:
        optimal_lap_impact_analisys(type_event, year, event, session)
        return_thing = get_return(request,convert_to_bytes,get_url)
        return return_thing
