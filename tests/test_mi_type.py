# -*- coding: utf-8 -*-

from debugger.enums import TypeCategory, BasicTypeCategory
from tests.conftest import setup_debugger

TEST_FILE = "test_type"
TEST_LINE = 51


def check_type(debugger, variable_name, type_name, type_category,
               basic_type_category=BasicTypeCategory.Invalid):
    type = debugger.variable_manager.get_type(variable_name)

    assert type.name == type_name
    assert type.type_category == type_category
    assert type.basic_type_category == basic_type_category

    return type


def test_types(debugger):
    def test_types_cb():
        check_type(debugger, "varInt", "int", TypeCategory.Builtin,
                   BasicTypeCategory.Int)
        check_type(debugger, "varUnsignedShort", "unsigned short",
                   TypeCategory.Builtin, BasicTypeCategory.UnsignedShort)
        check_type(debugger, "varFloat", "float", TypeCategory.Builtin,
                   BasicTypeCategory.Float)
        check_type(debugger, "varClassA", "classA", TypeCategory.Class)
        check_type(debugger, "varStructA", "structA", TypeCategory.Struct)
        check_type(debugger, "varUnionA", "unionA", TypeCategory.Union)
        check_type(debugger, "varEnumA", "enumA", TypeCategory.Enumeration)
        check_type(debugger, "varEnumB", "enumB", TypeCategory.Enumeration)
        type = check_type(debugger, "varVector",
                          "std::vector<int, std::allocator<int> >",
                          TypeCategory.Vector)
        assert type.child_type.name == "int"

        check_type(debugger, "varString", "std::string", TypeCategory.String)

        type = check_type(debugger, "varArray", "int [10]", TypeCategory.Array)
        assert type.count == 10
        assert type.child_type.name == "int"

        check_type(debugger, "varPointer", "int *", TypeCategory.Pointer)
        check_type(debugger, "varReference", "int &", TypeCategory.Reference)
        check_type(debugger, "varFunctionPointer", "void (*)(void)",
                   TypeCategory.Function)

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_types_cb)
