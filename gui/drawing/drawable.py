# -*- coding: utf-8 -*-

import abc
from drawing.size import Size
from drawing.vector import Vector


class Color(object):
    def __init__(self, red=0.0, green=0.0, blue=0.0, alpha=1.0):
        """
        Represents RGBA color.
        @type red: float
        @type green: float
        @type blue: float
        @type alpha: float
        """
        self._red = red
        self._green = green
        self._blue = blue
        self._alpha = alpha

    @property
    def red(self):
        return self._red

    @property
    def green(self):
        return self._green

    @property
    def blue(self):
        return self._blue

    @property
    def alpha(self):
        return self._alpha


class DrawingUtils(object):
    @staticmethod
    def get_text_size(canvas, text):
        size = canvas.cr.text_extents(text)

        return Size(size[2], -size[1])   # (width, height)

    @staticmethod
    def set_color(canvas, color):
        """
        Sets color for Cairo context in canvas.
        @type canvas: canvas.Canvas
        @type color: Color
        """
        canvas.cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)

    @staticmethod
    def draw_text(canvas, text, position, color=Color(), y_center=False, x_center=False):
        """
        Draws text on a given position. When no centering is set, it will be drawn from top-left corner.
        @type canvas: canvas.Canvas
        @type text: str
        @type position: Vector
        @param color: Color
        @param y_center: bool
        @param x_center: bool
        """
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
        else:
            position.y += text_size.height

        DrawingUtils.set_color(canvas, color)
        cr.move_to(position.x, position.y)

        cr.show_text(text)

        cr.restore()

    @staticmethod
    def draw_line(canvas, point_from, point_to, color=Color(), width=1):
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
    def draw_arrow(canvas, point_from, point_to, color=Color(), width=1):
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
    def draw_rectangle(canvas, position, size, color=Color(), width=1, center=False):
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


class Margin(object):
    def __init__(self, top=0, right=0, bottom=0, left=0):
        """
        @type top: int
        @type right: int
        @type bottom: int
        @type left: int
        """
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left


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


class BoxedLabelDrawable(Drawable):
    def __init__(self, label, margin=None):
        """
        @type label: str
        @type margin: Margin
        """
        super(BoxedLabelDrawable, self).__init__()

        self.label = label
        self.margin = margin if margin else Margin()

    def get_bbox(self, canvas):
        label_size = DrawingUtils.get_text_size(canvas, self.label)

        width = self.margin.left + label_size.width + self.margin.right
        height = self.margin.top + label_size.height + self.margin.bottom

        return RectangleBBox(self.position, Size(width, height))

    def draw(self, canvas):
        bbox = self.get_bbox(canvas)

        # box
        DrawingUtils.draw_rectangle(canvas, self.position, bbox.size, center=False)

        text_x = self.position.x + self.margin.left
        text_y = self.position.y + self.margin.top

        # value
        DrawingUtils.draw_text(canvas, self.label, Vector(text_x, text_y), y_center=False)


class AbsValueDrawable(Drawable):
    def __init__(self, value):
        super(AbsValueDrawable, self).__init__()

        self.value = value

    def get_name(self):
        return self.value.name

    def get_value(self):
        value = self.value.value

        if value is None:
            return "(none)"
        else:
            return value

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
        height = self.position.y

        for index, var in enumerate(self.variables):
            var.position.y = height
            height += var.get_bbox(canvas).height
            var.draw(canvas)


class SimpleVarDrawable(AbsValueDrawable):
    def __init__(self, var):
        super(SimpleVarDrawable, self).__init__(var)

        self.name_box = BoxedLabelDrawable(self.get_name(), Margin(10, 10, 10, 10))
        self.value_box = BoxedLabelDrawable(self.get_value(), Margin(10, 10, 10, 10))
    
    def get_bbox(self, canvas):
        self.name_box.set_position(self.position)
        name_bbox = self.name_box.get_bbox(canvas)

        self.value_box.set_position(self.position.add(Vector(name_bbox.width, 0)))
        value_bbox = self.value_box.get_bbox(canvas)

        return RectangleBBox.contain((name_bbox, value_bbox))

    def draw(self, canvas):
        self.name_box.set_position(self.position)
        name_bbox = self.name_box.get_bbox(canvas)

        self.value_box.set_position(self.position.add(Vector(name_bbox.width, 0)))

        self.name_box.draw(canvas)
        self.value_box.draw(canvas)


class PointerDrawable(SimpleVarDrawable):
    pass


class VectorDrawable(SimpleVarDrawable):
    pass


class StructDrawable(SimpleVarDrawable):
    def __init__(self, val):
        super(StructDrawable, self).__init__(val)
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def get_children_left_offset(self):
        return 10

    def get_bbox(self, canvas):
        bboxes = []
        height = self.position.y

        for index, var in enumerate(self.children):
            bbox = var.get_bbox(canvas).copy()
            bbox.y = height
            bbox.x += self.position.x + self.get_children_left_offset()
            height += bbox.height
            bboxes.append(bbox)

        return RectangleBBox.contain(bboxes)

    def draw(self, canvas):
        height = self.position.y

        for index, var in enumerate(self.children):
            var.position.y = height
            var.position.x = self.position.x + self.get_children_left_offset()
            height += var.get_bbox(canvas).height
            var.draw(canvas)
