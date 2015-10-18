# -*- coding: utf-8 -*-

import os
import paths

from gi.repository import Gtk
from gi.repository import Gdk


class Config(object):
    UI_DIR = os.path.join(paths.DIR_ROOT, paths.DIR_RES, "gui")
    GUI_MAIN_WINDOW_MENU = None
    GUI_MAIN_WINDOW_TOOLBAR = None
    GUI_IO_CONSOLE = None
    GUI_MEMORY_CANVAS_TOOLBAR = None

    @staticmethod
    def get_gui_builder(path):
        return Gtk.Builder.new_from_file(os.path.join(Config.UI_DIR, path + ".glade"))

    @staticmethod
    def preload():
        Config.UI_DIR = os.path.join(paths.DIR_ROOT, paths.DIR_RES, "gui")
        Config.GUI_MAIN_WINDOW_MENU = Config.get_gui_builder("main_window_menu")
        Config.GUI_MAIN_WINDOW_TOOLBAR = Config.get_gui_builder("main_window_toolbar")
        Config.GUI_IO_CONSOLE = Config.get_gui_builder("io_console")
        Config.GUI_MEMORY_CANVAS_TOOLBAR = Config.get_gui_builder("memory_canvas_toolbar")

        provider = Gtk.CssProvider.new()
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        provider.load_from_path(os.path.join(paths.DIR_RES, "css", "style.css"))
