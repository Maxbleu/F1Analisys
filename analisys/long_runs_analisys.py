import matplotlib.pyplot as plt

import fastf1.plotting as f1_plotting

from utils._init_ import get_session, try_get_session_laps

def long_runs_analisys(type_event:str, year: int, event: int, session: str, threshold:float, vueltas_pilotos: dict):
    """
    Analyzes long runs specific drivers in sessions.

    Parameters:
    type_event (str): The type of event ('official', 'pretest').
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    threshold (float): The threshold for quick laps.
    vueltas_pilotos (dict): A dictionary with the laps of each driver in the session
    """

    f1_plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True, color_scheme='fastf1')

    session = get_session(type_event, year, event, session)
    laps = try_get_session_laps(session=session)

    fig, ax = plt.subplots()
    for piloto in vueltas_pilotos.keys():
        drv_laps = laps.pick_driver(piloto)
        drv_laps = drv_laps.pick_laps(range(vueltas_pilotos[piloto][0],vueltas_pilotos[piloto][1]))
        drv_laps = drv_laps.reset_index(drop=True)

        drv_laps = drv_laps.pick_quicklaps(threshold)

        abb = drv_laps['Driver'].iloc[0]
        style = f1_plotting.get_driver_style(identifier=abb,
                                                style=['color', 'linestyle'],
                                                session=session)
        style['marker'] = 'o'

        drv_laps["LapTime"] = drv_laps["LapTime"].dt.total_seconds()
        ax.plot(drv_laps["LapNumber"], drv_laps['LapTime'], label=piloto, **style)

    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
    ax.set_ylabel("LapTime")
    ax.set_xlabel("LapNumber")
    plt.legend()

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n"
            f"Long runs comparative of {', '.join(vueltas_pilotos.keys())}")
    plt.tight_layout()