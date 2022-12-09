#!/home/pi/Dev/python/stromzaehler/venv/bin/python3

from main import threads

from main.customtypes import MonitorDict
from threading import Thread


# initialize globally shared Dictionary
monitor: MonitorDict = { "datetime": [], "power_kW": [] }

# start db-ingestion-Thread
ingestThread: Thread = Thread(target=threads.ingestIntoDb, args=([monitor]))
ingestThread.start()

# start main-function of main-Thread
threads.mainThread(monitor)