# -*- coding: utf-8 -*-

from debugger.enums import ProcessState

THREAD_LINE = 22


def prepare_debugger(debugger, on_state_change=None):
    debugger.load_binary("src/test_thread")
    debugger.breakpoint_manager.add_breakpoint("src/test_thread.cpp",
                                               THREAD_LINE)
    debugger.launch()
    debugger.wait_for_stop()

    if on_state_change:
        def on_stop(state, data):
            if state == ProcessState.Stopped:
                on_state_change()
        debugger.on_process_state_changed.subscribe(on_stop)


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

    prepare_debugger(debugger, test_thread_info_cb)


def test_thread_switch(debugger):
    def test_thread_switch_cb():
        selected = select_other_thread(debugger)

        thread_info = debugger.thread_manager.get_thread_info()
        assert thread_info.selected_thread.id == selected.id

    prepare_debugger(debugger, test_thread_switch_cb)


def test_thread_location(debugger):
    def test_thread_location_cb():
        assert debugger.file_manager.get_current_location()[1] in range(27, 35)

        select_other_thread(debugger)

        assert debugger.file_manager.get_current_location()[1] in range(9, 18)

    prepare_debugger(debugger, test_thread_location_cb)


def test_thread_frame(debugger):
    def test_thread_frame_cb():
        thread_info = debugger.thread_manager.get_thread_info()
        frame = debugger.thread_manager.get_current_frame()

        assert thread_info.selected_thread.frame.func == frame.func
        assert "b" in [var.name for var in frame.variables]

        select_other_thread(debugger)

        frame = debugger.thread_manager.get_current_frame()
        assert "a" in [var.name
                       for var
                       in frame.variables]

    prepare_debugger(debugger, test_thread_frame_cb)
