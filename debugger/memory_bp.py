import gdb

class MallocBreakpoint(gdb.Breakpoint):
    def __init__(self, debugger):
        gdb.Breakpoint.__init__(self, "main")
        self.debugger = debugger
    
    def stop(self):
        print("malloc breakpoint")
        return False


class FreeBreakpoint(gdb.Breakpoint):
    def __init__(self, debugger):
        gdb.Breakpoint.__init__(self, "free")
        self.debugger = debugger
        
    def stop(self):
        print("free breakpoint")
        return False