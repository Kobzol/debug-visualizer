# -*- coding: utf-8 -*-

import socket
import threading
import select
import json
import sys

from debugcommand import CommandType, DebugCommand

class DebugServer(object):
    def __init__(self, port):
        self.address = ("localhost", port)
        self.running = False
        self.connected_client = None
        
    def is_running(self):
        return self.running

    def is_client_connected(self):
        return self.connected_client is not None

    def start(self):
        if not self.is_running():
            self.create_socket()
            self.server_thread = threading.Thread(target=self.run_server_thread)
            self.running = True
            self.server_thread.start()
    
    def stop(self):
        if self.is_running():
            self.running = False
            self.server_thread.join()
            self.server.close()
    
    def create_socket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)
        self.server.listen(1)
    
    def is_data_available(self, fd, timeout = 0.2):
        return len(select.select([fd], [], [], timeout)[0]) != 0
    
    def run_server_thread(self):
        while self.is_running():
            try:
                if self.is_data_available(self.server, 0.2) and not self.is_client_connected():
                    client, address = self.server.accept()
                    self.handle_client(client, address)
            except:
                pass
    
    def handle_command(self, command):
        if command.type == CommandType.LoopbackCommand:
            self.send_command(command)
    
    def handle_client(self, client, address):
        self.connected_client = client
        
        try:
            while self.is_running():
                if self.is_data_available(client, 0.2):
                    self.handle_command(DebugCommand.receive(client))
        except:
            pass
        finally:
            self.client_connected = None
    
    def send_command(self, command):
        if self.is_client_connected():
            command.send(self.connected_client)