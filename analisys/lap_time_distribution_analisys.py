import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import fastf1.plotting

from enums.process_state import ProcessState
from utils._init_ import format_time_mmssmmm, get_session

def lap_time_distribution_analisys(year: int, round: int, session: str):
    """
    Analyzes the fastest stints of a race selecting only the top 10 drivers

    Parameters:
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    test_number (int): The test number of the session.
    session_number (int): The session number of the session.

    Returns:
    str: The process state, either 'FAILED' or 'COMPLETED'.
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme='fastf1')

    session = get_session(year, round, session)
    if session is None:
        return ProcessState.FAILED

    session.load()

    finishing_order = session.results.iloc[0:10]['Abbreviation'].tolist()

    laps = session.laps

    driver_laps = laps.pick_drivers(finishing_order).pick_quicklaps().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))

    driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

    sns.violinplot(data=driver_laps,
                x="Driver",
                y="LapTime(s)",
                hue="Driver",
                inner=None,
                density_norm="area",
                order=finishing_order,
                palette=fastf1.plotting.get_driver_color_mapping(session=session)
                )

    print(fastf1.plotting.get_compound_mapping(session=session))
    print(driver_laps["Compound"].unique().tolist())

    sns.swarmplot(data=driver_laps,
                x="Driver",
                y="LapTime(s)",
                order=finishing_order,
                hue="Compound",
                palette=fastf1.plotting.get_compound_mapping(session=session),
                hue_order=driver_laps["Compound"].unique().tolist(),
                linewidth=0,
                size=4,
                )

    ax.set_xlabel("Driver")
    ax.set_ylabel("Lap Time (s)")
    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name} | Lap Pace Top 10")
    sns.despine(left=True, bottom=True)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: format_time_mmssmmm(x)))
    plt.tight_layout()

    return ProcessState.COMPLETED.name