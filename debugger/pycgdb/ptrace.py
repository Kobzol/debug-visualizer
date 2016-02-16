# -*- coding: utf-8 -*-

import ctypes
import os

lib = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'libptrace.so'))

PTRACE_TRACEME = 0
PTRACE_PEEKTEXT = 1
PTRACE_POKETEXT = 4
PTRACE_CONT = 7
PTRACE_SINGLESTEP = 9
PTRACE_GETREGS = 12
PTRACE_SETREGS = 13


class UserRegs64(ctypes.Structure):
    _fields_ = [
        ("r15", ctypes.c_ulonglong),
        ("r14", ctypes.c_ulonglong),
        ("r13", ctypes.c_ulonglong),
        ("r12", ctypes.c_ulonglong),
        ("rbp", ctypes.c_ulonglong),
        ("rbx", ctypes.c_ulonglong),
        ("r11", ctypes.c_ulonglong),
        ("r10", ctypes.c_ulonglong),
        ("r9", ctypes.c_ulonglong),
        ("r8", ctypes.c_ulonglong),
        ("rax", ctypes.c_ulonglong),
        ("rcx", ctypes.c_ulonglong),
        ("rdx", ctypes.c_ulonglong),
        ("rsi", ctypes.c_ulonglong),
        ("rdi", ctypes.c_ulonglong),
        ("orig_rax", ctypes.c_ulonglong),
        ("rip", ctypes.c_ulonglong),
        ("cs", ctypes.c_ulonglong),
        ("eflags", ctypes.c_ulonglong),
        ("rsp", ctypes.c_ulonglong),
        ("ss", ctypes.c_ulonglong),
        ("fs_base", ctypes.c_ulonglong),
        ("gs_base", ctypes.c_ulonglong),
        ("ds", ctypes.c_ulonglong),
        ("es", ctypes.c_ulonglong),
        ("fs", ctypes.c_ulonglong),
        ("gs", ctypes.c_ulonglong)
    ]


class UserRegs32(ctypes.Structure):
    _fields_ = [
        ("ebx", ctypes.c_long),
        ("ecx", ctypes.c_long),
        ("edx", ctypes.c_long),
        ("esi", ctypes.c_long),
        ("edi", ctypes.c_long),
        ("ebp", ctypes.c_long),
        ("eax", ctypes.c_long),
        ("xds", ctypes.c_long),
        ("xes", ctypes.c_long),
        ("xfs", ctypes.c_long),
        ("xgs", ctypes.c_long),
        ("orig_eax", ctypes.c_long),
        ("eip", ctypes.c_long),
        ("xcs", ctypes.c_long),
        ("eflags", ctypes.c_long),
        ("esp", ctypes.c_long),
        ("xss", ctypes.c_long),
    ]


def ptrace(request, pid=0, addr=0, data=0):
    return lib.py_ptrace(request, pid, addr, data)


def ptrace_getregs(pid, bit32=True):
    regs = UserRegs32()

    if not bit32:
        regs = UserRegs64()

    regs_p = ctypes.pointer(regs)
    assert lib.py_ptrace(PTRACE_GETREGS, pid, 0, regs_p) >= 0
    return regs_p.contents


def ptrace_setregs(pid, regs):
    regs_p = ctypes.pointer(regs)
    return lib.py_ptrace(PTRACE_SETREGS, pid, 0, regs_p) >= 0


def ptrace_get_instruction(pid, address):
    return lib.py_ptrace(PTRACE_PEEKTEXT, pid, address)


def ptrace_set_instruction(pid, address, instruction):
    return lib.py_ptrace(PTRACE_POKETEXT, pid, address, instruction) >= 0


def get_error():
    return lib.py_errno()
