# -*- coding: utf-8 -*-

import lldb
import threading
import os
from events import EventBroadcaster
import lldbc.exceptions as exceptions
import time

from debugger_state import DebuggerState
from lldbc.lldb_breakpoint_manager import LldbBreakpointManager
from lldbc.lldb_file_manager import LldbFileManager
from lldbc.lldb_io_manager import LldbIOManager
from lldbc.lldb_memory_manager import LldbMemoryManager
from lldbc.lldb_thread_manager import LldbThreadManager
from lldbc.lldb_process_enums import ProcessState, StopReason
from flags import Flags


class ProcessExitedEventData(object):
    def __init__(self, return_code, return_desc):
        self.return_code = return_code
        self.return_desc = return_desc


class ProcessStoppedEventData(object):
    def __init__(self, stop_reason, stop_desc=None, breakpoints=None):
        if breakpoints is None:
            breakpoints = []

        self.stop_reason = stop_reason
        self.stop_desc = stop_desc
        self.breakpoints = breakpoints


class LldbDebugger(object):
    def __init__(self):
        self.debugger = lldb.SBDebugger.Create()
        self.debugger.SetAsync(True)

        self.breakpoint_manager = LldbBreakpointManager(self)
        self.file_manager = LldbFileManager(self)
        self.thread_manager = LldbThreadManager(self)
        self.memory_manager = LldbMemoryManager(self)
        self.io_manager = LldbIOManager()

        self.target = None
        self.process = None
        self.event_thread = None

        self.state = Flags(DebuggerState, DebuggerState.Started)
        self.process_state = ProcessState.Invalid

        self.on_debugger_state_changed = EventBroadcaster()
        self.state.on_value_changed.redirect(self.on_debugger_state_changed)
        self.on_process_state_changed = EventBroadcaster()

    def _check_events(self):
        event = lldb.SBEvent()
        listener = self.debugger.GetListener()

        while self.process is not None:
            if listener.WaitForEvent(1, event):
                if lldb.SBProcess.EventIsProcessEvent(event):
                    state = ProcessState(lldb.SBProcess.GetStateFromEvent(event))
                    self._handle_process_state(state)

        self.event_thread = None

    def _handle_process_state(self, state):
        self.process_state = state

        if state == ProcessState.Exited:
            self.state.unset(DebuggerState.Running)

            return_code = self.process.GetExitStatus()
            return_desc = self.process.GetExitDescription()

            self.process = None
            self.io_manager.stop_io()

            self.on_process_state_changed.notify(state, ProcessExitedEventData(return_code, return_desc))

            return
        elif state == ProcessState.Stopped:
            thread = self.thread_manager.get_current_thread()
            stop_reason = StopReason(thread.GetStopReason())
            breakpoints = []

            if stop_reason == StopReason.Breakpoint:
                for i in xrange(0, thread.GetStopReasonDataCount(), 2):
                    bp_id = thread.GetStopReasonDataAtIndex(i)
                    bp_loc_id = thread.GetStopReasonDataAtIndex(i + 1)
                    bp = self.breakpoint_manager.find_breakpoint(bp_id)

                    breakpoints.append((bp, bp.FindLocationByID(bp_loc_id)))

            for bp in breakpoints:
                is_memory_bp = self.memory_manager.is_memory_bp(bp[0])

                if is_memory_bp:
                    self.memory_manager.handle_memory_bp(bp[0])
                    self.exec_continue()
                    return

            self.on_process_state_changed.notify(state,
                 ProcessStoppedEventData(stop_reason, thread.GetStopDescription(100), breakpoints)
            )

            return

        self.on_process_state_changed.notify(state, None)

    def require_state(self, required_state):
        if not self.get_state().is_set(required_state):
            raise exceptions.BadStateError(required_state, self.state)

    def get_state(self):
        return self.state

    def get_process_state(self):
        return self.process_state

    def load_binary(self, binary_path):
        #error = lldb.SBError()
        #self.target = self.debugger.CreateTarget(os.path.abspath(binary_path), "i386-pc-linux", None, True, error)
        self.target = self.debugger.CreateTarget(os.path.abspath(binary_path))

        if self.target is not None:
            self.state.set(DebuggerState.BinaryLoaded)

            self.memory_manager.create_memory_bps()

            return True
        else:
            return False
    
    def launch(self, arguments=None, env_vars=None, working_directory=None):
        self.require_state(DebuggerState.BinaryLoaded)

        if self.process is not None:
            self.stop(True)

        if type(arguments) is str:
            arguments = [arguments]

        if type(env_vars) is str:
            env_vars = [env_vars]

        if working_directory is None:
            working_directory = os.path.dirname(self.target.GetExecutable().fullpath)

        stdin, stdout, stderr = self.io_manager.handle_io()

        error = lldb.SBError()
        self.process = self.target.Launch(self.debugger.GetListener(),
                                          arguments, # argv
                                          env_vars, # envp
                                          stdin, # stdin
                                          stdout, # stdout
                                          stderr, # stderr
                                          working_directory, # working directory
                                          lldb.eLaunchFlagNone, # launch flags
                                          False, # stop at entry
                                          error)

        self.state.set(DebuggerState.Running)

        if error.fail:
            self.process = None
            self.stop(True)
            raise Exception(error.description)

        self.event_thread = threading.Thread(target=self._check_events)
        self.event_thread.start()

    def exec_continue(self):
        self.require_state(DebuggerState.Running)
        self.process.Continue()

    def exec_pause(self):
        self.require_state(DebuggerState.Running)
        self.process.Stop()

    def exec_step_over(self):
        self.require_state(DebuggerState.Running)
        self.thread_manager.get_current_thread().StepOver(lldb.eOnlyDuringStepping)

    def stop(self, kill_process=False):
        if not self.state.is_set(DebuggerState.Running):
            return

        if self.process is not None:
            if kill_process:
                self.process.Kill()
            else:
                while self.process_state != ProcessState.Exited:
                    time.sleep(0.1)

        if self.event_thread is not None:
            self.event_thread.join()
            self.event_thread = None

        self.io_manager.stop_io()

        self.state.unset(DebuggerState.Running)
