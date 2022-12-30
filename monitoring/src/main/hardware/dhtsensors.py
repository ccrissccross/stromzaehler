import platform
if platform.system() != "Windows":
	from adafruit_dht import DHTBase, DHT11, DHT22


class DHTSensor:

    def __init__(self) -> None:
        self._sensor: DHTBase

    def getMeasurement(self) -> tuple[float, float]:
        """conducts measurements and returns result as tuple"""
        while True:
            # try to get measurements, quite often fails, repeat solves that
            try:
                _temp = self._sensor.temperature
                _rH = self._sensor.humidity
                if _temp is None or _rH is None:
                    raise Exception
            except Exception:
                # imideately measure again
                continue
            
            return _temp, _rH


class DHT11Sensor(DHTSensor):

    def __init__(self, pin) -> None:
        self._sensor: DHT11 = DHT11(pin)


class DHT22Sensor(DHTSensor):

    def __init__(self, pin) -> None:
        self._sensor: DHT22 = DHT22(pin)
