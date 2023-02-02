import altair as alt
import pandas as pd

from custom_enums import *


def draw_altair_bin(data: pd.DataFrame, timeframe: str):
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
        x=alt.X(
            Columns.time,
            title="Datetime: " + timeframe,
            type="temporal",
            timeUnit=x_axis_label,
        ),
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


def draw_altair_agg(data: pd.DataFrame, timeframe: str):
    tooltip = [Columns.cars]

    # Chart configs on given data
    base = alt.Chart(data).encode(
        x=alt.X(Columns.time, title="Datetime: " + timeframe, type="ordinal"),
        y=alt.Y(Columns.cars, title="Number of Cars", type="quantitative"),
        tooltip=tooltip,
    )

    # Draw scatter plot and line chart with base chart data
    chart = alt.layer(base.mark_bar())

    return chart
