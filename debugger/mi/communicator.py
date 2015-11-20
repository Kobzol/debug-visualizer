# -*- coding: utf-8 -*-

import re
import select
import subprocess
import threading

from enum import Enum

from util import RepeatTimer


class ResultType(Enum):
    Success = 0
    Error = 1
    Exit = 2


class CommandResult(object):
    result_map = {
        "done": ResultType.Success,
        "running": ResultType.Success,
        "error": ResultType.Error,
        "exit": ResultType.Exit
    }

    @staticmethod
    def parse(response):
        match = re.match("^(\d)+", response)
        token = None

        if match:
            digits = match.group(0)
            response = response[len(digits):]
            token = int(digits)

        assert response[0] == Communicator.RESPONSE_START

        data = response[1:]

        if data in CommandResult.result_map:
            result_type = CommandResult.result_map[data]
            return CommandResult(result_type, token)
        else:
            raise Exception("No result found for type: " + data)

    def __init__(self, result_type, token=None, data=""):
        """
        @type result_type: ResultType
        @type token: int
        """
        self.result_type = result_type
        self.token = token
        self.data = data

    def is_success(self):
        return self.result_type == ResultType.Success

    def __repr__(self):
        return "[CMD_RESULT: {0} ({1}): {2}]".format(self.result_type, self.token, self.data)


class OutputType(Enum):
    CommandResult = 1
    AsyncExec = 2
    AsyncNotify = 3
    Separator = 4
    Unknown = 5


class OutputMessage(object):
    def __init__(self, type, data=None):
        """
        @type type: OutputType
        """
        self.type = type
        self.data = data

    def __repr__(self):
        return "[MSG: {0}, {1}]".format(self.type, self.data)


class Communicator(object):
    GROUP_SEPARATOR = "(gdb)"
    RESPONSE_START = "^"
    EXEC_ASYNC_START = "*"
    NOTIFY_ASYNC_START = "="

    def __init__(self):
        self.process = None
        self.io_lock = threading.RLock()

        self.token = 0

        self.read_timer = None

    def start_gdb(self):
        if self.process is not None:
            self.kill()

        if self.read_timer is not None:
            self.read_timer.stop()

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

        self.send("-gdb-set mi-async on")
        self.send("set non-stop on")

        self.read_timer = RepeatTimer(0.1, self._read_thread)
        self.read_timer.start()

        #fl = fcntl.fcntl(self.process.stdout, fcntl.F_GETFL)
        #fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def send(self, command):
        self.io_lock.acquire()
        response = ""

        token = self.token
        self.token += 1

        try:
            self.process.stdin.write(str(token) + command + "\n")
            self.process.stdin.flush()

            while True:
                output = self._parse_output(self._readline(True))
                if output.type == OutputType.CommandResult and output.data.token == token:
                    response = output.data
                elif output.type == OutputType.Separator:
                    break
                else:
                    self._handle_output(output)

        except IOError as e:
            print(e)

        self.io_lock.release()

        return response

    def finish(self):
        self.send("-gdb-exit")
        self.process.wait()
        self._reset()

    def kill(self):
        self.process.kill()
        self._reset()

    def _timer_read_output(self):
        self.io_lock.acquire()

        output = self._parse_output(self._readline(False))
        self._handle_output(output)

        self.io_lock.release()

    def _reset(self):
        self.process = None

        if self.read_timer is not None:
            self.read_timer.stop()
        self.read_timer = None

    def _handle_output(self, output):
        if output.type == OutputType.AsyncExec:
            pass
        elif output.type == OutputType.AsyncNotify:
            pass

    def _readline(self, block=False):
        self.io_lock.acquire()

        process = self.process
        input = ""

        try:
            if not block:
                if select.select([process.stdout], [], [], 0.05):
                    input = process.stdout.readline()
            else:
                input = process.stdout.readline()
        except IOError as e:
            print(e)

        self.io_lock.release()

        print(input)
        return input.strip()

    def _read_thread(self):
        pass

    def _skip_to_separator(self):
        data = ""

        while data != Communicator.GROUP_SEPARATOR:
            data = self._readline(True)

    def _parse_output(self, response):
        if response == Communicator.GROUP_SEPARATOR:
            return OutputMessage(OutputType.Separator)
        elif response[0].isdigit() or response[0] == Communicator.RESPONSE_START:
            return OutputMessage(OutputType.CommandResult, CommandResult.parse(response))
        elif response[0] == Communicator.EXEC_ASYNC_START:
            return OutputMessage(OutputType.AsyncExec, response)
        elif response[0] == Communicator.NOTIFY_ASYNC_START:
            return OutputMessage(OutputType.AsyncNotify, response)
        else:
            return OutputMessage(OutputType.Unknown)
