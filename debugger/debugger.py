# -*- coding: utf-8 -*-

import util
from enums import DebuggerState, ProcessState
from events import EventBroadcaster
from flags import Flags


class ProcessExitedEventData(object):
    def __init__(self, return_code):
        self.return_code = return_code


class ProcessStoppedEventData(object):
    def __init__(self, stop_reason):
        self.stop_reason = stop_reason


class Debugger(object):
    def __init__(self):
        self.state = Flags(DebuggerState, DebuggerState.Started)
        self.process_state = ProcessState.Invalid

        self.on_process_state_changed = EventBroadcaster()
        self.on_debugger_state_changed = EventBroadcaster()
        self.state.on_value_changed.redirect(self.on_debugger_state_changed)
        self.on_process_state_changed = EventBroadcaster()
        self.on_frame_changed = EventBroadcaster()
        self.on_thread_changed = EventBroadcaster()

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
        raise NotImplementedError()
