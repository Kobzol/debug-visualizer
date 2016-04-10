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
