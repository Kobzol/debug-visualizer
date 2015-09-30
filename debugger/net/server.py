# -*- coding: utf-8 -*-

import socket
import threading
import select
import json
import sys
import traceback

from net.command import Command, CommandType
from dispatcher import Dispatcher


class Server(object):
    def __init__(self, port, debugger):
        self.address = ("localhost", port)
        self.debugger = debugger
        self.running = False
        self.connected_client = None
        self.server = None
        self.server_thread = None
        
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
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server.bind(self.address)
        self.server.listen(1)
    
    def is_data_available(self, fd, timeout=0.1):
        return len(select.select([fd], [], [], timeout)[0]) != 0
    
    def run_server_thread(self):
        while self.is_running():
            try:
                if self.is_data_available(self.server, 0.1) and not self.is_client_connected():
                    client, address = self.server.accept()
                    self.handle_client(client, address)
            except Exception as e:
                print(e)
                sys.stdout.flush()
    
    def handle_command(self, command):
        if command.type == CommandType.Loopback:
            self.send_result(command, "ok")
        elif command.type == CommandType.StopServer:
            self.server.close()
            self.running = False
        elif command.type == CommandType.Execute:           
            arguments = command.data["arguments"] if "arguments" in command.data else None
            properties = command.data["properties"]

            try:
                result = Dispatcher.dispatch(self.debugger, properties, arguments)
                self.send_result(command, result)
            except:
                print(traceback.format_exc())
                sys.stdout.flush()
                self.send_result_error(command, traceback.format_exc())
    
    def handle_client(self, client, address):
        self.connected_client = client
        
        try:
            while self.is_running():
                if self.is_data_available(client, 0.1):
                    self.handle_command(Command.receive(client))
        except Exception as e:
            print(e)
        finally:
            self.connected_client = None
            
    def send_result(self, command, result):
        try:
            command.send_result(self.connected_client, result)
        except:
            print(traceback.format_exc())
            sys.stdout.flush()
        
    def send_result_error(self, command, error):
        try:
            command.send_result_error(self.connected_client, error)
        except:
            print(traceback.format_exc())
            sys.stdout.flush()
