import psycopg2
from parser_classes.metadata import Field
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import ConstraintDetail
from parser_classes.xml_to_ram import Reader
import re
import copy


class DBGenerator:
    def __init__(self, database_schema):
        self.database_schema = database_schema
        self.query = Query()

    def find_field(self, obj_list, obj_name):
        for element in obj_list:
            if element.name == obj_name:
                return element

    def get_domain_in_db(self, domain_name):
        for domain in self.get_domains():
            if domain.name == domain_name:
                return domain.description

    def get_primary_keys(self, table_name):
        sql = 'SELECT a.attname FROM pg_index i ' \
              'JOIN pg_attribute a ON a.attrelid = i.indrelid ' \
              'AND a.attnum = ANY(i.indkey) ' \
              'WHERE  i.indrelid = \'{}\'::regclass ' \
              'AND i.indisprimary;'.format(table_name)
        self.query.execute(sql)
        result = self.query.fetchall()
        if result:
            return result[0][0]

    def get_tables(self):
        for child_key, child_value in self.database_schema['dbd_schema'].items():
            return child_value['table']

    def get_domains(self):
        for child_key, child_value in self.database_schema['dbd_schema'].items():
            return child_value['domain']

    def generate_tables(self):
        tables = []
        for table, attr_dict in self.get_tables().items():
            sql = 'CREATE TABLE {}('.format(table.name)
            column_list = []
            for field in attr_dict:
                if isinstance(field, Field):
                    column_list.append(self.generate_field(field))
            sql += ', '.join(column_list)
            sql += self.generate_primary_key(attr_dict) + ');'
            tables.append(sql)
        return tables

    def generate_field(self, field):
        domain = self.find_field(self.get_domains(), field.domain_id)
        return field.name + ' ' + self.get_domain_in_db(domain.name)

    def get_domain_type(self, domain):
        domain_type = ''
        if domain in ['STRING', 'MEMO']:
            domain_type = 'varchar'
        elif domain == 'BOOLEAN':
            domain_type = 'BOOLEAN'
        elif domain == 'DATE':
            domain_type = 'date'
        elif domain == 'TIME':
            domain_type = 'time'
        elif domain in ['LARGEINT', 'CODE']:
            domain_type = 'bigint'
        elif domain in ['WORD', 'BYTE', 'SMALLINT']:
            domain_type = 'INTEGER'
        elif domain == 'BLOB':
            domain_type = 'bytea'
        elif domain == 'FLOAT':
            domain_type = 'REAL'
        return domain_type

    def replace_all(self, text, dic):
        new_text = copy.copy(text)
        for i, j in dic.items():
            new_text = new_text.replace(i, j)
        return new_text

    def get_domain_name(self, domain):
        if re.match("^[A-Za-z0-9_-]*$", domain.name) == None:
            symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                       u"abvgdeejzijklmnoprstufhzc_s_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
            tr = {ord(a): ord(b) for a, b in zip(*symbols)}
            new_name = domain.name.translate(tr)
            new_name = self.replace_all(new_name, {' ': '_', '.': '', '\\': '', '-': '_', '/': '_'})
            return new_name
        else:
            new_name = self.replace_all(domain.name, {' ': '_', '.': '', '\\': '', '-': '_', '/': '_'})
            return new_name

    def generate_domain(self, domain):
        sql = 'CREATE DOMAIN {} '.format(self.get_domain_name(domain))
        domain_type = self.get_domain_type(domain.type)
        if domain.type == 'STRING':
            domain_type += '({})'.format(domain.char_length)
        sql += 'AS {} ;'.format(domain_type)
        domain.description = self.get_domain_name(domain)
        return sql

    def generate_domains(self):
        domains = []
        for domain in self.get_domains():
            domains.append(self.generate_domain(domain))
        return domains

    def generate_primary_key(self, table_attr):
        fields = []
        for const in table_attr:
            if isinstance(const, ConstraintDetail) and const.constraint_id.constraint_type == 'PRIMARY':
                fields.append(const.field_id)
        if not fields:
            return ''
        else:
            return ', PRIMARY KEY ({})'.format(', '.join(fields))

    def generate_foreign_key(self, table, table_attr):
        fields = []
        for const in table_attr:
            if isinstance(const, ConstraintDetail) and const.constraint_id.constraint_type == 'FOREIGN':
                sql = 'alter table {} ' \
                      'add constraint fk_{} ' \
                      'foreign key ({}) ' \
                      'REFERENCES {} ({}); '.format(table.name, const.constraint_id.reference + '_' + const.field_id,
                                                    const.field_id, const.constraint_id.reference,
                                                    self.get_primary_keys(const.constraint_id.reference))
                fields.append(sql)
        return fields

    def generate_foreign_keys(self):
        fks = []
        for table_name, attr_dict in self.get_tables().items():
            fks += self.generate_foreign_key(table_name, attr_dict)
        return fks

    def generate_indexes(self):
        sql = []
        for table_key, table_child in self.get_tables().items():
            for index in table_child:
                if isinstance(index, IndexDetail):
                    sql.append('CREATE INDEX ' + table_key.name + '_' + index.field_id +
                               ' ON ' + table_key.name + ' (' + index.field_id + ');')
        return sql

    def generate_sql(self):
        for domain in self.generate_domains():
            self.query.execute(domain)
        self.query.execute('commit')
        for table in self.generate_tables():
            self.query.execute(table)
        for index in self.generate_indexes():
            self.query.execute(index)
        self.query.execute('commit')
        for foreign_key in self.generate_foreign_keys():
            self.query.execute(foreign_key)
        self.query.execute('commit')

    def execute(self):
        self.generate_sql()


class Query:
    def __init__(self):
        self.conn = psycopg2.connect(dbname='postgres', user='postgres', password='123')
        self.cursor = self.conn.cursor()
        self.cursor.execute("COMMIT")
        self.cursor.execute("DROP DATABASE IF EXISTS test;")
        self.cursor.execute("COMMIT")
        self.cursor.execute("CREATE DATABASE test;")
        self.cursor.execute("COMMIT")
        self.conn = psycopg2.connect(dbname='test', user='postgres', password='123')
        self.cursor = self.conn.cursor()

    def kill_connection(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql):
        self.cursor.execute(sql)

    def fetchall(self):
        return self.cursor.fetchall()


reader = Reader('O:/progas/python/metadata/tasks.xml')
gen = DBGenerator(reader.xml_to_ram())
gen.execute()
