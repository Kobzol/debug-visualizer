# -*- coding: utf-8 -*-

import os
import tempfile
import threading


class LldbIOManager(object):
    @staticmethod
    def create_pipe():
        tmpdir = tempfile.gettempdir()
        temp_name = next(tempfile._get_candidate_names())

        fifo = os.path.join(tmpdir, temp_name + ".fifo")

        os.mkfifo(fifo)

        return os.path.abspath(fifo)

    def __init__(self):
        self.file_threads = []
        self.file_paths = []

        self.stdin = None
        self.stdout = None
        self.stderr = None

    def _open_file(self, attribute, mode, file_path):
        setattr(self, attribute, open(file_path, mode, buffering=0))

    def _close_file(self, attribute):
        try:
            if getattr(self, attribute):
                getattr(self, attribute).close()
                setattr(self, attribute, None)
        except:
            pass

    def handle_io(self):
        if len(self.file_threads) > 0:
            return

        stdin, stdout, stderr = [LldbIOManager.create_pipe() for _ in xrange(3)]

        self.file_paths += (stdin, stdout, stderr)

        self.file_threads.append(threading.Thread(target=self._open_file, args=["stdin", "w", stdin]))
        self.file_threads.append(threading.Thread(target=self._open_file, args=["stdout", "r", stdout]))
        self.file_threads.append(threading.Thread(target=self._open_file, args=["stderr", "r", stderr]))

        map(lambda thread: thread.start(), self.file_threads)

        return (stdin, stdout, stderr)

    def stop_io(self):
        map(lambda thread: thread.join(), self.file_threads)

        self._close_file("stdin")
        self._close_file("stdout")
        self._close_file("stderr")

        self.file_threads = []

        for path in self.file_paths:
            try:
                os.remove(path)
            except:
                pass

        self.file_paths = []