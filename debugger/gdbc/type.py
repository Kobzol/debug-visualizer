# -*- coding: utf-8 -*-

from enum import IntEnum


class TypeCode(IntEnum):
    Pointer = 1
    Array = 2
    Struct = 3
    Union = 4
    Enum = 5
    Int = 6
    Float = 7
    String = 8
    Char = 9
    Bool = 10
    Reference = 11
    Function = 12
    Method = 13
    Void = 14
    Unknown = 15


class Type(object):
    type_cache = {}

    @classmethod
    def register_type(cls, gdb_type):
        if gdb_type is None:
            return

        gdb_type = cls.get_raw_type(gdb_type)
        name = gdb_type.name

        if name not in cls.type_cache:
            size = gdb_type.sizeof
            code = cls.parse_gdb_code(gdb_type.code)
            target = None

            if code == TypeCode.Pointer:
                target = gdb_type.target().name

            members = []

            try:
                for field in gdb_type.fields():
                    member_type = cls.from_gdb_type(field.type)
                    member_name = field.name
                    members.append(Member(member_name, name, member_type.name,
                                          member_type.size,
                                          code,
                                          member_type.fields,
                                          member_type.target))
            except:
                pass

            final_type = Type(name, size, code, members, target)
            cls.type_cache[name] = final_type

    @staticmethod
    def get_raw_type(gdb_type):
        names_to_keep = ["std::string"]

        if gdb_type.name in names_to_keep:
            return gdb_type
        else:
            return gdb_type.strip_typedefs()

    @classmethod
    def from_gdb_type(cls, gdb_type):
        cls.register_type(gdb_type)

        return cls.type_cache[cls.get_raw_type(gdb_type).name]

    @staticmethod
    def parse_gdb_code(gdb_code):
        import gdb

        map = {
            gdb.TYPE_CODE_PTR: TypeCode.Pointer,
            gdb.TYPE_CODE_ARRAY: TypeCode.Array,
            gdb.TYPE_CODE_STRUCT: TypeCode.Struct,
            gdb.TYPE_CODE_UNION: TypeCode.Union,
            gdb.TYPE_CODE_ENUM: TypeCode.Enum,
            gdb.TYPE_CODE_INT: TypeCode.Int,
            gdb.TYPE_CODE_FLT: TypeCode.Float,
            gdb.TYPE_CODE_STRING: TypeCode.String,
            gdb.TYPE_CODE_CHAR: TypeCode.Char,
            gdb.TYPE_CODE_BOOL: TypeCode.Bool,
            gdb.TYPE_CODE_REF: TypeCode.Reference,
            gdb.TYPE_CODE_FUNC: TypeCode.Function,
            gdb.TYPE_CODE_METHOD: TypeCode.Method,
            gdb.TYPE_CODE_VOID: TypeCode.Void
        }

        if gdb_code in map:
            return map[gdb_code]
        else:
            return TypeCode.Unknown

    def __init__(self, name, size, code, fields=None, target=None):
        if fields is None:
            fields = []

        self.name = str(name)
        self.size = int(size)
        self.code = code
        self.fields = fields
        self.target = target

    def __repr__(self):
        repr = "{} ({}, {} bytes)".format(self.name, TypeCode(self.code),
                                          self.size)

        if self.target:
            repr += " targets " + str(self.target)

        return repr


class Member(Type):
    def __init__(self, member_name, parent_name, name, size, code, fields=None,
                 target=None):
        if fields is None:
            fields = []
        Type.__init__(self, name, size, code, fields, target)
        self.member_name = member_name
        self.parent_name = parent_name
