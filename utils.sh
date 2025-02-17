#!/usr/bin/env sh

get-ssid() {
  nmcli -t -f active,ssid dev wifi | egrep '^yes' | cut -d\: -f2
}
