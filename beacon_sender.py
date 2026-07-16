'''

This program shows the way how to use
 socket client in python.

'''

#Process
#01. Preparing Socket : socket()
#02. Configuring Soccket and Connect to the Server : connect()
#03. Data　Yaritori : send(), recv()
#04. Closing the connection : close()

import sys
import asyncio
from bleak import BleakScanner
import socket

#HOST = '192.168.200.1'
HOST = '127.0.0.1'
PORT = 30000
BUFSIZE = 4096
FORMAT = 'utf-8'

def solve_args(args):
  if not len(args) == 4:
    print('command positionX positionY scanning_interval')
    exit()
  return int(args[1]),int(args[2]), int(args[3])

def make_connection(addr, port):
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect((addr,port))
  return client

def detection_callback(device,advertisement_data):
  print(f"Device: {device.address} | Name: {device.name} | RSSI: {advertisement_data.rssi}")

async def main():
  locx,locy,interval=solve_args(sys.argv)
  client=make_connection(HOST,PORT)
  while True:
    data=client.recv(BUFSIZE)
    print(f'receive message1: {data.decode(FORMAT)}')
    if data.decode(FORMAT) == 'accepted':
      data=f'location|x:{locx}|y:{locy}'
      client.sendall(data.encode(FORMAT))
      break
    else:
      continue

  while True:
    data=client.recv(BUFSIZE)
    if data.decode(FORMAT) == 'start scanning':
      break

  msg=''
  scanner=BleakScanner(detection_callback)
  while True:
    await scanner.start()
    print('Scanning... ')
    await asyncio.sleep(interval)
    await scanner.stop()
    print('Scan stopped')
    msg=f'x:{locx}|y:{locy}'
    for addr, (dev, adv) in scanner.discovered_devices_and_advertisement_data.items():
        print(addr, dev, adv)
        print(f'addr:{addr}|dev:{dev}|rssi:{adv.rssi}|tx_power:{adv.tx_power}')
        msg+=f',DEVICE:{dev.name}|ADDR:{dev.address}|RSSI:{adv.rssi}|tx_power:{adv.tx_power}|UUID:{adv.service_uuids}'
    try:
        client.sendall(msg.encode(FORMAT))
        print(msg)
    except (BrokenPipeError, ConnectionResetError):
        print("Server disconnected. Shutting down client.")
        break
    

if __name__ == '__main__':
  asyncio.run(main())



