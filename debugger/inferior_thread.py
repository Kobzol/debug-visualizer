# -*- coding: utf-8 -*-


class ThreadInfo(object):
    """
    Represents thread state (list of threads and the selected thread) of the debugged process.
    """
    def __init__(self, selected_thread, threads):
        """
        @type selected_thread: InferiorThread
        @type threads: list of InferiorThread
        """
        self.selected_thread = selected_thread
        self.threads = threads

    def __repr__(self):
        return "Thread info: active: {0}, threads: {1}".format(str(self.selected_thread), str(self.threads))


class InferiorThread(object):
    """
    Represents a thread of the debugged process.
    """
    def __init__(self, id, name, state, frame=None):
        """
        @type id: int
        @type name: str
        @type state: enums.ProcessState
        @type frame: frame.Frame
        """
        self.id = id
        self.name = name
        self.state = state
        self.frame = frame

    def __repr__(self):
        return "Thread #{0} ({1}): {2}".format(self.id, self.name, self.state)