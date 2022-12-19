import logging

from datetime import datetime as dt
from mysql.connector.cursor import MySQLCursor
from typing import Union
from .connection import ConnectionForBackend, ConnectionForMonitoring, ZeroWConnection
from ..customtypes import StromzaehlerTableData


class StromzaehlerRepo:

    def __init__(self, connect_from: str="monitor") -> None:
        # initialize logger...
        self._repoLogger: logging.Logger = logging.getLogger(__name__)
        # custom Cursor-Objekt auf dem die DB-Operationen ausgeführt werden
        self._connection: ZeroWConnection
        if connect_from == "monitor":
            self._connection = ConnectionForMonitoring()
        elif connect_from == "backend":
            self._connection = ConnectionForBackend()
            # ... and now wire the gunicorn-logger to this class' self._repoLogger
            gunicornLogger: logging.Logger = logging.getLogger('gunicorn.error')
            self._repoLogger.handlers = gunicornLogger.handlers
            self._repoLogger.setLevel(gunicornLogger.level)
    
    def insertManyRows(self, rows: list[list[Union[dt, float]]]) -> None:
        """inserts many rows into the 'stromzaehler'-table"""
        sqlStatement: str = (
            "INSERT INTO stromzaehler"
            "(datetime, meanPower_perSec_kW, impulses_perSec) "
            "VALUES "
            "(%s, %s, %s)"
        )
        
        _cursor: MySQLCursor = self._connection.getCursor()
        _cursor.executemany(sqlStatement, rows)
        self._connection.closeCursor()
    
    def getAllRows(self) -> tuple[bool, StromzaehlerTableData]:
        """returns entire table as list of tuples"""

        sqlStatement: str = ("SELECT * FROM stromzaehler")

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
