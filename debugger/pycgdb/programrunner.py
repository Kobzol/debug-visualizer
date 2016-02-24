# -*- coding: utf-8 -*-

import os
import ptrace
import Queue
import signal
import threading
import traceback

from debugger.enums import ProcessState
from debugger.util import EventBroadcaster


class ProcessExitException(BaseException):
    pass


class ProgramRunner(object):
    def __init__(self, debugger, file, *args):
        self.debugger = debugger
        self.file = os.path.abspath(file)
        self.args = args
        self.parent_thread = None
        self.on_signal = EventBroadcaster()
        self.msg_queue = Queue.Queue()
        self.child_pid = None
        self.last_signal = None

    def run(self):
        assert not self.parent_thread

        self.parent_thread = threading.Thread(target=self._start_process)
        self.parent_thread.start()

    def exec_step_single(self):
        self._add_queue_command("step-single")

    def exec_continue(self):
        self._add_queue_command("continue")

    def exec_interrupt(self):
        try:
            os.kill(self.child_pid, signal.SIGUSR1)
            return True
        except:
            return False

    def exec_kill(self):
        try:
            os.kill(self.child_pid, signal.SIGKILL)
            return True
        except:
            return False

    def _add_queue_command(self, cmd):
        self.msg_queue.put(cmd)

    def _start_process(self):
        child_pid = os.fork()

        if child_pid:
            self.child_pid = child_pid
            self._parent()
        else:
            self._child()

    def _child(self):
        if ptrace.ptrace(ptrace.PTRACE_TRACEME) < 0:
            raise Exception()

        os.execl(self.file, self.file, *self.args)
        exit(0)

    def _parent(self):
        try:
            while True:
                pid, status = os.waitpid(self.child_pid, os.WNOHANG)

                if pid != 0:
                    self._handle_child_status(status)

                try:
                    command = self.msg_queue.get(True, 0.1)
                    self._handle_command(self.child_pid, status, command)
                except Queue.Empty:
                    pass
                except:
                    traceback.print_exc()
        except OSError:
            self.on_signal.notify(ProcessState.Exited)
        except ProcessExitException:
            pass
        except:
            traceback.print_exc()

        self.child_pid = None
        self.parent_thread = None

    def _handle_child_status(self, status):
        if os.WIFSTOPPED(status):
            self._on_stop(status)
        elif os.WIFEXITED(status):
            self.on_signal.notify(ProcessState.Exited,
                                  os.WTERMSIG(status),
                                  os.WEXITSTATUS(status))
            raise ProcessExitException()

    def _handle_command(self, pid, status, command):
        if command == "continue":
            self._do_continue(pid)
        elif command == "step-single":
            self._do_step_single(pid)

    def _on_stop(self, status):
        self.last_signal = os.WSTOPSIG(status)
        self.debugger.breakpoint_manager.set_breakpoints(self.child_pid)

        self.on_signal.notify(ProcessState.Stopped, self.last_signal)

    def _continue_after_breakpoint(self, exec_continue):
        pid = self.child_pid
        regs = ptrace.ptrace_getregs(pid)
        orig_address = regs.eip - 1
        if self.debugger.breakpoint_manager.has_breakpoint_for_address(
                orig_address):
            self.debugger.breakpoint_manager.restore_instruction(pid,
                                                                 orig_address)
            regs.eip -= 1
            assert ptrace.ptrace_setregs(pid, regs)
            self._do_step_single(pid)
            pid, status = os.waitpid(pid, 0)
            self.debugger.breakpoint_manager.set_breakpoints(pid)

            if exec_continue:
                self.exec_continue()
            else:
                self._handle_child_status(status)
            return True
        else:
            return False

    def _do_continue(self, pid):
        if self.last_signal == 5:   # sigtrap
            if self._continue_after_breakpoint(True):
                return

        ptrace.ptrace(ptrace.PTRACE_CONT, pid)

    def _do_step_single(self, pid):
        if self.last_signal == 5:   # sigtrap
            if self._continue_after_breakpoint(False):
                return

        ptrace.ptrace(ptrace.PTRACE_SINGLESTEP, pid)
