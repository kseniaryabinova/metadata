# дедлайн - первые 2 задания до 21 октября
# 4 задача должна быть выложена до начала декабря
from xml.dom.minidom import parse, Element
from minidom_fixed import Document
from io import StringIO
from xml_to_ram import xml_to_ram


# TODO переделать под рекурсию
# for el1 in dom.childNodes:
#     print('\t'+el1.tagName)
#     for el2 in el1.childNodes:
#         if type(el2) == Element:
#             print('\t\t'+el2.tagName)
#             for el3 in el2.childNodes:
#                 if type(el3) == Element:
#                     print('\t\t\t'+el3.tagName)
#                     for el4 in el3.childNodes:
#                         if type(el4) == Element:
#                             print('\t\t\t\t' + el4.tagName)

# сравнение: fc /N tasks.xml filename.xml


def set_attributes():
    return {}


def set_tag(doc, tag_name, attributes=None):
    doc_elem = doc.createElement(tag_name)
    if attributes is not None:
        for key, value in set_attributes():
            doc_elem.setAttribute(key, str(value))
    doc.appendChild(doc_elem)


def prefix_traverse_rtx(tree, tab):
    if isinstance(tree, dict):
        for key, value in tree.items():
            if value is not None:
                print(tab+str(key))
                prefix_traverse_rtx(value, tab+'\t')
    elif isinstance(tree, list):
        for element in tree:
            if element is not None:
                pass
                # print(element)


def ram_to_xml(database_schema):
    doc = Document()
    dbd_schema = doc.createElement('dbd_schema')
    domains_output = doc.createElement('domains')

    for domain in database_schema['domains']:
        domain_output = doc.createElement("domain")

        for k, v in domain.get_attributes().items():
            domain_output.setAttribute(k, str(v))
        domains_output.appendChild(domain_output)

    dbd_schema.appendChild(domains_output)
    # tables_output = doc.createElement('tables')
    #
    # for table, container in database_schema['tables'].items():
    #     table_output = doc.createElement("table")
    #
    #     for key, value in table.get_attributes().items():
    #         table_output.setAttribute(key, str(value))
    #
    #     for field in container['field']:
    #         field_output = doc.createElement('field')
    #         dict_for_output = field.get_attributes()
    #
    #         for domain in database_schema['domains']:
    #             if domain.id == field.domain_id:
    #                 dict_for_output['domain'] = domain.name
    #
    #         for key, value in dict_for_output.items():
    #             if key[-2:] != "id":
    #                 field_output.setAttribute(key, str(value))
    #         table_output.appendChild(field_output)
    #
    #     for constraint in container['constraint']:
    #         constraint_output = doc.createElement('constraint')
    #         dict_for_output = constraint.get_attributes()
    #
    #         for const_det in container['constraint_details']:
    #             if const_det.constraint_id == constraint.id:
    #                 dict_for_output['items'] = const_det.field_id
    #
    #         for key, value in dict_for_output.items():
    #             if key[-2:] != "id":
    #                 constraint_output.setAttribute(key, str(value))
    #         table_output.appendChild(constraint_output)
    #
    #     for index in container['index']:
    #         index_output = doc.createElement('index')
    #
    #         for key, value in index.get_attributes().items():
    #             index_output.setAttribute(key, str(value))
    #         table_output.appendChild(index_output)
    #
    #     tables_output.appendChild(table_output)

    # dbd_schema.appendChild(tables_output)
    doc.appendChild(dbd_schema)

    st = StringIO()
    doc.writexml(st, '', '  ', '\n', 'utf-8')
    print(st.getvalue())
    file_handle = open("output.xml", "wb")
    file_handle.write(st.getvalue().encode())
    file_handle.close()


prefix_traverse_rtx(xml_to_ram('tasks.xml'), '')
# xml_to_ram('prjadm.xdb.xml')
# try:
# ram_to_xml(xml_to_ram('prjadm.xdb.xml'))
# ram_to_xml(xml_to_ram('tasks.xml'))
# ram_to_xml(xml_to_ram('tst.xml'))
# except Exception as e:
#     print(e)
