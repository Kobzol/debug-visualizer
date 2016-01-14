import os


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

    assert debugger.file_manager.get_line_address(SRC_FILE, 3) == ("0x8048471", "0x8048478")
