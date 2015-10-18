# -*- coding: utf-8 -*-

from drawing.size import Size
from drawing.vector import Vector


class RectangleBBox(object):
    @staticmethod
    def contain(bboxes):
        if len(bboxes) < 1:
            return None

        min_x = bboxes[0].x
        max_x = bboxes[0].x + bboxes[0].width
        min_y = bboxes[0].y
        max_y = bboxes[0].y + bboxes[0].height

        for bbox in bboxes[1:]:
            min_x = min(min_x, bbox.x)
            max_x = max(max_x, bbox.x + bbox.width)
            min_y = min(min_y, bbox.y)
            max_y = max(max_y, bbox.y + bbox.height)

        return RectangleBBox((min_x, min_y), (max_x - min_x, max_y - min_y))

    def __init__(self, position=(0, 0), size=(0, 0)):
        self.position = Vector.vectorize(position)
        self.size = Size.make_size(size)

        self.x = self.position.x
        self.y = self.position.y
        self.width = self.size.width
        self.height = self.size.height

    def moved(self, offset):
        return RectangleBBox(self.position.add(Vector.vectorize(offset)), self.size)

    def scaled(self, scale):
        return RectangleBBox(self.position, self.size + Size.make_size(scale))

    def copy(self):
        return RectangleBBox((self.x, self.y), (self.width, self.height))

    def is_point_inside(self, point):
        """
        @type point: Vector
        """
        return (self.position.x <= point.x <= self.position.x + self.width and
                self.position.y <= point.y <= self.position.y + self.height)


class Margin(object):
    @staticmethod
    def all(size):
        """
        Makes a margin with all sub-margins equal to the given value.
        @type size: float
        @rtype: Margin
        """
        return Margin(size, size, size, size)

    def __init__(self, top=0.0, right=0.0, bottom=0.0, left=0.0):
        """
        @type top: float
        @type right: float
        @type bottom: float
        @type left: float
        """
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
