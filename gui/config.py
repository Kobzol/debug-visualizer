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
    GUI_STARTUP_INFO_DIALOG = None

    @staticmethod
    def get_gui_builder(path):
        return Gtk.Builder.new_from_file(os.path.join(Config.UI_DIR,
                                                      path + ".glade"))

    @staticmethod
    def preload():
        Config.UI_DIR = os.path.join(paths.DIR_ROOT, paths.DIR_RES, "gui")
        Config.GUI_MAIN_WINDOW_MENU = Config.get_gui_builder(
            "main_window_menu")
        Config.GUI_MAIN_WINDOW_TOOLBAR = Config.get_gui_builder(
            "main_window_toolbar")
        Config.GUI_IO_CONSOLE = Config.get_gui_builder(
            "io_console")
        Config.GUI_MEMORY_CANVAS_TOOLBAR = Config.get_gui_builder(
            "memory_canvas_toolbar")
        Config.GUI_STARTUP_INFO_DIALOG = Config.get_gui_builder(
            "startup_info_dialog"
        )

        provider = Gtk.CssProvider.new()
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        provider.load_from_path(os.path.join(paths.DIR_RES,
                                             "css",
                                             "style.css"))
