import matplotlib.pyplot as plt
import fastf1.plotting

from enums.process_state import ProcessState

def analisys_race_position_evolution(year: int, round: int, session: str):
    """
    Analyzes the race position evolution of the drivers in a race session.

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
        if session != "R": return ProcessState.CANCELED.name
        session = fastf1.get_session(year, round, session)
    except Exception as e:
        return ProcessState.FAILED.name

    session.load()

    fig, ax = plt.subplots(figsize=(8.0, 4.9))

    for drv in session.drivers:
        drv_laps = session.laps.pick_driver(drv)

        abb = drv_laps['Driver'].iloc[0]
        style = fastf1.plotting.get_driver_style(identifier=abb,
                                                style=['color', 'linestyle'],
                                                session=session)

        ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
                label=abb, **style)

    ax.set_ylim([20.5, 0.5])
    ax.set_yticks([1, 5, 10, 15, 20])
    ax.set_xlabel('Lap')
    ax.set_ylabel('Position')

    ax.legend(bbox_to_anchor=(1.0, 1.02))
    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name} | Results")
    plt.tight_layout()

    return ProcessState.COMPLETED.name