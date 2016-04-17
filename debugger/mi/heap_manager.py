# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015-2016 Jakub Beranek
#
#    This file is part of Devi.
#
#    Devi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Devi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
#


import os
import threading
import select
import traceback

from debugger.debugee import HeapBlock
from debugger import debugger_api, util
from debugger.util import Logger


class HeapManager(debugger_api.HeapManager):
    def __init__(self, debugger):
        """
        @type debugger: debugger.Debugger
        """
        super(HeapManager, self).__init__(debugger)
        self.heap = []
        """@type heap: list of HeapBlock"""

        self.total_allocations = 0
        self.total_deallocations = 0

        self.read_thread = None
        self.alloc_path = None
        self.file = None
        self.stop_flag = threading.Event()

    def watch(self):
        """
        @rtype: str
        """
        assert self.read_thread is None

        self.total_allocations = 0
        self.total_deallocations = 0

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

    def find_block_by_address(self, addr):
        """
        @type addr: str
        @rtype: HeapBlock | None
        """
        for block in self.heap:
            if block.address == addr:
                return block

        return None

    def get_total_allocations(self):
        """
        @rtype: int
        """
        return self.total_allocations

    def get_total_deallocations(self):
        """
        @rtype: int
        """
        return self.total_deallocations

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
            Logger.debug(traceback.format_exc())

    def _handle_malloc(self, addr, size, notify=True):
        """
        @type addr: str
        @type size: str
        """
        size = int(size)
        block = HeapBlock(addr, size)
        self.heap.append(block)

        self.total_allocations += 1

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

        self.total_deallocations += 1

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

        try:
            if action in ("malloc", "calloc"):
                self._handle_malloc(*args)
            elif action == "realloc":
                self._handle_realloc(*args)
            elif action == "free":
                self._handle_free(*args)
            else:
                Logger.debug("Unknown allocation action: {}".format(action))
        except:
            Logger.debug(traceback.format_exc())
