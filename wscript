#!/usr/bin/env python

import subprocess


def patch_lldb(conf):
    exit_status = subprocess.call(["./util/lldb_patch.sh", conf.options.lldb])

    if exit_status == 0:
        print("LLDB patched")
    else:
        print("LLDB not found")


def options(opt):
    opt.add_option("-l", "--lldb", default="", action="store", help="version of LLDB to use")

    opt.load("python")
    opt.load("compiler_cxx")


def configure(conf):
    conf.load("python")
    conf.load("compiler_cxx")

    patch_lldb(conf)

    conf.check_python_version((2, 7, 0))
    if conf.options.lldb:
        conf.check_python_module("lldb")
    conf.check_python_module("enum")
    conf.check_python_module("gi.repository.Gtk")
    conf.check_python_module("jsonpickle")
    conf.check_python_module("epydoc")
    conf.check_python_module("matplotlib")


def build(ctx):
    ctx.recurse("debugger/mi")


def cleanall(ctx):
    import shutil
    shutil.rmtree("./docs", True)
    subprocess.call(["find", ".", "-name", "*.pyc", "-delete"])


def docs(ctx):
    subprocess.call(["epydoc", "epydoc", "-v", "--config", "epydoc"])
