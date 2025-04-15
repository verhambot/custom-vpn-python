import socket
import threading
import struct
import os
import fcntl
import time
import logging
import signal
import sys

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(levelname)s: %(message)s")

CLIENT_VPN_IP = "<REPLACE>"
SERVER_PUBLIC_IP = "<REPLACE>"
SERVER_HOST_IP = "0.0.0.0"
SERVER_HOST_PORT = <REPLACE>
KEEPALIVE_INTERVAL = 10
CLIENT_TIMEOUT = 30
TUN_INTERFACE = "<REPLACE>"
MTU = 65535

def setup_tun():
    TUNSETIFF = 0x400454ca
    IFF_TUN   = 0x0001
    IFF_NO_PI = 0x1000

    tun = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack("16sH", TUN_INTERFACE.encode(), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    return tun

class VPNServer:
    def __init__(self, ip, port):
        self.clients = {}
        self.lock = threading.Lock()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.tun = setup_tun()
        self.running = True

    def handle_client_packets(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(MTU)
                if data.startswith(b"KEEPALIVE"):
                    vpn_ip = data[9:].decode()
                    with self.lock:
                        self.clients[vpn_ip] = (addr, time.time())
                    logging.debug(f"Received KEEPALIVE from {vpn_ip} @ {addr}")
                else:
                    vpn_ip = socket.inet_ntoa(data[16:20])
                    with self.lock:
                        if vpn_ip in self.clients:
                            self.sock.sendto(data, self.clients[vpn_ip][0])
                            logging.debug(f"Forwarded packet to {vpn_ip}")
                    os.write(self.tun, data)
            except Exception as e:
                logging.error(f"Error in handle_client_packets: {e}")

    def handle_tun_packets(self):
        while self.running:
            try:
                packet = os.read(self.tun, MTU)
                dst_ip = socket.inet_ntoa(packet[16:20])
                with self.lock:
                    if dst_ip in self.clients:
                        self.sock.sendto(packet, self.clients[dst_ip][0])
                        logging.debug(f"Sent packet to {dst_ip}")
            except Exception as e:
                logging.error(f"Error in handle_tun_packets: {e}")

    def cleanup_clients(self):
        while self.running:
            time.sleep(KEEPALIVE_INTERVAL)
            now = time.time()
            with self.lock:
                before = len(self.clients)
                self.clients = {ip: (addr, ts) for ip, (addr, ts) in self.clients.items() if now - ts < CLIENT_TIMEOUT}
                after = len(self.clients)
                if before != after:
                    logging.info(f"Cleaned up clients: {before - after} removed")

    def shutdown(self, signum, frame):
        logging.info("Shutting down server...")
        self.running = False
        self.sock.close()
        os.close(self.tun)
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        threading.Thread(target=self.handle_client_packets, daemon=True).start()
        threading.Thread(target=self.handle_tun_packets, daemon=True).start()
        threading.Thread(target=self.cleanup_clients, daemon=True).start()
        logging.info("[SERVER] VPN server is running...")
        while self.running:
            time.sleep(1)


class VPNClient:
    def __init__(self, server_ip, server_port, vpn_ip):
        self.server_addr = (server_ip, server_port)
        self.vpn_ip = vpn_ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tun = setup_tun()
        self.running = True

    def send_keepalive(self):
        while self.running:
            try:
                msg = b"KEEPALIVE" + self.vpn_ip.encode()
                self.sock.sendto(msg, self.server_addr)
                logging.debug(f"Sent KEEPALIVE to server")
                time.sleep(KEEPALIVE_INTERVAL)
            except Exception as e:
                logging.error(f"Error in send_keepalive: {e}")

    def handle_tun_packets(self):
        while self.running:
            try:
                packet = os.read(self.tun, MTU)
                self.sock.sendto(packet, self.server_addr)
                logging.debug("Sent packet to server")
            except Exception as e:
                logging.error(f"Error in handle_tun_packets: {e}")

    def handle_server_packets(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(MTU)
                os.write(self.tun, data)
                logging.debug("Received packet from server")
            except Exception as e:
                logging.error(f"Error in handle_server_packets: {e}")

    def shutdown(self, signum, frame):
        logging.info("Shutting down client...")
        self.running = False
        self.sock.close()
        os.close(self.tun)
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        threading.Thread(target=self.send_keepalive, daemon=True).start()
        threading.Thread(target=self.handle_tun_packets, daemon=True).start()
        threading.Thread(target=self.handle_server_packets, daemon=True).start()
        logging.info(f"[CLIENT] VPN client {self.vpn_ip} is running...")
        while self.running:
            time.sleep(1)


# server = VPNServer(SERVER_HOST_IP, SERVER_HOST_PORT)
# server.run()

# client = VPNClient(SERVER_PUBLIC_IP, SERVER_HOST_PORT, CLIENT_VPN_IP)
# client.run()
