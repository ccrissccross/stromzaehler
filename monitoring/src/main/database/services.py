from datetime import datetime as dt
from typing import Any, Optional, Union

from .repo import HardwaremonitorRepo, StromzaehlerRepo
from ..customtypes import StromzaehlerTableData, SqlServerResultStromzaehler, DB


class StromzaehlerServices:
    
    def __init__(self, table_name: str=DB.stromzaehler.ZeroW) -> None:
        self._repo: StromzaehlerRepo = StromzaehlerRepo(table_name)
    
    def setGunicornLogger(self) -> None:
        """wires the gunicorn-logger to this class' self._repoLogger"""
        self._repo.setGunicornLogger()
    
    def insertPowerConsumptionData(
        self, values: list[list[Union[dt, float, int]]]) -> None:
        """calls appropriate _repo-method and passes data as parameter"""
        self._repo.insertPowerConsumptionData(values)
    
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


class HardwaremonitorServices:

    def __init__(self, table_name: Optional[str]=None) -> None:
        self._repo: Optional[HardwaremonitorRepo]
        if table_name is None:
            self._repo = None
        else:
            self._repo = HardwaremonitorRepo(table_name)
    
    def setActiveTable(self, table_name: str) -> None:
        self._repo = HardwaremonitorRepo(table_name)

    def setGunicornLogger(self) -> None:
        """wires the gunicorn-logger to this class' self._repoLogger"""
        if self._repo is None:
            raise AttributeError(
                "du musst erst mit 'setActiveTable()'-method eine Tabelle auswählen"
            )
        self._repo.setGunicornLogger()
    
    def insertMonitoringData(self, values: dict[str, Any]) -> None:
        """
        Inserts hardware-monitoring values, which consists of a single line of
        data
        """
        if self._repo is None:
            raise AttributeError(
                "du musst erst mit 'setActiveTable()'-method eine Tabelle auswählen"
            )
        self._repo.insertMonitoringData(values)