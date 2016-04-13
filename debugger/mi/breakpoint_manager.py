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


import os

from debugger.enums import DebuggerState
from debugger.mi.parser import Parser
from debugger import debugger_api


class BreakpointManager(debugger_api.BreakpointManager):
    def __init__(self, debugger):
        super(BreakpointManager, self).__init__(debugger)
        self.parser = Parser()

    def add_breakpoint(self, location, line):
        """
        Adds a breakpoint, if there is not a breakpoint with the same location
        and line already.
        @type location: str
        @type line: int
        @rtype: boolean
        """
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        if self.find_breakpoint(location, line) is not None:
            return False

        if line is not None:
            location += ":" + str(line)

        success = self.debugger.communicator.send(
            "-break-insert {0}".format(location)).is_success()

        if success:
            self.on_breakpoint_changed.notify(self.find_breakpoint(location,
                                                                   line))

        return success

    def toggle_breakpoint(self, location, line):
        """
        Toggles a breakpoint on the given location and line.
        @type location: str
        @type line: int
        @rtype: boolean
        """
        bp = self.find_breakpoint(location, line)
        if bp:
            return self.remove_breakpoint(location, line)
        else:
            return self.add_breakpoint(location, line)

    def get_breakpoints(self):
        """
        @rtype: list of debugger.Breakpoint
        """
        bps = self.debugger.communicator.send("-break-list")

        if bps:
            try:
                return self.parser.parse_breakpoints(bps.data)
            except:
                return []
        else:
            return []

    def find_breakpoint(self, location, line):
        """
        @type location: str
        @type line: int
        @rtype: debugger.Breakpoint | None
        """
        location = os.path.abspath(location)

        for bp in self.get_breakpoints():
            if bp.location == location and bp.line == line:
                return bp

        return None

    def remove_breakpoint(self, location, line):
        """
        @type location: str
        @type line: int
        @rtype: boolean
        """
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        bp = self.find_breakpoint(location, line)

        if bp:
            success = self.debugger.communicator.send(
                "-break-delete {0}".format(bp.number)).is_success()

            if success:
                self.on_breakpoint_changed.notify(bp)
            return success
        else:
            return False
