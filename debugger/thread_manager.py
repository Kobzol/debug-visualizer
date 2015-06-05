# -*- coding: utf-8 -*-

import gdb
import re
from gdb_helper import GdbHelper

class ThreadManager(object):
    def __init__(self):
        self.gdb_helper = GdbHelper()
    
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
    
    def get_thread_locals(self, thread_id):
        original_thread = self.get_current_thread()
        self.switch_to_thread(thread_id)
        
        self.switch_to_thread(original_thread.num)