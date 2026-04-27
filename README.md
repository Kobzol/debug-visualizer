Devi (debug visualizer)
=======================

Devi is a graphical debugger frontend that visualizes the debugged
program's memory in a form of an object diagram. It can be used for
debugging C/C++ programs with the attached GDB 7.11.

It contains a self-contained communication library that can be adapted
to work with various other debuggers (it can be found in the package
`debugger`).

The application is licensed under GNU GPLv3.
Resource attributions can be found in CREDITS.

This software work has been created as a part of a bachelor thesis
at VŠB-TUO: Technical University of Ostrava. The text of the thesis
can be found in the folder `thesis`.

Dependencies
============
* `Python 2.7.x`
* `GTK3 3.10.8+`
* `g++`
* python packages `enum34`, `matplotlib`, `clang`
* debian packages `python-dev`, `clang-3.6`, `texinfo`
* (optional) python package `pytest` (for tests)
* (optional) python package `epydoc` (for documentation generation)
* (optional, only on 64-bit OS) debian package `g++-multilib` (for compiling test binaries)

Quick package installation
`sudo apt-get install python-enum34 python-matplotlib python-clang-3.6
clang-3.6 g++ texinfo python-dev python-pytest python-epydoc`


Build
=====
The build will download and compile a source distribution of GDB 7.11.

Use Waf
```
./waf download (this will install necessary packages using Aptitude)
./waf configure
./waf build
```
or just launch the attached install script
```
./install.sh
```

Launch
======
Use Python directly
```
python gui/initialize.py [path_to_debugged_binary]
```
or use the attached launch script
```
./start.sh
```

You can try the attached example programs (they are placed in
`build/examples` after build).

Docker
======

A Dockerfile has been put together based on Ubuntu 14.04 from when the project
was built. It doesn't copy the whole app in, assuming that the repo will be
bind-mounted in so the code can still be edited.

The project can be run inside a Docker container but with the host UI, by
forwarding in an X11 UNIX socket - i.e. bind mounting the socket with
`-v /tmp/.X11-unix:/tmp/.X11-unix`.

### Example Docker usage:
```
docker build -t devi:dev .
docker run --rm -v /tmp/.X11-unix:/tmp/.X11-unix -v ./:/repo -e NO_AT_BRIDGE=1 -e DISPLAY=unix:0 -w /repo devi:dev python2.7 gui/initialize.py
```

### Notes on Docker setup

The processes under Docker probably won't have permission to use the socket by
default, so you may need to run the following from the host to allow them to
connect:

```
xhost +local:docker
```

GTK may warn about not being able to access the system accessibility bus:

```
** (initialize.py:80453): WARNING **: Couldn't connect to accessibility bus: Failed to connect to socket /run/user/1000/at-spi/bus: No such file or directory
```

This can be avoided by running the app with `NO_AT_BRIDGE=1` set as an environment variable.


More info on X11 in Docker: https://stackoverflow.com/questions/24095968/docker-for-gui-based-environments