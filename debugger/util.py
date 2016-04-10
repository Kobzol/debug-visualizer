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

# -*- coding: utf-8 -*-

import Queue
import logging
import inspect
import os
import tempfile
import threading

from threading import Event, Thread

import time

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_pipe():
    """
    Creates a named FIFO pipe in the temp dir.
    @rtype: str
    """
    tmpdir = tempfile.gettempdir()
    temp_name = next(tempfile._get_candidate_names())

    fifo = os.path.join(tmpdir, temp_name + ".fifo")

    os.mkfifo(fifo)

    return os.path.abspath(fifo)


def get_root_path(path):
    """
    @type path: str
    @rtype: str
    """
    return os.path.join(root_path, path)


class Logger(object):
    """
    Helper class for logging.
    """
    logger = None

    @staticmethod
    def init_logger(level):
        logging.basicConfig()
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
        self.name = "RepeatTimer with period {}".format(time)

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


class Flags(object):
    """
    Represents bitfield composed enums.

    Raises events when changed.
    """
    def __init__(self, enum_cls, initial_value=0):
        """
        @type enum_cls: enum class
        @type initial_value: int | enum instance
        """
        if not inspect.isclass(enum_cls):
            raise TypeError("parameter must be class")

        if isinstance(initial_value, enum_cls):
            initial_value = initial_value.value

        self.enum_cls = enum_cls
        self.value = initial_value

        self.on_value_changed = EventBroadcaster()

    def _check_cls(self, obj):
        if not isinstance(obj, self.enum_cls):
            raise TypeError("enum must be of class " + str(self.enum_cls))

    def set(self, value):
        """
        Sets the given value in the bitfield.
        @type value: enum instance
        """
        self._check_cls(value)

        old_value = self.value
        self.value |= (1 << value.value)
        self.on_value_changed.notify(self, Flags(self.enum_cls, old_value))

    def unset(self, value):
        """
        Unsets the given value in the bitfield.
        @type value: enum instance
        """
        self._check_cls(value)

        old_value = self.value
        self.value &= ~(1 << value.value)
        self.on_value_changed.notify(self, Flags(self.enum_cls, old_value))

    def is_set(self, value):
        """
        Checks whether the given value is set in the bitfield.
        @type value: enum instance
        @rtype: bool
        """
        self._check_cls(value)
        return (self.value & (1 << value.value)) != 0

    def get_value(self):
        """
        Returns the integer value of the whole bitfield.
        @rtype: int
        """
        return self.value

    def clear(self):
        """
        Clears the bitfield to 0 (effectively unsetting all flags).
        """
        old_value = self.value
        self.value = 0
        self.on_value_changed.notify(self, Flags(self.enum_cls, old_value))

    def __repr__(self):
        flags = "["

        for enum_val in self.enum_cls:
            if self.is_set(enum_val):
                flags += str(enum_val) + ", "

        if len(flags) > 1:
            flags = flags[:-2]

        return flags + "]"


class EventBroadcaster(object):
    """
    Object that broadcasts event to it's listeners.

    Evety broadcaster represents a single event type.
    """
    def __init__(self):
        self.listeners = []

    def notify(self, *args, **kwargs):
        """
        Notifies all listeners that an event has occured.
        @param args: arbitraty arguments that will be passed to the listeners
        """
        map(lambda listener: listener(*args, **kwargs), self.listeners)

    def subscribe(self, listener):
        """
        Subscribes an event listener, who will receive events from the
        broadcaster.
        @type listener: function
        """
        self.listeners.append(listener)

    def unsubscribe(self, listener):
        """
        Unsubscribes an event listener.
        It will no longer receive events after he unsubscribes.
        @param listener: function
        """
        self.listeners.remove(listener)

    def clear(self):
        """
        Removes all event listeners.
        """
        self.listeners = []

    def redirect(self, broadcaster):
        """
        Redirects this broadcaster to the given broadcaster.

        All events fired by this broadcaster will be also delivered to the
        given broadcaster.
        @type broadcaster: EventBroadcaster
        """
        self.subscribe(broadcaster.notify)

    def __call__(self, *args, **kwargs):
        self.notify(*args, **kwargs)


class Profiler(object):
    def __init__(self, name=""):
        self.name = name
        self.start = 0
        self.fn_info = None

    def __enter__(self):
        func = inspect.currentframe().f_back.f_code
        self.fn_info = "{}:{}".format(func.co_filename, func.co_firstlineno)
        self.start = time.clock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.clock() - self.start
        if self.name:
            print("Profiler {} took {} s".format(self.name, elapsed_time))
        else:
            print(
                "Profiler at {} took {} s".format(self.fn_info, elapsed_time))


class Worker(Thread):
    WORKER_ID = 0

    def __init__(self):
        super(Worker, self).__init__(target=self._do_work)
        self.jobs = Queue.Queue()
        self.lock = threading.Lock()
        self.stop = False
        self.daemon = True
        self.name = "Worker {}".format(Worker.WORKER_ID)
        Worker.WORKER_ID += 1

    def stop(self):
        self.stop = True
        self.jobs.put((lambda: 0, [], None))

    def add_job(self, fn, args, callback):
        """
        @type fn: callable
        @type args: list of object
        @type callback: callable
        """
        self.jobs.put((fn, args, callback))

    def _do_work(self):
        while not self.stop:
            job = self.jobs.get()
            job[0](*job[1])
            if job[2]:
                job[2]()


Logger.init_logger(logging.DEBUG)
