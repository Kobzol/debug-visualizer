# -*- coding: utf-8 -*-

import unittest
import sys
import os
import time
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
        self.debugger.load_binary("../debugger/test")

        self.assertEqual(self.debugger.file_manager.get_main_source_file(), os.path.abspath("../debugger/test.cpp"))
        self.assertTrue(self.debugger.get_state().is_set(DebuggerState.BinaryLoaded))


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

    def test_communication(self):
        state = self.client.cmd_get_debugger_state()#.is_set(DebuggerState.Started))
        a = 5

if __name__ == '__main__':
    unittest.main()