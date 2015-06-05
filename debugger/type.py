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
    Unknown = 12

class Type(object):
    @staticmethod
    def from_gdb_type(gdb_type):
        if gdb_type is None:
            return None
        
        gdb_type = gdb_type.strip_typedefs()
        
        name = gdb_type.name
        size = gdb_type.sizeof
        
        code = Type.parse_gdb_code(gdb_type.code)
        target = None
        
        if code == TypeCode.Pointer:
            target = gdb_type.target().name
        
        members = []
        
        try:
            for field in gdb_type.fields():
                member_type = Type.from_gdb_type(field.type)
                member_name = field.name
                members.append(Member(member_type.name, member_type.size, code, member_name, name, member_type.fields, member_type.target))
        except:
            pass
            
        return Type(name, size, code, members, target)
    
    @staticmethod
    def parse_gdb_code(gdb_code):
        import gdb
        
        map = {
            gdb.TYPE_CODE_PTR : TypeCode.Pointer,
            gdb.TYPE_CODE_ARRAY : TypeCode.Array,
            gdb.TYPE_CODE_STRUCT : TypeCode.Struct,
            gdb.TYPE_CODE_UNION : TypeCode.Union,
            gdb.TYPE_CODE_ENUM : TypeCode.Enum,
            gdb.TYPE_CODE_INT : TypeCode.Int,
            gdb.TYPE_CODE_FLT : TypeCode.Float,
            gdb.TYPE_CODE_STRING : TypeCode.String,
            gdb.TYPE_CODE_CHAR : TypeCode.Char,
            gdb.TYPE_CODE_BOOL : TypeCode.Bool,
            gdb.TYPE_CODE_REF : TypeCode.Reference
        }
        
        if gdb_code in map:
            return map[gdb_code]
        else:
            return TypeCode.Unknown
    
    def __init__(self, name, size, code, fields=[], target=None):
        self.name = str(name)
        self.size = int(size)
        self.code = code
        self.fields = fields
        self.target = target
        
    def __repr__(self):
        repr = self.name + " (" + str(TypeCode(self.code)) + ", " + str(self.size) + " bytes)"
        
        if self.target:
            repr += " targets " + str(self.target)
            
        return repr
        
class Member(Type):
    def __init__(self, name, size, code, member_name, parent_name, fields=[], target=None):
        Type.__init__(self, name, size, code, fields, target)
        self.member_name = member_name
        self.parent_name = parent_name