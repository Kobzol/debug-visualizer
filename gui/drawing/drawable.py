# -*- coding: utf-8 -*-

import abc

from gi.repository import Gtk
from gi.repository import Gdk

from drawing.geometry import Margin, RectangleBBox
from drawing.size import Size
from drawing.vector import Vector
from events import EventBroadcaster
from mouse import ClickHandler


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


class ValueEntry(Gtk.Frame):
    def __init__(self):
        Gtk.Frame.__init__(self)

        self.set_label("Edit value")
        self.set_label_align(0.0, 0.0)

        self.box = Gtk.Box()
        self.box.set_margin_bottom(5)
        self.box.set_margin_left(2)
        self.box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.text_entry = Gtk.Entry()
        self.confirm_button = Gtk.Button(label="Set")

        self.get_style_context().add_class("value-entry")

        self.box.pack_start(self.text_entry, False, False, 0)
        self.box.pack_start(self.confirm_button, False, False, 5)
        self.add(self.box)
        self.show_all()

        self.confirm_button.connect("clicked", lambda btn: self._handle_confirm_click())

        self.on_value_entered = EventBroadcaster()

    def _handle_confirm_click(self):
        value = self.text_entry.get_text()
        self.text_entry.set_text("")

        self.on_value_entered.notify(value)
        self.hide()


class Drawable(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.position = Vector(0, 0)
        self.children = []
        self.click_handler = ClickHandler(self)

    def set_position(self, position):
        self.position = Vector.vectorize(position)

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def get_bbox(self):
        pass


class BoxedLabelDrawable(Drawable):
    def __init__(self, canvas, label, margin=None):
        """
        @type label: str | callable
        @type margin: Margin
        """
        super(BoxedLabelDrawable, self).__init__(canvas)

        self.label = label
        self.margin = margin if margin else Margin()

    def get_label(self):
        if isinstance(self.label, str):
            return self.label
        else:
            return self.label()

    def get_bbox(self):
        label_size = DrawingUtils.get_text_size(self.canvas, self.get_label())

        width = self.margin.left + label_size.width + self.margin.right
        height = self.margin.top + label_size.height + self.margin.bottom

        return RectangleBBox(self.position, Size(width, height))

    def draw(self):
        bbox = self.get_bbox()

        # box
        DrawingUtils.draw_rectangle(self.canvas, self.position, bbox.size, center=False)

        text_x = self.position.x + self.margin.left
        text_y = self.position.y + self.margin.top

        # value
        DrawingUtils.draw_text(self.canvas, self.get_label(), Vector(text_x, text_y), y_center=False)


class AbsValueDrawable(Drawable):
    def __init__(self, canvas, value):
        """
        @type value: variable.Variable
        """
        super(AbsValueDrawable, self).__init__(canvas)

        self.value = value

    def get_name(self):
        return self.value.name

    def get_value(self):
        value = self.value.value

        if value is None:
            return "(none)"
        else:
            return value

    def draw(self):
        pass

    def get_bbox(self):
        return None


class StackFrameDrawable(Drawable):
    def __init__(self, canvas):
        super(StackFrameDrawable, self).__init__(canvas)

        self.variables = []

    def add_variable(self, var):
        self.variables.append(var)
        self.click_handler.propagate_handler(var.click_handler)

    def get_bbox(self):
        bboxes = []
        height = 0

        for index, var in enumerate(self.variables):
            bbox = var.get_bbox().copy()
            bbox.y += height
            height += bbox.height
            bboxes.append(bbox)

        return RectangleBBox.contain(bboxes)

    def draw(self):
        height = self.position.y

        for index, var in enumerate(self.variables):
            var.position.y = height
            height += var.get_bbox().height
            var.draw()


class SimpleVarDrawable(AbsValueDrawable):
    def __init__(self, canvas, value):
        """
        @type value: variable.Variable
        """
        super(SimpleVarDrawable, self).__init__(canvas, value)

        self.name_box = BoxedLabelDrawable(canvas, self.get_name, Margin.all(5.0))
        self.value_box = BoxedLabelDrawable(canvas, self.get_value, Margin.all(5.0))

        self.value_entry = None
        self.click_handler.on_mouse_click.subscribe(self._handle_mouse_click)

    def _handle_value_change(self, value):
        self.value.change_value(value)

    def _handle_mouse_click(self, point):
        """
        @type point: drawing.vector.Vector
        """
        if self.value_entry is None:
            self.value_entry = ValueEntry()
            self.canvas.fixed_wrapper.put(self.value_entry, point.x, point.y)
            self.canvas.fixed_wrapper.show_all()
            self.value_entry.on_value_entered.subscribe(self._handle_value_change)
        else:
            if self.value_entry.props.visible:
                self.value_entry.hide()
            else:
                self.value_entry.show()
                self.canvas.fixed_wrapper.move(self.value_entry, point.x, point.y)

    def get_bbox(self):
        self.name_box.set_position(self.position)
        name_bbox = self.name_box.get_bbox()

        self.value_box.set_position(self.position.add(Vector(name_bbox.width, 0)))
        value_bbox = self.value_box.get_bbox()

        return RectangleBBox.contain((name_bbox, value_bbox))

    def draw(self):
        self.name_box.set_position(self.position)
        name_bbox = self.name_box.get_bbox()

        self.value_box.set_position(self.position.add(Vector(name_bbox.width, 0)))

        self.name_box.draw()
        self.value_box.draw()

    def get_name(self):
        return "{0} {1}".format(self.value.type.name, self.value.name)


class PointerDrawable(SimpleVarDrawable):
    pass


class VectorDrawable(SimpleVarDrawable):
    pass


class StructDrawable(AbsValueDrawable):
    def __init__(self, canvas, value):
        """
        @type val: variable.Variable
        """
        super(StructDrawable, self).__init__(canvas, value)
        self.struct_label = BoxedLabelDrawable(canvas, "{0} {1}".format(value.type.name, value.name),
                                               Margin.all(6.0))
        self.children = []

    def add_child(self, child):
        """
        @type child: Drawable
        """
        self.children.append(child)
        self.click_handler.propagate_handler(child.click_handler)

    def get_children_left_offset(self):
        return 10

    def get_bbox(self):
        self.struct_label.set_position(self.position)
        label_bbox = self.struct_label.get_bbox()

        bboxes = [label_bbox]
        height = self.position.y + label_bbox.height

        for index, var in enumerate(self.children):
            bbox = var.get_bbox().copy()
            bbox.y = height
            bbox.x += self.position.x + self.get_children_left_offset()
            height += bbox.height
            bboxes.append(bbox)

        return RectangleBBox.contain(bboxes)

    def draw(self):
        self.struct_label.set_position(self.position)
        label_bbox = self.struct_label.get_bbox()

        height = self.position.y + label_bbox.height

        self.struct_label.draw()

        for index, var in enumerate(self.children):
            var.position.y = height
            var.position.x = self.position.x + self.get_children_left_offset()
            height += var.get_bbox().height
            var.draw()
