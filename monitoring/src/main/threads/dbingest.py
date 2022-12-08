import time

import mysql.connector
import numpy as np
import pandas as pd

from copy import deepcopy
from datetime import datetime as dt, timedelta
from threading import Event, Lock
from typing import Any, Iterable, Union

from mysql.connector.connection import MySQLConnection


def waitForMinuteChange() -> None:
    # welche Uhrzeit ist gerade
    nowTime: dt = dt.now()
    # bis zu welcher Uhrzeit soll geschlafen werden
    waitUntil: dt = nowTime + timedelta(minutes=1)
    waitUntil = waitUntil.replace(second=0, microsecond=0)
    # differenz in sekunden berechnen, just in case positiv zwingen
    sleepTime: float = abs( (waitUntil - nowTime).total_seconds() )
    # solange schlafen bis differenz überwunden
    time.sleep(sleepTime)


def ingestIntoDb(
    monitor: dict[str, list[Union[dt, float]]]) -> None:

    # setup MySQL connection
    mysqlConnection: MySQLConnection = mysql.connector.connect(
        user="pythonConnection", host="192.168.178.23", database="zeroW")
    # Cursor-Objekt auf dem die DB-Operationen ausgeführt werden
    cursor = mysqlConnection.cursor()
    
    # setup des insert-statement
    sqlStatement: str = (
        "INSERT INTO stromzaehler "
        "(datetime, meanPower_perSec_kW, impulses_perSec) "
        "VALUES "
        "(%s, %s, %s)")
    # wird die in die MySQL-DB einzusetzenden Werte/Reihen aufnehmen
    values: list[list[Union[dt, float]]] = []

    while True:

        waitForMinuteChange()

        # eine deepcopy des ursprünglichen monitor-dicts machen und anschließend
        # dieses wieder als leeres Object neu initialisieren
        with lock:

            # Prüfen ob überhaupt schon Daten vorliegen
            if len(monitor["datetime"]) == 0:
                # wenn noch keine Daten vorliegen, dann wieder an den Anfang der
                # Schleife zurückgehen
                continue

            monitorCopy: dict[str, list[Any]] = deepcopy(monitor)
            monitor.update(datetime=[], power_kW=[])
        
        # einen aggregierten df erzeugen aus dem kopierten monitor-dict
        dfAgg: pd.DataFrame = (
            pd.DataFrame(data=monitorCopy)
            .groupby(pd.Grouper(key="datetime", freq="1S"))
            ["power_kW"]
            .agg([np.mean, len])
            .dropna())
        
        # einen Iterator aller Zeilen dieses aggregierten df's erzeugen
        itertuples: Iterable[tuple[Any]] = dfAgg.itertuples()

        # dieser Fall tritt dann ein, wenn die Methode das erste mal durchläuft
        if len(values) == 0:
            for row in itertuples:
                values.append([row.Index.to_pydatetime(), row.mean, row.len])

        else:

            # hole dir die erste Reihe aus dem aggregierten Result-df
            firstRow = next(itertuples)

            # Der Fall verhindert dass der Primär-Key doppelt vorhanden sein 
            # wird. Also der Fall prüft ob es Überschneidungen beim Zeitstempel
            # gibt und kombiniert die Werte der beiden identischen Zeitstempel.
            if firstRow.Index == values[0][0]:

                # was waren die Werte beim alten Durchlauf
                oldMean: float = values[0][1]
                oldCount: int = values[0][2]
                # und was haben die Werte jetzt
                newMean: float = firstRow.mean
                newCount: int = firstRow.len
                # Mittelwert und Count neu bilden
                count: int = oldCount + newCount
                values[0][1] = ((oldMean*oldCount) + (newMean*newCount)) / (count)
                values[0][2] = count

            else:
                values.append(
                    [
                        firstRow.Index.to_pydatetime(),
                        firstRow.mean,
                        firstRow.len])
            
            # alle weiteren Zeilen des aggregierten df's durchiterieren
            for row in itertuples:
                values.append(
                    [
                        row.Index.to_pydatetime(),
                        row.mean,
                        row.len])

        # in die MySQL-DB einfügen, bis auf die allerletzte Zeile
        cursor.executemany(sqlStatement, values[:-1])
        mysqlConnection.commit()

        # so setzen, dass die allerletzte Zeile für den nächsten Durchlauf übrig
        # bleibt
        values = values[-1:]


lock: Lock = Lock()