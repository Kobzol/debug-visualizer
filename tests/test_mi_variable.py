from enums import ProcessState


def prepare_debugger(debugger):
    debugger.load_binary("src/test_variable")
    debugger.breakpoint_manager.add_breakpoint("src/test_variable.cpp", 35)
    debugger.launch()
    debugger.wait_for_stop()


def check_variable(debugger, expression, value):
    variable = debugger.variable_manager.get_variable(expression)

    assert variable.path == expression
    assert variable.value == value


def test_values(debugger):
    prepare_debugger(debugger)

    check_variable(debugger, "a", "5")
    check_variable(debugger, "b", "5.5")
    check_variable(debugger, "c", "true")
    check_variable(debugger, "d", "hello")
    check_variable(debugger, "strA.x", "5")

    vec = debugger.variable_manager.get_variable("vec")
    assert map(lambda child: int(child.value), vec.children) == [1, 2, 3]


def test_update_variable(debugger):
    prepare_debugger(debugger)

    a = debugger.variable_manager.get_variable("a")
    a.change_value("8")

    assert debugger.variable_manager.get_variable("a").value == "8"
