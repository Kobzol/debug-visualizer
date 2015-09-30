# -*- coding: utf-8 -*-


class LldbThreadManager(object):
    def __init__(self, debugger):
        self.debugger = debugger
    
    def get_current_thread(self):
        return self.debugger.process.GetSelectedThread()
    
    def get_threads(self):
        return [t for t in self.debugger.process]
    
    def set_thread_by_index(self, thread_index):
        self.debugger.process.SetSelectedThreadByIndexId(thread_index)