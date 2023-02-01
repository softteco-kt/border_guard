import requests
import enum

import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

from datetime import datetime as dt
from datetime import timedelta as td


class Timeframe(enum.StrEnum):
    """Data timeframes"""

    min = "Min"
    hourly = "Hourly"
    daily = "Daily"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Columns(enum.StrEnum):
    """DataFrame column names"""

    moving_average = "Moving Average"
    cars = "Number of cars"
    time = "Datetime"


def date_to_timestamp(date):
    return int(dt.combine(date, dt.min.time()).timestamp())


def get_data(
    timeframe: str,
    moving_average: int = 1,
    date_from: dt.date = None,
    date_to: dt.date = None,
):
    response = requests.get(
        "http://api:8000/cars_on_border",
        params={
            "processed": True,
            "start_timestamp": date_to_timestamp(date_from),
            "end_timestamp": date_to_timestamp(date_to),
        },
    )
    data = pd.DataFrame(response.json(), columns=["created_at", "number_of_cars"])

    data.rename(
        columns={"created_at": Columns.time, "number_of_cars": Columns.cars},
        inplace=True,
    )

    # Convert to Datetime
    data[Columns.time] = pd.to_datetime(data[Columns.time])

    # Transform data to selected timeperiod
    match timeframe:
        case Timeframe.min:
            # Additional column for tooltip
            data["Time"] = data[Columns.time].dt.strftime("%b %-d %H:%M")
        case Timeframe.hourly:
            data = data.resample("60min", on=Columns.time).mean()
            data.reset_index(inplace=True)
            data["Time"] = data[Columns.time].dt.strftime("%b %-d %H:00")
        case Timeframe.daily:
            data = data.resample("1d", on=Columns.time).mean()
            data.reset_index(inplace=True)
            data["Day"] = data[Columns.time].dt.strftime("%B %-d")

    # Calculate moving average
    data[Columns.moving_average] = (
        data[Columns.cars].rolling(window=moving_average).mean().fillna(0)
    )

    # Round DataFrame with precision to 1 after comma
    data = data.round(1)

    return data


def draw_altair(data: pd.DataFrame, timeframe: str):
    tooltip = [Columns.cars]

    x_axis_label = None

    # Make appropriate to timeframe x-axis labels
    match timeframe:
        case Timeframe.min:
            tooltip.append("Time")
            x_axis_label = "yearmonthdatehoursminutes"
        case Timeframe.hourly:
            tooltip.append("Time")
            x_axis_label = "yearmonthdatehours"
        case Timeframe.daily:
            tooltip.append("Day")
            x_axis_label = "yearmonthdate"

    # Chart configs on given data
    base = alt.Chart(data).encode(
        x=alt.X(Columns.time, title="Datetime", type="temporal", timeUnit=x_axis_label),
        y=alt.Y(Columns.cars, title="Number of Cars", type="quantitative"),
        tooltip=tooltip,
    )

    # Draw scatter plot and line chart with base chart data
    chart = alt.layer(
        base.mark_point(),
        base.mark_line().encode(
            y=alt.Y(Columns.moving_average, type="quantitative"),
            color=alt.value("#FFAA00"),
        ),
    )

    return chart


st.set_page_config(layout="wide", page_title="Border Guard", page_icon="🧊")

# Disable scrolling and remove menu
css = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            section.main > div:has(~ footer ) {
                padding-bottom: 5px;
            }
        </style>
        """
st.markdown(css, unsafe_allow_html=True)

st.title("Statistics")

# Input for api filtering
tf_widget, ma_widget, from_widget, to_widget = st.columns(4)
input_tf = tf_widget.selectbox("Timeframe:", Timeframe.list())
input_ma = ma_widget.number_input("Moving average:", 1)
input_date_from = from_widget.date_input("Date From:", dt.today() - td(days=1))
input_date_to = to_widget.date_input("Date To:")

try:
    # Get API data
    data = get_data(
        timeframe=input_tf,
        moving_average=input_ma,
        date_from=input_date_from,
        date_to=input_date_to,
    )
    st.altair_chart(draw_altair(data, timeframe=input_tf), use_container_width=True)
except Exception as e:
    st.write("No data...")
