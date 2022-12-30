import logging

from datetime import datetime as dt
from mysql.connector.cursor import MySQLCursor
from typing import Any, Union
from .connection import DBConnection
from ..customtypes import StromzaehlerTableData, DB


class BaseRepo:

    def __init__(self, database_name: str) -> None:
        # initialize logger...
        self._repoLogger: logging.Logger = logging.getLogger(__name__)
        # custom Cursor-Objekt auf dem die DB-Operationen ausgeführt werden
        self._connection: DBConnection = DBConnection(database_name)
    
    def setGunicornLogger(self) -> None:
        """wires the gunicorn-logger to this class' self._repoLogger"""
        gunicornLogger: logging.Logger = logging.getLogger('gunicorn.error')
        self._repoLogger.handlers = gunicornLogger.handlers
        self._repoLogger.setLevel(gunicornLogger.level)
    
    def insertManyRows(self, sqlStatement: str, rows: list[list[Any]]) -> None:
        _cursor: MySQLCursor = self._connection.getCursor()
        _cursor.executemany(sqlStatement, rows)
        self._connection.closeCursor()
    
    def insertSingleRow(self, sqlStatement: str, data: dict[str, Any]) -> None:
        _cursor: MySQLCursor = self._connection.getCursor()
        _cursor.execute(sqlStatement, data)
        self._connection.closeCursor()


class StromzaehlerRepo(BaseRepo):

    def __init__(self, table_name: str=DB.stromzaehler.ZeroW) -> None:
        self._tableName: str = table_name
        super().__init__("stromzaehler")
    
    def insertPowerConsumptionData(self, rows: list[list[Union[dt, float, int]]]) -> None:
        """inserts many rows into the 'stromzaehler'-table"""

        sqlStatement: str = (
            f"INSERT INTO {self._tableName} "
            "(datetime, meanPower_perSec_kW, impulses_perSec) "
            "VALUES "
            "(%s, %s, %s)"
        )
        super().insertManyRows(sqlStatement, rows)
    
    def getAllRows(self) -> tuple[bool, StromzaehlerTableData]:
        """returns entire table as list of tuples"""

        sqlStatement: str = (f"SELECT * FROM {self._tableName}")

        # initialize Result-set
        queryFailed: bool = False
        queryRes: StromzaehlerTableData = StromzaehlerTableData(
            datetime=[], power_kW=[], agg_consumption_Wh=[])

        try:

            _cursor: MySQLCursor = self._connection.getCursor()
            _cursor.execute(sqlStatement)

        except Exception as e:

            queryFailed = True
            self._repoLogger.exception(e.args)

        else:

            # no Exception got thrown, query successful
            aggConsumption: int = 0
            for (datetime, power_kW, agg_consumption_Wh) in _cursor.fetchall():
                queryRes["datetime"].append(datetime.astimezone(tz=None))
                queryRes["power_kW"].append(power_kW)
                aggConsumption += agg_consumption_Wh
                queryRes["agg_consumption_Wh"].append(aggConsumption)
            
            self._connection.closeCursor()
            
        return  queryFailed, queryRes


class HardwaremonitorRepo(BaseRepo):

    def __init__(self, table_name: str) -> None:
        self._tableName: str = table_name
        super().__init__("hardwaremonitor")

    def insertMonitoringData(self, hwmonitorData: dict[str, Any]) -> None:
        # base statement / beginning of statement
        sqlStatement: str = (
            f"INSERT INTO {self._tableName} "
        )
        # get column-names of dictionary as a list
        columns: list[str] = list(hwmonitorData.keys())
        # convert list to a string, and get rid of '-chars of the keys
        strColumns: str = str(columns).replace("'", '')
        # replace square brackets with round brackets as SQL demands
        # but strColumns-variable is not overwritten with round brackets!strColumns = strColumns.replace('[','(').replace(']',')')
        sqlStatement += strColumns.replace('[','(').replace(']',')')
        # add values-part of statement
        strValues: str = "VALUES "
        strValues += strColumns.replace('[', "(%(").replace(", ", ")s, %(").replace(']', ")s)")
        sqlStatement += strValues
        #
        super().insertSingleRow(sqlStatement, hwmonitorData)