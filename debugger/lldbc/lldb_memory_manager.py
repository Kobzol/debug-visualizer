# -*- coding: utf-8 -*-


class LldbMemoryManager(object):
    def __init__(self, debugger):
        self.debugger = debugger

        self.bp_free = None
        self.bp_malloc = None

    def _handle_free(self, bp):
        pass

    def _handle_malloc(self, bp):
        pass

    def create_memory_bps(self):
        self.bp_free = self.debugger.breakpoint_manager.add_breakpoint("free")
        self.bp_malloc = self.debugger.breakpoint_manager.add_breakpoint("malloc")

    def is_memory_bp(self, bp):
        return bp in (self.bp_free, self.bp_malloc)

    def handle_memory_bp(self, bp):
        if bp == self.bp_free:
            self._handle_free(bp)
        elif bp == self.bp_malloc:
            self._handle_malloc(bp)
