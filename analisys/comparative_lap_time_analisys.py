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

    fig, ax = plt.subplots(6, 1, figsize=(6, 12), gridspec_kw={'height_ratios': [0.8, 0.3, 0.3, 0.3, 0.3, 0.3]})

    ax[0].plot(ref_tel['Distance'], ref_tel['Speed'], color=plotting.get_team_color(vueltas[keys[0]]['Team'].iloc[0], session), label=keys[0])
    ax[0].plot(compare_tel['Distance'], compare_tel['Speed'], color=plotting.get_team_color(vueltas[keys[1]]['Team'].iloc[0], session), label=keys[1])
    ax[0].legend(loc="upper right")

    ax[0].set_xlabel("Track distance")
    ax[0].set_ylabel("Speed")
    
    twin = ax[0].twinx()
    twin.plot(ref_tel['Distance'], delta_time, '--', color='white')
    twin.set_ylabel(f" {keys[1]} ahead | {keys[0]} ahead")

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n{keys[0]} lap {vueltas_pilotos[keys[0]]} vs {keys[1]} lap {vueltas_pilotos[keys[1]]}")

    #   Obtenemos las telemetrias de las vueltas más rápidas de cada piloto.
    tel_fastest_lap = vueltas[keys[0]].get_telemetry()
    second_tel_fastest_lap = vueltas[keys[1]].get_telemetry()

    #   Gráfico de acelerador.
    ax[1].stairs(tel_fastest_lap['Throttle'], label=keys[0], color=plotting.get_team_color(vueltas[keys[0]]['Team'].iloc[0], session))
    ax[1].stairs(second_tel_fastest_lap['Throttle'], label=keys[1], color=plotting.get_team_color(vueltas[keys[1]]['Team'].iloc[0], session))
    ax[1].set_ylabel("Throttle")

    #   Gráfico de freno.
    ax[2].stairs(tel_fastest_lap['Brake'], label=keys[0], color=plotting.get_team_color(vueltas[keys[0]]['Team'].iloc[0], session))
    ax[2].stairs(second_tel_fastest_lap['Brake'], label=keys[1], color=plotting.get_team_color(vueltas[keys[1]]['Team'].iloc[0], session))
    ax[2].set_ylabel("Brake")

    #   Gráfico de RPM
    ax[3].plot(tel_fastest_lap['RPM'], label=keys[0], color=plotting.get_team_color(vueltas[keys[0]]['Team'].iloc[0], session))
    ax[3].plot(second_tel_fastest_lap['RPM'], label=keys[1], color=plotting.get_team_color(vueltas[keys[1]]['Team'].iloc[0], session))
    ax[3].set_ylabel("RPM")

    #   Gráfico de Gear
    ax[4].stairs(tel_fastest_lap['nGear'], label=keys[0], color=plotting.get_team_color(vueltas[keys[0]]['Team'].iloc[0], session))
    ax[4].stairs(second_tel_fastest_lap['nGear'], label=keys[1], color=plotting.get_team_color(vueltas[keys[1]]['Team'].iloc[0], session))
    ax[4].set_ylabel("nGear")

    #   Gráfico de DRS
    ax[5].stairs(tel_fastest_lap['DRS'], label=keys[0], color=plotting.get_team_color(vueltas[keys[0]]['Team'].iloc[0], session))
    ax[5].stairs(second_tel_fastest_lap['DRS'], label=keys[1], color=plotting.get_team_color(vueltas[keys[1]]['Team'].iloc[0], session))
    ax[5].set_ylabel("DRS")

    plt.tight_layout()