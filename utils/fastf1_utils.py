import fastf1.plotting
import fastf1

from utils._init_ import send_error_message

def get_session(year, round=None, session=None, test_number=None, session_number=None):
    if session is not None and round is not None:
            session = fastf1.get_session(year, round, session)
    elif test_number is not None and session_number is not None:
        session = fastf1.get_testing_session(year, test_number, session_number)
    return session

def get_team_colors(df, session):
    team_colors = list()
    for team in df['Team'].values:
        color = fastf1.plotting.get_team_color(team, session=session)
        team_colors.append(color)
    return team_colors

def try_get_session_laps(session):
    laps = None
    try:
        session.load()
        laps = session.laps
    except Exception as e:
        send_error_message(status_code=404, title="No hay vueltas disponibles", message=f"Los datos de la sesión {session.event["EventName"]} {session.event.year} {session.name} no existen o no se han podido cargar todavia")
    return laps