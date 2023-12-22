#!/usr/bin/env bash
set -e

# This is a very preliminary script. Use with caution.

systemctl stop pve-cluster
systemctl stop corosync
pmxcfs -systemctl

rm /etc/pve/corosync.conf
rm -r /etc/corosync/*

killall pmxcfs
systemctl start pve-cluster

rm /var/lib/corosync/*
