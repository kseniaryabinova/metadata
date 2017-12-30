import pprint
import time
from database_classes.query import MSSQLQuery
from database_classes.ram_to_postgres import RAMtoPostgres
from parser_classes.metadata import ConstraintDetail
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import Constraint
from parser_classes.metadata import DbdSchema
from parser_classes.metadata import Domain
from parser_classes.metadata import Field
from parser_classes.metadata import Index
from parser_classes.metadata import Table
from parser_classes.ram_to_xml import Writer


class MSSQLtoRAM:
    def __init__(self):
        self.query = MSSQLQuery()
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

    @staticmethod
    def get_query(table, additional=None):
        if table == 'schema':
            return """
                    SELECT
                        NULL             AS description
                        ,NULL            AS fulltext_engine
                        ,sch.name        AS name
                        ,NULL            AS version
                    FROM sys.schemas     AS sch
                    WHERE sch.name = 'dbo'
                    """
        elif table == 'domain':
            return """
            	    SELECT
                         col.name + CAST(col.object_id AS VARCHAR(20))   AS name
                        ,NULL                                            AS description
                        ,type.name                                       AS data_type_name
                        ,CAST(col.max_length AS varchar(3))              AS length
                        ,CAST(col.max_length AS varchar(3))              AS char_length
                        ,CAST(col.precision AS varchar(3))               AS precision
                        ,CAST(col.scale AS varchar(3))                   AS scale
                        ,NULL                                            AS width
                        ,NULL                                            AS align
                        ,NULL                                            AS show_null
                        ,NULL                                            AS show_lead_nulls
                        ,NULL                                            AS thousands_separator
                        ,NULL                                            AS summable
                        ,NULL                                            AS case_sensitive
                    FROM sys.columns       AS col
                    INNER JOIN sys.types   AS type
                        ON col.system_type_id = type.system_type_id
                        AND col.user_type_id = type.user_type_id
                    INNER JOIN sys.tables 
                        ON sys.tables.object_id = col.object_id
                   """
        elif table == 'table':
            return """
                    SELECT
                        'dbo'          AS schema_id
                        ,tab.name	   AS name
                        ,NULL          AS description
                        ,NULL          AS can_add
                        ,NULL          AS can_edit
                        ,NULL          AS can_delete
                        ,NULL          AS temporal_mode
                        ,NULL          AS means
                    FROM sys.tables    AS tab
                   """
        elif table == 'field':
            return """
                    SELECT
                         sys.tables.name                                      AS table_id
                        ,field.name                                           AS name
                        ,field.collation_name                                 AS russian_short_name
                        ,NULL                                                 AS description
                        ,field.name + CAST(field.object_id AS VARCHAR(20))    AS domain_id
                        ,NULL                                                 AS can_input
                        ,NULL                                                 AS can_edit
                        ,NULL                                                 AS show_in_grid
                        ,NULL                                                 AS show_in_details
                        ,NULL                                                 AS is_mean
                        ,field.is_computed                                    AS autocalculated
                        ,NULL                                                 AS required
                    FROM sys.columns                                          AS field
	                INNER JOIN sys.tables 
	                    ON sys.tables.object_id = field.object_id
	                WHERE sys.tables.name = '{}'""".format(additional)
        elif table == 'index':
            return """
                    SELECT
                         sys.tables.name                              AS table_id
                        ,ind.name                                     AS name
                        ,NULL                                         AS local
                        ,CASE
                            WHEN ind.is_unique = 1
                                THEN 'uniqueness'
                            ELSE NULL
                         END AS kind
                        ,col.name                                     AS field_name
                        ,NULL                                         AS expression
                        ,NULL                                         AS descend
                    FROM sys.indexes AS ind
                    INNER JOIN sys.tables 
                        ON sys.tables.object_id = ind.object_id
                    INNER JOIN sys.index_columns AS detail
                        ON detail.object_id = ind.object_id
                        AND detail.index_id = ind.index_id
                    INNER JOIN sys.columns AS col
                        ON detail.column_id = col.column_id
                        AND detail.object_id = col.object_id
                    WHERE sys.tables.name = '{}'""".format(additional)
        elif table == 'constraint':
            return """
                   SELECT                         
                         sys.tables.name                        AS table_id
                        ,con.name			                    AS name
                        ,con.type_desc                          AS constraint_type
                        ,OBJECT_NAME(fk.referenced_object_id)   AS reference
                        ,NULL                                   AS unique_key_id
                        ,NULL                                   AS has_value_edit
                        ,NULL                                   AS cascading_delete
                        ,definition                             AS expression
                        ,det.COLUMN_NAME                        AS field_id
                    FROM sys.objects                            AS con
                    INNER JOIN sys.tables 
                        ON sys.tables.object_id = con.parent_object_id
                    INNER JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE AS det
                        ON con.name = det.CONSTRAINT_NAME
                    LEFT OUTER JOIN sys.check_constraints AS chk
                        ON chk.object_id = con.object_id
					LEFT OUTER JOIN sys.foreign_keys AS fk
						ON fk.object_id = con.object_id
                    WHERE con.type_desc LIKE '%CONSTRAINT' AND sys.tables.name = '{}'""".format(additional)

    @staticmethod
    def _create_object(obj, args):
        obj.set_list_attributes(args)
        if obj.is_valid():
            return obj
        else:
            raise Exception

    def select_func(self, query):
        self.query.execute(query)
        result = self.query.fetchall()
        return [list(elem) for elem in result]

    @staticmethod
    def find_proper_index(indices, index_attributes):
        for index in indices:
            if isinstance(index, IndexDetail) and index_attributes[1] == index.index_id.name:
                return index.index_id

    def create_db_in_ram(self):
        for schema in self.select_func(self.get_query('schema')):
            self.tree['dbd_schema'] = {
                self._create_object(self.get_object_by_name('schema'), schema): {'domain': [], 'table': {}}}
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
                    index_obj = self.find_proper_index(db_schema['table'][table_obj], index)
                    if not isinstance(index_obj, Index):
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


# ram = MSSQLtoRAM()
# ram.create_db_in_ram()
# ram.query.kill_connection()
# # ram.write_to_concole()
# writer = Writer(ram.get_schema())
# writer.ram_to_xml()
# writer.write_to_file()
#
# begin_time = time.time()
#
# generator = RAMtoPostgres(ram.get_schema())
# generator.generate()
#
# end_time = time.time()
# print(end_time-begin_time)
