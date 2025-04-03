import numpy as np
import pandas as pd
import fastf1
import fastf1.plotting as plotting
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.collections import LineCollection
from utils._init_ import get_session, try_get_session_laps, send_error_message, get_team_colors

def frase_grafica_qualy(drivers):
    cadena = ""
    for i, driver in enumerate(drivers):
        if i > 0:
            cadena += " vs "
        cadena += f"{driver}"
    return cadena

def track_dominance_analisys(year: int, round: int, session: str, test_number: int, session_number: int, vueltas_pilotos_dict: dict):
    """
    Analyzes the track dominance of the top 3 drivers in a specific session.
    """
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme='fastf1')

    session = get_session(year, round, session, test_number, session_number)
    laps = try_get_session_laps(session)
    laps["LapTime"] = pd.to_timedelta(laps["LapTime"])

    vueltas_pilotos = dict()
    if len(vueltas_pilotos_dict) == 0:
        df_three_best_race_laps = laps.sort_values(by="LapTime").drop_duplicates(subset="Driver").reset_index(drop=True).head(3)
        for i, piloto in enumerate(df_three_best_race_laps["Driver"]):
            df_telemetria = df_three_best_race_laps.iloc[i].get_telemetry().reset_index(drop=True)
            df_telemetria = df_telemetria.assign(
                DriverNumber=df_three_best_race_laps.iloc[i]["DriverNumber"],
                Team=df_three_best_race_laps.iloc[i]["Team"],
                LapTime=df_three_best_race_laps.iloc[i]["LapTime"]
            )
            vueltas_pilotos[piloto] = df_telemetria
    else:
        for piloto, lap_number in vueltas_pilotos_dict.items():
            vuelta_seleccionada = laps[(laps["Driver"] == piloto) & (laps["LapNumber"] == lap_number)]
            if vuelta_seleccionada.empty:
                send_error_message(
                    status_code=404,
                    title="No hay vueltas disponibles",
                    message=f"No existen vueltas para {piloto} en la sesión {session.event['EventName']} {session.event.year} {session.name}"
                )
                continue  # Skip this driver if no lap is found
            df_telemetria = vuelta_seleccionada.iloc[0].get_telemetry().reset_index(drop=True)
            df_telemetria = df_telemetria.assign(
                DriverNumber=vuelta_seleccionada["DriverNumber"].iloc[0],
                Team=vuelta_seleccionada["Team"].iloc[0],
                LapTime=vuelta_seleccionada["LapTime"].iloc[0]
            )
            vueltas_pilotos[piloto] = df_telemetria

    if not vueltas_pilotos:
        raise ValueError("No valid laps found for analysis.")

    df_vueltas = pd.concat(vueltas_pilotos, names=["Driver"]).reset_index()

    tel_fastest_lap = df_vueltas.loc[df_vueltas["LapTime"] == df_vueltas["LapTime"].min()]
    x = np.array(tel_fastest_lap['X'].values)
    y = np.array(tel_fastest_lap['Y'].values)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Driver mapping for color indices
    team_colors = get_team_colors(df_vueltas[["Team", "Driver"]].drop_duplicates(), session)
    driver_map = {driver: i for i, driver in enumerate(df_vueltas["Driver"].drop_duplicates())}
    cmap = ListedColormap(team_colors)

    leading_driver_per_point = df_vueltas.groupby('RelativeDistance').apply(
        lambda x: driver_map.get(x.loc[x['Time'].idxmin(), 'Driver'], -1)
    ).to_numpy()

    lc_comp = LineCollection(segments, cmap=cmap, norm=plt.Normalize(-0.5, len(team_colors) - 0.5))
    lc_comp.set_array(leading_driver_per_point)
    lc_comp.set_linewidth(len(driver_map))

    plt.subplots()
    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    drivers = list(driver_map.keys())
    title = f"{session.event['EventName']} {session.event.year} {session.name}"
    if session.name == "Qualifying":
        title += f"\n{frase_grafica_qualy(drivers)}"
    else:
        title += " | Track dominance\nfastest laps"
    plt.suptitle(title)

    cbar = plt.colorbar(
        mappable=lc_comp,
        label="Drivers",
        boundaries=np.arange(0, len(team_colors) + 1) - 0.5,
        ticks=np.arange(len(team_colors)),
    )
    cbar.set_ticklabels(drivers)
    plt.tight_layout()