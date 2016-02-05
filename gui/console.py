# -*- coding: utf-8 -*-

import threading
import select
import traceback
import sys
import time
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject

from enums import ProcessState
from gui_util import require_gui_thread, run_on_gui


class Console(Gtk.ScrolledWindow):
    @staticmethod
    def is_data_available(fd, timeout=0.05):
        return len(select.select([fd], [], [], timeout)[0]) != 0

    def __init__(self, width=-1, height=-1):
        Gtk.ScrolledWindow.__init__(self)

        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_size_request(width, height)

        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)

        self.textview = Gtk.TextView()

        font_desc = Pango.FontDescription.from_string("monospace")
        if font_desc:
            self.textview.modify_font(font_desc)

        self.add(self.textview)

        self.show_all()

    @require_gui_thread
    def get_buffer(self):
        return self.textview.get_buffer()

    @require_gui_thread
    def get_cursor_iter(self):
        cursor_rectangle = self.textview.get_cursor_locations(None)[0]
        return self.textview.get_iter_at_location(cursor_rectangle.x, cursor_rectangle.y)

    @require_gui_thread
    def get_current_line(self):
        return self.get_cursor_iter().get_line()

    @require_gui_thread
    def get_line_iters(self, line_number):
        start_line = self.textview.get_buffer().get_iter_at_line(line_number)
        end_line = start_line.copy()
        end_line.forward_to_line_end()
        return (start_line, end_line)

    @require_gui_thread
    def clear(self):
        self.get_buffer().set_text("")


class IOConsole(Console):
    @staticmethod
    def _add_iter_char(iter, string="", end_text=None):
        if end_text is None:
            end_text = iter.copy()
            end_text.forward_char()
        return string + iter.get_text(end_text)

    def __init__(self, width=-1, height=-1):
        Console.__init__(self, width, height)

        self.textview.set_editable(True)

        self.tag_stdout = self.get_buffer().create_tag("stdout", foreground="black", editable=False)
        self.tag_stderr = self.get_buffer().create_tag("stderr", foreground="red", editable=False)
        self.tag_stdin = self.get_buffer().create_tag("stdin", foreground="blue", editable=True)
        self.tag_handled = self.get_buffer().create_tag("handled", editable=False)

        self.watch_thread = None
        self.stop_thread = threading.Event()

        self.textview.connect_after("key-release-event", lambda widget, key: self._handle_key(key))

        self.debugger = None
        self.last_handled_char = Gtk.TextMark.new("last-checked-text", True)
        self.get_buffer().add_mark(self.last_handled_char, self.get_buffer().get_start_iter())

        self.textview.set_editable(False)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Running:
            run_on_gui(self.textview.set_editable, True)
        else:
            run_on_gui(self.textview.set_editable, False)

    @require_gui_thread
    def _handle_key(self, key):
        if key.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self._emit_buffer()

    @require_gui_thread
    def _handle_input_char(self, start_iter):
        if not start_iter.has_tag(self.tag_handled):
            buffer = self.get_buffer()

            end_iter = start_iter.copy()
            end_iter.forward_char()

            buffer.apply_tag(self.tag_handled, start_iter, end_iter)
            buffer.apply_tag(self.tag_stdin, start_iter, end_iter)

            return start_iter.get_text(end_iter)
        else:
            return None

    @require_gui_thread
    def _collect_buffer(self):
        input_buffer = ""
        buffer = self.get_buffer()

        start_check = buffer.get_iter_at_mark(self.last_handled_char)

        char = self._handle_input_char(start_check)

        if char:
            input_buffer += char

        while start_check.forward_char():
            char = self._handle_input_char(start_check)

            if char:
                input_buffer += char

        buffer.move_mark(self.last_handled_char, start_check)

        return input_buffer

    @require_gui_thread
    def _emit_buffer(self):
        if not self.debugger.io_manager.stdin:
            return

        input_buffer = self._collect_buffer()

        try:
            self.debugger.io_manager.stdin.write(input_buffer)
        except:
            traceback.print_exc()

    @require_gui_thread
    def _write_on_ui(self, text, tag_name=None):
        if tag_name:
            self.write(text, tag_name)
        else:
            self.write(text)

    def _read_data(self, debugger, stream_attr, data_tag):
        stream_file = getattr(debugger.io_manager, stream_attr)

        if Console.is_data_available(stream_file):
            data = stream_file.readline()

            if len(data) > 0:
                run_on_gui(self._write_on_ui, data, data_tag)

    def _watch_file_thread(self, debugger):
        while not self.stop_thread.is_set():
            try:
                self._read_data(debugger, "stdout", "stdout")
                self._read_data(debugger, "stderr", "stderr")
            except:
                time.sleep(0.01)

    def _stop_watch_thread(self):
        if self.watch_thread is not None:
            self.stop_thread.set()
            self.watch_thread.join()
            self.watch_thread = None
            self.stop_thread.clear()

    def _watch_output(self, debugger):
        self._stop_watch_thread()

        self.watch_thread = threading.Thread(target=self._watch_file_thread, args=[debugger])
        self.watch_thread.start()

    @require_gui_thread
    def clear(self):
        Console.clear(self)

        buffer = self.get_buffer()
        buffer.move_mark(self.last_handled_char, buffer.get_start_iter())

    def watch(self, debugger):
        self.debugger = debugger

        debugger.on_process_state_changed.subscribe(self._handle_process_state_change)

        self._watch_output(debugger)

    @require_gui_thread
    def write(self, text, tag_name="stdout"):
        buffer = self.get_buffer()
        buffer.insert_with_tags_by_name(buffer.get_end_iter(), text, tag_name, "handled")

    def stop_watch(self):
        self._stop_watch_thread()
        self.debugger.on_process_state_changed.unsubscribe(self._handle_process_state_change)

    @require_gui_thread
    def filter_toggle_io(self, type):
        tag = self.get_buffer().get_tag_table().lookup(type)

        if tag:
            tag.props.invisible = not tag.props.invisible