import enum


class DebuggerState(enum.IntEnum):
    Started = 1
    BinaryLoaded = 2
    Running = 3
    Exited = 4