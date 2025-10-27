import fastf1
import pandas as pd

import matplotlib.pyplot as plt

from app.utils import get_team_colors, get_session, try_get_session_laps

def braking_analisys(type_event:str, year:int, event:int, session:str):
    """
    Analyzes the braking of the drivers in a specific session.

    Parameters:
    type_event (str): The type of event ('official', 'pretest').
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True, color_scheme='fastf1')

    session = get_session(type_event, year, event, session)
    laps = try_get_session_laps(session=session)

    all_telemetry = []

    for _, lap in laps.iterrows():
        try:
            telemetry = lap.get_telemetry()
            telemetry["Driver"] = lap["Driver"]
            telemetry["Team"] = lap["Team"]
            telemetry["Brake"] = 1 - telemetry["Throttle"]
            all_telemetry.append(telemetry)
        except Exception as e:
            print(f'Error processing telemetry for lap {lap["LapNumber"]} of driver {lap["Driver"]}: {e}')

    all_telemetry_df = pd.concat(all_telemetry, ignore_index=True)

    all_telemetry_df["Brake"] = all_telemetry_df["Brake"].abs()
    df_mean_brake_drive = all_telemetry_df.groupby(["Driver", "Team"], as_index=False)["Brake"].mean()
    df_mean_brake_drive.sort_values(by="Brake", ascending=False, inplace=True)
    df_mean_brake_drive.reset_index(drop=True, inplace=True)

    team_colors = get_team_colors(df_mean_brake_drive, session)

    fig, ax = plt.subplots()
    bars = ax.barh(df_mean_brake_drive.index, df_mean_brake_drive["Brake"],
        color=team_colors, edgecolor='grey')
    ax.set_yticks(df_mean_brake_drive.index)
    ax.set_yticklabels(df_mean_brake_drive["Driver"])

    ax.set_xlabel('Brake Usage')
    ax.set_ylabel('Drivers')

    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    time_diff_to_pole = list()
    for i, bar in enumerate(bars.patches):
        brake = df_mean_brake_drive["Brake"].loc[i]
        cadena = f'{brake:.2f}'
        time_diff_to_pole.append(brake)

        ax.text(df_mean_brake_drive["Brake"].loc[i] + 0.015, bar.get_y() + bar.get_height()/2, cadena, 
        va='center', ha='left', color='white')
    ax.set_xlim(0, max(time_diff_to_pole) * 1.15)

    plt.suptitle(f'{session.event["EventName"]} {session.event.year} {session.name} | Brake Usage')
    plt.tight_layout()