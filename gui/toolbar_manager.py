# -*- coding: utf-8 -*-

from gi.repository import GObject

from debugger_state import DebuggerState
from lldbc.lldb_process_enums import ProcessState


class ToolbarManager(object):
    def __init__(self, toolbar_builder, debugger):
        signals = {
            "toolbar-run": lambda *x: self.run(),
            "toolbar-continue": lambda *x: self.cont(),
            "toolbar-stop": lambda *x: self.stop(),
            "toolbar-pause": lambda *x: self.pause(),
            "toolbar-step-over": lambda *x: self.step_over()
        }

        toolbar_builder.connect_signals(signals)

        self.toolbar_builder = toolbar_builder
        self.toolbar = toolbar_builder.get_object("toolbar")
        self.debugger = debugger
        self.debugger.on_process_state_changed.subscribe(self._handle_process_state_change)
        self.debugger.on_debugger_state_changed.subscribe(self._handle_debugger_state_change)

        self._change_state("run", False)
        self._change_state("stop", False)
        self._change_state("pause", False)
        self._change_state("continue", False)
        self._change_state("step_over", False)

    def _get_items(self):
        return [self.toolbar.get_nth_item(i) for i in xrange(0, self.toolbar.get_n_items())]

    def _state_exited(self):
        self._change_state("run", True)
        self._change_state("stop", False)
        self._change_state("pause", False)
        self._change_state("continue", False)
        self._change_state("step_over", False)

    def _state_stopped(self):
        self._change_state("run", False)
        self._change_state("stop", True)
        self._change_state("pause", False)
        self._change_state("continue", True)
        self._change_state("step_over", True)

    def _state_running(self):
        self._change_state("run", False)
        self._change_state("stop", True)
        self._change_state("pause", True)
        self._change_state("continue", False)
        self._change_state("step_over", False)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Exited:
            self._state_exited()
        elif state == ProcessState.Stopped:
            self._state_stopped()
        elif state == ProcessState.Running:
            self._state_running()

    def _handle_debugger_state_change(self, state):
        if state.is_set(DebuggerState.BinaryLoaded):
            self._change_state("run", True)
        else:
            self._change_state("run", False)

    def _change_state(self, item_name, sensitive=True):
        GObject.idle_add(lambda *x: self._change_state_ui(item_name, sensitive))

    def _change_state_ui(self, item_name, sensitive=True):
        item = self.toolbar_builder.get_object(item_name)
        item.set_sensitive(sensitive)

    def run(self):
        self.debugger.launch()

    def cont(self):
        self.debugger.exec_continue()

    def stop(self):
        self.debugger.stop(True)

    def pause(self):
        self.debugger.exec_pause()

    def step_over(self):
        self.debugger.exec_step_over()
