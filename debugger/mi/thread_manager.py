# -*- coding: utf-8 -*-

from mi.parser import Parser
from inferior_thread import InferiorThread


class ThreadManager(object):
    def __init__(self, debugger):
        """
        @type debugger: mi.debugger.Debugger
        """
        self.debugger = debugger
        self.parser = Parser()

    def get_current_thread(self):
        """
        @return: thread.Thread | None
        """
        thread_info = self.get_thread_info()
        for thread in thread_info[1]:
            if thread.id == thread_info[0]:
                return thread

        return None

    def get_thread_info(self):
        """
        Returns (active_thread_id, all_threads).
        @return: tuple of (int, list of thread.Thread) | None
        """
        output = self.debugger.communicator.send("-thread-info")

        if output:
            return self.parser.parse_thread_info(output.data)
        else:
            return None

    def set_thread_by_index(self, thread_id):
        """
        @type thread_id: int
        """
        return self.debugger.communicator.send("-thread-select").is_success()

    def get_current_frame(self):
        """
        @return: frame.Frame | None
        """
        output = self.debugger.communicator.send("-stack-info-frame")

        if output:
            frame = self.parser.parse_stack_frame(output.data)
            variables_info = self.parser.parse_frame_variables(
                self.debugger.communicator.send("-stack-list-variables --skip-unavailable 0").data
            )

            for variable in variables_info:
                frame.variables.append(self.debugger.variable_manager.get_variable(variable["name"]))

            return frame

        else:
            return None

    def get_frames(self):
        """
        @return: list of frame.Frame | None
        """
        output = self.debugger.communicator.send("-stack-list-frames")

        if output:
            return self.parser.parse_stack_frames(output.data)
        else:
            return None

    def change_frame(self, frame_index):
        """
        @type frame_index: int
        @return: bool
        """
        if frame_index >= len(self.get_frames()):
            return False

        return self.debugger.communicator.send("-stack-select-frame {0}".format(frame_index)).is_success()