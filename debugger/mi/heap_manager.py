# -*- coding: utf-8 -*-

import os
import threading
import select
import traceback

import debugger
import util
from debugee import HeapBlock


class HeapManager(debugger.HeapManager):
    def __init__(self, debugger):
        """
        @type debugger: debugger.Debugger
        """
        super(HeapManager, self).__init__(debugger)
        self.heap = []
        """@type heap: list of HeapBlock"""
        self.read_thread = None
        self.alloc_path = None
        self.file = None
        self.stop_flag = threading.Event()

    def watch(self):
        """
        @rtype: str
        """
        assert self.read_thread is None

        self.stop_flag.clear()

        self.alloc_path = util.create_pipe()

        self.read_thread = threading.Thread(target=self._read_thread,
                                            args=(self.alloc_path,))
        self.read_thread.daemon = True
        self.read_thread.start()

        return self.alloc_path

    def stop(self):
        self.stop_flag.set()

        self.read_thread.join()

        try:
            os.remove(self.alloc_path)
        except:
            pass

        self.heap = []
        self.read_thread = None

    def _read_thread(self, alloc_path):
        """
        @type alloc_path: str
        """
        try:
            with os.fdopen(os.open(alloc_path, os.O_NONBLOCK | os.O_RDONLY),
                           "r", 1) as alloc_file:
                self.alloc_file = alloc_file

                while not self.stop_flag.is_set():
                    if len(select.select([alloc_file], [], [], 0.1)[0]) != 0:
                        line = alloc_file.readline()[:-1]

                        if line:
                            self._handle_message(line)
        except:
            traceback.print_exc()

    def find_block_by_address(self, addr):
        """
        @type addr: str
        @rtype: HeapBlock | None
        """
        for block in self.heap:
            if block.address == addr:
                return block

        return None

    def _handle_malloc(self, addr, size, notify=True):
        """
        @type addr: str
        @type size: str
        """
        size = int(size)
        block = HeapBlock(addr, size)
        self.heap.append(block)

        if notify:
            self.on_heap_change.notify(self.heap)

    def _handle_realloc(self, addr, new_addr, size):
        """
        @type addr: str
        @type new_addr: str
        @type size: str
        """
        self._handle_free(addr, False)
        self._handle_malloc(new_addr, size, False)

        self.on_heap_change.notify(self.heap)

    def _handle_free(self, addr, notify=True):
        """
        @type addr: str
        """
        if addr == "NULL":
            return

        block = self.find_block_by_address(addr)
        if not block:
            self.on_free_error.notify(addr)

        self.heap.remove(block)

        if notify:
            self.on_heap_change.notify(self.heap)

    def _handle_message(self, message):
        """
        @type message: str
        """
        util.Logger.debug("HEAP: {}".format(message))

        msg_parts = message.split(" ")
        action = msg_parts[0]
        args = msg_parts[1:]

        if action in ("malloc", "calloc"):
            self._handle_malloc(*args)
        elif action == "realloc":
            self._handle_realloc(*args)
        elif action == "free":
            self._handle_free(*args)
        else:
            raise Exception("Unknown allocation action: {}".format(action))
