import sys
import time
import socket
import random

HOST = '127.0.0.1'
PORT = 30000
BUFSIZE = 65536
FORMAT = 'utf-8'

def solve_args(args):
  if len(args) < 4:
    print('command positionX positionY scanning_interval [num_devices]')
    sys.exit()
  num_devices = 2
  if len(args) >= 5:
    num_devices = int(args[4])
  return int(args[1]), int(args[2]), int(args[3]), num_devices

def make_connection(addr, port):
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect((addr,port))
  return client

def main():
  locx, locy, interval, num_devices = solve_args(sys.argv)
  client = make_connection(HOST, PORT)
  
  # Handshake phase
  while True:
    data = client.recv(BUFSIZE)
    print(f'receive message: {data.decode(FORMAT)}')
    if data.decode(FORMAT) == 'accepted':
      data = f'location|x:{locx}|y:{locy}'
      client.sendall(data.encode(FORMAT))
      break
    else:
      continue

  # Wait for the trigger
  while True:
    data = client.recv(BUFSIZE)
    if data.decode(FORMAT) == 'start scanning':
      break

  # Infinite scanning loop (Mocked)
  while True:
    print('Scanning (MOCK)... ')
    time.sleep(interval)
    print('Scan stopped (MOCK)')
    
    # Generate some mock data
    msg = f'x:{locx}|y:{locy}'
    
    for i in range(num_devices):
        rssi = random.randint(-80, -60)
        # Ensure unique MAC addresses across different senders and devices
        mac = f"00:11:22:{locx % 256:02X}:{locy % 256:02X}:{i % 256:02X}"
        msg += f',DEVICE:Device {i}|ADDR:{mac}|RSSI:{rssi}|tx_power:12|UUID:[]'
        
    try:
        client.sendall(msg.encode(FORMAT))
        print(f"Sent mock data: {msg}")
    except (BrokenPipeError, ConnectionResetError):
        print("Server disconnected. Shutting down client.")
        break

if __name__ == '__main__':
  main()
