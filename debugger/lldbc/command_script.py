# -*- coding: utf-8 -*-

import lldb
import os, sys
import json

data = {}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "options.json"), "r") as options:
    data = json.loads(options.read())
    
sys.path.append(data["code_path"])

from lldbc.lldb_debugger import LldbDebugger
from net.server import Server

debugger = LldbDebugger()

server = Server(data["server_port"], debugger)
server.start()