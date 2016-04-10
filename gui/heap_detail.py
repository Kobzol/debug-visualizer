# -*- coding: utf-8 -*-
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


class HeapDetail(Gtk.Box):
    def __init__(self, debugger, *args, **kwargs):
        """
        @type debugger: debugger.Debugger
        """
        Gtk.Box.__init__(self, *args, **kwargs)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.debugger = debugger
        self.debugger.heap_manager.on_heap_change.subscribe(
            lambda heap: self._handle_heap_change(heap))

        self.stats_wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.stats_wrapper.set_margin_bottom(5)
        self.pack_start(self.stats_wrapper, False, False, 0)

        self.block_tracker = self._create_stat_label()
        self.total_allocation_tracker = self._create_stat_label()
        self.total_deallocation_tracker = self._create_stat_label()
        self.total_memory_tracker = self._create_stat_label()

        self.graph = HeapGraph(debugger)
        self.pack_start(self.graph, True, True, 0)

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
        self.total_memory_tracker.set_label("Heap size: {} b".format(
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
