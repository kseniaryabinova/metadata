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

    def get_attribute_by_name(self, name):
        if name in self.__dict__.keys():
            return self.__dict__[name]


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

    def get_attribute_by_name(self, name):
        if name in self.__dict__.keys():
            return self.__dict__[name]

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

    def get_attribute_by_name(self, name):
        if name in self.__dict__.keys():
            return self.__dict__[name]


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

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def is_valid(self):
        if not self.name:
            return False
        return True

    def get_attribute_by_name(self, name):
        if name in self.__dict__.keys():
            return self.__dict__[name]


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

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def is_valid(self):
        if not self.constraint_type:
            return False
        return True

    def get_attribute_by_name(self, name):
        if name in self.__dict__.keys():
            return self.__dict__[name]


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

    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def is_valid(self):
        if not self.name:
            return False
        return True

    def get_attribute_by_name(self, name):
        if name in self.__dict__.keys():
            return self.__dict__[name]


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
