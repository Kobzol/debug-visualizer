# -*- coding: utf-8 -*-

import math
import numbers


class Vector(object):
    @staticmethod
    def from_points(point_from, point_to):
        return Vector(point_to[0] - point_from[0], point_to[1] - point_from[1])

    @staticmethod
    def vectorize(vector):
        if isinstance(vector, Vector):
            return vector
        else:
            return Vector(vector[0], vector[1])

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def add(self, vector):
        vector = Vector.vectorize(vector)

        return Vector(vector.x + self.x, vector.y + self.y)

    def sub(self, vector):
        vector = Vector.vectorize(vector)

        return Vector(self.x - vector.x, self.y - vector.y)

    def dot(self, vector):
        vector = Vector.vectorize(vector)

        return self.x * vector.x +  self.y * vector.y

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        length = self.length()

        if length == 0:
            return Vector(0, 0)
        else:
            return Vector(self.x / length, self.y / length)

    def scaled(self, scale):
        return Vector(self.x * scale, self.y * scale)

    def inverse(self):
        return Vector(-self.x, -self.y)

    def angle(self):
        return math.degrees(math.atan2(self.x, -self.y))

    def rotate(self, angle, point=(0, 0)):
        theta = math.radians(angle)

        sin = math.sin(theta)
        cos = math.cos(theta)

        px = self.x - point[0]
        py = self.y - point[1]

        rot_x = px * cos - py * sin
        rot_y = px * sin + py * cos

        rot_x += point[0]
        rot_y += point[1]

        return Vector(rot_x, rot_y)

    def to_point(self):
        return (self.x, self.y)

    def copy(self):
        return Vector(self.x, self.y)

    def __add__(self, other):
        assert isinstance(other, Vector)

        return self.add(other)

    def __sub__(self, other):
        assert isinstance(other, Vector)

        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __mul__(self, other):
        """
        @type other: Vector | Number
        @return: Vector
        """
        if isinstance(other, numbers.Number):
            return Vector(self.x * other, self.y * other)
        elif isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        else:
            raise TypeError

    def __div__(self, other):
        assert isinstance(other, numbers.Number)

        return Vector(self.x / other, self.y / other)

    def __repr__(self):
        return "[" + str(self.x) + "," + str(self.y) + "]"
