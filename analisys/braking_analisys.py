import fastf1
import fastf1.plotting as plotting
import fastf1.utils as utils

import pandas as pd
import matplotlib.pyplot as plt

from utils._init_ import get_team_colors, get_session, try_get_session_laps

def braking_analisys(year:int, round:int, session:str, test_number:int, session_number:int):
    """
    Analyzes the braking of the drivers in a specific session.

    Parameters:
    year (int): The year of the race.
    round (int): The round number of the race.
    session (str): The session type (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R').
    test_number (int): The test number of the session.
    session_number (int): The session number of the session.
    """

    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                        color_scheme='fastf1')

    session = get_session(year, round, session, test_number, session_number)
    laps = try_get_session_laps(session=session)

    print(laps.get_telemetry().columns)