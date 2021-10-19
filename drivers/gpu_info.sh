#!/bin/sh -e

echo "GPU devices"
lspci -k | grep -EA3 'VGA|3D|Display'
echo

echo "Current OpenGL implementation"
glxinfo | grep -i vendor
echo

echo "Providers"
xrandr --listproviders
echo

echo "Monitors"
xrandr --listmonitors
echo

echo "Active monitors"
xrandr --listactivemonitors
