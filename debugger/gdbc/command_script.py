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

from debugger.gdbc.gdb_debugger import GdbDebugger  # noqa
from debugger.net.server import Server  # noqa

debugger = GdbDebugger(data)
tstcommand = TestCommand(debugger)

server = Server(data["server_port"], debugger)
server.start()
