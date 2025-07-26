import fastf1

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from collections import Counter

from utils._init_ import get_session, try_get_session_laps, send_error_message, get_team_colors, get_delta_time

def comparative_lap_time_analisys(type_event:str, year: int, event: int, session: str, vueltas_pilotos_dict: dict):
    """
    Analisys of one lap time from two drivers in a speciffic session.

    Parameters:
    type_event (str): The type of event ('official', 'pretest').
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    vueltas_pilotos (dict): A dictionary with the laps of each driver.
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')

    # Get the session and laps data
    session = get_session(type_event, year, event, session)
    laps = try_get_session_laps(session=session)

    # Check if user indicated laps to analyze
    vueltas_pilotos = {}
    if vueltas_pilotos_dict is None or len(vueltas_pilotos_dict) == 0:
        # Select the three best laps of the session
        df_laps_ordered = laps.sort_values(by="LapTime")
        df_best_laps = df_laps_ordered.head(3)

        # Keep only the laps of the top 3 drivers in the dictionary
        for i, piloto in enumerate(df_best_laps["Driver"]):
            vueltas_pilotos[piloto] = laps.pick_driver(piloto).pick_lap(df_best_laps.iloc[i]["LapNumber"])
    else:
        # Get laps each driver from the dictionary
        for piloto in vueltas_pilotos_dict.keys():
            vuelta_seleccionada = laps.loc[laps["Driver"] == piloto].loc[laps["LapNumber"] == vueltas_pilotos_dict[piloto][0]]
            if vuelta_seleccionada.empty:
                send_error_message(status_code=404, title="Laps not enabled", message=f'No exists {piloto} laps in {session.event["EventName"]} {session.event.year} {session.name}')
            vueltas_pilotos[piloto] = vuelta_seleccionada

    # Check if laps are valid
    if not vueltas_pilotos:
        raise ValueError("No valid laps found for analysis.")

    # Keep laps in a data frame
    df_vueltas = pd.concat(vueltas_pilotos).reset_index()

    # Driver mapping for color indices
    team_colors = get_team_colors(df_vueltas[["Team", "Driver"]].drop_duplicates(), session)

    # Check if there are duplicate colors
    conteo = Counter(team_colors)
    for color_contado, count in conteo.items():
        if count > 1:
            for i, color in reversed(list(enumerate(team_colors))):
                if color == color_contado:
                    team_colors[i] = mcolors.to_rgba(color_contado, alpha=0.5)
                    break

    fig, ax = plt.subplots(7, 1, figsize=(6, 12), gridspec_kw={'height_ratios': [0.8, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]})

    keys = list(vueltas_pilotos.keys())

    # Show telemetry of each lap driver 
    for i, piloto in enumerate(keys):

        color = team_colors[i]
        tel_lap = vueltas_pilotos[keys[i]].get_telemetry()

        # Get telemetry data for the reference lap and the compared lap
        delta_time, ref_tel, compare_tel = get_delta_time(vueltas_pilotos[keys[0]], vueltas_pilotos[keys[i]])

        # Show speed vs distance
        ax[0].plot(ref_tel["Distance"] if i == 0 else compare_tel["Distance"], ref_tel["Speed"] if i == 0 else compare_tel["Speed"], color=color, label=keys[i])

        # Show delta time
        ax[1].plot(ref_tel['Distance'], delta_time, '--', color=color)

        # Show telemetry throttle
        ax[2].stairs(tel_lap['Throttle'], color=color, label=keys[i])

        # Show telemetry brake
        ax[3].stairs(tel_lap['Brake'], color=color, label=keys[i])

        # Show telemetry RPM
        ax[4].plot(tel_lap['RPM'], color=color, label=keys[i])

        # Show telemetry nGear
        ax[5].stairs(tel_lap['nGear'], color=color, label=keys[i])

        # Show telemetry DRS
        ax[6].stairs(tel_lap['DRS'], color=color, label=keys[i])

    # Enumerate cornes in speed vs distance plot
    v_max = vueltas_pilotos[keys[0]].get_telemetry()['Speed'].max()
    v_min = vueltas_pilotos[keys[0]].get_telemetry()['Speed'].min()
    circuit_info = session.get_circuit_info()

    ax[0].vlines(x=circuit_info.corners['Distance'], ymin=v_min-20, ymax=v_max+20, linestyles='dotted', colors='grey')
    for _, corner in circuit_info.corners.iterrows():
        txt = f'{corner["Number"]}{corner["Letter"]}'
        ax[0].text(corner['Distance'], v_min-20, txt,
                va='center_baseline', ha='center', size='small')

    # Put details plotts
    y_labels = ["Speed", "Delta", "Throttle", "Brake", "RPM", "nGear", "DRS"]
    for i in range(len(ax)):
        if i == 0:
            ax[i].legend(loc='upper right', fontsize='small')
            ax[i].set_xlabel("Track distance")
        ax[i].set_ylabel(y_labels[i])
        ax[i].xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    plt.suptitle(f'{session.event["EventName"]} {session.event.year} {session.name}\n'
                f'Lap time comparative of {", ".join(keys)}')
    plt.tight_layout()