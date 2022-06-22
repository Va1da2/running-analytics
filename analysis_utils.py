"""Functions that help analyse data and draw graphs"""
import math
from typing import List, Tuple


def round_decimals(number:float, decimals:int=2,  down=False):
    """
    Returns a value rounded down to a specific number of decimal places.
    """
    rounding_func = math.floor if down else math.ceil
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return rounding_func(number)

    factor = 10 ** decimals
    
    return rounding_func(number * factor) / factor


def get_stride_min_max(stride_lengths: List[float]) -> Tuple[float]:
    
    stride_pre_post_fix = 0.1
    min_, max_ = round_decimals(min(stride_lengths), 1, down=True), round_decimals(max(stride_lengths), 1)

    return min_ - stride_pre_post_fix, max_ + stride_pre_post_fix

def get_cadence_min_max(cadences: List[int]) -> Tuple[int]:

    cadence_pre_post_fix = 10
    min_, max_ = min(cadences), max(cadences)
    min_adjusted = min_ - (min_ % 10)
    max_adjusted = max_ + (10 - (max_ % 10))

    return int(min_adjusted - cadence_pre_post_fix), int(max_adjusted + cadence_pre_post_fix)

def get_y_axis_ticks(stride_lengths, cadences) -> Tuple[List[float], List[int]]:

    stride_min, stride_max = get_stride_min_max(stride_lengths)
    cadence_min, cadence_max = get_cadence_min_max(cadences)

    stride_ticks = [i / 10 for i in range(int(stride_min * 10), int(stride_max * 10) + 1, 1)]
    cadence_ticks = [i for i in range(cadence_min, cadence_max + 1, 10)]

    n_stride_ticks = len(stride_ticks)
    n_cadence_ticks = len(cadence_ticks)

    if n_stride_ticks == n_cadence_ticks:
        return stride_ticks, cadence_ticks
    
    elif n_stride_ticks > n_cadence_ticks:
        n = n_stride_ticks - n_cadence_ticks
        for i in range(1, n+1):
            cadence_ticks.append(cadence_ticks[-1]+10)
    
    else:
        n = n_cadence_ticks - n_stride_ticks
        for i in range(1, n+1):
            stride_ticks.append(stride_ticks[-1]+0.1)
    
    return stride_ticks, cadence_ticks
    