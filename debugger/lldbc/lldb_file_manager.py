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

# -*- coding: utf-8 -*-


class LldbFileManager(object):
    def __init__(self, debugger):
        self.debugger = debugger

    def get_main_source_file(self):
        main_functions = self.debugger.target.FindFunctions("main")
        main_function = main_functions.GetContextAtIndex(0)
        compile_unit = main_function.GetCompileUnit()
        source_file = compile_unit.GetFileSpec()

        return source_file.fullpath

    def get_thread_location(self, thread):
        frame = thread.GetSelectedFrame()
        line_entry = frame.line_entry

        return (line_entry.file.fullpath, line_entry.line)

    def get_current_location(self):
        return self.get_thread_location(
            self.debugger.thread_manager.get_current_thread())
