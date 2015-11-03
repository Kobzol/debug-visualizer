# -*- coding: utf-8 -*-

from gi.repository import Gtk
from enums import ProcessState


class StackFrameListRow(Gtk.ListBoxRow):
    def __init__(self, frame):
        super(StackFrameListRow, self).__init__()

        self.frame = frame


class StackFrameSelector(Gtk.ListBox):
    def __init__(self, debugger):
        """
        @type debugger: lldbc.lldb_debugger.LldbDebugger
        """
        super(StackFrameSelector, self).__init__()

        self.debugger = debugger
        self.debugger.on_process_state_changed.subscribe(self._handle_process_change)

        self.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.connect("row-selected", lambda listbox, row: self._handle_frame_selected(row))

    def _handle_process_change(self, state, event):
        if state == ProcessState.Exited:
            self.clear_frames()
        elif state == ProcessState.Stopped:
            self.clear_frames()
            frames = self.debugger.thread_manager.get_frames()

            for frame in frames:
                self.add_frame(frame)

            self.select_row(self.get_row_at_index(0))

    def _handle_frame_selected(self, row):
        """
        @type row: StackFrameListRow
        """
        if row is None:
            return

        self.debugger.thread_manager.change_frame(row.get_index())

    def clear_frames(self):
        for widget in self.get_children():
            self.remove(widget)

    def add_frame(self, frame):
        row = StackFrameListRow(frame)

        frame_desc = str(frame)
        frame_desc_trunc = (frame_desc[:50] + "...") if len(frame_desc) > 53 else frame_desc

        label = Gtk.Label(frame_desc_trunc)
        label.set_tooltip_text(frame_desc)
        row.add(label)

        self.add(row)
        self.show_all()
