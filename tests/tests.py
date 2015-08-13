# -*- coding: utf-8 -*-

import unittest
import socket
import sys
import time
sys.path.append("../debugger")

import debug_server
import debug_command
import debug_launcher
import debug_client

class BasicTest(unittest.TestCase):
	pass

class ServerTest(unittest.TestCase):
	def setUp(self):
		self.port = 9994
		self.server = debug_server.DebugServer(self.port, None)
		self.server.start()
		
		assert self.server.is_running()
		
		self.client = self.connect_client(self.port)
	
	def tearDown(self):
		self.server.stop()
		assert not self.server.is_running()
		
		self.client.disconnect()
		assert not self.client.is_connected()
		
	def test_loopback(self):
		self.client.cmd_loopback(self.check_loopback_response)
	
	def check_loopback_response(self, response):
		assert response == "ok"
	
	def connect_client(self, port):
		client = debug_client.DebugClient(("localhost", port))
		client.connect()
		
		assert client.is_connected()
		
		return client

if __name__ == '__main__':
    unittest.main()