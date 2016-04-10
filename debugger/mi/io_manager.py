# -*- coding: utf-8 -*-
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


import os
import threading

from debugger import util, debugger_api


class IOManager(debugger_api.IOManager):
    def __init__(self):
        super(IOManager, self).__init__()

        self.file_threads = []
        self.file_paths = []

    def _open_file(self, attribute, mode, file_path):
        setattr(self,
                attribute,
                open(file_path, mode, buffering=0))

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

        stdin, stdout, stderr = [util.create_pipe() for _ in xrange(3)]

        self.file_paths += (stdin, stdout, stderr)

        self._create_thread(["stdout", "r", stdout])
        self._create_thread(["stderr", "r", stderr])
        self._create_thread(["stdin", "w", stdin])

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

    def _create_thread(self, args):
        thread = threading.Thread(target=self._open_file, args=args)
        thread.daemon = True
        self.file_threads.append(thread)
