# -*- coding: utf-8 -*-

import cairo
from gi.repository import Gtk
from gi.repository import Gdk

from drawing.drawable import DrawingUtils, Color
from drawing.memtoview import MemToViewTransformer
from drawing.mouse import MouseButtonState, MouseData
from drawing.vector import Vector
from enums import ProcessState


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
        """@type cr: cairo.Context"""

        self.drawables = []

    def _notify_handlers(self):
        for drawable in self.drawables:  # TODO: synchronize
            drawable.click_handler.handle_mouse_event(MouseData(self.mouse_button_state, self.mouse_position * (1 / self.zoom)))

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
        """
        @type debugger: lldbc.lldb_debugger.LldbDebugger
        """
        super(MemoryCanvas, self).__init__()

        self.debugger = debugger
        self.debugger.on_process_state_changed.subscribe(self._handle_process_state_change)
        self.debugger.on_frame_changed.subscribe(self._handle_frame_change)

        self.memtoview = MemToViewTransformer()
        self.active_frame = None

    def _handle_var_change(self, variable):
        self.redraw()

    def _handle_frame_change(self, frame):
        self._set_frame(frame)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Stopped:
            frame = self.debugger.thread_manager.get_current_frame()
            self._set_frame(frame)

    def _set_frame(self, frame):
        self.active_frame = frame

        for widget in self.fixed_wrapper.get_children():
            self.fixed_wrapper.remove(widget)

        for var in frame.variables:
            var.on_value_changed.subscribe(self._handle_var_change)

        self.set_drawables([self.memtoview.transform_frame(self, frame.variables)])


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
