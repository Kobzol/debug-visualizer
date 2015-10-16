# -*- coding: utf-8 -*-

import abc
from drawing.size import Size
from drawing.vector import Vector


class DrawingUtils(object):
    @staticmethod
    def get_text_size(canvas, text):
        size = canvas.cr.text_extents(text)

        return Size(size[2], -size[1])   # (width, height)

    @staticmethod
    def set_color(canvas, color):
        canvas.cr.set_source_rgba(color[0], color[1], color[2], color[3])

    @staticmethod
    def draw_text(canvas, text, position, color=(0, 0, 0, 1), y_center=False, x_center=False):
        cr = canvas.cr
        cr.save()

        position = Vector.vectorize(position)

        text = text.strip()
        text_size = DrawingUtils.get_text_size(canvas, text)

        if x_center:
            position.x -= text_size.width / 2.0

        if y_center:
            w_size = DrawingUtils.get_text_size(canvas, "W")
            position.y += w_size.height / 2.0

        DrawingUtils.set_color(canvas, color)
        cr.move_to(position.x, position.y)

        cr.show_text(text)

        cr.restore()

    @staticmethod
    def draw_line(canvas, point_from, point_to, color=(0, 0, 0, 1), width=1):
        cr = canvas.cr
        cr.save()

        point_from = Vector.vectorize(point_from)
        point_to = Vector.vectorize(point_to)

        DrawingUtils.set_color(canvas, color)
        cr.set_line_width(width)

        cr.move_to(point_from.x, point_from.y)
        cr.line_to(point_to.x, point_to.y)
        cr.stroke()

        cr.restore()

    @staticmethod
    def draw_arrow(canvas, point_from, point_to, color=(0, 0, 0, 1), width=1):
        point_from = Vector.vectorize(point_from)
        point_to = Vector.vectorize(point_to)

        DrawingUtils.draw_line(canvas, point_from, point_to, color, width)

        vec_arrow = Vector.from_points(point_from, point_to)

        wing = vec_arrow.inverse().normalized().scaled(10)
        wing_right = wing.copy().rotate(45)
        wing_left = wing.copy().rotate(-45)

        DrawingUtils.draw_line(canvas, point_to, wing_right.add(point_to).to_point(), color, width)
        DrawingUtils.draw_line(canvas, point_to, wing_left.add(point_to).to_point(), color, width)

    @staticmethod
    def draw_rectangle(canvas, position, size, color=(0, 0, 0, 1), width=1, center=False):
        cr = canvas.cr
        cr.save()

        position = Vector.vectorize(position)
        size = Size.make_size(size)

        if center:
            position.x -= size.width / 2
            position.y -= size.height / 2

        DrawingUtils.set_color(canvas, color)
        cr.set_line_width(width)
        cr.rectangle(position.x, position.y, size.width, size.height)
        cr.stroke()

        cr.restore()


class RectangleBBox(object):
    @staticmethod
    def contain(bboxes):
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


class AbsValueDrawable(Drawable):
    def __init__(self, value):
        super(AbsValueDrawable, self).__init__()

        self.value = value

    def draw(self, canvas):
        pass

    def get_bbox(self, canvas):
        return None


class StackFrameDrawable(Drawable):
    def __init__(self):
        super(StackFrameDrawable, self).__init__()

        self.variables = []

    def add_variable(self, var):
        self.variables.append(var)

    def get_bbox(self, canvas):
        bboxes = []
        height = 0

        for index, var in enumerate(self.variables):
            bbox = var.get_bbox(canvas).copy()
            bbox.y += height
            height += bbox.height
            bboxes.append(bbox)

        return RectangleBBox.contain(bboxes)

    def draw(self, canvas):
        height = 0

        for index, var in enumerate(self.variables):
            var.position.y = height
            height += var.get_bbox(canvas).height
            var.draw(canvas)


class SimpleVarDrawable(AbsValueDrawable):
    def get_name(self):
        return self.value.name

    def get_value(self):
        value = self.value.value

        if value is None:
            return "(none)"
        else:
            return value

    def get_name_margins(self):
        return (2, 2)

    def get_value_margins(self):
        return (2, 2)

    def get_bbox(self, canvas):
        name_margins = self.get_name_margins()
        value_margins = self.get_value_margins()
        name_size = DrawingUtils.get_text_size(canvas, self.get_name())
        value_size = DrawingUtils.get_text_size(canvas, self.get_value())

        rect_size = Size(sum(name_margins) + sum(value_margins) + name_size.width + value_size.width,
                         name_size.height + 10)

        return RectangleBBox(self.position, rect_size)

    def draw(self, canvas):
        bbox = self.get_bbox(canvas)
        name_margins = self.get_name_margins()
        value_margins = self.get_value_margins()
        name_size = DrawingUtils.get_text_size(canvas, self.get_name())

        # rectangle
        DrawingUtils.draw_rectangle(canvas, self.position, bbox.size, center=False)
        # name
        DrawingUtils.draw_text(canvas, self.get_name(), self.position.add((name_margins[0], bbox.height / 2)), y_center=True)
        # divider
        line_top = self.position.add((name_margins[0] + name_size.width + name_margins[1], 0))
        DrawingUtils.draw_line(canvas,
                              line_top,
                              line_top.add((0, bbox.height)))
        # value
        DrawingUtils.draw_text(canvas, self.get_value(), line_top.add((value_margins[0], bbox.height / 2)), y_center=True)


class PointerDrawable(SimpleVarDrawable):
    pass


class StringDrawable(SimpleVarDrawable):
    pass


class VectorDrawable(SimpleVarDrawable):
    pass


class StructDrawable(SimpleVarDrawable):
    pass