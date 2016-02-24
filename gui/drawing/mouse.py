# -*- coding: utf-8 -*-

from gi.repository import Gdk

from enum import Enum

from vector import Vector


class ClickedState(Enum):
    Released = 1
    ReadyToPress = 2
    Pressed = 3


class PositionState(Enum):
    Inside = 1
    Outside = 2


class MouseButtonState(Enum):
    Up = 1
    Down = 2


class MouseData(object):
    def __init__(self, lb_state, rb_state, position):
        """
        @type lb_state: MouseButtonState
        @type rb_state: MouseButtonState
        @type position: drawing.vector.Vector
        """
        self.lb_state = lb_state
        self.rb_state = rb_state
        self.position = position

    def copy(self):
        return MouseData(self.lb_state, self.rb_state, self.position.copy())

    def __repr__(self):
        return "MouseData: {}, {}, {}".format(self.lb_state,
                                              self.rb_state,
                                              self.position)


class ClickHandler(object):
    def __init__(self, drawable):
        """
        Handles clicks.
        @type drawable: drawable.Drawable
        """
        self.drawable = drawable
        self.click_state = ClickedState.Released
        self.position_state = PositionState.Outside

        self.propagated_handlers = []

    def _is_point_inside(self, point):
        return self.drawable.get_rect().is_point_inside(point)

    def _handle_mouse_up(self, mouse_data):
        """
        @type mouse_data: MouseData
        """
        if self._is_point_inside(mouse_data.position):
            if self.click_state == ClickedState.Released:
                self.click_state = ClickedState.ReadyToPress
            if self.click_state == ClickedState.Pressed:
                self.drawable.on_mouse_click.notify(mouse_data)
                self.click_state = ClickedState.ReadyToPress
        else:
            self.click_state = ClickedState.Released

    def _handle_mouse_down(self, mouse_data):
        """
        @type mouse_data: MouseData
        """
        if self._is_point_inside(mouse_data.position):
            if self.click_state == ClickedState.ReadyToPress:
                self.click_state = ClickedState.Pressed

    def _handle_mouse_move(self, mouse_data):
        """
        @type mouse_data: MouseData
        """
        next_state = PositionState.Outside
        if self._is_point_inside(mouse_data.position):
            next_state = PositionState.Inside

        if self.position_state != next_state:
            if next_state == PositionState.Outside:
                self.drawable.on_mouse_leave.notify(mouse_data)
            else:
                self.drawable.on_mouse_enter.notify(mouse_data)

        self.position_state = next_state

    def propagate_handler(self, handler):
        """
        @type handler: ClickHandler
        """
        self.propagated_handlers.append(handler)

    def handle_mouse_event(self, mouse_data):
        """
        @type mouse_data: MouseData
        """
        if mouse_data.lb_state == MouseButtonState.Down:
            self._handle_mouse_down(mouse_data)
        elif mouse_data.lb_state == MouseButtonState.Up:
            self._handle_mouse_up(mouse_data)

        self._handle_mouse_move(mouse_data)

        for handler in self.propagated_handlers:
            handler.handle_mouse_event(mouse_data)


class TranslationHandler(object):
    def __init__(self, canvas):
        """
        Handles translation of canvas using right mouse dragging.
        @type canvas: canvas.Canvas
        """
        self.canvas = canvas
        self.mouse_state = MouseButtonState.Up
        self.position = Vector(0, 0)

    def set_drag_cursor(self):
        self.canvas.set_cursor(Gdk.Cursor.new(Gdk.CursorType.HAND1))

    def set_default_cursor(self):
        self.canvas.set_cursor(None)

    def handle_mouse_event(self, mouse_data):
        """
        @type mouse_data: MouseData
        """
        if self.mouse_state == MouseButtonState.Up:
            if mouse_data.rb_state == MouseButtonState.Down:
                self.set_drag_cursor()
        else:
            if mouse_data.rb_state == MouseButtonState.Up:
                self.set_default_cursor()
            else:
                diff = mouse_data.position - self.position
                self.canvas.translate_by(diff)

        self.position = mouse_data.position.copy()
        self.mouse_state = mouse_data.rb_state

    def is_dragging(self):
        return self.mouse_state == MouseButtonState.Down
