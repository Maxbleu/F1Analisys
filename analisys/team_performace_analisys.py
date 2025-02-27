import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker

import fastf1.plotting

from utils._init_ import format_time_mmssmmm, get_session, try_get_session_laps

def team_performace_analisys(year: int, round: int, session: str, test_number:int, session_number:int):
    """
    Analyzes the team performance in a specific session.

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
    laps = try_get_session_laps(session=session).pick_quicklaps()

    laps.dropna(ignore_index=True)

    transformed_laps = laps.copy()
    transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()

    team_order = (
        transformed_laps[["Team", "LapTime (s)"]]
        .groupby("Team")
        .median()["LapTime (s)"]
        .sort_values()
        .index
    )

    team_palette = {team: fastf1.plotting.get_team_color(team, session=session)
                    for team in team_order}

    fig, ax = plt.subplots(figsize=(15, 10))
    sns.boxplot(
        data=transformed_laps,
        x="Team",
        y="LapTime (s)",
        hue="Team",
        order=team_order,
        palette=team_palette,
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
    )

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: format_time_mmssmmm(x)))
    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name} | Team Performance")
    plt.tight_layout()
