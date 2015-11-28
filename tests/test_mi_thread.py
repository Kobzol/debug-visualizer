THREAD_LINE = 22


def prepare_debugger(debugger):
    debugger.load_binary("src/test_thread")
    debugger.breakpoint_manager.add_breakpoint("src/test_thread.cpp", THREAD_LINE)
    debugger.launch()
    debugger.wait_for_stop()


def select_other_thread(debugger):
    thread_info = debugger.thread_manager.get_thread_info()
    selected = None

    for thread in thread_info.threads:
        if thread != thread_info.selected_thread:
            debugger.thread_manager.set_thread_by_index(thread.id)
            selected = thread

    return selected


def test_thread_info(debugger):
    prepare_debugger(debugger)

    thread_info = debugger.thread_manager.get_thread_info()

    assert len(thread_info.threads) == 2
    assert thread_info.selected_thread.id == 1


def test_thread_switch(debugger):
    prepare_debugger(debugger)

    selected = select_other_thread(debugger)

    assert debugger.thread_manager.get_thread_info().selected_thread.id == selected.id


def test_thread_location(debugger):
    prepare_debugger(debugger)

    assert debugger.file_manager.get_current_location()[1] == THREAD_LINE

    select_other_thread(debugger)

    assert debugger.file_manager.get_current_location()[1] in range(7, 10)


def test_thread_frame(debugger):
    prepare_debugger(debugger)

    thread_info = debugger.thread_manager.get_thread_info()

    assert thread_info.selected_thread.frame.func == debugger.thread_manager.get_current_frame().func
    assert "b" in [var.name for var in debugger.thread_manager.get_current_frame().variables]

    select_other_thread(debugger)

    assert "a" in [var.name for var in debugger.thread_manager.get_current_frame().variables]
