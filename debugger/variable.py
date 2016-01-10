# -*- coding: utf-8 -*-

from enums import BasicTypeCategory
from enums import TypeCategory
from events import EventBroadcaster


class Type(object):
    typename_replacements = {
        ":__1": "",
        "std::basic_string<char, std::char_traits<char>, std::allocator<char> >": "std::string"
    }

    @staticmethod
    def from_lldb(lldb_type):
        """
        @type lldb_type: lldb.SBType
        @rtype: Type
        """

        type_name = lldb_type.GetCanonicalType().name

        for original, replacement in Type.typename_replacements.iteritems():
            type_name = type_name.replace(original, replacement)

        type_category = TypeCategory(lldb_type.type)

        if type_name.startswith("std::vector"):
            type_category = TypeCategory.Vector

        return Type(type_name, type_category, BasicTypeCategory(lldb_type.GetBasicType()))

    def __init__(self, name, type_category, basic_type_category, size):
        """
        @type name: str
        @type type_category: enums.TypeCategory
        @type basic_type_category: enums.BasicTypeCategory
        @type size: int
        @return:
        """
        self.name = name
        self.type_category = type_category
        self.basic_type_category = basic_type_category
        self.size = size

    def is_composite(self):
        return self.type_category in (TypeCategory.Struct, TypeCategory.Class, TypeCategory.Vector, TypeCategory.Array)

    def is_valid(self):
        return self.type_category != TypeCategory.Invalid

    def __repr__(self):
        return "Type {0}: {1}".format(self.type_category, self.name)


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
        self._value = value
        self.type = type
        self.path = path

        self.children = []

        self.on_value_changed = EventBroadcaster()

    def add_child(self, child):
        """
        @type child: Variable
        """
        self.children.append(child)
        child.on_value_changed.redirect(self.on_value_changed)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.on_value_changed.notify(self)

    def __repr__(self):
        return "Variable: {0} ({1}) = {2}".format(self.type.name, self.path, self.value)
