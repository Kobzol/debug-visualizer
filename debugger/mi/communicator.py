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


import glob
import os
import re
import select
import subprocess
import threading
import traceback
import signal
from enum import Enum

import debugger.util as util
from debugger.enums import ProcessState
from debugger.mi.parser import Parser

GDB_PATH = util.get_root_path("build/gdb-build/gdb")

if not os.path.isfile(GDB_PATH):
    raise BaseException(
        "GDB executable is missing in {}. Please run install.sh."
        "".format(os.path.dirname(GDB_PATH)))


gdb_pretty_print_file = os.path.join(os.path.dirname(__file__),
                                     "gdb_pretty_print.py")

pp_function = "register_libstdcxx_printers"
pp_dir = glob.glob("/usr/share/gcc-*/python")
pp_import = "from libstdcxx.v6.printers import {}".format(pp_function)

if len(pp_dir) < 1:  # use pre-packaged STL printers
    pp_dir = util.get_root_path("util/")
    pp_import = "from stl_printers import {}".format(pp_function)
else:
    pp_dir = pp_dir[0]


class OutputParser(object):
    @staticmethod
    def get_name_until_param(data):
        if "," in data:
            return data[:data.index(",")]
        else:
            return data


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

        data = response[1:]  # skip ^
        status = OutputParser.get_name_until_param(data)
        data = data[len(status) + 1:]

        if status in CommandResult.result_map:
            result_type = CommandResult.result_map[status]
            return CommandResult(result_type, token, data)
        else:
            raise Exception("No result found for type: " + status)

    def __init__(self, result_type, token=None, data=""):
        """
        @type result_type: ResultType
        @type token: int
        @type data: str
        """
        self.result_type = result_type
        self.token = token
        self.data = data
        self.cli_data = []

    def is_success(self):
        return self.result_type == ResultType.Success

    def __repr__(self):
        return "[CMD_RESULT: {0} ({1}): {2}]".format(self.result_type,
                                                     self.token,
                                                     self.data)

    def __nonzero__(self):
        return self.is_success()


class StateOutput(object):
    parser = Parser()

    @staticmethod
    def parse(data):
        assert data[0] == Communicator.EXEC_ASYNC_START

        data = data[1:]
        state = OutputParser.get_name_until_param(data)

        if state == "running":
            return StateOutput(ProcessState.Running)
        elif state == "stopped":
            data = data[len(state) + 1:]
            data = StateOutput.parser.parse(data)

            state = ProcessState.Stopped
            exit_code = None

            reason = ""

            if "reason" in data:
                reason = data["reason"]

            if "exited" in reason:
                state = ProcessState.Exited

                if "exit-code" in data:
                    exit_code = int(data["exit-code"])
                elif "normally" in reason:
                    exit_code = 0

            return StateOutput(state, reason, exit_code)
        else:
            raise Exception("No state found for data: {0}".format(data))

    def __init__(self, state, reason=None, exit_code=None):
        """
        @type state: enums.ProcessState
        @type reason: enums.StopReason
        @type exit_code: int
        """
        self.state = state
        self.reason = reason
        self.exit_code = exit_code


class OutputType(Enum):
    CommandResult = 1
    AsyncExec = 2
    AsyncNotify = 3
    CliResponse = 4
    Separator = 5
    Unknown = 6


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
    CLI_START = "~"

    def __init__(self):
        self.process = None
        self.io_lock = threading.RLock()

        self.token = 0

        self.read_timer = None

        self.on_process_change = util.EventBroadcaster()

    def start_gdb(self):
        if self.process is not None:
            self.kill()

        if self.read_timer is not None:
            self.read_timer.stop_repeating()

        self.token = 0

        self.process = subprocess.Popen(
            bufsize=0,
            args=["{}".format(GDB_PATH),
                  "-return-child-result",
                  "-quiet",
                  "-nx",  # ignore .gdbinit
                  '-nw',  # inhibit window interface
                  '-interpreter=mi2',  # use GDB/MI v2
                  ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            close_fds=True
        )

        self._skip_to_separator()

        self.send("set print elements 0")
        self.send("set print frame-arguments none")
        self.send("set print address on")  # should be default
        self.send("python sys.path = [\"{}\"] + sys.path"
                  .format(pp_dir))
        self.send("python {}".format(pp_import))
        self.send("python {}(None)".format(pp_function))
        self.send("source {0}".format(gdb_pretty_print_file))

        self.read_timer = util.RepeatTimer(0.1, self._timer_read_output)
        self.read_timer.start()

    def send(self, command):
        """
        Sends the given command to GDB.
        @type command: str
        @rtype: CommandResult
        """
        self.io_lock.acquire()
        response = CommandResult(ResultType.Error)

        token = self.token
        self.token += 1

        cli = command[0] != "-"
        cli_data = []

        try:
            self.process.stdin.write(str(token) + command + "\n")
            self.process.stdin.flush()

            while True:
                output = self._parse_output(self._readline(True))
                if (output.type == OutputType.CommandResult and
                        output.data.token == token):
                    response = output.data
                elif cli and output.type == OutputType.CliResponse:
                    cli_data.append(output.data[2:-1].rstrip("\\n").strip())
                elif output.type == OutputType.Separator:
                    break
                else:
                    self._handle_output(output)

        except:
            util.Logger.debug(traceback.format_exc())

        self.io_lock.release()

        response.cli_data = cli_data

        return response

    def quit_program(self):
        if self.process:
            self.pause_program()
            self.send("kill")

    def pause_program(self):
        os.kill(self.process.pid, signal.SIGINT)

    def finish(self):
        if self.process:
            self.send("-gdb-exit")
            self.process.wait()
        self._reset()

    def kill(self):
        if self.process:
            self.process.kill()
        self._reset()

    def _timer_read_output(self):
        try:
            self.io_lock.acquire()
        except:
            return

        try:
            output = self._readline(False)

            if output:
                output = self._parse_output(output)
                self._handle_output(output)
        except:
            util.Logger.debug(traceback.format_exc())
        finally:
            self.io_lock.release()

    def _reset(self):
        if self.read_timer is not None:
            self.read_timer.stop_repeating()
        self.read_timer = None

        self.process = None

    def _handle_output(self, output):
        if output.type == OutputType.AsyncExec:
            self.on_process_change.notify(StateOutput.parse(output.data))
        elif output.type == OutputType.AsyncNotify:
            pass

    def _readline(self, block=False):
        self.io_lock.acquire()

        process = self.process
        input = None

        try:
            if not block:
                if len(select.select([process.stdout], [], [], 0.05)[0]) > 0:
                    input = process.stdout.readline()
            else:
                input = process.stdout.readline()
        except:
            util.Logger.debug(traceback.format_exc())

        self.io_lock.release()

        if not input:
            return None

        return input.strip()

    def _skip_to_separator(self):
        data = ""

        while data != Communicator.GROUP_SEPARATOR:
            data = self._readline(True)

    def _parse_output(self, response):
        if response is None:
            return OutputMessage(OutputType.Unknown)

        if response == Communicator.GROUP_SEPARATOR:
            return OutputMessage(OutputType.Separator)
        elif (response[0].isdigit() or
                response[0] == Communicator.RESPONSE_START):
            return OutputMessage(OutputType.CommandResult,
                                 CommandResult.parse(response))
        elif response[0] == Communicator.EXEC_ASYNC_START:
            return OutputMessage(OutputType.AsyncExec, response)
        elif response[0] == Communicator.NOTIFY_ASYNC_START:
            return OutputMessage(OutputType.AsyncNotify, response)
        elif response[0] == Communicator.CLI_START:
            return OutputMessage(OutputType.CliResponse, response)
        else:
            return OutputMessage(OutputType.Unknown)
