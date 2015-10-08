# -*- coding: utf-8 -*-
from __future__ import print_function


from gi.repository import Gtk
from lldbc.lldb_debugger import LldbDebugger
from window import MainWindow


class VisualiserApp(object):
    def __init__(self, config):
        self.debugger = LldbDebugger()
        self.main_window = MainWindow(self, config)

    def quit(self):
        self.debugger.stop(True)
        Gtk.main_quit()

    def start(self):
        self.main_window.show_all()
        Gtk.main()
