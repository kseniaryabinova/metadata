# обработка xml - minidom

# дедлайн - первые 2 задания до 21 октября
from xml.dom.minidom import parse
from metadata import *
from minidom_fixed import *
from io import StringIO


def parse_table_props(props=None):
    return {'can_' + s: True for s in props.split(', ')}


def parse_domain_props(props=None):
    return {s: True for s in props.split(', ')}


def parse_const_props(dic=None):
    if 'props' in dic.keys():
        for s in dic['props'].split(', '):
            dic[s] = True
    dic['constraint_type'] = dic['kind']
    return dic


def parse_index_props(props=None):
    return {'kind': s for s in props.split(', ')}


def parse_field_props(props=None):
    props = props.replace('input', 'can_input')
    props = props.replace('edit', 'can_edit')
    return {s: True for s in props.split(', ')}


domain_id = table_id = const_id = field_id = index_id = 1
dom = parse("tasks.xml")
# dom = parse("prjadm.xdb.xml")

domain_dict = {'id': None,
               'name': None,
               'description': None,
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
               'uuid': None}

domains = []
for node in dom.getElementsByTagName('domain'):
    d = dict(node.attributes.items())
    d['id'] = domain_id
    domain_id += 1
    domains.append(Domain(dict(dict(domain_dict, **parse_domain_props(d['props']) if 'props' in d.keys() else {}), **d)))

table_dict = {'id': None,
              'schema_id': None,
              'name': None,
              'description': None,
              'can_add': None,
              'can_edit': None,
              'can_delete': None,
              'temporal_mode': None,
              'means': None,
              'uuid': None}

field_dict = {'id': None,
              'table_id': None,
              'position': None,
              'name': None,
              'russian_short_name': None,
              'description': None,
              'domain_id': None,
              'can_input': None,
              'can_edit': None,
              'show_in_grid': None,
              'show_in_details': None,
              'is_mean': None,
              'autocalculated': None,
              'required': None,
              'uuid': None}

const_dict = {'id': None,
              'table_id': None,
              'name': None,
              'constraint_type': None,
              'reference': None,
              'unique_key_id': None,
              'has_value_edit': None,
              'cascading_delete': None,
              'expression': None,
              'uuid': None}

index_dict = {'id': None,
              'table_id': None,
              'name': None,
              'local': None,
              'kind': None,
              'uuid': None}
tables = []
fields = []
consts = []
const_details = []
indexes = []
for table in dom.getElementsByTagName('table'):
    d = dict(table.attributes.items())
    d['id'] = table_id
    tables.append(Table(dict(dict(table_dict, **parse_table_props(d['props']) if 'props' in d.keys() else {}), **d)))
    for child in table.childNodes:
        if child.attributes is not None:
            dct = dict(child.attributes.items())
            if child.tagName == 'field':
                dct['russian_short_name'] = dct.pop('rname')
                dct['domain_id'] = None
                for domain in domains:
                    if dct['domain'] == domain.name:
                        dct['domain_id'] = domain.id
                dct['table_id'] = table_id
                dct['id'] = field_id
                field_id += 1
                fields.append(Field(dict(
                    dict(field_dict, **parse_field_props(dct['props']) if 'props' in dct.keys() else {}), **dct)))
            if child.tagName == 'constraint':
                dct['table_id'] = table_id
                dct['id'] = const_id
                const_id += 1
                const_details.append(ConstraintDetail({'id': None,
                                                       'position': None,
                                                       'constraint_id': dct['id'],
                                                       'field_id': dct['items']}))
                consts.append(Constraint(dict(
                    dict(const_dict, **parse_const_props(dct)), **dct)))
            if child.tagName == 'index':
                dct['name'] = dct.pop('field')
                dct['table_id'] = table_id
                dct['id'] = index_id
                index_id += 1
                indexes.append(Index(dict(
                    dict(index_dict, **parse_index_props(dct['props']) if 'props' in dct.keys() else {}), **dct)))
    table_id += 1

doc = Document()
nd = doc.createElement('dbd_schema')
node = doc.createElement('domains')
for elem in domains:
    domain = doc.createElement("domain")
    for k, v in elem.get_attributes().items():
        if k[-2:] != "id":
            domain.setAttribute(k, str(v))
    node.appendChild(domain)
nd.appendChild(node)

node = doc.createElement('tables')
for elem in tables:
    domain = doc.createElement("table")
    for k, v in elem.get_attributes().items():
        if k[-2:] != "id":
            domain.setAttribute(k, str(v))
    for field in fields:
        if field.table_id == elem.id:
            f = doc.createElement('field')
            dctn = field.get_attributes()
            for dom in domains:
                if dom.id == field.domain_id:
                    dctn['domain'] = dom.name
            for k, v in dctn.items():
                if k[-2:] != "id":
                    f.setAttribute(k, str(v))
            domain.appendChild(f)
    for const in consts:
        if const.table_id == elem.id:
            f = doc.createElement('constraint')
            dctn = const.get_attributes()
            for const_det in const_details:
                if const_det.constraint_id == const.id:
                    dctn['items'] = const_det.field_id
            for k, v in dctn.items():
                if k[-2:] != "id":
                    f.setAttribute(k, str(v))
            domain.appendChild(f)
    for index in indexes:
        if index.table_id == elem.id:
            f = doc.createElement('index')
            for k, v in index.get_attributes().items():
                if k[-2:] != "id":
                    f.setAttribute(k, str(v))
            domain.appendChild(f)
    node.appendChild(domain)
nd.appendChild(node)
doc.appendChild(nd)

st = StringIO()
doc.writexml(st, '', '  ', '\n', 'utf-8')
print(st.getvalue())
