# -*- coding: utf-8 -*-

import gdb
import traceback
import enum

from gdb_helper import GdbHelper
from memory import Memory
from thread_manager import ThreadManager

class DebuggerState(enum.IntEnum):
    Stopped = 1
    Running = 2
    Exited = 3

class Debugger(object):
    def __init__(self, options):
        self.breakpoints = []
        self.add_breakpoint("malloc", self.handle_malloc)
        self.add_breakpoint("free", self.handle_free)
        
        self.state = DebuggerState.Exited
        self.manual_stepping = False
        
        self.memory = Memory()
        self.gdb_helper = GdbHelper()
        self.thread_manager = ThreadManager()
        
        gdb.events.stop.connect(self.handle_break)
        gdb.events.exited.connect(self.handle_exit)
        
        if "valgrind_pid" in options:
            gdb.execute("target remote | vgdb --pid=" + str(options["valgrind_pid"]))
            self.state = DebuggerState.Running
            
        self.add_breakpoint("main")
        self.command_run()
    
    def handle_exit(self, exit_event):
        self.state = DebuggerState.Exited
    
    def handle_break(self, stop_event):
        if self.state == DebuggerState.Exited:
            return
        
        self.state = DebuggerState.Stopped
        
        try:
            locals = self.thread_manager.get_thread_vars()[0]
            self.memory.match_pointers(locals)
            
            if isinstance(stop_event, gdb.SignalEvent):
                print("ERROR: " + str(stop_event.stop_signal))
            
            if not isinstance(stop_event, gdb.BreakpointEvent):
                return
            
            for bp, callback in self.breakpoints:
                if bp in stop_event.breakpoints:
                    if callback and not callback() and not self.manual_stepping:
                        self.command_continue()
                    break
        except:
            print(traceback.format_exc())
    
    def command_continue(self):
        self.state = DebuggerState.Running
        self.manual_stepping = False
        gdb.execute("continue")
    
    def command_finish(self):
        self.state = DebuggerState.Running
        gdb.execute("finish")
    
    def command_run(self):
        self.state = DebuggerState.Running
        self.manual_stepping = False
        gdb.execute("run")
    
    def command_next(self):
        self.state = DebuggerState.Running
        self.manual_stepping = True
        gdb.execute("next")
    
    def add_breakpoint(self, location, callback=None):
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
        
        return False