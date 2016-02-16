# -*- coding: utf-8 -*-

from enums import TypeCategory, BasicTypeCategory, ProcessState


def prepare_debugger(debugger, on_state_change=None):
    debugger.load_binary("src/test_type")
    debugger.breakpoint_manager.add_breakpoint("src/test_type.cpp", 51)
    debugger.launch()
    debugger.wait_for_stop()

    if on_state_change:
        def on_stop(state, data):
            if state == ProcessState.Stopped:
                on_state_change()
        debugger.on_process_state_changed.subscribe(on_stop)


def check_type(debugger, variable_name, type_name, type_category,
               basic_type_category=BasicTypeCategory.Invalid):
    type = debugger.variable_manager.get_type(variable_name)

    assert type.name == type_name
    assert type.type_category == type_category
    assert type.basic_type_category == basic_type_category


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
        check_type(debugger, "varVector",
                   "std::vector<int, std::allocator<int> >",
                   TypeCategory.Vector)
        check_type(debugger, "varString", "std::string", TypeCategory.String)
        check_type(debugger, "varArray", "int [10]", TypeCategory.Array)
        check_type(debugger, "varPointer", "int *", TypeCategory.Pointer)
        check_type(debugger, "varReference", "int &", TypeCategory.Reference)
        check_type(debugger, "varFunctionPointer", "void (*)(void)",
                   TypeCategory.Function)

    prepare_debugger(debugger, test_types_cb)
