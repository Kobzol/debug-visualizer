# -*- coding: utf-8 -*-

import os
import paths

from gi.repository import Gtk
from gi.repository import Gdk


class Config(object):
    def __init__(self):
        self.ui_dir = os.path.join(paths.DIR_ROOT, paths.DIR_RES, "gui")
        self.gui_main_window_menu = self.get_gui_builder("main_window_menu")
        self.gui_main_window_toolbar = self.get_gui_builder("main_window_toolbar")
        self.gui_io_console = self.get_gui_builder("io_console")

        provider = Gtk.CssProvider.new()
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        provider.load_from_path(os.path.join(paths.DIR_RES, "css", "style.css"))

    def get_gui_builder(self, path):
        return Gtk.Builder.new_from_file(os.path.join(self.ui_dir, path + ".glade"))
