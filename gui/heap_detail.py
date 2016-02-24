# -*- coding: utf-8 -*-

from gi.repository import Gtk, GObject

import time

from debugger.enums import ProcessState
from gui_util import require_gui_thread, run_on_gui

import matplotlib

matplotlib.use('gtk3agg')
from matplotlib.backends.backend_gtk3agg\
    import FigureCanvasGTK3Agg as Canvas  # noqa
from matplotlib.figure import Figure  # noqa


class HeapGraph(Gtk.ScrolledWindow):
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


class HeapDetail(Gtk.ScrolledWindow):
    def __init__(self, debugger, *args, **kwargs):
        """
        @type debugger: debugger.Debugger
        """
        Gtk.ScrolledWindow.__init__(self, *args, **kwargs)

        self.debugger = debugger
        self.debugger.heap_manager.on_heap_change.subscribe(
            lambda heap: self._handle_heap_change(heap))

        self.wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        stats_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.stats_wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.stats_wrapper.set_margin_bottom(5)
        stats_wrapper.pack_start(self.stats_wrapper, False, False, 0)

        self.wrapper.pack_start(stats_wrapper, False, False, 0)

        self.block_tracker = self._create_stat_label()
        self.total_allocation_tracker = self._create_stat_label()
        self.total_deallocation_tracker = self._create_stat_label()
        self.total_memory_tracker = self._create_stat_label()

        self.graph = HeapGraph(debugger)
        self.wrapper.pack_start(self.graph, True, True, 0)

        self.add(self.wrapper)

        self.update_blocks([])

    @require_gui_thread
    def update_blocks(self, heap):
        """
        @type heap: list of debugee.HeapBlock
        """
        self.block_tracker.set_label("Block count: {}".format(len(heap)))
        self.total_allocation_tracker.set_label(
            "Total allocations: {}".format(
                self.debugger.heap_manager.get_total_allocations()))
        self.total_deallocation_tracker.set_label(
            "Total deallocations: {}".format(
                self.debugger.heap_manager.get_total_deallocations()))
        self.total_memory_tracker.set_label("Heap size: {}".format(
            sum([block.size for block in heap])))

    def _create_stat_label(self):
        """
        @rtype: Gtk.Widget
        """
        view = Gtk.Label()
        view.set_margin_left(5)
        view.set_justify(Gtk.Justification.LEFT)
        view.set_alignment(0, 0)

        self.stats_wrapper.pack_start(view, False, False, 0)

        return view

    def _handle_heap_change(self, heap):
        """
        @type heap: list of debugeee.HeapBlock
        """
        run_on_gui(self.update_blocks, heap)
