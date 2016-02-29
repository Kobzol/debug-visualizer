# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk

from debugger.debugee import Variable
from drawable import DrawingUtils, Color, LinearLayout,\
    LinearLayoutDirection, VariableContainer
from memtoview import MemToViewTransformer
from mouse import MouseButtonState, MouseData, TranslationHandler
from vector import Vector
from debugger.enums import ProcessState
from gui.gui_util import run_on_gui, require_gui_thread


class FixedGuiWrapper(Gtk.Fixed):
    def __init__(self):
        super(FixedGuiWrapper, self).__init__()

    def remove_all(self):
        for child in self.get_children():
            self.remove(child)

    def hide_all(self):
        for widget in self.get_children():
            widget.hide()


class LayeredDrawScheduler(object):
    def __init__(self, size):
        """
        @type size: int
        """
        self.size = size
        self.draw_actions = [[] for i in xrange(size)]

    @property
    def last_level(self):
        return self.size - 1

    def reset(self):
        self.draw_actions = [[] for i in xrange(self.size)]

    def register_action(self, level, action, *args, **kwargs):
        """
        @type level: int
        @type action: callable
        """
        self.draw_actions[level].append((action, args, kwargs))

    def invoke_actions(self):
        for level in self.draw_actions:
            for action in level:
                action[0](*action[1], **action[2])


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
        self.connect("button-press-event",
                     lambda widget, button_event:
                     self._handle_press(button_event, True))
        self.connect("button-release-event",
                     lambda widget, button_event:
                     self._handle_press(button_event, False))
        self.connect("motion-notify-event",
                     lambda widget, move_event:
                     self._handle_mouse_move(move_event))
        self.connect("scroll-event",
                     lambda widget, scroll_event:
                     self._handle_mouse_scroll(scroll_event))

        self.mouse_data = MouseData(MouseButtonState.Up,
                                    MouseButtonState.Up,
                                    Vector(0, 0))
        self.translation_handler = TranslationHandler(self)

        self.zoom = 1.0
        self.zoom_limits = (0.5, 2.0)
        self.translation = Vector(0, 0)
        self.cr = None
        """@type cr: cairo.Context"""

        self.drawables = []
        """@type drawables: list of drawable.Drawable"""
        self.drawable_registry = []
        """@type drawable_registry: list of drawable.Drawable"""

        self.tooltip_drawable = None
        self.first_draw = True

        self.draw_scheduler = LayeredDrawScheduler(3)

    def _notify_handlers(self):
        mouse_data = self.get_mouse_data()
        for drawable in self.get_drawables():  # TODO: synchronize
            drawable.click_handler.handle_mouse_event(mouse_data)
        self.translation_handler.handle_mouse_event(self.mouse_data)

    def _handle_press(self, button_event, mouse_down):
        """
        @type button_event: Gdk.EventButton
        @type mouse_down: bool
        """
        mouse_state = MouseButtonState.Up
        if mouse_down:
            mouse_state = MouseButtonState.Down

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

    def _handle_mouse_scroll(self, scroll_event):
        """
        @type scroll_event: Gdk.EventScroll
        """
        if scroll_event.direction == Gdk.ScrollDirection.UP:
            self.zoom_in()
        elif scroll_event.direction == Gdk.ScrollDirection.DOWN:
            self.zoom_out()

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

        self.draw_scheduler.reset()

        for drawable in self.get_drawables():
            if drawable:
                drawable.draw()

        self.draw_scheduler.invoke_actions()

    def get_mouse_data(self):
        """
        @rtype: drawing.mouse.MouseData
        """
        position = self.mouse_data.position - self.translation
        return MouseData(self.mouse_data.lb_state,
                         self.mouse_data.rb_state,
                         position * (1.0 / self.zoom))

    def get_drawables(self):
        """
        @rtype: list of drawing.drawable.Drawable
        """
        return self.drawables

    def set_drawables(self, drawables):
        self.drawables = drawables
        self.redraw()

    def clear_drawables(self):
        self.drawables = []
        self.drawable_registry = []

    def register_drawable(self, drawable):
        """
        Registers the given drawable in the canvas.
        @type drawable: drawable.Drawable
        """
        self.drawable_registry.append(drawable)

    def set_cursor(self, cursor):
        """
        @type cursor: Gdk.Cursor
        """
        self.get_window().set_cursor(cursor)

    def set_drawable_tooltip(self, drawable, text):
        """
        @type drawable: drawable.Drawable
        @type text: str
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


class MemoryModel(object):
    def __init__(self, canvas):
        """
        @type canvas: MemoryCanvas
        """
        self.canvas = canvas
        self.heap = []
        self.heap_wrapper = None
        self.stack_wrapper = None
        self.wrapper = None

    def get_drawable_by_pointer(self, pointer):
        """
        @type pointer: debugee.PointerVariable
        @rtype: drawing.drawable.Drawable | None
        """
        for drawable in self.canvas.drawable_registry:
            if isinstance(drawable, VariableContainer):
                var = drawable.variable
                if isinstance(var, Variable):
                    if var.address == pointer.value:
                        return drawable

        var = self.canvas.debugger.variable_manager.get_variable(
            "{{{}}}({})".format(
                pointer.target_type.name,
                pointer.value
            ))

        if var and var.address == pointer.value:
            drawable = self.canvas.memtoview.transform_var(var)
            self.heap_wrapper.add_child(drawable)
            self.canvas.redraw()

            return drawable
        else:
            return None

    def get_drawables(self):
        """
        @rtype: list of drawing.drawable.Drawable
        """
        if self.wrapper:
            return [self.wrapper]
        else:
            return []

    def prepare_gui(self, selected_frame=None):
        """
        @type selected_frame: debugee.Frame
        """
        self.wrapper = LinearLayout(self.canvas,
                                    LinearLayoutDirection.Horizontal,
                                    name="wrapper")

        self.stack_wrapper = LinearLayout(self.canvas,
                                          LinearLayoutDirection.Vertical)
        self.wrapper.add_child(self.stack_wrapper)

        self.heap_wrapper = LinearLayout(self.canvas,
                                         LinearLayoutDirection.Vertical)
        self.heap_wrapper.margin.left = 80
        self.wrapper.add_child(self.heap_wrapper)

        if selected_frame:
            v = self.canvas.debugger.thread_manager.get_frames_with_variables()
            for i, fr in enumerate(v):
                fr = self.canvas.memtoview.transform_frame(fr)
                fr.margin.bottom = 20
                self.stack_wrapper.add_child(fr)

            for var in selected_frame.variables:
                var.on_value_changed.subscribe(self.canvas._handle_var_change)


class MemoryCanvas(Canvas):
    def __init__(self, debugger):
        """
        @type debugger: debugger.debugger_api.Debugger
        """
        super(MemoryCanvas, self).__init__()

        self.debugger = debugger
        self.debugger.on_process_state_changed.subscribe(
            self._handle_process_state_change)
        self.debugger.on_frame_changed.subscribe(self._handle_frame_change)

        self.memtoview = MemToViewTransformer(self)
        self.memory_model = MemoryModel(self)

        self._rebuild(None)

    def _handle_var_change(self, variable):
        self.redraw()

    def _handle_frame_change(self, frame):
        self._rebuild(frame)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Stopped:
            location = self.debugger.file_manager.get_current_location()
            if location and len(location[0]) > 0 and location[1] > 0:
                frame = self.debugger.thread_manager.get_current_frame(False)
                self._rebuild(frame)

    def get_drawables(self):
        return self.memory_model.get_drawables()

    @require_gui_thread
    def _rebuild_gui(self, frame):
        """
        @type frame: debugee.Frame
        """
        self.clear_drawables()
        self.fixed_wrapper.remove_all()

        self.memory_model = MemoryModel(self)
        self.memory_model.prepare_gui(frame)

        self.redraw()

    def _rebuild(self, frame):
        run_on_gui(self._rebuild_gui, frame)


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
