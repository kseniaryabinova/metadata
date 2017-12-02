from parser_classes.ram_to_xml import Writer
from parser_classes.xml_to_ram import Reader

reader = Reader('prjadm.xdb.xml')
writer = Writer(reader.xml_to_ram())
writer.ram_to_xml()
writer.write_to_console()


"""
крч, sqlite нужен, чтобы к нему быстро запросы писать, а не ходить по объектам в словарях
или не грузить сервак
схема загрузки будет такая:
xml -> ram -> sqlite
sqlite -> ram -> ddl инструкции -> postgres
ms sql -> ram -> sqlite -> ram -> ddl инструкции -> postgres  
"""