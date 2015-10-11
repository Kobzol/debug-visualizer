# -*- coding: utf-8 -*-

import unittest
import sys
import os
import time
from lldbc.lldb_process_enums import ProcessState

sys.path.append("../debugger")

from net.server import Server
from net.client import Client
from net.helper import NetHelper
from lldbc.lldb_debugger import LldbDebugger
from debugger_state import DebuggerState


class AsyncSequence(object):
    def __init__(self, state_seq=None, loc_seq=None, com_seq=None, start_ignore=0):
        if state_seq is None:
            state_seq = []

        if loc_seq is None:
            loc_seq = []

        if com_seq is None:
            com_seq = []

        self.state_seq = state_seq
        self.loc_seq = loc_seq
        self.com_seq = com_seq

        self.index = 0
        self.start_ignore = start_ignore
        self.ignore_index = 0

    def _has_value(self, arr):
        return len(arr) > self.index and arr[self.index] is not None

    def _get_value(self, arr):
        return arr[self.index]

    def has_state(self):
        return self._has_value(self.state_seq)

    def has_location(self):
        return self._has_value(self.loc_seq)

    def has_command(self):
        return self._has_value(self.com_seq)

    def get_state(self):
        return self._get_value(self.state_seq)

    def get_location(self):
        return self._get_value(self.loc_seq)

    def get_command(self):
        return self._get_value(self.com_seq)

    def should_skip(self):
        return self.ignore_index < self.start_ignore

    def skip(self):
        self.ignore_index += 1

    def increment(self):
        self.index += 1


class BasicTest(unittest.TestCase):
    def setUp(self):
        self.debugger = LldbDebugger()

    def test_binary_load(self):
        self.debugger.load_binary("src/test_breakpoint_basic")

        self.assertEqual(self.debugger.file_manager.get_main_source_file(), os.path.abspath("src/test_breakpoint_basic.cpp"))
        self.assertTrue(self.debugger.get_state().is_set(DebuggerState.BinaryLoaded))

    def test_breakpoint_basic(self):
        src_file = "test_breakpoint_basic.cpp"
        src_abs_path = os.path.abspath("src/" + src_file)
        line_number = 3

        self.debugger.load_binary("src/test_breakpoint_basic")

        self.debugger.breakpoint_manager.add_breakpoint(src_file, line_number)

        states = [ProcessState.Stopped, ProcessState.Running, ProcessState.Exited]
        locations = [(src_abs_path, line_number)]
        commands = [lambda: self.debugger.exec_continue()]

        async_seq = AsyncSequence(states, locations, commands, 3)

        self.debugger.on_process_state_changed.subscribe(lambda state, event_data: self._async_bp_step(state, async_seq))
        self.debugger.launch()

        self.debugger.stop(False)

    def test_step_over(self):
        src_file = "test_breakpoint_basic.cpp"
        src_abs_path = os.path.abspath("src/" + src_file)
        line_number = 3

        self.debugger.load_binary("src/test_breakpoint_basic")

        self.debugger.breakpoint_manager.add_breakpoint(src_file, line_number)

        states = [ProcessState.Stopped, ProcessState.Running, ProcessState.Stopped, ProcessState.Running, ProcessState.Exited]
        locations = [(src_abs_path, line_number), None, (src_abs_path, line_number + 2)]
        commands = [lambda: self.debugger.exec_step_over(), None, lambda: self.debugger.exec_continue()]

        async_seq = AsyncSequence(states, locations, commands, 3)

        self.debugger.on_process_state_changed.subscribe(lambda state, event_data: self._async_bp_step(state, async_seq))
        self.debugger.launch()

        self.debugger.stop(False)

    def _async_bp_step(self, state, async_seq):
        if async_seq.should_skip():
            async_seq.skip()
            return

        if async_seq.has_state():
            self.assertEqual(state, async_seq.get_state())
        if async_seq.has_location():
            self.assertEqual(self.debugger.file_manager.get_current_location(), async_seq.get_location())
        if async_seq.has_command():
            async_seq.get_command()()

        async_seq.increment()


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.debugger = LldbDebugger()
        port = NetHelper.get_free_port()
        self.server = Server(port, self.debugger)
        self.server.start()

        self.assertTrue(self.server.is_running())

        self.client = Client(("localhost", port))
        self.client.connect_repeat(5)

        self.assertTrue(self.client.is_connected())

        time.sleep(0.1)

        self.assertTrue(self.server.is_client_connected())

    def tearDown(self):
        self.client.stop_server()
        self.client.disconnect()

        time.sleep(0.1)

        self.assertFalse(self.server.is_client_connected())
        self.assertFalse(self.server.is_running())
        self.assertFalse(self.client.is_connected())

    """def test_communication(self):
        state = self.client.cmd_get_debugger_state()#.is_set(DebuggerState.Started))
        a = 5"""

if __name__ == '__main__':
    unittest.main()