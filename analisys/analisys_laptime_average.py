import fastf1

import matplotlib.pyplot as plt

import pandas as pd

def analisys_laptime_average(session):

    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False,
                            color_scheme='fastf1')

    session.laps["LapTime"] = pd.to_timedelta(session.laps["LapTime"])

    #   CREAR EL DATA FRAME
    df_valid_laps = session.laps[session.laps["Deleted"] == False]

    drivers = session.laps['Driver'].unique()
    teams = []
    for driver in drivers:
        team_name = session.results.loc[session.results['Abbreviation'] == driver, 'TeamName'][0]
        teams.append(team_name)

    df_median_lap_time_drivers = pd.DataFrame({
        'Driver' : drivers, 
        'Team' : teams,
    })

    #   OBTENER LA MEDIA POR VUELTA DE CADA PILOTO
    median_lap_time_drivers = []
    for driver in drivers:
        driver_laps = df_valid_laps[session.laps['Driver'] == driver]
        median_driver_lap_time = driver_laps["LapTime"].median()
        median_driver_lap_time = median_driver_lap_time.total_seconds()
        median_lap_time_drivers.append(median_driver_lap_time)

    #   OBTENEMOS LA DIFERENCIA FRENTE AL PRIMERO
    diff_median_lap_time_drivers = []
    best_median_lap_time = min(median_lap_time_drivers)
    for median_lap_time in median_lap_time_drivers:
        diff_median_lap_time = median_lap_time - best_median_lap_time
        diff_median_lap_time_drivers.append(diff_median_lap_time)

    df_median_lap_time_drivers["MedianLapTime"] = diff_median_lap_time_drivers

    #   CONFIGURAMOS EL DATA FRAME PARA QUE SE MUESTRE LA DIFERENCIA FRENTE AL PRIMERO
    df_median_lap_time_drivers = df_median_lap_time_drivers.sort_values(by="MedianLapTime")
    df_median_lap_time_drivers.dropna(inplace=True, ignore_index=True)

    #   OBTENEMOS LOS COLORES DEL EQUIPO
    team_colors = list()
    for team in df_median_lap_time_drivers['Team'].values:
        color = fastf1.plotting.get_team_color(team, session=session)
        team_colors.append(color)

    #   CONFIGURAMOS LA GRAFICA
    fig, ax = plt.subplots(figsize=(11, 7))
    bars = ax.barh(df_median_lap_time_drivers.index, df_median_lap_time_drivers["MedianLapTime"], color=team_colors)
    ax.set_yticks(df_median_lap_time_drivers.index)
    ax.set_yticklabels(df_median_lap_time_drivers["Driver"])

    ax.invert_yaxis()
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    plt.title(f"AVERANGE LAP TIME DRIVERS {session.event['EventName']} {session.event.year}")

    for bar in bars:
        width = bar.get_width()
        if(width > 0):
            cadena = f'{width:.2f}'
        else:
            cadena = 'Fastest'

        ax.text(width+0.01, bar.get_y() + bar.get_height()/2, cadena, 
        va='center', ha='left', color='white')

    plt.show()