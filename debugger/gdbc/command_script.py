# -*- coding: utf-8 -*-

import gdb
import json
import os
import sys


class TestCommand(gdb.Command):
    def __init__(self, debugger):
        gdb.Command.__init__(self, "tnext", gdb.COMMAND_NONE)
        self.debugger = debugger

    def invoke(self, argument, from_tty):
        print(self.debugger.file_manager.get_current_location())

data = {}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "options.json"), "r") as options:
    data = json.loads(options.read())

sys.path.append(data["code_path"])

from gdbc.gdb_debugger import GdbDebugger  # noqa
from net.server import Server  # noqa

debugger = GdbDebugger(data)
tstcommand = TestCommand(debugger)

server = Server(data["server_port"], debugger)
server.start()
