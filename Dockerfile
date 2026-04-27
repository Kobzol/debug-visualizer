FROM ubuntu:14.04 AS base

RUN DEBIAN_FRONTEND=noninteractive apt-get update

FROM base AS pybuild

# Use a substitute from https://www.gnu.org/prep/ftp.html for faster downloading
ARG GNUFTP_BASEURL=http://ftp.gnu.org/gnu/

WORKDIR /dockerbuild

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y wget python2.7

COPY waf wscript /dockerbuild/

# Run the waf command so that it gets bootstrapped
RUN python2.7 ./waf --version

# Install required APT packages
RUN python2.7 ./waf download
RUN python2.7 ./waf configure

# Pre-download GDB (gives better progress bar than wscript)
WORKDIR /dockerbuild/build
RUN wget "${GNUFTP_BASEURL}gdb/gdb-7.11.tar.gz" &&\
    echo "9382f5534aa0754169e1e09b5f1a3b77d1fa8c59c1e57617e06af37cb29c669a  gdb-7.11.tar.gz" | sha256sum -c -

WORKDIR /dockerbuild

# Run the GDB build. It uses --with-python flags so may well need to be done in
# the same container as the python install
RUN python2.7 ./waf build_gdb

# Build everything else
RUN python2.7 ./waf build

# ENTRYPOINT python2.7 gui/initialize.py