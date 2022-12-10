from datetime import datetime as dt
from typing import Union
from .repo import StromzaehlerRepo
from ..customtypes import StromzaehlerTableData


class StromzaehlerServices:
    
    def __init__(self) -> None:
        self._repo: StromzaehlerRepo = StromzaehlerRepo()
    
    def insertPowerConsumptionData(
        self, values: list[list[Union[dt, float]]]) -> None:
        """calls appropriate _repo-method and passes data as parameter"""
        self._repo.insertManyRows(values)
    
    def getPowerConsumptionData(self) -> StromzaehlerTableData:
        """returns the ENTIRE table as TypedDict"""

        queryRes: StromzaehlerTableData = StromzaehlerTableData(
            datetime=[], power_kW=[], agg_consumption_Wh=[])

        aggConsumption: int = 0
        for (datetime, power_kW, agg_consumption_Wh) in self._repo.getAllRows():
            queryRes["datetime"].append(datetime)
            queryRes["power_kW"].append(power_kW)
            aggConsumption += agg_consumption_Wh
            queryRes["agg_consumption_Wh"].append(aggConsumption)
        
        return queryRes