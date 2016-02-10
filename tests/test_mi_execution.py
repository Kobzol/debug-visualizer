import os

import time

EXECUTION_FILE = "src/test_execution.cpp"


def make_location(line):
    return (os.path.abspath(EXECUTION_FILE), line)


def prepare_execution_program(debugger, line=None):
    debugger.load_binary("src/test_execution")

    if line:
        debugger.breakpoint_manager.add_breakpoint(EXECUTION_FILE, line)

    debugger.launch()

    if line:
        debugger.wait_for_stop()


def test_step_over(debugger):
    prepare_execution_program(debugger, 11)

    debugger.exec_step_over()
    debugger.wait_for_stop()

    assert debugger.file_manager.get_current_location() == make_location(12)


def test_step_in(debugger):
    prepare_execution_program(debugger, 11)

    debugger.exec_step_in()
    debugger.wait_for_stop()

    assert debugger.file_manager.get_current_location() == make_location(5)


def test_step_out(debugger):
    prepare_execution_program(debugger, 5)

    debugger.exec_step_out()
    debugger.wait_for_stop()

    location = debugger.file_manager.get_current_location()
    assert location[0] == make_location(11)[0]
    assert location[1] in (11, 12)


def test_continue(debugger):
    prepare_execution_program(debugger, 11)

    debugger.breakpoint_manager.add_breakpoint(EXECUTION_FILE, 13)

    debugger.exec_continue()
    debugger.wait_for_stop()

    assert debugger.file_manager.get_current_location() == make_location(13)


def test_pause(debugger):
    prepare_execution_program(debugger)

    time.sleep(0.5)
    debugger.exec_pause()
    debugger.wait_for_stop()


def test_stop(debugger):
    prepare_execution_program(debugger)

    time.sleep(0.5)
    debugger.quit_program()
    debugger.wait_for_stop()
