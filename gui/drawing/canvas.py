# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk
from drawing.size import Size
from drawing.vector import Vector

from events import EventBroadcaster


class ValueEntry(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self)

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.text_entry = Gtk.Entry()
        self.confirm_button = Gtk.Button(label="Set")

        self.add(self.text_entry)
        self.add(self.confirm_button)

        self.confirm_button.connect("clicked", lambda btn: self._handle_confirm_click())

        self.on_value_entered = EventBroadcaster()

    def _handle_confirm_click(self):
        value = self.text_entry.get_text()
        self.text_entry.set_text("")

        self.on_value_entered.notify(value)


class CanvasUtils(object):
    @staticmethod
    def get_text_size(canvas, text):
        size = canvas.cr.text_extents(text)

        return Size(size[2], size[3])   # (width, height)

    @staticmethod
    def set_color(canvas, color):
        canvas.cr.set_source_rgba(color[0], color[1], color[2], color[3])

    @staticmethod
    def draw_text(canvas, text, point_from, color=(0, 0, 0, 1), center=False):
        cr = canvas.cr
        cr.save()

        point_from = Vector.vectorize(point_from)

        text = text.strip()

        if center:
            text_size = CanvasUtils.get_text_size(canvas, text)

            point_from.x -= text_size.width / 2
            point_from.y += text_size.height / 2

        CanvasUtils.set_color(canvas, color)
        cr.move_to(point_from.x, point_from.y)
        cr.show_text(text)

        cr.restore()

    @staticmethod
    def draw_line(canvas, point_from, point_to, color=(0, 0, 0, 1), width=1):
        cr = canvas.cr
        cr.save()

        point_from = Vector.vectorize(point_from)
        point_to = Vector.vectorize(point_to)

        CanvasUtils.set_color(canvas, color)
        cr.set_line_width(width)

        cr.move_to(point_from.x, point_from.y)
        cr.line_to(point_to.x, point_to.y)
        cr.stroke()

        cr.restore()

    @staticmethod
    def draw_arrow(canvas, point_from, point_to, color=(0, 0, 0, 1), width=1):
        point_from = Vector.vectorize(point_from)
        point_to = Vector.vectorize(point_to)

        CanvasUtils.draw_line(canvas, point_from, point_to, color, width)

        vec_arrow = Vector.from_points(point_from, point_to)

        wing = vec_arrow.inverse().normalized().scaled(10)
        wing_right = wing.copy().rotate(45)
        wing_left = wing.copy().rotate(-45)

        CanvasUtils.draw_line(canvas, point_to, wing_right.add(point_to).to_point(), color, width)
        CanvasUtils.draw_line(canvas, point_to, wing_left.add(point_to).to_point(), color, width)

    @staticmethod
    def draw_rectangle(canvas, position, size, color=(0, 0, 0, 1), width=1, center=False):
        cr = canvas.cr
        cr.save()

        position = Vector.vectorize(position)
        size = Size.make_size(size)

        if center:
            position.x -= size.width / 2
            position.y -= size.height / 2

        CanvasUtils.set_color(canvas, color)
        cr.set_line_width(width)
        cr.rectangle(position.x, position.y, size.width, size.height)
        cr.stroke()

        cr.restore()


class Canvas(Gtk.EventBox):
    def __init__(self):
        super(Canvas, self).__init__()

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.fixed_wrapper = Gtk.Fixed()
        self.add(self.fixed_wrapper)

        self.bg_color = (0.8, 0.8, 0.8, 1.0)

        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect("draw", lambda canvas, cr: self._handle_draw(cr))

        self.mouse_click = None
        self.cr = None

        self.drawables = []

    def _handle_draw(self, cr):
        should_draw, rectangle = Gdk.cairo_get_clip_rectangle(cr)

        if should_draw:
            self._draw(cr, rectangle.width, rectangle.height)

    def _draw(self, cr, width, height):
        self.cr = cr

        CanvasUtils.set_color(self, self.bg_color)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        for drawable in self.drawables:
            drawable.draw(self)

    def add_drawable(self, drawable):
        self.drawables.append(drawable)
        self.redraw()

    def clear_drawables(self):
        self.drawables = []
        self.redraw()

    def set_background_color(self, r, g, b, a=1.0):
        self.bg_color = (r, g, b, a)
        self.redraw()

    def redraw(self):
        self.queue_draw()
