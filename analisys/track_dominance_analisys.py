import numpy as np
import pandas as pd
import fastf1

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
from matplotlib.collections import LineCollection

from collections import Counter

from utils._init_ import get_session, try_get_session_laps, send_error_message, get_team_colors

def track_dominance_analisys(year: int, round: int, session: str, test_number: int, session_number: int, vueltas_pilotos_dict: dict):
    """
    Analyzes the track dominance of the top 3 drivers in a specific session.
    
    Parameters:
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    test_number (int): The test number of the session.
    session_number (int): The session number of the session.
    vueltas_pilotos (dict): A dictionary with the laps of each driver.
    """
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme='fastf1')

    session = get_session(year, round, session, test_number, session_number)
    laps = try_get_session_laps(session)
    laps["LapTime"] = pd.to_timedelta(laps["LapTime"])

    vueltas_pilotos = dict()
    if len(vueltas_pilotos_dict) == 0:
        df_three_best_race_laps = laps.sort_values(by="LapTime").drop_duplicates(subset="Driver").reset_index(drop=True).head(3)
        for i, piloto in enumerate(df_three_best_race_laps["Driver"]):
            df_telemetria = df_three_best_race_laps.iloc[i].get_telemetry().reset_index(drop=True)
            df_telemetria = df_telemetria.assign(
                DriverNumber=df_three_best_race_laps.iloc[i]["DriverNumber"],
                Team=df_three_best_race_laps.iloc[i]["Team"],
                LapTime=df_three_best_race_laps.iloc[i]["LapTime"]
            )
            vueltas_pilotos[piloto] = df_telemetria
    else:
        for piloto, lap_number in vueltas_pilotos_dict.items():
            vuelta_seleccionada = laps.pick_driver(piloto)[laps.pick_driver(piloto)["LapNumber"] == lap_number[0]]
            print(vuelta_seleccionada["LapTime"])
            if vuelta_seleccionada.empty:
                send_error_message(
                    status_code=404,
                    title="No hay vueltas disponibles",
                    message=f"No existen vueltas para {piloto} en la sesión {session.event['EventName']} {session.event.year} {session.name}"
                )
            df_telemetria = vuelta_seleccionada.iloc[0].get_telemetry().reset_index(drop=True)
            df_telemetria = df_telemetria.assign(
                DriverNumber=vuelta_seleccionada.iloc[0]["DriverNumber"],
                Team=vuelta_seleccionada.iloc[0]["Team"],
                LapTime=vuelta_seleccionada.iloc[0]["LapTime"]
            )
            vueltas_pilotos[piloto] = df_telemetria

    if not vueltas_pilotos:
        raise ValueError("No valid laps found for analysis.")

    df_vueltas = pd.concat(vueltas_pilotos, names=["Driver"]).reset_index()

    tel_fastest_lap = df_vueltas.loc[df_vueltas["LapTime"] == df_vueltas["LapTime"].min()]
    x = np.array(tel_fastest_lap['X'].values)
    y = np.array(tel_fastest_lap['Y'].values)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Driver mapping for color indices
    team_colors = get_team_colors(df_vueltas[["Team", "Driver"]].drop_duplicates(), session)

    #   Comprobar que no hay colores repetidos
    conteo = Counter(team_colors)
    for color_contado, count in conteo.items():
        if count > 1:
            for i, color in enumerate(team_colors):
                if color == color_contado:
                    team_colors[i] = mcolors.to_rgba(color_contado, alpha=0.1)
                    break

    cmap = ListedColormap(team_colors)

    driver_map = {driver: i for i, driver in enumerate(df_vueltas["Driver"].drop_duplicates())}

    mini_sectors = min({len(df_vueltas[df_vueltas["Driver"] == driver]) for driver in df_vueltas["Driver"].drop_duplicates()})
    
    leading_driver_per_point = list()
    telemetrias_por_piloto = {driver: df_vueltas[df_vueltas["Driver"] == driver] for driver in df_vueltas["Driver"].unique()}
    for i in range(mini_sectors):
        distances = [telemetrias_por_piloto[driver]["RelativeDistance"].iloc[i] 
                    for driver in telemetrias_por_piloto.keys()]        
        leading_driver_per_point.append(np.argmax(distances))

    lc_comp = LineCollection(segments, cmap=cmap, norm=plt.Normalize(-0.5, len(team_colors) - 0.5))
    lc_comp.set_array(leading_driver_per_point)
    lc_comp.set_linewidth(len(driver_map))

    plt.subplots()
    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    cbar = plt.colorbar(
        mappable=lc_comp,
        label="Drivers",
        boundaries=np.arange(0, len(team_colors) + 1) - 0.5,
        ticks=np.arange(len(team_colors)),
    )

    cbar.set_ticklabels(driver_map.keys())

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n"+
            f"Fastest laps comparative {', '.join(df_vueltas['Driver'].drop_duplicates().to_list())}")
    plt.tight_layout()