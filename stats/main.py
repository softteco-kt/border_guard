from datetime import datetime as dt
from datetime import timedelta as td

import streamlit as st
from streamlit import session_state as session

from custom_charts import *
from custom_enums import *
from data import *

st.set_page_config(layout="wide", page_title="Border Guard", page_icon="🧊")


def get_raw_data(date_from, date_to):
    # Get API data
    raw_data = get_data(
        date_from=date_from,
        date_to=date_to,
    )

    raw_data = add_url_column(raw_data)

    # Include only valid data
    raw_data = raw_data[raw_data.is_valid == True]
    return raw_data


def get_camera_locations():
    locations = requests.get("http://api:8000/camera_locations")
    return locations.json()

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
location_widget, type_widget, from_widget, to_widget = st.columns(4)
input_location = location_widget.selectbox("Location", get_camera_locations(), key="location")
input_type = type_widget.selectbox("View", ["Aggregation", "Plain"])

from_datetime_placeholder = from_widget.empty()
session.date_from = from_datetime_placeholder.date_input(
    "Date From:",
    dt.today() - td(days=1),
)

to_datetime_placeholder = to_widget.empty()
session.date_to = to_datetime_placeholder.date_input(
    "Date To:",
    dt.today() + td(days=1),
)


try:
    sidebar_header = "**Additional params:**"
    match input_type:

        case "Plain":
            # Apply binning to data
            with st.sidebar:
                st.write(sidebar_header)
                input_ma = st.number_input("Moving average:", 0)
                input_tf = st.selectbox("Bucket by", Timeframe.list())

                # Utility datetime ranges that overwrite initial values
                input_last_n_days = st.selectbox(
                    "Default datetime range: ",
                    [None, 7, 14, 30],
                    format_func=lambda x: f"Last {x} days." if x is not None else None,
                )

                if input_last_n_days:
                    # Overwrite and disable initial date ranges
                    session.date_from = dt.today() - td(days=input_last_n_days)
                    session.date_to = dt.today() + td(days=1)

                    # Redraw date widgets, show current date and disable
                    from_datetime_placeholder.date_input(
                        "Date from: ", session.date_from, disabled=True
                    )
                    to_datetime_placeholder.date_input(
                        "Date to: ", session.date_to, disabled=True
                    )

                # Filtering inputs
                with st.expander(label="Included days: ", expanded=False):
                    include_monday = st.checkbox("Monday", value=True)
                    include_tuesday = st.checkbox("Tuesday", value=True)
                    include_wednesday = st.checkbox("Wednesday", value=True)
                    include_thursday = st.checkbox("Thursday", value=True)
                    include_friday = st.checkbox("Friday", value=True)
                    include_saturday = st.checkbox("Saturday", value=True)
                    include_sunday = st.checkbox("Sunday", value=True)

            included_days = []
            if include_monday:
                included_days.append(Weekdays.monday)
            if include_tuesday:
                included_days.append(Weekdays.tuesday)
            if include_wednesday:
                included_days.append(Weekdays.wednesday)
            if include_thursday:
                included_days.append(Weekdays.thursday)
            if include_friday:
                included_days.append(Weekdays.friday)
            if include_saturday:
                included_days.append(Weekdays.saturday)
            if include_sunday:
                included_days.append(Weekdays.sunday)

            raw_data = get_raw_data(session.date_from, session.date_to)

            # Convert created to datetime to use dt.day_of_week
            raw_data[Columns.day_of_week] = pd.to_datetime(
                raw_data.created_at
            ).dt.day_of_week

            # Filter raw data in pandas according to chosen checkboxes
            raw_data["include"] = raw_data[Columns.day_of_week].apply(
                lambda x: x in included_days
            )

            # Apply filter
            raw_data = raw_data[raw_data.include == True]

            # raw_data = raw_data[raw_data.]
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

            raw_data = get_raw_data(session.date_from, session.date_to)

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
