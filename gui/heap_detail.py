# -*- coding: utf-8 -*-

from gi.repository import Gtk, GObject

import time

from enums import ProcessState

import matplotlib
matplotlib.use('gtk3agg')
from matplotlib.backends.backend_gtk3agg\
    import FigureCanvasGTK3Agg as Canvas  # noqa
from matplotlib.figure import Figure  # noqa


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

        figure.subplots_adjust(bottom=0.3)

        self.canvas = Canvas(figure)
        self.add_with_viewport(self.canvas)

        self.heap_size = 0
        self.start_time = 0

    def redraw(self):
        self.axis.set_xlabel('time [s]')
        self.axis.set_ylabel('heap size [MiB]')
        self.axis.plot(self.times, self.sizes, "r")
        self.canvas.queue_draw()

    def _reset(self):
        self.sizes = []
        self.times = []
        self.heap_size = 0
        self.start_time = time.time()
        self.axis.cla()

    def _handle_process_change(self, state):
        """
        @type state: enums.ProcessState
        """
        if state == ProcessState.Launching:
            self._reset()
            self.redraw()
        elif state == ProcessState.Running:
            self._schedule_refresh()

    def _timer_tick(self):
        self.sizes.append(self.heap_size)
        self.times.append(time.time() - self.start_time)
        self.redraw()
        return self.debugger.process_state == ProcessState.Running

    def _schedule_refresh(self):
        GObject.timeout_add(1000,
                            self._timer_tick)

    def _handle_heap_change(self, heap):
        """
        @type heap: list of debugee.HeapBlock
        """
        size = 0
        for block in heap:
            size += block.size

        self.heap_size = size / 1024.0  # size in MiBs
