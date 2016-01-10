# -*- coding: utf-8 -*-
import re

from enums import BasicTypeCategory, TypeCategory
from mi.parser import Parser
from variable import Type, Variable

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

            size = None
            size_output = self.debugger.communicator.send("p sizeof({0})".format(type_name))
            if size_output:
                size = int(self.parser.parse_print_expression(size_output.cli_data[0]))

            return Type(type_name, type_category, basic_type_category, size)
        else:
            return None

    def get_variable(self, expression):
        """
        @type expression: str
        @return: variable.Variable
        """
        type = self.get_type(expression)
        output = self.debugger.communicator.send("p {0}".format(expression))

        if output and type:
            data = self.parser.parse_print_expression(output.cli_data)
            address = None

            address_output = self.debugger.communicator.send("p &{0}".format(expression))
            if address_output:
                address = self.parser.parse_print_expression(address_output.cli_data)
                address = address[address.rfind(" ") + 1:]

            name = self._get_name(expression)
            value = None
            children = []

            if type.type_category in (TypeCategory.Builtin, TypeCategory.Pointer,
                                      TypeCategory.Reference, TypeCategory.Function):
                value = data
            elif type.type_category == TypeCategory.String:
                value = data.strip("\"")
            elif type.type_category in (TypeCategory.Class, TypeCategory.Struct):
                result = self.debugger.communicator.send(
                    "python print([field.name for field in gdb.lookup_type(\"{0}\").fields()])".format(type.name)
                )

                if result:
                    members = self.parser.parse_struct_member_names(result.cli_data[0])
                    for member in members:
                        children.append(self.get_variable("{0}.{1}".format(expression, member)))

            elif type.type_category == TypeCategory.Vector:
                length = self.debugger.communicator.send("call {0}.size()".format(expression))

                if length:
                    length = int(self.parser.parse_print_expression(length.cli_data))
                    for i in xrange(length):
                        expr = "*({0}._M_impl._M_start + {1})".format(expression, i)
                        children.append(self.get_variable(expr))
            else:
                pass  # TODO

            variable = Variable(address, name, value, type, expression)
            variable.on_value_changed.subscribe(self.update_variable)

            for child in children:
                if child:
                    variable.add_child(child)

            return variable

        else:
            return None

    def update_variable(self, variable):
        format = "set variable {0} = {1}"

        if variable.type.type_category == TypeCategory.String:
            format = "call {0}.assign(\"{1}\")"

        self.debugger.communicator.send(format.format(variable.path, variable.value))

    def get_memory(self, address, count):
        """
        Returns count bytes from the given address.
        @type address: str
        @type count: int
        @return: list of int
        """
        command = "x/{0}xb {1}".format(count, address)
        output = self.debugger.communicator.send(command)

        bytes = []
        for line in output.cli_data:
            start = line.find(":")
            line = line[start + 1:]
            for num in line.split("\\t"):
                if num:
                    bytes.append(int(num, 16))

        return bytes

    def _get_name(self, expression):
        """
        @type expression: str
        @return: str
        """
        match = re.search("([a-zA-Z_$]+)$", expression)

        if match:
            return match.group(0)
        else:
            return expression