from datetime import datetime as dt
from datetime import timedelta as td

import numpy as np
import pandas as pd
import requests

from custom_enums import *


def date_to_timestamp(date):
    return int(dt.combine(date, dt.min.time()).timestamp())


def get_data(
    date_from: dt.date = None,
    date_to: dt.date = None,
) -> pd.DataFrame:
    response = requests.get(
        # "http://api:8000/cars_on_border",
        "http://164.92.167.135:8000/cars_on_border",
        params={
            "processed": True,
            "start_timestamp": date_to_timestamp(date_from),
            "end_timestamp": date_to_timestamp(date_to),
        },
    )
    return pd.DataFrame(response.json())


def add_url_column(data: pd.DataFrame) -> pd.DataFrame:
    data[Columns.image] = (
        "http://164.92.167.135:8000/static/"
        + data["image_path"]
        .str.split(
            "/usr/src/parser/data/",
        )
        .str[1]
    )
    return data


def bin_data(
    data,
    timeframe: str,
    moving_average: int = 1,
) -> pd.DataFrame:
    data = pd.DataFrame(data, columns=["created_at", "number_of_cars", Columns.image])

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


def agg_data(data, timeframe: str) -> pd.DataFrame:

    data = pd.DataFrame(data, columns=["created_at", "number_of_cars"])

    data.rename(
        columns={"created_at": Columns.time, "number_of_cars": Columns.cars},
        inplace=True,
    )

    # Convert to Datetime
    data[Columns.time] = pd.to_datetime(data[Columns.time])

    # Create column to aggregate on
    match timeframe:

        case (Timeframe.min | Timeframe.hourly):
            data[Columns.time] = data[Columns.time].dt.strftime("%H:00")

        case Timeframe.daily:
            data[Columns.time] = data[Columns.time].dt.day_name()

    # Aggregate data
    data = data.groupby(Columns.time)[Columns.cars].mean().reset_index()

    # Round DataFrame with precision to 1 after comma
    data = data.round(1)

    return data
