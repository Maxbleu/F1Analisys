import matplotlib.pyplot as plt
import fastf1.plotting

import pandas as pd

from utils._init_ import get_session, try_get_session_laps

def long_runs_analisys(year: int, round: int, session: str, test_number: int, session_number : int, vueltas_pilotos: dict):
    """
    Analyzes long runs specific drivers in sessions.

    Parameters:
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    test_number (int): The test number of the session.
    session_number (int): The session number of the session.
    vueltas_pilotos (dict): A dictionary with the laps of each driver in the session
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme='fastf1')

    session = get_session(year, round, session, test_number, session_number)
    laps = try_get_session_laps(session=session)

    laps["LapTime"] = pd.to_timedelta(laps["LapTime"]).dt.seconds

    fig, ax = plt.subplots()
    for piloto in vueltas_pilotos.keys():
        drv_laps = laps.pick_driver(piloto)
        drv_laps = drv_laps.pick_laps(range(vueltas_pilotos[piloto][0],vueltas_pilotos[piloto][1]))

        abb = drv_laps['Driver'].iloc[0]
        style = fastf1.plotting.get_driver_style(identifier=abb,
                                                style=['color', 'linestyle'],
                                                session=session)
        style['marker'] = 'o'

        ax.plot(drv_laps['LapNumber'], drv_laps['LapTime'], label=piloto, **style)

    ax.set_ylabel("LapTime")
    ax.set_xlabel("LapNumber")
    plt.legend()

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n"
            f"Long runs comparative of {', '.join(vueltas_pilotos.keys())}")
    plt.tight_layout()