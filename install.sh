#!/bin/bash
wget https://www.python.org/ftp/python/3.6.10/Python-3.6.10.tgz
tar zxfv Python-3.6.10.tgz
rm Python-3.6.10.tgz
find ./Python-3.6.10/Python -type d | xargs chmod 0755
cd Python-3.6.10
./configure --prefix=$PWD/Python-3.6.10/Python
make
make install
export PATH=$CWD:$PATH 
python3 msys.py jar mingw-w64-x86_64-gtk4 mingw-w64-x86_64-libadwaita mingw-w64-x86_64-gstreamer --name gtk_native.jar --class GtkNative --package gtk_native --path win --output lib
mvn install:install-file -Dfile=lib/gtk_native.jar -DgroupId="io.github.hamza-Algohary" -DartifactId=gtk_native -Dversion=0.1.0 -Dpackaging=jar -DgeneratePom=true