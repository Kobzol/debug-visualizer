# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk

from drawing.drawable import DrawingUtils, Color
from drawing.memtoview import MemToViewTransformer
from drawing.mouse import MouseButtonState
from drawing.vector import Vector
from events import EventBroadcaster
from enums import ProcessState
from variable import Variable


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

        self.bg_color = Color(0.8, 0.8, 0.8, 1.0)

        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect("draw", lambda canvas, cr: self._handle_draw(cr))
        self.connect("button-press-event", lambda widget, button_event: self._handle_press(button_event, True))
        self.connect("button-release-event", lambda widget, button_event: self._handle_press(button_event, False))
        self.connect("motion-notify-event", lambda widget, move_event: self._handle_mouse_move(move_event))

        self.mouse_button_state = MouseButtonState.Up
        self.mouse_position = Vector(0, 0)

        self.zoom = 1.0
        self.zoom_limits = (0.5, 2.0)
        self.cr = None

        self.drawables = []

    def _notify_handlers(self):
        for drawable in self.drawables:  # TODO: synchronize
            drawable.click_handler.handle_mouse_event(self.mouse_button_state, self.mouse_position)

    def _handle_press(self, button_event, mouse_down):
        """
        @type button_event: Gdk.EventButton
        @type mouse_down: bool
        """
        self.mouse_button_state = MouseButtonState.Down if mouse_down else MouseButtonState.Up
        self._notify_handlers()
        self.redraw()

    def _handle_mouse_move(self, move_event):
        """
        @type move_event: Gdk.EventMotion
        """
        self.mouse_position = Vector(move_event.x, move_event.y)
        self.mouse_position *= (1 / self.zoom)

        self._notify_handlers()
        self.redraw()

    def _handle_draw(self, cr):
        should_draw, rectangle = Gdk.cairo_get_clip_rectangle(cr)

        if should_draw:
            self._draw(cr, rectangle.width, rectangle.height)

    def _draw(self, cr, width, height):
        """
        @type cr: cairo.Context
        @type width: int
        @type height: int
        """
        self.cr = cr

        self.cr.scale(1.0, 1.0)

        DrawingUtils.set_color(self, self.bg_color)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        self.cr.scale(self.zoom, self.zoom)

        for drawable in self.drawables:
            drawable.draw()

    def set_drawables(self, drawables):
        self.drawables = drawables
        self.redraw()

    def clear_drawables(self):
        self.drawables = []
        self.redraw()

    def set_background_color(self, color=Color()):
        self.bg_color = color
        self.redraw()

    def redraw(self):
        self.queue_draw()

    def zoom_in(self):
        """
        Zooms the canvas in by 10 %.
        """
        self.zoom += 0.1
        self.zoom = min(self.zoom, self.zoom_limits[1])
        self.redraw()

    def zoom_out(self):
        """
        Zooms the canvas out by 10 %.
        """
        self.zoom -= 0.1
        self.zoom = max(self.zoom, self.zoom_limits[0])
        self.redraw()

    def zoom_reset(self):
        """
        Resets the zoom of the canvas to 1.
        """
        self.zoom = 1.0
        self.redraw()


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

            parsed_vars = [Variable.from_lldb(var) for var in frame.vars]

            if frame.IsValid():
                self.set_drawables([self.memtoview.transform_frame(self, parsed_vars)])


class CanvasToolbarWrapper(Gtk.VBox):
    def __init__(self, canvas, toolbar):
        """
        Wrapper for a canvas with it's toolbar.
        @type canvas: Canvas
        @type toolbar: Gtk.Toolbar
        """
        super(CanvasToolbarWrapper, self).__init__()
        
        self.canvas = canvas
        self.toolbar = toolbar

        self.pack_start(self.toolbar, False, False, 0)
        self.pack_start(self.canvas, True, True, 0)
