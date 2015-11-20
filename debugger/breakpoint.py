# -*- coding: utf-8 -*-


class Breakpoint(object):
    def __init__(self, number, location, line):
        """
        @type number: int
        @type location: str
        @type line: int
        """
        self.number = number
        self.location = location
        self.line = line
