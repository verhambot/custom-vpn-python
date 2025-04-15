# Custom VPN Implementation in Python

<br>

### NOTE : 
This project is purely demonstrative and does not strive to be a replacement for reputed VPN providers.

This implementation **does not** provide any sort of encryption whatsoever, although it is something I wish to implement in the future.

This project provides no guarantees, run this at your own risk.

<br>

## Installation
Simply clone the repository on both the client and server machines : `$ git clone https://github.com/verhambot/custom-vpn-python.git`

<br>

## Setup
Make sure you have `sudo` privileges enabled on your user as this is required to setup the network interface.

Also make sure that your server has a public IP address.

### 1. On Server
- Replace `SERVER_HOST_PORT` and `TUN_INTERFACE` in `main.py`.

- Uncomment the following lines :
  ```
  server = VPNServer(SERVER_HOST_IP, SERVER_HOST_PORT)
  server.run()
  ```

- Run `server-setup.sh` as `root` : `$ sudo ./server-setup.sh <TUN_INTERFACE>`.

  Note that the `<TUN_INTERFACE>` must be the same as the value in `main.py`

- Run `main.py` : `$ python3 main.py`

### 2. On Client
- Replace `SERVER_PUBLIC_IP`, `SERVER_HOST_PORT`, `CLIENT_VPN_IP` and `TUN_INTERFACE` in `main.py`.

- Uncomment the following lines :
  ```
  client = VPNClient(SERVER_PUBLIC_IP, SERVER_HOST_PORT, CLIENT_VPN_IP)
  client.run()
  ```

- Run `client-setup.sh` as `root` : `$ sudo ./client-setup.sh <TUN_INTERFACE> <CLIENT_VPN_IP>`.

  Note that the `<TUN_INTERFACE>` and `<CLIENT_VPN_IP>` must be the same as the value in `main.py` and `SERVER_HOST_PORT` must be the same port as in the server's version of `main.py`

- Run `main.py` : `$ python3 main.py`

<br>

## TODO
- Fix the fact that the server's VPN IP is hardcoded as `10.0.0.1/24`. This currently forces the client's VPN IPs to be `10.0.0.x/24`
- Better management of config variables and setup scripts
- Encryption
