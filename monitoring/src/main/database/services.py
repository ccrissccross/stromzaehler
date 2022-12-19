from datetime import datetime as dt
from typing import Union
from .repo import StromzaehlerRepo
from ..customtypes import StromzaehlerTableData, SqlServerResultStromzaehler


class StromzaehlerServices:
    
    def __init__(self, connect_from: str="monitor") -> None:
        self._repo: StromzaehlerRepo = StromzaehlerRepo(connect_from)
    
    def insertPowerConsumptionData(
        self, values: list[list[Union[dt, float]]]) -> None:
        """calls appropriate _repo-method and passes data as parameter"""
        self._repo.insertManyRows(values)
    
    def getPowerConsumptionData(self) -> SqlServerResultStromzaehler:
        """returns the ENTIRE table as a SqlServerResult-TypedDict"""

        queryFailed: bool
        allRows: StromzaehlerTableData
        queryFailed, allRows = self._repo.getAllRows()

        if queryFailed:
            return SqlServerResultStromzaehler(
                status_code=500, data=allRows)
        else:
            return SqlServerResultStromzaehler(
                status_code=200, data=allRows)
