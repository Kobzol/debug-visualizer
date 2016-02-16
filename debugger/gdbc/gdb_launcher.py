# -*- coding: utf-8 -*-

import json
import os
import shutil
import subprocess
import tempfile


class GdbLauncher(object):
    def __init__(self, binary_path, server_port):
        self.gdb_path = "/home/kobzol/Downloads/gdb-7.10/gdb/gdb"
        self.binary_path = binary_path
        self.server_port = server_port

        self.debugger_process = None
        self.valgrind_process = None

        self.running = False

    def is_running(self):
        if self.running:
            if self.debugger_process.poll() is not None:
                self.stop()

        return self.running

    def launch(self, program_arguments=None, script_arguments=None,
               use_valgrind=False):
        if program_arguments is None:
            program_arguments = []

        if script_arguments is None:
            script_arguments = {}

        if not self.is_running():
            script_arguments["code_path"] = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            script_arguments["server_port"] = self.server_port

            self.prepare_tmp_folder(os.path.join(os.path.join(
                script_arguments["code_path"], "gdbc"), "command_script.py"))

            launch_data = [self.gdb_path,
                           "--silent",
                           "-x",
                           self.get_tmp_script_path(),
                           "--args",
                           self.binary_path] + program_arguments

            if use_valgrind:
                self.valgrind_process = subprocess.Popen(
                    ["valgrind",
                     "--tool=memcheck",
                     "--vgdb=yes",
                     "--vgdb-error=0",
                     self.binary_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                script_arguments["valgrind_pid"] = self.valgrind_process.pid

            self.write_script_options(script_arguments)

            self.debugger_process = subprocess.Popen(
                launch_data,
                stdin=subprocess.PIPE)
            # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running = True

    def stop(self):
        if self.is_running():
            self.debugger_process.kill()

            if self.valgrind_process:
                self.valgrind_process.kill()
                self.valgrind_process = None

            self.debugger_process = None

            self.running = False
            shutil.rmtree(self.tmpdir, ignore_errors=True)

    def get_tmp_script_path(self):
        return os.path.join(self.tmpdir, "dv_script.py")

    def get_tmp_options_path(self):
        return os.path.join(self.tmpdir, "options.json")

    def prepare_tmp_folder(self, script_path):
        self.tmpdir = tempfile.mkdtemp(prefix="dv")
        shutil.copy(script_path, self.get_tmp_script_path())

    def write_script_options(self, options):
        with open(self.get_tmp_options_path(), "w") as options_file:
            options_file.write(json.dumps(options))
