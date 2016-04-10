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


class GdbBreakpointManager(object):
    def __init__(self, before_bp, after_bp):
        self.before_bp = before_bp
        self.after_bp = after_bp
        gdb.events.stop.connect(self.handle_break)

        self.breakpoints = []

    def handle_break(self, stop_event):
        self.before_bp(stop_event)

        callback = None

        for bp, cb in self.breakpoints:
            if bp in stop_event.breakpoints:
                callback = cb
                break

        if callback:
            cb(stop_event)  # inspecting callback, continue execution
            self.after_bp(stop_event, True)
        else:
            self.after_bp(stop_event, False)

    def add_breakpoint(self, location, callback=None):
        self.breakpoints.append((gdb.Breakpoint(location, internal=True),
                                 callback))

    def remove_breakpoint(self, location):
        for bp, callback in self.breakpoints:
            if bp.location == location:
                bp.delete()

        self.breakpoints = [bp for bp in self.breakpoints if
                            bp[0].location != location]

    def remove_all_breakpoints(self):
        for bp, callback in self.breakpoints:
            bp.delete()

        self.breakpoints = []
