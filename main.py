# дедлайн - первые 2 задания до 21 октября
# 4 задача должна быть выложена до начала декабря
from xml.dom.minidom import parse, Element
from minidom_fixed import Document
from io import StringIO
from metadata import *
from custom_exception import *
# TODO исправить import *
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


def parse_dbd_schema(attributes):
    if set(attributes.keys()) <= {'fulltext_engine', 'version',
                                  'name', 'description'}:
        return attributes
    else:
        raise Exception


def parse_domain(attributes):
    if set(attributes.keys()) <= {'name', 'type', 'description', 'data_type_id',
                                 'length', 'char_length', 'precision',
                                 'scale', 'width', 'align', 'props'}:
        if 'props' in attributes.keys():
            def parse_domain_props():
                props_dict = {}
                for prop in attributes['props'].split(', '):
                    if prop == 'show_null':
                        props_dict['show_null'] = True
                    elif prop == 'show_lead_nulls':
                        props_dict['show_lead_nulls'] = True
                    elif prop == 'thousands_separator':
                        props_dict['thousands_separator'] = True
                    elif prop == 'summable':
                        props_dict['summable'] = True
                    elif prop == 'case_sensitive':
                        props_dict['case_sensitive'] = True
                return props_dict
            attributes.update(parse_domain_props())
        return attributes
    else:
        raise Exception


def parse_table(attributes):
    if set(attributes.keys()) <= {'name', 'description', 'temporal_mode',
                                  'means', 'props'}:
        if 'props' in attributes.keys():
            def parse_table_props():
                props_dict = {}
                for prop in attributes['props'].split(', '):
                    if prop == 'add':
                        props_dict['can_add'] = True
                    elif prop == 'edit':
                        props_dict['can_edit'] = True
                    elif prop == 'delete':
                        props_dict['can_delete'] = True
                return props_dict
            attributes.update(parse_table_props())
        return attributes
    else:
        raise Exception


def parse_field(attributes):
    if set(attributes.keys()) <= {'position', 'name', 'rname',
                                  'description', 'domain', 'props'}:
        def parse_field_props():
            props_dict = {}
            for prop in attributes['props'].split(', '):
                if prop == 'input':
                    props_dict['can_input'] = True
                elif prop == 'edit':
                    props_dict['can_edit'] = True
                elif prop == 'show_in_grid':
                    props_dict['show_in_grid'] = True
                elif prop == 'show_in_details':
                    props_dict['show_in_details'] = True
                elif prop == 'is_mean':
                    props_dict['is_mean'] = True
                elif prop == 'autocalculated':
                    props_dict['autocalculated'] = True
                elif prop == 'required':
                    props_dict['required'] = True
            return props_dict
        attributes.update(parse_field_props())
        attributes['russian_short_name'] = attributes.pop('rname')
        return attributes
    else:
        raise Exception


def parse_constraint(attributes):
    if set(attributes.keys()) <= {'name', 'constraint_type', 'reference',
                                  'props', 'expression', 'kind', 'items'}:
        if 'props' in attributes.keys():
            def parse_const_props():
                props_dict = {}
                for prop in attributes['props'].split(', '):
                    if prop == 'full_cascading_delete':
                        props_dict['cascading_delete'] = True
                    elif prop == 'cascading_delete':
                        props_dict['cascading_delete'] = False
                    elif prop == 'has_value_edit':
                        props_dict['has_value_edit'] = True
                return props_dict
            attributes.update(parse_const_props())
        attributes['constraint_type'] = attributes.pop('kind')
        return attributes
    else:
        raise Exception


def parse_index(attributes):
    if set(attributes.keys()) <= {'name', 'props', 'kind', 'field'}:
        if 'props' in attributes.keys():
            def parse_index_props():
                return {'kind': attributes['props']}
            attributes.update(parse_index_props())
        attributes['name'] = attributes.pop('field')
        return attributes
    else:
        raise Exception


def get_parse_func(node_name):
    try:
        return globals()['parse_'+node_name]
    except Exception as e:
        raise e


def get_object_by_name(obj_name):
    try:
        return globals()[obj_name.title().replace("_", "")]()
    except Exception as e:
        raise e


def create_object(obj, xml_attr, parse_func):
    obj.set_attributes(parse_func(dict(xml_attr.attributes.items())))
    if obj.is_valid():
        return obj
    else:
        raise Exception


def prefix_traverse(node):
    if node.hasChildNodes():
        for child in node.childNodes:
            if isinstance(child, Element) and child.hasAttributes():
                print(child.tagName)
                create_object(get_object_by_name(child.tagName),
                              child,
                              get_parse_func(child.tagName))
            prefix_traverse(child)


def xml_to_ram(filename):
    dom = parse(filename)
    prefix_traverse(dom)

    # domain_id = table_id = const_id = field_id = index_id = 1
    # domains = []
    # for domain in dom.getElementsByTagName('domain'):
    #     domains.append(create_object(Domain(), domain, parse_domain))
    # return {'domains': domains}

    # tables = {}
    #
    # try:
    #     for table in dom.getElementsByTagName('table'):
    #         table_attributes = dict(table.attributes.items())
    #         init_dict = dict(dict
    #                        (database_dict['table'],
    #                         **parse_table_props(table_attributes['props'])
    #                         if 'props' in table_attributes.keys() else {}),
    #                        **table_attributes)
    #         if set(init_dict.keys()) > set(database_dict['table'].keys()):
    #             raise DBException("tables")
    #         init_dict['id'] = table_id
    #         t = Table(init_dict)
    #         tables[t] = {'field': [],
    #                      'constraint': [],
    #                      'constraint_details': [],
    #                      'index': []}
    #         for child in table.childNodes:
    #             if child.attributes is not None:
    #                 child_node_attrib = dict(child.attributes.items())
    #                 if child.tagName == 'field':
    #                     child_node_attrib['russian_short_name'] = child_node_attrib.pop('rname')
    #                     init_dict = dict(dict(database_dict['field'],
    #                                           **parse_field_props(child_node_attrib['props'])
    #                                           if 'props' in child_node_attrib.keys() else {}),
    #                                      **child_node_attrib)
    #                     if set(init_dict.keys()) > set(database_dict['field'].keys()):
    #                         raise DBException("fields")
    #                     child_node_attrib['domain_id'] = None
    #                     for domain in domains:
    #                         if child_node_attrib['domain'] == domain.name:
    #                             init_dict['domain_id'] = domain.id
    #                             break
    #                     init_dict['table_id'] = table_id
    #                     init_dict['id'] = field_id
    #                     field_id += 1
    #                     tables[t]['field'].append(Field(init_dict))
    #                 if child.tagName == 'constraint':
    #                     child_node_attrib['table_id'] = table_id
    #                     child_node_attrib['id'] = const_id
    #                     init_dict = dict(dict(database_dict['constraint'],
    #                                           **parse_const_props(child_node_attrib)),
    #                                      **child_node_attrib)
    #                     if set(init_dict.keys()) > set(database_dict['constraint'].keys()):
    #                         raise DBException("constraints")
    #                     const_id += 1
    #                     tables[t]['constraint_details'].\
    #                         append(ConstraintDetail({'id': None,
    #                                                  'position': None,
    #                                                  'constraint_id': child_node_attrib['id'],
    #                                                  'field_id': child_node_attrib['items']}))
    #                     tables[t]['constraint'].append(Constraint(init_dict))
    #                 if child.tagName == 'index':
    #                     child_node_attrib['name'] = child_node_attrib.pop('field')
    #                     child_node_attrib['table_id'] = table_id
    #                     child_node_attrib['id'] = index_id
    #                     init_dict = dict(dict(database_dict['index'],
    #                                           **parse_index_props(child_node_attrib['props'])
    #                                           if 'props' in child_node_attrib.keys() else {}),
    #                                      **child_node_attrib)
    #                     if set(init_dict.keys()) > set(database_dict['index'].keys()):
    #                         DBException("indexes")
    #                     index_id += 1
    #                     tables[t]['index'].append(Index(init_dict))
    #         table_id += 1
    # except KeyError as e:
    #     raise KeyException(e)
    # return {'domains': domains, 'tables': tables}


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
    file_handle = open("filename.xml", "wb")
    file_handle.write(st.getvalue().encode())
    file_handle.close()


xml_to_ram('tasks.xml')
# xml_to_ram('prjadm.xdb.xml')
# try:
    # ram_to_xml(xml_to_ram('prjadm.xdb.xml'))
# ram_to_xml(xml_to_ram('tasks.xml'))
    # ram_to_xml(xml_to_ram('tst.xml'))
# except Exception as e:
#     print(e)
