import pprint
from xml.dom.minidom import parse, Element
from parser_classes.metadata import Constraint
from parser_classes.metadata import ConstraintDetail
from parser_classes.metadata import DbdSchema
from parser_classes.metadata import Domain
from parser_classes.metadata import Field
from parser_classes.metadata import Index
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import Table


class ParseException(Exception):
    pass


class GetParseFuncException(Exception):
    pass


class CreateObjectException(Exception):
    pass


class FillTreeException(Exception):
    pass


class Reader:
    def __init__(self, filename):
        self.dom = parse(filename)
        self.tree = {}

    @staticmethod
    def parse_dbd_schema(attributes):
        if set(attributes.keys()) <= {'fulltext_engine', 'version',
                                      'name', 'description'}:
            return attributes
        else:
            raise ParseException

    @staticmethod
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
            raise ParseException

    @staticmethod
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
            raise ParseException

    @staticmethod
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
            raise ParseException

    @staticmethod
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
            raise ParseException

    @staticmethod
    def parse_index(attributes):
        if set(attributes.keys()) <= {'name', 'props', 'kind', 'field'}:
            if 'props' in attributes.keys():
                def parse_index_props():
                    return {'kind': attributes['props']}

                attributes.update(parse_index_props())
            attributes['name'] = attributes.pop('field')
            return attributes
        else:
            raise ParseException

    def get_parse_func(self, node_name):
        try:
            return getattr(self, 'parse_' + node_name)
        except Exception as e:
            raise GetParseFuncException(e)

    @staticmethod
    def get_object_by_name(obj_name):
        try:
            return globals()[obj_name.title().replace("_", "")]()
        except Exception as e:
            raise GetParseFuncException(e)

    @staticmethod
    def create_object(obj, xml_attr, parse_func):
        obj.set_attributes(parse_func(xml_attr))
        if obj.is_valid():
            return obj
        else:
            raise CreateObjectException

    def create_detail(self, obj, detail_name):
        detail = self.get_object_by_name(detail_name+'_detail')
        detail.set_attributes({'field_id': obj.name, detail_name+'_id': obj})
        obj.name = None
        return detail

    def fill_tree(self, child, tree, obj):
        if child.tagName == 'dbd_schema':
            tree[child.tagName] = {obj: {'domain': [], 'table': {}}}
        elif child.tagName == 'table':
            tree[child.tagName][obj] = []
        elif child.tagName in ['constraint', 'index']:
            tree.append(self.create_detail(obj, child.tagName))
        elif child.tagName == 'domain':
            tree[child.tagName].append(obj)
        elif child.tagName == 'field':
            obj.domain_id = child.getAttribute('domain')
            tree.append(obj)
        else:
            raise FillTreeException
        return tree

    def prefix_traverse(self, node, tree):
        if node.hasChildNodes():
            for child in node.childNodes:
                obj = None
                if isinstance(child, Element) and child.hasAttributes():
                    obj = self.create_object(self.get_object_by_name(child.tagName),
                                             dict(child.attributes.items()),
                                             self.get_parse_func(child.tagName))
                    tree = self.fill_tree(child, tree, obj)
                if obj is None or not child.hasChildNodes():
                    self.prefix_traverse(child, tree)
                else:
                    self.prefix_traverse(child, tree[child.tagName][obj])
        return tree

    def xml_to_ram(self):
        self.tree = {}
        return self.prefix_traverse(self.dom, self.tree)

    def write_to_concole(self):
        pp = pprint.PrettyPrinter(depth=6)
        pp.pprint(self.tree)
