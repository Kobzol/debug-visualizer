# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015-2016 Jakub Beranek
#
#    This file is part of Devi.
#
#    Devi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Devi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
#


import select
import socket
import threading
import traceback

from command import Command, CommandType
from debugger.util import Dispatcher


class Server(object):
    """
    TCP server that dispatches commands to debugger.

    Can handle only one client at a time.
    """
    def __init__(self, port, debugger):
        """
        @type port: int
        @type debugger: debugger
        """
        self.address = ("localhost", port)
        self.debugger = debugger
        self.running = False
        self.connected_client = None
        self.server = None
        self.server_thread = None

    def is_running(self):
        """
        Checks that the server is listening.
        @rtype: bool
        """
        return self.running

    def is_client_connected(self):
        """
        Checks that a client is connected.
        @rtype: bool
        """
        return self.connected_client is not None

    def start(self):
        """
        Starts the server (noop if the server is already started).
        """
        if not self.is_running():
            self._create_socket()
            self.server_thread = threading.Thread(
                target=self.run_server_thread)
            self.running = True
            self.server_thread.start()

    def stop(self):
        """
        Stop the server (noop if the server is not running).
        """
        if self.is_running():
            self.running = False
            self.server_thread.join()
            self.server.close()

    def _create_socket(self):
        """
        Creates a TCP socket.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server.bind(self.address)
        self.server.listen(1)

    def is_data_available(self, fd, timeout=0.1):
        """
        Checks whether data is available for reading on the given file
        descriptor.
        @type fd: file descriptor
        @type timeout: float
        @rtype: bool
        """
        return len(select.select([fd], [], [], timeout)[0]) != 0

    def run_server_thread(self):
        """
        Loop that is run by the server thread.
        """
        while self.is_running():
            try:
                if (self.is_data_available(self.server, 0.1) and
                        not self.is_client_connected()):
                    client, address = self.server.accept()
                    self.handle_client(client, address)
            except:
                traceback.print_exc()

    def handle_command(self, command):
        """
        Handles an incoming command from the client.
        @type command: net.Command
        """
        if command.type == CommandType.Loopback:
            self.send_result(command, "ok")
        elif command.type == CommandType.StopServer:
            self.server.close()
            self.running = False
        elif command.type == CommandType.Execute:
            arguments = command.data["arguments"] if "arguments"\
                                                     in command.data else None
            properties = command.data["properties"]

            try:
                result = Dispatcher.dispatch(self.debugger, properties,
                                             arguments)
                self.send_result(command, result)
            except:
                traceback.print_exc()
                self.send_result_error(command, traceback.format_exc())

    def handle_client(self, client, address):
        """
        Handles an incoming client.
        @type client: socket
        @type address: (str, int)
        """
        self.connected_client = client

        try:
            while self.is_running():
                if self.is_data_available(client, 0.1):
                    self.handle_command(Command.receive(client))
        except:
            traceback.print_exc()
        finally:
            self.connected_client = None

    def send_result(self, command, result):
        """
        Sends result of the given command to the client.
        @type command: Command
        @type result: any
        """
        try:
            command.send_result(self.connected_client, result)
        except:
            traceback.print_exc()

    def send_result_error(self, command, error):
        """
        Sends an error result of the given command to the client.
        @type command: Command
        @type error: any
        """
        try:
            command.send_result_error(self.connected_client, error)
        except:
            traceback.print_exc()
