# -*- coding: utf-8 -*-

import gdb
import re
from gdbc.gdb_helper import GdbHelper

class GdbThreadManager(object):
    def __init__(self):
        self.gdb_helper = GdbHelper()
        self.thread_stack = []
    
    def get_inferior(self):
        return gdb.selected_inferior()
    
    def get_current_thread(self):
        return gdb.selected_thread()
    
    def get_thread(self, thread_id):
        return self.get_threads()[thread_id - 1]
    
    def get_threads(self):
        return sorted(self.get_inferior().threads(), key=lambda x: x.num)
    
    def switch_to_thread(self, thread_id):
        self.get_threads()[thread_id - 1].switch()
    
    def push_thread(self, new_thread_id):
        self.thread_stack.append(self.get_current_thread())
        self.switch_to_thread(new_thread_id)
        
    def pop_thread(self):
        self.switch_to_thread(self.thread_stack.pop().num)
    
    def get_thread_vars(self, thread_id=None):
        if thread_id is not None:
            self.push_thread(thread_id)
        
        locals = self.gdb_helper.get_locals()
        args = self.gdb_helper.get_args()
        
        if thread_id is not None:
            self.pop_thread()
        
        return (locals, args)