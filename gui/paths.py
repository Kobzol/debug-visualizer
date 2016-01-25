import os
import subprocess

DIR_GUI = os.path.dirname(os.path.abspath(__file__))
DIR_ROOT = os.path.dirname(DIR_GUI)

DIR_DEBUGGER = os.path.join(DIR_ROOT, "debugger")
DIR_RES = os.path.join(DIR_ROOT, "res")

lldb_loc_proc = subprocess.Popen(["lldb", "-P"], stdout=subprocess.PIPE)
LLDB_LOCATION = lldb_loc_proc.stdout.readline().strip()


def root_path(path):
    return os.path.join(DIR_ROOT, path)


def get_resource(path):
    return os.path.join(DIR_RES, path)
