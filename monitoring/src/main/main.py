#!/home/pi/Dev/python/stromzaehler/venv/bin/python3


import threads

import RPi.GPIO as gpio

from datetime import datetime as dt, timedelta
from threading import Event, Lock, Thread
from typing import Any, Final, Iterable, Union


def calc_power(_time: dt) -> float:
    global curent_time
    delta_t_sec: float = (_time - curent_time).total_seconds()
    curent_time = _time
    return 3.6 / delta_t_sec


def fill_monitor_dict(_time: dt) -> None:
    global monitor
    with lock:
        # start filling
        monitor["datetime"].append(_time)
        monitor["power_kW"].append(calc_power(_time))

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

monitor: dict[str, list[Union[dt, float]]] = { "datetime": [], "power_kW": [] }

# initialize objects needed for Treads
lock: Lock = Lock()
_thread: Thread = Thread(target=threads.ingestIntoDb, name="ingestIntoDb", args=([monitor]))
_thread.start()


while True:

    # I2C Pins schalten gegen Masse, also auf fallende Flanke warten
    gpio.wait_for_edge(PIN_NUMBER, gpio.FALLING)
    fill_monitor_dict(dt.now())
