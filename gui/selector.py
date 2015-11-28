# -*- coding: utf-8 -*-

import abc

from gi.repository import Gtk
from gi.repository import GObject

from enums import ProcessState
from utils import run_on_gui


class FrameListRow(Gtk.ListBoxRow):
    def __init__(self, frame):
        """
        @type frame: frame.Frame
        """
        super(FrameListRow, self).__init__()

        self.frame = frame


class ThreadListRow(Gtk.ListBoxRow):
    def __init__(self, thread):
        """
        @type thread: inferior_thread.InferiorThread
        """
        super(ThreadListRow, self).__init__()

        self.thread = thread


class Selector(Gtk.ListBox):
    def __init__(self, debugger):
        """
        @type debugger: mi.debugger.Debugger
        """
        super(Selector, self).__init__()

        self.debugger = debugger
        self.debugger.on_process_state_changed.subscribe(self._handle_process_change)
        self.debugger.on_thread_changed.subscribe(self._handle_thread_change)
        self.debugger.on_frame_changed.subscribe(self._handle_frame_change)

        self.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.connect("row-selected", lambda listbox, row: self._handle_row_selected(row))

        self.auto_select = False

    def clear_children(self):
        for widget in self.get_children():
            self.remove(widget)

    @abc.abstractmethod
    def _handle_process_change(self, state, event):
        pass

    @abc.abstractmethod
    def _handle_frame_change(self, frame):
        pass

    @abc.abstractmethod
    def _handle_thread_change(self, thread):
        pass

    @abc.abstractmethod
    def _handle_row_selected(self, row):
        pass

    def _is_auto_select_on(self):
        return self.auto_select

    def _select_row_auto(self, row):
        self.auto_select = True
        run_on_gui(self._select_row_auto_callback, row)

    def _select_row_auto_callback(self, row):
        self.select_row(row)
        self.auto_select = False


class FrameSelector(Selector):
    def __init__(self, debugger):
        """
        @type debugger: mi.debugger.Debugger
        """
        super(FrameSelector, self).__init__(debugger)

    def add_frame(self, frame):
        row = FrameListRow(frame)

        frame_desc = str(frame)
        frame_desc_trunc = (frame_desc[:50] + "...") if len(frame_desc) > 53 else frame_desc

        label = Gtk.Label(frame_desc_trunc)
        label.set_tooltip_text(frame_desc)
        row.add(label)

        self.add(row)
        self.show_all()

        return row

    def _handle_frame_change(self, frame):
        run_on_gui(self._load_frames)

    def _handle_thread_change(self, thread):
        run_on_gui(self._load_frames)

    def _handle_row_selected(self, row):
        """
        @type row: FrameListRow
        """
        if row is None or self._is_auto_select_on():
            return

        self.debugger.thread_manager.change_frame(row.get_index())

    def _handle_process_change(self, state, event):
        if state == ProcessState.Exited:
            run_on_gui(self.clear_children)
        elif state == ProcessState.Stopped:
            run_on_gui(self._load_frames)

    def _load_frames(self):
        self.clear_children()
        frames = self.debugger.thread_manager.get_frames()
        selected_frame = self.debugger.thread_manager.get_current_frame()

        for frame in frames:
            row = self.add_frame(frame)

            if frame.level == selected_frame.level:
                self._select_row_auto(row)


class ThreadSelector(Selector):
    def __init__(self, debugger):
        super(ThreadSelector, self).__init__(debugger)

    def add_thread(self, thread):
        """
        @type thread: inferior_thread.InferiorThread
        @return: ThreadListRow
        """
        row = ThreadListRow(thread)

        thread_desc = str(thread)
        thread_desc_trunc = (thread_desc[:50] + "...") if len(thread_desc) > 53 else thread_desc

        label = Gtk.Label(thread_desc_trunc)
        label.set_tooltip_text(thread_desc)
        row.add(label)

        self.add(row)
        self.show_all()

        return row

    def _handle_process_change(self, state, event):
        if state == ProcessState.Exited:
            run_on_gui(self.clear_children)
        elif state == ProcessState.Stopped:
            run_on_gui(self._load_threads)

    def _handle_frame_change(self, frame):
        pass

    @abc.abstractmethod
    def _handle_thread_change(self, thread):
        run_on_gui(self._load_threads)

    @abc.abstractmethod
    def _handle_row_selected(self, row):
        """
        @type row: ThreadListRow
        """
        if row is None or self._is_auto_select_on():
            return

        self.debugger.thread_manager.set_thread_by_index(row.thread.id)

    def _load_threads(self):
        self.clear_children()
        thread_info = self.debugger.thread_manager.get_thread_info()

        for thread in thread_info.threads:
            row = self.add_thread(thread)

            if thread == thread_info.selected_thread:
                self._select_row_auto(row)
