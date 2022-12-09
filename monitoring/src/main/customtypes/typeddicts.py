
from datetime import datetime as dt
from typing import TypedDict


class MonitorDict(TypedDict):
    datetime: list[dt]
    power_kW: list[float]