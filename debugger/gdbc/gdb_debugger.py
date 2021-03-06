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


import gdb
import sys

from gdb_helper import GdbHelper
from gdb_thread_manager import GdbThreadManager
from gdb_frame_manager import GdbFrameManager
from gdb_file_manager import GdbFileManager
from gdb_breakpoint_manager import GdbBreakpointManager
from memory import Memory
from debugger.enums import DebuggerState


class GdbDebugger(object):
    def __init__(self, options):
        self.memory = Memory()
        self.gdb_helper = GdbHelper()
        self.thread_manager = GdbThreadManager()
        self.frame_manager = GdbFrameManager()
        self.file_manager = GdbFileManager()
        self.bp_manager = GdbBreakpointManager(self.before_bp, self.after_bp)
        # self.bp_manager.add_breakpoint("malloc", self.handle_malloc)
        # self.bp_manager.add_breakpoint("free", self.handle_free)

        self.set_options()
        gdb.events.exited.connect(self.handle_exit)

        if "valgrind_pid" in options:
            gdb.execute("target remote | vgdb --pid={}".format(
                options["valgrind_pid"]))

        self.change_state(DebuggerState.Started)

    def get_status(self):
        return self.state

    def set_options(self):
        gdb.execute("set print elements 0")

    def change_state(self, state):
        self.state = state
        print("Changed state: " + str(DebuggerState(state)))
        sys.stdout.flush()

    def handle_exit(self, exit_event):
        self.change_state(DebuggerState.Exited)
        self.bp_manager.remove_all_breakpoints()

    def before_bp(self, stop_event):
        self.change_state(DebuggerState.Stopped)

        """try:
            locals = self.thread_manager.get_thread_vars()[0]
            self.memory.match_pointers(locals)

            if isinstance(stop_event, gdb.SignalEvent):
                print("ERROR: " + str(stop_event.stop_signal))

            if not isinstance(stop_event, gdb.BreakpointEvent):
                return False

            return True
        except:
            traceback.print_exc()
            return False"""

    def after_bp(self, stop_event, continue_exec):
        if continue_exec:
            self.continue_exec()

    def continue_exec(self):
        self.change_state(DebuggerState.Running)
        gdb.execute("continue")

    def finish(self):
        self.change_state(DebuggerState.Running)
        gdb.execute("finish")

    def run(self):
        self.change_state(DebuggerState.Running)
        gdb.execute("run")

    def next(self):
        self.change_state(DebuggerState.Running)
        gdb.execute("next")

    def is_valid_memory_frame(self, frame):
        return frame.is_valid() and frame.type() in [gdb.NORMAL_FRAME,
                                                     gdb.INLINE_FRAME]

    def handle_malloc(self, stop_event):
        frame = gdb.newest_frame()
        frame_name = frame.name()

        if not self.is_valid_memory_frame(frame):
            return

        args = self.gdb_helper.get_args()

        if len(args) == 1:
            byte_count = args[0].value
            finish = gdb.FinishBreakpoint(internal=False)

            if not finish.is_valid():
                return

            self.finish()

            if not finish.is_valid():
                return

            address = str(finish.return_value)
            self.memory.malloc(address, byte_count, frame_name)

            if finish.is_valid():
                finish.delete()

    def handle_free(self, stop_event):
        frame = gdb.newest_frame()

        if not self.is_valid_memory_frame(frame):
            return

        args = self.gdb_helper.get_args()

        if len(args) == 1:
            address = self.gdb_helper.get_args()[0].value
            self.memory.free(address)
