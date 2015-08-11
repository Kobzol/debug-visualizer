# -*- coding: utf-8 -*-

import gdb
import os, sys
import json

class TestCommand(gdb.Command):
    def __init__(self, debugger):
        gdb.Command.__init__(self, "tnext", gdb.COMMAND_NONE)
        self.debugger = debugger
        
    def invoke(self, argument, from_tty):
        self.debugger.command_next()

data = {}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "options.json"), "r") as options:
    data = json.loads(options.read())
    
sys.path.append(data["code_path"])

from debugger import Debugger
from debugserver import DebugServer

debugger = Debugger(data)
tstcommand = TestCommand(debugger)

#server = DebugServer(data["server_port"])
#server.start()