import matplotlib.pyplot as plt
import pandas as pd
from timple.timedelta import strftimedelta

import fastf1.plotting
from fastf1.core import Laps

def qualy_results(session):
    drivers = pd.unique(session.laps['Driver'])
    print(drivers)

    list_fastest_laps = list()
    for drv in drivers:
        drvs_fastest_lap = session.laps.pick_driver(drv).pick_fastest()
        list_fastest_laps.append(drvs_fastest_lap)
    fastest_laps = Laps(list_fastest_laps) \
        .sort_values(by='LapTime') \
        .reset_index(drop=True)

    pole_lap = fastest_laps.pick_fastest()
    fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']

    print(fastest_laps[['Driver', 'LapTime', 'LapTimeDelta']])

    team_colors = list()
    for index, lap in fastest_laps.iterlaps():
        color = fastf1.plotting.get_team_color(lap['Team'], session=session)
        team_colors.append(color)

    fig, ax = plt.subplots()
    ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(fastest_laps.index)
    ax.set_yticklabels(fastest_laps['Driver'])

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

    plt.title(f"{session.event['EventName']} {session.event.year} Qualifying\n"
                f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")

    plt.show()