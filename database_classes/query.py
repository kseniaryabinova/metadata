from abc import ABC


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
