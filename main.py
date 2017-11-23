from xml_to_ram import Reader
from ram_to_xml import Writer


reader = Reader('prjadm.xdb.xml')
writer = Writer(reader.xml_to_ram())
writer.ram_to_xml()
writer.write_to_file()
