# -*- coding: utf-8 -*-

import gdb
import traceback
import sys

from gdb_helper import GdbHelper
from memory import Memory
from thread_manager import ThreadManager
from frame_manager import FrameManager
from file_manager import FileManager
from breakpoint_manager import BreakpointManager
from debugger_state import DebuggerState


class Debugger(object):
    def __init__(self, options):
        self.memory = Memory()
        self.gdb_helper = GdbHelper()
        self.thread_manager = ThreadManager()
        self.frame_manager = FrameManager()
        self.file_manager = FileManager()
        self.bp_manager = BreakpointManager(self.before_bp, self.after_bp)
        #self.bp_manager.add_breakpoint("malloc", self.handle_malloc)
        #self.bp_manager.add_breakpoint("free", self.handle_free)
        
        self.set_gdb_options()
        gdb.events.exited.connect(self.handle_exit)
        
        if "valgrind_pid" in options:
            gdb.execute("target remote | vgdb --pid=" + str(options["valgrind_pid"]))
    
        self.change_state(DebuggerState.Started)
    
    def get_status(self):
        return self.state
    
    def set_gdb_options(self):
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
            print(traceback.format_exc())
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
        return frame.is_valid() and frame.type() in [gdb.NORMAL_FRAME, gdb.INLINE_FRAME]   
        
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