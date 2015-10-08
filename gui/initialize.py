# -*- coding: utf-8 -*-

import sys

import paths
sys.path.append(paths.DIR_GUI)
sys.path.append(paths.DIR_DEBUGGER)
sys.path.append(paths.LLDB_LOCATION)


from config import Config
from app import VisualiserApp
 
if __name__ == '__main__':
    config = Config()
    app = VisualiserApp(config)
    app.start()
