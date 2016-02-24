# -*- coding: utf-8 -*-

import json
import os
import sys

data = {}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "options.json"), "r") as options:
    data = json.loads(options.read())

sys.path.append(data["code_path"])

from debugger.lldbc.lldb_debugger import LldbDebugger  # noqa
from debugger.net.server import Server  # noqa

debugger = LldbDebugger()

server = Server(data["server_port"], debugger)
server.start()
