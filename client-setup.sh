#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi


if [ $# -lt 2 ]; then
  echo "Usage: $0 <interface> <client_ip>"
  echo "Example (client): $0 tun0 10.0.0.2"
  exit 1
fi


INTERFACE=$1
CLIENT_IP=$2

ip tuntap add dev $INTERFACE mode tun
ip addr add $CLIENT_IP/24 dev $INTERFACE
ip link set dev $INTERFACE up
echo "TUN interface $INTERFACE created"
echo "Client TUN interface $INTERFACE configured with IP $CLIENT_IP/24"

echo 1 > /proc/sys/net/ipv4/ip_forward
echo "IP forwarding enabled"


echo "Setup completed successfully"
