# -*- coding: utf-8 -*-

import os
import sys
import gettext
import locale

import paths
sys.path.append(paths.DIR_GUI)
sys.path.append(paths.DIR_DEBUGGER)

from config import Config
from app import VisualiserApp
 
if __name__ == '__main__':
  config = Config()
  app = VisualiserApp(config)
  app.start()
