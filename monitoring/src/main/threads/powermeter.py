from datetime import datetime as dt
from threading import Lock, Thread
from ..customtypes import PowermeterMonitorDict
from ..hardware import S0interface, ZeroW



def _calcPower(_time: dt) -> float:
    global currentTime
    delta_t_sec: float = (_time - currentTime).total_seconds()
    currentTime = _time
    return 3.6 / delta_t_sec


def _fillMonitorDict(_time: dt, monitor: PowermeterMonitorDict, lock: Lock) -> None:
    """calculates electric power and fills PowermeterMonitorDict"""

    # calculate power before filling monitor-dict
    power: float = _calcPower(_time)

    # if power is too big (rarely happens under heavy load -> "Sensorprellung")
    # limit: 3 Phasen à 63A à 240V == 45.36kW
    if power > 46:
        # Werte darüber sind unmöglich
        return

    with lock:
        # start filling
        monitor["datetime"].append(_time)
        monitor["power_kW"].append(power)


# initialize time to get clean intervals for calculating consumed electric power
currentTime: dt = dt.now()


def _powermeterFunc(device: ZeroW, monitor: PowermeterMonitorDict, lock: Lock) -> None:
    """
    Main loop waiting for S0-interface to receive a signal, and then storing its
    state in a globally shared python-Dictionary.
    """
    
    # initialisiere S0-Schnittstelle
    s0interface: S0interface = device.powermeter
    s0interface.wasteSignal()

    while True:
        s0interface.waitForSignal()
        _fillMonitorDict(dt.now(), monitor, lock)


def powermeterThread(device: ZeroW, monitor: PowermeterMonitorDict, lock: Lock) -> None:
    """starts the powermeter-Thread"""
    powermeterThread: Thread = Thread(
        target=_powermeterFunc,
        name="powermeterThread",
        args=([device, monitor, lock])
    )
    powermeterThread.start()