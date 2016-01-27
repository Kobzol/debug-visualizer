# -*- coding: utf-8 -*-
import os
import tempfile

import time

import util
from enums import DebuggerState, ProcessState


class ProcessExitedEventData(object):
    def __init__(self, return_code):
        self.return_code = return_code


class ProcessStoppedEventData(object):
    def __init__(self, stop_reason):
        self.stop_reason = stop_reason


class IOManager(object):
    def __init__(self):
        self.stdin = None
        self.stdout = None
        self.stderr = None

    def create_pipe(self):
        tmpdir = tempfile.gettempdir()
        temp_name = next(tempfile._get_candidate_names())

        fifo = os.path.join(tmpdir, temp_name + ".fifo")

        os.mkfifo(fifo)

        return os.path.abspath(fifo)

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

    def add_breakpoint(self, location, line):
        """
        Adds a breakpoint, if there is not a breakpoint with the same location and line already.
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
        Returns the starting address and ending address in hexadecimal format of code at the specified line in the given file.
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
        Disassembles the given line in a raw form (returns a string with the line and all assembly instructions for it).
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

    def get_current_frame(self):
        """
        @rtype: debugee.Frame | None
        """
        raise NotImplementedError()

    def get_frames(self):
        """
        @rtype: list of debugee.Frame | None
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
    Handles retrieval and updating of variables and raw memory of the debugged process.
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
        Returns the register values as a list of tuples with name and value of the given register.
        @rtype: list of register.Register
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

    def launch(self):
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

    def kill(self, kill_process=False):
        raise NotImplementedError()

    def stop_program(self, return_code=1):
        raise NotImplementedError()

    def wait_for_stop(self):
        while self.process_state not in (ProcessState.Stopped, ProcessState.Exited):
            time.sleep(0.1)

        return self.process_state

    def quit(self):
        pass
