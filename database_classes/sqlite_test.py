import sqlite3
from parser_classes.metadata import Field
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import ConstraintDetail
from parser_classes.xml_to_ram import Reader


class DBGenerator:
    def __init__(self, database_schema):
        self.database_schema = database_schema
        self.query = Query()

    def find_field(self, obj_list, obj_name):
        for element in obj_list:
            if element.name == obj_name:
                return element

    def get_tables(self):
        for child_key, child_value in self.database_schema['dbd_schema'].items():
            return child_value['table']

    def get_domains(self):
        for child_key, child_value in self.database_schema['dbd_schema'].items():
            return child_value['domain']

    def generate_tables(self):
        tables = []
        for table in self.get_tables():
            sql = 'CREATE TABLE '+table.name+'('
            column_list = []
            for field in self.get_tables()[table]:
                if isinstance(field, Field):
                    column_list.append(self.generate_field(field))
            sql += ', '.join(column_list) + ')'
            tables.append(sql)
        return tables

    def generate_field(self, field):
        domain = self.find_field(self.get_domains(), field.domain_id).type
        type = ''
        if domain in ['STRING', 'MEMO']:
            type = 'TEXT'
        elif domain in ['LARGEINT', 'WORD', 'BOOLEAN', 'TIME', 'DATE', 'BYTE', 'SMALLINT']:
            type = 'INTEGER'
        elif domain == 'BLOB':
            type = 'BLOB'
        elif domain in ['FLOAT', 'CODE']:
            type = 'REAL'
        return field.name+' '+type

    def generate_primary_key(self, table_attr):
        for constraint in table_attr:
            if isinstance(constraint, ConstraintDetail):
                pass

    def generate_foreign_key(self, table_attr):
        pass

    def generate_constraint(self):
        pass

    def generate_indexes(self):
        sql = []
        for table_key, table_child in self.get_tables().items():
            for index in table_child:
                if isinstance(index, IndexDetail):
                    sql.append('CREATE INDEX '+table_key.name+'_'+index.field_id +
                               ' ON '+table_key.name+' ('+index.field_id+');')
        return sql

    def generate_sql(self):
        self.query.execute('begin')
        for table in self.generate_tables():
            self.query.execute(table)
        for index in self.generate_indexes():
            self.query.execute(index)
        self.query.execute('commit')

    def execute(self):
        self.generate_sql()


class Query:
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite')
        self.cursor = self.conn.cursor()

    def kill_connection(self):
        self.conn.close()

    def execute(self, sql):
        self.cursor.execute(sql)


reader = Reader('O:/progas/python/metadata/tasks.xml')
gen = DBGenerator(reader.xml_to_ram())
gen.execute()
