import ctypes

from enums import ProcessState

int_size = ctypes.sizeof(ctypes.c_voidp)


def prepare_debugger(debugger, on_state_change=None):
    assert debugger.load_binary("src/test_variable")
    assert debugger.breakpoint_manager.add_breakpoint("src/test_variable.cpp", 36)
    assert debugger.launch()
    debugger.wait_for_stop()

    if on_state_change:
        def on_stop(state, data):
            if state == ProcessState.Stopped:
                on_state_change()
        debugger.on_process_state_changed.subscribe(on_stop)


def check_variable(debugger, expression, value, size=None):
    variable = debugger.variable_manager.get_variable(expression)

    assert variable.path == expression
    assert variable.value == value

    if size:
        assert variable.type.size == size


def test_values(debugger):
    def test_values_cb():
        check_variable(debugger, "a", "5", int_size)
        check_variable(debugger, "b", "5.5", int_size)
        check_variable(debugger, "c", "true", 1)
        check_variable(debugger, "d", "hello")
        check_variable(debugger, "strA.x", "5", int_size)

        vec = debugger.variable_manager.get_variable("vec")
        assert map(lambda child: int(child.value), vec.children) == [1, 2, 3]

    prepare_debugger(debugger, test_values_cb)


def test_update_variable(debugger):
    def test_update_variable_cb():
        a = debugger.variable_manager.get_variable("a")
        a.value = "8"

        assert debugger.variable_manager.get_variable("a").value == "8"

        d = debugger.variable_manager.get_variable("d")
        d.value = "hi"

        assert debugger.variable_manager.get_variable("d").value == "hi"

        vec = debugger.variable_manager.get_variable("vec")
        vec.children[0].value = "10"

        assert debugger.variable_manager.get_variable("vec").children[0].value == "10"

    prepare_debugger(debugger, test_update_variable_cb)


def test_get_memory(debugger):
    def test_get_memory_cb():
        var = debugger.variable_manager.get_variable("a")

        assert [5, 0, 0, 0] == debugger.variable_manager.get_memory(var.address, var.type.size)
        assert len(debugger.variable_manager.get_memory(var.address, 128)) == 128

    prepare_debugger(debugger, test_get_memory_cb)
