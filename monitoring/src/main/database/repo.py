from datetime import datetime as dt
from mysql.connector.connection import MySQLConnection
from typing import Union


class StromzaehlerRepo:

    def __init__(self) -> None:
        # setup MySQL connection
        self._mysqlConnection: MySQLConnection = MySQLConnection(
            user="pythonConnection", host="192.168.178.23", database="zeroW")
        # Cursor-Objekt auf dem die DB-Operationen ausgeführt werden
        self._cursor = self._mysqlConnection.cursor()
    
    def insertManyRows(
        self, rows: list[list[Union[dt, float]]], sqlStatement: str) -> None:
        """inserts many rows into the 'stromzaehler'-table"""
        self._cursor.executemany(sqlStatement, rows)
        self._mysqlConnection.commit()