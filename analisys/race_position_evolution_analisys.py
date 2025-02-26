import matplotlib.pyplot as plt
import fastf1.plotting

from utils._init_ import get_session, send_error_message, try_get_session_laps

def race_position_evolution_analisys(year: int, round: int, session: str):
    """
    Analyzes the race position evolution of the drivers in a race session.

    Parameters:
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type ('R').
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                            color_scheme='fastf1')

    if session != "R": send_error_message(status_code=400, title="Solo carreras", message="Esta gráfico solo está disponible para carreras")
    session = get_session(year, round, session)
    laps = try_get_session_laps(session=session)

    fig, ax = plt.subplots(figsize=(10.0, 6))

    for drv in session.drivers:
        drv_laps = laps.pick_driver(drv)

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