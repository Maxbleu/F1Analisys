import matplotlib.pyplot as plt

import fastf1.plotting as f1_plotting
from app.utils import get_session, send_error_message, try_get_session_laps

import numpy as np
import pandas as pd

def show_drivers(y_positions, y_labels, ax, label):
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels)
    ax.set_ylabel(label)

def optimal_lap_impact_analisys(type_event:str, year: int, event: int, session: str):
    """
    Analizes the impact of optimal lap on qualy results.

    Parameters:
    type_event (str): The type of event ('official', 'pretest').
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    """

    f1_plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True, color_scheme='fastf1')

    if (session != "Q" and session != "SS" and session != "SQ"): 
        send_error_message(status_code=400, title="Only qualy, sprint qualy and sprint shootout", 
                    message="This plot is only available for qualy or sprint qualy and sprint shootout sessions")

    session = get_session(type_event, year, event, session)
    laps = try_get_session_laps(session=session)

    # Get results of qualy
    df_qualy_results = session.results[["Abbreviation", "Position"]]

    laps["Sector1Time"] = laps["Sector1Time"].dt.total_seconds()
    laps["Sector2Time"] = laps["Sector2Time"].dt.total_seconds()
    laps["Sector3Time"] = laps["Sector3Time"].dt.total_seconds()

    # Get optimal laps
    df_optimal_laps = pd.DataFrame(columns=["Driver","OptimalPosition", "OptimalTime"])
    drivers = df_qualy_results["Abbreviation"].tolist()
    for drv in drivers:
        driver_laps = laps.pick_drivers(drv)
        if driver_laps.empty:
            new_row = {
                "Driver": drv,
                "OptimalTime": float(1000.0)
            }
        else:
            sector1 = float(driver_laps[["Sector1Time"]].min())
            sector2 = float(driver_laps[["Sector2Time"]].min())
            sector3 = float(driver_laps[["Sector3Time"]].min())
            optimal_lap_time = sector1 + sector2 + sector3
            new_row = {
                "Driver": drv,
                "OptimalTime": optimal_lap_time
            }
        df_optimal_laps = pd.concat([df_optimal_laps, pd.DataFrame([new_row])], ignore_index=True)

    # Sort optimal laps by optimal time
    df_optimal_laps["OptimalPosition"] = df_optimal_laps["OptimalTime"].rank(method="min").astype(int)

    # Show plot
    fig, ax = plt.subplots()

    left_x = 0.00
    right_x = 1.00
    label_lengend_show = list()
    num_drivers = len(drivers)
    y_positions = np.linspace(0.95, 0.05, num_drivers)

    df_qualy_results = df_qualy_results.sort_values("Position")
    df_optimal_laps = df_optimal_laps.sort_values("OptimalPosition")

    # Crear un mapeo más seguro
    for driver in drivers:
        qual_pos = df_qualy_results[df_qualy_results["Abbreviation"] == driver]["Position"].iloc[0]
        opti_pos = df_optimal_laps[df_optimal_laps["Driver"] == driver]["OptimalPosition"].iloc[0]
        
        start_y = y_positions[int(qual_pos)-1]
        end_y = y_positions[int(opti_pos)-1]
        
        x_curve = np.linspace(left_x+0.05, right_x-0.05, 100)
        y_curve = start_y + (end_y - start_y) * (1 - np.cos(np.pi * (x_curve - left_x - 0.05) / (right_x - left_x - 0.1))) / 2
        
        if opti_pos < qual_pos:
            line_color = '#00FF00'
            label = "gain" if "gain" not in label_lengend_show else ""
            alpha = 0.7
        elif opti_pos > qual_pos:
            line_color = '#FF4444'
            label = "lost" if "lost" not in label_lengend_show else ""
            alpha = 0.7
        else:
            line_color = '#4444FF' 
            label = "hold" if "hold" not in label_lengend_show else ""
            alpha = 0.5

        if label != "" and label not in label_lengend_show: label_lengend_show.append(label)

        ax.plot(x_curve, y_curve, color=line_color, linewidth=2, alpha=alpha, label=label)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Show qualy result
    show_drivers(
        y_positions=y_positions,
        y_labels=df_qualy_results.sort_values("Position")["Abbreviation"].tolist(),
        ax=ax,
        label="Qualy result"
    )

    # Show optimal qualy result
    ax_right = ax.twinx()
    show_drivers(
        y_positions=y_positions,
        y_labels=df_optimal_laps.sort_values("OptimalPosition")["Driver"].tolist(),
        ax=ax_right,
        label="Optimal qualy result"
    )

    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
    ax.set_axisbelow(True)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(session.drivers)//2)
    plt.suptitle(f'{session.event["EventName"]} {session.event.year} {session.name}\n Optimal qualy lap results')
    plt.tight_layout()