# -*- coding: utf-8 -*-

from collections import Iterable

from tests.conftest import setup_debugger

int_size = (4, 8)
TEST_FILE = "test_variable"
TEST_LINE = 36


def check_variable(debugger, expression, value=None, size=None):
    variable = debugger.variable_manager.get_variable(expression)

    assert variable.path == expression

    if value is not None:
        assert variable.value == value

    if size:
        if isinstance(size, Iterable):
            assert variable.type.size in size
        else:
            assert variable.type.size == size

    return variable


def test_values(debugger):
    def test_values_cb():
        check_variable(debugger, "a", "5", int_size)
        check_variable(debugger, "b", "5.5", int_size)
        check_variable(debugger, "c", "true", 1)
        check_variable(debugger, "d", "hello")
        var = check_variable(debugger, "e")
        assert var.data_address == var.address
        assert var.max_size == 10
        arr_item = debugger.variable_manager.get_variable("e[2]")
        assert arr_item.value == "3"
        assert var.get_index_by_address(arr_item.address) == 2

        check_variable(debugger, "strA.x", "5", int_size)

        vec = debugger.variable_manager.get_variable("vec")
        vec.count = vec.max_size
        debugger.variable_manager.get_vector_items(vec)
        assert map(lambda child: int(child.value), vec.children) == [1, 2, 3]

        vec_item = debugger.variable_manager.get_variable(
            "*((({}*){}) + 2)".format(
                vec.type.child_type.name,
                vec.data_address))

        assert vec_item.value == "3"
        assert vec.get_index_by_address(vec_item.address) == 2

        assert vec.data_address != vec.address

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_values_cb)


def test_update_variable(debugger):
    def test_update_variable_cb():
        a = debugger.variable_manager.get_variable("a")
        a.value = "8"

        assert debugger.variable_manager.get_variable("a").value == "8"

        d = debugger.variable_manager.get_variable("d")
        d.value = "hi"

        assert debugger.variable_manager.get_variable("d").value == "hi"

        vec = debugger.variable_manager.get_variable("vec")
        vec.count = vec.max_size
        debugger.variable_manager.get_vector_items(vec)
        vec.children[0].value = "10"

        vec = debugger.variable_manager.get_variable("vec")
        vec.count = vec.max_size
        debugger.variable_manager.get_vector_items(vec)
        assert vec.children[0].value == "10"

    setup_debugger(debugger, TEST_FILE, TEST_LINE,
                   test_update_variable_cb)


def test_get_memory(debugger):
    def test_get_memory_cb():
        var = debugger.variable_manager.get_variable("a")

        assert [5, 0, 0, 0] == debugger.variable_manager.get_memory(
            var.address, var.type.size)
        assert len(debugger.variable_manager.get_memory(
            var.address, 128)) == 128

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_get_memory_cb)
