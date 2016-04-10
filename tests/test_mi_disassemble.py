# -*- coding: utf-8 -*-

"""
This test is made towards a specific version of GDB and operating system
(i686), so it may not work elsewhere.
"""

from tests.conftest import setup_debugger

TEST_FILE = "test_disassemble"
SRC_FILE = "src/{}.cpp".format(TEST_FILE)


def generate_instructions(instruction, reg32bit, reg64bit):
    return (instruction.format(reg32bit),
            instruction.format(reg64bit))


def test_address_invalid_file(debugger):
    def test_address_invalid_file_cb():
        assert debugger.file_manager.get_line_address("x.cpp", 0) is None

    setup_debugger(debugger, TEST_FILE, 3, test_address_invalid_file_cb)


def test_address_invalid_line(debugger):
    def test_address_invalid_line_cb():
        assert debugger.file_manager.get_line_address(SRC_FILE, 100) is None

    setup_debugger(debugger, TEST_FILE, 3, test_address_invalid_line_cb)


def test_address_no_code(debugger):
    def test_address_no_code_cb():
        assert debugger.file_manager.get_line_address(SRC_FILE, 5) is None

    setup_debugger(debugger, TEST_FILE, 3, test_address_no_code_cb)


def test_address_with_code(debugger):
    def test_address_with_code_cb():
        line_address = debugger.file_manager.get_line_address(SRC_FILE, 3)
        assert isinstance(line_address, tuple)
        assert len(line_address) == 2
        assert int(line_address[0], 16) < int(line_address[1], 16)

    setup_debugger(debugger, TEST_FILE, 3, test_address_with_code_cb)


def test_disassemble(debugger):
    def test_disassemble_cb():
        disas = debugger.file_manager.disassemble(SRC_FILE, 3)

        assert len(disas) == 6

        decl_ds = disas[1]

        assert decl_ds["line"] == 3
        assert len(decl_ds["instructions"]) == 1
        assert decl_ds["instructions"][0] in (
            generate_instructions("movl   $0x5,-0x4(%{})", "ebp", "rbp"))

        assign_ds = disas[2]

        assert assign_ds["line"] == 4
        assert len(assign_ds["instructions"]) == 1
        assert assign_ds["instructions"][0] in (
            generate_instructions("addl   $0xa,-0x4(%{})", "ebp", "rbp"))

    setup_debugger(debugger, TEST_FILE, 3, test_disassemble_cb)
