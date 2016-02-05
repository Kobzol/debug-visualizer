# -*- coding: utf-8 -*-

from enums import BasicTypeCategory, TypeCategory
from util import EventBroadcaster


class Type(object):
    """
    Represent's variable's type.
    """
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
        """
        self.name = name
        self.type_category = type_category
        self.basic_type_category = basic_type_category
        self.size = size

    def is_composite(self):
        """
        Return true if this type is a composite type, containing child elements (struct, class, vector, array)
        @rtype: bool
        """
        return self.type_category in (TypeCategory.Struct, TypeCategory.Class, TypeCategory.Vector, TypeCategory.Array)

    def is_valid(self):
        """
        Checks that the type is valid.
        @rtype: bool
        """
        return self.type_category != TypeCategory.Invalid

    def __repr__(self):
        return "Type {0}: {1}".format(self.type_category, self.name)


class Variable(object):
    """
    Represents a variable with type.
    """
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
        Adds a child variable to this variable.
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
        return "Variable: {0} ({1}) = {2}".format(self.type, self.path if self.path else self.name, self.value)


class PointerVariable(Variable):
    def __init__(self, target_type, *args, **kwargs):
        """
        @type target_type: Type
        """
        super(PointerVariable, self).__init__(*args, **kwargs)
        self.target_type = target_type


class Frame(object):
    """
    Represents a stack frame of the debugged process.
    """
    def __init__(self, level, func, file, line):
        """
        @type level: int
        @type func: str
        @type file: str
        @type line: int
        """
        self.level = level
        self.func = func
        self.file = file
        self.line = line
        self.variables = []

    def __repr__(self):
        return "Frame #{0} ({1} at {2}:{3}".format(self.level, self.func, self.file, self.line)


class ThreadInfo(object):
    """
    Represents thread state (list of threads and the selected thread) of the debugged process.
    """
    def __init__(self, selected_thread, threads):
        """
        @type selected_thread: InferiorThread
        @type threads: list of InferiorThread
        """
        self.selected_thread = selected_thread
        self.threads = threads

    def __repr__(self):
        return "Thread info: active: {0}, threads: {1}".format(str(self.selected_thread), str(self.threads))


class InferiorThread(object):
    """
    Represents a thread of the debugged process.
    """
    def __init__(self, id, name, state, frame=None):
        """
        @type id: int
        @type name: str
        @type state: enums.ProcessState
        @type frame: Frame
        """
        self.id = id
        self.name = name
        self.state = state
        self.frame = frame

    def __repr__(self):
        return "Thread #{0} ({1}): {2}".format(self.id, self.name, self.state)


class Breakpoint(object):
    """
    Represents a breakpoint.
    """
    def __init__(self, number, location, line):
        """
        @type number: int
        @type location: str
        @type line: int
        """
        self.number = number
        self.location = location
        self.line = line

    def __repr__(self):
        return "BP #{0}: {1}:{2}".format(self.number, self.location, self.line)


class Register(object):
    def __init__(self, name, value):
        """
        Represents a CPU register.
        @type name: str
        @type value: str
        """
        self.name = name
        self.value = value

    def __repr__(self):
        return "Register: {} = {}".format(self.name, self.value)
