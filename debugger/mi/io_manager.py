# -*- coding: utf-8 -*-

import os
import tempfile
import threading


class IOManager(object):
    def __init__(self):
        self.file_threads = []

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

    def handle_io(self, tty_master):
        tty_path = os.ttyname(tty_master)
        print(tty_path)

        self.stdin = open(tty_path, "w", buffering=0)
        self.stdout = open(tty_path, "r", buffering=0)
