from enum import Enum


class DebuggerState(Enum):
    Started = 1
    BinaryLoaded = 2
    Running = 3


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


class ThreadState(Enum):
    Running = 1
    Stopped = 2
    Exited = 3


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


class TypeCategory(Enum):
    Any = -1
    Array = 1
    BlockPointer = 2
    Builtin = 4
    Class = 8
    ComplexFloat = 16
    ComplexInteger = 32
    Enumeration = 64
    Function = 128
    Invalid = 0
    MemberPointer = 256
    ObjCInterface = 1024
    ObjCObject = 512
    ObjCObjectPointer = 2048
    Other = -2147483648
    Pointer = 4096
    Reference = 8192
    Struct = 16384
    Typedef = 32768
    Union = 65536
    Vector = 131072
    String = 42

    def nice_name(self):
        name_mappings = {
            TypeCategory.Class: "class",
            TypeCategory.Struct: "struct"
        }
        return name_mappings.get(self, str(self))


class BasicTypeCategory(Enum):
    Bool = 20
    Char = 2
    Char16 = 8
    Char32 = 9
    Double = 23
    DoubleComplex = 26
    Float = 22
    FloatComplex = 25
    Half = 21
    Int = 12
    Int128 = 18
    Invalid = 0
    Long = 14
    LongDouble = 24
    LongDoubleComplex = 27
    LongLong = 16
    NullPtr = 31
    ObjCClass = 29
    ObjCID = 28
    ObjCSel = 30
    Other = 32
    Short = 10
    SignedChar = 3
    SignedWChar = 6
    UnsignedChar = 4
    UnsignedInt = 13
    UnsignedInt128 = 19
    UnsignedLong = 15
    UnsignedLongLong = 17
    UnsignedShort = 11
    UnsignedWChar = 7
    Void = 1
    WChar = 5
