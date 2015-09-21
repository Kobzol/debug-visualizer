# -*- coding: utf-8 -*-

import lldb
import os, sys
import json

data = {}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "options.json"), "r") as options:
    data = json.loads(options.read())
    
sys.path.append(data["code_path"])

print(str(data))

"""from gdbc.gdb_debugger import GdbDebugger
from net.server import Server

debugger = GdbDebugger(data)
tstcommand = TestCommand(debugger)

server = Server(data["server_port"], debugger)
server.start()"""