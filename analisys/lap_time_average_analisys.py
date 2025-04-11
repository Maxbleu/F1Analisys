import fastf1
import matplotlib.pyplot as plt
import pandas as pd
from utils._init_ import get_team_colors, get_session, try_get_session_laps

def lap_time_average_analisys(type_event:str, year: int, event: int, session: str):
    """
    Analyzes the lap time average each drive in specific session

    Parameters:
    type_event (str): The type of event ('official', 'pretest').
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True, color_scheme='fastf1')

    session = get_session(type_event, year, event, session)
    laps = try_get_session_laps(session)

    laps["LapTime"] = pd.to_timedelta(laps["LapTime"])

    drivers = laps['Driver'].unique()
    teams = [session.results.loc[session.results['Abbreviation'] == driver, 'TeamName'].iloc[0] for driver in drivers]

    median_lap_times = []
    for driver in drivers:
        driver_laps = laps[laps['Driver'] == driver]
        median_lap_time = driver_laps["LapTime"].median().total_seconds()
        median_lap_times.append(median_lap_time)

    best_median_lap_time = min(median_lap_times)
    lap_time_diffs = [time - best_median_lap_time for time in median_lap_times]

    df_median_lap_time_drivers = pd.DataFrame({
        'Driver': drivers,
        'Team': teams,
        'MedianLapTimeDiff': lap_time_diffs,
    }).sort_values(by="MedianLapTimeDiff").reset_index(drop=True)

    team_colors = get_team_colors(df_median_lap_time_drivers, session)

    fig, ax = plt.subplots()

    bars = ax.barh(df_median_lap_time_drivers.index, df_median_lap_time_drivers["MedianLapTimeDiff"], 
                    color=team_colors, edgecolor='grey')
    ax.set_yticks(df_median_lap_time_drivers.index)
    ax.set_yticklabels(df_median_lap_time_drivers["Driver"])

    ax.set_xlabel("Diff")
    ax.set_ylabel("Drivers")

    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    time_diff_to_pole = list()
    for bar in bars:
        width = bar.get_width()
        if(width > 0):
            cadena = f'{width:.2f}'
        else:
            cadena = 'Fastest'
        time_diff_to_pole.append(width)

        ax.text(width+0.05, bar.get_y() + bar.get_height()/2, cadena, 
        va='center', ha='left', color='white')
    ax.set_xlim(0, max(time_diff_to_pole) * 1.15)

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name} | Lap Time Average")
    plt.tight_layout()