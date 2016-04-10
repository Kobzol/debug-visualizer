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


from gi.repository import GObject

import inspect
import threading


def run_on_gui(function, *args, **kwargs):
    """
    @type function: callable
    """
    GObject.idle_add(lambda *x: function(*args, **kwargs))


def assert_is_gui_thread():
    func = inspect.currentframe().f_back.f_back.f_code

    if not isinstance(threading.current_thread(), threading._MainThread):
        raise Exception("Not on the main thread at {0} ({1}:{2})".format(
            func.co_name, func.co_filename, func.co_firstlineno))


def require_gui_thread(func):
    """
    @type func: callable
    @rtype: callable
    """
    def check(*args, **kwargs):
        assert_is_gui_thread()
        return func(*args, **kwargs)
    return check


def truncate(data, length, end=None):
    """
    Truncates the data string to the given length (inclusive).
    If end is given, the end is appended to the truncated input.
    The final length will be <= len, so end will not go over len.
    @type data: str
    @type length: int
    @type end: str
    @rtype: str
    """
    if end:
        end_len = len(end)
        trunc_length = length - end_len
        if trunc_length < 1:
            return end
        else:
            return data[:trunc_length] + end

    else:
        return data[:length]


class Cooldown(object):
    def __init__(self, value):
        """
        @type value: float
        """
        self.value = value
        self.delta = 0.0

    def update(self, delta):
        self.delta += delta

    def is_ready(self):
        return self.delta >= self.value

    def reset(self):
        self.delta = 0.0

    def reset_if_ready(self):
        if self.is_ready():
            self.reset()
            return True
        else:
            return False
