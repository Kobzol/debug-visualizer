# -*- coding: utf-8 -*-

from tests.conftest import setup_debugger

TEST_FILE = "test_thread"
TEST_LINE = 29


def select_other_thread(debugger):
    thread_info = debugger.thread_manager.get_thread_info()
    selected = None

    for thread in thread_info.threads:
        if thread != thread_info.selected_thread:
            debugger.thread_manager.set_thread_by_index(thread.id)
            selected = thread

    return selected


def test_thread_info(debugger):
    def test_thread_info_cb():
        thread_info = debugger.thread_manager.get_thread_info()

        assert len(thread_info.threads) == 2
        assert thread_info.selected_thread.id == 1

        debugger.quit_program()

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_thread_info_cb,
                   cont=False)


def test_thread_switch(debugger):
    def test_thread_switch_cb():
        selected = select_other_thread(debugger)

        thread_info = debugger.thread_manager.get_thread_info()
        assert thread_info.selected_thread.id == selected.id

        debugger.quit_program()

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_thread_switch_cb,
                   cont=False)


def test_thread_location(debugger):
    def test_thread_location_cb():
        assert debugger.file_manager.get_current_location()[1] in range(27, 35)

        select_other_thread(debugger)

        assert debugger.file_manager.get_current_location()[1] in range(9, 18)

        debugger.quit_program()

    setup_debugger(debugger, TEST_FILE, TEST_LINE,
                   test_thread_location_cb, cont=False)


def test_thread_frame(debugger):
    def test_thread_frame_cb():
        thread_info = debugger.thread_manager.get_thread_info()
        frame = debugger.thread_manager.get_current_frame(True)

        assert thread_info.selected_thread.frame.func == frame.func
        vars = [var.name for var in frame.variables]
        assert "thread" in vars
        assert "result" in vars

        select_other_thread(debugger)

        frame = debugger.thread_manager.get_current_frame(True)
        assert "param" in [var.name for var in frame.variables]

        debugger.quit_program()

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_thread_frame_cb,
                   cont=False)
