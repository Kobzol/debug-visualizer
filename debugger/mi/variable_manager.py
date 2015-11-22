# -*- coding: utf-8 -*-

from enums import BasicTypeCategory, TypeCategory
from mi.parser import Parser
from variable import Type

basic_type_map = {
    "bool" : BasicTypeCategory.Bool,
    "char" : BasicTypeCategory.Char,
    "signed char": BasicTypeCategory.SignedChar,
    "unsigned char": BasicTypeCategory.UnsignedChar,
    "char16_t": BasicTypeCategory.Char16,
    "wchar_t": BasicTypeCategory.WChar,
    "unsigned wchar_t": BasicTypeCategory.UnsignedWChar,
    "short": BasicTypeCategory.Short,
    "unsigned short": BasicTypeCategory.UnsignedShort,
    "int": BasicTypeCategory.Int,
    "signed int": BasicTypeCategory.Int,
    "unsigned int": BasicTypeCategory.UnsignedInt,
    "long": BasicTypeCategory.Long,
    "unsigned long": BasicTypeCategory.UnsignedLong,
    "long long": BasicTypeCategory.LongLong,
    "unsigned long long": BasicTypeCategory.UnsignedLongLong,
    "void": BasicTypeCategory.Void,
    "float": BasicTypeCategory.Float,
    "double": BasicTypeCategory.Double,
    "long double": BasicTypeCategory.LongDouble
}

"""
    Basic types:
    Bool = 20
    Char = 2
    Char16 = 8
    Char32 = 9
    Double = 23
    DoubleComplex = 26
    Float = 22
    FloatComplex = 25
    Half = 21
    Int = 12
    Int128 = 18
    Invalid = 0
    Long = 14
    LongDouble = 24
    LongDoubleComplex = 27
    LongLong = 16
    NullPtr = 31
    ObjCClass = 29
    ObjCID = 28
    ObjCSel = 30
    Other = 32
    Short = 10
    SignedChar = 3
    SignedWChar = 6
    UnsignedChar = 4
    UnsignedInt = 13
    UnsignedInt128 = 19
    UnsignedLong = 15
    UnsignedLongLong = 17
    UnsignedShort = 11
    UnsignedWChar = 7
    Void = 1
    WChar = 5

    Types:
    Any = -1
    Array = 1
    BlockPointer = 2
    Builtin = 4
    Class = 8
    ComplexFloat = 16
    ComplexInteger = 32
    Enumeration = 64
    Function = 128
    Invalid = 0
    MemberPointer = 256
    ObjCInterface = 1024
    ObjCObject = 512
    ObjCObjectPointer = 2048
    Other = -2147483648
    Pointer = 4096
    Reference = 8192
    Struct = 16384
    Typedef = 32768
    Union = 65536
    Vector = 131072
    """


class VariableManager(object):
    def __init__(self, debugger):
        """
        @type debugger: mi.debugger.Debugger
        """
        self.debugger = debugger
        self.parser = Parser()

    def get_type(self, expression):
        """
        @type expression: str
        @return: variable.Type
        """
        output = self.debugger.communicator.send("ptype {0}".format(expression))
        short_output = self.debugger.communicator.send("whatis {0}".format(expression))

        if output and short_output:
            type = self.parser.parse_variable_type(output.cli_data[0])
            type_name = self.parser.parse_variable_type(short_output.cli_data[0])
            basic_type_category = BasicTypeCategory.Invalid
            type_category = TypeCategory.Any

            if type in basic_type_map:
                basic_type_category = basic_type_map[type]
                type_category = TypeCategory.Builtin
            else:
                if type.startswith("struct"):
                    type_category = TypeCategory.Struct
                elif type.startswith("class"):
                    type_category = TypeCategory.Class
                elif type.startswith("union"):
                    type_category = TypeCategory.Union
                elif type.startswith("enum"):
                    type_category = TypeCategory.Enumeration
                elif type.endswith("*"):
                    type_category = TypeCategory.Pointer
                elif type.endswith("&"):
                    type_category = TypeCategory.Reference
                elif type.endswith("]"):
                    type_category = TypeCategory.Array
                elif type.endswith(")"):
                    type_category = TypeCategory.Function
                elif type.startswith("std::vector"):
                    type_category = TypeCategory.Vector
                elif type.startswith("std::string"):
                    type_category = TypeCategory.String

            return Type(type_name, type_category, basic_type_category)
        else:
            return None
