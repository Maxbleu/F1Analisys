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

def show_compound_used_during_race(ax, session, drv):
    """
    Show every compound used since first lap counting
    with the new compound tyres put it in pit stops
    in the middle of the race

    Parameters:
    ax (axis): y axis
    session (obj): object with data about the session
    drv (string): driver
    """

    # Get drivers retired
    drivers_retired = session.results[session.results["Status"] == "Retired"]["Abbreviation"].tolist()
    drv_laps = session.laps.pick_drivers(drv)

    try:
        # Plot compound used in the start of the race
        compound = str(drv_laps[drv_laps['LapNumber'] == 1].iloc[0]["Compound"])
        first_compound = fastf1.plotting.get_compound_color(compound, session)

        ax.scatter(
            x=0,
            y=int(session.results[session.results["Abbreviation"] == drv]["GridPosition"]),
            c=first_compound,
            edgecolors='#000000',
            s=80,
            zorder=3
        )
    except Exception as e:
        ...

    # Check the driver is not retired
    if drv not in drivers_retired:
        # Get pit in laps and pit out laps
        box_laps = drv_laps.pick_box_laps(which='both').reset_index()

        # From that we take only pit in laps
        box_laps["TrackStatus"] = box_laps['TrackStatus'].astype(int)
        box_in_laps = box_laps.loc[box_laps["PitInTime"].notna() & box_laps["TrackStatus"] == 1]

        # Each pit in laps I show LapNumber, Position and 
        # compound put it in pit out lap
        for idx, box_lap in box_in_laps.iterrows():
            try:
                compound = str(box_laps.iloc[idx]["Compound"])
                compound_color = fastf1.plotting.get_compound_color(compound, session)
                ax.scatter(
                    x=box_lap['LapNumber'],
                    y=box_lap['Position'],
                    c=compound_color,
                    edgecolors='#000000',
                    s=80,
                    zorder=3
                )
            except Exception as e:
                continue

def get_track_status_color(msg):
    color = "#00FF00FF"
    if msg == "Yellow":
        color = '#FFD700'
    elif msg == "Red":
        color = "#FF7070"
    elif msg == "SCDeployed":
        color = "#FFE760"
    elif msg == "VSCDeployed":
        color = '#B8860B'
    return color

def get_track_status(session):
    track_status = session.track_status
    track_status = track_status[track_status["Message"] != "VSCEnding"]

    track_status['Color'] = track_status["Message"].apply(get_track_status_color)

    track_status['NextTime'] = track_status['Time'].shift(-1)
    track_status['NextMessage'] = track_status['Message'].shift(-1)
    track_status['LapStartEvent'] = 0
    track_status['LapFinishEvent'] = 0

    driver_laps = session.laps
    for status_idx in track_status.index:
        status_row = track_status.loc[status_idx]
        if pd.notna(status_row['NextTime']):
            mask = (status_row["Time"] <= driver_laps["Time"]) & \
                    (driver_laps["Time"] <= status_row["NextTime"])
            laps_in_period = driver_laps[mask]
            laps_in_period["LapNumber"] = laps_in_period["LapNumber"].astype("int")
            if not laps_in_period.empty:
                track_status.loc[status_idx, 'LapStartEvent'] = laps_in_period['LapNumber'].min()
                track_status.loc[status_idx, 'LapFinishEvent'] = laps_in_period['LapNumber'].max()+1 if int(laps_in_period['LapNumber'].max()) == int(laps_in_period['LapNumber'].min()) else laps_in_period['LapNumber'].max()
    track_status = track_status.loc[(track_status['LapStartEvent'] != 0) | (track_status['LapFinishEvent'] != 0)]
    return track_status

def show_race_control_events(session, ax):

    events = list()
    track_status = get_track_status(session=session)
    for idx, row in track_status.iterrows():
        ax.axvspan(
            xmin=row["LapStartEvent"], 
            xmax=row["LapFinishEvent"], 
            color=row["Color"], 
            alpha= 0.2 if row["Message"] != "AllClear" else 0.0, 
            lw=0,
            label= row['Message'] if (row['Message'] not in events) & (row["Message"] != "AllClear") else "",
            )
        if row['Message'] not in events: events.append(row['Message'])

def show_starting_grid(session, ax):

    df = session.results[["Abbreviation", "GridPosition"]]
    position_drivers = dict(zip(df['GridPosition'], df['Abbreviation']))
    show_drivers(session=session, position_drivers=position_drivers, ax=ax)

def show_final_positions(session, ax):
    positions = {}
    for index, driver_result in session.results.iterrows():
        position = driver_result["Position"] if not pd.isna(driver_result["Position"]) else len(session.results)
        positions[int(position)] = driver_result['Abbreviation']
    show_drivers(session=session, position_drivers=positions, ax=ax)

def show_drivers(session, position_drivers, ax):
    # Create custom badges for the Y-axis
    y_labels = [position_drivers.get(pos, "") for pos in range(1, len(session.results)+1)]
    positions = range(1, len(session.results) + 1)

    # Configure the Y-axis with custom labels
    ax.set_yticks(positions)
    ax.set_yticklabels(y_labels)

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

    # Get drivers saw checked flag
    drivers_saw_checked_flag = session.results[session.results["Time"].notna()]["Abbreviation"].tolist()

    fig, ax = plt.subplots(figsize=(9.5, 6))

    # Show laps in the plot
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

        # Indicate grid position
        start_row = pd.DataFrame([{
            'LapNumber': 0,
            'Position': int(session.results[session.results["Abbreviation"] == abb]["GridPosition"].iloc[0]),
        }])

        # Indicate last position with race finishers and retires drivers
        last_row = pd.DataFrame([{
            "LapNumber": drv_laps["LapNumber"].max() + 1,
            "Position": int(session.results.loc[session.results["Abbreviation"] == abb, "Position"].iloc[0])
        }])

        drv_laps = pd.concat([start_row, last_row, drv_laps[["LapNumber", "Position"]]], ignore_index=True)
        drv_laps = drv_laps.sort_values("LapNumber").reset_index(drop=True)

        # Plot the laps of the driver
        ax.plot(drv_laps['LapNumber'], drv_laps['Position'], **style, zorder=1)

        # Show compound used during race
        show_compound_used_during_race(
            ax=ax,
            session=session,
            drv=drv
        )

        # Check the driver saw checked flag
        if drv in drivers_saw_checked_flag:
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

    show_starting_grid(session=session, ax=ax)

    ax1 = ax.twinx()
    ax1.set_ylim(ax.get_ylim())
    ax1.invert_yaxis()

    show_final_positions(session=session, ax=ax1)

    # Stablish left and right limits in xaxis
    last_lap = int(laps["LapNumber"].max())
    ax.set_xlim(left=-1,right=last_lap+2)

    # Add labels and legend
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Position')
    ax.invert_yaxis()
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    # Invert Y-axis so position 1 is at the top
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(session.drivers)//2)

    plt.suptitle(f'{session.event["EventName"]} {session.event.year} {session.name} | Results')
    plt.tight_layout()