# -*- coding: utf-8 -*-

import socket
import threading
import select
import sys
import time

from net.command import Command, CommandType

class Client(object):
    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.socket = None
        
        self.listening = False
        self.receive_thread = None
        
        self.waiting_messages = {}
        
    def is_connected(self):
        return self.connected
    
    def connect(self):
        if self.is_connected():
            return
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.address)
        except:
            return False
        
        self.socket = sock
        self.connected = True
        
        self.receive_thread = threading.Thread(target=self.receive_thread_fn)
        self.listening = True
        self.receive_thread.start()
        
        return True
    
    def connect_repeat(self, timeout=5):
        start_time = time.clock()
        
        while not self.connect() and time.clock() < start_time + timeout:
            time.sleep(0.1)
            
        return self.is_connected()
        
    def disconnect(self):
        if not self.is_connected():
            return
        
        if self.receive_thread:
            self.listening = False
            self.receive_thread.join()
            self.receive_thread = None
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        self.connected = False
    
    def is_data_available(self, timeout = 0.2):
        return len(select.select([self.socket], [], [], timeout)[0]) != 0
    
    def receive_thread_fn(self):
        while self.listening:
            if self.is_data_available(0.2):
                command = Command.receive(self.socket)
                self.handle_command(command)
    
    def handle_command(self, command):
        if command.type == CommandType.Result:
            query_id = command.data["query_id"]
            callback = self.waiting_messages.pop(query_id, None)
            
            if callback:
                callback(command.data["result"])
    
    def send(self, command, callback):
        self.waiting_messages[command.id] = callback
        command.send(self.socket)
        
    def exec_command(self, properties, args, callback):
        data = {"properties" : properties}
        
        if args is not None:
            data["args"] = args
        
        cmd = Command(CommandType.Execute, data)
        self.send(cmd, callback)
        
    def cmd_get_location(self, callback):
        self.exec_command(["file_manager", "get_current_location"], None, callback)
        
    def cmd_loopback(self, callback):
        self.send(Command(CommandType.Loopback, {}), callback)