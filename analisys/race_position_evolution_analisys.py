import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import fastf1.plotting

import numpy as np
import pandas as pd

from utils._init_ import get_session, send_error_message, try_get_session_laps

def create_checkered_flag(row=4, columns=6):
    """
    Create a checked flag to show later in fig with
    a specific number of rows and columns

    Parameters:
    row (int) = 4 def: Number rows of checked flag
    columns (int) = 6 def: Number columns of checked flag
    return: checked flag.
    """
    # Crear una matriz para la bandera a cuadros
    flag = np.zeros((row, columns))
    
    # Llenar con patrón de ajedrez (1=negro, 0=blanco)
    for i in range(row):
        for j in range(columns):
            if (i + j) % 2 == 0:
                flag[i, j] = 1
    
    return flag

def show_checked_flag(ax, last_position, last_lap_number):
    """
    Show checked flag by drivers what have finished the race

    Parameters:
    ax (axis): y axis
    last_position (int): The last position record in the last lap
    last_lap (int): LapNumber of the last lap of the race
    """
    checkered_flag = create_checkered_flag()
    checkered_image = OffsetImage(checkered_flag, cmap='binary', zoom=2)

    ab = AnnotationBbox(checkered_image, (last_lap_number, last_position), frameon=False)
    ax.add_artist(ab)
    plt.scatter(
        x=last_lap_number, 
        y=last_position, 
        marker='s', 
        s=0, 
        edgecolors='none', 
    )

def show_compound_used_during_race(ax, session, drv, drv_laps, drivers_retired):
    """
    Show every compound used since first lap counting
    with the new compound tyres put it in pit stops
    in the middle of the race

    Parameters:
    ax (axis): y axis
    session (obj): object with data about the session
    drv (string): driver
    drivers_retired (list): retired drivers list of the race
    """
    # Get first lap of the race
    first_lap_df = drv_laps[drv_laps['LapNumber'] == 1].iloc[0]

    # Plot compound used in the start of the race
    compound = str(first_lap_df['Compound'])
    first_compound_color = fastf1.plotting.get_compound_color(compound, session)
    ax.scatter(
        x=first_lap_df['LapNumber'],
        y=first_lap_df['Position'],
        c=first_compound_color,
        edgecolors='#000000',
        s=80,
        zorder=3
    )

    # Check the driver is not retired
    if drv not in drivers_retired:
        # Get pit in laps and pit out laps
        box_laps = drv_laps.pick_box_laps(which='both').reset_index()

        # From that we take only pit in laps
        box_in_laps = box_laps[box_laps["PitInTime"].notna()]

        # Each pit in laps I show LapNumber, Position and 
        # compound put it in pit out lap
        for idx, box_lap in box_in_laps.iterrows():
            compound = str(box_laps.iloc[idx+1]["Compound"])
            compound_color = fastf1.plotting.get_compound_color(compound, session)
            ax.scatter(
                x=box_lap['LapNumber'],
                y=box_lap['Position'],
                c=compound_color,
                edgecolors='#000000',
                s=80,
                zorder=3
            )

def get_race_control_events(session):

    flags = ["RED","DOUBLE YELLOW","YELLOW"]
    flags_showed = list(set(session.race_control_messages["Flag"].tolist())&set(flags))

    safety_cars = ["SAFETY CAR", "VIRTUAL SAFETY CAR"]
    safety_cars_deployed = list()
    for type_safety in safety_cars:
        if "VIRTUAL" in type_safety:
            mask = session.race_control_messages["Message"].str.contains(r"SAFETY(?!.*VIRTUAL)", case=False, regex=True)
        else:
            mask = (session.race_control_messages["Message"].str.contains("SAFETY", case=False, regex=True) &
                ~session.race_control_messages["Message"].str.contains("VIRTUAL", case=False, regex=True))

        # Get safety laps
        safety_car_messages = session.race_control_messages[mask]
        if not safety_car_messages.empty:
            safety_cars_deployed.append(
                safety_cars[1] if type_safety == safety_cars[1] else safety_cars[2]
            )
    race_control_events_happened = flags_showed + safety_cars_deployed

    return race_control_events_happened

def show_race_control_events(session, ax):

    track_status_obj = {
        'RED': {
            'Label': 'Red flag',
            'Color': '#FF7F7F'
        },
        'DOUBLE YELLOW': {
            'Label': 'Double yellow',
            'Color': '#FFFECD'
        },
        'YELLOW': {
            'Label': 'Yellow flag',
            'Color': '#FFFACD'
        },
        'SAFETY CAR': {
            'Label': 'Safety car',
            'Color': '#FFD700',
        },
        'VIRTUAL SAFETY CAR': {
            'Label': 'Virtual safety car',
            'Color': '#B8860B'
        }
    }

    # Get every race control flag event in a list
    race_control_events_happened = get_race_control_events(session=session)

    # Get flags list
    flags = list(track_status_obj.keys())[0:3]
    for key, value in track_status_obj.items():

        # Check if the key is the track status
        if key in race_control_events_happened:

            # Get laps with the track status
            if key in flags:
                laps_track_status = session.race_control_messages[session.race_control_messages["Flag"] == key]
            else:
                if "VIRTUAL" in key:
                    laps_track_status = session.race_control_messages[session.race_control_messages["Message"].str.contains("VIRTUAL", case=False, regex=True)]
                else:
                    laps_track_status = session.race_control_messages[session.race_control_messages["Message"].str.contains("SAFETY CAR", case=False, regex=True)]

            # Group events in different momments of the session
            laps_track_status['diff'] = laps_track_status['Lap'].diff().fillna(1)
            laps_track_status['grupo'] = (laps_track_status['diff'] > 1).cumsum()
            grups = laps_track_status.groupby('grupo').agg({'Lap': ['min', 'max']})
            grups.columns = ['Start', 'End']
            print(grups)

            # Plot event in grahpic
            for idx, row in grups.iterrows():

                lap_start = float(row["Start"])
                lap_finish = float(row["End"])

                # Check if lap finish is the same like
                # lap start
                if lap_start == lap_finish:
                    lap_finish = lap_finish + 1

                # Check if array has only one row
                if len(grups) == 1:
                    label_track_status = value["Label"]
                else:

                    # Check if it is the first iteration
                    if idx == 0:
                        label_track_status = value["Label"]
                    else:
                        label_track_status = ""

                color = track_status_obj[key]["Color"]
                ax.axvspan(
                    xmin=lap_start, 
                    xmax=lap_finish, 
                    color=color, 
                    alpha=0.2, 
                    lw=0,
                    label=label_track_status,
                    )

def race_position_evolution_analisys(type_event:str, year: int, event: int, session: str):
    """
    Analyzes the race position evolution of the drivers in a race session.

    Parameters:
    year (int): The year of the race.
    event (int): The event number of the race.
    session (str): The session type ('R' and 'S').
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True, color_scheme='fastf1')

    # Check if the session is valid
    if (session != "R" and session != "S"): 
        send_error_message(status_code=400, title="Only races or sprint races", 
                    message="This plot is only available for races or sprint races")

    # Get the session
    session = get_session(type_event, year, event, session)

    # Get the laps data
    laps = try_get_session_laps(session=session, laps_not_wo_box=False)

    # Get drivers retired
    drivers_retired = session.results[session.results["Status"] == "Retired"]["Abbreviation"].tolist()

    # Get drivers saw checked flag
    drivers_saw_checked_flag = session.results[session.results["Time"].notna()]["Abbreviation"].tolist()

    fig, ax = plt.subplots(figsize=(9.5, 6))

    # Show laps in the plot
    driver_stints = {}
    drivers = session.results["Abbreviation"].tolist()
    for drv in drivers:
        # Get the laps for the driver
        drv_laps = laps.pick_drivers(drv)

        # Check if the driver has any laps
        if drv_laps.empty:
            continue

        # Get the style of the driver
        abb = drv_laps['Driver'].iloc[0]
        style = fastf1.plotting.get_driver_style(identifier=abb,
                                                style=['color', 'linestyle'],
                                                session=session)

        # Plot the laps of the driver
        ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
                **style, zorder=1)

        # Show compound used during race
        show_compound_used_during_race(
            ax=ax,
            session=session,
            drv=drv,
            drv_laps=drv_laps,
            drivers_retired=drivers_retired
        )

        # Check the driver saw checked flag
        if drv in drivers_saw_checked_flag:
            # Get last position record in the last lap
            last_position = int(drv_laps.iloc[len(drv_laps)-1]["Position"])
            # Get last lap number of the race
            last_lap_number = int(drv_laps.iloc[len(drv_laps)-1]["LapNumber"])
            show_checked_flag(
                ax=ax,
                last_position=last_position,
                last_lap_number=last_lap_number
            )

    # Show race control events during the race
    show_race_control_events(
        session=session,
        ax=ax
    )

    # Get final positions of drivers
    final_positions = {}
    for index, driver_result in session.results.iterrows():
        position = driver_result['Position'] if not pd.isna(driver_result['Position']) else len(session.results)
        final_positions[int(position)] = driver_result['Abbreviation']

    # Create custom badges for the Y-axis
    positions = range(1, len(session.results) + 1)
    y_labels = [f'{final_positions.get(pos, "")}' for pos in positions]

    # Configure the Y-axis with custom labels
    ax.set_yticks(positions)
    ax.set_yticklabels(y_labels)

    # Stablish left and right limits in xaxis
    last_lap = int(laps["LapNumber"].max())
    ax.set_xlim(left=0,right=last_lap+2)

    # Add labels and legend
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Position')
    ax.invert_yaxis()
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    # Invert Y-axis so position 1 is at the top
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(session.drivers)//2)

    plt.suptitle(f'{session.event["EventName"]} {session.event.year} {session.name} | Results')
    plt.tight_layout()