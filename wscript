#!/usr/bin/env python

from __future__ import print_function

import os
import shutil
import subprocess
import urllib2
import tarfile

gdb_build_dir = os.path.abspath("./build/gdb-build")
gdb_extract_dir = os.path.abspath("./build/gdb-source")
gdb_src_dir = os.path.join(gdb_extract_dir, "gdb-7.10.1")
gdb_src_zip = os.path.abspath("./build/gdb-7.10.1.tar.gz")
gdb_archive_length = 34526368


def build_gdb():
    if not os.path.isfile(gdb_src_zip) or os.path.getsize(gdb_src_zip) != gdb_archive_length:
        print("Downloading GDB 7.10.1...")

        gdb = urllib2.urlopen("http://ftp.gnu.org/gnu/gdb/gdb-7.10.1.tar.gz")
        if gdb.getcode() != 200:
            raise BaseException("GDB could not be downloaded, error code {}".format(gdb.getcode()))

        info = gdb.info()
        length = info["Content-Length"]
        total_read = 0

        with open(gdb_src_zip, 'wb') as archive:
            while True:
                data = gdb.read(1024)
                if len(data) < 1:
                    break
                else:
                    total_read += len(data)
                    archive.write(data)
                    print("\r{:0.2f} %".format((total_read / float(length)) * 100.0), end="")
        print("\n")
    print("Extracting GDB...")

    with tarfile.open(gdb_src_zip) as archive:
        archive.extractall(gdb_extract_dir)

    cwd = os.getcwd()
    os.chdir(gdb_src_dir)

    print("Compiling and installing GDB...")

    result = subprocess.call("./configure --prefix={0} --bindir={0} --with-python"
                             .format(gdb_build_dir), shell=True)
    try:
        if result == 0:
            result == subprocess.call("make -j4", shell=True)

            if result != 0:
                raise BaseException("GDB could no be compiled")
            else:
                result == subprocess.call("make install", shell=True)

                if result != 0:
                    raise BaseException("GDB could not be installed")
        else:
            raise BaseException("GDB could not be configured")
    except Exception as exc:
        print(exc.message)
        shutil.rmtree(gdb_extract_dir, ignore_errors=True)
        shutil.rmtree(gdb_build_dir, ignore_errors=True)

    os.chdir(cwd)


def patch_lldb(conf):
    exit_status = subprocess.call(["./util/lldb_patch.sh", conf.options.lldb],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

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
    conf.check_python_module("clang.cindex")


def build(ctx):
    ctx.recurse("debugger")
    build_gdb()


def download(ctx):
    apt_args = ["g++", "texinfo", "python-dev", "python-pip", "python-matplotlib",
                "python-enum34" "python-jsonpickle", "python-epydoc", "python-pytest", "python-clang-3.6"]
    subprocess.check_call(["sudo", "apt-get", "install"] + apt_args)


def cleanall(ctx):
    import shutil
    shutil.rmtree("./docs", True)
    subprocess.call(["find", ".", "-name", "*.pyc", "-delete"])


def docs(ctx):
    subprocess.call(["epydoc", "epydoc", "-v", "--config", "epydoc"])
