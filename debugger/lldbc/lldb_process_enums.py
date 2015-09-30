from enum import Enum


class ProcessState(Enum):
    Attaching = 3
    Connected = 2
    Crashed = 8
    Detached = 9
    Exited = 10
    Invalid = 0
    Launching = 4
    Running = 6
    Stepping = 7
    Stopped = 5
    Suspended = 11
    Unloaded = 1


class StopReason(Enum):
    Breakpoint = 3
    Exception = 6
    Exec = 7
    Invalid = 0
    NoReason = 1
    PlanComplete = 8
    Signal = 5
    ThreadExiting = 9
    Trace = 2
    Watchpoint = 4
