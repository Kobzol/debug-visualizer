# -*- coding: utf-8 -*-

"""
This test depends on particular implementation of glibc (that does not
allocate memory on it's own for the given program (src/test_alloc.cpp),
so it may not work elsewhere.
"""

import copy

from tests.conftest import setup_debugger

TEST_FILE = "test_alloc"
TEST_LINE = 8


def test_alloc(debugger):
    heap = []
    debugger.heap_manager.on_heap_change.subscribe(lambda new_heap:
                                                   heap.append(
                                                       copy.copy(new_heap)))

    def test_alloc_cb():
        assert len(heap[0]) == 1
        assert heap[0][0].size == 1024
        assert len(heap[1]) == 0

    setup_debugger(debugger, TEST_FILE, TEST_LINE, test_alloc_cb)
