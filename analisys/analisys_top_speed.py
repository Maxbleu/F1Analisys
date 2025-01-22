import fastf1
import matplotlib.pyplot as plt

from enums.process_state import ProcessState

def analisys_top_speed(year, round, session):
    """
    Analyzes the top speed of the drivers in a specific session.

    Parameters:
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'R').

    Returns:
    str: The process state, either 'FAILED' or 'SUCCESS'.
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                        color_scheme='fastf1')

    try:
        session = fastf1.get_session(year, round, session)
    except Exception as e:
        return ProcessState.FAILED.name

    session.load()

    laps = session.laps[session.laps["Deleted"] == False]

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

    team_colors = list()
    df_teams = df_top_speeds[["Team", "Driver"]].drop_duplicates().reset_index(drop=True)
    for index, lap in df_teams.iterlaps():
        color = fastf1.plotting.get_team_color(lap['Team'], session=session)
        team_colors.append(color)

    fig, ax = plt.subplots(figsize=(10, 8))

    bars = ax.bar(df_top_speeds["Driver"], df_top_speeds["TopSpeed"], color=team_colors)

    plt.title(f"{session.event['EventName']} {session.event.year} {session.name} | Top Speed")
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

    return ProcessState.COMPLETED.name