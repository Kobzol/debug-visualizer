import os

FRAME_FILE = "src/test_frame.cpp"
FRAME_LINE = 3


def prepare_frame_program(debugger):
    debugger.load_binary("src/test_frame")
    debugger.breakpoint_manager.add_breakpoint(FRAME_FILE, FRAME_LINE)
    debugger.launch()
    debugger.wait_for_stop()


def test_frame_list(debugger):
    prepare_frame_program(debugger)

    assert len(debugger.thread_manager.get_frames()) == 2


def test_frame_properties(debugger):
    prepare_frame_program(debugger)

    frame = debugger.thread_manager.get_current_frame()

    assert frame.file == os.path.abspath(FRAME_FILE)
    assert frame.line == FRAME_LINE
    assert frame.func == "test"
    assert frame.level == 0


def test_frame_select(debugger):
    prepare_frame_program(debugger)

    assert debugger.thread_manager.change_frame(1)

    frame = debugger.thread_manager.get_current_frame()

    assert frame.func == "main"
