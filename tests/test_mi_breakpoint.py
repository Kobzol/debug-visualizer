# -*- coding: utf-8 -*-

import os

from tests.conftest import TEST_SRC_DIR


def test_bp_add(debugger):
    src_file = "src/test_breakpoint_basic.cpp"
    line = 5

    debugger.load_binary(os.path.join(TEST_SRC_DIR, "test_breakpoint_basic"))
    assert debugger.breakpoint_manager.add_breakpoint(src_file, line)
    assert not debugger.breakpoint_manager.add_breakpoint(src_file, 100)
    assert not debugger.breakpoint_manager.add_breakpoint("", line)

    debugger.breakpoint_manager.add_breakpoint(src_file, 1)

    assert len(debugger.breakpoint_manager.get_breakpoints()) == 2


def test_bp_remove(debugger):
    src_file = "src/test_breakpoint_basic.cpp"
    line = 5

    debugger.load_binary(os.path.join(TEST_SRC_DIR, "test_breakpoint_basic"))
    debugger.breakpoint_manager.add_breakpoint(src_file, line)

    assert debugger.breakpoint_manager.remove_breakpoint(src_file, line)
    assert len(debugger.breakpoint_manager.get_breakpoints()) == 0
