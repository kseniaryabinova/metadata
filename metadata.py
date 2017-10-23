import copy


class Schema:
    def __init__(self, init_dict):
        self.fulltext_engine = init_dict['fulltext_engine']
        self.version = init_dict['version']
        self.name = init_dict['name']
        self.description = init_dict['description']


class Domain:
    def __init__(self, init_dict):
        self.id = init_dict['id']
        self.name = init_dict['name']
        self.description = init_dict['description']
        self.type = init_dict['type']
        self.data_type_id = init_dict['data_type_id']
        self.length = init_dict['length']
        self.char_length = init_dict['char_length']
        self.precision = init_dict['precision']
        self.scale = init_dict['scale']
        self.width = init_dict['width']
        self.align = init_dict['align']
        self.show_null = init_dict['show_null']
        self.show_lead_nulls = init_dict['show_lead_nulls']
        self.thousands_separator = init_dict['thousands_separator']
        self.summable = init_dict['summable']
        self.case_sensitive = init_dict['case_sensitive']
        self.uuid = init_dict['uuid']

    def get_attributes(self):
        dict_order = {'name': None,
                      'description': None,
                      'type': None,
                      'align': None,
                      'width': None,
                      'length': None,
                      'precision': None,
                      'props': None,
                      'scale': None,
                      'char_length': None}
        dict_order.update({k: v for k, v in self.__dict__.items()
                           if v is not None and v is not True})
        s = ""
        for k, v in self.__dict__.items():
            if v is True:
                s += k + ', '
        if not s == "":
            dict_order['props'] = s[:-2]
        return {k: v for k, v in dict_order.items() if v is not None and k[-2:] != "id"}


class Table:
    def __init__(self, init_dict):
        self.id = init_dict['id']
        self.schema_id = init_dict['schema_id']
        self.name = init_dict['name']
        self.description = init_dict['description']
        self.can_add = init_dict['can_add']
        self.can_edit = init_dict['can_edit']
        self.can_delete = init_dict['can_delete']
        self.temporal_mode = init_dict['temporal_mode']
        self.means = init_dict['means']
        self.uuid = init_dict['uuid']

    def get_attributes(self):
        dict_order = {'name': None,
                      'description': None,
                      'props': None}
        dict_order.update({k: v for k, v in self.__dict__.items()
                           if v is not None and v is not True})
        s = ""
        for k, v in self.__dict__.items():
            if v is True:
                s += k[4:] + ', '
        if not s == "":
            dict_order['props'] = s[:-2]
        return {k: v for k, v in dict_order.items() if v is not None and k[-2:] != "id"}


class Field:
    def __init__(self, init_dict):
        self.id = init_dict['id']
        self.table_id = init_dict['table_id']
        self.position = init_dict['position']
        self.name = init_dict['name']
        self.russian_short_name = init_dict['russian_short_name']
        self.description = init_dict['description']
        self.domain_id = init_dict['domain_id']
        self.can_input = init_dict['can_input']
        self.can_edit = init_dict['can_edit']
        self.show_in_grid = init_dict['show_in_grid']
        self.show_in_details = init_dict['show_in_details']
        self.is_mean = init_dict['is_mean']
        self.autocalculated = init_dict['autocalculated']
        self.required = init_dict['required']
        self.uuid = init_dict['uuid']

    def get_attributes(self):
        s = ""
        for k, v in self.__dict__.items():
            if v is True:
                if k[:4] == "can_":
                    s += k[4:] + ', '
                else:
                    s += k + ', '
        new_dict = {}
        if not s == "":
            new_dict['props'] = s[:-2]
        new_dict.update({k: v for k, v in self.__dict__.items()
                        if v is not None and v is not True})
        new_dict['rname'] = new_dict.pop('russian_short_name')
        dict_order = {'name': None,
                      'rname': None,
                      'domain': "",
                      'description': None,
                      'props': None}
        dict_order.update(new_dict)
        return {k: v for k, v in dict_order.items() if v is not None and k[-2:] != "id"}


class Setting:
    def __init__(self, key=None, value=None, valueb=None):
        self.key = key
        self.value = value
        self.valueb = valueb


class Constraint:
    def __init__(self, init_dict):
        self.id = init_dict['id']
        self.table_id = init_dict['table_id']
        self.name = init_dict['name']
        self.constraint_type = init_dict['constraint_type']
        self.reference = init_dict['reference']
        self.unique_key_id = init_dict['unique_key_id']
        self.has_value_edit = init_dict['has_value_edit']
        self.cascading_delete = init_dict['cascading_delete']
        self.expression = init_dict['expression']
        self.uuid = init_dict['uuid']

    def get_attributes(self):
        new_dict = {}
        if any(value is True or value is False for value in self.__dict__.values()):
            a = self.__dict__.values()
            b = [True, False, None] in a
            new_dict['props'] = ""
            if self.__dict__['has_value_edit'] is True:
                new_dict['props'] = 'has_value_edit'
            if self.__dict__['cascading_delete'] is not None:
                if self.__dict__['has_value_edit'] is not None:
                    new_dict['props'] += ', '
                if self.__dict__['cascading_delete'] is True:
                    new_dict['props'] += 'full_cascading_delete'
                elif self.__dict__['cascading_delete'] is False:
                    new_dict['props'] += 'cascading_delete'
        new_dict.update({k: v for k, v in self.__dict__.items()
                        if v not in [True, False, None]})
        new_dict['kind'] = new_dict.pop('constraint_type')
        dict_order = {'kind': None,
                      'items': "",
                      'reference': None,
                      'props': None}
        dict_order.update(new_dict)
        return {k: v for k, v in dict_order.items() if v is not None}


class ConstraintDetail:
    def __init__(self, init_dict):
        self.id = init_dict['id']
        self.constraint_id = init_dict['constraint_id']
        self.position = init_dict['position']
        self.field_id = init_dict['field_id']


class Index:
    def __init__(self, init_dict):
        self.id = init_dict['id']
        self.table_id = init_dict['table_id']
        self.name = init_dict['name']
        self.local = init_dict['local']
        self.kind = init_dict['kind']
        self.uuid = init_dict['uuid']

    def get_attributes(self):
        new_dict = copy.copy(self.__dict__)
        new_dict['field'] = new_dict.pop('name')
        new_dict['props'] = new_dict.pop('kind')
        return {k: v for k, v in new_dict.items() if v is not None and k[-2:] != "id"}


class IndexDetail:
    def __init__(self, id=None, index_id=None, position=None,
                 field_id=None, expression=None, descend=None):
        self.id = id
        self.index_id = index_id
        self.position = position
        self.field_id = field_id
        self.expression = expression
        self.descend = descend
