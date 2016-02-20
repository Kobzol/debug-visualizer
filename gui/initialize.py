# -*- coding: utf-8 -*-

import paths
import sys
from config import Config

sys.path.append(paths.DIR_DEBUGGER)

from app import VisualiserApp

if __name__ == '__main__':
    Config.preload()
    app = VisualiserApp()
    app.start()
