# -*- coding: utf-8 -*-

import os

from debugee import Breakpoint
import ptrace


class BreakpointManager(object):
    BREAKPOINT_ID = 0

    def __init__(self, debugger):
        self.debugger = debugger
        self.breakpoints = []
        self.original_instructions = {}

    def add_breakpoint(self, file, line):
        file = os.path.abspath(file)

        assert self.debugger.program_info.has_location(file, line)

        for bp in self.breakpoints:  # assumes different (file, line) maps to
            # different addresses
            if bp.location == file and bp.line == line:
                return

        self.breakpoints.append(Breakpoint(BreakpointManager.BREAKPOINT_ID,
                                           file, line))
        BreakpointManager.BREAKPOINT_ID += 1

    def set_breakpoints(self, pid):
        for bp in self.breakpoints:
            if bp.number not in self.original_instructions:
                addr = self.debugger.program_info.get_address(bp.location,
                                                              bp.line)
                inst = ptrace.ptrace_get_instruction(pid, addr)
                self.original_instructions[bp.number] = inst
                inst = (inst & 0xFFFFFF00) | 0xCC
                assert ptrace.ptrace_set_instruction(pid, addr, inst)

    def has_breakpoint_for_address(self, address):
        return self._get_breakpoint_for_address(address) is not None

    def restore_instruction(self, pid, address):
        bp = self._get_breakpoint_for_address(address)
        inst = self.original_instructions[bp.number]
        assert ptrace.ptrace_set_instruction(pid, address, inst)
        assert ptrace.ptrace_get_instruction(pid, address) == inst

        del self.original_instructions[bp.number]

    def _get_breakpoint_for_address(self, address):
        for bp in self.breakpoints:
            if self.debugger.program_info.get_address(
                    bp.location, bp.line) == address:
                return bp

        return None
