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

# -*- coding: utf-8 -*-

from gi.repository import Gtk

from debugger.debugger_api import StartupInfo
from gui.dialog import FileOpenDialog
from gui.gui_util import require_gui_thread


class EnvVarWidget(Gtk.Box):
    def __init__(self, *args, **kwargs):
        Gtk.Box.__init__(self, *args, **kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.entry_name = Gtk.Entry()
        self.entry_value = Gtk.Entry()

        self.pack_start(self.entry_name, False, False, 0)
        self.pack_start(self.entry_value, False, False, 0)

    @property
    def name(self):
        return self.entry_name.get_text()

    @property
    def value(self):
        return self.entry_value.get_text()


class StartupDialog(object):
    @require_gui_thread
    def __init__(self, dialog_builder):
        """
        @type dialog_builder: Gtk.Builder
        """
        signals = {
            "working-directory-choose":
            lambda *x: self._show_choose_dir_dialog(),
            "startup-cancel": lambda *x: self._cancel_dialog(),
            "startup-confirm": lambda *x: self._confirm_dialog(),
            "env-var-add": lambda *x: self._add_env_var()
        }

        self.dialog_builder = dialog_builder
        self.dialog_builder.connect_signals(signals)
        self.dialog = dialog_builder.get_object("startup_dialog")
        self.grid = self.dialog_builder.get_object("env_var_grid")
        self.env_line_mapping = []

        self.working_dir_entry = self.dialog_builder.get_object(
            "working_directory")
        self.cmd_arguments_entry = self.dialog_builder.get_object(
            "cmd_arguments")

    @require_gui_thread
    def show(self, startup_info):
        """
        @type startup_info: debugger.debugger_api.StartupInfo
        @rtype: debugger.debugger_api.StartupInfo
        """
        self._set_startup_info(startup_info)

        response = self.dialog.run()
        self.dialog.hide()

        if response != Gtk.ResponseType.YES:
            return startup_info
        else:
            return self._construct_startup_info()

    @require_gui_thread
    def _set_startup_info(self, startup_info):
        """
        @type startup_info: debugger.debugger_api.StartupInfo
        """
        for mapping in self.env_line_mapping:
            self.grid.remove_row(1)

        self.env_line_mapping = []

        self.working_dir_entry.set_text(startup_info.working_directory)
        self.cmd_arguments_entry.set_text(startup_info.cmd_arguments)

        for env in startup_info.env_vars:
            self._add_env_var(env[0], env[1])

    @require_gui_thread
    def _construct_startup_info(self):
        """
        @rtype: debugger.debugger_api.StartupInfo
        """
        startup_info = StartupInfo()
        startup_info.working_directory = self.working_dir_entry.get_text()
        startup_info.cmd_arguments = self.cmd_arguments_entry.get_text()

        for mapping in self.env_line_mapping:
            name = mapping[1].get_text()
            value = mapping[2].get_text()

            if name != "":
                startup_info.env_vars.append((name, value))

        return startup_info

    @require_gui_thread
    def _show_choose_dir_dialog(self):
        current_folder = self.working_dir_entry.get_text()
        folder = FileOpenDialog.select_folder("Choose working directory",
                                              self.dialog,
                                              current_folder)
        if folder:
            self.dialog_builder.get_object("working_directory").set_text(
                folder
            )

    @require_gui_thread
    def _add_env_var(self, name="", value=""):
        """
        @type name: str
        @type value: str
        """
        name_entry = Gtk.Entry()
        name_entry.set_text(name)
        name_entry.set_tooltip_text("Environment variable name")
        name_entry.show_all()

        value_entry = Gtk.Entry()
        value_entry.set_text(value)
        value_entry.set_tooltip_text("Environment variable value")
        value_entry.show_all()

        remove_button = Gtk.Button()
        remove_button.set_image(Gtk.Image().new_from_stock(
            Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON))
        remove_button.connect("clicked", lambda *x: self._remove_env_row(x[0]))
        remove_button.set_hexpand(False)
        remove_button.set_halign(Gtk.Align.CENTER)
        remove_button.set_tooltip_text("Remove environment variable")
        remove_button.show_all()

        row = len(self.env_line_mapping) + 1  # + 1 because of header

        self.grid.attach(name_entry, 0, row, 1, 1)
        self.grid.attach(value_entry, 1, row, 1, 1)
        self.grid.attach(remove_button, 2, row, 1, 1)

        self.env_line_mapping.append((remove_button, name_entry, value_entry))

    @require_gui_thread
    def _remove_env_row(self, remove_button):
        """
        @type remove_button: Gtk.Button
        """
        row = 0

        for i, mapping in enumerate(self.env_line_mapping):
            if mapping[0] == remove_button:
                row = i
                break

        self.grid.remove_row(row + 1)  # + 1 because of header

        del self.env_line_mapping[row]

    @require_gui_thread
    def _cancel_dialog(self):
        self.dialog.response(Gtk.ResponseType.CANCEL)

    @require_gui_thread
    def _confirm_dialog(self):
        self.dialog.response(Gtk.ResponseType.YES)
