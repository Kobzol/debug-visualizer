# -*- coding: utf-8 -*-


class Frame(object):
    def __init__(self, level, func, file, line):
        """
        @type level: int
        @type func: str
        @type file: str
        @type line: int
        """
        self.level = level
        self.func = func
        self.file = file
        self.line = line

    def __repr__(self):
        return "Frame #{0} ({1} at {2}:{3}".format(self.level, self.func, self.file, self.line)
