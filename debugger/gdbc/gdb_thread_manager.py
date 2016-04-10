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


import gdb
from gdb_helper import GdbHelper


class GdbThreadManager(object):
    def __init__(self):
        self.gdb_helper = GdbHelper()
        self.thread_stack = []

    def get_inferior(self):
        return gdb.selected_inferior()

    def get_current_thread(self):
        return gdb.selected_thread()

    def get_thread(self, thread_id):
        return self.get_threads()[thread_id - 1]

    def get_threads(self):
        return sorted(self.get_inferior().threads(), key=lambda x: x.num)

    def switch_to_thread(self, thread_id):
        self.get_threads()[thread_id - 1].switch()

    def push_thread(self, new_thread_id):
        self.thread_stack.append(self.get_current_thread())
        self.switch_to_thread(new_thread_id)

    def pop_thread(self):
        self.switch_to_thread(self.thread_stack.pop().num)

    def get_thread_vars(self, thread_id=None):
        if thread_id is not None:
            self.push_thread(thread_id)

        locals = self.gdb_helper.get_locals()
        args = self.gdb_helper.get_args()

        if thread_id is not None:
            self.pop_thread()

        return (locals, args)
