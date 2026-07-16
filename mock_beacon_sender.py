import sys
import time
import socket
import random

HOST = '127.0.0.1'
PORT = 30000
BUFSIZE = 65536
FORMAT = 'utf-8'

def solve_args(args):
  if not len(args) == 4:
    print('command positionX positionY scanning_interval')
    sys.exit()
  return int(args[1]), int(args[2]), int(args[3])

def make_connection(addr, port):
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect((addr,port))
  return client

def main():
  locx, locy, interval = solve_args(sys.argv)
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
    
    # We pretend we always see "Device A" and "Device B", but with slightly randomized RSSI
    rssi_a = random.randint(-80, -60)
    rssi_b = random.randint(-90, -70)
    
    msg += f',DEVICE:Device A|ADDR:11:22:33:44:55:66|RSSI:{rssi_a}|tx_power:12|UUID:[]'
    msg += f',DEVICE:Device B|ADDR:AA:BB:CC:DD:EE:FF|RSSI:{rssi_b}|tx_power:None|UUID:[]'
    
    try:
        client.sendall(msg.encode(FORMAT))
        print(f"Sent mock data: {msg}")
    except (BrokenPipeError, ConnectionResetError):
        print("Server disconnected. Shutting down client.")
        break

if __name__ == '__main__':
  main()
