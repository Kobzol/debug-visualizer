# -*- coding: utf-8 -*-

import os

import debugger
from enums import DebuggerState
from mi.parser import Parser


class BreakpointManager(debugger.BreakpointManager):
    def __init__(self, debugger):
        super(BreakpointManager, self).__init__(debugger)
        self.parser = Parser()

    def add_breakpoint(self, location, line):
        """
        Adds a breakpoint, if there is not a breakpoint with the same location and line already.
        @type location: str
        @type line: int
        @rtype: boolean
        """
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        if self.find_breakpoint(location, line) is not None:
            return False

        if line is not None:
            location += ":" + str(line)

        return self.debugger.communicator.send("-break-insert {0}".format(location)).is_success()

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
            return self.parser.parse_breakpoints(bps.data)
        else:
            return None

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
            return self.debugger.communicator.send("-break-delete {0}".format(bp.number)).is_success()
        else:
            return False
