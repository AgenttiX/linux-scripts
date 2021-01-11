#!/bin/sh -e
if [ ! $# -eq 1 ]; then
    echo "Give the path of the mounted partition as an argument"
    exit 1
fi
if [ ! -d $1 ]; then
    echo "The given argument should be a directory"
    exit 2
fi
if [ ! -f "/usr/bin/f3write" ]; then
    sudo apt-get install f3
fi
f3write $1
f3read $1
