from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor


class CursorZeroW(MySQLCursor):
    """
    My own MySQLCursor which allows me to abstract the handling of MySQLConnection
    objects in conjunction with a MySQLCursor object, since the MySQLCursor relies
    on the existence of a MySQLConnection.
    """

    def __init__(self) -> None:
        # setup MySQL connection as member variable, otherwise it gets garbage-
        # collected in its super()-class, since it is initialized as a weakref!
        self._mysqlConnection: MySQLConnection = MySQLConnection(
            user="pythonConnection",
            host="192.168.178.23",
            database="zeroW",
            autocommit=True)
        super().__init__(self._mysqlConnection)
    
    def reconnectCursor(self) -> None:
        """does a reconnect to the database itself"""
        # use MySQLConnection-member of super()-class
        self._connection.reconnect(attempts=1, delay=0)
