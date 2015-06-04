# -*- coding: utf-8 -*-

import gdb
import os, sys
import json

data = {}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "options.json"), "r") as options:
    data = json.loads(options.read())
    
sys.path.append(data["code_path"])

from debugger import Debugger
from debugserver import DebugServer

debugger = Debugger()

#server = DebugServer(data["server_port"])
#server.start()