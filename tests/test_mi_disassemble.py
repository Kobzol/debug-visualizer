# -*- coding: utf-8 -*-

"""
This test is made towards a specific version of GDB and operating system
(i686), so it may not work elsewhere.
"""

SRC_FILE = "src/test_disassemble.cpp"


def prepare_program(debugger, line=None):
    debugger.load_binary("src/test_disassemble")

    if line:
        debugger.breakpoint_manager.add_breakpoint(SRC_FILE, line)

    debugger.launch()

    if line:
        debugger.wait_for_stop()


def test_address_invalid_file(debugger):
    prepare_program(debugger, 3)

    assert debugger.file_manager.get_line_address("x.cpp", 0) is None


def test_address_invalid_line(debugger):
    prepare_program(debugger, 3)

    assert debugger.file_manager.get_line_address(SRC_FILE, 100) is None


def test_address_no_code(debugger):
    prepare_program(debugger, 3)

    assert debugger.file_manager.get_line_address(SRC_FILE, 5) is None


def test_address_with_code(debugger):
    prepare_program(debugger, 3)

    assert debugger.file_manager.get_line_address(SRC_FILE, 3) == (
        "0x8048471", "0x8048478"
    )


def test_disassemble(debugger):
    prepare_program(debugger, 3)

    disas = debugger.file_manager.disassemble(SRC_FILE, 3)

    assert len(disas) == 6

    decl_ds = disas[1]

    assert decl_ds["line"] == 3
    assert len(decl_ds["instructions"]) == 1
    assert decl_ds["instructions"][0] == "movl   $0x5,-0x4(%ebp)"

    assign_ds = disas[2]

    assert assign_ds["line"] == 4
    assert len(assign_ds["instructions"]) == 1
    assert assign_ds["instructions"][0] == "addl   $0xa,-0x4(%ebp)"
