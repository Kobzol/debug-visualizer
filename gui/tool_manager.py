# -*- coding: utf-8 -*-

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
