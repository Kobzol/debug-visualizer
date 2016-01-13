import re
from gi.repository import Gtk

from enums import ProcessState
from events import EventBroadcaster


class MemoryGrid(Gtk.Grid):
    def __init__(self, debugger, width, height):
        super(MemoryGrid, self).__init__()

        self.debugger = debugger
        self.width = width
        self.height = height
        self.address = None

        self.row_labels = []
        self.rows = []

        self.set_column_spacing(2)
        self.set_row_spacing(2)

        self.set_margin_left(10)

        for x in xrange(1, height + 1):
            self.row_labels.append(self._create_row_label(x))
            self.rows.append([])
            for y in xrange(1, width + 1):
                self.rows[-1].append(self._create_block_view(x, y))

    def _create_row_label(self, row):
        view = Gtk.Label()
        view.set_label("?")
        view.set_margin_right(20)
        self.attach(view, 0, row, 1, 1)

        return view

    def _create_block_view(self, row, column, width=1, height=1):
        view = Gtk.Button()
        view.set_label("?")
        self.attach(view, column, row, width, height)

        return view

    def load_address(self, address):
        if re.match("^0(x|X)", address):
            try:
                address_int = int(address, 16)
            except:
                return
        else:
            variable = self.debugger.variable_manager.get_variable(address)
            if not variable:
                return
            else:
                address = variable.address
                address_int = int(address, 16)

        memory = self.debugger.variable_manager.get_memory(address, self.width * self.height)

        for i, row in enumerate(self.rows):
            for j, block in enumerate(row):
                index = i * self.width + j
                value = "?"

                if index < len(memory):
                    value = str(memory[index])

                block.set_label(value)

        for i, label in enumerate(self.row_labels):
            text = hex(address_int)
            label.set_label(text)
            address_int += self.width


class AddressInput(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self)

        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.label_row = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        self.label = Gtk.Label().new("Hex address or variable name")
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

        self.confirm_button.connect("clicked", lambda *x: self.on_address_selected.notify(self.address_input.get_text()))


class MemoryView(Gtk.ScrolledWindow):
    """
    Displays value of raw memory in a grid.
    Enables selection of which memory will be shown.
    """
    def __init__(self, debugger):
        Gtk.ScrolledWindow.__init__(self)

        self.address_input = AddressInput()
        self.memorygrid = MemoryGrid(debugger, 10, 4)

        self.wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.wrapper.pack_start(self.address_input, False, False, 10)
        self.wrapper.pack_start(self.memorygrid, False, False, 0)

        self.add(self.wrapper)

        self.address_input.on_address_selected.subscribe(lambda address: self.memorygrid.load_address(address))
