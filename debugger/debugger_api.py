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

import time

import util
from enums import DebuggerState, ProcessState


class ProcessExitedEventData(object):
    def __init__(self, return_code):
        self.return_code = return_code


class ProcessStoppedEventData(object):
    def __init__(self, stop_reason):
        self.stop_reason = stop_reason


class StartupInfo(object):
    def __init__(self, cmd_arguments="", working_directory="", env_vars=None):
        """
        @type cmd_arguments: str
        @type working_directory: str
        @type env_vars: list of tuple of (str, str)
        """
        self.cmd_arguments = cmd_arguments
        self.working_directory = working_directory
        self.env_vars = env_vars if env_vars is not None else []

    def copy(self):
        return StartupInfo(self.cmd_arguments,
                           self.working_directory,
                           list(self.env_vars))

    def __repr__(self):
        return "StartupInfo: [{}, {}, {}]".format(
            self.cmd_arguments, self.working_directory, self.env_vars
        )


class HeapManager(object):
    def __init__(self, debugger):
        """
        @type debugger: debugger.Debugger
        """
        self.debugger = debugger

        self.on_heap_change = util.EventBroadcaster()
        self.on_free_error = util.EventBroadcaster()

    def watch(self):
        """
        @rtype: str
        """
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def find_block_by_address(self, addr):
        """
        @type addr: str
        @rtype: HeapBlock | None
        """
        raise NotImplementedError()

    def get_total_allocations(self):
        """
        @rtype: int
        """
        raise NotImplementedError()

    def get_total_deallocations(self):
        """
        @rtype: int
        """
        raise NotImplementedError()


class IOManager(object):
    def __init__(self):
        self.stdin = None
        self.stdout = None
        self.stderr = None

    def handle_io(self):
        raise NotImplementedError()

    def stop_io(self):
        raise NotImplementedError()


class BreakpointManager(object):
    def __init__(self, debugger):
        """
        @type debugger: Debugger
        """
        self.debugger = debugger
        self.on_breakpoint_changed = util.EventBroadcaster()

    def add_breakpoint(self, location, line):
        """
        Adds a breakpoint, if there is not a breakpoint with the same
        location and line already.
        @type location: str
        @type line: int
        @rtype: boolean
        """
        raise NotImplementedError()

    def toggle_breakpoint(self, location, line):
        """
        Toggles a breakpoint on the given location and line.
        @type location: str
        @type line: int
        @rtype: boolean
        """
        raise NotImplementedError()

    def get_breakpoints(self):
        """
        @rtype: list of debugger.Breakpoint
        """
        raise NotImplementedError()

    def find_breakpoint(self, location, line):
        """
        @type location: str
        @type line: int
        @rtype: debugger.Breakpoint | None
        """
        raise NotImplementedError()

    def remove_breakpoint(self, location, line):
        """
        @type location: str
        @type line: int
        @rtype: boolean
        """
        raise NotImplementedError()


class FileManager(object):
    def __init__(self, debugger):
        """
        @type debugger: Debugger
        """
        self.debugger = debugger

    def get_main_source_file(self):
        raise NotImplementedError()

    def get_current_location(self):
        """
        Returns the current file and line of the debugged process.
        @rtype: tuple of basestring, int | None
        """
        raise NotImplementedError()

    def get_line_address(self, filename, line):
        """
        Returns the starting address and ending address in hexadecimal
        format of code at the specified line in the given file.
        Returns None if no code is at the given location.
        @type filename: str
        @type line: int
        @rtype: tuple of int | None
        """
        raise NotImplementedError()

    def disassemble(self, filename, line):
        """
        Returns disassembled code for the given location.
        Returns None if no code was found,
        @type filename: str
        @type line: int
        @rtype: str | None
        """
        raise NotImplementedError()

    def disassemble_raw(self, filename, line):
        """
        Disassembles the given line in a raw form (returns a string with the
        line and all assembly instructions for it).
        @type filename: str
        @type line: int
        @rtype: str | None
        """
        raise NotImplementedError()


class ThreadManager(object):
    def __init__(self, debugger):
        """
        @type debugger: Debugger
        """
        self.debugger = debugger

    def get_current_thread(self):
        """
        @rtype: debugee.Thread
        """
        raise NotImplementedError()

    def get_thread_info(self):
        """
        Returns (active_thread_id, all_threads).
        @rtype: debugee.ThreadInfo | None
        """
        raise NotImplementedError()

    def set_thread_by_index(self, thread_id):
        """
        @type thread_id: int
        @rtype: bool
        """
        raise NotImplementedError()

    def get_current_frame(self, with_variables=False):
        """
        @type with_variables: bool
        @rtype: debugee.Frame | None
        """
        raise NotImplementedError()

    def get_frames(self):
        """
        @rtype: list of debugee.Frame
        """
        raise NotImplementedError()

    def get_frames_with_variables(self):
        """
        @rtype: list of debugee.Frame
        """
        raise NotImplementedError()

    def change_frame(self, frame_index):
        """
        @type frame_index: int
        @rtype: bool
        """
        raise NotImplementedError()


class VariableManager(object):
    """
    Handles retrieval and updating of variables and raw memory of the
    debugged process.
    """
    def __init__(self, debugger):
        """
        @type debugger: Debugger
        """
        self.debugger = debugger

    def get_type(self, expression):
        """
        Returns type for the given expression.
        @type expression: str
        @rtype: debugee.Type
        """
        raise NotImplementedError()

    def get_variable(self, expression):
        """
        Returns a variable for the given expression-
        @type expression: str
        @rtype: debugee.Variable
        """
        raise NotImplementedError()

    def update_variable(self, variable):
        """
        Updates the variable's value in the debugged process.
        @type variable: debugee.Variable
        """
        raise NotImplementedError()

    def get_memory(self, address, count):
        """
        Returns count bytes from the given address.
        @type address: str
        @type count: int
        @rtype: list of int
        """
        raise NotImplementedError()

    def get_registers(self):
        """
        Returns the register values as a list of tuples with name and
        value of the given register.
        @rtype: list of register.Register
        """
        raise NotImplementedError()

    def get_vector_items(self, vector):
        """
        @type vector: debugger.debugee.VectorVariable
        @rtype: list of debugger.debugee.Variable
        """
        raise NotImplementedError()


class Debugger(object):
    def __init__(self):
        self.state = util.Flags(DebuggerState, DebuggerState.Started)
        self.process_state = ProcessState.Invalid

        self.io_manager = IOManager()
        self.breakpoint_manager = BreakpointManager(self)
        self.file_manager = FileManager(self)
        self.thread_manager = ThreadManager(self)
        self.variable_manager = VariableManager(self)
        self.heap_manager = HeapManager(self)

        self.on_process_state_changed = util.EventBroadcaster()
        self.on_debugger_state_changed = util.EventBroadcaster()
        self.state.on_value_changed.redirect(self.on_debugger_state_changed)
        self.on_process_state_changed = util.EventBroadcaster()
        self.on_frame_changed = util.EventBroadcaster()
        self.on_thread_changed = util.EventBroadcaster()

    def require_state(self, required_state):
        if not self.get_state().is_set(required_state):
            raise util.BadStateError(required_state, self.state)

    def get_state(self):
        return self.state

    def get_process_state(self):
        return self.process_state

    def load_binary(self, binary_path):
        raise NotImplementedError()

    def launch(self, startup_info=None):
        """
        Launches the program with the given startup info.
        @type startup_info: StartupInfo | None
        @rtype: bool
        """
        raise NotImplementedError()

    def exec_continue(self):
        raise NotImplementedError()

    def exec_pause(self):
        raise NotImplementedError()

    def exec_step_over(self):
        raise NotImplementedError()

    def exec_step_in(self):
        raise NotImplementedError()

    def exec_step_out(self):
        raise NotImplementedError()

    def quit_program(self, return_code=1):
        raise NotImplementedError()

    def terminate(self):
        raise NotImplementedError()

    def wait_for_stop(self):
        while self.process_state not in (ProcessState.Stopped,
                                         ProcessState.Exited):
            time.sleep(0.1)

        return self.process_state

    def wait_for_exit(self):
        while self.process_state != ProcessState.Exited:
            time.sleep(0.1)

        return self.process_state
