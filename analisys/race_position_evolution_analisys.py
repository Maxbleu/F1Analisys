import matplotlib.pyplot as plt

import fastf1.plotting

import pandas as pd

from utils._init_ import get_session, send_error_message, try_get_session_laps

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

    fig, ax = plt.subplots(figsize=(10.0, 6))

    # Show laps in the plot
    driver_stints = {}
    drivers = session.drivers
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
                label=abb, **style, zorder=1)

        # Get box laps
        box_laps = laps.pick_drivers(drv).pick_box_laps(which='out')

        # Get first lap of the race
        first_lap_df = drv_laps[drv_laps['LapNumber'] == 1].copy()

        # Concatenar verticalmente (si necesitas ambos juntos)
        combined_laps = pd.concat([first_lap_df, box_laps], ignore_index=True)

        # Plot compound use in the first lap of each stint
        for index, row in combined_laps.iterrows():
            compound_color = fastf1.plotting.get_compound_color(row['Compound'], session)
            ax.scatter(
                x=row['LapNumber'],
                y=row['Position'],
                c=compound_color,
                edgecolors='#000000',
                s=80,
                zorder=3
            )

    # Check if race was clean
    # 2 = Yellow Flag
    # 4 = Safety Car
    # 5 = Red Flag
    # 6 = Virtual Safety Car deployed
    track_status = laps["TrackStatus"].unique().tolist()
    track_status_color = {
        '2': '#FFFACD',
        '4': '#FFD700',
        '5': '#FF7F7F',
        '6': '#B8860B'
    }
    track_status_map = {
        '2': 'Yellow Flag',
        '4': 'Safety Car',
        '5': 'Red Flag',
        '6': 'Virtual Safety Car'
    }
    if ('2' in track_status) or ('4' in track_status) or ('5' in track_status) or ('6' in track_status):
        for key, value in track_status_color.items():

            # Check if the key is the track status
            if key in track_status:

                # Get laps with the track status
                laps_track_status = laps.loc[laps['TrackStatus'] == key]

                # Group events in different momments of the session
                laps_track_status['diff'] = laps_track_status['LapNumber'].diff().fillna(1)
                laps_track_status['grupo'] = (laps_track_status['diff'] > 1).cumsum()
                grups = laps_track_status.groupby('grupo').agg({'LapNumber': ['min', 'max', 'count']})
                grups.columns = ['Inicio', 'Fin', 'Duración']

                color = track_status_color[key]
                label_track_status = track_status_map[key]

                # Plot event in grahpic
                for _, row in grups.iterrows():
                    plt.axvspan(
                        row['Inicio'], 
                        row['Fin'], 
                        color=color, 
                        alpha=0.2, 
                        lw=0,
                        label=label_track_status
                        )

    # Get final positions of drivers
    final_positions = {}
    for index, driver_result in session.results.iterrows():
        position = driver_result['Position'] if not pd.isna(driver_result['Position']) else len(session.results)
        final_positions[int(position)] = driver_result['Abbreviation']

    # Create custom badges for the Y-axis
    positions = range(1, len(session.results) + 1)
    y_labels = [f'{pos}. {final_positions.get(pos, "")}' for pos in positions]

    # Configure the Y-axis with custom labels
    ax.set_yticks(positions)
    ax.set_yticklabels(y_labels)

    # Add labels and legend
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Position')
    ax.invert_yaxis()
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    # Invert Y-axis so position 1 is at the top
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(session.drivers)//2)

    plt.suptitle(f'{session.event["EventName"]} {session.event.year} {session.name} | Results')
    plt.tight_layout()