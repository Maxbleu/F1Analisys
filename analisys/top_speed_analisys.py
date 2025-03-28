import fastf1
import matplotlib.pyplot as plt

from utils._init_ import get_team_colors, get_session, try_get_session_laps

def top_speed_analisys(year:int, round:int, session:str, test_number:int, session_number:int):
    """
    Analyzes the top speed of the drivers in a specific session.

    Parameters:
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    test_number (int): The test number of the session.
    session_number (int): The session number of the session.
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                        color_scheme='fastf1')

    session = get_session(year, round, session, test_number, session_number)
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

    fig, ax = plt.subplots(figsize=(10, 8))

    bars = ax.bar(df_top_speeds["Driver"], df_top_speeds["TopSpeed"], color=team_colors)

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name} | Top Speed")
    plt.xlabel('Drivers')
    plt.ylabel('Speed')

    iterator = 0
    for bar in bars:
        top_speed = df_top_speeds.iloc[iterator]["TopSpeed"]
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 1,
            f"{top_speed}",
            ha='center',
            va='bottom',
            color='white',
            fontsize=10
        )
        iterator += 1
    plt.tight_layout()
