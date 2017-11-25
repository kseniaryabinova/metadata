from parser_classes.ram_to_xml import Writer
from parser_classes.xml_to_ram import Reader

reader = Reader('prjadm.xdb.xml')
writer = Writer(reader.xml_to_ram())
writer.ram_to_xml()
writer.write_to_file()
