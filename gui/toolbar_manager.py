# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015-2016 Jakub Beranek
#
#    This file is part of Devi.
#
#    Devi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Devi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
#


from debugger.enums import ProcessState, DebuggerState
from debugger.util import EventBroadcaster
from gui_util import require_gui_thread, run_on_gui


class ToolbarManager(object):
    def __init__(self, toolbar_builder, debugger):
        signals = {
            "toolbar-run": lambda *x: self.run(),
            "toolbar-continue": lambda *x: self.cont(),
            "toolbar-stop": lambda *x: self.stop(),
            "toolbar-pause": lambda *x: self.pause(),
            "toolbar-step-over": lambda *x: self.step_over(),
            "toolbar-step-in": lambda *x: self.step_in(),
            "toolbar-step-out": lambda *x: self.step_out()
        }

        toolbar_builder.connect_signals(signals)

        self.toolbar_builder = toolbar_builder
        self.toolbar = toolbar_builder.get_object("toolbar")
        self.debugger = debugger
        self.debugger.on_process_state_changed.subscribe(
            self._handle_process_state_change)
        self.debugger.on_debugger_state_changed.subscribe(
            self._handle_debugger_state_change)

        self.grp_halt_control = ["stop", "pause"]
        self.grp_step = ["continue", "step_over", "step_in", "step_out"]

        self.on_run_process = EventBroadcaster()

    @require_gui_thread
    def _get_items(self):
        return [self.toolbar.get_nth_item(i)
                for i in xrange(0, self.toolbar.get_n_items())]

    def _state_exited(self):
        self._change_grp_state(self.grp_halt_control, False)
        self._change_grp_state(self.grp_step, False)
        self._change_state("run", True)

    def _state_stopped(self):
        self._change_grp_state(self.grp_halt_control, False)
        self._change_grp_state(self.grp_step, True)

        self._change_state("stop", True)

    def _state_running(self):
        self._change_grp_state(self.grp_halt_control, True)
        self._change_grp_state(self.grp_step, False)
        self._change_state("run", False)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Exited:
            self._state_exited()
        elif state == ProcessState.Stopped:
            self._state_stopped()
        elif state == ProcessState.Running:
            self._state_running()

    def _handle_debugger_state_change(self, state, old_value):
        if (state.is_set(DebuggerState.BinaryLoaded) and
                not state.is_set(DebuggerState.Running)):
            self._change_state("run", True)
        else:
            self._change_state("run", False)

    def _change_state(self, item_name, sensitive=True):
        run_on_gui(self._change_state_ui, item_name, sensitive)

    def _change_grp_state(self, group, sensitive=True):
        for item in group:
            self._change_state(item, sensitive)

    @require_gui_thread
    def _change_state_ui(self, item_name, sensitive=True):
        item = self.toolbar_builder.get_object(item_name)
        item.set_sensitive(sensitive)

    def run(self):
        self.on_run_process.notify()

    def cont(self):
        self.debugger.exec_continue()

    def stop(self):
        self.debugger.quit_program()

    def pause(self):
        self.debugger.exec_pause()

    def step_over(self):
        self.debugger.exec_step_over()

    def step_in(self):
        self.debugger.exec_step_in()

    def step_out(self):
        self.debugger.exec_step_out()
