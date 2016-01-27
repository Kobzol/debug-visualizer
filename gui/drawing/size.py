# -*- coding: utf-8 -*-

import numbers
from drawing.vector import Vector


class Size(object):
    @staticmethod
    def make_size(size):
        if isinstance(size, Size):
            return size
        elif isinstance(size, Vector):
            return Size(size.x, size.y)
        else:
            return Size(size[0], size[1])

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def replace_default(self, size):
        """
        Returns a new size that has values lower than one replaced from the given size.
        @type size: Size
        @rtype: Size
        """
        width = self.width if self.width >= 0 else size.width
        height = self.height if self.height >= 0 else size.height

        return Size(width, height)

    def copy(self):
        return Size(self.width, self.height)

    def __add__(self, other):
        assert isinstance(other, Size)

        return Size(self.width + other.width, self.height + other.height)

    def __sub__(self, other):
        assert isinstance(other, Size)

        return Size(self.width - other.width, self.height - other.height)

    def __mul__(self, other):
        assert isinstance(other, numbers.Number)

        return Size(self.width * other, self.height * other)

    def __div__(self, other):
        assert isinstance(other, numbers.Number)

        return Size(self.width / other, self.height / other)

    def __repr__(self):
        return "(" + str(self.width) + "," + str(self.height) + ")"
