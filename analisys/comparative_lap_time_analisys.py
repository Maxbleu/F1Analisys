import fastf1
import fastf1.plotting as plotting
import fastf1.utils as utils

import pandas as pd
import matplotlib.pyplot as plt

from utils._init_ import get_session
from enums.process_state import ProcessState

def comparative_lap_time_analisys(
        year: int, 
        round: int, 
        session: str, 
        test_number: int,
        session_number: int,
        vueltas_pilotos: dict
    ):

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)

    session = get_session(year, round, session, test_number, session_number)
    if session is None:
        return ProcessState.FAILED.name

    session.load()

    laps = session.laps

    laps["LapTime"] = pd.to_timedelta(laps["LapTime"])

    vueltas = {}
    for piloto in vueltas_pilotos.keys():
        try:
            vueltas[piloto] = laps.loc[laps["Driver"] == piloto].loc[laps["LapNumber"] == vueltas_pilotos[piloto]]
        except Exception as e:
            return ProcessState.FAILED.name

    keys = list(vueltas.keys())
    delta_time, ref_tel, compare_tel = utils.delta_time(vueltas[keys[0]], vueltas[keys[1]])

    fig, ax = plt.subplots()

    line1 = ax.plot(ref_tel['Distance'], ref_tel['Speed'], color=plotting.get_team_color(vueltas[keys[0]]['Team'].iloc[0], session))
    line2 = ax.plot(compare_tel['Distance'], compare_tel['Speed'], color=plotting.get_team_color(vueltas[keys[1]]['Team'].iloc[0], session))
    
    ax.set_xlabel("Track distance")
    ax.set_ylabel("Speed")

    twin = ax.twinx()
    line3 = twin.plot(ref_tel['Distance'], delta_time, '--', color='white')
    twin.set_ylabel(f" {keys[1]} ahead | {keys[0]} ahead")

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n{keys[0]} lap {vueltas_pilotos[keys[0]]} vs {keys[1]} lap {vueltas_pilotos[keys[1]]}")

    return ProcessState.COMPLETED.name