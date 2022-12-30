
from datetime import datetime as dt
from typing import TypedDict


# pre database types

class PowermeterMonitorDict(TypedDict):
    datetime: list[dt]
    power_kW: list[float]

class DeviceMonitorDict(TypedDict, total=False):
    datetime: list[dt]
    ambient_temp_degC: list[float]
    ambient_rH_percent: list[float]
    ram_load_percent: list[float]
    disk_usage_percent: list[float]
    network_sent_bytes: list[int]
    network_recv_bytes: list[int]
    cpu_freq_percent: list[float]
    cpu_load_percent: list[float]
    cpu_temp_degC: list[float]


# post database types

class StromzaehlerTableData(TypedDict):
    datetime: list[dt]
    power_kW: list[float]
    agg_consumption_Wh: list[int]

class SqlServerResult(TypedDict):
    status_code: int

class SqlServerResultStromzaehler(SqlServerResult):
    data: StromzaehlerTableData