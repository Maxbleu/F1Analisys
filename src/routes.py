from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, Response

from analisys._init_ import track_dominance_analisys, top_speed_analisys, lap_time_average_analisys, team_performace_analisys, \
    lap_time_distribution_analisys, fastest_laps_analisys, race_position_evolution_analisys, fastest_drivers_compound_analisys, \
    comparative_lap_time_analisys, braking_analisys, throttle_analisys, long_runs_analisys, optimal_lap_impact_analisys

from utils._init_ import convert_img_to_bytes, save_img, get_info_drivers, get_path_temp_plot, remove_all_temp_plots, exists_plot_in_temp, verify_token

router = APIRouter(prefix="/api")

@router.get("/health", dependencies=[Depends(verify_token)], tags=["System"])
async def health_check():
    return {"status": "ok"}

@router.delete("/temp/remove", dependencies=[Depends(verify_token)], tags=["System"])
async def delete_temp_plots():
    remove_all_temp_plots()
    return Response(content="Deletion complete")

@router.get("/{type_event}/top_speed/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_top_speed(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="top_speed", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    top_speed_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/{type_event}/braking/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_braking(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="braking", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    braking_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/{type_event}/throttle/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_throttle(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="throttle", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    throttle_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/{type_event}/lap_time_average/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_lap_time_average(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="lap_time_average", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    lap_time_average_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/{type_event}/team_performace/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_team_performace(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="team_performace", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    team_performace_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/official/lap_time_distribution/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_lap_time_distribution(
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    type_event = "official"
    file_path = get_path_temp_plot(type_event=type_event, analisis="lap_time_distribution", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    lap_time_distribution_analisys(year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)()
    return return_thing

#   REVISAR EL ERROR VUELTAS RAPIDAS EN AGUA http://localhost:8000/official/fastest_laps/2024/15/FP3
@router.get("/{type_event}/fastest_laps/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_fastest_laps(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="fastest_laps", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    fastest_laps_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/official/race_position_evolution/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_race_position_evolution(
    year: int, 
    event: int, 
    session: str, 
    convert_to_bytes: bool = False
    ):

    type_event = "official"
    file_path = get_path_temp_plot(type_event=type_event, analisis="race_position_evolution", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    race_position_evolution_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/{type_event}/fastest_drivers_compound/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_fastest_drivers_compound(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="fastest_drivers_compound", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    fastest_drivers_compound_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/{type_event}/track_dominance/{year}/{event}/{session}", tags=["Oficial sessions"])
@router.get("/{type_event}/track_dominance/{year}/{event}/{session}/compare/{pilotos_info:path}", tags=["Oficial sessions"])
async def get_track_dominance(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    pilotos_info: str = None,
    convert_to_bytes: bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="track_dominance", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    vueltas_pilotos_dict = get_info_drivers(pilotos_info)
    track_dominance_analisys(type_event, year, event, session, vueltas_pilotos_dict)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/{type_event}/comparative_lap_time/{year}/{event}/{session}", tags=["Oficial sessions"])
@router.get("/{type_event}/comparative_lap_time/{year}/{event}/{session}/compare/{pilotos_info:path}", tags=["Oficial sessions"])
async def get_comparative_lap_time(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    pilotos_info: str = None,
    convert_to_bytes : bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="comparative_lap_time", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    vueltas_pilotos_dict = get_info_drivers(pilotos_info)
    comparative_lap_time_analisys(type_event, year, event, session, vueltas_pilotos_dict)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/{type_event}/long_runs/{year}/{event}/{session}/compare/{pilotos_info:path}", tags=["Oficial sessions"])
async def get_long_runs(
    type_event: str,
    year: int, 
    event: int = None, 
    session: str = None,
    pilotos_info: str = None,
    indexing: str = "index",
    threshold: float = 1.05,
    convert_to_bytes: bool = False
    ):

    file_path = get_path_temp_plot(type_event=type_event, analisis="long_runs", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    vueltas_pilotos_dict = get_info_drivers(pilotos_info)
    long_runs_analisys(type_event, year, event, session, threshold, vueltas_pilotos_dict, indexing)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing

@router.get("/official/optimal_lap_impact/{year}/{event}/{session}", tags=["Oficial sessions"])
async def get_optimal_lap_impact(
    year: int, 
    event: int = None, 
    session: str = None,
    convert_to_bytes: bool = False
    ):

    type_event = "official"
    file_path = get_path_temp_plot(type_event=type_event, analisis="optimal_lap_impact", year=year, round=event, session=session)
    if exists_plot_in_temp(file_path): return RedirectResponse(url=file_path[1:])

    optimal_lap_impact_analisys(type_event, year, event, session)
    return_thing = convert_img_to_bytes() if convert_to_bytes else save_img(file_path)
    return return_thing