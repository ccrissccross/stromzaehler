from main import threads
from main.customtypes import MonitorDict
from threading import Lock


# initialize globally shared Dictionary and lock
monitor: MonitorDict = { "datetime": [], "power_kW": [] }
globalLock: Lock = Lock()

# start db-ingestion-Thread
threads.ingestIntoDb(monitor, globalLock)

# start main-function of main-Thread
threads.mainThread(monitor, globalLock)