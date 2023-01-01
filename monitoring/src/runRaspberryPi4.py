from main import threads
from main.customtypes import DeviceMonitorDict
from main.hardware import RaspberryPi4
from threading import Lock


# initialize Device-object this code is running on
pi4: RaspberryPi4 = RaspberryPi4()

# initialize globally shared Dictionary and lock
monitorDevice: DeviceMonitorDict = pi4.getEmptyDeviceMonitorDict()
globalLock: Lock = Lock()

# start Device-monitoring-Thread
threads.monitorDevice(pi4, monitorDevice, globalLock)

# start db-ingestion-Thread as Main-Thread
threads.ingestIntoDb(pi4, monitorDevice, globalLock)