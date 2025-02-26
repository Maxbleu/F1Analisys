import fastf1.plotting
from timple.timedelta import strftimedelta
import pandas as pd
import matplotlib.pyplot as plt

from utils._init_ import get_team_colors, get_session, try_get_session_laps

def fastest_drivers_compound_analisys(year: int, round: int, session: str, test_number: int, session_number: int):
    """
    Analyzes the fastest drivers each compound in specific session

    Parameters:
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    test_number (int): The test number of the session.
    session_number (int): The session number of the session.
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)

    session = get_session(year, round, session, test_number, session_number)
    laps = try_get_session_laps(session=session)

    laps["LapTime"] = pd.to_timedelta(laps["LapTime"])

    avg_lap_times = laps.groupby(["Driver","Team", "Compound"])["LapTime"].mean().reset_index()
    avg_lap_times.rename(columns={"LapTime": "AvgLapTime"}, inplace=True)

    compounds_laps = {}

    for compound in avg_lap_times['Compound'].unique():
        compound_laps = avg_lap_times[avg_lap_times['Compound'] == compound]
        
        total_laps = laps[laps['Compound'] == compound].groupby(["Driver"])["LapTime"].count()
        compound_laps["TotalLaps"] = compound_laps["Driver"].map(total_laps)
        compound_laps = compound_laps.dropna()
        
        if compound_laps.empty: continue
        compound_laps = compound_laps.sort_values(by="AvgLapTime", ascending=True).reset_index(drop=True)
        
        compound_laps["AvgLapTimeDiff"] = compound_laps["AvgLapTime"] - compound_laps["AvgLapTime"].iloc[0]
        compounds_laps[compound] = compound_laps

    team_colors = {}
    for key, value in compounds_laps.items():
        team_colors[key] = get_team_colors(value, session)

    if len(compounds_laps) == 1:
        fig, axes = plt.subplots(1, len(compounds_laps))
    elif len(compounds_laps) >= 2:
        fig, axes = plt.subplots(1, len(compounds_laps), figsize=(10, 5))

    if len(compounds_laps) == 1:
        axes = [axes]

    for ax, (key, value) in zip(axes, compounds_laps.items()):

        colors = team_colors[key]

        ax.barh(value.index, value["AvgLapTimeDiff"], color=colors)
        ax.set_yticks(value.index)
        ax.set_yticklabels(value['Driver'])
        ax.invert_yaxis()
        ax.set_axisbelow(True)
        ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

        fastest_lap = value.iloc[0]
        driver = fastest_lap['Driver']
        fastest_time = fastest_lap['AvgLapTime']

        ax.set_title(f"{key} average fastest\n {driver} - {strftimedelta(fastest_time, '%m:%s.%ms')}", fontsize=11)