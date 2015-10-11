# -*- coding: utf-8 -*-

import abc
from drawing.canvas import CanvasUtils
from drawing.size import Size
from drawing.vector import Vector


class RectangleBBox(object):
    def __init__(self, position, size):
        self.position = Vector.vectorize(position)
        self.size = Size.make_size(size)

        self.x = self.position.x
        self.y = self.position.y
        self.width = self.size.width
        self.height = self.size.height


class Drawable(object):
    def __init__(self):
        self.position = Vector(0, 0)
        self.children = []

    def set_position(self, position):
        self.position = Vector.vectorize(position)

    @abc.abstractmethod
    def draw(self, canvas):
        pass

    @abc.abstractmethod
    def get_bbox(self, canvas):
        pass


class SimpleVarDrawable(Drawable):
    def __init__(self, value):
        super(SimpleVarDrawable, self).__init__()
        
        self.value = value

    def get_name(self):
        return "name"  # self.value.name

    def get_value(self):
        return "value"  # self.value.name

    def get_name_margins(self):
        return (2, 2)

    def get_value_margins(self):
        return (2, 2)

    def get_bbox(self, canvas):
        name_margins = self.get_name_margins()
        value_margins = self.get_value_margins()
        name_size = CanvasUtils.get_text_size(canvas, self.get_name())
        value_size = CanvasUtils.get_text_size(canvas, self.get_value())

        rect_size = Size(sum(name_margins) + sum(value_margins) + name_size.width + value_size.width,
                         name_size.height + 10)

        return RectangleBBox(self.position, rect_size)

    def draw(self, canvas):
        bbox = self.get_bbox(canvas)
        name_margins = self.get_name_margins()
        value_margins = self.get_value_margins()
        name_size = CanvasUtils.get_text_size(canvas, self.get_name())

        # rectangle
        CanvasUtils.draw_rectangle(canvas, self.position, bbox.size, center=False)
        # name
        CanvasUtils.draw_text(canvas, self.get_name(), self.position.add((name_margins[0], bbox.height / 2)), y_center=True)
        # divider
        line_top = self.position.add((name_margins[0] + name_size.width + name_margins[1], 0))
        CanvasUtils.draw_line(canvas,
                              line_top,
                              line_top.add((0, bbox.height)))
        # value
        CanvasUtils.draw_text(canvas, self.get_value(), line_top.add((value_margins[0], bbox.height / 2)), y_center=True)
