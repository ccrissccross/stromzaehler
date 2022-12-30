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

# start db-ingestion-Thread
threads.ingestIntoDb(zeroW, monitorDevice, globalLock, monitorPowermeter)

# start powerMeter-function as main-Thread
threads.powermeterFunc(zeroW, monitorPowermeter, globalLock)