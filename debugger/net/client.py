# -*- coding: utf-8 -*-

import time
import threading
import select
import socket
import sys

from net.command import Command, CommandType


class Client(object):
    def __init__(self, address, async=False):
        self.address = address
        self.async = async

        self.connected = False
        self.socket = None

        self.listening = False
        self.receive_thread = None

        self.waiting_messages = {}
        self.command_lock = threading.Lock()

    def is_connected(self):
        return self.connected

    def connect(self):
        if self.is_connected():
            return

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.connect(self.address)
        except:
            return False

        self.socket = sock
        self.connected = True

        if self.async:
            self.receive_thread = threading.Thread(
                target=self.receive_thread_fn)
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

    def disconnect_async(self):
        if not self.is_connected():
            return

        self.receive_thread = None
        self.listening = False

        if self.socket:
            self.socket.close()
            self.socket = None

        self.connected = False

    def is_data_available(self, timeout=0.1):
        return len(select.select([self.socket], [], [], timeout)[0]) != 0

    def receive_thread_fn(self):
        while self.listening:
            if self.is_data_available(0.1):
                try:
                    command = Command.receive(self.socket)
                    self.handle_command(command)
                except:
                    self.disconnect_async()

    def handle_command(self, command):
        if command.type == CommandType.Result:
            query_id = command.data["query_id"]
            callback = self.waiting_messages.pop(query_id, None)

            if callback:
                if "error" in command.data:
                    callback(True, command.data["error"])

                    print("ERROR CLIENT: " + str(command.data["error"]))
                    sys.stdout.flush()
                elif "result" in command.data:
                    callback(False, command.data["result"])

    def send(self, command, callback=None):
        if self.socket:
            self.waiting_messages[command.id] = callback
            command.send(self.socket)

    def exec_command(self, properties, args=None, callback=None):
        data = {"properties": properties}

        if args is not None:
            data["arguments"] = args

        cmd = Command(CommandType.Execute, data)

        self.command_lock.acquire()
        self.send(cmd, callback)

        result = None

        if not self.async:
            result = Command.receive(self.socket)

        self.command_lock.release()

        return result.data["result"]

    def stop_server(self):
        self.send(Command(CommandType.StopServer))

    def cmd_load_binary(self, binary_path, callback=None):
        return self.exec_command(["load_binary"], binary_path, callback)

    def cmd_get_location(self, callback=None):
        return self.exec_command(["file_manager", "get_current_location"],
                                 None, callback)

    def cmd_get_main_file(self, callback=None):
        return self.exec_command(["file_manager", "get_main_source_file"],
                                 None, callback)

    def cmd_get_debugger_state(self, callback=None):
        return self.exec_command(["get_state"], None, callback)
