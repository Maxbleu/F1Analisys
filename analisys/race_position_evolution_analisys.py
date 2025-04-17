import matplotlib.pyplot as plt
import fastf1.plotting

from utils._init_ import get_session, send_error_message, try_get_session_laps

def race_position_evolution_analisys(type_event:str, year: int, event: int, session: str):
    """
    Analyzes the race position evolution of the drivers in a race session.

    Parameters:
    year (int): The year of the race.
    event (int): The event number of the race.
    session (str): The session type ('R' and 'S').
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                            color_scheme='fastf1')

    # Check if the session is valid
    if (session != "R" and session != "S"): 
        send_error_message(status_code=400, title="Only races or sprint races", 
                    message="This plot is only available for races or sprint races")

    # Get the session
    session = get_session(type_event, year, event, session)

    # Get the laps data
    laps = try_get_session_laps(session=session)

    fig, ax = plt.subplots(figsize=(10.0, 6))

    # Show laps in the plot
    driver_stints = {}
    for drv in session.drivers:
        # Get the laps for the driver
        drv_laps = laps.pick_driver(drv)

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

        # Plot compound use in the first lap of each stint
        driver_stints[drv] = drv_laps["Stint"].nunique()
        total_stints = driver_stints[drv]
        for stint in range(1, total_stints + 1):
            laps_stints = drv_laps[drv_laps['Stint'] == stint]
            first_stint_lap = laps_stints.iloc[0]
            compound_color = fastf1.plotting.get_compound_color(first_stint_lap['Compound'], session)
            ax.scatter(
                x=first_stint_lap['LapNumber'],
                y=first_stint_lap['Position'],
                c=compound_color,
                edgecolors='#000000',
                s=80,
                zorder=3
            )

    # Add labels and legend
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Position')
    ax.invert_yaxis()  

    # Invert Y-axis so position 1 is at the top
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(session.drivers)//2)

    plt.suptitle(f"{session.event['EventName']} {session.event.year} {session.name} | Results")
    plt.tight_layout()