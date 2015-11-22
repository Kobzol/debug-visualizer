# -*- coding: utf-8 -*-

from enums import DebuggerState


class BreakpointInfo(object):
    def __init__(self, breakpoint, location, line):
        self.breakpoint = breakpoint
        self.location = location
        self.line = line

    def has_location(self, location, line):
        return location == self.location and line == self.line


class LldbBreakpointManager(object):
    def __init__(self, debugger):
        self.debugger = debugger
        self.breakpoints = []

    def get_breakpoints(self):
        return [ self.debugger.target.GetBreakpointAtIndex(i) for i in self.debugger.target.GetNumBreakpoints()]

    def add_breakpoint(self, location, line=None):
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        if line is not None:
            bp = self.debugger.target.BreakpointCreateByLocation(location, line)
        else:
            bp = self.debugger.target.BreakpointCreateByName(location)

        self.breakpoints.append(BreakpointInfo(bp, location, line))

        return bp

    def find_breakpoint(self, breakpoint_id):
        return self.debugger.target.FindBreakpointByID(breakpoint_id)

    def remove_breakpoint(self, location, line):
        self.debugger.require_state(DebuggerState.BinaryLoaded)

        breakpoints = [bp_info.breakpoint for bp_info in self.breakpoints if bp_info.has_location(location, line)]

        for breakpoint in breakpoints:
            self.debugger.target.BreakpointDelete(breakpoint.id)
