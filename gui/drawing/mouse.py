# -*- coding: utf-8 -*-

from enum import Enum
from events import EventBroadcaster


class ClickedState(Enum):
    Released = 0
    ReadyToPress = 1
    Pressed = 2


class MouseButtonState(Enum):
    Up = 1
    Down = 2


class MouseData(object):
    def __init__(self, state, position):
        """
        @type state: MouseButtonState
        @type position: drawing.vector.Vector
        """
        self.state = state
        self.position = position


class ClickHandler(object):
    def __init__(self, drawable):
        """
        Handles clicks.
        @type drawable: drawable.Drawable
        """
        self.drawable = drawable
        self.state = ClickedState.Released

        self.propagated_handlers = []

    def _is_point_inside(self, point):
        return self.drawable.get_rect().is_point_inside(point)

    def _handle_mouse_up(self, point):
        """
        @type point: drawing.vector.Vector
        """
        if self._is_point_inside(point):
            if self.state == ClickedState.Released:
                self.state = ClickedState.ReadyToPress
            if self.state == ClickedState.Pressed:
                self.drawable.on_mouse_click(point)
                self.state = ClickedState.ReadyToPress
        else:
            self.state = ClickedState.Released

        for handler in self.propagated_handlers:
            handler._handle_mouse_up(point)

    def _handle_mouse_down(self, point):
        """
        @type point: drawing.vector.Vector
        """
        if self._is_point_inside(point):
            if self.state == ClickedState.ReadyToPress:
                self.state = ClickedState.Pressed

        for handler in self.propagated_handlers:
            handler._handle_mouse_down(point)

    def propagate_handler(self, handler):
        """
        @type handler: ClickHandler
        """
        self.propagated_handlers.append(handler)

    def handle_mouse_event(self, mouse_data):
        """
        @type mouse_data: MouseData
        """
        if mouse_data.state == MouseButtonState.Down:
            self._handle_mouse_down(mouse_data.position)
        elif mouse_data.state == MouseButtonState.Up:
            self._handle_mouse_up(mouse_data.position)
