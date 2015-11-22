# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.INFO)

import threading
import os
import time

import lldb
from events import EventBroadcaster
import exceptions as exceptions
from enums import DebuggerState
from lldbc.lldb_breakpoint_manager import LldbBreakpointManager
from lldbc.lldb_file_manager import LldbFileManager
from lldbc.lldb_io_manager import LldbIOManager
from lldbc.lldb_memory_manager import LldbMemoryManager
from lldbc.lldb_thread_manager import LldbThreadManager
from enums import ProcessState, StopReason, DebuggerState
from flags import Flags
from lldbc.lldb_variable_editor import LldbVariableEditor


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
        self.variable_editor = LldbVariableEditor(self)
        self.io_manager = LldbIOManager()

        self.target = None
        self.process = None
        self.event_thread = None
        self.event_thread_stop_flag = threading.Event()
        self.fire_events = True

        self.state = Flags(DebuggerState, DebuggerState.Started)
        self.process_state = ProcessState.Invalid

        self.exit_lock = threading.Lock()

        self.on_debugger_state_changed = EventBroadcaster()
        self.state.on_value_changed.redirect(self.on_debugger_state_changed)
        self.on_process_state_changed = EventBroadcaster()
        self.on_frame_changed = EventBroadcaster()

    def _check_events(self):
        event = lldb.SBEvent()
        listener = self.debugger.GetListener()

        while not self.event_thread_stop_flag.is_set():
            if listener.WaitForEvent(1, event):
                if lldb.SBProcess.EventIsProcessEvent(event):
                    state = ProcessState(lldb.SBProcess.GetStateFromEvent(event))

                    if self.fire_events:
                        self._handle_process_state(state)

        self.event_thread = None

    def _handle_process_state(self, state):
        self.process_state = state

        if state == ProcessState.Exited:
            self.stop(False)

            return
        elif state == ProcessState.Stopped:
            thread = self.thread_manager.get_current_thread()
            stop_reason = StopReason(thread.stop_reason)
            breakpoints = []

            """if stop_reason == StopReason.Breakpoint:
                for i in xrange(0, thread.GetStopReasonDataCount(), 2):
                    bp_id = thread.GetStopReasonDataAtIndex(i)
                    bp_loc_id = thread.GetStopReasonDataAtIndex(i + 1)
                    bp = self.breakpoint_manager.find_breakpoint(bp_id)

                    breakpoints.append((bp, bp.FindLocationByID(bp_loc_id)))

            for bp in breakpoints:
                is_memory_bp = self.memory_manager.is_memory_bp(bp[0])

                if is_memory_bp:
                    self.memory_manager.handle_memory_bp(bp[0]) # TODO: catch exceptions and propagate them
                    self.exec_continue()

                    return"""

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
        self.target = self.debugger.CreateTarget(os.path.abspath(binary_path))

        if self.target is not None:
            self.state.set(DebuggerState.BinaryLoaded)

            #self.memory_manager.create_memory_bps()

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

        self.event_thread_stop_flag.clear()
        self.event_thread = threading.Thread(target=self._check_events)
        self.event_thread.start()

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

    def exec_continue(self):
        self.require_state(DebuggerState.Running)
        self.process.Continue()

    def exec_pause(self):
        self.require_state(DebuggerState.Running)
        self.process.Stop()

    def exec_step_over(self):
        self.require_state(DebuggerState.Running)
        self.thread_manager.get_current_thread().StepOver()

    def exec_step_in(self):
        self.require_state(DebuggerState.Running)
        self.thread_manager.get_current_thread().StepInto()

    def exec_step_out(self):
        self.require_state(DebuggerState.Running)
        self.thread_manager.get_current_thread().StepOut()

    def stop(self, kill_process=False):
        self.exit_lock.acquire()

        try:
            if not self.state.is_set(DebuggerState.Running):
                return

            if self.process is not None:
                if kill_process:
                    self.process.Kill()
                else:
                    while self.process_state != ProcessState.Exited:
                        time.sleep(0.1)

                return_code = self.process.GetExitStatus()
                return_desc = self.process.GetExitDescription()

                self.on_process_state_changed.notify(ProcessState.Exited, ProcessExitedEventData(return_code, return_desc))
                self.process = None

            self.state.unset(DebuggerState.Running)

            if self.event_thread is not None:
                self.event_thread_stop_flag.set()
                self.event_thread = None

            self.io_manager.stop_io()
        finally:
            self.exit_lock.release()

    def quit(self):
        self.debugger.Terminate()
