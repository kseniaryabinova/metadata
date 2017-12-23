import pyodbc
from database_classes.query import AbstractQuery


"""
SELECT 
     TableName = t.name,
     IndexName = ind.name,
     --IndexId = ind.index_id,
     --ColumnId = ic.index_column_id,
     ColumnName = col.name,
     ind.is_unique
     --ic.*,
     --col.* 
FROM 
     sys.indexes ind 
INNER JOIN 
     sys.index_columns ic ON  ind.object_id = ic.object_id and ind.index_id = ic.index_id 
INNER JOIN 
     sys.columns col ON ic.object_id = col.object_id and ic.column_id = col.column_id 
INNER JOIN 
     sys.tables t ON ind.object_id = t.object_id 
ORDER BY 
     t.name, ind.name, ind.index_id, ic.index_column_id;
     
CHECK
FOREIGN KEY
PRIMARY KEY
UNIQUE
"""


class MSSQLtoRAM:
    def __init__(self):
        self.query = Query()
        self.tree = {}

    def gueries(self, table, additional):
        if table == 'schema':
            return """SELECT SCHEMA_NAME();"""
        elif table == 'domain':
            return """SELECT  *
                      FROM INFORMATION_SCHEMA.DOMAINS
                      """
        elif table == 'table':
            return """SELECT TABLE_SCHEMA, TABLE_NAME 
                      FROM NORTHWND.INFORMATION_SCHEMA.TABLES
                      WHERE TABLE_TYPE = 'BASE TABLE';"""
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

    def guery1(self):
        self.query.execute('select    TABLE_NAME, COLUMN_NAME, IS_NULLABLE, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION from      information_schema.COLUMNS')
        result = self.query.fetchall()
        return result


class Query(AbstractQuery):
    def __init__(self):
        super().__init__(pyodbc, r'DRIVER={ODBC Driver 13 for SQL Server};'
                                 r'SERVER=DESKTOP-3RTKIEI\SQLEXPRESS;'
                                 r'DATABASE=NORTHWND;'
                                 r'Trusted_Connection=yes;')


ram = MSSQLtoRAM()
ram.guery1()
