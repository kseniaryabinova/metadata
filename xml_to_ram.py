from metadata import DbdSchema
from metadata import Domain
from metadata import Table
from metadata import Field
from metadata import Index
from metadata import Constraint
from metadata import ConstraintDetail
from metadata import IndexDetail
import pprint
from xml.dom.minidom import parse, Element


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
        attributes['name'] = attributes.pop('items')
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
        return globals()['parse_' + node_name]
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


def find_field(field_list, name):
    for element in field_list:
        if element.name == name:
            return element
    raise Exception


def set_detail(tree, obj, detail_name):
    cd = get_object_by_name(detail_name+'_detail')
    cd.set_attributes({'field_id': find_field(tree['field'], obj.name),
                       detail_name+'_id': obj})
    tree[detail_name+'_detail'].append(cd)
    obj.name = None


def fill_tree(child, tree, obj):
    if child.tagName == 'dbd_schema':
        tree[child.tagName] = {obj: {'domain': [], 'table': {}}}
    elif child.tagName == 'table':
        tree[child.tagName][obj] = {'field': [],
                                    'constraint': [],
                                    'index': [],
                                    'constraint_detail': [],
                                    'index_detail': []}
    elif child.tagName in ['field', 'constraint', 'index', 'domain']:
        tree[child.tagName].append(obj)
        if child.tagName in ['constraint', 'index']:
            set_detail(tree, obj, child.tagName)
    else:
        raise Exception
    return tree


def prefix_traverse_xtr(node, tree):
    if node.hasChildNodes():
        for child in node.childNodes:
            obj = None
            if isinstance(child, Element) and child.hasAttributes():
                obj = create_object(get_object_by_name(child.tagName), child, get_parse_func(child.tagName))
                tree = fill_tree(child, tree, obj)
            if obj is None or not child.hasChildNodes():
                prefix_traverse_xtr(child, tree)
            else:
                prefix_traverse_xtr(child, tree[child.tagName][obj])
    return tree


def xml_to_ram(filename):
    dom = parse(filename)
    return prefix_traverse_xtr(dom, {})
    # pp = pprint.PrettyPrinter(depth=6)
    # pp.pprint(prefix_traverse_xtr(dom, {}))
