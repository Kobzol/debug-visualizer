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


class BasicTest(unittest.TestCase):
    def setUp(self):
        self.debugger = LldbDebugger()

    def test_binary_load(self):
        self.debugger.load_binary("src/test_empty")

        self.assertEqual(self.debugger.file_manager.get_main_source_file(), os.path.abspath("src/test_empty.cpp"))
        self.assertTrue(self.debugger.get_state().is_set(DebuggerState.BinaryLoaded))

    def test_breakpoint_basic(self):
        src_file = os.path.abspath("test_breakpoint_basic.cpp")
        line_number = 3

        self.debugger.load_binary("src/test_breakpoint_basic")

        self.debugger.breakpoint_manager.add_breakpoint(src_file, line_number)
        self.debugger.on_process_state_changed.subscribe(lambda state, event_data: self._async_bp_basic(state, src_file, line_number))
        self.debugger.launch()

        time.sleep(2)

    def _async_bp_basic(self, state, file, line_number):
        if state == ProcessState.Stopped:
            location = self.debugger.file_manager.get_current_location()

            if location[0] is not None:
                self.assertEqual(location, (file, line_number))


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