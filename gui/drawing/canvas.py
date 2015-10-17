# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk

from drawing.drawable import DrawingUtils
from drawing.memtoview import MemToViewTransformer
from events import EventBroadcaster
from enums import ProcessState


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

        DrawingUtils.set_color(self, self.bg_color)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        for drawable in self.drawables:
            drawable.draw(self)

    def set_drawables(self, drawables):
        self.drawables = drawables
        self.redraw()

    def clear_drawables(self):
        self.drawables = []
        self.redraw()

    def set_background_color(self, r, g, b, a=1.0):
        self.bg_color = (r, g, b, a)
        self.redraw()

    def redraw(self):
        self.queue_draw()


class MemoryCanvas(Canvas):
    def __init__(self, debugger):
        super(MemoryCanvas, self).__init__()

        self.debugger = debugger
        self.debugger.on_process_state_changed.subscribe(self._handle_process_state_change)

        self.memtoview = MemToViewTransformer()

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Stopped:
            thread = self.debugger.thread_manager.get_current_thread()
            frame = thread.GetSelectedFrame()

            if frame.IsValid():
                self.set_drawables([self.memtoview.transform_frame(frame.vars)])
