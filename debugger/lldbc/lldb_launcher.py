# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015-2016 Jakub Beranek
#
#    This file is part of Devi.
#
#    Devi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Devi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
#


import json
import os
import shutil
import subprocess
import tempfile


class LldbLauncher(object):
    def __init__(self, server_port):
        self.python_path = "python2.7"
        self.server_port = server_port
        self.code_path = os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))

        self.debugger_process = None
        self.running = False

    def is_running(self):
        return self.running

    def launch(self):
        if not self.is_running():
            script_arguments = {
                "code_path": self.code_path,
                "server_port": self.server_port
            }

            self.prepare_tmp_folder(os.path.join(
                os.path.join(script_arguments["code_path"], "lldbc"),
                "command_script.py"))
            self.write_script_options(script_arguments)

            launch_data = [self.python_path, self.get_tmp_script_path()]

            self.debugger_process = subprocess.Popen(
                launch_data,
                stdin=subprocess.PIPE)
            # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running = True

    def stop(self):
        if self.is_running():
            self.debugger_process.kill()
            self.debugger_process.wait()
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
