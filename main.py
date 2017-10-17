# обработка xml - minidom

# дедлайн - первые 2 задания до 21 октября
from xml.dom.minidom import *
from metadata import *
# TODO учитывать, что есть еще thousands_separator в доменах
# TODO вывод всех полей в констах
# TODO разобраться с юникнесс в индексах
# TODO разобраться с внешним ключем в констах

def parse_table_props(props=None):
    return {'can_' + s: True for s in props.split(', ')}


def parse_props(props=None):
    return {s: True for s in props.split(', ')}


def parse_field_props(props=None):
    props = props.replace('input', 'can_input')
    props = props.replace('edit', 'can_edit')
    return {s: True for s in props.split(', ')}


dom = parse("tasks.xml")
# dom = parse("prjadm.xdb.xml")

domain_dict = {'id': None, 'name': None, 'description': None, 'data_type_id': None, 'length': None,
               'char_length': None, 'precision': None, 'scale': None, 'width': None, 'align': None,
               'show_null': None, 'show_lead_nulls': None, 'thousands_separator': None,
               'summable': None, 'case_sensitive': None, 'uuid': None}
domains = []
for node in dom.getElementsByTagName('domain'):
    d = dict(node.attributes.items())
    domains.append(Domain(dict(dict(domain_dict, **parse_props(d['props']) if 'props' in d.keys() else {}), **d)))

table_dict = {'id': None, 'schema_id': None, 'name': None, 'description': None, 'can_add': None,
              'can_edit': None, 'can_delete': None, 'temporal_mode': None, 'means': None, 'uuid': None}
field_dict = {'id': None, 'table_id': None, 'position': None, 'name': None, 'russian_short_name': None,
              'description': None, 'domain_id': None, 'can_input': None, 'can_edit': None,
              'show_in_grid': None, 'show_in_details': None, 'is_mean': None, 'autocalculated': None,
              'required': None, 'uuid': None}
const_dict = {'id': None, 'table_id': None, 'name': None, 'constraint_type': None, 'unique_key_id': None,
              'has_value_edit': None, 'cascading_delete': None, 'expression': None, 'uuid': None}
index_dict = {'id': None, 'table_id': None, 'name': None, 'local': None, 'kind': None, 'uuid': None}
tables = []
fields = []
consts = []
indexes = []
for table in dom.getElementsByTagName('table'):
    d = dict(table.attributes.items())
    tables.append(Table(dict(dict(table_dict, **parse_table_props(d['props']) if 'props' in d.keys() else {}), **d)))
    for child in table.childNodes:
        if child.attributes is not None:
            dct = dict(child.attributes.items())
            if child.tagName == 'field':
                dct['russian_short_name'] = dct.pop('rname')
                dct['table_id'] = d['name']
                fields.append(Field(dict(
                    dict(field_dict, **parse_field_props(dct['props']) if 'props' in dct.keys() else {}), **dct)))
            if child.tagName == 'constraint':
                dct['table_id'] = d['name']
                consts.append(Constraint(dict(
                    dict(const_dict, **parse_props(dct['props']) if 'props' in dct.keys() else {}), **dct)))
            if child.tagName == 'index':
                dct['name'] = dct.pop('field')
                dct['table_id'] = d['name']
                indexes.append(Index(dict(index_dict, **dct)))

doc = Document()

# node = doc.createElement('domains')
# for elem in domains:
#     domain = doc.createElement("domain")
#     for k, v in elem.get_attributes().items():
#         domain.setAttribute(k, str(v))
#     node.appendChild(domain)
# doc.appendChild(node)

node = doc.createElement('tables')
for elem in tables:
    domain = doc.createElement("table")
    for k, v in elem.get_attributes().items():
        domain.setAttribute(k, str(v))
    for field in fields:
        if field.table_id == elem.name:
            f = doc.createElement('field')
            for k, v in field.get_attributes().items():
                f.setAttribute(k, str(v))
            domain.appendChild(f)
    for const in consts:
        if const.table_id == elem.name:
            f = doc.createElement('constraint')
            for k, v in const.get_attributes().items():
                f.setAttribute(k, str(v))
            domain.appendChild(f)
    for index in indexes:
        if index.table_id == elem.name:
            f = doc.createElement('index')
            for k, v in index.get_attributes().items():
                f.setAttribute(k, str(v))
            domain.appendChild(f)
    node.appendChild(domain)
doc.appendChild(node)

print(doc.toprettyxml())
