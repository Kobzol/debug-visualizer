# -*- coding: utf-8 -*-


class Breakpoint(object):
    """
    Represents a breakpoint.
    """
    def __init__(self, number, location, line):
        """
        @type number: int
        @type location: str
        @type line: int
        """
        self.number = number
        self.location = location
        self.line = line

    def __repr__(self):
        return "BP #{0}: {1}:{2}".format(self.number, self.location, self.line)
