#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi


if [ $# -lt 1 ]; then
    echo "Usage: $0 <interface>"
    echo "Example: $0 tun0"
    exit 1
fi


INTERFACE=$1

ip tuntap add dev $INTERFACE mode tun
ip addr add 10.0.0.1/24 dev $INTERFACE
ip link set dev $INTERFACE up
echo "TUN interface $INTERFACE created"
echo "Server TUN interface $INTERFACE configured with IP 10.0.0.1/24"

echo 1 > /proc/sys/net/ipv4/ip_forward
echo "IP forwarding enabled"


echo "Setup completed successfully"
