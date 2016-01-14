from breakpoint import Breakpoint


class BreakpointManager(object):
    BREAKPOINT_ID = 0

    def __init__(self, debugger):
        self.debugger = debugger
        self.breakpoints = []

    def add_breakpoint(self, file, line):
        assert self.debugger.program_info.has_location(file, line)

        self.breakpoints.append(Breakpoint(BreakpointManager.BREAKPOINT_ID, file, line))
        BreakpointManager.BREAKPOINT_ID += 1
