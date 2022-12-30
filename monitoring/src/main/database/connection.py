from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from numpy import Infinity


class DBConnection:
    """Wrapper-class around MySQLConnection"""

    def __init__(self, database_name: str) -> None:
        self._mysqlConnection: MySQLConnection = MySQLConnection(
            user="pythonConnection",
            host="192.168.178.23",
            database=database_name,
            autocommit=True)
        self._cursor: MySQLCursor
    
    def getCursor(self, _attempts: float=Infinity, _delay: int=1) -> MySQLCursor:
        """
        Checks whether connection to MySQL-Server still exists, if not then it
        reconnects in an inifite loop (it is okay since it is not blocking any-
        thing).
        Finally acquires cursor and returns it.
        """
        if not self._mysqlConnection.is_connected():
            # Wenn keine Verbindung mehr zum MySQL-Server besteht, dann probier
            # so lange wie nötig, da der Part bottleneck ist. Aufgrund multi-
            # threading blockiert auch nichts.
            self._mysqlConnection.reconnect(attempts=_attempts, delay=_delay)

        self._cursor = self._mysqlConnection.cursor()
        return self._cursor

    def closeCursor(self) -> bool:
        """simply closes the cursor"""
        return self._cursor.close()
