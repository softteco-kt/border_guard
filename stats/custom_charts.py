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

    # Create a selection that chooses the nearest point & selects based on x-value
    # By default, all data values are considered to lie within an empty selection.
    # When empty set to none, selections contain no data values.
    highlight = alt.selection(
        type="single", on="mouseover", nearest=True, empty="none", fields=[Columns.time]
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=f"{Columns.time}:T",
            opacity=alt.value(0),
        )
        .add_selection(highlight)
    )

    # Chart configs on given data
    base = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X(
                Columns.time,
                title="Datetime: " + timeframe,
                type="temporal",
                timeUnit=x_axis_label,
            ),
            y=alt.Y(Columns.cars, title="Number of Cars", type="quantitative"),
            color=alt.value("cornflowerblue"),
            tooltip=tooltip,
        )
    )

    # Moving average line chart
    line = base.mark_line().encode(
        y=alt.Y(Columns.moving_average, type="quantitative"),
        color=alt.value("#FFAA00"),
    )

    # Draw points on the line, add tooltip to the point and highlight based on selection
    points = line.mark_point().encode(
        tooltip=[Columns.moving_average, Columns.time],
        opacity=alt.condition(highlight, alt.value(1), alt.value(0)),
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align="left", dx=5, dy=-5).encode(
        text=alt.condition(highlight, f"{Columns.moving_average}:Q", alt.value(" ")),
    )

    # Draw a rule at the location of the selection
    rules = (
        alt.Chart(data)
        .mark_rule(color="grey")
        .encode(x=f"{Columns.time}:T")
        .transform_filter(highlight)
    )

    # Draw scatter plot and line chart with base chart data
    chart = alt.layer(
        line,
        selectors,
        points,
        rules,
        text,
        base.mark_point(),
    )

    return chart


def draw_altair_agg(data: pd.DataFrame, timeframe: str):
    tooltip = [Columns.cars]

    highlight = alt.selection_single(on="mouseover")
    # Chart configs on given data
    base = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X(Columns.time, title="Datetime: " + timeframe, type="ordinal"),
            y=alt.Y(Columns.cars, title="Number of Cars", type="quantitative"),
            tooltip=tooltip,
            color=alt.condition(
                highlight,
                alt.value("steelblue"),
                alt.value("lightblue"),
            ),
        )
        .add_selection(highlight)
    )

    return base
