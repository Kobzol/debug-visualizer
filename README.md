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

This software work has been created as a part of school thesis
at VŠB-TUO: Technical University of Ostrava. The text of the thesis
can be found in the folder `thesis`.

Build
=====
The build will also download and compile a source distribution of GDB 7.11.

Use Waf
```
./waf download
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

