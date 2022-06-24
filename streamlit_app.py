import os
import traceback

import pandas as pd
import streamlit as st
from fitparse import FitFile

from analysis import process_files, make_figure, clean_data
from utils import get_pace_ranges_for_select_slider, speed_from_pace_string

FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DEMO_FILE = os.path.join(FILE_DIRECTORY, "data", "8599886615_ACTIVITY.fit")
EXCEPTION_IMAGE = os.path.join(FILE_DIRECTORY, "assets", "MA19-SportsMedicine.jpeg")

MIN_LAP_TIME_SECONDS = 5
MAX_LAP_TIME_SECONDS = int(1.5 * 60 * 60)


st.set_page_config(
    page_title="Cadence vs Stride", page_icon="\U0001F3C3", layout="centered"
)

st.title("\U0001F3C3" + "Cadence vs Stride")
st.header("Why Cadence vs Stride")
st.markdown(
    """
When Asics released their first super shows - MetaSpeed Sky and Edge - I was a bit confused about the whole stride 
vs cadence distinction. I was not sure (although I had an idea) where I fall on this spectrum although I went ahead 
and bought myself a Sky variant. From a quick glance at my data, it looked close - I increased both my cadence 
as well as stride length.

With the release of the updated Sky+ & Edge+, they also released (or I noticed them this time) some graphs where 
Asics give a bit more concrete explanation about the distinction between a `Stride` and `Cadence` runners 
(see the graphs below that I have found on [Reddit](https://www.reddit.com/r/RunningShoeGeeks/comments/mgjxmc/asics_distinguishes_stride_runners_vs_cadence/))
""".strip()
)
st.image("./assets/asics-stride-cadence.png")
st.markdown(
    """
A few observations from the above graphs:

1. These are very fast runners.
2. There is quite a big difference between the two runners, but these might be cherry-picked graphs to illustrate the differences.
3. Since paces are fast, it is not obvious that this translates well for slower runners.
4. I haven't seen such a graph as part of the regular Garmin/Strava activity analytics set. 
""".strip()
)
st.subheader("Stride vs Cadence analysis for a regular runner")
st.markdown(
    """
To see how the stride and cadence differ for me (and others), I have created this app. All you need to do is to provide
a `.fit` file that you can download from your Garmin connect application (Or you can see how the analysis looks for my Mitching workout by checking the `Use demo data` checkbox).
You can provide multiple files if you wish. The main consideration should be the range of paces. For this analysis to be meaningful,
there needs to be a range of paces and associated stride lengths and cadences. I used the Michigan workout to develop this
because it features a lot of different paces - easy pace for warm-up, tempo, 10k, 5k, and 3k paces for the workout sets.

Since I am using a Garmin watch, I used `.fit` files. If you use a different platform and would like to see this analysis, you could provide me with the data of your activity and
I will expand this app to allow for other types of input files.
"""
)

files = st.file_uploader(
    label="Select .fit file(s) for analysis", type="fit", accept_multiple_files=True
)
use_demo_data = st.checkbox("Use demo data")

if files or use_demo_data:

    try:
        files = files if files else [open(DEMO_FILE, "rb")]
        data = process_files(files)
    except Exception as e:
        data = pd.DataFrame({})
        st.write(
            "Sorry, the data processing failed! Please send the stacktrace to vaidas (dot) armonas (at) gmail (dot) com"
        )
        st.image(
            EXCEPTION_IMAGE,
            caption="Source: https://impactmagazine.ca/health/sport-medicine/injury-free-running/",
        )
        with st.expander("Stack Trace"):
            stack_trace = traceback.format_exception(e)
            st.write(f"{''.join(stack_trace)}")
    
    if not data.empty:
        
        with st.expander("Advnaced data clearning options [NOT USED YET]"):
            min_lap_time, max_lap_time = int(data["lap_time"].min()), int(data["lap_time"].max())
            selected_min_lap_time, selected_max_lap_time = st.slider(
                "Lap time range (seconds)",
                min_lap_time,
                max_lap_time,
                (min_lap_time, max_lap_time),
                step=5,
            )
            
            pace_ranges = get_pace_ranges_for_select_slider(540, 120)
            slow_selected_pace, fast_selected_pace = st.select_slider(
                "Pace range (min/km)", pace_ranges, (pace_ranges[0], pace_ranges[-1])
            )

        with st.expander("Advanced regression options"):
            weight_points_by_distance = st.checkbox(
                "Weight results by the lap distance?"
            )
        cleaned_data = clean_data(
            data,
            min_lap_time=selected_min_lap_time,
            max_lap_time=selected_max_lap_time,
            min_speed=speed_from_pace_string(slow_selected_pace),
            max_speed=speed_from_pace_string(fast_selected_pace),
        )
        fig = make_figure(cleaned_data, weight_points_by_distance)
        st.pyplot(fig, clear_figure=True)

        st.markdown(
            """
        Hopefully, your graph indicates which type of runner you are.

        If you have selected demo data - I am most likely a `cadence` runner. Even though the angle seems a bit too steep
        compared with the Asics graph, but both stride length and cadence increase at the same rate, which is consistent
        with the cadence runners graph.
        """
        )

st.subheader("TO DO:")
st.markdown(
    """
1. Add comments
3. Add statistical analysis of the slopes -> is there a statistical difference between the two slopes?
"""
)
