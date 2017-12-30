import sqlite3
from abc import ABC

import pyodbc

import psycopg2


class AbstractQuery(ABC):
    def __init__(self, driver, connect_string):
        self.conn = driver.connect(connect_string)
        self.cursor = self.conn.cursor()

    def kill_connection(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql):
        self.cursor.execute(sql)

    def executescript(self, sql):
        self.cursor.executescript(sql)

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.cursor.execute('COMMIT')

    def begin(self):
        self.cursor.execute('BEGIN')


class MSSQLQuery(AbstractQuery):
    def __init__(self):
        super().__init__(pyodbc, r'DRIVER={ODBC Driver 13 for SQL Server};'
                                 r'SERVER=DESKTOP-3RTKIEI\SQLEXPRESS;'
                                 r'DATABASE=NORTHWND;'
                                 r'Trusted_Connection=yes;')


class PostgresQuery(AbstractQuery):
    def __init__(self):
        super().__init__(psycopg2, "dbname='test' user='postgres' password='123'")


class SQLiteQuery(AbstractQuery):
    def __init__(self):
        super().__init__(sqlite3, 'db.sqlite')
