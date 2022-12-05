#!/home/pi/Dev/python/stromzaehler/venv/bin/python3

import time
import RPi.GPIO as gpio

import psutil

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
    
    print(f"CPU Temperatur: {psutil.sensors_temperatures(fahrenheit=False)['cpu_thermal'][0].current:.1f} °C")
    print(f"CPU   Frequenz: {psutil.cpu_freq().current} MHz")
    print(f"CPU       Last: {psutil.cpu_percent(interval=None)} %")
    print(f"RAM Auslastung: {psutil.virtual_memory().percent} %")
    print(f"RAM      total: {psutil.virtual_memory().total} bytes")
    print(f"RAM  available: {psutil.virtual_memory().available} bytes")
    print(f"WLAN  gesendet: {psutil.net_io_counters(nowrap=False).bytes_sent} bytes")
    print(f"WLAN empfangen: {psutil.net_io_counters().bytes_recv} bytes")
    print()
    #break
    time.sleep(1)
    continue
    # I2C Pins schalten gegen Masse, also auf fallende Flanke warten
    gpio.wait_for_edge(pinNumber, gpio.FALLING)
    calc_power(dt.now())
   

