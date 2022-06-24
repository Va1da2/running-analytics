"""Utilities for the application."""
from typing import List

SECONDS_IN_MINUTE = 60
METERS_IN_KM = 1000


def get_pace_ranges_for_select_slider(
    min_pace_seconds: int, max_pace_seconds: int, step_seconds: int = 15
) -> List[str]:

    output = []
    for pace_in_seconds in range(max_pace_seconds, min_pace_seconds + 1, step_seconds):
        output.append(from_seconds_to_pace_string(pace_in_seconds))
    output.reverse()

    return output


def from_seconds_to_pace_string(seconds: int) -> str:

    minutes_ = seconds // SECONDS_IN_MINUTE
    seconds_ = seconds % SECONDS_IN_MINUTE

    return f"{minutes_}:{str(seconds_).zfill(2)}"

def parse_pace_string(pace_string: str) -> int:

    minutes, seconds = pace_string.split(":")

    return int(int(minutes) * SECONDS_IN_MINUTE + int(seconds))


def speed_from_pace_string(pace_string: str) -> float:
    
    pace_in_seconds = parse_pace_string(pace_string)

    return METERS_IN_KM / pace_in_seconds

