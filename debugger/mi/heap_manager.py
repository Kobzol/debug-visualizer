# -*- coding: utf-8 -*-

import os
import threading
import sys
import select

import util


class HeapBlock(object):
    def __init__(self, address, size):
        """
        @type address: str
        @type size: int
        """
        self.address = address
        self.size = size


class HeapManager(object):
    def __init__(self, debugger):
        """
        @type debugger: debugger.Debugger
        """
        self.heap = []
        self.read_thread = None
        self.debugger = debugger
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

        self.read_thread = threading.Thread(target=self._read_thread, args=(self.alloc_path,))
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
            with open(alloc_path, "r", buffering=1) as alloc_file:
                self.alloc_file = alloc_file

                while not self.stop_flag.is_set():
                    if len(select.select([alloc_file], [], [], 0.1)[0]) != 0:
                        line = alloc_file.readline()[:-1]

                        if line:
                            self._handle_message(line)
        except:
            pass

    def _handle_message(self, message):
        """
        @type message: str
        """
        print(message) # TODO: handle messages
        sys.stdout.flush()
