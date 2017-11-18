import copy
# TODO
# TODO добавить validate, write методы
# TODO убрать get_attributes


# class AbstractDBObject:
#     def __init__(self):
#         pass
#
#     def set_attributes(self, attr_dict):
#         pass
#
#     def is_valid(self):
#         if not self.name:
#             self.__dict__ = None
#             raise Exception


class DbdSchema:
    def __init__(self):
        self.fulltext_engine = None
        self.version = None
        self.name = None
        self.description = None

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def is_valid(self):
        if not self.name:
            return False
        return True


class Domain:
    def __init__(self):
        self.id = None
        self.name = None
        self.description = None
        self.type = None
        self.data_type_id = None
        self.length = None
        self.char_length = None
        self.precision = None
        self.scale = None
        self.width = None
        self.align = None
        self.show_null = None
        self.show_lead_nulls = None
        self.thousands_separator = None
        self.summable = None
        self.case_sensitive = None
        self.uuid = None

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

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

    def is_valid(self):
        if not self.name:
            return False
        return True


class Table:
    def __init__(self):
        self.id = None
        self.schema_id = None
        self.name = None
        self.description = None
        self.can_add = None
        self.can_edit = None
        self.can_delete = None
        self.temporal_mode = None
        self.means = None
        self.uuid = None

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

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def is_valid(self):
        if not self.name:
            return False
        return True


class Field:
    def __init__(self):
        self.id = None
        self.table_id = None
        self.position = None
        self.name = None
        self.russian_short_name = None
        self.description = None
        self.domain_id = None
        self.can_input = None
        self.can_edit = None
        self.show_in_grid = None
        self.show_in_details = None
        self.is_mean = None
        self.autocalculated = None
        self.required = None
        self.uuid = None

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

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def is_valid(self):
        if not self.name:
            return False
        return True


class Constraint:
    def __init__(self):
        self.id = None
        self.table_id = None
        self.name = None
        self.constraint_type = None
        self.reference = None
        self.unique_key_id = None
        self.has_value_edit = None
        self.cascading_delete = None
        self.expression = None
        self.uuid = None

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

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def is_valid(self):
        if not self.constraint_type:
            return False
        return True


class ConstraintDetail:
    def __init__(self):
        self.id = None
        self.constraint_id = None
        self.position = None
        self.field_id = None

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def is_valid(self):
        if not self.constraint_id or not self.field_id:
            self.__dict__ = None
            raise Exception


class Index:
    def __init__(self):
        self.id = None
        self.table_id = None
        self.name = None
        self.local = None
        self.kind = None
        self.uuid = None

    def get_attributes(self):
        new_dict = copy.copy(self.__dict__)
        new_dict['field'] = new_dict.pop('name')
        new_dict['props'] = new_dict.pop('kind')
        return {k: v for k, v in new_dict.items() if v is not None and k[-2:] != "id"}

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def is_valid(self):
        if not self.name:
            return False
        return True


class IndexDetail:
    def __init__(self):
        self.id = None
        self.index_id = None
        self.position = None
        self.field_id = None
        self.expression = None
        self.descend = None

    def is_valid(self):
        if not self.index_id or not self.field_id:
            self.__dict__ = None
            raise Exception

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]
