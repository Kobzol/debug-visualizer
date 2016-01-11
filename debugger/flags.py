# -*- coding: utf-8 -*-

import inspect
from events import EventBroadcaster


class Flags(object):
    """
    Represents bitfield composed enums.

    Raises events when changed.
    """
    def __init__(self, enum_cls, initial_value=0):
        """
        @type enum_cls: enum class
        @type initial_value: int | enum instance
        """
        if not inspect.isclass(enum_cls):
            raise TypeError("parameter must be class")

        if isinstance(initial_value, enum_cls):
            initial_value = initial_value.value

        self.enum_cls = enum_cls
        self.value = initial_value

        self.on_value_changed = EventBroadcaster()

    def _check_cls(self, obj):
        if not isinstance(obj, self.enum_cls):
            raise TypeError("enum must be of class " + str(self.enum_cls))

    def set(self, value):
        """
        Sets the given value in the bitfield.
        @type value: enum instance
        """
        self._check_cls(value)

        old_value = self.value
        self.value |= (1 << value.value)
        self.on_value_changed.notify(self, Flags(self.enum_cls, old_value))

    def unset(self, value):
        """
        Unsets the given value in the bitfield.
        @type value: enum instance
        """
        self._check_cls(value)

        old_value = self.value
        self.value &= ~(1 << value.value)
        self.on_value_changed.notify(self, Flags(self.enum_cls, old_value))

    def is_set(self, value):
        """
        Checks whether the given value is set in the bitfield.
        @type value: enum instance
        @return: bool
        """
        self._check_cls(value)
        return (self.value & (1 << value.value)) != 0

    def get_value(self):
        """
        Returns the integer value of the whole bitfield.
        @return: int
        """
        return self.value

    def clear(self):
        """
        Clears the bitfield to 0 (effectively unsetting all flags).
        """
        old_value = self.value
        self.value = 0
        self.on_value_changed.notify(self, Flags(self.enum_cls, old_value))

    def __repr__(self):
        flags = "["

        for enum_val in self.enum_cls:
            if self.is_set(enum_val):
                flags += str(enum_val) + ", "

        if len(flags) > 1:
            flags = flags[:-2]

        return flags + "]"
