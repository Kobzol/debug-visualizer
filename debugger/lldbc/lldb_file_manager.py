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
