# -*- coding: utf-8 -*-

import os
import time

from tests.conftest import AsyncState, setup_debugger

TEST_FILE = "test_execution"


def make_location(line):
    return (os.path.abspath("src/{}.cpp".format(TEST_FILE)), line)


def test_step_over(debugger):
    state = AsyncState()

    def test_step_over_cb():
        if state.state == 0:
            state.inc()
            debugger.exec_step_over()
        else:
            assert debugger.file_manager.get_current_location() ==\
                make_location(12)
            debugger.quit_program()

    setup_debugger(debugger, TEST_FILE, 11, test_step_over_cb, cont=False)


def test_step_in(debugger):
    state = AsyncState()

    def test_step_in_cb():
        if state.state == 0:
            state.inc()
            debugger.exec_step_in()
        else:
            assert debugger.file_manager.get_current_location() ==\
                make_location(5)
            debugger.quit_program()

    setup_debugger(debugger, TEST_FILE, 11, test_step_in_cb, cont=False)


def test_step_out(debugger):
    state = AsyncState()

    def test_step_out_cb():
        if state.state == 0:
            state.inc()
            debugger.exec_step_out()
        else:
            location = debugger.file_manager.get_current_location()
            assert location[0] == make_location(11)[0]
            assert location[1] in (11, 12)
            debugger.quit_program()

    setup_debugger(debugger, TEST_FILE, 5, test_step_out_cb, cont=False)


def test_continue(debugger):
    state = AsyncState()

    def test_continue_cb():
        if state.state == 0:
            state.inc()
            debugger.exec_continue()
        else:
            assert debugger.file_manager.get_current_location() ==\
                make_location(13)
            debugger.quit_program()

    setup_debugger(debugger, TEST_FILE, (11, 13), test_continue_cb,
                   cont=False)


def test_pause(debugger):
    def test_pause_cb():
        debugger.quit_program()

    setup_debugger(debugger, TEST_FILE, [], test_pause_cb,
                   cont=False, wait=False)

    time.sleep(0.5)
    debugger.exec_pause()


def test_stop(debugger):
    setup_debugger(debugger, TEST_FILE, [], None,
                   cont=False, wait=False)

    time.sleep(0.5)
    debugger.quit_program()
