import enum


class Timeframe(enum.StrEnum):
    """Data timeframes"""

    min = "None"
    hourly = "Hours"
    daily = "Daily"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Columns(enum.StrEnum):
    """DataFrame column names"""

    moving_average = "Moving Average"
    cars = "Number of cars"
    time = "Datetime"
    day = "Day"
    hour = "Hour"
    minute = "Minute"
