import sqlite3


class SQLite:
    def __init__(self):
        pass


class Query:
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite')
        self.cursor = self.conn.cursor()

    def kill_connection(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql):
        self.cursor.execute(sql)

    def fetchall(self):
        return self.cursor.fetchall()
