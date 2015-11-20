# -*- coding: utf-8 -*-

import os
import subprocess

import fcntl

import select
import threading

from enum import Enum


class ResultType(Enum):
    Success = 0
    Error = 1
    Exit = 2


class CommandResult(object):
    result_map = {
        "done": ResultType.Success,
        "error": ResultType.Error,
        "exit": ResultType.Exit
    }

    @staticmethod
    def parse_result_type(data):
        data = data[1:]

        if data in CommandResult.result_map:
            return CommandResult.result_map[data]
        else:
            raise Exception("No result found for type: " + data)

    def __init__(self, result_type, data=""):
        self.result_type = result_type
        self.data = data

    def is_success(self):
        return self.result_type == ResultType.Success

    def __repr__(self):
        return "[{0}: {1}]".format(self.result_type, self.data)


class Communicator(object):
    GROUP_SEPARATOR = "(gdb)"
    RESPONSE_START = "^"

    def __init__(self):
        self.process = None
        self.io_lock = threading.RLock()
        self.token = 0
        self.pty = None

    def start_gdb(self):
        if self.process is not None:
            self.kill()

        self.token = 0

        self.process = subprocess.Popen(
            bufsize=0,
            args=["gdb",
                    "--return-child-result",
                    "--quiet",
                    "--nx",  # ignore .gdbinit
                    '--nw',  # inhibit window interface
                    '--interpreter=mi2',  # use GDB/MI v2
                  ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            close_fds=True
        )

        self._skip_to_separator()

        #self.send("-gdb-set mi-async on")

        #fl = fcntl.fcntl(self.process.stdout, fcntl.F_GETFL)
        #fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def readline(self, block=False):
        self.io_lock.acquire()

        process = self.process
        input = ""

        try:
            if block:
                if select.select([process.stdout], [], [], 0.1):
                    input = process.stdout.readline()
            else:
                input = process.stdout.readline()
        except IOError as e:
            print(e)

        self.io_lock.release()

        print(input)
        return input.strip()

    def send(self, command):
        self.io_lock.acquire()
        response = ""

        try:
            self.process.stdin.write(command + "\n")
            response = self.readline(True)
        except IOError as e:
            print(e)

        self.io_lock.release()

        return self._parse_response(response)

    def finish(self):
        self.send("-gdb-exit")
        self.process.wait()
        self.process = None

    def kill(self):
        self.process.kill()
        self.process = None

    def prepare_inferior_tty(self):
        pid = os.getpid()
        (master, slave) = os.openpty()
        slave_node = "/proc/%d/fd/%d" % (pid, slave)

        self.send("-inferior-tty-set " + slave_node)

        return master

    def _skip_to_separator(self):
        data = ""

        while data != Communicator.GROUP_SEPARATOR:
            data = self.readline(True)

    def _parse_response(self, response):
        if response == Communicator.GROUP_SEPARATOR:
            return True
        elif response[0] == Communicator.RESPONSE_START:
            return CommandResult(CommandResult.parse_result_type(response))
        else:
            print("UNKNOWN: " + response)
