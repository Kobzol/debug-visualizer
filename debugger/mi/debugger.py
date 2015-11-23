# -*- coding: utf-8 -*-

import os
import threading

import time

import exceptions

import util
from enums import ProcessState, DebuggerState
from events import EventBroadcaster
from flags import Flags
from mi.breakpoint_manager import BreakpointManager
from mi.communicator import Communicator
from mi.file_manager import FileManager
from mi.io_manager import IOManager
from mi.thread_manager import ThreadManager
from mi.variable_manager import VariableManager


class ProcessExitedEventData(object):
    def __init__(self, return_code):
        self.return_code = return_code


class ProcessStoppedEventData(object):
    def __init__(self, stop_reason):
        self.stop_reason = stop_reason


class Debugger(object):
    def __init__(self):
        self.communicator = Communicator()
        self.communicator.on_process_change.subscribe(self._handle_process_state)

        self.io_manager = IOManager()
        self.breakpoint_manager = BreakpointManager(self)
        self.file_manager = FileManager(self)
        self.thread_manager = ThreadManager(self)
        self.variable_manager = VariableManager(self)

        self.state = Flags(DebuggerState, DebuggerState.Started)
        self.process_state = ProcessState.Invalid

        self.exit_lock = threading.Lock()

        self.on_debugger_state_changed = EventBroadcaster()
        self.state.on_value_changed.redirect(self.on_debugger_state_changed)
        self.on_process_state_changed = EventBroadcaster()
        self.on_frame_changed = EventBroadcaster()

    def _handle_process_state(self, output):
        """
        @type output: mi.communicator.StateOutput
        """
        self.process_state = output.state

        if output.state == ProcessState.Exited:
            self.stop(False, output.exit_code)
        elif output.state == ProcessState.Stopped:
            self.on_process_state_changed.notify(output.state,
                ProcessStoppedEventData(output.reason)
            )
        else:
            self.on_process_state_changed.notify(output.state, None)

    def require_state(self, required_state):
        if not self.get_state().is_set(required_state):
            raise util.BadStateError(required_state, self.state)

    def get_state(self):
        return self.state

    def get_process_state(self):
        return self.process_state

    def load_binary(self, binary_path):
        binary_path = os.path.abspath(binary_path)

        self.communicator.start_gdb()
        result = self.communicator.send("-file-exec-and-symbols {0}".format(binary_path))

        if result.is_success():
            self.state.set(DebuggerState.BinaryLoaded)

            return True
        else:
            return False

    def launch(self):
        self.require_state(DebuggerState.BinaryLoaded)

        stdin, stdout, stderr = self.io_manager.handle_io()

        self.communicator.send("run 1>{0} 2>{1} <{2}".format(stdout, stderr, stdin))

        self.state.set(DebuggerState.Running)

    def exec_continue(self):
        self.require_state(DebuggerState.Running)
        self.communicator.send("-exec-continue")

    def exec_pause(self):
        self.require_state(DebuggerState.Running)
        self.communicator.send("-exec-interrupt")

    def exec_step_over(self):
        self.require_state(DebuggerState.Running)
        self.communicator.send("-exec-next")

    def exec_step_in(self):
        self.require_state(DebuggerState.Running)
        self.communicator.send("-exec-next-instruction")

    def exec_step_out(self):
        self.require_state(DebuggerState.Running)
        self.communicator.send("-exec-finish")

    def stop(self, kill_process=False, return_code=None):
        self.exit_lock.acquire()

        try:
            if not self.state.is_set(DebuggerState.Running):
                return

            if kill_process:
                self.communicator.finish()
            else:
                while self.process_state != ProcessState.Exited:
                    time.sleep(0.1)

                self.on_process_state_changed.notify(ProcessState.Exited, ProcessExitedEventData(return_code))

            self.state.unset(DebuggerState.Running)

            self.io_manager.stop_io()
        finally:
            self.exit_lock.release()

    def wait_for_stop(self):
        while self.process_state not in (ProcessState.Stopped, ProcessState.Exited):
            time.sleep(0.1)

        return self.process_state