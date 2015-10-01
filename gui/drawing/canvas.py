# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk
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
    def get_text_size(cr, text):
        size = cr.text_extents(text)

        return (size[2], size[3])   # (width, height)


class Canvas(Gtk.EventBox):
    def __init__(self):
        super(Canvas, self).__init__()

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.fixed_wrapper = Gtk.Fixed()
        self.value_entry = ValueEntry()
        self.fixed_wrapper.add(self.value_entry)
        self.add(self.fixed_wrapper)

        self.value_entry.hide()

        self.bg_color = (0.0, 0.8, 0.8, 1.0)

        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)

        self.connect("draw", self._handle_draw)

        self.mouse_click = None

    def _handle_draw(self, canvas, cr):
        should_draw, rectangle = Gdk.cairo_get_clip_rectangle(cr)

        if should_draw:
            self._draw(cr, rectangle.width, rectangle.height)

    def _draw(self, cr, width, height):
        cr.set_source_rgba(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
        cr.rectangle(0, 0, width, height)
        cr.fill()


    def draw_text(self, cr, text, x, y, color=(0, 0, 0, 1), center=False):
        cr.save()

        text = text.strip()

        if center:
            text_size = CanvasUtils.get_text_size(cr, text)

            x -= text_size[0] / 2
            y -= text_size[1] / 2

        cr.set_source_rgba(color[0], color[1], color[2], color[3])
        cr.move_to(x, y)
        cr.show_text(text)

        cr.restore()

    def draw_line(self, cr, point_from, point_to, color=(0, 0, 0, 1), width=1):
        cr.save()

        cr.set_source_rgba(color[0], color[1], color[2], color[3])
        cr.set_line_width(width)

        cr.move_to(point_from[0], point_from[1])
        cr.line_to(point_to[0], point_to[1])
        cr.stroke()

        cr.restore()

    def draw_arrow(self, cr, point_from, point_to, color=(0, 0, 0, 1), width=1):
        self.draw_line(cr, point_from, point_to, color, width)

        vec_arrow = Vector.from_points(point_from, point_to)

        wing = vec_arrow.inverse().normalized().scaled(10)
        wing_right = wing.copy().rotate(45)
        wing_left = wing.copy().rotate(-45)

        self.draw_line(cr, point_to, wing_right.add(point_to).to_point(), color, width)
        self.draw_line(cr, point_to, wing_left.add(point_to).to_point(), color, width)

    def show_value_entry(self, x, y):
        self.value_entry.set_visible(True)
        self.fixed_wrapper.move(self.value_entry, x, y)

    def hide_value_entry(self):
        self.value_entry.set_visible(False)

    def set_background_color(self, r, g, b, a=1.0):
        self.bg_color = (r, g, b, a)
        self.redraw()

    def redraw(self):
        self.queue_draw()
