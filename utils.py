"""Utilities for the application."""
from typing import List

SECONDS_IN_MINUTE = 60


def get_pace_ranges_for_select_slider(min_pace_seconds: int, max_pace_seconds: int, step_seconds: int = 15) -> List[str]:

    output = []
    for pace_in_seconds in range(max_pace_seconds, min_pace_seconds + 1, step_seconds):
        output.append(from_seconds_to_pace_string(pace_in_seconds))
    output.reverse()

    return output

def from_seconds_to_pace_string(seconds: int) -> str:
    
    minutes_ = seconds // SECONDS_IN_MINUTE
    seconds_ = seconds % SECONDS_IN_MINUTE

    return f"{minutes_}:{str(seconds_).zfill(2)}"