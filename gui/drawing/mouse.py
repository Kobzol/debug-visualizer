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


class ClickHandler(object):
    def __init__(self, drawable):
        """
        Handles clicks.
        @type drawable: drawable.Drawable
        """
        self.drawable = drawable
        self.state = ClickedState.Released

        self.propagated_handlers = []
        self.on_mouse_click = EventBroadcaster()

    def _is_point_inside(self, point):
        return self.drawable.get_bbox().is_point_inside(point)

    def _handle_mouse_up(self, point):
        """
        @type point: drawing.vector.Vector
        """
        if self._is_point_inside(point):
            if self.state == ClickedState.Released:
                self.state = ClickedState.ReadyToPress
            if self.state == ClickedState.Pressed:
                self.on_mouse_click.notify(point)
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

    def handle_mouse_event(self, mouse_state, mouse_position):
        if mouse_state == MouseButtonState.Down:
            self._handle_mouse_down(mouse_position)
        elif mouse_state == MouseButtonState.Up:
            self._handle_mouse_up(mouse_position)
