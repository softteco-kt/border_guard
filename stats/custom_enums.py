import enum


class Timeframe(enum.StrEnum):
    """Data timeframes"""

    min = "None"
    hourly = "Hours"
    daily = "Days"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Columns(enum.StrEnum):
    """DataFrame column names"""

    created_at = "created_at"
    cars = "number_of_cars"
    image_path = "image_path"
    moving_average = "Moving Average"
    image = "image"
    time = "Datetime"
    day_of_week = "Day of Week"
    day = "Day"
    hour = "Hour"
    minute = "Minute"


class Weekdays(enum.IntEnum):
    """Enum representing pandas int weekdays."""

    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6
