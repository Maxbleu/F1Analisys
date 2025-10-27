from .utils import send_error_message
import fastf1, pandas as pd, numpy as np

def get_session(type_event, year, event, session):
    try:
        if type_event == "official":
                session = fastf1.get_session(year, event, session)
        elif type_event == "pretest":
            session = fastf1.get_testing_session(year, event, session)
    except Exception as e:
        send_error_message(
            status_code=404, 
            title="Selected session does not exist", 
            message=f'The session {year}/{event}/{session} does not exist or has not been loaded yet.'
        )
    return session

def get_team_colors(df, session):
    team_colors = list()
    for team in df['Team'].values:
        color = fastf1.plotting.get_team_color(team, session=session)
        team_colors.append(color)
    return team_colors

def try_get_session_laps(session, laps_not_deleted=True, laps_not_wo_box=True):
    laps = None
    try:
        session.load()
        if laps_not_deleted & laps_not_wo_box:
            laps = session.laps.pick_not_deleted().pick_wo_box()
        elif laps_not_deleted:
            laps = session.laps.pick_not_deleted()
        elif laps_not_wo_box:
            laps = session.laps.pick_wo_box()
        else:
            laps = session.laps.copy()
            laps.loc[:, "LapTime"] = pd.to_timedelta(laps["LapTime"])
    except Exception as e:
        send_error_message(
            status_code=404, 
            title="No laps available", 
            message=f'The data for the session {session.event["EventName"]} {session.event.year} {session.name} does not exist or has not been loaded yet.'
        )
    return laps

def get_delta_time(reference_lap, compare_lap):
    ref = reference_lap.get_car_data(interpolate_edges=True).add_distance()
    comp = compare_lap.get_car_data(interpolate_edges=True).add_distance()

    def mini_pro(stream):
        dstream_start = stream[1] - stream[0]
        dstream_end = stream[-1] - stream[-2]
        return np.concatenate(
            [[stream[0] - dstream_start], stream, [stream[-1] + dstream_end]]
        )

    ltime = mini_pro(comp['Time'].dt.total_seconds().to_numpy())
    multiplier = ref.Distance.iat[-1]/comp.Distance.iat[-1]
    ldistance = mini_pro(comp['Distance'].to_numpy())*multiplier
    lap_time = np.interp(ref['Distance'], ldistance, ltime)

    delta = lap_time - ref['Time'].dt.total_seconds()

    return delta, ref, comp