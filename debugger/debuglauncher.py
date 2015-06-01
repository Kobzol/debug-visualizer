# -*- coding: utf-8 -*-

from subprocess import PIPE, Popen, call
import threading, socket
import os, tempfile, shutil
import json

class DebugLauncher(object):
    def __init__(self, binary_path, server_port):
        self.gdb_path = "gdb"
        self.binary_path = binary_path
        self.server_port = server_port
        self.running = False
    
    def is_running(self):
        if self.running:
            if self.debugger_process.poll() is not None:
                self.running = False
                
        return self.running
        
    def launch(self, program_arguments = [], script_arguments = {}):
        if not self.is_running():
            script_arguments["code_path"] = os.path.dirname(os.path.abspath(__file__))
            script_arguments["server_port"] = self.server_port
            
            self.prepare_tmp_folder(os.path.join(script_arguments["code_path"], "command_script.py"), script_arguments)
            
            launch_data = [self.gdb_path, "--silent", "-x", self.get_tmp_script_path(), "--args", self.binary_path] + program_arguments
            
            self.debugger_process = Popen(launch_data, stdout=PIPE, stderr=PIPE)
            self.running = True
    
    def stop(self):
        if self.is_running():
            self.debugger_process.kill()
            self.running = False
    
    def get_tmp_script_path(self):
        return os.path.join(self.tmpdir, "dv_script.py")
    
    def get_tmp_options_path(self):
        return os.path.join(self.tmpdir, "options.json")
    
    def prepare_tmp_folder(self, script_path, script_arguments):
        self.tmpdir = tempfile.mkdtemp(prefix="dv")
        shutil.copy(script_path, self.get_tmp_script_path())
        
        with open(self.get_tmp_options_path(), "w") as options_file:
            options_file.write(json.dumps(script_arguments))