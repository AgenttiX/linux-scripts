#!/bin/sh -e
# TODO: Work in progress

wget https://cdn.geekbench.com/Geekbench-5.4.0-Linux.tar.gz -O geekbench5.tar.gz
wget https://cdn.geekbench.com/Geekbench-4.3.3-Linux.tar.gz -O geekbench4.tar.gz
wget https://cdn.primatelabs.com/Geekbench-3.4.2-Linux.tar.gz -O geekbench3.tar.gz
wget https://cdn.primatelabs.com/Geekbench-2.4.3-Linux.tar.gz -O geekbench2.tar.gz
tar -xzf geekbench5.tar.gz
tar -xzf geekbench4.tar.gz
tar -xzf geekbench3.tar.gz
tar -xzf geekbench2.tar.gz
rm geekbench*.tar.gz
mv ./dist/* .
rm ./dist -r
