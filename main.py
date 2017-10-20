# дедлайн - первые 2 задания до 21 октября
from xml.dom.minidom import parse
from metadata import *
from minidom_fixed import *
from io import StringIO
from custom_exception import *

# сравнение: fc /N tst.xml filename.xml


def parse_table_props(props=None):
    return {'can_' + s: True for s in props.split(', ')}


def parse_domain_props(props=None):
    return {s: True for s in props.split(', ')}


def parse_const_props(dic=None):
    if 'props' in dic.keys():
        for s in dic['props'].split(', '):
            if s == "full_cascading_delete":
                dic['cascading_delete'] = True
            else:
                dic[s] = True
    dic['constraint_type'] = dic['kind']
    return dic


def parse_index_props(props=None):
    return {'kind': s for s in props.split(', ')}


def parse_field_props(props=None):
    props = props.replace('input', 'can_input')
    props = props.replace('edit', 'can_edit')
    return {s: True for s in props.split(', ')}


def xml_to_ram(filename):
    domain_id = table_id = const_id = field_id = index_id = 1
    dom = parse(filename)

    database_dict = {'domain': {'id': None,
                                'name': None,
                                'description': None,
                                'type': None,
                                'data_type_id': None,
                                'length': None,
                                'char_length': None,
                                'precision': None,
                                'scale': None,
                                'width': None,
                                'align': None,
                                'show_null': None,
                                'show_lead_nulls': None,
                                'thousands_separator': None,
                                'summable': None,
                                'case_sensitive': None,
                                'uuid': None,
                                'props': None},
                     'table': {'id': None,
                               'schema_id': None,
                               'name': None,
                               'description': None,
                               'can_add': None,
                               'can_edit': None,
                               'can_delete': None,
                               'temporal_mode': None,
                               'means': None,
                               'props': None,
                               'uuid': None},
                     'field': {'id': None,
                               'table_id': None,
                               'position': None,
                               'name': None,
                               'russian_short_name': None,
                               'description': None,
                               'domain_id': None,
                               'domain': None,
                               'can_input': None,
                               'can_edit': None,
                               'show_in_grid': None,
                               'show_in_details': None,
                               'is_mean': None,
                               'autocalculated': None,
                               'required': None,
                               'props': None,
                               'uuid': None},
                     'constraint': {'id': None,
                                    'table_id': None,
                                    'name': None,
                                    'constraint_type': None,
                                    'reference': None,
                                    'unique_key_id': None,
                                    'has_value_edit': None,
                                    'cascading_delete': None,
                                    # 'full_cascading_delete': None,
                                    'expression': None,
                                    'props': None,
                                    'uuid': None,
                                    'kind': None,
                                    'items': None},
                     'index': {'id': None,
                               'table_id': None,
                               'name': None,
                               'local': None,
                               'kind': None,
                               'props': None,
                               'uuid': None}}

    domains = []
    for node in dom.getElementsByTagName('domain'):
        domain_attrib = dict(node.attributes.items())
        init_dict = dict(dict(database_dict['domain'],
                              **parse_domain_props(domain_attrib['props'])
                              if 'props' in domain_attrib.keys() else {}),
                         **domain_attrib)
        if set(init_dict.keys()) > set(database_dict['domain'].keys()):
            raise DBException("domains")
        domain_attrib['id'] = domain_id
        domain_id += 1
        domains.append(Domain(init_dict))

    tables = {}

    try:
        for table in dom.getElementsByTagName('table'):
            table_attributes = dict(table.attributes.items())
            init_dict = dict(dict
                           (database_dict['table'],
                            **parse_table_props(table_attributes['props'])
                            if 'props' in table_attributes.keys() else {}),
                           **table_attributes)
            if set(init_dict.keys()) > set(database_dict['table'].keys()):
                raise DBException("tables")
            table_attributes['id'] = table_id
            t = Table(init_dict)
            tables[t] = {'field': [],
                         'constraint': [],
                         'constraint_details': [],
                         'index': []}
            for child in table.childNodes:
                if child.attributes is not None:
                    child_node_attrib = dict(child.attributes.items())
                    if child.tagName == 'field':
                        child_node_attrib['russian_short_name'] = child_node_attrib.pop('rname')
                        init_dict = dict(dict(database_dict['field'],
                                              **parse_field_props(child_node_attrib['props'])
                                              if 'props' in child_node_attrib.keys() else {}),
                                         **child_node_attrib)
                        if set(init_dict.keys()) > set(database_dict['field'].keys()):
                            raise DBException("fields")
                        child_node_attrib['domain_id'] = None
                        for domain in domains:
                            if child_node_attrib['domain'] == domain.name:
                                child_node_attrib['domain_id'] = domain.id
                        child_node_attrib['table_id'] = table_id
                        child_node_attrib['id'] = field_id
                        field_id += 1
                        tables[t]['field'].append(Field(init_dict))
                    if child.tagName == 'constraint':
                        child_node_attrib['table_id'] = table_id
                        child_node_attrib['id'] = const_id
                        init_dict = dict(dict(database_dict['constraint'],
                                              **parse_const_props(child_node_attrib)),
                                         **child_node_attrib)
                        if set(init_dict.keys()) > set(database_dict['constraint'].keys()):
                            raise DBException("constraints")
                        const_id += 1
                        tables[t]['constraint_details'].\
                            append(ConstraintDetail({'id': None,
                                                     'position': None,
                                                     'constraint_id': child_node_attrib['id'],
                                                     'field_id': child_node_attrib['items']}))
                        tables[t]['constraint'].append(Constraint(init_dict))
                    if child.tagName == 'index':
                        child_node_attrib['name'] = child_node_attrib.pop('field')
                        child_node_attrib['table_id'] = table_id
                        child_node_attrib['id'] = index_id
                        init_dict = dict(dict(database_dict['index'],
                                              **parse_index_props(child_node_attrib['props'])
                                              if 'props' in child_node_attrib.keys() else {}),
                                         **child_node_attrib)
                        if set(init_dict.keys()) > set(database_dict['index'].keys()):
                            DBException("indexes")
                        index_id += 1
                        tables[t]['index'].append(Index(init_dict))
            table_id += 1
    except KeyError as e:
        raise KeyException(e)
    return {'domains': domains, 'tables': tables}


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
    tables_output = doc.createElement('tables')

    for table, container in database_schema['tables'].items():
        table_output = doc.createElement("table")

        for key, value in table.get_attributes().items():
            table_output.setAttribute(key, str(value))

        for field in container['field']:
            field_output = doc.createElement('field')
            dict_for_output = field.get_attributes()

            for domain in database_schema['domains']:
                if domain.id == field.domain_id:
                    dict_for_output['domain'] = domain.name

            for key, value in dict_for_output.items():
                if key[-2:] != "id":
                    field_output.setAttribute(key, str(value))
            table_output.appendChild(field_output)

        for constraint in container['constraint']:
            constraint_output = doc.createElement('constraint')
            dict_for_output = constraint.get_attributes()

            for const_det in container['constraint_details']:
                if const_det.constraint_id == constraint.id:
                    dict_for_output['items'] = const_det.field_id

            for key, value in dict_for_output.items():
                if key[-2:] != "id":
                    constraint_output.setAttribute(key, str(value))
            table_output.appendChild(constraint_output)

        for index in container['index']:
            index_output = doc.createElement('index')

            for key, value in index.get_attributes().items():
                index_output.setAttribute(key, str(value))
            table_output.appendChild(index_output)

        tables_output.appendChild(table_output)

    dbd_schema.appendChild(tables_output)
    doc.appendChild(dbd_schema)

    st = StringIO()
    doc.writexml(st, '', '  ', '\n', 'utf-8')
    # file_handle = open("filename.xml", "wb")
    # file_handle.write(st.getvalue().encode())
    # file_handle.close()
    print(st.getvalue())


try:
    # ram_to_xml(xml_to_ram('prjadm.xdb.xml'))
    ram_to_xml(xml_to_ram('tasks.xml'))
    # ram_to_xml(xml_to_ram('tst.xml'))
except Exception as e:
    print(e)
