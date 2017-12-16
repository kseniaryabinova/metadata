from parser_classes.metadata import ConstraintDetail
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import Constraint
from parser_classes.metadata import DbdSchema
from parser_classes.metadata import Domain
from parser_classes.metadata import Field
from parser_classes.metadata import Index
from parser_classes.metadata import Table
from database_classes.query import AbstractQuery
import sqlite3
import pprint


class SQLiteToRAM:
    def __init__(self):
        self.query = Query()
        self.tree = {}

    @staticmethod
    def get_object_by_name(obj_name):
        try:
            if obj_name == 'dbd$schemas':
                return DbdSchema()
            elif obj_name == 'dbd$domains':
                return Domain()
            elif obj_name == 'dbd$tables':
                return Table()
            elif obj_name == 'dbd$fields':
                return Field()
            elif obj_name == 'dbd$constraints':
                return Constraint()
            elif obj_name == 'dbd$constraint_details':
                return ConstraintDetail()
            elif obj_name == 'dbd$indices':
                return Index()
            elif obj_name == 'dbd$index_details':
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
        if table == 'dbd$schemas':
            return """select name, fulltext_engine, version, description from dbd$schemas"""
        elif table == 'dbd$domains':
            return """select id, name, description, data_type_id, length, char_length, precision, scale, width, align, 
                      show_null, show_lead_nulls, thousands_separator, summable, case_sensitive
                      from dbd$view_domains"""
        elif table == 'dbd$tables':
            return """select id, schema_id, name, description, can_add, can_edit, can_delete, temporal_mode, means 
                      from dbd$view_tables"""
        elif table == 'dbd$fields':
            return """select id, table_id, name, russian_short_name, description, domain_id, can_input, can_edit, 
                      show_in_grid, show_in_details, is_mean, autocalculated, required
                      from dbd$view_fields
                      where table_id = '{}'""".format(additional)

    def create_objects(self):
        for schema in self.select_func(self.get_query('dbd$schemas')):
            self.tree['dbd_schema'] = {self._create_object(self.get_object_by_name('dbd$schemas'), schema):
                                                      {'domain': [], 'table': {}}}
            db_schema = list(self.tree['dbd_schema'].values())[0]
            for domain in self.select_func(self.get_query('dbd$domains')):
                db_schema['domain'].append(self._create_object(self.get_object_by_name('dbd$domains'), domain))
            for table in self.select_func(self.get_query('dbd$tables')):
                table_obj = self._create_object(self.get_object_by_name('dbd$tables'), table)
                db_schema['table'][table_obj] = []
                for field in self.select_func(self.get_query('dbd$fields', table_obj.name)):
                    field_obj = self._create_object(self.get_object_by_name('dbd$fields'), field)
                    db_schema['table'][table_obj].append(field_obj)

    def write_to_concole(self):
        pp = pprint.PrettyPrinter(depth=6)
        pp.pprint(self.tree)


class Query(AbstractQuery):
    def __init__(self):
        super().__init__(sqlite3, 'db.sqlite')


ram = SQLiteToRAM()
ram.create_objects()
ram.write_to_concole()
