# -*- coding: utf-8 -*-

from gi.repository import Gtk

class VisualiserApp(object):
	def __init__(self, config):
		self.config = config
		self.builder = Gtk.Builder()
		self.builder.add_from_file(config.main_window_gui)
	
	def start(self):
		print("program started!")
	
