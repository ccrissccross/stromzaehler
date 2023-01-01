import platform
if platform.system() != "Windows":
	import board

from abc import ABC, abstractmethod, abstractproperty
from .dhtsensors import DHTSensor, DHT11Sensor, DHT22Sensor
from .powermeter import S0interface
from ..customtypes import DeviceMonitorDict


class Device(ABC):

    def __init__(self) -> None:
        self._ip_address: str
    
    @property
    def IP_ADDRESS(self) -> str:
        """return the ip-address of this device"""
        return self._ip_address

    @abstractmethod
    def getEmptyDeviceMonitorDict(self) -> DeviceMonitorDict:
        """returns an empty DeviceMonitorDict Dictionary"""
        raise NotImplementedError
    
    @abstractproperty
    def rootDir(self) -> str:
        """returns the root-dir as a string"""
        raise NotImplementedError


class RaspberryPi(Device):

    def __init__(self) -> None:
        self._dht_sensor_type: DHTSensor
        self._dht_signal_pin = None
    
    @property
    def dhtSensor(self) -> DHTSensor:
        """instantiates a DHTSensor-object and returns it"""
        if self._dht_sensor_type is DHT11Sensor:
            return DHT11Sensor(self._dht_signal_pin)
        elif self._dht_sensor_type is DHT22Sensor:
            return DHT22Sensor(self._dht_signal_pin)
        else:
            raise TypeError(
                f"definierter Sensor-Typ {self._dht_sensor_type} ist nicht bekannt")
    
    @property
    def rootDir(self) -> str:
        """returns the root-dir as a string, on Ubuntu-Server -> '/' """
        return '/'
    
    def getEmptyDeviceMonitorDict(self) -> DeviceMonitorDict:
        """returns an empty DeviceMonitorDict Dictionary"""
        return {
            "datetime": [],
            "ambient_temp_degC": [], "ambient_rH_percent": [],
            "cpu_freq_percent": [], "cpu_load_percent": [], "cpu_temp_degC": [],
            "ram_load_percent": [], "disk_usage_percent": [], "network_sent_bytes": [],
            "network_recv_bytes": []
        }


class ZeroW(RaspberryPi):

    def __init__(self) -> None:
        self._ip_address: str = "192.168.178.26"
        self._dht_sensor_type = DHT11Sensor
        self._dht_signal_pin = board.D18
    
    @property
    def powermeter(self) -> S0interface:
        """instantiates a S0interface-object and returns it"""
        return S0interface()


class RaspberryPi4(RaspberryPi):

    def __init__(self) -> None:
        self._ip_address: str = "192.168.178.23"
        self._dht_sensor_type = DHT22Sensor
        self._dht_signal_pin = board.D4


class WindowsPC(Device):

    def __init__(self) -> None:
        self._ip_address: str = "192.168.178.22"
    
    @property
    def rootDir(self) -> str:
        """returns the root-dir as a string, on a Windows-PC -> 'C:\\' """
        return "C:\\"
    
    def getEmptyDeviceMonitorDict(self) -> DeviceMonitorDict:
        """returns an empty DeviceMonitorDict Dictionary"""
        return {
            "datetime": [],
            "cpu_freq_percent": [], "cpu_load_percent": [], "cpu_temp_degC": [],
            "ram_load_percent": [], "disk_usage_percent": [], "network_sent_bytes": [],
            "network_recv_bytes": []
        }