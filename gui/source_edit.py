# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import GtkSource
from gi.repository import GObject
import os

from enum import Enum

from analysis.source_analyser import SourceAnalyzer
from events import EventBroadcaster
from enums import ProcessState


class BreakpointChangeType(Enum):
    Create = 1
    Delete = 2


class SourceEditor(GtkSource.View):
    @staticmethod
    def load_file(path):
        try:
            return open(path).read()
        except:
            return None

    def __init__(self, language="cpp"):
        self.buffer = GtkSource.Buffer()
        super(SourceEditor, self).__init__(buffer=self.get_buffer())

        self.start_undoable()

        self.set_language(language)
        self.get_buffer().set_highlight_syntax(True)
        self.get_buffer().set_highlight_matching_brackets(True)
        self.tag_breakpoint = self.get_buffer().create_tag("bp-line", background="Red")
        self.tag_exec = self.get_buffer().create_tag("exec-line", background="Yellow")

        self.stop_undoable()

        self.set_show_line_numbers(True)
        self.set_highlight_current_line(True)
        self.set_show_right_margin(True)
        self.set_right_margin_position(80)

        self.file = None
        self.on_breakpoint_changed = EventBroadcaster()

        self.analyser = SourceAnalyzer()
        self.connect("motion-notify-event", lambda widget, event: self._handle_mouse_move(event))

    def _handle_mouse_move(self, event):
        x, y = self.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, event.x, event.y)
        iter = self.get_iter_at_location(x, y)

        symbol = self.analyser.get_symbol_name(iter.get_line() + 1, iter.get_line_offset())

    def get_buffer(self):
        return self.buffer

    def get_file(self):
        return self.file

    def set_language(self, key):
        manager = GtkSource.LanguageManager()
        language = manager.get_language(key)

        self.start_undoable()
        self.get_buffer().set_language(language)
        self.stop_undoable()

    def start_undoable(self):
        self.get_buffer().begin_not_undoable_action()

    def stop_undoable(self):
        self.get_buffer().end_not_undoable_action()

    def set_content_from_file(self, path):
        content = SourceEditor.load_file(path)

        if content:
            self.file = path
            self.start_undoable()
            self.get_buffer().set_text(content)
            self.stop_undoable()
            self.analyser.set_file(path)

    def get_cursor_iter(self):
        cursor_rectangle = self.get_cursor_locations(None)[0]
        return self.get_iter_at_location(cursor_rectangle.x, cursor_rectangle.y)

    def get_current_column(self):
        return self.get_cursor_iter().get_line_offset()

    def get_current_line(self):
        return self.get_cursor_iter().get_line()

    def get_line_iters(self, line_number):
        start_line = self.get_buffer().get_iter_at_line(line_number)
        end_line = start_line.copy()
        end_line.forward_to_line_end()
        return (start_line, end_line)

    def _create_bp_event(self, line, create=True):
        # +1 because the lines are usually addressed starting from 1
        return ((self.file, line + 1), BreakpointChangeType.Create if create else BreakpointChangeType.Delete)

    def breakpoint_change(self, line_number, enable=True):
        line_iters = self.get_line_iters(line_number)

        if enable:
            self.get_buffer().apply_tag(self.tag_breakpoint, line_iters[0], line_iters[1])
        else:
            self.get_buffer().remove_tag(self.tag_breakpoint, line_iters[0], line_iters[1])

        self.on_breakpoint_changed.notify(*self._create_bp_event(line_number, enable))

    def breakpoint_toggle(self, line_number):
        line_iters = self.get_line_iters(line_number)

        if line_iters[0].has_tag(self.tag_breakpoint):
            self.breakpoint_change(line_number, False)
        else:
            self.breakpoint_change(line_number, True)

    def set_exec_line(self, line_number):
        self.unset_exec_line()
        line_iters = self.get_line_iters(line_number)
        self.get_buffer().apply_tag(self.tag_exec, line_iters[0], line_iters[1])

    def unset_exec_line(self):
        buffer = self.get_buffer()
        buffer.remove_tag(self.tag_exec, buffer.get_start_iter(), buffer.get_end_iter())

    def undo(self):
        if self.get_buffer().can_undo():
            self.get_buffer().undo()
            return True
        else:
            return False

    def redo(self):
        if self.get_buffer().can_redo():
            self.get_buffer().redo()
            return True
        else:
            return False


class SourceManager(Gtk.Notebook):
    def __init__(self, debugger):
        super(SourceManager, self).__init__()

        self.debugger = debugger

        self.popup_enable()

        self.on_breakpoint_changed = EventBroadcaster()
        self.on_breakpoint_changed.subscribe(self._handle_breakpoint_change)

        self.debugger.on_process_state_changed.subscribe(self._handle_process_state_change)

    def _handle_breakpoint_change(self, location, change_type):
        if change_type == BreakpointChangeType.Create:
            self.debugger.breakpoint_manager.add_breakpoint(*location)
        elif change_type == BreakpointChangeType.Delete:
            self.debugger.breakpoint_manager.remove_breakpoint(*location)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Stopped:
            location = self.debugger.file_manager.get_current_location()
            if location[0]:
                GObject.idle_add(lambda *x: self.set_exec_line(location[0], location[1]))
        elif state == ProcessState.Exited:
            GObject.idle_add(lambda *x: self.unset_exec_line())

    def get_tabs(self):
        return [self.get_nth_page(i) for i in xrange(0, self.get_n_pages())]

    def open_file(self, file_path):
        for index, tab in enumerate(self.get_tabs()):
            if tab.file == file_path:
                self.select_tab(index)
                return tab

        return self._add_tab(file_path)

    def set_exec_line(self, file_path, line_number):
        tab = self.open_file(file_path)
        tab.set_exec_line(line_number - 1)

    def unset_exec_line(self):
        for tab in self.get_tabs():
            tab.unset_exec_line()

    def get_selected_editor(self):
        selected = self.get_current_page()

        if selected != -1:
            return self.get_nth_page(selected)
        else:
            return None

    def toggle_breakpoint(self):
        editor = self.get_selected_editor()
        editor.breakpoint_toggle(editor.get_current_line())

    def select_tab(self, index):
        self.set_current_page(index)

    def _create_label(self, path, widget):
        content = Gtk.Box(Gtk.Orientation.HORIZONTAL)

        label = Gtk.Label(os.path.basename(path))

        button = Gtk.Button()
        button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.connect("clicked", lambda *x: self._close_tab(widget))

        content.pack_start(label, True, True, 0)
        content.pack_start(button, False, False, 0)
        content.show_all()

        return content

    def _close_tab(self, widget):
        self.remove_page(self.get_tabs().index(widget))

    def _add_tab(self, file_path):
        editor = SourceEditor()
        editor.set_content_from_file(file_path)
        editor.set_hexpand(True)
        editor.set_vexpand(True)
        editor.show_all()

        label = self._create_label(file_path, editor)

        index = self.append_page_menu(editor, label, Gtk.Label(label=file_path))

        if index != -1:
            self.select_tab(index)
            self.set_tab_reorderable(editor, True)
            editor.on_breakpoint_changed.subscribe(lambda location, type: self.on_breakpoint_changed.notify(location, type))
            return editor
        else:
            return None
