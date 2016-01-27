# -*- coding: utf-8 -*-

import logging

import util

logging.basicConfig(level=logging.INFO)

import lldb
import threading
import os
import time

import debugger
from lldbc.lldb_breakpoint_manager import LldbBreakpointManager
from lldbc.lldb_file_manager import LldbFileManager
from lldbc.lldb_io_manager import LldbIOManager
from lldbc.lldb_memory_manager import LldbMemoryManager
from lldbc.lldb_thread_manager import LldbThreadManager
from enums import ProcessState, StopReason, DebuggerState
from lldbc.lldb_variable_editor import LldbVariableEditor


class LldbDebugger(debugger.Debugger):
    def __init__(self):
        super(LldbDebugger, self).__init__()
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

        self.exit_lock = threading.Lock()

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
            self.kill(False)

            return
        elif state == ProcessState.Stopped:
            thread = self.thread_manager.get_current_thread()
            stop_reason = StopReason(thread.stop_reason)

            self.on_process_state_changed.notify(state, debugger.ProcessStoppedEventData(stop_reason))

            return

        self.on_process_state_changed.notify(state, None)

    def require_state(self, required_state):
        if not self.get_state().is_set(required_state):
            raise util.BadStateError(required_state, self.state)

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
            self.kill(True)

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
            self.kill(True)
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

    def kill(self, kill_process=False):
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

                self.on_process_state_changed.notify(ProcessState.Exited, debugger.ProcessExitedEventData(return_code))
                self.process = None

            self.state.unset(DebuggerState.Running)

            if self.event_thread is not None:
                self.event_thread_stop_flag.set()
                self.event_thread = None

            self.io_manager.stop_io()
        finally:
            self.exit_lock.release()

    def stop_program(self, return_code=1):
        self.exit_lock.acquire()

        try:
            if not self.state.is_set(DebuggerState.Running):
                return

            self.process.Kill()

            self.process_state = ProcessState.Exited
            self.on_process_state_changed.notify(ProcessState.Exited, debugger.ProcessExitedEventData(return_code))
            util.Logger.debug("Debugger process ended")
            self.state.unset(DebuggerState.Running)

            self.io_manager.stop_io()
        finally:
            self.exit_lock.release()

    def quit(self):
        self.debugger.Terminate()
