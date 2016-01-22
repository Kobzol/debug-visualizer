# -*- coding: utf-8 -*-

from enum import Enum
from events import EventBroadcaster


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
        if mouse_data.state == MouseButtonState.Down:
            self._handle_mouse_down(mouse_data)
        elif mouse_data.state == MouseButtonState.Up:
            self._handle_mouse_up(mouse_data)

        self._handle_mouse_move(mouse_data)

        for handler in self.propagated_handlers:
            handler.handle_mouse_event(mouse_data)
