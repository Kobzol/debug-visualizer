# -*- coding: utf-8 -*-
from __future__ import print_function


from gi.repository import Gtk
from mi.mi_debugger import MiDebugger
from window import MainWindow


class VisualiserApp(object):
    def __init__(self):
        self.debugger = MiDebugger()
        self.main_window = MainWindow(self)
        Gtk.init()

    def quit(self):
        self.debugger.terminate()
        Gtk.main_quit()

    def start(self):
        self.main_window.show_all()
        Gtk.main()
