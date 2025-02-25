import fastf1.plotting
import fastf1

def get_session(year, round=None, session=None, test_number=None, session_number=None):
    try:
        if session is not None and round is not None:
            session = fastf1.get_session(year, round, session)
        elif test_number is not None and session_number is not None:
            session = fastf1.get_testing_session(year, test_number, session_number)
    except Exception as e:
        return None
    return session

def get_team_colors(df, session):
    team_colors = list()
    for team in df['Team'].values:
        color = fastf1.plotting.get_team_color(team, session=session)
        team_colors.append(color)
    return team_colors
