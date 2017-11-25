from abc import ABC, abstractmethod


class AbstractDBObject:
    def set_attributes(self, init_dict):
        for key, value in self.__dict__.items():
            if key in init_dict.keys():
                self.__dict__[key] = init_dict[key]

    def get_attribute_by_name(self, name):
        if name in self.__dict__.keys():
            return self.__dict__[name]


class DbdSchema(AbstractDBObject):
    def __init__(self):
        self.fulltext_engine = None
        self.version = None
        self.name = None
        self.description = None

    def is_valid(self):
        if not self.name:
            return False
        return True


class Domain(AbstractDBObject):
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

    def is_valid(self):
        if not self.name:
            return False
        return True


class Table(AbstractDBObject):
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

    def is_valid(self):
        if not self.name:
            return False
        return True


class Field(AbstractDBObject):
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

    def is_valid(self):
        if not self.name:
            return False
        return True


class Constraint(AbstractDBObject):
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

    def is_valid(self):
        if not self.constraint_type:
            return False
        return True


class ConstraintDetail(AbstractDBObject):
    def __init__(self):
        self.id = None
        self.constraint_id = None
        self.position = None
        self.field_id = None

    def is_valid(self):
        if not self.constraint_id or not self.field_id:
            self.__dict__ = None
            raise Exception


class Index(AbstractDBObject):
    def __init__(self):
        self.id = None
        self.table_id = None
        self.name = None
        self.local = None
        self.kind = None
        self.uuid = None

    def is_valid(self):
        if not self.name:
            return False
        return True


class IndexDetail(AbstractDBObject):
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
