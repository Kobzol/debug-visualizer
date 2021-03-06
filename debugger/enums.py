#
#    Copyright (C) 2015-2016 Jakub Beranek
#
#    This file is part of Devi.
#
#    Devi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Devi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
#

from enum import Enum


class DebuggerState(Enum):
    """
    Represents debugger state.
    """
    Started = 1
    BinaryLoaded = 2
    Running = 3


class ProcessState(Enum):
    """
    Represents the debugged process' state.
    """
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
    """
    Represents thread state.
    """
    Running = 1
    Stopped = 2
    Exited = 3


class StopReason(Enum):
    """
    Reason why the debugged process stoped.
    """
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
    """
    Represents type of C/C++ type.
    """
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
    CString = 4097
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
    """
    Represents type of a primitive C/C++ type.
    """
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

    @staticmethod
    def is_char(type):
        """
        @type type: BasicTypeCategory
        @rtype: bool
        """
        return type in (BasicTypeCategory.Char,
                        BasicTypeCategory.Char16,
                        BasicTypeCategory.Char32,
                        BasicTypeCategory.SignedChar,
                        BasicTypeCategory.UnsignedChar,
                        BasicTypeCategory.SignedWChar,
                        BasicTypeCategory.UnsignedWChar,
                        BasicTypeCategory.WChar)
