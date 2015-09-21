# -*- coding: utf-8 -*-

import lldb

class LldbBreakpointManager(object):
    def __init__(self, before_bp, after_bp):
        self.before_bp = before_bp
        self.after_bp = after_bp
        #gdb.events.stop.connect(self.handle_break) TODO
        
        self.breakpoints = []
            
    def handle_break(self, stop_event):
        self.before_bp(stop_event)
        
        callback = None
        
        for bp, cb in self.breakpoints:
            if bp in stop_event.breakpoints:
                callback = cb
                break
            
        if callback:
            cb(stop_event) # inspecting callback, continue execution
            self.after_bp(stop_event, True)
        else:
            self.after_bp(stop_event, False)
    
    def add_breakpoint(self, location, callback = None):
        self.breakpoints.append((gdb.Breakpoint(location, internal=True), callback))
        
    def remove_breakpoint(self, location):
        for bp, callback in self.breakpoints:
            if bp.location == location:
                bp.delete()
                
        self.breakpoints = [bp for bp in self.breakpoints if bp[0].location != location]
        
    def remove_all_breakpoints(self):
        for bp, callback in self.breakpoints:
            bp.delete()
        
        self.breakpoints = []