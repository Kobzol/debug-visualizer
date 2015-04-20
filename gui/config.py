# -*- coding: utf-8 -*-

import os
import paths

class Config(object):
	def __init__(self):
		self.ui_dir = os.path.join(paths.DIR_ROOT, paths.DIR_RES, "gui")
		self.main_window_gui = self.get_ui_path("main_window.glade")
		
	def get_ui_path(self, path):
		return os.path.join(self.ui_dir, path)
