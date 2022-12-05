#!/home/pi/Dev/python/stromzaehler/venv/bin/python3

import time
import RPi.GPIO as gpio

import pandas as pd
import psutil

from copy import deepcopy
from datetime import datetime as dt, timedelta
from pandas.core.groupby.generic import DataFrameGroupBy
from threading import Event, Lock, Thread
from typing import Any, Final


def send_to_database(_event: Event) -> None:
    global monitor

    while True:
        _event.wait()
        with lockMain:
            _monitor: dict[str, list[Any]] = deepcopy(monitor)
            monitor = {
                "datetime": [],
                "power_kW": [],
                "ram_usage_%": [],
                "wlan_sent_bytes": [], "wlan_recv_bytes": [],
                "disk_usage_%": [],
                "cpu_temp_°C": [], "cpu_freq_MHz": [], "cpu_load_%": [],
            }
        
        df: pd.DataFrame = pd.DataFrame(data=_monitor)#, dtype={"datetime": dt})
        # groupedDf: DataFrameGroupBy = df.groupby(
        #     pd.Grouper(key="datetime", freq="1S"))
        #meanDf.dropna(inplace=True)
        #meanDf["datetime"] = meanDf.
        #meanDf.reset_index(drop=True, inplace=True)
        # print(groupedDf)
        # print(groupedDf.keys)
        #print(meanDf.to_dict(orient="list"))
        print(df.to_dict(orient="records"))#"list"))

        time.sleep(5)
        _event.clear()
        


def calc_power(_time: dt) -> float:
    global curent_time
    delta_t_sec: float = (_time - curent_time).total_seconds()
    curent_time = _time
    return 3.6 / delta_t_sec


def fill_monitor_dict(_time: dt) -> None:
    global monitor
    with lockMain:
        # start filling
        monitor["datetime"].append(_time)
        monitor["power_kW"].append(calc_power(_time))
        # RAM data
        monitor["ram_usage_%"].append(
            psutil.virtual_memory().percent)
        # WLAN data
        monitor["wlan_recv_bytes"].append(
            psutil.net_io_counters().bytes_recv)
        monitor["wlan_sent_bytes"].append(
            psutil.net_io_counters().bytes_sent)
        # disk
        monitor["disk_usage_%"].append(
            psutil.disk_usage('/').percent)
        # CPU data
        monitor["cpu_temp_°C"].append(
            psutil.sensors_temperatures(fahrenheit=False)['cpu_thermal'][0].current)
        monitor["cpu_freq_MHz"].append(
            psutil.cpu_freq().current)
        monitor["cpu_load_%"].append(
            psutil.cpu_percent(interval=None))


# nutze Pin-Nummern des 'J8-Headers' (0-40 Bezeichnung)
gpio.setmode(gpio.BOARD)
# Pin festlegen
PIN_NUMBER: Final[int] = 3
# Pin konfigurieren. Pin 3 (SDA -> I2C) hat einen Pull-Up-Widerstand eingebaut
gpio.setup(PIN_NUMBER, gpio.IN)

# zu Begin des programs auf eine fallende Flanke warten, um für den weiteren 
# Programm-Ablauf saubere Intervalle zu haben
gpio.wait_for_edge(PIN_NUMBER, gpio.FALLING)

curent_time: dt = dt.now()

monitor: dict[str, list[Any]] = {
    "datetime": [],
    "power_kW": [],
    "ram_usage_%": [],
    "wlan_sent_bytes": [], "wlan_recv_bytes": [],
    "disk_usage_%": [],
    "cpu_temp_°C": [], "cpu_freq_MHz": [], "cpu_load_%": [],
}

# initialize objects needed for Treads
event: Event = Event()
lockMain: Lock = Lock()
_thread: Thread = Thread(target=send_to_database, name="sent_to_database", args=([event]))
_thread.start()

#counter: int = 1
while True:

    #print(event.is_set())

    # I2C Pins schalten gegen Masse, also auf fallende Flanke warten
    gpio.wait_for_edge(PIN_NUMBER, gpio.FALLING)
    fill_monitor_dict(dt.now())

    event.set()
    
    # nowTime: dt = dt.now()
    # print(nowTime, calc_power(nowTime))

    # if counter % 5 == 0:
    #     for idx in range(len(monitor["datetime"])-1):
    #         print((monitor["datetime"][idx] - monitor["datetime"][idx+1]).total_seconds())
    #     event.set()
    
    #counter += 1
