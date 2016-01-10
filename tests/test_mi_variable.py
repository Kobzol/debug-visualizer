import ctypes
int_size = ctypes.sizeof(ctypes.c_voidp)


def prepare_debugger(debugger):
    debugger.load_binary("src/test_variable")
    debugger.breakpoint_manager.add_breakpoint("src/test_variable.cpp", 35)
    debugger.launch()
    debugger.wait_for_stop()


def check_variable(debugger, expression, value, size=None):
    variable = debugger.variable_manager.get_variable(expression)

    assert variable.path == expression
    assert variable.value == value

    if size:
        assert variable.type.size == size


def test_values(debugger):
    prepare_debugger(debugger)

    check_variable(debugger, "a", "5", int_size)
    check_variable(debugger, "b", "5.5", int_size)
    check_variable(debugger, "c", "true", 1)
    check_variable(debugger, "d", "hello")
    check_variable(debugger, "strA.x", "5", int_size)

    vec = debugger.variable_manager.get_variable("vec")
    assert map(lambda child: int(child.value), vec.children) == [1, 2, 3]


def test_update_variable(debugger):
    prepare_debugger(debugger)

    a = debugger.variable_manager.get_variable("a")
    a.value = "8"

    assert debugger.variable_manager.get_variable("a").value == "8"

    d = debugger.variable_manager.get_variable("d")
    d.value = "hi"

    assert debugger.variable_manager.get_variable("d").value == "hi"

    vec = debugger.variable_manager.get_variable("vec")
    vec.children[0].value = "10"

    assert debugger.variable_manager.get_variable("vec").children[0].value == "10"


def test_get_memory(debugger):
    prepare_debugger(debugger)

    var = debugger.variable_manager.get_variable("a")

    assert [5, 0, 0, 0] == debugger.variable_manager.get_memory(var.address, var.type.size)
    assert len(debugger.variable_manager.get_memory(var.address, 128)) == 128
