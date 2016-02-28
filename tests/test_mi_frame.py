# -*- coding: utf-8 -*-

import os

from tests.conftest import setup_debugger

TEST_FILE = "test_frame"
TEST_LINE = 6


def test_frame_list(debugger):
    def test_frame_list_cb():
        assert len(debugger.thread_manager.get_frames()) == 2

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_frame_list_cb)


def test_frame_properties(debugger):
    def test_frame_properties_cb():
        frame = debugger.thread_manager.get_current_frame(False)

        assert frame.file == os.path.abspath("src/{}.cpp".format(TEST_FILE))
        assert frame.line == TEST_LINE
        assert frame.func == "test"
        assert frame.level == 0
        assert len(frame.variables) == 0

    setup_debugger(debugger, TEST_FILE, TEST_LINE,
                   test_frame_properties_cb)


def test_frame_select(debugger):
    def test_frame_select_cb():
        assert debugger.thread_manager.change_frame(1)

        frame = debugger.thread_manager.get_current_frame(False)

        assert frame.func == "main"

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_frame_select_cb)


def test_frame_locals(debugger):
    def test_frame_locals_cb():
        frame = debugger.thread_manager.get_current_frame(True)

        assert len(frame.variables) == 4

        var_names = [var.name for var in frame.variables]
        assert set(var_names) == {"a", "b", "c", "d"}

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_frame_locals_cb)
