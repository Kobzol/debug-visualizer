# -*- coding: utf-8 -*-

import socket
import threading
import select
import json
import sys
import traceback

from net.command import Command, CommandType

class Server(object):
    def __init__(self, port, debugger):
        self.address = ("localhost", port)
        self.debugger = debugger
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
            except Exception as e:
                print(e)
    
    def handle_command(self, command):       
        if command.type == CommandType.Loopback:
            self.send_result(command, "ok")
        elif command.type == CommandType.Execute:           
            target_prop = self.debugger
            
            result = None
            
            try:
                for prop in command.data["properties"]: 
                    target_prop = getattr(target_prop, prop)
            
                if "arguments" in command.data:
                    result = target_prop(command.data["arguments"])
                else:
                    result = target_prop()
                    
                self.send_result(command, result)
            except:
                self.send_result_error(command, traceback.format_exc())
    
    def handle_client(self, client, address):
        self.connected_client = client
        
        try:
            while self.is_running():
                if self.is_data_available(client, 0.2):
                    self.handle_command(Command.receive(client))
        except Exception as e:
            print(e)
        finally:
            self.client_connected = None
            
    def send_result(self, command, result):
        command.send_result(self.connected_client, result)
        
    def send_result_error(self, command, error):
        command.send_result_error(self.connected_client, error)