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


import traceback

from debugger.mi.parser import Parser
from debugger import util, debugger_api
from debugger.util import Logger


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

        if thread_info:
            return thread_info.selected_thread
        else:
            return None

    def get_thread_info(self):
        """
        Returns (active_thread_id, all_threads).
        @rtype: debugee.ThreadInfo | None
        """
        output = self.debugger.communicator.send("-thread-info")

        if output:
            try:
                return self.parser.parse_thread_info(output.data)
            except:
                Logger.debug(traceback.format_exc())

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
            try:
                frame = self.parser.parse_stack_frame(output.data)

                if with_variables:
                    variables_info = self.parser.parse_frame_variables(
                        self.debugger.communicator.send(
                            "-stack-list-variables --skip-unavailable 0").data
                    )

                    for variable in variables_info:
                        try:
                            variable = self.debugger.variable_manager.\
                                get_variable(variable["name"])
                            if variable:
                                frame.variables.append(variable)
                        except:
                            Logger.debug("Coult not load variable {}"
                                         .format(variable))

                return frame
            except:
                Logger.debug(traceback.format_exc())

        return None

    def get_frames(self):
        """
        @rtype: list of debugee.Frame
        """
        output = self.debugger.communicator.send("-stack-list-frames")

        if output:
            try:
                return self.parser.parse_stack_frames(output.data)
            except:
                Logger.debug(traceback.format_exc())

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
            Logger.debug(traceback.format_exc())
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
