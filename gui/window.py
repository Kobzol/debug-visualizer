# -*- coding: utf-8 -*-

from gi.repository import Gtk

import os

import paths
from config import Config

from drawing.canvas import MemoryCanvas, CanvasToolbarWrapper
from gui.startup_dialog import StartupDialog
from gui_util import require_gui_thread, run_on_gui
from debugger.enums import ProcessState
from heap_detail import HeapDetail
from memory_view import MemoryView, RegisterList
from source_edit import SourceManager
from dialog import FileOpenDialog, MessageBox
from console import IOConsole
from selector import FrameSelector, ThreadSelector
from tool_manager import ToolManager
from toolbar_manager import ToolbarManager


class TitleWindow(Gtk.ScrolledWindow):
    def __init__(self, title, content, *args, **kwargs):
        Gtk.ScrolledWindow.__init__(self, *args, **kwargs)

        self.wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        label = Gtk.Label.new(title)
        label.set_halign(Gtk.Align.START)
        label.set_margin_left(5)
        self.wrapper.pack_start(label, False, False, 5)
        self.wrapper.pack_start(content, True, True, 0)

        self.add(self.wrapper)


class MainWindow(Gtk.Window):
    def __init__(self, app):
        """
        @type app: gui.app.VisualiserApp
        """
        Gtk.Window.__init__(self, title="Devi")

        self.app = app
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)
        self.connect("delete-event", lambda *x: self.quit())

        self.set_default_size(1024, 768)
        self.set_icon_from_file(paths.get_resource("img/circle32x32.png"))

        self._init_components(app)

        app.debugger.on_process_state_changed.subscribe(
            self._handle_process_state_change)

        self.startup_dialog = StartupDialog(Config.GUI_STARTUP_INFO_DIALOG)

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
            "menu-binary-load": lambda *x: self._show_binary_load_dialog(),
            "menu-source-open": lambda *x: self._show_source_open_dialog(),
            "menu-quit": lambda *x: self.quit(),
            "menu-startup-info-dialog":
            lambda *x: self._show_startup_info_dialog(),
            "menu-about-dialog": lambda *x: self._show_about_dialog()
        }
        Config.GUI_MAIN_WINDOW_MENU.connect_signals(menu_signals)
        self.menu = Config.GUI_MAIN_WINDOW_MENU.get_object("menu")
        self._add_to_row(self.menu, 0)

        # toolbar
        self.toolbar_manager = ToolbarManager(Config.GUI_MAIN_WINDOW_TOOLBAR,
                                              app.debugger)
        self.toolbar_manager.on_run_process.subscribe(
            lambda: self.app.debugger.launch(self.app.startup_info.copy()))
        self._add_to_row(self.toolbar_manager.toolbar, 1)

        # content
        self.content = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self._add_to_row(self.content, 2)

        self.source_manager = SourceManager(app.debugger)
        self.source_manager.set_size_request(-1, 500)
        self.content.add1(self.source_manager)

        canvas = MemoryCanvas(app.debugger)
        Config.GUI_MEMORY_CANVAS_TOOLBAR.connect_signals({
            "zoom-in": lambda *x: canvas.zoom_in(),
            "zoom-out": lambda *x: canvas.zoom_out(),
            "zoom-reset": lambda *x: canvas.zoom_reset(),
            "translation-reset": lambda *x: canvas.reset_translation()
        })
        canvas_toolbar = Config.GUI_MEMORY_CANVAS_TOOLBAR.get_object("toolbar")
        self.content.add2(CanvasToolbarWrapper(canvas, canvas_toolbar))

        self.content.set_position(400)

        # tools
        self.tool_manager = ToolManager()

        self.console = IOConsole(height=150)
        self.console.watch(app.debugger)

        Config.GUI_IO_CONSOLE.connect_signals({
            "filter-changed": lambda button:
            self.console.filter_toggle_io(button.get_label()),
            "console-clear": lambda button: self.console.clear()
        })
        self.console_wrapper = Config.GUI_IO_CONSOLE.get_object("wrapper")
        self.console_wrapper.add(self.console)
        self.tool_manager.add_tool("Console", self.console_wrapper)

        self.frame_selector = FrameSelector(app.debugger)
        window = TitleWindow("Call stack", self.frame_selector)
        window.set_size_request(-1, 100)
        self.tool_manager.add_tool("Call stack", window)

        self.thread_selector = ThreadSelector(app.debugger)
        window = TitleWindow("Threads", self.thread_selector)
        window.set_size_request(-1, 100)
        self.tool_manager.add_tool("Threads", window)

        self.register_list = RegisterList(app.debugger)
        self.tool_manager.add_tool("Registers",
                                   TitleWindow("Registers",
                                               self.register_list))

        self.memory_view = MemoryView(app.debugger)
        self.tool_manager.add_tool("Memory view",
                                   TitleWindow("Memory view",
                                               self.memory_view))

        self.heap_detail = HeapDetail(app.debugger)
        self.tool_manager.add_tool("Heap detail",
                                   TitleWindow("Heap detail",
                                               self.heap_detail))

        self._add_to_row(self.tool_manager, 3)

        # status bar
        self.status_bar = Gtk.Statusbar.new()
        self._add_to_row(self.status_bar, 4)

    def _add_to_row(self, widget, row_index):
        self.wrapper.attach(widget, 0, row_index, 1, 1)

    def _handle_process_state_change(self, state, event_data):
        if state == ProcessState.Exited:
            run_on_gui(self.add_status_message,
                       "Process exited with code {0}.".format(
                           event_data.return_code))
        elif state == ProcessState.Stopped:
            location = self.app.debugger.file_manager.get_current_location()
            if location and location[0]:
                run_on_gui(self.add_status_message,
                           "Process stopped at {0}:{1} - {2}"
                           .format(location[0],
                                   location[1],
                                   event_data.stop_reason))
            else:
                run_on_gui(self.add_status_message, "Process stopped - {0}"
                           .format(event_data.stop_reason))
        elif state == ProcessState.Running:
            run_on_gui(self.add_status_message, "Process is running...")

    @require_gui_thread
    def _show_startup_info_dialog(self):
        self.app.startup_info = self.startup_dialog.show(
            self.app.startup_info.copy())

    @require_gui_thread
    def _show_about_dialog(self):
        dialog = Config.GUI_MAIN_WINDOW_MENU.get_object("about_dialog")
        dialog.run()
        dialog.hide()

    @require_gui_thread
    def add_status_message(self, text):
        self.status_bar.push(1, text)

    def add_shortcut(self, key, callback, mask=0):
        self.accel_group.connect(key, mask, Gtk.AccelFlags.VISIBLE,
                                 lambda *x: callback())

    @require_gui_thread
    def _show_binary_load_dialog(self):
        file_path = FileOpenDialog.select_file("Choose a binary file", self,
                                               os.path.abspath("../debugger/"))

        if file_path:
            self.app.debugger.quit_program()
            loaded = self.app.debugger.load_binary(file_path)

            if loaded:
                main_file = self.app.debugger.file_manager.\
                    get_main_source_file()

                if main_file:
                    self.source_manager.open_file(main_file)
                    self.add_status_message(
                        "Main file \"{0}\" has been loaded.".format(main_file))
                else:
                    MessageBox.show("The main file of this binary file"
                                    "couldn't be loaded.",
                                    "Main file",
                                    self,
                                    Gtk.MessageType.WARNING)
            else:
                MessageBox.show("This file couldn't be loaded.",
                                "Binary load",
                                self, Gtk.MessageType.ERROR)

    @require_gui_thread
    def _show_source_open_dialog(self):
        file_path = FileOpenDialog.select_file("Choose a source file", self)

        if file_path:
            self.source_manager.open_file(file_path)
            self.add_status_message(
                "Source file \"{0}\" has been opened.".format(file_path))

    def quit(self):
        self.console.stop_watch()
        self.app.quit()
