#!/bin/bash

LLDB_VERSION="3.6"

if [ "$#" -ge 1 ]; then
    LLDB_VERSION=$1  
fi

cd /usr/lib/llvm-$LLDB_VERSION/lib/python2.7/site-packages/lldb || exit 1
sudo rm _lldb.so
sudo ln -s ../../../liblldb.so.1 _lldb.so
sudo rm libLLVM-$LLDB_VERSION.0.so.1
sudo ln -s ../../../libLLVM-$LLDB_VERSION.0.so.1 libLLVM-$LLDB_VERSION.0.so.1
sudo rm libLLVM-$LLDB_VERSION.so.1
sudo ln -s ../../../libLLVM-$LLDB_VERSION.0.so.1 libLLVM-$LLDB_VERSION.so.1
