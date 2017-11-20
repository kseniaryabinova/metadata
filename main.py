from xml_to_ram import Parser
from ram_to_xml import Writer


parser = Parser('tasks.xml')
writer = Writer(parser.xml_to_ram())
writer.ram_to_xml()
writer.write_to_console()
