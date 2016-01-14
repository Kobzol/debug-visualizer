import traceback

import signal
import Queue
import os
import threading

import ptrace
from enums import ProcessState
from events import EventBroadcaster


class ProcessExitException(BaseException):
    pass


class ProgramRunner(object):
    def __init__(self, file, *args):
        self.file = os.path.abspath(file)
        self.args = args
        self.parent_thread = None
        self.on_signal = EventBroadcaster()
        self.msg_queue = Queue.Queue()
        self.child_pid = None

    def run(self):
        assert not self.parent_thread

        self.parent_thread = threading.Thread(target=self._start_process)
        self.parent_thread.start()

    def exec_step_single(self):
        self.msg_queue.put("step-single")

    def exec_continue(self):
        self.msg_queue.put("continue")

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
                    print(traceback.format_exc())
        except OSError:
            self.on_signal.notify(ProcessState.Exited)
        except ProcessExitException:
            pass
        except:
            print(traceback.format_exc())

        self.child_pid = None
        self.parent_thread = None

    def _handle_child_status(self, status):
        if os.WIFSTOPPED(status):
            self.on_signal.notify(ProcessState.Stopped)
        elif os.WIFEXITED(status):
            self.on_signal.notify(ProcessState.Exited)
            raise ProcessExitException()

    def _handle_command(self, pid, status, command):
        result = 0

        if command == "continue":
            result = ptrace.ptrace(ptrace.PTRACE_CONT, pid)
        elif command == "step-single":
            result = ptrace.ptrace(ptrace.PTRACE_SINGLESTEP, pid)

        if result < 0:
            print(ptrace.get_error())
