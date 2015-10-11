# -*- coding: utf-8 -*-
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
