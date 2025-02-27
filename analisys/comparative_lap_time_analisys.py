import fastf1
import fastf1.plotting as plotting
import fastf1.utils as utils

import pandas as pd
import matplotlib.pyplot as plt

from utils._init_ import get_session, try_get_session_laps, send_error_message

def comparative_lap_time_analisys(year: int, round: int, session: str, test_number: int, session_number: int, vueltas_pilotos: dict):
    """
    Analisys of one lap time from two drivers in a speciffic session.

    Parameters:
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    test_number (int): The test number of the session.
    session_number (int): The session number of the session.
    vueltas_pilotos (dict): A dictionary with the laps of each driver.
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)

    session = get_session(year, round, session, test_number, session_number)
    laps = try_get_session_laps(session=session)

    laps["LapTime"] = pd.to_timedelta(laps["LapTime"]) 

    vueltas = {}
    for piloto in vueltas_pilotos.keys():
        vuelta_seleccionada = laps.loc[laps["Driver"] == piloto].loc[laps["LapNumber"] == vueltas_pilotos[piloto]]
        if vuelta_seleccionada.empty:
            send_error_message(status_code=404, title="No hay vueltas disponibles", message=f"No existen vueltas para {piloto} en la sesión {session.event["EventName"]} {session.event.year} {session.name}")
        vueltas[piloto] = vuelta_seleccionada

    keys = list(vueltas.keys())
    delta_time, ref_tel, compare_tel = utils.delta_time(vueltas[keys[0]], vueltas[keys[1]])

    fig, ax = plt.subplots()

    ax.plot(ref_tel['Distance'], ref_tel['Speed'], color=plotting.get_team_color(vueltas[keys[0]]['Team'].iloc[0], session), label=keys[0])
    ax.plot(compare_tel['Distance'], compare_tel['Speed'], color=plotting.get_team_color(vueltas[keys[1]]['Team'].iloc[0], session), label=keys[1])
    ax.legend(loc="upper right")

    ax.set_xlabel("Track distance")
    ax.set_ylabel("Speed")
    
    twin = ax.twinx()
    twin.plot(ref_tel['Distance'], delta_time, '--', color='white')
    twin.set_ylabel(f" {keys[1]} ahead | {keys[0]} ahead")

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n{keys[0]} lap {vueltas_pilotos[keys[0]]} vs {keys[1]} lap {vueltas_pilotos[keys[1]]}")
    plt.tight_layout()
