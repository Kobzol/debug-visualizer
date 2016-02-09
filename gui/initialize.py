# -*- coding: utf-8 -*-

import sys

import paths

sys.path.append(paths.DIR_DEBUGGER)


from config import Config
from app import VisualiserApp


if __name__ == '__main__':
    Config.preload()
    app = VisualiserApp()
    app.start()
