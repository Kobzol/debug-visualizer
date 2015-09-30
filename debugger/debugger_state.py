# -*- coding: utf-8 -*-

import enum


class DebuggerState(enum.Enum):
    Started = 1
    BinaryLoaded = 2
    Running = 3
