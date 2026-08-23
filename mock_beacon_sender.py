import sys
import time
import socket
import random

HOST = '127.0.0.1'
PORT = 30000
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
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
    
    msg = f'x:{locx}|y:{locy}'
    
    # Generate 30 mock devices
    for i in range(1, 31):
        # We need rssi >= -70 to not be ignored by the server's filter!
        # Make specific devices close to specific receivers so trilateration works
        if locx == 800 and locy == 1100 and 1 <= i <= 10:
            rssi = random.randint(-45, -35)
        elif locx == 800 and locy == 1700 and 11 <= i <= 20:
            rssi = random.randint(-45, -35)
        elif locx == 1250 and locy == 1200 and 21 <= i <= 30:
            rssi = random.randint(-45, -35)
        else:
            rssi = random.randint(-69, -65)
            
        mac = f"11:22:33:44:55:{i:02d}"
        msg += f',DEVICE:MockDev_{i}|ADDR:{mac}|RSSI:{rssi}|tx_power:12|UUID:[]'
        
    
    try:
        client.sendall(msg.encode(FORMAT))
        print(f"Sent mock data: {msg}")
    except (BrokenPipeError, ConnectionResetError):
        print("Server disconnected. Shutting down client.")
        break

if __name__ == '__main__':
  main()
