# -*- coding: utf-8 -*-

import enum


class MemoryException(Exception):
    def __init__(self, *args, **kwargs):
        super(MemoryException, self).__init__(*args, **kwargs)


class MemoryBlockState(enum.Enum):
    Allocated = 0
    Freed = 1


class MemoryBlock(object):
    def __init__(self, address, size):
        """
        Represents a heap-allocated memory block.
        @type address: int
        @type size: int
        """
        self.address = address
        self.size = size
        self.state = MemoryBlockState.Allocated

    def free(self):
        if self.state == MemoryBlockState.Freed:
            raise MemoryException("Memory block deallocated twice ({0} - {1} bytes)".format(self.address, self.size))

        self.state = MemoryBlockState.Freed


class LldbMemoryManager(object):
    def __init__(self, debugger):
        """
        @type debugger: lldbc.lldb_debugger.LldbDebugger
        """
        self.debugger = debugger

        self.breakpoints = []
        self.memory_blocks = []

    def _find_block_by_address(self, address):
        for block in self.memory_blocks:
            if block.address == address:
                return block

        return None

    def _handle_free(self, bp):
        address = self.debugger.thread_manager.get_current_frame().args[0].value
        block = self._find_block_by_address(address)
        
        if block is None:
            raise MemoryException("Non-existent memory block deallocated ({0})".format(address))
        else:
            block.free()

    def _handle_malloc(self, bp):
        self.debugger.debugger.SetAsync(False)
        self.debugger.fire_events = False

        try:
            thread = self.debugger.thread_manager.get_current_thread()
            frame = self.debugger.thread_manager.get_current_frame()

            if len(frame.args) < 1 or frame.args[0] is None:
                return

            bytes = frame.args[0].value

            self.debugger.exec_step_out()
            address = thread.return_value.value

            block = self._find_block_by_address(address)

            if block is not None:
                raise MemoryException("Memory block allocated twice ({0} - {1} bytes, originally {2} bytes)".format(
                    address, bytes, block.bytes
                ))
            else:
                self.memory_blocks.append(MemoryBlock(address, bytes))
        finally:
            self.debugger.fire_events = True
            self.debugger.debugger.SetAsync(True)

    def create_memory_bps(self):
        self.breakpoints.append((self.debugger.breakpoint_manager.add_breakpoint("free"), self._handle_free))
        self.breakpoints.append((self.debugger.breakpoint_manager.add_breakpoint("malloc"), self._handle_malloc))

    def is_memory_bp(self, bp):
        for x in self.breakpoints:
            if x[0] == bp:
                return True
        return False

    def handle_memory_bp(self, bp):
        for x in self.breakpoints:
            if x[0] == bp:
                x[1](bp)
                return
