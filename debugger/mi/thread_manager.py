# -*- coding: utf-8 -*-

import traceback

from debugger.mi.parser import Parser
from debugger import util, debugger_api


class ThreadManager(debugger_api.ThreadManager):
    def __init__(self, debugger):
        """
        @type debugger: debugger.Debugger
        """
        super(ThreadManager, self).__init__(debugger)
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
        result = self.debugger.communicator.send(
            "-thread-select {0}".format(thread_id)).is_success()

        if result:
            self.debugger.on_thread_changed.notify(
                self.get_thread_info().selected_thread)
            self.debugger.on_frame_changed.notify(self.get_current_frame())

            util.Logger.debug("Changed to thread with id {0}".format(
                thread_id))

            return True
        else:
            return False

    def get_current_frame(self, with_variables=False):
        """
        Returns the current stack frame, optionally with it's parameters.
        @type with_variables: bool
        @rtype: debugee.Frame | None
        """
        output = self.debugger.communicator.send("-stack-info-frame")

        if output:
            frame = self.parser.parse_stack_frame(output.data)

            if with_variables:
                variables_info = self.parser.parse_frame_variables(
                    self.debugger.communicator.send(
                        "-stack-list-variables --skip-unavailable 0").data
                )

                for variable in variables_info:
                    variable = self.debugger.variable_manager.get_variable(
                        variable["name"])
                    if variable:
                        frame.variables.append(variable)

            return frame

        else:
            return None

    def get_frames(self):
        """
        @rtype: list of debugee.Frame
        """
        output = self.debugger.communicator.send("-stack-list-frames")

        if output:
            return self.parser.parse_stack_frames(output.data)
        else:
            return []

    def get_frames_with_variables(self):
        """
        Returns all stack frames with all their local variables and arguments.
        @rtype: list of debugger.debugee.Frame
        """
        current_frame = self.get_current_frame(False)

        if not current_frame:
            return []

        frames = []
        try:
            for i, fr in enumerate(self.get_frames()):
                self.change_frame(i, False)
                frames.append(self.get_current_frame(True))
        except:
            traceback.print_exc()
        finally:
            self.change_frame(current_frame.level, False)

        return frames

    def change_frame(self, frame_index, notify=True):
        """
        @type frame_index: int
        @type notify: bool
        @rtype: bool
        """
        if frame_index >= len(self.get_frames()):
            return False

        result = self.debugger.communicator.send(
            "-stack-select-frame {0}".format(frame_index)).is_success()

        if result:
            if notify:
                self.debugger.on_frame_changed.notify(self.get_current_frame())

                util.Logger.debug("Changed to frame with id {0}".format(
                    frame_index))

            return True
        else:
            return False
