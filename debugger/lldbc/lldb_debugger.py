# -*- coding: utf-8 -*-

import lldb
import threading
import sys
import os
from events import EventBroadcaster
import lldbc.exceptions as exceptions
import time

from debugger_state import DebuggerState
from lldbc.lldb_breakpoint_manager import LldbBreakpointManager
from lldbc.lldb_file_manager import LldbFileManager
from lldbc.lldb_io_manager import LldbIOManager
from lldbc.lldb_thread_manager import LldbThreadManager
from lldbc.lldb_process_enums import ProcessState, StopReason
from flags import Flags


class LldbDebugger(object):
    def __init__(self):
        self.debugger = lldb.SBDebugger.Create()
        self.debugger.SetAsync(True)

        self.breakpoint_manager = LldbBreakpointManager(self)
        self.file_manager = LldbFileManager(self)
        self.thread_manager = LldbThreadManager(self)
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

            self.on_process_state_changed.notify(state, return_code, return_desc)

            return
        elif state == ProcessState.Stopped:
            thread = self.thread_manager.get_current_thread()

            self.on_process_state_changed.notify(state, StopReason(thread.GetStopReason()), thread.GetStopDescription(100))

            return

        self.on_process_state_changed.notify(state, None, None)

    def require_state(self, required_state):
        if not self.get_state().is_set(required_state):
            raise exceptions.BadStateError(required_state, self.state)

    def get_state(self):
        return self.state

    def get_process_state(self):
        return self.process_state

    def load_binary(self, binary_path):
        self.target = self.debugger.CreateTargetWithFileAndArch(binary_path, lldb.LLDB_ARCH_DEFAULT)

        if self.target is not None:
            self.state.set(DebuggerState.BinaryLoaded)
            return True
        else:
            return False
    
    def launch(self, arguments=None, env_vars=None, file_in=None, file_out=None, file_err=None, working_directory=None):
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

        self.event_thread = threading.Thread(target=self._check_events)
        self.event_thread.start()

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
