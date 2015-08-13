# -*- coding: utf-8 -*-

import gdb

class BreakpointManager(object):
    def __init__(self, before_bp, after_bp):
        self.before_bp = before_bp
        self.after_bp = after_bp
        gdb.events.stop.connect(self.handle_break)
        
        self.breakpoints = []
            
    def handle_break(self, stop_event):
        should_continue = self.before_bp(stop_event)
        
        if not should_continue:
            return
        
        callback = None
        
        for bp, cb in self.breakpoints:
            if bp in stop_event.breakpoints:
                callback = cb
                break
            
        if callback:
            cb(stop_event)
        
        self.after_bp(stop_event)
    
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