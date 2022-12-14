import logging

from datetime import datetime as dt
from mysql.connector import errorcode
from mysql.connector.errors import DatabaseError
from typing import Union
from .connection import CursorZeroW
from ..customtypes import StromzaehlerTableData


class StromzaehlerRepo:

    def __init__(self) -> None:
        # custom Cursor-Objekt auf dem die DB-Operationen ausgeführt werden
        self._cursorZeroW: CursorZeroW = CursorZeroW()
        # initialize logger...
        self._repoLogger: logging.Logger = logging.getLogger(__name__)
        gunicornLogger: logging.Logger = logging.getLogger('gunicorn.error')
        # ... and now wire the gunicorn-logger to this class' self._repoLogger
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
        self._cursorZeroW.executemany(sqlStatement, rows)
    
    def getAllRows(self, implicit: bool=True) -> tuple[bool, StromzaehlerTableData]:
        """returns entire table as list of tuples"""

        sqlStatement: str = ("SELECT * FROM stromzaehler")

        # initialize Result-set
        queryFailed: bool = False
        queryRes: StromzaehlerTableData = StromzaehlerTableData(
            datetime=[], power_kW=[], agg_consumption_Wh=[])

        try:

            self._cursorZeroW.execute(sqlStatement)

        except DatabaseError as dbError:

            self._repoLogger.exception(dbError.msg)

            if dbError.errno == errorcode.ER_CLIENT_INTERACTION_TIMEOUT:
                # connection was inactive for too long, reconnect
                self._cursorZeroW.reconnectCursor()
                # call method again, after Cursor-Reconnection, but prevent
                # another implicit method-call
                if implicit == True:
                    self._repoLogger.log(logging.INFO, f"call {__name__}.getAllRows() again")
                    self.getAllRows(implicit=False)
            else:
                # a different DB-Error has happened, log for now
                queryFailed = True

        except Exception as e:

            queryFailed = True
            self._repoLogger.exception(e.args)

        else:

            # no Exception got thrown, query successful
            aggConsumption: int = 0
            for (datetime, power_kW, agg_consumption_Wh) in self._cursorZeroW.fetchall():# self._repo.getAllRows():
                queryRes["datetime"].append(datetime.astimezone(tz=None))
                queryRes["power_kW"].append(power_kW)
                aggConsumption += agg_consumption_Wh
                queryRes["agg_consumption_Wh"].append(aggConsumption)
            
        return  queryFailed, queryRes
