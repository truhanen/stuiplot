import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def date_parser(s: str) -> pd.Timestamp:
    return pd.Timestamp(datetime.strptime(s, "%Y-%m-%d_%H:%M:%S"))


def read_log(path: Path) -> pd.DataFrame:
    """Read s-tui log file into pandas DataFrame."""
    return pd.read_csv(
        path,
        index_col=0,
        parse_dates=True,
        date_parser=date_parser,
    )


def get_mean_series_freq(log_frame: pd.DataFrame) -> pd.Series:
    """Get frequency time series as mean over CPU cores."""
    columns_freq = [
        c for c in log_frame.columns if re.fullmatch(r"Frequency:Core \d+", c)
    ]
    values_freq = log_frame[columns_freq].mean(axis=1)
    return values_freq


def get_mean_series_temp(log_frame: pd.DataFrame):
    """Get temperature time series as mean over CPU cores."""
    columns_temp = [c for c in log_frame.columns if re.fullmatch(r"Temp:Core\d+,0", c)]
    values_temp = log_frame[columns_temp].mean(axis=1)
    return values_temp


def get_mean_series_util(log_frame: pd.DataFrame):
    """Get utilization percentage time series as mean over CPU cores."""
    columns_util = [c for c in log_frame.columns if re.fullmatch(r"Util:Core \d+", c)]
    values_util = log_frame[columns_util].mean(axis=1)
    return values_util


def _plot_stui_log(
    log_frame: pd.DataFrame,
    ax_util: plt.Axes,
    ax_freq: plt.Axes,
    ax_temp: plt.Axes,
    write_ylabel: bool,
    minutes_max: int,
    line_width: float,
    align_threshold: Optional[int],
):
    values_util = get_mean_series_util(log_frame=log_frame)
    values_freq = get_mean_series_freq(log_frame=log_frame)
    values_temp = get_mean_series_temp(log_frame=log_frame)

    # Convert index to minutes.
    if align_threshold is not None:
        over_threshold = log_frame["Util:Avg"] > align_threshold
        if not np.any(over_threshold):
            raise ValueError(
                f"No utilization values over align threshold {align_threshold}"
            )
        load_start_index = np.where(over_threshold)[0][0]
        minutes_min = -1
    else:
        load_start_index = 0
        minutes_min = 0
    load_start_time = log_frame.index[load_start_index]
    minutes = (log_frame.index - load_start_time).total_seconds() / 60

    for values, ax, label in zip(
        (values_util, values_freq, values_temp),
        (ax_util, ax_freq, ax_temp),
        ("Utilization, %", "Frequency, MHz", "Temperature, C"),
    ):
        ax.plot(minutes, values, label="Core average", linewidth=line_width)
        if write_ylabel:
            ax.set_ylabel(label)
        ax.grid()

    ax_util.set_ylim(-2, 102)
    ax_freq.set_ylim(0, 5000)
    ax_temp.set_ylim(25, 110)

    ax_last = ax_temp
    ax_last.set_xlim(minutes_min, minutes_max)
    ax_last.set_xlabel("Time, minutes")
    major_div = 5
    major_range_max = (minutes_max // major_div) * major_div + 1
    ax_last.set_xticks(range(0, major_range_max, major_div))
    ax_last.set_xticks(range(0, major_range_max), minor=True)


def plot_stui_logs(
    log_frames: Dict[str, pd.DataFrame],
    figure_size: Optional[Tuple[int, int]],
    figure_path: Optional[Path],
    align_threshold: Optional[int],
    minutes_max: int,
):
    figure_size = figure_size or (1 + 4 * len(log_frames), 5)
    fig, axs = plt.subplots(
        3,
        len(log_frames),
        figsize=figure_size,
        constrained_layout=True,
        sharex="col",
        sharey="row",
    )
    if len(axs.shape) == 1:
        axs = axs[:, np.newaxis]
    for ax_column, (label, log_frame) in enumerate(log_frames.items()):
        ax_util, ax_freq, ax_temp = axs[:, ax_column]
        write_ylabel = ax_column == 0
        _plot_stui_log(
            log_frame=log_frame,
            ax_util=ax_util,
            ax_freq=ax_freq,
            ax_temp=ax_temp,
            write_ylabel=write_ylabel,
            minutes_max=minutes_max,
            line_width=0.5,
            align_threshold=align_threshold,
        )

        ax_util.set_title(label, fontsize="small")

    if figure_path:
        fig.savefig(figure_path)
    else:
        plt.show()


def parse_args():
    argparser = argparse.ArgumentParser(
        description=(
            "Read s-tui csv log files & plot CPU frequency, temperature, &\n"
            "utilization percentage as a function of time. All values shown are\n"
            "means over all CPU cores."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argparser.add_argument(
        "log",
        action="extend",
        nargs="+",
        type=Path,
        help="path to s-tui log file",
    )
    argparser.add_argument(
        "--figure-path",
        type=Path,
        help="if given, don't show the figure but write it to this file",
    )
    argparser.add_argument(
        "--align-threshold",
        type=int,
        help="CPU utilization threshold for aligning the data on the time axis",
    )
    argparser.add_argument(
        "--minutes",
        type=int,
        default=15,
        help="amount of time to show",
    )
    return argparser.parse_args()


def main():
    args = parse_args()
    log_frames = {log_path.name: read_log(log_path) for log_path in args.log}
    plot_stui_logs(
        log_frames=log_frames,
        figure_size=None,
        figure_path=args.figure_path,
        align_threshold=args.align_threshold,
        minutes_max=args.minutes,
    )


if __name__ == "__main__":
    main()
