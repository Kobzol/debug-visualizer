# -*- coding: utf-8 -*-

import inspect
from events import EventBroadcaster


class Flags(object):
    def __init__(self, enum_cls, initial_value=0):
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
        self._check_cls(value)

        old_value = self.value
        self.value |= (1 << value.value)
        self.on_value_changed.notify(self, old_value)

    def unset(self, value):
        self._check_cls(value)

        old_value = self.value
        self.value &= ~(1 << value.value)
        self.on_value_changed.notify(self, old_value)

    def is_set(self, value):
        self._check_cls(value)
        return (self.value & (1 << value.value)) != 0

    def get_value(self):
        return self.value

    def clear(self):
        old_value = self.value
        self.value = 0
        self.on_value_changed.notify(self, old_value)

    def __repr__(self):
        flags = "["

        for enum_val in self.enum_cls:
            if self.is_set(enum_val):
                flags += str(enum_val) + ", "

        if len(flags) > 1:
            flags = flags[:-2]

        return flags + "]"
