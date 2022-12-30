import numpy as np
import pandas as pd

from copy import deepcopy
from datetime import datetime as dt
from threading import Lock, Thread
from typing import Any, Iterable, Optional, Union
from .waits import waitForMinuteChange
from ..customtypes import DeviceMonitorDict, PowermeterMonitorDict, DB
from ..database.services import HardwaremonitorServices, StromzaehlerServices
from ..hardware import Device, ZeroW, RaspberryPi4, WindowsPC


def _preparePowerConsumptionData(
        values: list[list[Union[dt, float, int]]],
        monitorCopy: PowermeterMonitorDict
    ) -> list[list[Union[dt, float, int]]]:
    """prepares power-consumption-data for insertion into MySQL-Database"""

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
    
    return values


def _prepareMonitorDeviceData(
        monitorCopy: DeviceMonitorDict
    ) -> Optional[dict[str, Any]]:
    """prepares device-monitoring-data for insertion into MySQL-Database"""

    # initialize finally to be returned dict
    emptyMonitor: dict[str, Any] = {}

    # handle datetime-object
    medianIdx: int = int( len(monitorCopy["datetime"]) / 2 )
    try:
        medianDt: dt = monitorCopy["datetime"][medianIdx]
    except IndexError:
        # liste ist noch leer
        return None
    medianDt = medianDt.replace(second=0, microsecond=0)
    emptyMonitor["datetime"] = medianDt

    # handle ambient data
    if "ambient_temp_degC" in monitorCopy.keys():
        meanTemp: float = np.mean(monitorCopy["ambient_temp_degC"])
        meanTemp = round(meanTemp, ndigits=1)
        emptyMonitor["ambientTemp_degC_mean"] = float(meanTemp)
    if "ambient_rH_percent" in monitorCopy.keys():
        meanRH: float = np.mean(monitorCopy["ambient_rH_percent"])
        meanRH = round(meanRH, ndigits=1)
        emptyMonitor["ambientRH_percent_mean"] = float(meanRH)

    # handle RAM data
    maxRam: float = max(monitorCopy["ram_load_percent"])
    emptyMonitor["ramLoad_percent_max"] = maxRam

    # handle disk-usage data
    maxDiskUsage: float = max(monitorCopy["disk_usage_percent"])
    emptyMonitor["diskUsage_percent_max"] = maxDiskUsage

    # Network-IO
    sentBytes: int = (
        monitorCopy["network_sent_bytes"][-1] - monitorCopy["network_sent_bytes"][0])
    recvBytes: int = (
        monitorCopy["network_recv_bytes"][-1] - monitorCopy["network_recv_bytes"][0])
    emptyMonitor["network_sent_bytes"] = sentBytes
    emptyMonitor["network_recv_bytes"] = recvBytes

    # handle CPU Frequency
    minFreq: float = min(monitorCopy["cpu_freq_percent"])
    meanFreq: float = np.mean(monitorCopy["cpu_freq_percent"])
    meanFreq = round(meanFreq, ndigits=1)
    maxFreq: float = max(monitorCopy["cpu_freq_percent"])
    emptyMonitor["cpuFreq_percent_min"] = minFreq
    emptyMonitor["cpuFreq_percent_mean"] = float(meanFreq)
    emptyMonitor["cpuFreq_percent_max"] = maxFreq

    # handle CPU Load
    minLoad: float = min(monitorCopy["cpu_load_percent"])
    meanLoad: float = np.mean(monitorCopy["cpu_load_percent"])
    meanLoad = round(meanLoad, ndigits=1)
    maxLoad: float = max(monitorCopy["cpu_load_percent"])
    emptyMonitor["cpuLoad_percent_min"] = minLoad
    emptyMonitor["cpuLoad_percent_mean"] = float(meanLoad)
    emptyMonitor["cpuLoad_percent_max"] = maxLoad

    # handle CPU Temperature
    minTemp: float = min(monitorCopy["cpu_temp_degC"])
    meanTemp: float = np.mean(monitorCopy["cpu_temp_degC"])
    meanTemp = round(meanTemp, ndigits=1)
    maxTemp: float = max(monitorCopy["cpu_temp_degC"])
    emptyMonitor["cpuTemp_degC_min"] = round(minTemp, ndigits=1)
    emptyMonitor["cpuTemp_degC_mean"] = float(meanTemp)
    emptyMonitor["cpuTemp_degC_max"] = round(maxTemp, ndigits=1)

    return emptyMonitor


def _ingestHardwareMonitorData(
        device: Device,
        monitorDevice: DeviceMonitorDict,
        lock: Lock
    ) -> None:

    # create an empty DeviceMonitorDict
    emptyDict: DeviceMonitorDict = device.getEmptyDeviceMonitorDict()

    # jetzt das ganze Prozedere für das Device-Monitoring noch durchführen
    # eine deepcopy des ursprünglichen monitor-dicts machen und anschließend
    # dieses wieder als neu prepariertes Object neu initialisieren
    with lock:
        monitorCopyDevice: DeviceMonitorDict = deepcopy(monitorDevice)
        monitorDevice.update(emptyDict)

    # Daten für db-ingest aufbereiten
    monitorDeviceValues: Optional[dict[str, Any]] = _prepareMonitorDeviceData(
        monitorCopyDevice
    )

    # preparierten Daten in die MySQL-DB einfügen
    if monitorDeviceValues is not None:
        hwmonitorServices.insertMonitoringData(monitorDeviceValues)


def _ingestPowerConsumptionData(
        powerConsumptionValues: list[list[Union[dt, float, int]]],
        monitorPowermeter: PowermeterMonitorDict,
        lock: Lock
    ) -> list[list[Union[dt, float, int]]]:

    # Beginne mit den Stromverbrauchs-Daten
    # eine deepcopy des ursprünglichen monitor-dicts machen und anschließend
    # dieses wieder als leeres Object neu initialisieren
    with lock:

        # Prüfen ob überhaupt schon Daten vorliegen
        if len(monitorPowermeter["datetime"]) == 0:
            # wenn noch keine Daten vorliegen, dann wieder an den Anfang der
            # Schleife zurückgehen
            return powerConsumptionValues

        monitorCopyPowermeter: PowermeterMonitorDict = deepcopy(monitorPowermeter)
        monitorPowermeter.update( {"datetime": [], "power_kW": []} )

    # bereite die Daten auf, dass sie 1-zu-1 in die DB eingespeist werden können
    powerConsumptionValues = _preparePowerConsumptionData(
        powerConsumptionValues, monitorCopyPowermeter
    )

    # in die MySQL-DB einfügen, bis auf die allerletzte Zeile
    stromzaehlerServices.insertPowerConsumptionData(powerConsumptionValues[:-1])

    # so setzen, dass die allerletzte Zeile für den nächsten Durchlauf übrig
    # bleibt
    return powerConsumptionValues[-1:]


def _ingestHardwareMonitorAndPowerConsumptionIntoDb(
        device: Device, 
        monitorDevice: DeviceMonitorDict,
        lock: Lock,
        monitorPowermeter: PowermeterMonitorDict
    ) -> None:
    
    # wird die in die MySQL-DB einzusetzenden Werte/Reihen aufnehmen
    powerConsumptionValues: list[list[Union[dt, float, int]]] = []

    while True:

        # Prozedur soll immer nur zum Beginn einer neuen Minute durchlaufen
        waitForMinuteChange()

        # ingeste die Stromverbrauchsdaten
        powerConsumptionValues = _ingestPowerConsumptionData(
            powerConsumptionValues, monitorPowermeter, lock)

        # ingeste die Hardware-Monitor-Daten
        _ingestHardwareMonitorData(device, monitorDevice, lock)


def _ingestOnlyHardwareMonitorIntoDb(
        device: Device, 
        monitorDevice: DeviceMonitorDict,
        lock: Lock
    ) -> None:

    while True:

        # Prozedur soll immer nur zum Beginn einer neuen Minute durchlaufen
        waitForMinuteChange()

        # ingeste die Hardware-Monitor-Daten
        _ingestHardwareMonitorData(device, monitorDevice, lock)


# initialize globale Service-Layer
stromzaehlerServices: StromzaehlerServices = StromzaehlerServices()
hwmonitorServices: HardwaremonitorServices = HardwaremonitorServices()


def ingestIntoDb(
        device: Device,
        monitorDevice: DeviceMonitorDict,
        lock: Lock,
        monitorPowermeter: Optional[PowermeterMonitorDict]=None
    ) -> None:
    """starts Database-ingestion Thread"""

    # ingestThread: Thread
    if isinstance(device, ZeroW):
        # aktive Tabelle auswählen auf der operiert werden soll
        hwmonitorServices.setActiveTable(DB.hardwaremonitor.ZeroW)
        # # Thread initialisieren
        # ingestThread = Thread(
        #     target=_ingestHardwareMonitorAndPowerConsumptionIntoDb,
        #     name="ingestThread",
        #     args=([device, monitorDevice, lock, monitorPowermeter])
        # )
        if monitorPowermeter is None:
            raise ValueError("passed parameter 'monitorPowermeter' must not be None!")
        else:
            _ingestHardwareMonitorAndPowerConsumptionIntoDb(
                device, monitorDevice, lock, monitorPowermeter
            )
    else:
        # aktive Tabelle auswählen auf der operiert werden soll
        if isinstance(device, RaspberryPi4):
            hwmonitorServices.setActiveTable(DB.hardwaremonitor.RaspberryPi4)
        elif isinstance(device, WindowsPC):
            hwmonitorServices.setActiveTable(DB.hardwaremonitor.WindowsPC)
        else:
            raise TypeError(
                f"initialisiertes Device enthält einen unbekannten Typ: {type(device)}"
            )
        # ingestThread = Thread(
        #     target=_ingestOnlyHardwareMonitorIntoDb,
        #     name="",
        #     args=([device, monitorDevice, lock])
        # )
        _ingestOnlyHardwareMonitorIntoDb(device, monitorDevice, lock)
    # ingestThread.start()
