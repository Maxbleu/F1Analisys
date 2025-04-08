import fastf1

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from collections import Counter

from utils._init_ import get_session, try_get_session_laps, send_error_message, get_team_colors, get_delta_time

def comparative_lap_time_analisys(year: int, round: int, session: str, test_number: int, session_number: int, vueltas_pilotos_dict: dict):
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
    vueltas_pilotos = {}
    if vueltas_pilotos_dict is None or len(vueltas_pilotos_dict) == 0:
        df_three_best_race_laps = laps.sort_values(by="LapTime").drop_duplicates(subset="Driver").reset_index(drop=True).head(3)
        for i, piloto in enumerate(df_three_best_race_laps["Driver"]):
            df_telemetria = df_three_best_race_laps.iloc[i:i+1]
            vueltas_pilotos[piloto] = df_telemetria.iloc[0]
    else:
        for piloto in vueltas_pilotos_dict.keys():
            vuelta_seleccionada = laps.loc[laps["Driver"] == piloto].loc[laps["LapNumber"] == vueltas_pilotos_dict[piloto][0]]
            if vuelta_seleccionada.empty:
                send_error_message(status_code=404, title="No hay vueltas disponibles", message=f"No existen vueltas para {piloto} en la sesión {session.event["EventName"]} {session.event.year} {session.name}")
            vueltas_pilotos[piloto] = vuelta_seleccionada

    if not vueltas_pilotos:
        raise ValueError("No valid laps found for analysis.")

    df_vueltas = pd.concat(vueltas_pilotos).reset_index()

    # Driver mapping for color indices
    team_colors = get_team_colors(df_vueltas[["Team", "Driver"]].drop_duplicates(), session)

    #   Comprobar que no hay colores repetidos
    conteo = Counter(team_colors)
    for color_contado, count in conteo.items():
        if count > 1:
            for i, color in reversed(list(enumerate(team_colors))):
                if color == color_contado:
                    team_colors[i] = mcolors.to_rgba(color_contado, alpha=0.5)
                    break

    fig, ax = plt.subplots(7, 1, figsize=(6, 12), gridspec_kw={'height_ratios': [0.8, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]})

    keys = list(vueltas_pilotos.keys())
    for i, piloto in enumerate(keys):

        color = team_colors[i]
        tel_lap = vueltas_pilotos[keys[i]].get_telemetry()

        delta_time, ref_tel, compare_tel = get_delta_time(vueltas_pilotos[keys[0]], vueltas_pilotos[keys[i]])

        #   Gráfico de velocidad en distancia
        ax[0].plot(ref_tel["Distance"] if i == 0 else compare_tel["Distance"], ref_tel["Speed"] if i == 0 else compare_tel["Speed"], color=color, label=keys[i])

        #   Gráfico de deltas
        ax[1].plot(ref_tel['Distance'], delta_time, '--', color=color)

        #   Gráfico de acelerador
        ax[2].stairs(tel_lap['Throttle'], color=color, label=keys[i])

        #   Gráfico de freno.
        ax[3].stairs(tel_lap['Brake'], color=color, label=keys[i])

        #   Gráfico de RPM
        ax[4].plot(tel_lap['RPM'], color=color, label=keys[i])

        #   Gráfico de Gear
        ax[5].stairs(tel_lap['nGear'], color=color, label=keys[i])

        #   Gráfico de DRS
        ax[6].stairs(tel_lap['DRS'], color=color, label=keys[i])

    #   Enumerar curvas en la telemetría
    v_max = vueltas_pilotos[keys[0]].get_telemetry()['Speed'].max()
    v_min = vueltas_pilotos[keys[0]].get_telemetry()['Speed'].min()
    circuit_info = session.get_circuit_info()

    ax[0].vlines(x=circuit_info.corners['Distance'], ymin=v_min-20, ymax=v_max+20,
            linestyles='dotted', colors='grey')
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        ax[0].text(corner['Distance'], v_min-20, txt,
                va='center_baseline', ha='center', size='small')

    #   Detallar gráficas
    ax[0].legend(loc="upper right")
    ax[0].set_xlabel("Track distance")
    ax[0].set_ylabel("Speed")

    ax[1].set_ylabel("Delta")
    ax[2].set_ylabel("Throttle")
    ax[3].set_ylabel("Brake")
    ax[4].set_ylabel("RPM")
    ax[5].set_ylabel("nGear")
    ax[6].set_ylabel("DRS")

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n"
                f"Lap time comparative of {', '.join(vueltas_pilotos_dict.keys())}")

    plt.tight_layout()