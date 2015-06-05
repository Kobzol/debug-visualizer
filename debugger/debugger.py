# -*- coding: utf-8 -*-

import gdb
import memory_bp
from gdb_helper import GdbHelper
from memory import Memory

class Debugger(object):
    def __init__(self, options):
        self.breakpoints = []
        self.add_breakpoint("malloc", self.handle_malloc)
        self.add_breakpoint("free", self.handle_free)
        
        self.exit_flag = False
        self.memory = Memory()
        self.gdb_helper = GdbHelper()
        
        gdb.events.stop.connect(self.handle_break)
        gdb.events.exited.connect(self.handle_exit)
        
        if "valgrind_pid" in options:
            gdb.execute("target remote | vgdb --pid=" + str(options["valgrind_pid"]))
    
    def handle_exit(self, exit_event):
        self.exit_flag = True
    
    def handle_break(self, stop_event):
        if isinstance(stop_event, gdb.SignalEvent):
            print("ERROR: " + str(stop_event.stop_signal))
        
        if not isinstance(stop_event, gdb.BreakpointEvent) or self.exit_flag:
            return
        
        for bp, callback in self.breakpoints:
            if bp in stop_event.breakpoints:
                if not callback():
                    self.command_continue()
                break
    
    def command_continue(self):
        gdb.execute("continue")
    
    def command_finish(self):
        gdb.execute("finish")
    
    def command_run(self):
        gdb.execute("run")
    
    def add_breakpoint(self, location, callback):
        self.breakpoints.append((gdb.Breakpoint(location, internal=True), callback))
        
    def handle_malloc(self):
        byte_count = self.gdb_helper.get_args()[0].value
        finish = gdb.FinishBreakpoint(internal=True)
        self.command_finish()
        address = str(finish.return_value)
        self.memory.malloc(address, byte_count)
        
        return False

    def handle_free(self):
        address = self.gdb_helper.get_args()[0].value
        
        self.memory.free(address)