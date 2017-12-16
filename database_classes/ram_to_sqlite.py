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

    def get_value_form(self, table_name, column_name, column_value):
        def get_column_type():
            self.query.execute('PRAGMA table_info({});'.format(table_name))
            for column in self.query.fetchall():
                if column[1] == column_name:
                    return column[2]

        column_type = get_column_type()
        if column_type == 'integer':
            if column_name in ['table_id', 'reference', 'domain_id', 'data_type_id']:
                return 1
                # return int(self.get_id(table_name, column_name, column_value))
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
                    values.append(self.get_value_form('dbd$indices', key, value))
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
                    values.append(self.get_value_form('dbd$constraints', key, value))
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
            values = []
            for key, value in obj.get_attributes().items():
                if value is None:
                    values.append('null')
                else:
                    values.append(self.get_value_form(table_name, key, value))
            return '({})'.format(', '.join(map(str, values)))
        except Exception as e:
            raise e

    @staticmethod
    def get_object(obj):
        if isinstance(obj, ConstraintDetail):
            return obj.constraint_id
        elif isinstance(obj, IndexDetail):
            return obj.index_id
        else:
            return obj

    @staticmethod
    def form_insert_query(obj, table_name, values):
        records = ', '.join(values)
        column_names = ', '.join(list(obj.get_attributes().keys()))
        return 'insert into {} ({}) VALUES {}'.format(table_name, column_names, records)

    def _generate_obj_in_db(self, list_attr):
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
            elements.append(self.generate_record(self.get_object(element), get_table_name(element)))
        query = self.form_insert_query(self.get_object(list_attr[0]), get_table_name(list_attr[0]), elements)
        return query

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

    def _generate_link_in_domains(self, list_attr):
        elements = []
        id_iter = 1
        for element in list_attr:
            elements.append('({}, \'{}\')'.format(id_iter, element.data_type_id))
            id_iter += 1
        self.query.execute("""insert into temp_domain_data_type VALUES {}""".format(', '.join(elements)))
        self.query.execute("""update temp_domain_data_type
                              set data_type_name = (select dbd$data_types.id 
                                                    from dbd$data_types
                                                    where dbd$data_types.type_id=temp_domain_data_type.data_type_name);""")
        return """update dbd$domains
                  set data_type_id = (select temp_domain_data_type.data_type_name
                                      from temp_domain_data_type
                                      where dbd$domains.id=temp_domain_data_type.domain_id)"""

    def _generate_link_in_fields(self, list_attr):
        elements = []
        id_iter = 1
        for element in list_attr:
            elements.append('({}, \'{}\')'.format(id_iter, element.domain_id))
            id_iter += 1
        self.query.execute(
            """insert into temp_field_domain VALUES {}""".format(', '.join(elements)))
        self.query.execute("""update temp_field_domain
                                      set domain_name = (select dbd$domains.id 
                                                         from dbd$domains
                                                         where dbd$domains.name=temp_field_domain.domain_name);""")
        return """update dbd$fields
                          set domain_id = (select temp_field_domain.domain_name
                                           from temp_field_domain
                                           where dbd$fields.id=temp_field_domain.field_id)"""

    def _generate_link_in_fields_t(self, list_attr):
        elements = []
        id_iter = 1
        for element in list_attr:
            elements.append('({}, \'{}\')'.format(id_iter, element.table_id))
            id_iter += 1
        self.query.execute(
            """insert into temp_field_table VALUES {}""".format(', '.join(elements)))
        self.query.execute("""update temp_field_table
                                      set table_name = (select dbd$tables.id 
                                                         from dbd$tables
                                                         where dbd$tables.name=temp_field_table.table_name);""")
        return """update dbd$fields
                          set table_id = (select temp_field_table.table_name
                                           from temp_field_table
                                           where dbd$fields.id=temp_field_table.field_id)"""

    def _generate_link_in_index(self, list_attr):
        elements = []
        id_iter = 1
        for element in list_attr:
            elements.append('({}, \'{}\')'.format(id_iter, element.index_id.table_id))
            id_iter += 1
        self.query.execute("""insert into temp_index_table VALUES {}""".format(', '.join(elements)))
        self.query.execute("""update temp_index_table
                                      set table_name = (select dbd$tables.id 
                                                         from dbd$tables
                                                         where dbd$tables.name=temp_index_table.table_name);""")
        return """update dbd$indices
                  set table_id = (select temp_index_table.table_name
                                  from temp_index_table
                                  where dbd$indices.id=temp_index_table.index_id)"""

    def _generate_link_in_constraint(self, list_attr):
        elements = []
        id_iter = 1
        for element in list_attr:
            elements.append('({}, \'{}\')'.format(id_iter, element.constraint_id.table_id))
            id_iter += 1
        self.query.execute("""insert into temp_constraint_table VALUES {}""".format(', '.join(elements)))
        self.query.execute("""update temp_constraint_table
                                      set table_name = (select dbd$tables.id 
                                                         from dbd$tables
                                                         where dbd$tables.name=temp_constraint_table.table_name);""")
        return """update dbd$constraints
                  set table_id = (select temp_constraint_table.table_name
                                  from temp_constraint_table
                                  where dbd$constraints.id=temp_constraint_table.constraint_id)"""

    def _generate_link_in_constraint_fk(self, list_attr):
        elements = []
        id_iter = 1
        for element in list_attr:
            if element.constraint_id.constraint_type == 'FOREIGN':
                elements.append('({}, \'{}\')'.format(id_iter, element.constraint_id.reference))
            id_iter += 1
        self.query.execute("""DELETE FROM temp_constraint_table;""")
        self.query.execute("""insert into temp_constraint_table VALUES {}""".format(', '.join(elements)))
        self.query.execute("""update temp_constraint_table
                                      set table_name = (select dbd$tables.id 
                                                         from dbd$tables
                                                         where dbd$tables.name=temp_constraint_table.table_name);""")
        return """update dbd$constraints
                  set reference = (select temp_constraint_table.table_name
                                  from temp_constraint_table
                                  where dbd$constraints.id=temp_constraint_table.constraint_id)"""

    def _generate_link_in_index_det(self, list_attr):
        elements = []
        id_iter = 1
        for element in list_attr:
            elements.append('({}, \'{}\')'.format(id_iter, element.field_id))
            id_iter += 1
        self.query.execute("""insert into dbd$index_details (index_id) VALUES {}""".format(', '.join(['({})'.format(x) for x in range(1, id_iter)])))
        self.query.execute("""insert into temp_index_field VALUES {}""".format(', '.join(elements)))
        self.query.execute("""update temp_index_field
                                      set field_id = (select dbd$fields.id 
                                                      from dbd$fields
                                                      where dbd$fields.name=temp_index_field.field_id);""")
        return """update dbd$index_details
                  set field_id = (select temp_index_field.field_id
                                  from temp_index_field
                                  where dbd$index_details.index_id = temp_index_field.index_id)"""

    def _generate_link_in_const_det(self, list_attr):
        elements = []
        id_iter = 1
        for element in list_attr:
            elements.append('({}, \'{}\')'.format(id_iter, element.field_id))
            id_iter += 1
        self.query.execute("""insert into dbd$constraint_details (constraint_id) VALUES {}""".format(', '.join(['({})'.format(x) for x in range(1, id_iter)])))
        self.query.execute("""insert into temp_index_field VALUES {}""".format(', '.join(elements)))
        self.query.execute("""update temp_index_field
                                      set field_id = (select dbd$fields.id 
                                                      from dbd$fields
                                                      where dbd$fields.name=temp_index_field.field_id);""")
        return """update dbd$constraint_details
                  set field_id = (select temp_index_field.field_id
                                  from temp_index_field
                                  where dbd$constraint_details.constraint_id = temp_index_field.index_id)"""

    def generate(self):
        self.query.execute(self._generate_obj_in_db(self.get_schemas()))
        self.query.execute(self._generate_obj_in_db(self.get_domains()))
        self.query.execute(self._generate_obj_in_db(self.get_tables()))
        self.query.execute(self._generate_obj_in_db(self.get_fields()))
        self.query.execute(self._generate_obj_in_db(self.get_constraints()))
        self.query.execute(self._generate_obj_in_db(self.get_indexes()))
        self.query.commit()
        self.query.execute(self._generate_link_in_domains(self.get_domains()))
        self.query.execute(self._generate_link_in_fields(self.get_fields()))
        self.query.execute(self._generate_link_in_fields_t(self.get_fields()))
        self.query.execute(self._generate_link_in_index(self.get_indexes()))
        self.query.execute(self._generate_link_in_constraint(self.get_constraints()))
        self.query.execute(self._generate_link_in_constraint_fk(self.get_constraints()))
        # self.query.execute(self._generate_link_in_index_det(self.get_indexes()))
        self.query.execute(self._generate_link_in_const_det(self.get_constraints()))
        self.query.commit()


class Query(AbstractQuery):
    def __init__(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove('db.sqlite')
        super().__init__(sqlite3, 'db.sqlite')


reader = Reader('O:/progas/python/metadata/tasks.xml')
generator = RAMtoSQLite(reader.xml_to_ram())
generator.generate()
