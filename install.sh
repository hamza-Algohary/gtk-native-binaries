#!/bin/bash
wget https://www.python.org/ftp/python/3.12.5/Python-3.12.5.tgz
tar xzf Python-3.12.5.tgz
cd Python-3.12.5
mkdir -p /tmp/python/3.12.5
./configure --prefix=/tmp/python/3.12.5/ --enable-optimizations --with-lto --with-computed-gotos --with-system-ffi
make -j "$(nproc)"
make altinstall

cd ..
make init
/tmp/python/3.12.5/bin/python3.12 msys.py jar mingw-w64-x86_64-gtk4 mingw-w64-x86_64-libadwaita mingw-w64-x86_64-gstreamer --name gtk_native.jar --class GtkNative --package gtk_native --path win --output lib