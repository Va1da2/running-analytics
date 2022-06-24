import codecs
from collections import defaultdict
from typing import Dict, List, IO, Union, Tuple, TypeVar

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fitparse import FitFile
from matplotlib.figure import Figure
from matplotlib.collections import PathCollection

from analysis_utils import get_y_axis_ticks

MatplotlibGraphType = TypeVar("MatplotlibGraphType")

SECONDS_IN_MINUTE = 60.0
CADENCE_MULTIPLIER = 2.0
METERS_IN_KM = 1000.0

PACE_TO_SPEED = {
    7: METERS_IN_KM / (7 * SECONDS_IN_MINUTE),
    6: METERS_IN_KM / (6 * SECONDS_IN_MINUTE),
    5: METERS_IN_KM / (5 * SECONDS_IN_MINUTE),
    4: METERS_IN_KM / (4 * SECONDS_IN_MINUTE),
    3: METERS_IN_KM / (3 * SECONDS_IN_MINUTE),
}


class NoFilesProvidedError(Exception):
    """Raised when no files were selected for analysis"""

    pass


def get_lap_data(fit_file: FitFile) -> Dict[str, List[float]]:

    output = defaultdict(list)
    for lap in fit_file.get_messages("lap"):
        output["average_speed"].append(lap.get_value("enhanced_avg_speed"))
        output["lap_distance"].append(lap.get_value("total_distance"))
        output["lap_time"].append(lap.get_value("total_elapsed_time"))
        output["lap_power"].append(lap.get_value("Lap Power"))
        output["average_stride_length"].append(
            lap.get_value("total_distance")
            / lap.get_value("total_strides")
            / CADENCE_MULTIPLIER
        )
        output["average_cadence"].append(
            lap.get_value("total_strides")
            / lap.get_value("total_elapsed_time")
            * SECONDS_IN_MINUTE
            * CADENCE_MULTIPLIER
        )

    return output


def clean_data(
    data: pd.DataFrame,
    min_lap_time: int,
    max_lap_time: int,
    min_speed: float,
    max_speed: float,
) -> pd.DataFrame:

    cleaned_data = data[data["average_speed"].between(min_speed, max_speed)]
    cleaned_data = cleaned_data[cleaned_data["lap_time"].between(min_lap_time, max_lap_time)]

    return cleaned_data.sort_values(by="average_speed")


def process_files(files: List[IO[bytes]]) -> pd.DataFrame:

    processing_results = []
    for file in files:
        processing_results.append(get_lap_data(FitFile(file)))

    output = None
    if processing_results:
        for result in processing_results:
            if output is None:
                output = result
            else:
                output["average_speed"].extend(result["average_speed"])
                output["lap_distance"].extend(result["lap_distance"])
                output["lap_time"].extend(result["lap_time"])
                output["average_stride_length"].extend(result["average_stride_length"])
                output["average_cadence"].extend(result["average_cadence"])
                output["lap_power"].extend(result["lap_power"])
    else:
        raise NoFilesProvidedError

    return pd.DataFrame(output)

def select_items_for_legend(lines: List, labels: List[str], line_type: MatplotlibGraphType) -> Tuple[List, List[str]]:

    selected_lines, selected_labels = [], []
    for index, line in enumerate(lines):
        if type(line) == line_type:
            selected_lines.append(line)
            selected_labels.append(labels[index])
    
    return selected_lines, selected_labels

def make_figure(data: pd.DataFrame, weight_by_lap_distance=False) -> Figure:

    average_speed = data["average_speed"].to_list()
    lap_distance = data["lap_distance"].to_list()
    average_stride_length = data["average_stride_length"].to_list()
    average_cadence = data["average_cadence"].to_list()

    stride_ticks, cadence_ticks = get_y_axis_ticks(
        average_stride_length, average_cadence
    )

    if weight_by_lap_distance:
        stride_b, stride_c = np.polyfit(
            np.array(average_speed), np.array(average_stride_length), 1, w=lap_distance
        )
        cadence_b, cadence_c = np.polyfit(
            np.array(average_speed), np.array(average_cadence), 1, w=lap_distance
        )
    else:
        stride_b, stride_c = np.polyfit(
            np.array(average_speed), np.array(average_stride_length), 1
        )
        cadence_b, cadence_c = np.polyfit(
            np.array(average_speed), np.array(average_cadence), 1
        )

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    fig.set_size_inches(10, 8)

    color = "tab:red"
    ax1.set_xlabel("Average lap running speed (m/s)", fontdict={"fontsize": 14})
    ax1.set_ylabel("Average stride length", color=color, fontdict={"fontsize": 14})
    ax1.tick_params(axis="x", labelsize=14)
    ax1.tick_params(axis="y", labelcolor=color, labelsize=14)
    if weight_by_lap_distance:
        ax1.scatter(
            average_speed,
            average_stride_length,
            color=color,
            s=lap_distance,
            alpha=0.7,
            label="Stride length",
        )
    else:
        ax1.scatter(
            average_speed,
            average_stride_length,
            color=color,
            s=250,
            alpha=0.7,
            label="Stride length",
        )
    ax1.plot(
        average_speed,
        stride_b * np.array(average_speed) + stride_c,
        color=color,
        linestyle="dashed",
        label="Stride length regression",
    )
    ax1.set_ylim([stride_ticks[0], stride_ticks[-1]])
    ax1.set_yticks(stride_ticks)

    color = "tab:blue"
    ax2.set_ylabel(
        "Average lap cadence", color=color, fontdict={"fontsize": 14}
    )  # we already handled the x-label with ax1
    ax2.tick_params(axis="y", labelcolor=color, labelsize=14)
    if weight_by_lap_distance:
        ax2.scatter(
            average_speed,
            average_cadence,
            color=color,
            s=lap_distance,
            alpha=0.7,
            label="Cadence",
        )
    else:
        ax2.scatter(
            average_speed, average_cadence, color=color, alpha=0.7, s=250, label="Cadence"
        )
    ax2.plot(
        average_speed,
        cadence_b * np.array(average_speed) + cadence_c,
        color=color,
        linestyle="dashed",
        label="Cadence regression",
    )
    ax2.set_ylim([cadence_ticks[0], cadence_ticks[-1]])
    ax2.set_yticks(cadence_ticks)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    selected_lines, selected_labels = select_items_for_legend(lines + lines2, labels + labels2, PathCollection)
    if weight_by_lap_distance:
        ax2.legend(
            selected_lines, selected_labels, loc=0, labelspacing=1.0, markerscale=0.2
        )
    else:
        ax2.legend(selected_lines, selected_labels, loc=0, labelspacing=1.0)

    # add lines to indicate pace
    min_speed, max_speed = min(average_speed), max(average_speed)
    max_y = max(average_cadence)
    for pace, speed in PACE_TO_SPEED.items():
        if (speed > min_speed) and (speed < max_speed):
            plt.axvline(
                x=speed, ymin=0.05, ymax=0.95, color="black", linestyle="dashed"
            )
            plt.text(
                speed,
                0.95 * max_y,
                s=f"{pace} min/km",
                bbox={"boxstyle": "square", "facecolor": "white"},
            )

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title(
        "Comapring stride length increase against cadence increase",
        fontdict={"fontsize": 20},
    )

    return fig
