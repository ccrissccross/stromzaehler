import platform
import psutil

from datetime import datetime as dt
from threading import Lock, Thread
from typing import NamedTuple
from .waits import waitForSecondChange
from ..customtypes import DeviceMonitorDict
from ..hardware import Device, DHTSensor, RaspberryPi, WindowsPC


# what os is this running on?
PLATFORM: str = platform.system()

if PLATFORM == "Windows":
    # the following is a Windows OS-specific Interface to WMI (="Windows Management
    # Instrumentation"), that allows for accessing and control of System-Settings
    # and statuses
    from wmi import WMI

    msacpiThermal: list[object] = WMI(namespace="root\wmi").MSAcpi_ThermalZoneTemperature()
    noCores: int = len(msacpiThermal)


class _HardwareStats(NamedTuple):
    virtMem: float
    diskUsage: float
    netIO_bytes_sent: int
    netIO_bytes_recv: int
    cpuTemp: float
    cpuFreq: float
    cpuLoad: float


def _readWindowsCPUTemp() -> float:
    cumTemp: float = 0
    for thermalZoneObj in msacpiThermal:
        cumTemp += thermalZoneObj.CurrentTemperature
    # temperature is in K and additionally needs to be divided by 10
    meanTemp: float = cumTemp / noCores / 10 - 273.15
    return meanTemp


def _readUbuntuServerCPUTemp() -> float:
    # CPU-Temp on a Ubuntu-Server on a RaspberryPi needs to be accessed via
    # 'cpu_thermal' which then returns a list with only one element. No 
    return psutil.sensors_temperatures()["cpu_thermal"][0].current


def _readHardwareStats(root: str) -> _HardwareStats:
    """reads Hardware statistics data and returns them as NamedTuple"""
    
    # ram
    virtMem: float = psutil.virtual_memory().percent

    # disk
    diskUsage: float = psutil.disk_usage(root).percent

    # network
    netIO = psutil.net_io_counters()

    # cpu-stuff
    cpuTemp: float
    if PLATFORM == "Windows":
        cpuTemp = _readWindowsCPUTemp()
    else:
        cpuTemp = _readUbuntuServerCPUTemp()
    cpuFreq: float = psutil.cpu_freq().current
    cpuLoad: float = psutil.cpu_percent()

    return _HardwareStats(
        virtMem, diskUsage, netIO.bytes_sent, netIO.bytes_recv, cpuTemp,
        cpuFreq, cpuLoad
    )


def _fillMonitorDict(monitor: DeviceMonitorDict, hardwareStats: _HardwareStats) -> None:
    """fills the DeviceMonitorDict with _HardwareStats-data"""
    monitor["ram_load_percent"].append(hardwareStats.virtMem)
    monitor["disk_usage_percent"].append(hardwareStats.diskUsage)
    monitor["network_sent_bytes"].append(hardwareStats.netIO_bytes_sent)
    monitor["network_recv_bytes"].append(hardwareStats.netIO_bytes_recv)
    monitor["cpu_freq_percent"].append(hardwareStats.cpuFreq)
    monitor["cpu_load_percent"].append(hardwareStats.cpuLoad)
    monitor["cpu_temp_degC"].append(hardwareStats.cpuTemp)


def _monitorRaspberryPi(device: RaspberryPi, monitor: DeviceMonitorDict, lock: Lock) -> None:
    """if this code runs on a RaspberryPi this method gets invoked"""

    # initialisiere Temperatur -und Feuchtesensor
    dht: DHTSensor = device.dhtSensor

    # -> '/'
    rootDir: str = device.rootDir

    while True:

        # Prozedur soll immer nur zum Beginn einer neuen Sekunde durchlaufen
        curTime: dt = waitForSecondChange()

        # get measurement of ambient DHT-Sensor
        temp, rH = dht.getMeasurement()

        # read Statistics of Hardware
        hardwareStats: _HardwareStats = _readHardwareStats(rootDir)

        # fill DeviceMonitorDict
        with lock:
            monitor["datetime"].append(curTime)
            monitor["ambient_temp_degC"].append(temp)
            monitor["ambient_rH_percent"].append(rH)
            _fillMonitorDict(monitor, hardwareStats)


def _monitorWindowsPC(device: WindowsPC, monitor: DeviceMonitorDict, lock: Lock) -> None:
    """if this code runs on a Windows-PC this method gets invoked"""

    # -> 'C:\\'
    rootDir: str = device.rootDir

    while True:

        # Prozedur soll immer nur zum Beginn einer neuen Sekunde durchlaufen
        curTime: dt = waitForSecondChange()

        # read Statistics of Hardware
        hardwareStats: _HardwareStats = _readHardwareStats(rootDir)

        # fill DeviceMonitorDict
        with lock:
            monitor["datetime"].append(curTime)
            _fillMonitorDict(monitor, hardwareStats)
            


def monitorDevice(device: Device, monitor: DeviceMonitorDict, lock: Lock) -> None:
    """initializes Thread and starts it"""
    
    monitorDeviceThread: Thread
    if isinstance(device, RaspberryPi):
        monitorDeviceThread = Thread(target=_monitorRaspberryPi, args=([device, monitor, lock]))
    elif isinstance(device, WindowsPC):
        monitorDeviceThread = Thread(target=_monitorWindowsPC, args=([device, monitor, lock]))
    else:
        raise TypeError(
            "Device-Type is not correct. It must be either of type <RaspberryPi> "
            f" or of type <WindowsPC> but yours is of type {type(device)}"
        )
    monitorDeviceThread.start()
