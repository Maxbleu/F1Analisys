import fastf1.plotting
from timple.timedelta import strftimedelta

import pandas as pd

import matplotlib.pyplot as plt

from enums.process_state import ProcessState

def analisys_fastest_drivers_compound(year: int, round: int, session: str):

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)

    try:
        session = fastf1.get_session(year, round, session)
    except Exception as e:
        return ProcessState.FAILED.name

    session.load()

    session.laps["LapTime"] = pd.to_timedelta(session.laps["LapTime"])

    session_laps = session.laps.pick_not_deleted()

    avg_lap_times = session_laps.groupby(["Driver","Team", "Compound"])["LapTime"].mean().reset_index()
    avg_lap_times.rename(columns={"LapTime": "AvgLapTime"}, inplace=True)

    compounds_laps = {}

    for compound in avg_lap_times['Compound'].unique():
        compound_laps = avg_lap_times[avg_lap_times['Compound'] == compound]
        compound_laps = compound_laps.sort_values(by="AvgLapTime", ascending=True).reset_index(drop=True)
        compounds_laps[compound] = compound_laps

    """team_colors = {}
    for key, value in compounds_laps.items():
        colors = []
        for index, row in value.iterrows():
            color = fastf1.plotting.get_team_color(row['Team'], session=session)
            colors.append(color)
        team_colors[key] = colors"""

    fig, axes = plt.subplots(1, len(compounds_laps), figsize=(10, 15))

    if len(compounds_laps) == 1:
        axes = [axes]

    for ax, (compound, lap_times) in zip(axes, compounds_laps.items()):
    
        
        ax.barh(avg_lap_times.index, avg_lap_times['AvgLapTime'], color="blue")
        ax.set_yticks(avg_lap_times.index)
        ax.set_yticklabels(avg_lap_times['Driver'])

        ax.invert_yaxis()

        ax.set_axisbelow(True)
        ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

        fastest_lap = avg_lap_times.loc[avg_lap_times['AvgLapTime'].idxmin()]
        lap_time_string = strftimedelta(fastest_lap['AvgLapTime'], '%m:%s.%ms')

        plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n"
                    f"Fastest Lap: {lap_time_string} ({fastest_lap['Driver']})")

    plt.show()

    return ProcessState.COMPLETED.name