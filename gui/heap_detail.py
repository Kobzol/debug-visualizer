# -*- coding: utf-8 -*-

from gi.repository import Gtk

import datetime
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure

from enums import ProcessState


class HeapDetail(Gtk.ScrolledWindow):
    def __init__(self, debugger):
        """
        @type debugger: debugger.Debugger
        """
        Gtk.ScrolledWindow.__init__(self)
        self.debugger = debugger
        self.debugger.heap_manager.on_heap_change.subscribe(
            lambda heap: self._handle_heap_change(heap))
        self.debugger.on_process_state_changed.subscribe(
            lambda state, data: self._handle_process_change(state))
        self.sizes = []
        self.times = []

        figure = Figure()
        self.axis = figure.add_subplot(111)

        self.axis.set_xlabel('time [s]')
        self.axis.set_ylabel('heap size [MiB]')

        self.canvas = FigureCanvas(figure)
        self.canvas.set_size_request(-1, 100)
        self.add_with_viewport(self.canvas)

    def redraw(self):
        self.axis.plot(self.times, self.sizes)
        self.canvas.queue_draw()

    def _reset(self):
        self.sizes = []
        self.times = []

    def _handle_process_change(self, state):
        """
        @type state: enums.ProcessState
        """
        if state == ProcessState.Exited:
            self._reset()

    def _handle_heap_change(self, heap):
        """
        @type heap: list of debugee.HeapBlock
        """
        size = 0
        for block in heap:
            size += block.size

        self.sizes.append(size)
        self.times.append(datetime.datetime.now())
        self.redraw()
