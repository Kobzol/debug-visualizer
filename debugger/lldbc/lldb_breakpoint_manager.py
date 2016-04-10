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

# -*- coding: utf-8 -*-

import os

from debugger.debugee import Breakpoint
from debugger.enums import DebuggerState
from debugger import debugger_api


class LldbBreakpointManager(debugger_api.BreakpointManager):
    def __init__(self, debugger):
        super(LldbBreakpointManager, self).__init__(debugger)

    def get_breakpoints(self):
        bps = [self.debugger.target.GetBreakpointAtIndex(i)
               for i in xrange(self.debugger.target.GetNumBreakpoints())]
        breakpoints = []
        for bp in bps:
            if bp.num_locations > 0:
                location = bp.GetLocationAtIndex(0)
                address = location.GetAddress().line_entry
                line = address.line
                file = os.path.abspath(address.file.fullpath)
                breakpoints.append(Breakpoint(bp.id, file, line))

        return breakpoints

    def toggle_breakpoint(self, location, line):
        bp = self.find_breakpoint(location, line)
        if bp:
            return self.remove_breakpoint(location, line)
        else:
            return self.add_breakpoint(location, line)

    def add_breakpoint(self, location, line):
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        location = os.path.abspath(location)

        bp = self.debugger.target.BreakpointCreateByLocation(location, line)

        if bp.IsValid() and bp.num_locations > 0:
            return True
        else:
            self.debugger.target.BreakpointDelete(bp.id)
            return False

    def find_breakpoint(self, location, line):
        location = os.path.abspath(location)

        bps = self.get_breakpoints()
        for bp in bps:
            if bp.location == location and bp.line == line:
                return bp

        return None

    def remove_breakpoint(self, location, line):
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        bp = self.find_breakpoint(location, line)
        if bp:
            self.debugger.target.BreakpointDelete(bp.number)
            return True
        else:
            return False
