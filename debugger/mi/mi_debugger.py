# -*- coding: utf-8 -*-

import os
import threading

import debugger.util as util
from debugger.enums import ProcessState, DebuggerState
from debugger.mi.breakpoint_manager import BreakpointManager
from debugger.mi.communicator import Communicator
from debugger.mi.file_manager import FileManager
from debugger.mi.heap_manager import HeapManager
from debugger.mi.io_manager import IOManager
from debugger.mi.thread_manager import ThreadManager
from debugger.mi.variable_manager import VariableManager
from debugger import debugger_api


shlib_path = util.get_root_path("build/debugger/liballochook.so")
if not os.path.isfile(shlib_path):
    raise BaseException("liballochook.so is not compiled in build/debugger")


class MiDebugger(debugger_api.Debugger):
    def __init__(self):
        super(MiDebugger, self).__init__()

        self.communicator = Communicator()
        self.communicator.on_process_change.subscribe(
            self._handle_process_state)

        self.io_manager = IOManager()
        self.breakpoint_manager = BreakpointManager(self)
        self.file_manager = FileManager(self)
        self.thread_manager = ThreadManager(self)
        self.variable_manager = VariableManager(self)
        self.heap_manager = HeapManager(self)

        self.exit_lock = threading.RLock()

    def _handle_process_state(self, output):
        """
        @type output: mi.communicator.StateOutput
        """
        util.Logger.debug("Process state changed: {0}".format(output.state))
        self.process_state = output.state

        if output.state == ProcessState.Exited:
            self._cleanup_program()
            self._on_program_ended(output.exit_code)
        elif output.state == ProcessState.Stopped:
            self.on_process_state_changed.notify(
                output.state,
                debugger_api.ProcessStoppedEventData(output.reason)
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
        result = self.communicator.send(
            "-file-exec-and-symbols {0}".format(binary_path))

        util.Logger.debug("Loading program binary {0} succeeded: {1}".format(
            binary_path, result.is_success()))

        if result.is_success():
            self.state.set(DebuggerState.BinaryLoaded)
            self.communicator.send("-gdb-set mi-async on")

            return True
        else:
            return False

    def launch(self):
        self.require_state(DebuggerState.BinaryLoaded)

        stdin, stdout, stderr = self.io_manager.handle_io()
        alloc_file = self.heap_manager.watch()

        self.communicator.send("set environment DEVI_ALLOC_FILE_PATH={}"
                               .format(alloc_file))
        self.communicator.send("set environment LD_PRELOAD={}"
                               .format(shlib_path))

        self.on_process_state_changed.notify(ProcessState.Launching, None)
        result = self.communicator.send("run 1>{0} 2>{1} <{2}".format(stdout,
                                                                      stderr,
                                                                      stdin))

        util.Logger.debug("Launching program: {0}".format(result))

        if result:
            self.state.set(DebuggerState.Running)

        return result.is_success()

    def exec_continue(self):
        self.require_state(DebuggerState.Running)
        self.communicator.send("-exec-continue")

    def exec_pause(self):
        self.require_state(DebuggerState.Running)
        self.communicator.pause_program()
        self.communicator.send("interrupt")

    def exec_step_over(self):
        self.require_state(DebuggerState.Running)
        self.communicator.send("-exec-next")

    def exec_step_in(self):
        self.require_state(DebuggerState.Running)
        self.communicator.send("-exec-step")

    def exec_step_out(self):
        self.require_state(DebuggerState.Running)
        self.communicator.send("-exec-finish")

    def quit_program(self, return_code=1):
        if not self.state.is_set(DebuggerState.Running):
            return

        self.communicator.quit_program()
        self._cleanup_program()
        self._on_program_ended(return_code)

    def terminate(self):
        self.quit_program()
        self.communicator.kill()

    def _cleanup_program(self):
        self.exit_lock.acquire()

        try:
            if not self.state.is_set(DebuggerState.Running):
                return

            util.Logger.debug("Cleaning debugged process")
            self.state.unset(DebuggerState.Running)

            self.io_manager.stop_io()
            self.heap_manager.stop()
        finally:
            self.exit_lock.release()

    def _on_program_ended(self, return_code):
        self.process_state = ProcessState.Exited
        self.on_process_state_changed.notify(
            ProcessState.Exited,
            debugger_api.ProcessExitedEventData(return_code))
