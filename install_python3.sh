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
echo $PATH 