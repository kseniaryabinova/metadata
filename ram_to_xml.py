# дедлайн - первые 2 задания до 21 октября
# 4 задача должна быть выложена до начала декабря
# from xml.dom.minidom import Document
import re

from metadata import Constraint
from metadata import DbdSchema
from metadata import Domain
from metadata import Field
from metadata import Index
from metadata import Table

from minidom_fixed import Document

from io import StringIO


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

class Writer:
    def __init__(self, database_schema):
        self.database_schema = database_schema

    def ram_to_xml(self):
        self.doc = Document()
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

    def get_domain_attributes(self, dict_order, obj):
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

    def get_table_attributes(self, dict_order, obj):
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

    def get_field_attributes(self, dict_order, obj):
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
        dict_order['domain'] = obj.domain_id.name

    def find_table_obj(self, table_obj):
        for child_key, child_value in self.database_schema.items():
            for grandchild_key, grandchild_value in child_value.items():
                for table, value in grandchild_value['table'].items():
                    if table is table_obj:
                        return value
        raise Exception

    def get_table_dict(self, table_obj):
        for child_key, child_value in self.database_schema.items():
            for grandchild_key, grandchild_value in child_value.items():
                for table_key, table_value in grandchild_value['table'].items():
                    if table_key is table_obj:
                        return table_value
        raise Exception

    def get_constraint_attributes(self, dict_order, obj):
        def get_bool_attributes():
            bool_array = []
            if obj.has_value_edit:
                bool_array.append('has_value_edit')
            if obj.cascading_delete is True:
                bool_array.append('full_cascading_delete')
            if obj.cascading_delete is False:
                bool_array.append('cascading_delete')
            if not bool_array:
                return None
            return ", ".join(bool_array)

        def get_field():
            for detail in self.get_table_dict(obj.table_id)['constraint_detail']:
                if detail.constraint_id is obj:
                    return detail.field_id.name
        dict_order['props'] = get_bool_attributes()
        dict_order['kind'] = obj.constraint_type
        dict_order['items'] = get_field()

    def get_index_attributes(self, dict_order, obj):
        def get_items():
            for detail in self.get_table_dict(obj.table_id)['index_detail']:
                if detail.index_id is obj:
                    return detail.field_id.name
        dict_order['field'] = get_items()

    def assembly_attributes(self, obj):
        try:
            dict_order = self.get_dict_order(obj)
            for key in dict_order.keys():
                dict_order[key] = obj.get_attribute_by_name(key)
            getattr(self, 'get_'+self.get_name_by_object(obj)+'_attributes')(dict_order, obj)
            return {key: value for key, value in dict_order.items() if value is not None}
        except Exception as e:
            raise e

    def get_dict_order(self, obj):
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
                    'props': None}
        elif isinstance(obj, Constraint):
            return {'kind': None,
                    'items': None,
                    'reference': None,
                    'props': None}
        elif isinstance(obj, Index):
            return {'field': None}

    def is_allowed_type(self, obj):
        if isinstance(obj, (DbdSchema, Domain, Field, Index, Constraint)):
            return True
        elif obj in ['domain', 'table']:
            return True
        return False

    def get_name_by_object(self, obj):
        if isinstance(obj, (DbdSchema, Domain, Table, Field, Index, Constraint)):
            word_list = re.findall('[A-Z][a-z]*', str(type(obj)))
            tag_name = "_".join([elem.lower() for elem in word_list])
            return tag_name
        elif obj in ['domain', 'table']:
            return obj+'s'
        elif obj == 'dbd_schema':
            return obj

    def tag(self, obj, doc, doc_child):
        doc_grandchild = doc.createElement(self.get_name_by_object(obj))
        if not isinstance(obj, str):
            for key, value in self.assembly_attributes(obj).items():
                doc_grandchild.setAttribute(key, str(value))
        doc_child.appendChild(doc_grandchild)
        if isinstance(obj, (DbdSchema, Table)) or obj in ['domain', 'table']:
            return doc_grandchild
        else:
            return doc_child

    def prefix_traverse(self, tree, doc, child_doc):
        if isinstance(tree, dict):
            for key, value in tree.items():
                if value is not None:
                    if self.is_allowed_type(key):
                        self.prefix_traverse(value, doc, self.tag(key, doc, child_doc))
                    elif isinstance(key, Table):
                        self.prefix_traverse(value, doc, self.tag(key, doc, doc.getElementsByTagName('tables')[0]))
                    else:
                        self.prefix_traverse(value, doc, child_doc)
        elif isinstance(tree, list):
            for element in tree:
                if self.is_allowed_type(element):
                    self.tag(element, doc, child_doc)
