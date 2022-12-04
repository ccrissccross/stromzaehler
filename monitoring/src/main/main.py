#!/home/pi/Dev/python/stromzaehler/venv/bin/python3

import time
import RPi.GPIO as gpio

from datetime import datetime as dt, timedelta

curent_time: dt = dt.now()

def calc_power(_time: dt) -> None:
    global curent_time
    delta_t_sec: float = (_time - curent_time).total_seconds()
    power_kW: float = 3.6 / delta_t_sec
    print(_time, power_kW)
    curent_time = _time

# nutze Pin-Nummern des 'J8-Headers' (0-40 Bezeichnung)
gpio.setmode(gpio.BOARD)

# Pin festlegen
pinNumber: int = 3
# Pin konfigurieren. Pin 3 (SDA -> I2C) hat einen Pull-Up-Widerstand eingebaut
gpio.setup(pinNumber, gpio.IN)

while True:
    
    # I2C Pins schalten gegen Masse, also auf fallende Flanke warten
    gpio.wait_for_edge(pinNumber, gpio.FALLING)
    calc_power(dt.now())
    

