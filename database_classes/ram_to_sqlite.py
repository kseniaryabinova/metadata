import sqlite3
import contextlib
import os
from database_classes.dbd_const import SQL_DBD_Init
from parser_classes.metadata import ConstraintDetail
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import Field
from parser_classes.metadata import DbdSchema
from parser_classes.metadata import Domain
from parser_classes.metadata import Table
from database_classes.query import AbstractQuery


class RAMtoSQLite:
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

    def get_value_form(self, table_name, column_name, column_value):
        def get_column_type():
            self.query.execute('PRAGMA table_info({});'.format(table_name))
            for column in self.query.fetchall():
                if column[1] == column_name:
                    return column[2]

        column_type = get_column_type()
        if column_type == 'integer':
            if column_name in ['table_id', 'reference', 'domain_id', 'data_type_id']:
                return 0
            elif column_name == 'schema_id':
                return 1
            return int(column_value)
        elif column_type in ['varchar', 'char']:
            return '\'{}\''.format(column_value)
        elif column_type == 'boolean':
            if column_value is True:
                return 1
            else:
                return 0

    def generate_record(self, obj, table_name):
        try:
            values = []
            for key, value in obj.get_attributes().items():
                if value is None:
                    values.append('null')
                else:
                    values.append(self.get_value_form(table_name, key, value))
            return '({})'.format(', '.join(map(str, values)))
        except Exception as e:
            raise e

    def _generate_record(self, list_attr):
        def get_object(obj):
            if isinstance(obj, ConstraintDetail):
                return obj.constraint_id
            elif isinstance(obj, IndexDetail):
                return obj.index_id
            else:
                return obj

        def form_insert_query(obj, table_name, values):
            records = ', '.join(values)
            column_names = ', '.join(list(obj.get_attributes().keys()))
            return 'insert into {} ({}) VALUES {}'.format(table_name, column_names, records)

        def get_table_name(obj):
            if isinstance(obj, Field):
                return 'dbd$fields'
            if isinstance(obj, DbdSchema):
                return 'dbd$schemas'
            if isinstance(obj, Domain):
                return 'dbd$domains'
            if isinstance(obj, Table):
                return 'dbd$tables'
            if isinstance(obj, ConstraintDetail):
                return 'dbd$constraints'
            if isinstance(element, IndexDetail):
                return 'dbd$indices'

        elements = []
        for element in list_attr:
            elements.append(self.generate_record(get_object(element), get_table_name(element)))
        query = form_insert_query(get_object(list_attr[0]), get_table_name(list_attr[0]), elements)
        self.query.execute(query)

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

    def get_indexes(self):
        for child_key, child_value in self.db_schema['dbd_schema'].items():
            return [item for sublist in list(child_value['table'].values()) for item in sublist if isinstance(item, IndexDetail)]

    def get_constraints(self):
        for child_key, child_value in self.db_schema['dbd_schema'].items():
            return [item for sublist in list(child_value['table'].values()) for item in sublist if isinstance(item, ConstraintDetail)]

    def get_field(self, obj, field=None):
        if isinstance(obj, IndexDetail):
            return obj.index_id.table_id
        elif isinstance(obj, ConstraintDetail):
            return obj.constraint_id.table_id
        else:
            return obj.get_attribute_by_name(field)

    def insert_set(self, elements, from_table, from_field, to_table, to_field):
        self.query.execute("""DELETE FROM temp""")
        self.query.execute("""insert into temp VALUES {}""".format(', '.join(elements)))
        self.query.execute("""update temp
                              set name = (select {}.id 
                                          from {}
                                          where {}.{}=temp.name);""".format(from_table, from_table, from_table, from_field))
        self.query.execute("""update {}
                              set {} = (select temp.name
                                        from temp
                                        where {}.id=temp.id)""".format(to_table, to_field, to_table))

    def _generate_links(self, list_attr, from_table, from_field, to_table, to_field):
        elements = []
        id_iter = 1
        for element in list_attr:
            elements.append('({}, \'{}\')'.format(id_iter, self.get_field(element, to_field)))
            id_iter += 1
        self.insert_set(elements, from_table, from_field, to_table, to_field)

    def _generate_link_constraint_fk(self, list_attr):
        elements = []
        id_iter = 1
        for element in list_attr:
            if element.constraint_id.constraint_type == 'FOREIGN':
                elements.append('({}, \'{}\')'.format(id_iter, element.constraint_id.reference))
            id_iter += 1
        self.insert_set(elements, 'dbd$tables', 'name', 'dbd$constraints', 'reference')

    def _generate_link_details(self, list_attr, to_table, to_field):
        def insert_into_details():
            if to_table == 'dbd$index_details':
                self.query.execute("""insert into dbd$index_details (index_id) VALUES {}""".format(
                    ', '.join(['({})'.format(x) for x in range(1, id_iter)])))
            elif to_table == 'dbd$constraint_details':
                self.query.execute("""insert into dbd$constraint_details (constraint_id) VALUES {}""".format(
                    ', '.join(['({})'.format(x) for x in range(1, id_iter)])))
        elements = []
        id_iter = 1
        for element in list_attr:
            elements.append('({}, \'{}\')'.format(id_iter, element.field_id))
            id_iter += 1
        insert_into_details()
        self.insert_set(elements, 'dbd$fields', 'name', to_table, to_field)

    def generate(self):
        self._generate_record(self.get_schemas())
        self._generate_record(self.get_domains())
        self._generate_record(self.get_tables())
        self._generate_record(self.get_fields())
        self._generate_record(self.get_constraints())
        self._generate_record(self.get_indexes())
        self.query.commit()

        self._generate_links(self.get_domains(), 'dbd$data_types', 'type_id', 'dbd$domains', 'data_type_id')
        self._generate_links(self.get_fields(), 'dbd$domains', 'name', 'dbd$fields', 'domain_id')
        self._generate_links(self.get_fields(), 'dbd$tables', 'name', 'dbd$fields', 'table_id')
        self._generate_links(self.get_indexes(), 'dbd$tables', 'name', 'dbd$indices', 'table_id')
        self._generate_links(self.get_constraints(), 'dbd$tables', 'name', 'dbd$constraints', 'table_id')
        self._generate_link_constraint_fk(self.get_constraints())
        self._generate_link_details(self.get_indexes(), 'dbd$index_details', 'field_id')
        self._generate_link_details(self.get_constraints(), 'dbd$constraint_details', 'field_id')
        self.query.commit()


class Query(AbstractQuery):
    def __init__(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove('db.sqlite')
        super().__init__(sqlite3, 'db.sqlite')
