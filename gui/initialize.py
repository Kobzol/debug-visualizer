# -*- coding: utf-8 -*-

import sys
import prctl
import resource

import paths
sys.path.append(paths.DIR_GUI)
sys.path.append(paths.DIR_DEBUGGER)
sys.path.append(paths.LLDB_LOCATION)


from config import Config
from app import VisualiserApp


if __name__ == '__main__':
    prctl.set_dumpable(True)
    resource.setrlimit(resource.RLIMIT_CORE, (resource.RLIM_INFINITY,resource.RLIM_INFINITY))

    Config.preload()
    app = VisualiserApp()
    app.start()
