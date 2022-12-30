from time import sleep
from datetime import datetime as dt, timedelta


def waitForMinuteChange() -> dt:
    """waits until Minute changes of the current datetime"""
    # welche Uhrzeit ist gerade
    nowTime: dt = dt.now()
    # bis zu welcher Uhrzeit soll geschlafen werden
    waitUntil: dt = nowTime + timedelta(minutes=1)
    waitUntil = waitUntil.replace(second=0, microsecond=0)
    # differenz in sekunden berechnen, just in case positiv zwingen
    sleepTime: float = abs( (waitUntil - nowTime).total_seconds() )
    # solange schlafen bis differenz überwunden
    sleep(sleepTime)
    return waitUntil


def waitForSecondChange() -> dt:
    """waits until Second changes of the current datetime"""
    # welche Uhrzeit ist gerade
    nowTime: dt = dt.now()
    # bis zu welcher Uhrzeit soll geschlafen werden
    waitUntil: dt = nowTime + timedelta(seconds=1)
    waitUntil = waitUntil.replace(microsecond=0)
    # differenz in sekunden berechnen, just in case positiv zwingen
    sleepTime: float = abs( (waitUntil - nowTime).total_seconds() )
    # solange schlafen bis differenz überwunden
    sleep(sleepTime)
    return waitUntil