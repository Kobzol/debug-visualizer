# -*- coding: utf-8 -*-

import os

from enums import DebuggerState
from conftest import TEST_SRC_DIR


def test_stop_no_launch(debugger):
    debugger.load_binary(os.path.join(TEST_SRC_DIR, "test_breakpoint_basic"))
    debugger.quit_program()


def test_load_file(debugger):
    assert debugger.load_binary(os.path.join(TEST_SRC_DIR,
                                             "test_breakpoint_basic"))
    assert debugger.state.is_set(DebuggerState.BinaryLoaded)
    assert debugger.file_manager.get_main_source_file() == os.path.join(
        TEST_SRC_DIR, "test_breakpoint_basic.cpp")
