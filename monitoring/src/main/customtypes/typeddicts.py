
from datetime import datetime as dt
from typing import TypedDict


# pre database types

class MonitorDict(TypedDict):
    datetime: list[dt]
    power_kW: list[float]
    power_kW: list[float]


# post database types

class StromzaehlerTableData(TypedDict):
    datetime: list[dt]
    power_kW: list[float]
    agg_consumption_Wh: list[int]

class SqlServerResult(TypedDict):
    status_code: int

class SqlServerResultStromzaehler(SqlServerResult):
    data: StromzaehlerTableData