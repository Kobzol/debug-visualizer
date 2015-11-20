# -*- coding: utf-8 -*-

import os
import threading

import exceptions
from debugger_state import DebuggerState
from enums import ProcessState
from events import EventBroadcaster
from flags import Flags
from mi.communicator import Communicator
from mi.io_manager import IOManager


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


class Debugger(object):
    def __init__(self):
        self.communicator = Communicator()
        self.target = None
        self.process = None
        self.event_thread = None
        self.event_thread_stop_flag = threading.Event()
        self.fire_events = True

        self.io_manager = IOManager()

        self.state = Flags(DebuggerState, DebuggerState.Started)
        self.process_state = ProcessState.Invalid

        self.exit_lock = threading.Lock()

        self.on_debugger_state_changed = EventBroadcaster()
        self.state.on_value_changed.redirect(self.on_debugger_state_changed)
        self.on_process_state_changed = EventBroadcaster()
        self.on_frame_changed = EventBroadcaster()

    def _check_events(self):
        """event = lldb.SBEvent()
        listener = self.debugger.GetListener()

        while not self.event_thread_stop_flag.is_set():
            if listener.WaitForEvent(1, event):
                if lldb.SBProcess.EventIsProcessEvent(event):
                    state = ProcessState(lldb.SBProcess.GetStateFromEvent(event))

                    if self.fire_events:
                        self._handle_process_state(state)"""

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

        self.event_thread_stop_flag.clear()
        self.event_thread = threading.Thread(target=self._check_events)
        self.event_thread.start()

        stdin, stdout, stderr = self.io_manager.handle_io()

        self.communicator.send("run 1>{0} 2>{1} <{2}".format(stdout, stderr, stdin))

        self.state.set(DebuggerState.Running)

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
