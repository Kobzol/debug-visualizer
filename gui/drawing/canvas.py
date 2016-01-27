# -*- coding: utf-8 -*-

import cairo
from gi.repository import Gtk
from gi.repository import Gdk

from drawing.drawable import DrawingUtils, Color
from drawing.memtoview import MemToViewTransformer
from drawing.mouse import MouseButtonState, MouseData, TranslationHandler
from drawing.vector import Vector
from enums import ProcessState
from gui_util import run_on_gui, require_gui_thread
from util import EventBroadcaster


class ValueEntry(Gtk.Frame):
    @require_gui_thread
    def __init__(self):
        Gtk.Frame.__init__(self)

        self.set_label_align(0.0, 0.0)

        self.box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box.set_margin_bottom(5)
        self.box.set_margin_left(2)
        self.text_entry = Gtk.Entry()
        self.confirm_button = Gtk.Button(label="Set")

        self.get_style_context().add_class("value-entry")

        self.box.pack_start(self.text_entry, False, False, 0)
        self.box.pack_start(self.confirm_button, False, False, 5)
        self.add(self.box)
        self.show_all()

        self.confirm_button.connect("clicked", lambda btn: self._handle_confirm_click())

        self.on_value_entered = EventBroadcaster()

    @require_gui_thread
    def set_value(self, value):
        """
        @type value: str
        """
        self.text_entry.set_text(value)

    def _handle_confirm_click(self):
        value = self.text_entry.get_text()
        self.set_value("")

        self.on_value_entered.notify(value)
        self.hide()

    def reset(self):
        self.on_value_entered.clear()

    def init(self, title, text, listener):
        """
        @type title: basestring
        @type text: basestring
        @type listener: function
        """
        self.set_label(title)
        self.text_entry.set_text(text)
        self.on_value_entered.subscribe(listener)


class FixedGuiWrapper(Gtk.Fixed):
    def __init__(self):
        super(FixedGuiWrapper, self).__init__()

        self.text_entry = ValueEntry()
        self.put(self.text_entry, 0, 0)
        self.text_entry.hide()

    def hide_all(self):
        for widget in self.get_children():
            widget.hide()

    def reset_widget_to(self, widget, position, *args):
        """
        @type widget: Gtk.Widget
        @type position: drawing.vector.Vector
        """
        self.move(widget, position.x, position.y)
        widget.reset()
        widget.init(*args)

    def toggle_widget_to(self, widget, position, *args):
        if widget.props.visible:
            widget.hide()
        else:
            self.reset_widget_to(widget, position, *args)
            widget.show()


class Canvas(Gtk.EventBox):
    def __init__(self):
        super(Canvas, self).__init__()

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.fixed_wrapper = FixedGuiWrapper()
        self.add(self.fixed_wrapper)

        self.bg_color = Color(0.8, 0.8, 0.8, 1.0)

        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect("draw", lambda canvas, cr: self._handle_draw(cr))
        self.connect("button-press-event", lambda widget, button_event: self._handle_press(button_event, True))
        self.connect("button-release-event", lambda widget, button_event: self._handle_press(button_event, False))
        self.connect("motion-notify-event", lambda widget, move_event: self._handle_mouse_move(move_event))

        self.mouse_data = MouseData(MouseButtonState.Up, MouseButtonState.Up, Vector(0, 0))
        self.translation_handler = TranslationHandler(self)

        self.zoom = 1.0
        self.zoom_limits = (0.5, 2.0)
        self.translation = Vector(0, 0)
        self.cr = None
        """@type cr: cairo.Context"""

        self.drawables = []
        self.tooltip_drawable = None
        self.first_draw = True

    def _notify_handlers(self):
        mouse_data = MouseData(self.mouse_data.lb_state, self.mouse_data.rb_state, self.mouse_data.position * (1 / self.zoom))
        for drawable in self.drawables:  # TODO: synchronize
            drawable.click_handler.handle_mouse_event(mouse_data.copy())
        self.translation_handler.handle_mouse_event(self.mouse_data.copy())

    def _handle_press(self, button_event, mouse_down):
        """
        @type button_event: Gdk.EventButton
        @type mouse_down: bool
        """
        mouse_state = MouseButtonState.Down if mouse_down else MouseButtonState.Up
        if button_event.button == 1:  # left button
            self.mouse_data.lb_state = mouse_state
        elif button_event.button == 3:  # right button
            self.mouse_data.rb_state = mouse_state

        self._notify_handlers()
        self.redraw()

    def _handle_mouse_move(self, move_event):
        """
        @type move_event: Gdk.EventMotion
        """
        self.mouse_data.position = Vector(move_event.x, move_event.y)
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
        if self.first_draw:
            self.fixed_wrapper.hide_all()
            self.first_draw = False

        self.cr = cr

        self.cr.scale(1.0, 1.0)

        DrawingUtils.set_color(self, self.bg_color)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        self.cr.translate(self.translation.x, self.translation.y)

        self.cr.scale(self.zoom, self.zoom)

        for drawable in self.drawables:
            drawable.draw()

    def set_drawables(self, drawables):
        self.drawables = drawables
        self.redraw()

    def clear_drawables(self):
        self.drawables = []
        self.redraw()

    def set_cursor(self, cursor):
        """
        @type cursor: Gdk.Cursor
        """
        self.get_window().set_cursor(cursor)

    def set_drawable_tooltip(self, drawable, text):
        """
        @type drawable: drawable.Drawable
        @type text: basestring
        """
        if text is None and drawable != self.tooltip_drawable:
            return

        self.tooltip_drawable = drawable
        self.set_tooltip_text(text)

    def set_background_color(self, color=Color()):
        self.bg_color = color
        self.redraw()

    def translate_by(self, vector):
        """
        Translates the canvas by the given vector.
        @type vector: Vector
        """
        self.translation += vector

    def reset_translation(self):
        """
        Resets the translation of the canvas.
        """
        self.translation = Vector(0, 0)
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

        self.memtoview = MemToViewTransformer(self)
        self.active_frame = None

    def _handle_var_change(self, variable):
        self.redraw()

    def _handle_frame_change(self, frame):
        self._set_frame(frame)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Stopped:
            frame = self.debugger.thread_manager.get_current_frame()
            self._set_frame(frame)

    @require_gui_thread
    def _set_frame_gui(self, frame):
        self.active_frame = frame

        self.fixed_wrapper.hide_all()

        for var in frame.variables:
            var.on_value_changed.subscribe(self._handle_var_change)

        self.set_drawables([self.memtoview.transform_frame(frame)])

    def _set_frame(self, frame):
        run_on_gui(self._set_frame_gui, frame)


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
