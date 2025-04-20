import matplotlib.pyplot as plt
import pandas as pd
from timple.timedelta import strftimedelta

import fastf1.plotting

from utils._init_ import get_team_colors, get_session, try_get_session_laps

def fastest_laps_analisys(type_event:str, year: int, event: int, session: str):
    """
    Analyzes the fastest laps each driver in specific session

    Parameters:
    type_event (str): The type of event ('official', 'pretest').
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True, color_scheme='fastf1')

    session = get_session(type_event, year, event, session)
    laps = try_get_session_laps(session)

    drivers = pd.unique(laps['Driver'])

    fastest_laps = pd.DataFrame()
    for drv in drivers:
        driver_laps = laps.pick_driver(drv)
        if not driver_laps.empty:
            fastest_lap = driver_laps.pick_fastest()
            if fastest_lap is not None:
                fastest_laps = pd.concat([fastest_laps, pd.DataFrame([fastest_lap])], ignore_index=True)

    if not fastest_laps.empty:
        # Sort by lap time
        fastest_laps = fastest_laps.sort_values(by='LapTime').reset_index(drop=True)
        
        # Get the pole lap and calculate deltas
        pole_lap = fastest_laps.iloc[0]
        fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']

    team_colors = get_team_colors(fastest_laps, session)

    fig, ax = plt.subplots()
    ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(fastest_laps.index)
    ax.set_yticklabels(fastest_laps['Driver'])

    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
    ax.set_xlabel('Delta to Fastest Lap')
    ax.set_ylabel('Driver')

    ax1 = ax.twinx()
    ax1.set_yticks(fastest_laps.index)
    ax1.set_yticklabels(fastest_laps['LapNumber'])
    ax1.set_ylabel('Lap Number')
    ax1.set_ylim(ax.get_ylim())

    lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n"
                f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")
    plt.tight_layout()