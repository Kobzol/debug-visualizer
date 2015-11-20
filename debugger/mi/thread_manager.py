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
        @return: tuple of (int, thread.Thread) | None
        """
        output = self.debugger.communicator.send("-thread-info")

        if output:
            return self.parser.parse_thread_info(output.data)
        else:
            return None

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
