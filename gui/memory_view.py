# -*- coding: utf-8 -*-

from gi.repository import Gtk

import re

from enums import ProcessState
from gui_util import require_gui_thread, run_on_gui
from util import EventBroadcaster


class RegisterList(Gtk.ListBox):
    def __init__(self, debugger):
        """
        @type debugger: debugger.Debugger
        """
        super(RegisterList, self).__init__()
        self.set_selection_mode(Gtk.SelectionMode.NONE)

        self.debugger = debugger
        self.debugger.on_process_state_changed.subscribe(
            self._handle_process_change)
        self.debugger.on_frame_changed.subscribe(self._handle_frame_change)

    def _handle_process_change(self, state, event_data):
        if state == ProcessState.Stopped:
            self.update_registers()

    def _handle_frame_change(self, frame):
        self.update_registers()

    @require_gui_thread
    def _update_register_gui(self, registers):
        """
        @type registers: list of debugee.Register
        """
        for widget in self.get_children():
            self.remove(widget)

        for register in registers:
            label = Gtk.Label.new("{} = {}".format(register.name,
                                                   register.value))
            label.set_halign(Gtk.Align.START)
            row = Gtk.ListBoxRow.new()
            row.add(label)
            self.add(row)

        self.show_all()

    def update_registers(self):
        run_on_gui(self._update_register_gui,
                   self.debugger.variable_manager.get_registers())


class MemoryGrid(Gtk.Grid):
    def __init__(self, debugger, width, height):
        super(MemoryGrid, self).__init__()

        self.debugger = debugger
        self.width = width
        self.height = height
        self.address = None

        self.row_labels = []
        self.byte_rows = []
        self.ascii_rows = []

        self.set_column_spacing(2)
        self.set_row_spacing(2)

        self.set_margin_left(10)

        for x in xrange(1, height + 1):
            self.row_labels.append(self._create_row_label(x))
            self.byte_rows.append([])
            self.ascii_rows.append([])
            for y in xrange(1, width + 1):
                self.byte_rows[-1].append(self._create_block_view(x, y))
            for y in xrange(width + 1, width * 2 + 1):
                self.ascii_rows[-1].append(self._create_ascii_block_view(x, y))

        self.attach(self._create_column_heading("Address"), 0, 0, 1, 1)
        self.attach(self._create_column_heading("Byte value"), 1, 0, width, 1)
        self.attach(self._create_column_heading("ASCII value"), width + 1, 0, width, 1)

    @require_gui_thread
    def load_address(self, address):
        """
        Loads an address into the view.
        The address should be a hexadecimal string starting with 0x/0X or
        a name of a variable.
        @type address: str
        """
        address, address_int = self._parse_address(address)

        if address_int is None:
            return

        memory = self.debugger.variable_manager.get_memory(address,
                                                           self.width *
                                                           self.height)

        for i, row in enumerate(self.byte_rows):
            for j, block in enumerate(row):
                index = i * self.width + j
                value = "?"

                if index < len(memory):
                    value = str(memory[index])

                block.set_label(value)

        for i, row in enumerate(self.ascii_rows):
            for j, block in enumerate(row):
                index = i * self.width + j
                value = "?"

                if index < len(memory):
                    value = memory[index]
                    if value <= 32 or value >= 127:
                        value = ord(".")
                    value = chr(value)

                block.set_label(value)

        for i, label in enumerate(self.row_labels):
            text = hex(address_int)

            if text[-1] == "L":
                text = text[:-1]

            label.set_label(text)
            address_int += self.width

    @require_gui_thread
    def _create_row_label(self, row):
        view = Gtk.Label()
        view.set_label("?")
        view.set_margin_right(20)
        self.attach(view, 0, row, 1, 1)

        return view

    @require_gui_thread
    def _create_block_view(self, row, column, width=1, height=1):
        view = Gtk.Label()
        view.set_label("?")
        view.set_margin_left(5)
        view.set_margin_right(5)

        if column == self.width:
            view.set_margin_right(15)

        self.attach(view, column, row, width, height)

        return view

    @require_gui_thread
    def _create_ascii_block_view(self, row, column, width=1, height=1):
        view = Gtk.Label()
        view.set_label("?")
        view.set_margin_left(5)
        view.set_margin_right(5)
        self.attach(view, column, row, width, height)

        return view

    def _create_column_heading(self, text):
        view = Gtk.Label.new()
        view.set_markup("<b>{}</b>".format(text))

        return view

    def _parse_address(self, address):
        """
        Parses the given address and returns tuple (hex address, int address).
        The input address should either be a hex string starting with 0x/0X
        or a name of a variable.
        @type address: str
        @rtype: tuple of (str, int)
        """
        if re.match("^0(x|X)", address):
            try:
                return (address, int(address, 16))
            except:
                return (None, None)
        else:
            variable = self.debugger.variable_manager.get_variable(address)
            if not variable or not variable.address:
                return (None, None)
            else:
                address = variable.address
                return (address, int(address, 16))


class AddressInput(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self)

        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.label_row = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        self.label = Gtk.Label().new("Hex address or expression")
        self.label_row.pack_start(self.label, False, False, 0)

        self.input_row = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        self.address_input = Gtk.Entry()
        self.address_input.set_editable(True)

        self.confirm_button = Gtk.Button()
        self.confirm_button.set_label("Load")

        self.input_row.pack_start(self.address_input, False, False, 0)
        self.input_row.pack_start(self.confirm_button, False, False, 0)

        self.pack_start(self.label_row, False, False, 2)
        self.pack_start(self.input_row, False, False, 0)

        self.set_margin_left(10)

        self.on_address_selected = EventBroadcaster()

        self.confirm_button.connect("clicked",
                                    lambda *x: self.on_address_selected.notify(
                                        self.address_input.get_text()))

    def set_enabled(self, value):
        """
        Sets whether the input should be enabled.
        @type value: bool
        """
        self.confirm_button.set_sensitive(value)
        self.address_input.set_sensitive(value)


class MemoryView(Gtk.ScrolledWindow):
    """
    Displays value of raw memory in a grid.
    Enables selection of which memory will be shown.
    """
    def __init__(self, debugger):
        """
        @type debugger: debugger.Debugger
        """
        Gtk.ScrolledWindow.__init__(self)

        self.address_input = AddressInput()
        self.address_input.set_enabled(False)
        self.memorygrid = MemoryGrid(debugger, 20, 8)

        self.wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.wrapper.pack_start(self.address_input, False, False, 10)
        self.wrapper.pack_start(self.memorygrid, False, False, 10)

        self.add(self.wrapper)

        self.address_input.on_address_selected.subscribe(
            lambda address: self.memorygrid.load_address(address))

        debugger.on_process_state_changed.subscribe(self._handle_process_state_change)

    def _handle_process_state_change(self, state, data):
        """
        @type state: enums.ProcessState
        @type data: debugger.ProcessStoppedEventData
        """
        if state == ProcessState.Stopped:
            self.address_input.set_enabled(True)
        else:
            self.address_input.set_enabled(False)
