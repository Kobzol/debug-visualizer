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

from __future__ import print_function


from gi.repository import Gtk

from debugger.debugger_api import StartupInfo
from debugger.mi.mi_debugger import MiDebugger
from window import MainWindow


class VisualiserApp(object):
    def __init__(self):
        self.debugger = MiDebugger()
        self.startup_info = StartupInfo()
        self.main_window = MainWindow(self)
        Gtk.init()

    def quit(self):
        self.debugger.terminate()
        Gtk.main_quit()

    def start(self):
        self.main_window.show()
        Gtk.main()
