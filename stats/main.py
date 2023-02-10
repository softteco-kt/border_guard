import streamlit as st

from datetime import datetime as dt
from datetime import timedelta as td

from custom_enums import *
from custom_charts import *
from data import *

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
type_widget, from_widget, to_widget = st.columns(3)
input_type = type_widget.selectbox("View", ["Aggregation", "Plain"])
input_date_from = from_widget.date_input("Date From:", dt.today() - td(days=1))
input_date_to = to_widget.date_input("Date To:")


try:
    # Get API data
    raw_data = get_data(
        date_from=input_date_from,
        date_to=input_date_to,
    )

    raw_data = add_url_column(raw_data)
    raw_data
    sidebar_header = "**Additional params:**"
    match input_type:

        case "Plain":
            # Apply binning to data
            with st.sidebar:
                st.write(sidebar_header)
                input_ma = st.number_input("Moving average:", 0)
                input_tf = st.selectbox("Bucket by", Timeframe.list())

            data = bin_data(
                raw_data,
                timeframe=input_tf,
                moving_average=input_ma,
            )

            chart = draw_altair_bin(
                data, timeframe=input_tf, moving_average=True if input_ma > 0 else False
            )

        case "Aggregation":
            with st.sidebar:
                st.write(sidebar_header)
                input_tf = st.selectbox(
                    "Aggregate by", [Timeframe.hourly, Timeframe.daily]
                )

            # Apply aggregation to data
            data = agg_data(
                raw_data,
                timeframe=input_tf,
            )
            chart = draw_altair_agg(data, timeframe=input_tf)

    st.altair_chart(chart, use_container_width=True)
    st.write("*\* Time is in UTC*")
except Exception as e:
    st.write("No data...")
