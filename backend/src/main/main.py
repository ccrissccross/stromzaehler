from flask import Flask, request, make_response
from flask.wrappers import Response
from ....monitoring.src.main.database.services import StromzaehlerServices


sServices: StromzaehlerServices = StromzaehlerServices()


app = Flask(__name__)


@app.get("/")
def getPowerConsumptionData():
    try:
        if request.method == "GET":
            response: Response = make_response(
                sServices.getPowerConsumptionData())
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
    except Exception as err:
        print(err.args)
        raise