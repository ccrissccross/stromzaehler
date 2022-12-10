from datetime import datetime as dt
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from typing import Union


class StromzaehlerRepo:

    def __init__(self) -> None:
        # setup MySQL connection
        self._mysqlConnection: MySQLConnection = MySQLConnection(
            user="pythonConnection",
            host="192.168.178.23",
            database="zeroW",
            autocommit=True)
        # Cursor-Objekt auf dem die DB-Operationen ausgeführt werden
        self._cursor: MySQLCursor = MySQLCursor(self._mysqlConnection)#.cursor()
    
    def insertManyRows(self, rows: list[list[Union[dt, float]]]) -> None:
        """inserts many rows into the 'stromzaehler'-table"""
        sqlStatement: str = (
            "INSERT INTO stromzaehler"
            "(datetime, meanPower_perSec_kW, impulses_perSec) "
            "VALUES "
            "(%s, %s, %s)"
        )
        self._cursor.executemany(sqlStatement, rows)
        # self._mysqlConnection.commit()
    
    def getAllRows(self) -> list[tuple[dt, float, int]]:
        """returns entire table as list of tuples"""
        sqlStatement: str = (
            "SELECT * FROM stromzaehler"
        )
        self._cursor.execute(sqlStatement)
        return self._cursor.fetchall()