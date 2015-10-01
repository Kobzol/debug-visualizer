# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk

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

        self.connect("draw", self._handle_draw)

    def _handle_draw(self, canvas, cr):
        should_draw, rectangle = Gdk.cairo_get_clip_rectangle(cr)

        if should_draw:
            self._draw(cr, rectangle.width, rectangle.height)

    def _draw(self, cr, width, height):
        cr.set_source_rgba(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
        cr.rectangle(0, 0, width, height)
        cr.fill()

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