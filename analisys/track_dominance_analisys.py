import numpy as np
import pandas as pd
import fastf1

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
from matplotlib.collections import LineCollection

from collections import Counter

from utils._init_ import get_session, try_get_session_laps, send_error_message, get_team_colors, get_delta_time

def track_dominance_analisys(type_event:str, year: int, event: int, session: str, vueltas_pilotos_dict: dict):
    """
    Analyzes the track dominance of the top 3 drivers in a specific session.
    
    Parameters:
    type_event (str): The type of event ('official', 'pretest').
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    vueltas_pilotos (dict): A dictionary with the laps of each driver.
    """
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme='fastf1')

    session = get_session(type_event, year, event, session)
    laps = try_get_session_laps(session)
    laps["LapTime"] = pd.to_timedelta(laps["LapTime"])

    vueltas_pilotos = dict()

    # Check if the user has selected laps for the drivers
    if vueltas_pilotos_dict is None or len(vueltas_pilotos_dict) == 0:

        # Select the three best laps of the session
        df_laps_ordered = laps.sort_values(by="LapTime")
        df_best_laps = df_laps_ordered.head(4)

        # Keep only the laps of the top 3 drivers in the dictionary
        for i, piloto in enumerate(df_best_laps["Driver"]):
            vueltas_pilotos[piloto] = laps.pick_driver(piloto).pick_lap(df_best_laps.iloc[i]["LapNumber"])
    else:

        # Select the laps of the drivers specified by the user
        for piloto, lap_number in vueltas_pilotos_dict.items():

            # Check if user has selected a lap number for the driver
            if not piloto or not lap_number:
                send_error_message(
                    status_code=400,
                    title="Parameter Error",
                    message=f'You must specify a driver and a lap number for session {session.event["EventName"]} {session.event.year} {session.name}'
                )

            vuelta_seleccionada = laps.pick_driver(piloto).pick_lap(lap_number[0])

            # Check if the lap exists
            if vuelta_seleccionada.empty:
                send_error_message(
                    status_code=404,
                    title="No Laps Available",
                    message=f'No laps exist for {piloto} in the session {session.event["EventName"]} {session.event.year} {session.name}'
                )
            vueltas_pilotos[piloto] = vuelta_seleccionada

    # Check if there are laps correctly selected
    if not vueltas_pilotos:
        send_error_message(
            status_code=404,
            title="No Laps Available",
            message=f'No laps exist for the selected drivers in the session {session.event["EventName"]} {session.event.year} {session.name}'
        )

    # Order descending the dictionary from the fastest lap to the slowest lap
    vueltas_pilotos = dict(sorted(vueltas_pilotos.items(), key=lambda item: 
                            item[1]['LapTime'].max() if isinstance(item[1], pd.DataFrame) else item[1]['LapTime']))

    # Keep it in a DataFrame
    df_vueltas = pd.concat(vueltas_pilotos).reset_index()
    drivers = df_vueltas["Driver"].drop_duplicates().to_list()

    # ---   COMPARATIVE BY DELTA TIME   ---

    # First we take the telemetry of the fastest lap of the session what it is keep it 
    # in the first position in the dictinary to take time deltas of the rest of the laps
    df_delta_per_point = pd.DataFrame()
    ref_lap = laps.pick_driver(df_vueltas.iloc[0]["Driver"]).pick_lap(df_vueltas.iloc[0]["LapNumber"])
    for i, piloto in enumerate(drivers):

        # Take the delta time of the lap
        delta_time, ref_tel, compare_tel = get_delta_time(
            ref_lap,
            laps.pick_driver(df_vueltas.iloc[i]["Driver"]).pick_lap(df_vueltas.iloc[i]["LapNumber"])
        )

        # Take the delta time in a dataframe column
        df_delta_per_point[i] = delta_time

    # Now we take the smallest delta time of each row to get the leader driver in this point
    # Why we do this? Because, each column represent the delta time of the lap of the driver

    #Driver1|Driver2|Driver3|
    #   0   |   1   |   2   |

    #   V
    #  0.0  |  0.1  |  0.2  |

    #           V
    #  0.1  |  0.0  |  0.3  |

    #                   V
    #  0.2  |  0.2  |  0.0  |

    # Now we have the leading driver in each point of the lap to show it in the graph
    leading_driver_per_point = list()
    for i, row in df_delta_per_point.iterrows():
        leading_driver_per_point.append(row.idxmin())

    # Now we take the telemetry of the fastest lap to show the track
    tel_fastest_lap = ref_lap.get_telemetry()
    x = np.array(tel_fastest_lap['X'].values)
    y = np.array(tel_fastest_lap['Y'].values)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Get the team colors of the drivers
    team_colors = get_team_colors(df_vueltas[["Team", "Driver"]].drop_duplicates(), session)

    # How I don't know if the drivers are in the same team or not, I have to check if the color is repeated
    # and if it is repeated, I have to set the color to transparent
    conteo = Counter(team_colors)
    for color_contado, count in conteo.items():
        if count > 1:
            for i, color in reversed(list(enumerate(team_colors))):
                if color == color_contado:
                    team_colors[i] = mcolors.to_rgba(color_contado, alpha=0.5)
                    break

    # Show the track with the colors of the drivers and the leading driver in each point
    cmap = ListedColormap(team_colors)
    lc_comp = LineCollection(segments, cmap=cmap, norm=plt.Normalize(-0.5, len(team_colors) - 0.5))
    lc_comp.set_array(leading_driver_per_point)
    lc_comp.set_linewidth(3)

    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    # Plot the leyend of the drivers colors
    cbar = plt.colorbar(
        mappable=lc_comp,
        label="Drivers",
        boundaries=np.arange(0, len(team_colors) + 1) - 0.5,
        ticks=np.arange(len(team_colors)),
    )

    # Set driver name in the color bar
    drivers_map = {driver: i for i, driver in enumerate(df_vueltas["Driver"].drop_duplicates())}
    cbar.set_ticklabels(drivers_map.keys())

    plt.suptitle(f'{session.event["EventName"]} {session.event.year} {session.name}\n' +
                    f'Fastest laps comparative {", ".join(df_vueltas["Driver"].drop_duplicates().to_list())}')
    plt.tight_layout()