# -*- coding: utf-8 -*-

import os

DIR_GUI = os.path.dirname(os.path.abspath(__file__))
DIR_ROOT = os.path.dirname(DIR_GUI)

DIR_DEBUGGER = os.path.join(DIR_ROOT, "debugger")
DIR_RES = os.path.join(DIR_ROOT, "res")


def get_root_path(path):
    return os.path.join(DIR_ROOT, path)


def get_resource(path):
    return os.path.join(DIR_RES, path)
