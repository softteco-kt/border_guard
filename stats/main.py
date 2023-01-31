import requests
import streamlit as st

import pandas as pd
import numpy as np

import altair as alt
import json
from datetime import datetime as dt, timedelta as td


def date_to_timestamp(date):
    return int(dt.combine(date, dt.min.time()).timestamp())


def get_data(date_from=None, date_to=None):
    response = requests.get(
        "http://api:8000/cars_on_border",
        params={
            "processed": True,
            "start_timestamp": date_to_timestamp(date_from),
            "end_timestamp": date_to_timestamp(date_to),
        },
    )
    data = pd.DataFrame(response.json(), columns=["created_at", "number_of_cars"])
    return data


def draw_altair(data):
    base = alt.Chart(data).encode(
        x=alt.X("created_at", title="Datetime", type="temporal"),
        y=alt.Y("number_of_cars", title="Number of Cars", type="quantitative"),
        tooltip=["Time", "number_of_cars"],
    )

    chart = (
        alt.layer(
            base.mark_point(),
            base.mark_line().encode(
                y=alt.Y(MOVING_AVERAGE_COL, type="quantitative"),
                color=alt.value("#FFAA00"),
            )
            # .mark_rule(),
        )
        # .interactive()
    )

    return chart


st.set_page_config(
    layout="wide",
    title="Border Guard",
    menu_items={},
)

st.title("Statistics")

# Input for api filtering
ma_widget, from_widget, to_widget = st.columns(3)
input_ma = ma_widget.number_input("Moving average (Hours)", 1) * 3
input_date_from = from_widget.date_input("Date From:", dt.today() - td(days=1))
input_date_to = to_widget.date_input("Date to: ")

# Get API data
data = get_data(date_from=input_date_from, date_to=input_date_to)

try:
    # Calculate moving average
    MOVING_AVERAGE_COL = f"Moving Average - {input_ma//3} hours"
    data[MOVING_AVERAGE_COL] = data.rolling(window=input_ma).mean().fillna(0)

    # Get datetime
    times = pd.to_datetime(data.created_at)
    data["Date"] = times.dt.date
    data["Time"] = times.dt.strftime("%H:%M")

    st.altair_chart(draw_altair(data), use_container_width=True)
except:
    st.write("No data...")
