import sqlite3
import contextlib
import os
from database_classes.dbd_const import SQL_DBD_Init
from parser_classes.xml_to_ram import Reader
from parser_classes.metadata import ConstraintDetail
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import Field

from parser_classes.metadata import DbdSchema
from parser_classes.metadata import Domain
from parser_classes.metadata import Table


class SQLite:
    def __init__(self, db_schema):
        self.query = Query()
        self.query.executescript(SQL_DBD_Init)
        for child_key, child_value in db_schema['dbd_schema'].items():
            for table, table_attr in child_value['table'].items():
                for element in table_attr:
                    if isinstance(element, Field):
                        element.table_id = table.name
                    if isinstance(element, IndexDetail):
                        element.index_id.table_id = table.name
                    if isinstance(element, ConstraintDetail):
                        element.constraint_id.table_id = table.name
        self.db_schema = db_schema

    def get_domains(self):
        for child_key, child_value in self.db_schema['dbd_schema'].items():
            return child_value['domain']

    def get_tables(self):
        for child_key, child_value in self.db_schema['dbd_schema'].items():
            return list(child_value['table'].keys())

    def get_schemas(self):
        for child_key, child_value in self.db_schema['dbd_schema'].items():
            return [child_key]

    def get_fields(self):
        for child_key, child_value in self.db_schema['dbd_schema'].items():
            return [item for sublist in list(child_value['table'].values()) for item in sublist if isinstance(item, Field)]

    def get_constraints(self):
        for child_key, child_value in self.db_schema['dbd_schema'].items():
            return [item for sublist in list(child_value['table'].values()) for item in sublist if isinstance(item, IndexDetail)]

    def get_indexes(self):
        for child_key, child_value in self.db_schema['dbd_schema'].items():
            return [item for sublist in list(child_value['table'].values()) for item in sublist if isinstance(item, ConstraintDetail)]

    def get_id(self, table, column_name, column_value):
        if column_name == 'data_type_id':
            self.query.execute('SELECT id FROM dbd$data_types WHERE type_id=\'{}\''.format(column_value))
        elif column_name in ['table_id', 'reference']:
            self.query.execute('SELECT id FROM dbd$tables WHERE name=\'{}\''.format(column_value))
        elif column_name == 'domain_id':
            self.query.execute('SELECT id FROM dbd$domains WHERE name=\'{}\''.format(column_value))
        else:
            self.query.execute('SELECT id FROM {} WHERE {}=\'{}\''.format(table, column_name, column_value))
        return self.query.fetchall()[0][0]

    def get_proper_value(self, table_name, column_name, column_value):
        def get_column_type():
            self.query.execute('PRAGMA table_info({});'.format(table_name))
            for column in self.query.fetchall():
                if column[1] == column_name:
                    return column[2]

        column_type = get_column_type()
        if column_type == 'integer':
            if column_name in ['table_id', 'reference', 'domain_id', 'data_type_id']:
                return int(self.get_id(table_name, column_name, column_value))
            if column_name == 'schema_id':
                return 1
            return int(column_value)
        elif column_type in ['varchar', 'char']:
            return '\'{}\''.format(column_value)
        elif column_type == 'boolean':
            if column_value is True:
                return 1
            else:
                return 0

    def generate_index(self, obj):
        try:
            columns = []
            values = []
            for key, value in obj.index_id.get_attributes().items():
                if value is not None:
                    columns.append(key)
                    values.append(self.get_proper_value('dbd$indices', key, value))
            index_sql = 'INSERT INTO dbd$indices ({}) VALUES ({})'.format(', '.join(map(str, columns)),
                                                                          ', '.join(map(str, values)))
            self.query.execute(index_sql)
            self.query.execute('select id from dbd$indices order by id desc limit 1')
            return 'INSERT INTO dbd$index_details (index_id, field_id) VALUES ({}, {})'.format(
                self.query.fetchall()[0][0],
                self.get_id('dbd$fields', 'name', obj.field_id))
        except Exception as e:
            raise e

    def generate_constraint(self, obj):
        try:
            columns = []
            values = []
            for key, value in obj.constraint_id.get_attributes().items():
                if value is not None:
                    columns.append(key)
                    values.append(self.get_proper_value('dbd$constraints', key, value))
            const_sql = 'INSERT INTO dbd$constraints ({}) VALUES ({})'.format(', '.join(map(str, columns)),
                                                                              ', '.join(map(str, values)))
            self.query.execute(const_sql)
            self.query.execute('select id from dbd$constraints order by id desc limit 1')
            return 'INSERT INTO dbd$constraint_details (constraint_id, field_id) VALUES ({}, {})'.format(
                self.query.fetchall()[0][0],
                self.get_id('dbd$fields', 'name', obj.field_id))
        except Exception as e:
            raise e

    def generate_record(self, obj, table_name):
        try:
            columns = []
            values = []
            for key, value in obj.get_attributes().items():
                if value is not None:
                    columns.append(key)
                    values.append(self.get_proper_value(table_name, key, value))
            return 'INSERT INTO {} ({}) VALUES ({})'.format(table_name,
                                                            ', '.join(map(str, columns)),
                                                            ', '.join(map(str, values)))
        except Exception as e:
            raise e

    def _generate(self, list_attr):
        def get_table_name(obj):
            if isinstance(obj, Field):
                return 'dbd$fields'
            if isinstance(obj, DbdSchema):
                return 'dbd$schemas'
            if isinstance(obj, Domain):
                return 'dbd$domains'
            if isinstance(obj, Table):
                return 'dbd$tables'
        domains = []
        for element in list_attr:
            if isinstance(element, ConstraintDetail):
                domains.append(self.generate_constraint(element))
            if isinstance(element, IndexDetail):
                domains.append(self.generate_index(element))
            if isinstance(element, (DbdSchema, Domain, Table, Field)):
                domains.append(self.generate_record(element, get_table_name(element)))
        return domains

    def generate(self):
        for element in self._generate(self.get_schemas()):
            self.query.execute(element)
        for element in self._generate(self.get_domains()):
            self.query.execute(element)
        for element in self._generate(self.get_tables()):
            self.query.execute(element)
        for element in self._generate(self.get_fields()):
            self.query.execute(element)
        for element in self._generate(self.get_constraints()):
            self.query.execute(element)
        for element in self._generate(self.get_indexes()):
            self.query.execute(element)
        self.query.commit()


class Query:
    def __init__(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove('db.sqlite')
        self.conn = sqlite3.connect('db.sqlite')
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


reader = Reader('O:/progas/python/metadata/tasks.xml')
generator = SQLite(reader.xml_to_ram())
generator.generate()
