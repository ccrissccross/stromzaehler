from flask import Flask, make_response
from flask.wrappers import Response
from ....monitoring.src.main.customtypes import SqlServerResultStromzaehler
from ....monitoring.src.main.database.services import StromzaehlerServices


sServices: StromzaehlerServices = StromzaehlerServices()


app = Flask(__name__)


@app.get("/")
def getPowerConsumptionData():
    # fetch result from database-server
    sqlServerResp: SqlServerResultStromzaehler = sServices.getPowerConsumptionData()
    # create response from it
    response: Response = make_response(sqlServerResp["data"])
    response.status_code = sqlServerResp["status_code"]
    response.headers.add("Access-Control-Allow-Origin", "*")
    # ...and return it
    return response
