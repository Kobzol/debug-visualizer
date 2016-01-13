# -*- coding: utf-8 -*-

import logging
from threading import Event, Thread


class Logger(object):
    """
    Helper class for logging.
    """
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
    """
    Thread that repeatedly calls the given function on a timer.
    Lasts until cancelled.
    """
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
        while self.stop_event and not self.stop_event.wait(self.wait_time):
            self.callback()

    def stop_repeating(self):
        """
        Stops the thread.
        """
        self.stop_event.set()


class Dispatcher(object):
    """
    Helper class for dynamically dispatching methods on a given object.

    The functions are invoked by name.
    """
    @staticmethod
    def dispatch(root_object, properties=None, arguments=None):
        target_prop = root_object

        if properties is None:
            properties = []

        if arguments is not None and not isinstance(arguments, (list, tuple)):
            arguments = [arguments]

        for prop in properties:
            target_prop = getattr(target_prop, prop)

        if hasattr(target_prop, "__call__"):
            if arguments is not None:
                result = target_prop(*arguments)
            else:
                result = target_prop()

            return result
        else:
            return target_prop


class BadStateError(Exception):
    """
    Exception that represents that an invalid state was encountered.
    """
    def __init__(self, required_state, current_state):
        self.required_state = required_state
        self.current_state = current_state


Logger.init_logger(logging.DEBUG)