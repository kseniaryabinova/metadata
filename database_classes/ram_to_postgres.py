import psycopg2
from parser_classes.metadata import Field
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import ConstraintDetail
from parser_classes.xml_to_ram import Reader
from database_classes.ram_to_sqlite import RAMtoSQLite
from database_classes.sqlite_to_ram import SQLiteToRAM
from database_classes.query import AbstractQuery
import re
import copy
import time


class RAMtoPostgres:
    def __init__(self, database_schema):
        self.database_schema = database_schema
        self.query = Query()

    def get_tables(self):
        for child_key, child_value in self.database_schema['dbd_schema'].items():
            return child_value['table']

    def get_domains(self):
        for child_key, child_value in self.database_schema['dbd_schema'].items():
            return child_value['domain']

    def generate_field(self, field):
        return field.name + ' ' + self.get_domain_name(field.domain_id)

    @staticmethod
    def get_domain_type(domain):
        if domain in ['STRING', 'MEMO']:
            return 'varchar'
        if domain == 'BOOLEAN':
            return 'BOOLEAN'
        if domain == 'DATE':
            return 'date'
        if domain == 'TIME':
            return 'time'
        if domain in ['LARGEINT', 'CODE']:
            return 'bigint'
        if domain in ['WORD', 'BYTE', 'SMALLINT']:
            return 'INTEGER'
        if domain == 'BLOB':
            return 'bytea'
        if domain == 'FLOAT':
            return 'REAL'

    def get_domain_name(self, domain_name):
        def replace_all(text, dic):
            new_text = copy.copy(text)
            for i, j in dic.items():
                new_text = new_text.replace(i, j)
            return new_text

        if re.match("^[A-Za-z0-9_-]*$", domain_name) is None:
            symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                       u"abvgdeejzijklmnoprstufhzc_s_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
            tr = {ord(a): ord(b) for a, b in zip(*symbols)}
            new_name = domain_name.translate(tr)
            new_name = replace_all(new_name, {' ': '_', '.': '', '\\': '', '-': '_', '/': '_'})
            return new_name
        else:
            new_name = replace_all(domain_name, {' ': '_', '.': '', '\\': '', '-': '_', '/': '_'})
            return new_name

    def generate_domains(self):
        def generate_domain(domain_obj):
            name = self.get_domain_name(domain_obj.name)
            sql = 'CREATE DOMAIN {} '.format(name)
            domain_type = self.get_domain_type(domain_obj.data_type_id)
            if domain.data_type_id == 'STRING':
                domain_type += '({})'.format(domain_obj.char_length)
            sql += 'AS {} ;'.format(domain_type)
            return sql
        domains = []
        for domain in self.get_domains():
            domains.append(generate_domain(domain))
        return domains

    def generate_tables(self):
        tables = []
        for table, attr_dict in self.get_tables().items():
            sql = 'CREATE TABLE {}('.format(table.name)
            columns = {}
            for field in attr_dict:
                if isinstance(field, Field):
                    columns[field.name] = '{} {} '.format(field.name, self.get_domain_name(field.domain_id))
            for const in attr_dict:
                if isinstance(const, ConstraintDetail):
                    if const.constraint_id.constraint_type == 'PRIMARY':
                        columns[const.field_id] += 'PRIMARY KEY'
            sql += ', '.join(columns.values())
            sql += ');'
            tables.append(sql)
        return tables

    def generate_foreign_keys(self):
        fks = []
        for table, attr_dict in self.get_tables().items():
            for const in attr_dict:
                if isinstance(const, ConstraintDetail) and const.constraint_id.constraint_type == 'FOREIGN':
                    sql = 'ALTER TABLE {} ADD CONSTRAINT {} FOREIGN KEY ({}) REFERENCES {} '.\
                        format(table.name, const.field_id, const.field_id, const.constraint_id.reference)
                    if const.constraint_id.cascading_delete is True:
                        sql += 'ON DELETE CASCADE;'
                    if const.constraint_id.cascading_delete is False:
                        sql += 'ON DELETE RESTRICT;'
                    if const.constraint_id.cascading_delete is None:
                        sql += 'ON DELETE SET NULL;'
                    fks.append(sql)
        return fks

    def generate_indexes(self):
        indices = []
        for table_key, table_child in self.get_tables().items():
            for index in table_child:
                if isinstance(index, IndexDetail):
                    indices.append('CREATE INDEX {}_{} ON {} ({});'.format(table_key.name, index.field_id,
                                                                           table_key.name, index.field_id))
        return indices

    def generate_sql(self):
        self.query.begin()
        for domain in self.generate_domains():
            self.query.execute(domain)
        for table in self.generate_tables():
            self.query.execute(table)
        for fk in self.generate_foreign_keys():
            self.query.execute(fk)
        for index in self.generate_indexes():
            self.query.execute(index)
        self.query.commit()

    def generate(self):
        self.generate_sql()


class Query(AbstractQuery):
    def __init__(self):
        self.conn = psycopg2.connect(dbname='postgres', user='postgres', password='123')
        self.cursor = self.conn.cursor()
        self.cursor.execute("COMMIT")
        self.cursor.execute("DROP DATABASE IF EXISTS test;")
        self.cursor.execute("COMMIT")
        self.cursor.execute("CREATE DATABASE test;")
        self.cursor.execute("COMMIT")
        super().__init__(psycopg2, "dbname='test' user='postgres' password='123'")


begin_time = time.time()
reader = Reader('O:/progas/python/metadata/tasks.xml')
sqlite = RAMtoSQLite(reader.xml_to_ram())
sqlite.generate()
sqlite.query.kill_connection()
ram = SQLiteToRAM()
ram.create_objects()
generator = RAMtoPostgres(ram.get_schema())
generator.generate()
end_time = time.time()
print(end_time-begin_time)
