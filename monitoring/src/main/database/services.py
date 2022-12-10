from datetime import datetime as dt
from typing import Union
from .repo import StromzaehlerRepo


class StromzaehlerServices:
    
    def __init__(self) -> None:
        self._repo: StromzaehlerRepo = StromzaehlerRepo()
    
    def insertPowerConsumptionData(
        self, values: list[list[Union[dt, float]]]) -> None:
        """creates SQL-statement and calls _repo-method to execute statement"""

        sqlStatement: str = (
            "INSERT INTO stromzaehler"
            "(datetime, meanPower_perSec_kW, impulses_perSec) "
            "VALUES "
            "(%s, %s, %s)"
        )
        self._repo.insertManyRows(values, sqlStatement)
