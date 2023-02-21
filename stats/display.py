from datetime import datetime as dt
from datetime import timedelta as td

import streamlit as st
from streamlit import session_state as session

from custom_charts import *
from custom_enums import *
from data import *

# Note: session is a streamlit's user-session dict like storage to persist data between reruns.


class Display:
    sidebar_header = "**Additional parameters**"

    def __init__(self):
        # session state initializations go in here
        if "render" not in session:
            session.render = self.__build_aggregation

    def __main_user_inputs(self):
        # Main inputs to choose chart type and date range to fetch data
        type_widget, self.from_widget, self.to_widget = st.columns(3)
        self.input_type = type_widget.selectbox(
            "View",
            ["Aggregation", "Plain"],
            key="chart_type",
            on_change=self.__set_render_type,
        )

        self.from_datetime_placeholder = self.from_widget.empty()
        session.date_from = self.from_datetime_placeholder.date_input(
            "Date From:",
            dt.today() - td(days=1),
        )

        self.to_datetime_placeholder = self.to_widget.empty()
        session.date_to = self.to_datetime_placeholder.date_input(
            "Date To:",
            dt.today() + td(days=1),
        )

    def __render(self):
        session.render()

    def __set_render_type(self):
        match session.chart_type:
            case "Aggregation":
                session.render = self.__build_aggregation
            case "Plain":
                session.render = self.__build_plain

    def __build_aggregation(self):
        self.aggregation_sidebar_parameters()
        self.get_data()
        self.draw_chart_aggregation()

        st.altair_chart(self.chart, use_container_width=True)

    def __build_plain(self):
        self.plain_sidebar_parameters()
        self.get_data()
        self.filter_data()
        self.draw_chart_plain()

        st.altair_chart(self.chart, use_container_width=True)

    def plain_sidebar_parameters(self):
        with st.sidebar:
            st.write(self.sidebar_header)
            self.input_ma = st.number_input("Moving average:", 0)
            self.input_tf = st.selectbox("Bucket by", Timeframe.list())

            # Utility datetime ranges that overwrite initial values
            self.input_last_n_days = st.selectbox(
                "Default datetime range: ",
                [None, 7, 14, 30],
                format_func=lambda x: f"Last {x} days." if x is not None else None,
            )

            if self.input_last_n_days:
                # Overwrite and disable initial date ranges
                session.date_from = dt.today() - td(days=self.input_last_n_days)
                session.date_to = dt.today() + td(days=1)

                # Redraw date widgets, show current date and disable
                self.from_datetime_placeholder.date_input(
                    "Date from: ", session.date_from, disabled=True
                )
                self.to_datetime_placeholder.date_input(
                    "Date to: ", session.date_to, disabled=True
                )

            # Filtering inputs
            with st.expander(label="Included days: ", expanded=False):
                self.include_monday = st.checkbox("Monday", value=True)
                self.include_tuesday = st.checkbox("Tuesday", value=True)
                self.include_wednesday = st.checkbox("Wednesday", value=True)
                self.include_thursday = st.checkbox("Thursday", value=True)
                self.include_friday = st.checkbox("Friday", value=True)
                self.include_saturday = st.checkbox("Saturday", value=True)
                self.include_sunday = st.checkbox("Sunday", value=True)

    def aggregation_sidebar_parameters(self):
        with st.sidebar:
            st.write(self.sidebar_header)
            self.input_tf = st.selectbox(
                "Aggregate by", [Timeframe.hourly, Timeframe.daily]
            )

    def get_data(self):
        # Get API data
        self.raw_data = get_data(
            date_from=session.date_from,
            date_to=session.date_to,
        )

        self.raw_data = add_url_column(self.raw_data)

        # Include only valid data
        self.raw_data = self.raw_data[self.raw_data.is_valid == True]

    def filter_data(self):
        included_days = []
        if self.include_monday:
            included_days.append(Weekdays.monday)
        if self.include_tuesday:
            included_days.append(Weekdays.tuesday)
        if self.include_wednesday:
            included_days.append(Weekdays.wednesday)
        if self.include_thursday:
            included_days.append(Weekdays.thursday)
        if self.include_friday:
            included_days.append(Weekdays.friday)
        if self.include_saturday:
            included_days.append(Weekdays.saturday)
        if self.include_sunday:
            included_days.append(Weekdays.sunday)

        # Convert created to datetime to use dt.day_of_week
        self.raw_data[Columns.day_of_week] = pd.to_datetime(
            self.raw_data.created_at
        ).dt.day_of_week

        # Filter raw data in pandas according to chosen checkboxes
        self.raw_data["include"] = self.raw_data[Columns.day_of_week].apply(
            lambda x: x in included_days
        )

        # Apply filter
        self.raw_data = self.raw_data[self.raw_data.include == True]

    def draw_chart_aggregation(self):
        # Apply aggregation to data
        self.data = agg_data(
            self.raw_data,
            timeframe=self.input_tf,
        )
        self.chart = draw_altair_agg(self.data, timeframe=self.input_tf)

    def draw_chart_plain(self):
        # raw_data = raw_data[raw_data.]
        self.data = bin_data(
            self.raw_data,
            timeframe=self.input_tf,
            moving_average=self.input_ma,
        )

        self.chart = draw_altair_bin(
            self.data,
            timeframe=self.input_tf,
            moving_average=True if self.input_ma > 0 else False,
        )

    def render(self):
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

        # Main web page title
        st.title("Statistics")

        # Starting point
        self.__main_user_inputs()

        try:
            self.__render()
        except Exception as e:
            e
            st.write("*No data...*")


if __name__ == "__main__":
    Display().render()
