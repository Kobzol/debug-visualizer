# -*- coding: utf-8 -*-

import os
from enums import DebuggerState
from mi.parser import Parser


class BreakpointManager(object):
    def __init__(self, debugger):
        self.debugger = debugger
        self.parser = Parser()

    def add_breakpoint(self, location, line=None):
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        if line is not None:
            location += ":" + str(line)

        return self.debugger.communicator.send("-break-insert {0}".format(location)).is_success()

    def get_breakpoints(self):
        """
        @return: debugger.Breakpoint[] | None
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
        """
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        bp = self.find_breakpoint(location, line)

        if bp:
            return self.debugger.communicator.send("-break-delete {0}".format(bp.number)).is_success()
        else:
            return False
