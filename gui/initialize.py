# -*- coding: utf-8 -*-

import paths
import sys
from config import Config
from app import VisualiserApp

sys.path.append(paths.DIR_DEBUGGER)


if __name__ == '__main__':
    Config.preload()
    app = VisualiserApp()
    app.start()
