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

from gui.gui_util import require_gui_thread
from debugger.util import EventBroadcaster


class ValueEntry(Gtk.Frame):
    @require_gui_thread
    def __init__(self, title, text):
        Gtk.Frame.__init__(self)

        self.set_label(title)
        self.set_label_align(0.0, 0.0)

        self.box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box.set_margin_bottom(5)
        self.box.set_margin_left(2)
        self.text_entry = Gtk.Entry()
        self.text_entry.set_text(text)
        self.confirm_button = Gtk.Button(label="Set")

        self.get_style_context().add_class("value-entry")

        self.box.pack_start(self.text_entry, False, False, 0)
        self.box.pack_start(self.confirm_button, False, False, 5)
        self.add(self.box)
        self.show_all()

        self.confirm_button.connect("clicked",
                                    lambda btn: self._handle_confirm_click())

        self.on_value_entered = EventBroadcaster()

    @require_gui_thread
    def set_value(self, value):
        """
        @type value: str
        """
        self.text_entry.set_text(value)

    def _handle_confirm_click(self):
        value = self.text_entry.get_text()
        self.set_value("")

        self.on_value_entered.notify(value)
        self.hide()
