# -*- coding: utf-8 -*-

from gi.repository import Gtk

class VisualiserApp(object):
	def __init__(self, config):
		self.config = config
		self.builder = Gtk.Builder()
		self.builder.add_from_file(config.main_window_gui)
		self.main_window = self.builder.get_object("main_window")
		self.main_window.connect("delete-event", Gtk.main_quit)
	
	def start(self):
		self.main_window.show_all()
		Gtk.main()