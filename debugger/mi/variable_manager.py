# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015-2016 Jakub Beranek
#
#    This file is part of Devi.
#
#    Devi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Devi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
#


import re
import traceback

from debugger.enums import BasicTypeCategory, TypeCategory
from debugger.mi.parser import Parser
from debugger.debugee import Type, Variable, Register, PointerVariable,\
    ArrayType, VectorVariable
from debugger import debugger_api
from debugger.util import Logger

basic_type_map = {
    "bool": BasicTypeCategory.Bool,
    "char": BasicTypeCategory.Char,
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


class VariableManager(debugger_api.VariableManager):
    RECURSION_LIMIT = 3

    """
    Handles retrieval and updating of variables and raw memory of the
    debugged process.
    """
    def __init__(self, debugger):
        """
        @type debugger: Debugger
        """
        super(VariableManager, self).__init__(debugger)
        self.parser = Parser()

    def get_type(self, expression, level=0):
        """
        Returns type for the given expression.
        @type expression: str
        @type level: int
        @rtype: debugee.Type
        """
        if level > VariableManager.RECURSION_LIMIT:
            return None

        output = self.debugger.communicator.send("ptype {0}".
                                                 format(expression))
        short_output = self.debugger.communicator.send("whatis {0}".
                                                       format(expression))

        if output and short_output:
            try:
                type = self.parser.parse_variable_type(output.cli_data[0])
                type_name = self.parser.parse_variable_type(
                    short_output.cli_data[0])
            except:
                Logger.debug(traceback.format_exc())
                return None

            basic_type_category = BasicTypeCategory.Invalid
            type_category = TypeCategory.Class

            modificators = []

            try:
                while type.startswith("volatile") or type.startswith("const"):
                    modificator = type[:type.find(" ")]
                    type = type[len(modificator) + 1:]
                    modificators.append(modificator)

                    if type_name.startswith(modificator):
                        type_name = type_name[len(modificator) + 1:]
            except:
                Logger.debug(traceback.format_exc())
                return None

            if type in basic_type_map:
                basic_type_category = basic_type_map[type]
                type_category = TypeCategory.Builtin
            else:
                if type_name.startswith("std::vector"):
                    type_category = TypeCategory.Vector
                elif type_name.startswith("std::string"):
                    type_category = TypeCategory.String
                elif type_name.endswith("*"):
                    type_category = TypeCategory.Pointer
                elif type_name.endswith("&"):
                    type_category = TypeCategory.Reference
                elif type_name.endswith("]"):
                    type_category = TypeCategory.Array
                elif type_name.endswith(")"):
                    type_category = TypeCategory.Function
                elif type.startswith("struct"):
                    type_category = TypeCategory.Struct
                elif type.startswith("class"):
                    type_category = TypeCategory.Class
                elif type.startswith("union"):
                    type_category = TypeCategory.Union
                elif type.startswith("enum"):
                    type_category = TypeCategory.Enumeration

            size = None
            size_output = self.debugger.communicator.send("p sizeof({0})".
                                                          format(type_name))
            if size_output:
                try:
                    size = int(self.parser.parse_print_expression(
                        size_output.cli_data[0]))
                except:
                    Logger.debug(traceback.format_exc())
                    return None

            args = [type_name, type_category, basic_type_category, size,
                    tuple(modificators)]

            try:
                if type_category == TypeCategory.Array:
                    right_bracket_end = type_name.rfind("]")
                    right_bracket_start = type_name.rfind("[")
                    count = int(type_name[
                                right_bracket_start + 1:right_bracket_end])
                    child_type = self.get_type("{}[0]".format(expression),
                                               level + 1)
                    type = ArrayType(count, child_type, *args)
                elif type_category == TypeCategory.Vector:
                    child_type = self.debugger.communicator.send(
                        "python print(gdb.lookup_type(\"{}\")"
                        ".template_argument(0))".format(type_name))
                    child_type = self.get_type(" ".join(child_type.cli_data),
                                               level + 1)
                    type = ArrayType(0, child_type, *args)
                else:
                    type = Type(*args)
            except:
                Logger.debug(traceback.format_exc())
                return None

            return type
        else:
            return None

    def get_variable(self, expression, level=0):
        """
        Returns a variable for the given expression-
        @type expression: str
        @type level: int
        @rtype: debugee.Variable
        """
        if level > VariableManager.RECURSION_LIMIT:
            return None

        type = self.get_type(expression)
        output = self.debugger.communicator.send("p {0}".format(expression))

        if output and type:
            try:
                data = self.parser.parse_print_expression(output.cli_data)
            except:
                Logger.debug(traceback.format_exc())
                return None

            address = None
            address_output = self.debugger.communicator.send(
                "p &{0}".format(expression))

            try:
                if address_output:
                    address = self._parse_address(address_output.cli_data)
            except:
                Logger.debug(traceback.format_exc())

            name = self._get_name(expression)
            value = None
            variable = None
            children = []

            try:
                if type.type_category == TypeCategory.Builtin:
                    value = data
                    variable = Variable(address, name, value, type, expression)

                elif type.type_category == TypeCategory.Pointer:
                        value = data[data.rfind(" ") + 1:].lower()
                        target_type = self.get_type("*{0}".format(expression))

                        if (target_type and BasicTypeCategory.is_char(
                                target_type.basic_type_category)):
                            type.type_category = TypeCategory.CString
                            value = value[1:-1]  # strip quotes
                        variable = PointerVariable(target_type, address, name,
                                                   value, type, expression)

                elif type.type_category == TypeCategory.Reference:
                    value = data[data.find("@") + 1:data.find(":")]
                    address = self.debugger.communicator.send(
                        "p &(&{0})".format(expression))
                    if address:
                        address = self._parse_address(address.cli_data)
                    else:
                        address = "0x0"

                    target_type = self.get_type("*{0}".format(expression))
                    variable = PointerVariable(target_type, address, name,
                                               value, type, expression)

                elif type.type_category == TypeCategory.Function:
                    # skip function pointer type
                    if data.startswith("({}) ".format(type.name)):
                        data = data[(3 + len(type.name)):]

                    variable = Variable(address, name, data, type, expression)

                elif type.type_category == TypeCategory.String:
                    value = data.strip("\"")
                    variable = Variable(address, name, value, type, expression)

                elif type.type_category in (TypeCategory.Class,
                                            TypeCategory.Struct,
                                            TypeCategory.Union):
                    result = self.debugger.communicator.send(
                        "python print([field.name for field in "
                        "gdb.lookup_type(\"{0}\").fields()])".format(type.name)
                    )

                    if result:
                        members = self.parser.parse_struct_member_names(
                            result.cli_data[0])
                        for member in members:
                            child = self.get_variable("({0}).{1}".format(
                                expression, member), level + 1)
                            if child:
                                children.append(child)
                    variable = Variable(address, name, value, type, expression)

                elif type.type_category == TypeCategory.Vector:
                    length = self.get_variable(
                        "({0}._M_impl._M_finish - {0}._M_impl._M_start)"
                        .format(expression), level + 1)

                    if length:
                        length = int(length.value)

                    data_address = self.debugger.communicator.send(
                        "p {}._M_impl._M_start".format(expression))
                    data_address = " ".join(data_address.cli_data).rstrip()
                    data_address = data_address[data_address.rfind(" ") + 1:]
                    variable = VectorVariable(length, data_address, address,
                                              name, value, type, expression)
                elif type.type_category == TypeCategory.Array:
                    length = type.count
                    data_address = self.get_variable(
                        "&({}[0])".format(expression), level + 1)

                    if data_address:
                        data_address = data_address.value
                    else:
                        data_address = ""

                    variable = VectorVariable(length, data_address, address,
                                              name, value, type, expression)

                elif type.type_category == TypeCategory.Enumeration:
                    variable = Variable(address, name, data, type, expression)
                else:
                    return None

            except:
                Logger.debug(traceback.format_exc())
                return None

            if variable:
                variable.on_value_changed.subscribe(self.update_variable)

                for child in children:
                    if child:
                        variable.add_child(child)

            return variable

        else:
            return None

    def update_variable(self, variable):
        """
        Updates the variable's value in the debugged process.
        @type variable: debugee.Variable
        """
        format = "set variable *{0} = {1}"

        value = variable.value

        try:
            if variable.type.type_category == TypeCategory.String:
                format = "call static_cast<std::string*>({0})->assign(\"{1}\")"
            elif BasicTypeCategory.is_char(variable.type.basic_type_category):
                char_value = variable.value
                if len(char_value) == 1 and not char_value[0].isdigit():
                    value = "'{}'".format(char_value)
        except:
            Logger.debug(traceback.format_exc())
            return False

        result = self.debugger.communicator.send(format.format(
            variable.address, value))

        return result.is_success()

    def get_memory(self, address, count):
        """
        Returns count bytes from the given address.
        @type address: str
        @type count: int
        @rtype: list of int
        """
        command = "x/{0}xb {1}".format(count, address)
        output = self.debugger.communicator.send(command)

        bytes = []
        try:
            for line in output.cli_data:
                start = line.find(":")
                line = line[start + 1:]
                for num in line.split("\\t"):
                    if num:
                        bytes.append(int(num, 16))
        except:
            Logger.debug(traceback.format_exc())

        return bytes

    def get_registers(self):
        """
        Returns the register values as a list of tuples with name and value of
        the given register.
        @rtype: list of register.Register
        """
        try:
            register_names = self.debugger.communicator.send(
                "-data-list-register-names")
            if not register_names:
                return []

            register_names = self.parser.parse(
                register_names.data)["register-names"]

            register_values = self.debugger.communicator.send(
                "-data-list-register-values --skip-unavailable x")
            if not register_values:
                return []

            registers = []
            register_values = self.parser.parse(
                register_values.data)["register-values"]
            for reg in register_values:
                number = int(reg["number"])
                if (number < len(register_names) and
                        len(register_names[number]) > 0):
                    registers.append(Register(str(register_names[number]),
                                              str(reg["value"])))
            return registers
        except:
            Logger.debug(traceback.format_exc())

        return []

    def get_vector_items(self, vector):
        """
        @type vector: debugger.debugee.VectorVariable
        @rtype: list of debugger.debugee.Variable
        """
        items = []
        for i in xrange(vector.start, vector.start + vector.count):
            expression = vector.path
            if vector.type.type_category == TypeCategory.Array:
                expression += "[{}]".format(i)
            elif vector.type.type_category == TypeCategory.Vector:
                expression = "*({}._M_impl._M_start + {})".format(
                    expression, i)
            var = self.get_variable(expression)
            if var:
                items.append(var)

        vector.children = items

        return items

    def _get_name(self, expression):
        """
        Returns name from the given expression.
        @type expression: str
        @rtype: str
        """
        match = re.search("([a-zA-Z_$]+)$", expression)

        if match:
            return match.group(0)
        else:
            return expression

    def _parse_address(self, expression):
        """
        @type expression: str
        @rtype: str | None
        """
        try:
            address = self.parser.parse_print_expression(expression)

            if len(address) > 0 and address[0] == "(":
                return address[address.rfind(" ") + 1:]
            elif address[:2] == "0x":
                return address[:address.find(" ")]
        except:
            Logger.debug(traceback.format_exc())

        return None
