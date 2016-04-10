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


from gi.repository import Gtk

from gui_util import require_gui_thread


class ToolManager(Gtk.Notebook):
    def __init__(self):
        super(ToolManager, self).__init__()

        self.set_tab_pos(Gtk.PositionType.BOTTOM)

    @require_gui_thread
    def get_active_tool(self):
        selected = self.get_current_page()

        if selected != -1:
            return self.get_nth_page(selected)
        else:
            return None

    @require_gui_thread
    def _handle_tab_click(self, widget):
        self.get_active_tool().set_visible(False)

    @require_gui_thread
    def add_tool(self, label, widget):
        """
        @type label: string
        @type widget: Gtk.Widget
        """
        self.append_page(widget, Gtk.Label(label=label))
