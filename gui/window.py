# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

import os
from config import Config

from drawing.canvas import MemoryCanvas, CanvasToolbarWrapper
from enums import ProcessState
from source_edit import SourceManager
from dialog import FileOpenDialog, MessageBox
from console import IOConsole
from stackframe_selector import StackFrameSelector
from tool_manager import ToolManager
from toolbar_manager import ToolbarManager


class MainWindow(Gtk.Window):
    def __init__(self, app):
        """
        @type app: app.VisualiserApp
        """
        Gtk.Window.__init__(self, title="Visualizing debugger")

        self.app = app
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)
        self.connect("delete-event", lambda *x: self.quit())

        self.set_default_size(800, 600)

        self._init_components(app)

        app.debugger.on_process_state_changed.subscribe(self._handle_process_state_change)

        loaded = self.app.debugger.load_binary("../debugger/test")

        if loaded:
            main_file = self.app.debugger.file_manager.get_main_source_file()

            if main_file:
                self.source_manager.open_file(main_file)

    def _init_components(self, app):
        """
        @type app: app.VisualiserApp
        """
        # wrapper
        self.wrapper = Gtk.Grid.new()
        self.wrapper.set_row_homogeneous(False)
        self.add(self.wrapper)

        # menu
        menu_signals = {
            "menu-binary-load": lambda *x: self.binary_load_dialog(),
            "menu-source-open": lambda *x: self.source_open_dialog(),
            "menu-quit": lambda *x: self.quit()
        }
        Config.GUI_MAIN_WINDOW_MENU.connect_signals(menu_signals)
        self.menu = Config.GUI_MAIN_WINDOW_MENU.get_object("menu")
        self._add_to_row(self.menu, 0)

        # toolbar
        self.toolbar_manager = ToolbarManager(Config.GUI_MAIN_WINDOW_TOOLBAR, app.debugger)
        self._add_to_row(self.toolbar_manager.toolbar, 1)

        # content
        self.content = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self._add_to_row(self.content, 2)

        self.source_manager = SourceManager(app.debugger)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(-1, 500)
        scrolled_window.add(self.source_manager)
        self.content.add1(scrolled_window)
        self.add_shortcut(Gdk.KEY_space, self.source_manager.toggle_breakpoint, Gdk.ModifierType.CONTROL_MASK)

        canvas = MemoryCanvas(app.debugger)
        Config.GUI_MEMORY_CANVAS_TOOLBAR.connect_signals({
            "zoom-in": lambda *x: canvas.zoom_in(),
            "zoom-out": lambda *x: canvas.zoom_out(),
            "zoom-reset": lambda *x: canvas.zoom_reset()
        })
        canvas_toolbar = Config.GUI_MEMORY_CANVAS_TOOLBAR.get_object("toolbar")
        self.content.add2(CanvasToolbarWrapper(canvas, canvas_toolbar))

        self.content.set_position(400)

        # tools
        self.tool_manager = ToolManager()

        self.console = IOConsole(height=150)
        self.console.watch(app.debugger)

        Config.GUI_IO_CONSOLE.connect_signals({
            "filter-changed": lambda button: self.console.filter_toggle_io(button.get_label()),
            "console-clear": lambda button: self.console.clear()
        })
        self.console_wrapper = Config.GUI_IO_CONSOLE.get_object("wrapper")
        self.console_wrapper.add(self.console)
        self.tool_manager.add_tool("Console", self.console_wrapper)

        self.stackframe_selector = StackFrameSelector(app.debugger)
        window = Gtk.ScrolledWindow()
        window.add_with_viewport(self.stackframe_selector)
        window.set_size_request(-1, 100)
        self.tool_manager.add_tool("Call stack", window)

        self._add_to_row(self.tool_manager, 3)

        # status bar
        self.status_bar = Gtk.Statusbar.new()
        self._add_to_row(self.status_bar, 4)

    def _add_to_row(self, widget, row_index):
        self.wrapper.attach(widget, 0, row_index, 1, 1)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Exited:
            self.add_status_message("Process exited with code {0} ({1}).".format(event_data.return_code, event_data.return_desc))
        elif state == ProcessState.Stopped:
            location = self.app.debugger.file_manager.get_current_location()
            if location[0]:
                self.add_status_message("Process stopped at {0}:{1} - {2} ({3})"
                                        .format(location[0], location[1], event_data.stop_reason, event_data.stop_desc))
            else:
                self.add_status_message("Process stopped - {0} ({1})"
                                        .format(event_data.stop_reason, event_data.stop_desc))
        elif state == ProcessState.Running:
            self.add_status_message("Process is running...")

    def add_status_message(self, text):
        self.status_bar.push(1, text)

    def add_shortcut(self, key, callback, mask=0):
        self.accel_group.connect(key, mask, Gtk.AccelFlags.VISIBLE, lambda *x: callback())

    def binary_load_dialog(self):
        file_path = FileOpenDialog.open_file("Choose a binary file", self, os.path.abspath("../debugger/"))

        if file_path:
            self.app.debugger.stop()
            loaded = self.app.debugger.load_binary(file_path)

            if loaded:
                main_file = self.app.debugger.file_manager.get_main_source_file()

                if main_file:
                    self.source_manager.open_file(main_file)
                    self.add_status_message("Main file \"{0}\" has been loaded.".format(main_file))
                else:
                    MessageBox.show("The main file of this binary file couldn't be loaded.", "Main file",
                                    self, Gtk.MessageType.WARNING)
            else:
                MessageBox.show("This file couldn't be loaded.", "Binary load", self, Gtk.MessageType.ERROR)

    def source_open_dialog(self):
        file_path = FileOpenDialog.open_file("Choose a source file", self)

        if file_path:
            self.source_manager.open_file(file_path)
            self.add_status_message("Source file \"{0}\" has been opened.".format(file_path))

    def quit(self):
        self.console.stop_watch()
        self.app.quit()
