from main import threads
from main.customtypes import DeviceMonitorDict, PowermeterMonitorDict
from main.hardware import ZeroW
from threading import Lock


# initialize Device-object this code is running on
zeroW: ZeroW = ZeroW()

# initialize globally shared Dictionary and lock
monitorDevice: DeviceMonitorDict = zeroW.getEmptyDeviceMonitorDict()
monitorPowermeter: PowermeterMonitorDict = { "datetime": [], "power_kW": [] }
globalLock: Lock = Lock()

# start Device-monitoring-Thread
threads.monitorDevice(zeroW, monitorDevice, globalLock)

# start powerMeter-Thread
threads.powermeterThread(zeroW, monitorPowermeter, globalLock)

# start db-ingestion-Thread as Main-Thread
threads.ingestIntoDb(zeroW, monitorDevice, globalLock, monitorPowermeter)