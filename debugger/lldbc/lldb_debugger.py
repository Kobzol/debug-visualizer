import lldb
import threading
import sys
import os
import time

from debugger_state import DebuggerState
from lldbc.lldb_thread_manager import LldbThreadManager

class LldbDebugger(object):
    def __init__(self):
        self.debugger = lldb.SBDebugger.Create()
        self.debugger.SetAsync(False) # we want blocking process control
        
        self.thread_manager = LldbThreadManager(self)
        
        self.change_state(DebuggerState.Started)
        
        self.target = None
        self.process = None
    
    def get_selected_thread(self):
        return self.process.GetSelectedThread()
    
    def get_selected_frame(self):
        return self.get_selected_thread().GetSelectedFrame()
    
    def change_state(self, state):
        self.state = state
        
    def load_binary(self, binary_path):
        self.target = self.debugger.CreateTargetWithFileAndArch(binary_path, lldb.LLDB_ARCH_DEFAULT)
        
        if self.target != None:
            self.change_state(DebuggerState.BinaryLoaded)
    
    def launch(self, arguments=None, file_in=None, file_out=None, async=True):
        if self.process != None:
            self.change_state(DebuggerState.Running)     
         
        if async:
            self.done = threading.Event()
            self.thread = threading.Thread(target=self.receive_events, args=[arguments,file_in,file_out])
            self.thread.start()
        else:
            self.receive_events(arguments, file_in, file_out)
        
    def receive_events(self, arguments, file_in,file_out):
        launch_info = lldb.SBLaunchInfo(arguments)
        launch_info.SetWorkingDirectory(os.path.dirname(os.path.abspath(self.target.GetExecutable().GetFilename())))
        launch_info.AddOpenFileAction(0, file_in, True, False)
        launch_info.AddOpenFileAction(1, file_out, False, True)
        error = lldb.SBError()
        self.process = self.target.Launch(launch_info, error)
        
        if self.process.state == lldb.eStateStopped:
            self.handle_stop()
        elif self.process.state == lldb.eStateExited:
            self.handle_exit()
    
    def handle_stop(self):
        print("program is stopped")
        print(self.get_selected_frame().locals)
        sys.stdout.flush()
    
    def handle_exit(self):
        print("program exited")
    
    def kill(self):
        self.process.kill()