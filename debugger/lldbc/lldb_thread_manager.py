# -*- coding: utf-8 -*-

import lldb
import re
from lldbc.lldb_helper import LldbHelper

class LldbThreadManager(object):
    def __init__(self, instance):
        self.instance = instance
    
    def get_current_thread(self):
        return self.process.process.GetSelectedThread()
    
    def get_threads(self):
        return [t for t in self.instance.process]
    
    def set_thread_by_index(self, thread_index):
        self.instance.process.SetSelectedThreadByIndexId(thread_index)
    
    def get_thread_vars(self, thread_id=None):
        
        return (locals, args)