# дедлайн - первые 2 задания до 21 октября
# 4 задача должна быть выложена до начала декабря
import re
from io import StringIO
from parser_classes.metadata import Constraint
from parser_classes.metadata import ConstraintDetail
from parser_classes.metadata import DbdSchema
from parser_classes.metadata import Domain
from parser_classes.metadata import Field
from parser_classes.metadata import Index
from parser_classes.metadata import IndexDetail
from parser_classes.metadata import Table
from parser_classes.minidom_fixed import Document


class AssemblyAttributesException(Exception):
    pass

# сравнение: fc /N tasks.xml filename.xml

class Writer:
    def __init__(self, database_schema):
        self.database_schema = database_schema
        self.doc = Document()
        dbd_schema = self.doc.createElement('dbd_schema')
        self.doc.appendChild(dbd_schema)
        dbd_schema.appendChild(self.doc.createElement('custom'))
        dbd_schema.appendChild(self.doc.createElement('domains'))
        dbd_schema.appendChild(self.doc.createElement('tables'))

    def ram_to_xml(self):
        self.prefix_traverse(self.database_schema, self.doc, self.doc)

    def write_to_file(self):
        st = StringIO()
        self.doc.writexml(st, '', '  ', '\n', 'utf-8')
        print(st.getvalue())
        file_handle = open("filename.xml", "wb")
        file_handle.write(st.getvalue().encode())
        file_handle.close()

    def write_to_console(self):
        print(self.doc.toprettyxml())

    def get_dbd_schema_attributes(self, dict_order, obj):
        pass

    @staticmethod
    def get_domain_attributes(dict_order, obj):
        def get_bool_attributes():
            bool_array = []
            if obj.show_null:
                bool_array.append('show_null')
            if obj.show_lead_nulls:
                bool_array.append('show_lead_nulls')
            if obj.thousands_separator:
                bool_array.append('thousands_separator')
            if obj.summable:
                bool_array.append('summable')
            if obj.case_sensitive:
                bool_array.append('case_sensitive')
            if not bool_array:
                return None
            return ", ".join(bool_array)
        dict_order['props'] = get_bool_attributes()
        dict_order['type'] = obj.data_type_id

    @staticmethod
    def get_table_attributes(dict_order, obj):
        def get_bool_attributes():
            bool_array = []
            if obj.can_add:
                bool_array.append('add')
            if obj.can_edit:
                bool_array.append('edit')
            if obj.can_delete:
                bool_array.append('delete')
            if not bool_array:
                return None
            return ", ".join(bool_array)
        dict_order['props'] = get_bool_attributes()

    @staticmethod
    def get_field_attributes(dict_order, obj):
        def get_bool_attributes():
            bool_array = []
            if obj.can_input:
                bool_array.append('input')
            if obj.can_edit:
                bool_array.append('edit')
            if obj.show_in_grid:
                bool_array.append('show_in_grid')
            if obj.show_in_details:
                bool_array.append('show_in_details')
            if obj.is_mean:
                bool_array.append('is_mean')
            if obj.autocalculated:
                bool_array.append('autocalculated')
            if obj.required:
                bool_array.append('required')
            if not bool_array:
                return None
            return ", ".join(bool_array)
        dict_order['props'] = get_bool_attributes()
        dict_order['rname'] = obj.russian_short_name
        dict_order['domain'] = obj.domain_id

    @staticmethod
    def get_constraint_attributes(dict_order, obj):
        def get_bool_attributes():
            bool_array = []
            if obj.constraint_id.has_value_edit:
                bool_array.append('has_value_edit')
            if obj.constraint_id.cascading_delete is True:
                bool_array.append('full_cascading_delete')
            if obj.constraint_id.cascading_delete is False:
                bool_array.append('cascading_delete')
            if not bool_array:
                return None
            return ", ".join(bool_array)

        dict_order['props'] = get_bool_attributes()
        dict_order['kind'] = obj.constraint_id.constraint_type
        dict_order['items'] = obj.field_id
        dict_order['reference'] = obj.constraint_id.reference

    @staticmethod
    def get_index_attributes(dict_order, obj):
        dict_order['field'] = obj.field_id
        dict_order['props'] = obj.index_id.kind

    def assembly_attributes(self, obj):
        try:
            dict_order = self.get_dict_order(obj)
            for key in dict_order.keys():
                dict_order[key] = obj.get_attribute_by_name(key)
            getattr(self, 'get_'+self.get_name_by_object(obj)+'_attributes')(dict_order, obj)
            return {key: value for key, value in dict_order.items() if value is not None}
        except Exception as e:
            raise AssemblyAttributesException(e)

    @staticmethod
    def get_name_by_object(obj):
        if isinstance(obj, (DbdSchema, Domain, Table, Field)):
            word_list = re.findall('[A-Z][a-z]*', str(type(obj)))
            tag_name = "_".join([elem.lower() for elem in word_list])
            return tag_name
        elif obj in ['domain', 'table']:
            return obj+'s'
        elif obj == 'dbd_schema':
            return obj
        elif isinstance(obj, (ConstraintDetail, IndexDetail)):
            return obj.__class__.__name__.replace('Detail', '').lower()

    @staticmethod
    def get_dict_order(obj):
        if isinstance(obj, DbdSchema):
            return {'fulltext_engine': None,
                    'version': None,
                    'name': None,
                    'description': None}
        elif isinstance(obj, Domain):
            return {'name': None,
                    'description': None,
                    'type': None,
                    'align': None,
                    'width': None,
                    'length': None,
                    'precision': None,
                    'props': None,
                    'char_length': None,
                    'scale': None}
        elif isinstance(obj, Table):
            return {'name': None,
                    'description': None,
                    'props': None}
        elif isinstance(obj, Field):
            return {'name': None,
                    'rname': None,
                    'domain': None,
                    'description': None,
                    'props': None}
        elif isinstance(obj, (Constraint, ConstraintDetail)):
            return {'kind': None,
                    'items': None,
                    'reference': None,
                    'props': None}
        elif isinstance(obj, (Index, IndexDetail)):
            return {'field': None}

    def create_tag(self, obj):
        if isinstance(obj, DbdSchema):
            for key, value in self.assembly_attributes(obj).items():
                self.doc.getElementsByTagName('dbd_schema')[0].setAttribute(key, value)
        elif isinstance(obj, (Domain, Table, Field, ConstraintDetail, IndexDetail)):
            if isinstance(obj, (Domain, Table)):
                element = self.doc.getElementsByTagName(obj.__class__.__name__.lower()+'s')[0]
            else:
                element = self.doc.getElementsByTagName('table')[-1]
            child_element = self.doc.createElement(self.get_name_by_object(obj))
            for key, value in self.assembly_attributes(obj).items():
                child_element.setAttribute(key, value)
            element.appendChild(child_element)

    def prefix_traverse(self, tree, doc, child_doc):
        if isinstance(tree, dict):
            for key, value in tree.items():
                if value is not None:
                    if isinstance(key, (DbdSchema, Table)):
                        self.create_tag(key)
                    self.prefix_traverse(value, doc, child_doc)
        elif isinstance(tree, list):
            for element in tree:
                self.create_tag(element)
