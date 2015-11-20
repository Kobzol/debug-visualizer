# -*- coding: utf-8 -*-

from threading import Event,Thread


class RepeatTimer(Thread):
    def __init__(self, time, callback):
        """
        @type time: float
        @type callback: callable
        """
        Thread.__init__(self, target=self._callback)
        self.stop = Event()
        self.wait_time = time
        self.callback = callback
        self.daemon = True

    def _callback(self):
        while not self.stop.wait(self.wait_time):
            self.callback()

    def stop(self):
        self.stop.set()
