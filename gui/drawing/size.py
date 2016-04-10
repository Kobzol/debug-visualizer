#
#    Copyright (C) 2015-2016 Jakub Beranek
#
#    This file is part of Devi.
#
#    Devi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Devi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
#

# -*- coding: utf-8 -*-

import numbers
from vector import Vector


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
