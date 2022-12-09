from main import threads
from main.customtypes import MonitorDict


# initialize globally shared Dictionary
monitor: MonitorDict = { "datetime": [], "power_kW": [] }

# start db-ingestion-Thread
threads.ingestIntoDb(monitor)

# start main-function of main-Thread
threads.mainThread(monitor)