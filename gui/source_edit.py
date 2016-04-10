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

from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Gtk
from gi.repository import GtkSource

import os
from enum import Enum

import paths
from debugger.analysis.source_analyser import SourceAnalyzer
from debugger.util import EventBroadcaster, Logger
from debugger.enums import ProcessState, DebuggerState
from gui_util import run_on_gui, require_gui_thread


class BreakpointChangeType(Enum):
    Create = 1
    Delete = 2


class BreakpointRenderer(GtkSource.GutterRendererPixbuf):
    def __init__(self, source_window, breakpoint_img_path,
                 execution_img_path, **properties):
        super(BreakpointRenderer, self).__init__(**properties)
        self.source_window = source_window
        self.bp_pixbuf = GdkPixbuf.Pixbuf.new_from_file(breakpoint_img_path)
        self.exec_pixbuf = GdkPixbuf.Pixbuf.new_from_file(execution_img_path)
        self.set_alignment(0.5, 0.5)
        self.set_size(15)
        self.set_padding(5, -1)

    def do_draw(self, cr, background_area, cell_area, start, end, state):
        line = start.get_line()

        if line in self.source_window.get_breakpoint_lines():
            self.set_pixbuf(self.bp_pixbuf)
            GtkSource.GutterRendererPixbuf.do_draw(self, cr, background_area,
                                                   cell_area,
                                                   start, end, state)

        if line == self.source_window.exec_line:
            self.set_pixbuf(self.exec_pixbuf)
            GtkSource.GutterRendererPixbuf.do_draw(self, cr, background_area,
                                                   cell_area,
                                                   start, end, state)


class SourceWindow(Gtk.ScrolledWindow):
    def __init__(self, editor):
        """
        @type editor: SourceEditor
        """
        Gtk.ScrolledWindow.__init__(self)

        self.editor = editor
        self.add(editor)

        self.show_all()


class SourceEditor(GtkSource.View):
    @staticmethod
    def load_file(path):
        try:
            return open(path).read()
        except:
            return None

    def __init__(self, debugger, language="cpp"):
        """
        @type debugger: debugger.mi.MiDebugger
        @type language: str
        """
        self.buffer = GtkSource.Buffer()
        super(SourceEditor, self).__init__(buffer=self.get_buffer())

        self.debugger = debugger

        self.start_undoable()

        self.set_language(language)
        self.get_buffer().set_highlight_syntax(True)
        self.get_buffer().set_highlight_matching_brackets(True)
        self.set_editable(False)

        self.gutter_renderer = BreakpointRenderer(self,
                                                  paths.get_resource(
                                                      "img/circle.png"),
                                                  paths.get_resource(
                                                      "img/arrow.png"))
        gutter = self.get_gutter(Gtk.TextWindowType.LEFT)
        gutter.insert(self.gutter_renderer, 0)

        self.stop_undoable()

        self.set_show_line_numbers(True)
        self.set_highlight_current_line(True)
        self.set_show_right_margin(True)
        self.set_right_margin_position(80)

        self.file = None
        self.on_breakpoint_changed = EventBroadcaster()

        self.exec_line = None
        self.bp_lines = set()

        self.analyser = SourceAnalyzer()
        self.connect("motion-notify-event",
                     lambda widget, event: self._handle_mouse_move(event))
        self.connect("button-press-event",
                     lambda widget, event: self._handle_mouse_click(event))
        self.on_symbol_hover = EventBroadcaster()

        self.debugger.breakpoint_manager.on_breakpoint_changed.subscribe(
            self._handle_model_breakpoint_change)
        self.breakpoint_lines = []

    def _handle_model_breakpoint_change(self, breakpoint):
        """
        @type breakpoint: debugee.Breakpoint
        """
        self._refresh_breakpoints()

    def _refresh_breakpoints(self):
        lines = []

        if (self.file and
                self.debugger.state.is_set(DebuggerState.BinaryLoaded) and
                self.debugger.process_state != ProcessState.Running):
            for bp in self.debugger.breakpoint_manager.get_breakpoints():
                if os.path.abspath(bp.location) == os.path.abspath(self.file):
                    lines.append(bp.line - 1)

        self.breakpoint_lines = lines

    def _handle_mouse_move(self, event):
        x, y = self.window_to_buffer_coords(Gtk.TextWindowType.TEXT,
                                            event.x,
                                            event.y)
        iter = self.get_iter_at_location(x, y)
        line = iter.get_line() + 1
        column = iter.get_line_offset() + 1
        symbol = self.analyser.get_symbol_name(line, column)

        if symbol is not None:
            self.on_symbol_hover.notify(self, symbol)

    def _handle_mouse_click(self, event):
        if (event.type == Gdk.EventType.BUTTON_PRESS and
                self.get_window(Gtk.TextWindowType.LEFT) == event.window):
            x, y = self.window_to_buffer_coords(Gtk.TextWindowType.LEFT,
                                                event.x,
                                                event.y)
            iter = self.get_iter_at_location(x, y)

            if self.debugger.state.is_set(DebuggerState.BinaryLoaded):
                self.toggle_breakpoint(iter.get_line())

    def get_buffer(self):
        return self.buffer

    def get_file(self):
        return self.file

    def get_breakpoint_lines(self):
        return self.breakpoint_lines

    @require_gui_thread
    def toggle_breakpoint(self, line):
        self.debugger.breakpoint_manager.toggle_breakpoint(self.file, line + 1)

        self.gutter_renderer.queue_draw()

    @require_gui_thread
    def set_language(self, key):
        manager = GtkSource.LanguageManager()
        language = manager.get_language(key)

        self.start_undoable()
        self.get_buffer().set_language(language)
        self.stop_undoable()

    @require_gui_thread
    def start_undoable(self):
        self.get_buffer().begin_not_undoable_action()

    @require_gui_thread
    def stop_undoable(self):
        self.get_buffer().end_not_undoable_action()

    @require_gui_thread
    def set_content_from_file(self, path):
        content = SourceEditor.load_file(path)

        if content:
            self.file = path
            self.start_undoable()
            self.get_buffer().set_text(content)
            self.stop_undoable()
            self.analyser.set_file(path)
            self._refresh_breakpoints()
            self.gutter_renderer.queue_draw()  # show existing breakpoints

    @require_gui_thread
    def get_cursor_iter(self):
        cursor_rectangle = self.get_cursor_locations(None)[0]
        return self.get_iter_at_location(cursor_rectangle.x,
                                         cursor_rectangle.y)

    @require_gui_thread
    def get_current_column(self):
        return self.get_cursor_iter().get_line_offset()

    @require_gui_thread
    def get_current_line(self):
        return self.get_cursor_iter().get_line()

    @require_gui_thread
    def get_line_iters(self, line_number):
        start_line = self.get_buffer().get_iter_at_line(line_number)
        end_line = start_line.copy()
        end_line.forward_to_line_end()
        return (start_line, end_line)

    @require_gui_thread
    def set_exec_line(self, line_number):
        self.unset_exec_line()
        line_iters = self.get_line_iters(line_number)
        self.scroll_to_iter(line_iters[0], 0.0, True, 0.5, 0.5)
        self.exec_line = line_number

        self.gutter_renderer.queue_draw()

    @require_gui_thread
    def unset_exec_line(self):
        self.exec_line = None

        self.gutter_renderer.queue_draw()

    @require_gui_thread
    def undo(self):
        if self.get_buffer().can_undo():
            self.get_buffer().undo()
            return True
        else:
            return False

    @require_gui_thread
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
        self.on_symbol_hover = EventBroadcaster()
        self.on_symbol_hover.subscribe(self._handle_symbol_hover)
        self.on_breakpoint_changed.subscribe(self._handle_breakpoint_change)

        self.debugger.on_process_state_changed.subscribe(
            self._handle_process_state_change)
        self.debugger.on_frame_changed.subscribe(self._handle_frame_change)

    def _handle_symbol_hover(self, source_editor, symbol):
        if self.debugger.process_state == ProcessState.Stopped:
            variable = self.debugger.variable_manager.get_variable(symbol)
            if variable and variable.address:
                source_editor.set_tooltip_text(str(variable))

    def _handle_breakpoint_change(self, location, change_type):
        if change_type == BreakpointChangeType.Create:
            self.debugger.breakpoint_manager.add_breakpoint(*location)
        elif change_type == BreakpointChangeType.Delete:
            self.debugger.breakpoint_manager.remove_breakpoint(*location)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Stopped:
            self._set_debugger_location()
        elif state == ProcessState.Exited:
            run_on_gui(self.unset_exec_line)

    def _handle_frame_change(self, frame):
        """
        @param frame: frame.Frame
        """
        self._set_debugger_location()

    def _set_debugger_location(self):
        location = self.debugger.file_manager.get_current_location()

        Logger.debug("Stop at {0}".format(location))

        if location and location[0]:
            run_on_gui(self.set_exec_line, location[0], location[1])

    @require_gui_thread
    def _create_label(self, path, widget):
        content = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        label = Gtk.Label(os.path.basename(path))

        button = Gtk.Button()
        button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE,
                                            Gtk.IconSize.MENU))
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.connect("clicked", lambda *x: self._close_tab(widget))

        event_box = Gtk.EventBox.new()
        event_box.add(label)
        event_box.connect("button-press-event",
                          lambda source, event: self._handle_tab_label_press(
                              event, widget))

        content.pack_start(event_box, True, True, 0)
        content.pack_start(button, False, False, 0)
        content.show_all()

        return content

    @require_gui_thread
    def _close_tab(self, widget):
        widget.editor.on_breakpoint_changed.clear()

        self.remove_page(self.get_tabs().index(widget))

    @require_gui_thread
    def _add_tab(self, file_path):
        editor = SourceEditor(self.debugger)
        editor.set_content_from_file(file_path)
        editor.set_hexpand(True)
        editor.set_vexpand(True)
        editor.show_all()

        window = SourceWindow(editor)

        label = self._create_label(file_path, window)

        menu_label = Gtk.Label(label=file_path)
        menu_label.set_alignment(0, 0)

        index = self.append_page_menu(window, label, menu_label)

        if index != -1:
            self.select_tab(index)
            self.set_tab_reorderable(window, True)
            editor.on_breakpoint_changed.redirect(self.on_breakpoint_changed)
            editor.on_symbol_hover.redirect(self.on_symbol_hover)
            return editor
        else:
            return None

    @require_gui_thread
    def _handle_tab_label_press(self, event, window):
        """
        @type event: Gdk.EventButton
        @type window: SourceWindow
        """
        if (event.type == Gdk.EventType.BUTTON_PRESS and
                event.button == 2):
            self._close_tab(window)

    @require_gui_thread
    def get_tabs(self):
        return [self.get_nth_page(i) for i in xrange(0, self.get_n_pages())]

    @require_gui_thread
    def open_file(self, file_path):
        for index, tab in enumerate(self.get_tabs()):
            if tab.editor.file == file_path:
                self.select_tab(index)
                return tab.editor

        return self._add_tab(file_path)

    @require_gui_thread
    def set_exec_line(self, file_path, line_number):
        self.unset_exec_line()

        tab = self.open_file(file_path)
        tab.set_exec_line(line_number - 1)

    @require_gui_thread
    def unset_exec_line(self):
        for tab in self.get_tabs():
            tab.editor.unset_exec_line()

    @require_gui_thread
    def get_selected_editor(self):
        selected = self.get_current_page()

        if selected != -1:
            return self.get_nth_page(selected).editor
        else:
            return None

    @require_gui_thread
    def select_tab(self, index):
        self.set_current_page(index)
