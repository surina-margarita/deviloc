'''

This program shows the way how to make your pc
 into server with socket in python.

 Ctrl + Break : quit

'''

#-----------------------------------------------
#Process
#01. Socket Making : socket()
#02. Address & Port : bind()
#03. Waiting the connection : listen()
#04. Getting the socket : accept()
#05. Data Yaritori : send(), recv()
#06. Closing the connection()
#-----------------------------------------------
import datetime
import socket
import sys

PORT = 30000
#SERVER = "192.168.200.1"
SERVER = "0.0.0.0"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
BUFSIZE = 4096

def make_socket(addr, port):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
  s.bind((addr,port))
  return s

def wait_clients(s_sock,client_num):
  clients={}
  while True:
    client, client_addr = s_sock.accept()
    print(f'[NEW CONNCTION] {client_addr} connected')
    data='accepted'
    client.sendall(data.encode(FORMAT))
    rcv=client.recv(BUFSIZE)
    data=rcv.decode(FORMAT)
    print(f'receive message:{data}')
    data_array=data.split('|')
    if not data_array[0] == 'location':
      continue
    clients[client_addr]={'addr':client_addr,'sock':client,'x':data_array[1].split(':')[1],'y':data_array[2].split(':')[1],'rcv':''}
    if len(clients) == client_num:
      break
  return clients


if not len(sys.argv)==2:
  print('command num_of_clients')
  exit()
num=int(sys.argv[1])

if not num>=3:
  print('error : command total_num_of_clients. Put an integer >= 3')
  exit()

try:
  server_socket=make_socket(SERVER,PORT)
  server_socket.listen()
  clients=wait_clients(server_socket, num)

  for c in clients:
    print(c)
    clients[c]['sock'].sendall('start scanning'.encode(FORMAT))


  while True:
    for c in clients:
      rcv=clients[c]['sock'].recv(BUFSIZE)
      clients[c]['rcv']=rcv.decode(FORMAT)
      print(f"client:{c}|rcv:{clients[c]['rcv']}")

except KeyboardInterrupt:
  print()
