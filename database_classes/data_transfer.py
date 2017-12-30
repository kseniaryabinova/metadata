import time

from database_classes.mssql_to_ram import MSSQLtoRAM
from database_classes.query import MSSQLQuery, PostgresQuery
from database_classes.ram_to_postgres import RAMtoPostgres


class DataTransfer:
    def __init__(self, tree):
        self.mssql_query = MSSQLQuery()
        self.postgres_query = PostgresQuery()
        self.tree = tree

    def select_func(self, query):
        self.mssql_query.execute(query)
        result = []
        for elem in self.mssql_query.fetchall():
            records = []
            for cell in elem:
                new_cell = str(cell)
                if '00:00:00' in new_cell:
                    new_cell = "to_timestamp('{}', 'YYYY-MM-DD HH24:MI:SS.MS')".format(new_cell)
                if isinstance(cell, str):
                    new_cell = new_cell.replace("'", "''")
                    new_cell = "'{}'".format(new_cell)
                if cell is None:
                    new_cell = 'null'
                if "b'\\x" in new_cell or 'b"\\x' in new_cell:
                    new_cell = new_cell[1:].replace("\\", "")
                    new_cell = new_cell[1:].replace("x", "")
                    new_cell = new_cell[1:].replace("'", "")
                    new_cell = "E'" + new_cell + "'::bytea"
                records.append(new_cell)
            result.append(', '.join(records))
        return '({})'.format('), ('.join(result))

    def select(self, table_name):
        return self.select_func(""" SELECT * FROM [{}] """.format(table_name))

    @staticmethod
    def insert(values, table_name):
        if not values == '()':
            result = """INSERT INTO {} VALUES {}""".format(table_name, values)
        else:
            result = False
        return result

    def get_table_names(self):
        sql = """SELECT name FROM sys.tables"""
        self.mssql_query.execute(sql)
        result = self.mssql_query.fetchall()
        return [elem[0] for elem in result]

    def transfer(self):
        self.postgres_query.begin()
        for table_name in self.get_table_names():
            self.postgres_query.execute('ALTER TABLE {} DISABLE trigger ALL;'.format('_'.join(table_name.split(' '))))
            sql = self.insert(self.select(table_name), '_'.join(table_name.split(' ')))
            if sql:
                self.postgres_query.execute(sql)
        for table_name in self.get_table_names():
            self.postgres_query.execute('ALTER TABLE {} ENABLE trigger ALL;'.format('_'.join(table_name.split(' '))))
        self.postgres_query.commit()


begin_time = time.time()
ram = MSSQLtoRAM()
ram.create_db_in_ram()
ram.query.kill_connection()
generator = RAMtoPostgres(ram.get_schema())
generator.generate()
generator.query.kill_connection()
dt = DataTransfer(ram.get_schema())
dt.transfer()
end_time = time.time()
print(end_time-begin_time)
