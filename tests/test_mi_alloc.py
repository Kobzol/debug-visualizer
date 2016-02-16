# -*- coding: utf-8 -*-

"""
This test depends on particular implementation of glibc (that does not
allocate memory on it's own for the given program (src/test_alloc.cpp),
so it may not work elsewhere.
"""

import copy
import time

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

    time.sleep(1)

    assert len(heap[0]) == 1
    assert heap[0][0].size == 1024
    assert len(heap[1]) == 0
