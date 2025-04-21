import fastf1
import matplotlib.pyplot as plt

from utils._init_ import get_team_colors, get_session, try_get_session_laps

def top_speed_analisys(type_event:str, year:int, event:int, session:str):
    """
    Analyzes the top speed of the drivers in a specific session.

    Parameters:
    type_event (str): The type of event ('official', 'pretest').
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True, color_scheme='fastf1')

    session = get_session(type_event, year, event, session)
    laps = try_get_session_laps(session=session)

    df_top_speeds = laps[["Driver","Team"]]
    df_top_speeds["TopSpeed"] = 0

    drivers = df_top_speeds['Driver'].unique()
    for driver in drivers:
        laps_driver_session = laps[laps["Driver"] == driver]
        top_speed_driver = laps_driver_session["SpeedST"].max()
        df_top_speeds.loc[df_top_speeds["Driver"] == driver, "TopSpeed"] = top_speed_driver

    df_top_speeds.dropna(inplace=True, ignore_index=True)
    df_top_speeds.sort_values(by="TopSpeed", inplace=True, ascending=False)

    df_top_speeds = df_top_speeds.drop_duplicates().reset_index(drop=True)

    team_colors = get_team_colors(df_top_speeds, session)

    fig, ax = plt.subplots()

    bars = ax.barh(df_top_speeds.index, df_top_speeds["TopSpeed"], color=team_colors, edgecolor='grey')
    ax.set_yticks(df_top_speeds.index)
    ax.set_yticklabels(df_top_speeds["Driver"])

    plt.xlabel('Speed (km/h)')
    plt.ylabel('Drivers')

    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    iterator = 0
    for bar in bars:
        top_speed = df_top_speeds.iloc[iterator]["TopSpeed"]
        width = bar.get_width()
        ax.text(
            width+0.05,
            bar.get_y() + bar.get_height()/2,
            f"{top_speed}",
            va='center',
            ha='left',
            color='white',
            fontsize=10
        )
        iterator += 1

    top_speed = df_top_speeds.iloc[0]["TopSpeed"]
    ax.set_xlim(0, top_speed * 1.10)

    plt.suptitle(f'{session.event["EventName"]} {session.event.year} {session.name} | Top Speed')
    plt.tight_layout()