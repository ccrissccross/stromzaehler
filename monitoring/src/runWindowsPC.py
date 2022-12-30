from main import threads
from main.customtypes import DeviceMonitorDict
from main.hardware import WindowsPC
from threading import Lock


# initialize Device-object this code is running on
winPC: WindowsPC = WindowsPC()

# initialize globally shared Dictionary and lock
monitorDevice: DeviceMonitorDict = winPC.getEmptyDeviceMonitorDict()
globalLock: Lock = Lock()

# start Device-monitoring-Thread
threads.monitorDevice(winPC, monitorDevice, globalLock)

# start db-ingestion-Thread as Main-Thread
threads.ingestIntoDb(winPC, monitorDevice, globalLock)