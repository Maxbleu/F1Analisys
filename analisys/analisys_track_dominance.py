import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib import colormaps
from matplotlib.colors import ListedColormap
from matplotlib.collections import LineCollection

import fastf1
import fastf1.plotting

import random

from enums.process_state import ProcessState

def frase_grafica_qualy(drivers):
    cadena = ""
    for i, driver in enumerate(drivers):
        if i > 0:
            cadena += " vs "
        cadena += f"{driver}"
    return cadena

def analisys_track_dominance(year, round, session):
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme='fastf1')

    try:
        session = fastf1.get_session(year, round, session)
    except Exception as e:
        return ProcessState.FAILED.name

    session.load()

    df_three_best_race_laps = session.laps.pick_not_deleted().sort_values(by="LapTime").drop_duplicates(subset="Driver").reset_index(drop=True).head(4)

    tel_fastest_lap = df_three_best_race_laps.iloc[0].get_telemetry().reset_index(drop=True)
    tel_second_fastest_lap = df_three_best_race_laps.iloc[1].get_telemetry().reset_index(drop=True)
    tel_third_fastest_lap = df_three_best_race_laps.iloc[2].get_telemetry().reset_index(drop=True)
    tel_fourth_fastest_lap = df_three_best_race_laps.iloc[3].get_telemetry().reset_index(drop=True)

    df_three_best_race_laps["DriverNumber"] = pd.to_numeric(df_three_best_race_laps["DriverNumber"], errors='coerce')

    team_colors = [fastf1.plotting.get_team_color(lap["Team"], session=session) for _, lap in df_three_best_race_laps.iterrows()]

    x = np.array(tel_fastest_lap['X'].values)
    y = np.array(tel_fastest_lap['Y'].values)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    cmap = ListedColormap(team_colors)
    lc_comp = LineCollection(segments, norm=plt.Normalize(0, cmap.N+1), cmap=cmap)

    best_driver_each_mini_sector = []
    mini_sectors = min(len(tel_fastest_lap), len(tel_second_fastest_lap), len(tel_third_fastest_lap), len(tel_fourth_fastest_lap))

    for i in range(mini_sectors):
        distances = [
            tel_fastest_lap["RelativeDistance"].iloc[i],
            tel_second_fastest_lap["RelativeDistance"].iloc[i],
            tel_third_fastest_lap["RelativeDistance"].iloc[i],
            tel_fourth_fastest_lap["RelativeDistance"].iloc[i]
        ]
        best_driver_each_mini_sector.append(np.argmax(distances))

    lc_comp.set_array(best_driver_each_mini_sector)
    lc_comp.set_linewidth(4)

    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    drivers = df_three_best_race_laps["Driver"].head(3).tolist()
    title = f"{session.event['EventName']} {session.event.year} {session.name}"
    if session.name == "Qualifying":
        title = title + f"\n {frase_grafica_qualy(drivers)}"
    else:
        title = title + " | Track dominance \nfastest laps"

    plt.suptitle(title)

    cbar = plt.colorbar(
        mappable=lc_comp,
        label="Drivers",
        boundaries=np.arange(0, len(team_colors)),
        ticks=np.arange(0.5, len(team_colors)-1),
    )

    cbar.set_ticklabels(df_three_best_race_laps["DriverNumber"].head(3).tolist())

    return ProcessState.COMPLETED.name