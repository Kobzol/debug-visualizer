# -*- coding: utf-8 -*-
from __future__ import print_function


from gi.repository import Gtk
from lldbc.lldb_debugger import LldbDebugger
from mi.debugger import Debugger
from window import MainWindow


class VisualiserApp(object):
    def __init__(self):
        self.debugger = Debugger()
        self.main_window = MainWindow(self)

    def quit(self):
        self.debugger.kill(True)
        Gtk.main_quit()

    def start(self):
        self.main_window.show_all()
        Gtk.main()
