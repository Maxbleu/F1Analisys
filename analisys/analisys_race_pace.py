import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import seaborn as sns

import fastf1.plotting

from enums.process_state import ProcessState

def format_time_mmssmmm(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"

def analisys_race_pace(year: int, round: int, session: str):
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                        color_scheme='fastf1')

    try:
        session = fastf1.get_session(year, round, session)
    except Exception as e:
        return ProcessState.FAILED.name

    session.load()

    point_finishers = session.drivers[:10]
    
    laps = session.laps[session.laps["Deleted"] == False]
    laps.dropna(ignore_index=True)
    
    driver_laps = laps.pick_drivers(point_finishers).pick_quicklaps()
    driver_laps = driver_laps.reset_index()

    finishing_order = [session.get_driver(i)["Abbreviation"] for i in point_finishers]

    fig, ax = plt.subplots(figsize=(10, 5))

    driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

    sns.violinplot(data=driver_laps,
                x="Driver",
                y="LapTime(s)",
                hue="Driver",
                inner=None,
                density_norm="area",
                order=finishing_order,
                palette=fastf1.plotting.get_driver_color_mapping(session=session)
                )

    sns.swarmplot(data=driver_laps,
                x="Driver",
                y="LapTime(s)",
                order=finishing_order,
                hue="Compound",
                palette=fastf1.plotting.get_compound_mapping(session=session),
                hue_order=["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"],
                linewidth=0,
                size=4,
                )
    
    ax.set_xlabel("Driver")
    ax.set_ylabel("Lap Time (s)")
    plt.title(f"{session.event['EventName']} {session.event.year} {session.name} | Lap Pace Top 10")
    sns.despine(left=True, bottom=True)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: format_time_mmssmmm(x)))

    plt.tight_layout()

    return ProcessState.COMPLETED.name