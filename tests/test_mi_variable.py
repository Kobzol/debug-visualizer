from conftest import wait_until_state
from enums import ProcessState, TypeCategory, BasicTypeCategory


def prepare_debugger(debugger):
    debugger.load_binary("src/test_variable")
    debugger.breakpoint_manager.add_breakpoint("src/test_variable.cpp", 35)
    debugger.launch()
    wait_until_state(debugger, ProcessState.Stopped)


def check_variable(debugger, expression, value):
    variable = debugger.variable_manager.get_variable(expression)

    assert variable.path == expression
    assert variable.value == value


def test_types(debugger):
    prepare_debugger(debugger)

    check_variable(debugger, "a", "5")
    check_variable(debugger, "b", "5.5")
    check_variable(debugger, "c", "true")
    check_variable(debugger, "d", "hello")
    check_variable(debugger, "strA.x", "5")

    vec = debugger.variable_manager.get_variable("vec")
    assert map(lambda child: int(child.value), vec.children) == [1, 2, 3]
