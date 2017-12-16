from parser_classes.metadata import ConstraintDetail
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import Constraint
from parser_classes.metadata import DbdSchema
from parser_classes.metadata import Domain
from parser_classes.metadata import Field
from parser_classes.metadata import Index
from parser_classes.metadata import Table
from database_classes.query import AbstractQuery
from parser_classes.ram_to_xml import Writer
import sqlite3
import pprint


class SQLiteToRAM:
    def __init__(self):
        self.query = Query()
        self.tree = {}

    @staticmethod
    def get_object_by_name(obj_name):
        try:
            if obj_name == 'schema':
                return DbdSchema()
            elif obj_name == 'domain':
                return Domain()
            elif obj_name == 'table':
                return Table()
            elif obj_name == 'field':
                return Field()
            elif obj_name == 'constraint':
                return Constraint()
            elif obj_name == 'constraint_detail':
                return ConstraintDetail()
            elif obj_name == 'index':
                return Index()
            elif obj_name == 'index_detail':
                return IndexDetail()
        except Exception as e:
            raise Exception(e)

    def select_func(self, query):
        self.query.execute(query)
        result = self.query.fetchall()
        return [list(elem) for elem in result]

    @staticmethod
    def _create_object(obj, args):
        obj.set_list_attributes(args)
        if obj.is_valid():
            return obj
        else:
            raise Exception

    @staticmethod
    def get_query(table, additional=None):
        if table == 'schema':
            return """select name, fulltext_engine, version, description from dbd$schemas"""
        elif table == 'domain':
            return """select name, description, data_type_id, length, char_length, precision, scale, width, align, 
                      show_null, show_lead_nulls, thousands_separator, summable, case_sensitive
                      from dbd$view_domains"""
        elif table == 'table':
            return """select schema_id, name, description, can_add, can_edit, can_delete, temporal_mode, means 
                      from dbd$view_tables"""
        elif table == 'field':
            return """select table_id, name, russian_short_name, description, domain_id, can_input, can_edit, 
                      show_in_grid, show_in_details, is_mean, autocalculated, required
                      from dbd$view_fields
                      where table_id = '{}'""".format(additional)
        elif table == 'index':
            return """select table_id, name, local, kind, field_name, expression, descend
                      from dbd$view_indices
                      where table_id = '{}'""".format(additional)
        elif table == 'constraint':
            return """select table_id, name, constraint_type, reference, unique_key_id, has_value_edit, cascading_delete, field_name
                      from dbd$view_constraints
                      where table_id = '{}'""".format(additional)

    def create_objects(self):
        for schema in self.select_func(self.get_query('schema')):
            self.tree['dbd_schema'] = {self._create_object(self.get_object_by_name('schema'), schema): {'domain': [], 'table': {}}}
            db_schema = list(self.tree['dbd_schema'].values())[0]
            for domain in self.select_func(self.get_query('domain')):
                db_schema['domain'].append(self._create_object(self.get_object_by_name('domain'), domain))
            for table in self.select_func(self.get_query('table')):
                table_obj = self._create_object(self.get_object_by_name('table'), table)
                db_schema['table'][table_obj] = []
                for field in self.select_func(self.get_query('field', table_obj.name)):
                    field_obj = self._create_object(self.get_object_by_name('field'), field)
                    db_schema['table'][table_obj].append(field_obj)
                for index in self.select_func(self.get_query('index', table_obj.name)):
                    index_obj = self._create_object(self.get_object_by_name('index'), index[:4])
                    index_detail_obj = self._create_object(self.get_object_by_name('index_detail'), [index_obj]+index[-3:])
                    db_schema['table'][table_obj].append(index_detail_obj)
                for const in self.select_func(self.get_query('constraint', table_obj.name)):
                    index_obj = self._create_object(self.get_object_by_name('constraint'), const[:-1])
                    index_detail_obj = self._create_object(self.get_object_by_name('constraint_detail'), [index_obj]+const[-1:])
                    db_schema['table'][table_obj].append(index_detail_obj)

    def write_to_concole(self):
        pp = pprint.PrettyPrinter(depth=6)
        pp.pprint(self.tree)

    def get_schema(self):
        return self.tree


class Query(AbstractQuery):
    def __init__(self):
        super().__init__(sqlite3, 'db.sqlite')


# ram = SQLiteToRAM()
# ram.create_objects()
# ram.write_to_concole()
# writer = Writer(ram.get_schema())
# writer.ram_to_xml()
# writer.write_to_file()
