from database_classes.ram_to_sqlite import RAMtoSQLite
from parser_classes.xml_to_ram import Reader

reader = Reader('prjadm.xdb.xml')
generator = RAMtoSQLite(reader.xml_to_ram())
generator.generate()

