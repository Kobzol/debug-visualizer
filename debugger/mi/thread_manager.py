# -*- coding: utf-8 -*-

from mi.parser import Parser
from util import Logger


class ThreadManager(object):
    def __init__(self, debugger):
        """
        @type debugger: mi.debugger.Debugger
        """
        self.debugger = debugger
        self.parser = Parser()

    def get_current_thread(self):
        """
        @rtype: debugee.Thread
        """
        thread_info = self.get_thread_info()
        return thread_info.selected_thread

    def get_thread_info(self):
        """
        Returns (active_thread_id, all_threads).
        @rtype: debugee.ThreadInfo | None
        """
        output = self.debugger.communicator.send("-thread-info")

        if output:
            return self.parser.parse_thread_info(output.data)
        else:
            return None

    def set_thread_by_index(self, thread_id):
        """
        @type thread_id: int
        @rtype: bool
        """
        result = self.debugger.communicator.send("-thread-select {0}".format(thread_id)).is_success()

        if result:
            self.debugger.on_thread_changed.notify(self.get_thread_info().selected_thread)
            self.debugger.on_frame_changed.notify(self.get_current_frame())

            Logger.debug("Changed to thread with id {0}".format(thread_id))

            return True
        else:
            return False

    def get_current_frame(self):
        """
        @rtype: debugee.Frame | None
        """
        output = self.debugger.communicator.send("-stack-info-frame")

        if output:
            frame = self.parser.parse_stack_frame(output.data)
            variables_info = self.parser.parse_frame_variables(
                self.debugger.communicator.send("-stack-list-variables --skip-unavailable 0").data
            )

            for variable in variables_info:
                variable = self.debugger.variable_manager.get_variable(variable["name"])
                if variable:
                    frame.variables.append(variable)

            return frame

        else:
            return None

    def get_frames(self):
        """
        @rtype: list of debugee.Frame | None
        """
        output = self.debugger.communicator.send("-stack-list-frames")

        if output:
            return self.parser.parse_stack_frames(output.data)
        else:
            return None

    def change_frame(self, frame_index):
        """
        @type frame_index: int
        @rtype: bool
        """
        if frame_index >= len(self.get_frames()):
            return False

        result = self.debugger.communicator.send("-stack-select-frame {0}".format(frame_index)).is_success()

        if result:
            self.debugger.on_frame_changed.notify(self.get_current_frame())

            Logger.debug("Changed to frame with id {0}".format(frame_index))

            return True
        else:
            return False
