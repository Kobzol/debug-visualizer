# -*- coding: utf-8 -*-

import logging
from threading import Event, Thread


class Logger(object):
    logger = None

    @staticmethod
    def init_logger(level):
        Logger.logger = logging.getLogger("debugger")
        Logger.logger.setLevel(level)

    @staticmethod
    def debug(message, *args, **kwargs):
        Logger.logger.debug(message, *args, **kwargs)

    @staticmethod
    def info(message, *args, **kwargs):
        Logger.logger.info(message, *args, **kwargs)


class RepeatTimer(Thread):
    def __init__(self, time, callback):
        """
        @type time: float
        @type callback: callable
        """
        Thread.__init__(self, target=self._callback)
        self.stop_event = Event()
        self.wait_time = time
        self.callback = callback
        self.daemon = True

    def _callback(self):
        while not self.stop_event.wait(self.wait_time):
            self.callback()

    def stop_repeating(self):
        self.stop_event.set()


class BadStateError(Exception):
    def __init__(self, required_state, current_state):
        self.required_state= required_state
        self.current_state = current_state


Logger.init_logger(logging.DEBUG)