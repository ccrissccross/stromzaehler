from datetime import datetime as dt
from threading import Lock
from ..customtypes import MonitorDict
from ..hardware import S0interface


def _calcPower(_time: dt) -> float:
    global currentTime
    delta_t_sec: float = (_time - currentTime).total_seconds()
    currentTime = _time
    return 3.6 / delta_t_sec


def _fillMonitorDict(_time: dt, monitor: MonitorDict) -> None:
    with lock:
        # start filling
        monitor["datetime"].append(_time)
        monitor["power_kW"].append(_calcPower(_time))


# initialize Lock needed for this Thread
lock: Lock = Lock()

# initialisiere S0-Schnittstelle
s0interface: S0interface = S0interface()
s0interface.wasteSignal()

# initialize time to get clean intervals for calculating consumed electric power
currentTime: dt = dt.now()


def mainThread(monitor: MonitorDict) -> None:
    """
    Main loop waiting for S0-interface to receive a signal, and then storing its
    state in a globally shared python-Dictionary.
    """
    while True:
        s0interface.waitForSignal()
        _fillMonitorDict(dt.now(), monitor)