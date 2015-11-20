# -*- coding: utf-8 -*-


class InferiorThread(object):
    def __init__(self, id, name, state, frame=None):
        """
        @type id: int
        @type name: str
        @type state: enums.ProcessState
        @type frame: frame.Frame
        @return:
        """
        self.id = id
        self.name = name
        self.state = state
        self.frame = frame

    def __repr__(self):
        return "Thread #{0} ({1}): {2}".format(self.id, self.name, self.state)