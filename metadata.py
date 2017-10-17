
class Domain:
    def __init__(self, d):
        self.id = d['id']
        self.name = d['name']
        self.description = d['description']
        self.type = d['type']
        self.data_type_id = d['data_type_id']
        self.length = d['length']
        self.char_length = d['char_length']
        self.precision = d['precision']
        self.scale = d['scale']
        self.width = d['width']
        self.align = d['align']
        self.show_null = d['show_null']
        self.show_lead_nulls = d['show_lead_nulls']
        self.thousands_separator = d['thousands_separator']
        self.summable = d['summable']
        self.case_sensitive = d['case_sensitive']
        self.uuid = d['uuid']

    def get_attributes(self):
        dict_order = {'name': None,
                      'description': None,
                      'type': None,
                      'align': None,
                      'width': None,
                      'props': None,
                      'char_length': None}
        dict_order.update({k: v for k, v in self.__dict__.items()
                           if not k == 'case_sensitive'})
        if 'case_sensitive' in self.__dict__.keys():
            dict_order['props'] = 'case_sensitive'
        return {k: v for k, v in dict_order.items() if v is not None}


class Table:
    def __init__(self, d):
        self.id = d['id']
        self.schema_id = d['schema_id']
        self.name = d['name']
        self.description = d['description']
        self.can_add = d['can_add']
        self.can_edit = d['can_edit']
        self.can_delete = d['can_delete']
        self.temporal_mode = d['temporal_mode']
        self.means = d['means']
        self.uuid = d['uuid']

    def get_attributes(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class Field:
    def __init__(self, d):
        self.id = d['id']
        self.table_id = d['table_id']
        self.position = d['position']
        self.name = d['name']
        self.russian_short_name = d['russian_short_name']
        self.description = d['description']
        self.domain_id = d['domain_id']
        self.can_input = d['can_input']
        self.can_edit = d['can_edit']
        self.show_in_grid = d['show_in_grid']
        self.show_in_details = d['show_in_details']
        self.is_mean = d['is_mean']
        self.autocalculated = d['autocalculated']
        self.required = d['required']
        self.uuid = d['uuid']

    def get_attributes(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

class Setting:
    def __init__(self, key=None, value=None, valueb=None):
        self.key = key
        self.value = value
        self.valueb = valueb


class Constraint:
    def __init__(self, d):
        self.id = d['id']
        self.table_id = d['table_id']
        self.name = d['name']
        self.constraint_type = d['constraint_type']
        self.unique_key_id = d['unique_key_id']
        self.has_value_edit = d['has_value_edit']
        self.cascading_delete = d['cascading_delete']
        self.expression = d['expression']
        self.uuid = d['uuid']

    def get_attributes(self):
        return {k: v for k, v in self.__dict__.items() if v is not None and not k == "table_id"}


class ConstraintDetail:
    def __init__(self, id=None, constraint_id=None, position=None, field_id=None):
        self.id = id
        self.constraint_id = constraint_id
        self.position = position
        self.field_id = field_id


class Index:
    def __init__(self, d):
        self.id = d['id']
        self.table_id = d['table_id']
        self.name = d['name']
        self.local = d['local']
        self.kind = d['kind']
        self.uuid = d['uuid']

    def get_attributes(self):
        return {k: v for k, v in self.__dict__.items() if v is not None and not k == "table_id"}


class IndexDetail:
    def __init__(self, id=None, index_id=None, position=None,
                 field_id=None, expression=None, descend=None):
        self.id = id
        self.index_id = index_id
        self.position = position
        self.field_id = field_id
        self.expression = expression
        self.descend = descend
