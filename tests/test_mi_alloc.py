import copy
import sys

FRAME_FILE = "src/test_alloc.cpp"
FRAME_LINE = 8


def prepare_frame_program(debugger):
    debugger.load_binary("src/test_alloc")
    debugger.breakpoint_manager.add_breakpoint(FRAME_FILE, FRAME_LINE)
    debugger.launch()
    debugger.wait_for_stop()


def test_alloc(debugger):
    heap = []
    debugger.heap_manager.on_heap_change.subscribe(lambda new_heap:
                                                   heap.append(
                                                       copy.copy(new_heap)))

    prepare_frame_program(debugger)

    assert len(heap[0]) == 1
    assert heap[1][1].size == 1024
    assert len(heap[2]) == 1
