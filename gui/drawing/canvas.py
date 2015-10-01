# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk


class Canvas(Gtk.DrawingArea):
    def __init__(self):
        super(Canvas, self).__init__()

        self.cr = None

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.bg_color = (0.8, 0.8, 0.8, 1.0)

        self.connect("draw", self._handle_draw)

    def _handle_draw(self, canvas, cr):
        should_draw, rectangle = Gdk.cairo_get_clip_rectangle(cr)

        if should_draw:
            self._draw(cr, rectangle.width, rectangle.height)

    def _draw(self, cr, width, height):
        cr.set_source_rgba(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
        cr.rectangle(0, 0, width, height)
        cr.fill()

    def set_background_color(self, r, g, b, a=1.0):
        self.bg_color = (r, g, b, a)
        self.redraw()

    def redraw(self):
        self.queue_draw()