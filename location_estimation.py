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
import numpy as np

PORT = 30000
#SERVER = "192.168.200.1"
SERVER = "0.0.0.0"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
BUFSIZE = 65536

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

def parse_received_data(clients):
    devices_data = {}
    for c, client_info in clients.items():
        rcv = client_info.get('rcv', '')
        if not rcv:
            continue
        parts = rcv.split(',')
        if len(parts) == 0:
            continue
        try:
            rx = float(client_info['x'])
            ry = float(client_info['y'])
        except ValueError:
            continue

        for part in parts[1:]:
            if not part.startswith('DEVICE:'):
                continue
            fields = part.split('|')
            device_info = {}
            for field in fields:
                if ':' in field:
                    k, v = field.split(':', 1)
                    device_info[k] = v
            addr = device_info.get('ADDR')
            rssi_str = device_info.get('RSSI')
            if addr and rssi_str:
                try:
                    rssi = float(rssi_str)
                    r = abs(rssi)
                    if addr not in devices_data:
                        devices_data[addr] = {'name': device_info.get('DEVICE', 'Unknown'), 'receivers': []}
                    devices_data[addr]['receivers'].append({'x': rx, 'y': ry, 'r': r})
                except ValueError:
                    continue
    return devices_data

def estimate_location(receivers):
    # Stop condition : if less than 3 receivers, return None -> trilateration needs 3 points
    if len(receivers) < 3:
        return None
    
    # Extract points as (x, y, r)
    points = [(r['x'], r['y'], r['r']) for r in receivers]
    
    n = len(points)
    
    # Extraction of the last point as reference (point n)
    xn, yn, rn = points[-1]
    
    # A is a matrix of size (n-1) x 2
    A = []
    # B is a vector of size (n-1) x 1
    B = []
    
    # Construction of matrices A and B for the first n-1 points
    for i in range(n - 1):
        xi, yi, ri = points[i]
        
        # Row for matrix A
        A_row = [2 * (xi - xn), 2 * (yi - yn)]
        A.append(A_row)
        
        # Row for vector B
        B_row = (xi**2 - xn**2) + (yi**2 - yn**2) - (ri**2 - rn**2)
        B.append(B_row)
        
    A = np.array(A)
    B = np.array(B)
    
    # Mathematical resolution: X = (A^T * A)^(-1) * A^T * B
    # In Python, the lstsq function directly handles the pseudo-inverse in a stable manner
    try:
        X, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)
        return float(X[0]), float(X[1])
    except Exception as e:
        return None

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
      if not rcv:
          print(f"Client {c} disconnected")
          sys.exit(1)
      clients[c]['rcv']=rcv.decode(FORMAT)
    devices_data = parse_received_data(clients)
    print("---------Parsed data----------")
    print(devices_data)
    print("------------------------------")
    print("---------Estimated Locations----------")
    for addr, data in devices_data.items():
        loc = estimate_location(data['receivers'])
        if loc:
            print(f"Device: {data['name']} ({addr}) -> Estimated Location: x={loc[0]:.2f}, y={loc[1]:.2f}")
        else:
            print(f"Device: {data['name']} ({addr}) -> Not enough receivers for estimation ({len(data['receivers'])}/3)")
    print("--------------------------------------")

except KeyboardInterrupt:
  print()
