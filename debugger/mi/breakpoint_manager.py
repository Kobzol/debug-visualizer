# -*- coding: utf-8 -*-

from debugger_state import DebuggerState
from mi.mi_parser import MiParser


class BreakpointManager(object):
    def __init__(self, debugger):
        self.debugger = debugger
        self.breakpoints = []
        self.parser = MiParser()

    def add_breakpoint(self, location, line=None):
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        if line is not None:
            location += ":" + str(line)

        result = self.debugger.communicator.send("-break-insert {0}".format(location))

        if result:
            self.breakpoints.append(self.parser.parse_breakpoint(result.data))

            return True
        else:
            return False

    def get_breakpoints(self):
        bps = self.debugger.communicator.send("-break-list")

        if bps:
            return self.parser.parse_breakpoints(bps.data)
        else:
            return None

    def remove_breakpoint(self, location, line):
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        #for breakpoint in breakpoints: TODO
            #self.debugger.target.BreakpointDelete(breakpoint.id)
