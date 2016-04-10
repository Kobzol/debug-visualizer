# -*- coding: utf-8 -*-

import os
import traceback
from collections import Iterable

import pytest
import sys

from debugger.enums import ProcessState
from tests.src import compile

path = os.path.dirname(os.path.abspath(__file__))

TEST_DIR = path
TEST_SRC_DIR = os.path.join(TEST_DIR, "src")
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "debugger")

sys.path.append(SRC_DIR)
os.chdir(TEST_DIR)

from debugger.mi.mi_debugger import MiDebugger  # noqa
from debugger.mi.parser import Parser  # noqa


compile.compile_tests()


class AsyncState(object):
    def __init__(self):
        self.state = 0

    def inc(self):
        self.state += 1


@pytest.fixture(scope="function")
def debugger():
    return MiDebugger()


@pytest.fixture(scope="module")
def parser():
    return Parser()


def setup_debugger(debugger, binary, lines, on_state_change=None,
                   startup_info=None, cont=True, wait=True):
    assert debugger.load_binary("src/{}".format(binary))

    test_exception = []

    if not isinstance(lines, Iterable):
        lines = [lines]

    for line in lines:
        assert debugger.breakpoint_manager.add_breakpoint(
            "src/{}.cpp".format(binary), line)

    if on_state_change:
        def on_stop(state, data):
            if state == ProcessState.Stopped:
                try:
                    on_state_change()
                    if cont:
                        debugger.exec_continue()
                except Exception as exc:
                    test_exception.append(traceback.format_exc(exc))
                    debugger.quit_program()

        debugger.on_process_state_changed.subscribe(on_stop)

    assert debugger.launch(startup_info)

    if wait:
        debugger.wait_for_exit()

    if len(test_exception) > 0:
        pytest.fail(test_exception[0], pytrace=False)
