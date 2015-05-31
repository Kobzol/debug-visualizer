# -*- coding: utf-8 -*-

import unittest
import socket
import sys
import time
sys.path.append("../debugger")

import debugserver
import debugcommand

class BasicTest(unittest.TestCase):
	pass

class ServerTest(unittest.TestCase):
	def setUp(self):
		self.port = 9999
		self.server = debugserver.DebugServer(self.port)
		self.server.start()
		
		assert self.server.is_running()
	
	def tearDown(self):
		self.server.stop()
		assert not self.server.is_running()
		
	def test_loopback(self):
		sock = self.connect_client()
		
		cmd = debugcommand.DebugCommand(debugcommand.CommandType.LoopbackCommand, { "message" : "hello" })
		cmd.send(sock)
		
		response = debugcommand.DebugCommand.receive(sock)
		assert response.type == cmd.type
		assert response.data["message"] == cmd.data["message"]
		
	def connect_client(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(("localhost", self.port))
		time.sleep(0.5)
		assert self.server.is_client_connected()
		
		return sock

if __name__ == '__main__':
    unittest.main()
