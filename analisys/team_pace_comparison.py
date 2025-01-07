import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker

import fastf1.plotting

def format_time_mmssmmm(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"

def team_pace_comparison(session):
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False,
                            color_scheme='fastf1')

    laps = session.laps.pick_quicklaps()

    laps = laps[session.laps["Deleted"] == False]

    laps.dropna(ignore_index=True)

    transformed_laps = laps.copy()
    transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()

    team_order = (
        transformed_laps[["Team", "LapTime (s)"]]
        .groupby("Team")
        .median()["LapTime (s)"]
        .sort_values()
        .index
    )

    team_palette = {team: fastf1.plotting.get_team_color(team, session=session)
                    for team in team_order}

    fig, ax = plt.subplots(figsize=(15, 10))
    sns.boxplot(
        data=transformed_laps,
        x="Team",
        y="LapTime (s)",
        hue="Team",
        order=team_order,
        palette=team_palette,
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
    )

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: format_time_mmssmmm(x)))

    plt.title(f"TEAM COMPARISON {session.event['EventName']} {session.event.year}")

    plt.tight_layout()
    plt.show()