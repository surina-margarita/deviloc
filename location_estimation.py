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
import time
import socket
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

PORT = 30000
SERVER = "192.168.200.1"
#SERVER = "0.0.0.0"
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
            tx_power_str = device_info.get('tx_power')
            if addr and rssi_str:
                if not tx_power_str or tx_power_str == 'None':
                    continue
                try:
                    rssi = float(rssi_str)
                    tx_power = float(tx_power_str)
                    if rssi < -70:
                        continue
                    
                    if addr not in devices_data:
                        devices_data[addr] = {'name': device_info.get('DEVICE', 'Unknown'), 'receivers': []}
                    devices_data[addr]['receivers'].append({
                        'x': rx, 
                        'y': ry, 
                        'rssi': rssi,
                        'tx_power': tx_power
                    })
                except ValueError:
                    continue
    return devices_data

def update_plot(clients, room_counts, ax, bg_img):
    ax.clear()
    
    if bg_img is not None:
        # On suppose que l'image couvre une zone de -5 à 15 (selon les coordonnées mock: 0, 10)
        ax.imshow(bg_img, extent=[-5, 15, -5, 15])
    else:
        ax.set_facecolor('#12121c')
        ax.text(0.5, 0.5, "Image non trouvée", ha='center', transform=ax.transAxes)
    
    # Affichage du nombre de personnes au centre de chaque "salle" (position du récepteur)
    for pos, count in room_counts.items():
        rx, ry = pos
        bbox_props = dict(boxstyle="circle,pad=0.5", fc="white", ec="#00d2ff", lw=2, alpha=0.9)
        ax.text(rx, ry, str(count), fontsize=24, color='#ff007f', fontweight='bold', ha='center', va='center', bbox=bbox_props)
        ax.text(rx, ry-1.5, "People", fontsize=10, color='white', ha='center', va='center')
        
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    ax.set_xticks([])
    ax.set_yticks([])

    plt.pause(0.01)

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

  plt.style.use('dark_background')
  plt.ion()
  fig, ax = plt.subplots(figsize=(8, 8))
  fig.patch.set_facecolor('#12121c')

  active_devices = {}
  TIME_WINDOW = 10.0
  
  try:
      bg_img = mpimg.imread('map.png')
  except FileNotFoundError:
      bg_img = None
      print("map.png not found, continuing without background.")

  while True:
    for c in clients:
      rcv=clients[c]['sock'].recv(BUFSIZE)
      if not rcv:
          print(f"Client {c} disconnected")
          sys.exit(1)
      clients[c]['rcv']=rcv.decode(FORMAT)
      
    devices_data = parse_received_data(clients)
    current_time = time.time()
    
    # Update timestamps for devices with strong enough signal
    for addr, data in devices_data.items():
        if not data['receivers']:
            continue
        # Find the receiver with the strongest RSSI
        best_receiver = max(data['receivers'], key=lambda r: r['rssi'])
        active_devices[addr] = {
            'time': current_time,
            'room_x': best_receiver['x'],
            'room_y': best_receiver['y']
        }
        
    # Prune old devices
    active_devices = {addr: info for addr, info in active_devices.items() if current_time - info['time'] <= TIME_WINDOW}
    
    room_counts = {}
    for addr, info in active_devices.items():
        pos = (info['room_x'], info['room_y'])
        room_counts[pos] = room_counts.get(pos, 0) + 1
    
    print("---------Room Counts-------------")
    for pos, count in room_counts.items():
        print(f"Room at {pos}: {count} people")
    print("---------------------------------")
    
    update_plot(clients, room_counts, ax, bg_img)

except KeyboardInterrupt:
  print()
