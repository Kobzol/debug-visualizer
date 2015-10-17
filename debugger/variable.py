# -*- coding: utf-8 -*-

from enums import BasicTypeCategory
from enums import TypeCategory


class Type(object):
    type_replacements = {
        "std::basic_string<char, std::char_traits<char>, std::allocator<char> >": "std::string"
    }

    @staticmethod
    def from_lldb(lldb_type):
        """
        @type lldb_type: lldb.SBType
        @rtype: Type
        """

        type_name = lldb_type.GetCanonicalType().name.replace("::__1", "")

        if type_name in Type.type_replacements:
            type_name = Type.type_replacements[type_name]

        return Type(type_name, TypeCategory(lldb_type.type), BasicTypeCategory(lldb_type.GetBasicType()))

    def __init__(self, name, type_category, basic_type_category):
        """
        @type name: str
        @type type_category: enums.TypeCategory
        @type basic_type_category: enums.BasicTypeCategory
        @return:
        """
        self.name = name
        self.type_category = type_category
        self.basic_type_category = basic_type_category

    def is_composite(self):
        return self.type_category in (TypeCategory.Struct, TypeCategory.Class)

    def is_valid(self):
        return self.type_category != TypeCategory.Invalid

    def __repr__(self):
        return "{{{0}: {1}}}".format(self.type_category, self.name)


class Variable(object):
    @staticmethod
    def from_lldb(lldb_var):
        """
        @type lldb_var: lldb.SBValue
        @rtype: Variable
        """
        address = str(lldb_var.addr)
        name = lldb_var.name
        value = lldb_var.value

        if value is None:
            value = lldb_var.summary

        type = Type.from_lldb(lldb_var.type)
        path = lldb_var.path

        var = Variable(address, name, value, type, path)

        if type.is_composite():
            for i in xrange(lldb_var.num_children):
                var.add_child(Variable.from_lldb(lldb_var.GetChildAtIndex(i)))

        return var

    def __init__(self, address=None, name=None, value=None, type=None, path=None):
        """
        @type address: str
        @type name: str
        @type value: str
        @type type: Type
        @type path: str
        """
        self.address = address
        self.name = name
        self.value = value
        self.type = type
        self.path = path

        self.children = []

    def add_child(self, child):
        """
        @type child: Variable
        """
        self.children.append(child)

    def __repr__(self):
        return "({0} {1} = {2})".format(self.type.name, self.path, self.value)
