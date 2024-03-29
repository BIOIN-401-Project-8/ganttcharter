import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import SU, DateFormatter, WeekdayLocator

COLOR_TABLE = {
    "red berry": "#cc4125",
    "red": "#e06666",
    "orange": "#f6b26b",
    "yellow": "#ffd966",
    "green": "#93c47d",
    "cyan": "#76a5af",
    "cornflower blue": "#6d9eeb",
    "blue": "#6fa8dc",
    "purple": "#8e7cc3",
    "magenta": "#c27ba0",
}

BIOIN_BLUE = "#333399"

# HATCH_TABLE = {
#     "Steven": "/",
#     "Robyn": "\\",
#     "Both": "x",
#     np.nan: "",
# }

matplotlib.rcParams.update({'font.size': 14})

def gantt_chart(csv_file: Path, fig_file: Path, current_date=pd.Timestamp.today()):
    """
    Generates a Gantt chart from a CSV file with title, start_date, end_date, and color columns.

    Args:
      csv_file: Path to the CSV file.
      fig_file: Path to the output fig file.
      current_date: The current date to mark on the chart (default: today's date).

    Returns:
      None. Displays the Gantt chart plot.
    """
    # TODO: https://stackoverflow.com/questions/67197205/move-grid-inbetween-bars

    # Read the CSV file
    df = pd.read_csv(csv_file)

    df = df.dropna(how="all")

    # Convert dates to datetime objects
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    df["days_to_start"] = (df["start_date"] - df["start_date"].min()).dt.days
    df["days_to_end"] = (df["end_date"] - df["start_date"].min()).dt.days
    df["task_duration"] = df["days_to_end"] - df["days_to_start"] + 1  # to include also the end date

    df["_color"] = df["color"].map(COLOR_TABLE)
    # df["_hatch"] = df["label"].map(HATCH_TABLE)

    fig, ax = plt.subplots(figsize=(16, 9))
    # increase left padding
    plt.subplots_adjust(left=0.2)

    ax.barh(
        y=df["title"],
        width=df["task_duration"],
        left=df["start_date"],
        color=df["_color"],
        label=df["label"],
        # hatch=df["_hatch"],
    )

    # change x-axis labels to dates
    ax.xaxis_date()
    # set date format on x-axis
    ax.xaxis.set_major_formatter(DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(WeekdayLocator(byweekday=SU))

    # add vertical line for current date
    ax.axvline(x=current_date, color=BIOIN_BLUE, linestyle="-")
    # add text above vertical line with current date outside of the plot
    # ax.text(current_date, 0, "Today", rotation=90, verticalalignment="bottom", horizontalalignment="right")
    date_ratio = (current_date - df["start_date"].min()) / (df["end_date"].max() - df["start_date"].min())
    plt.gcf().text(date_ratio - 0.025, 0.89, current_date.strftime("%b %d"), fontsize=14, color=BIOIN_BLUE)

    ax.set_xlabel("Date")
    ax.set_ylabel("Task")
    # ax.set_title("Gantt Chart")

    # horizontal lines
    number_bars = len(df['title'].unique())
    ax.set_yticks(list(map(lambda y: y - 0.5, range(number_bars + 1))), minor=True)
    ax.set_ylim(-0.5, number_bars - 0.5)
    ax.grid(axis='y', which='minor', zorder=0)  # set the grid on the minor ticks
    ax.tick_params(axis='y', which='minor', length=0)  # hide minor tick marks

    # add legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    by_label = {k: v for k, v in by_label.items() if k != "nan"}
    plt.legend(by_label.values(), by_label.keys(), loc="lower right")

    ax.xaxis.grid(True)
    plt.savefig(fig_file, bbox_inches="tight")


def main():
    parser = argparse.ArgumentParser(description="Generate a Gantt chart from a CSV file.")
    parser.add_argument("csv_file", help="Path to the input CSV file.")
    parser.add_argument("fig_file", help="Path to the output fig file.")
    args = parser.parse_args()
    gantt_chart(Path(args.csv_file), Path(args.fig_file))


if __name__ == "__main__":
    main()
