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


class LldbThreadManager(object):
    def __init__(self, debugger):
        """
        @type debugger: lldbc.lldb_debugger.LldbDebugger
        """
        self.debugger = debugger

    def get_current_thread(self):
        return self.debugger.process.GetSelectedThread()

    def get_threads(self):
        return [t for t in self.debugger.process]

    def set_thread_by_index(self, thread_index):
        self.debugger.process.SetSelectedThreadByIndexId(thread_index)

    def get_current_frame(self):
        return self.get_frames()[0]

    def get_frames(self):
        return self.get_current_thread().frames

    def change_frame(self, frameIndex):
        """
        @type frameIndex: int
        """
        if frameIndex >= len(self.get_frames()):
            return

        frame = self.get_frames()[frameIndex]
        self.get_current_thread().SetSelectedFrame(frameIndex)
        self.debugger.on_frame_changed.notify(frame)
