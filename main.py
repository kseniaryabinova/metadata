from database_classes.ram_to_sqlite import RAMtoSQLite
from parser_classes.xml_to_ram import Reader

reader = Reader('prjadm.xdb.xml')
generator = RAMtoSQLite(reader.xml_to_ram())
generator.generate()


"""
крч, sqlite нужен, чтобы к нему быстро запросы писать, а не ходить по объектам в словарях
или не грузить сервак
схема загрузки будет такая:
xml -> ram -> sqlite
sqlite -> ram -> ddl инструкции -> postgres
ms sql -> ram -> sqlite -> ram -> ddl инструкции -> postgres  
"""