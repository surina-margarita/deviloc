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
import itertools
import numpy as np
import matplotlib.pyplot as plt

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

def estimate_location_4_devices(receivers):
    if len(receivers) < 3:
        return None
    
    # Calculate distances using Log-Distance Path Loss Model
    points = []
    for r_data in receivers:
        rssi = r_data['rssi']
        calibrated_tx_power = r_data['tx_power']
        
        #n = 2.5 # Path loss exponent for indoor environments
        n = 6.2
        distance_meters = 10 ** ((calibrated_tx_power - rssi) / (10 * n))
        r = distance_meters * 100 # Convert to cm
        points.append((r_data['x'], r_data['y'], r))
    
    valid_estimates = []
    for combo in itertools.combinations(points, 3):
        p1, p2, p3 = combo
        xa, ya, ra = p1
        xb, yb, rb = p2
        xc, yc, rc = p3
        
        x_ab = xb - xa
        y_ab = yb - ya
        rxy_ab2 = ra**2 - rb**2 - xa**2 + xb**2 - ya**2 + yb**2
        
        x_bc = xc - xb
        y_bc = yc - yb
        rxy_bc2 = rb**2 - rc**2 - xb**2 + xc**2 - yb**2 + yc**2
        
        denom_x = 2 * (x_ab * y_bc - x_bc * y_ab)
        denom_y = 2 * (y_ab * x_bc - x_ab * y_bc)
        
        if denom_x == 0 or denom_y == 0:
            continue
            
        x = (rxy_ab2 * y_bc - rxy_bc2 * y_ab) / denom_x
        y = (rxy_ab2 * x_bc - rxy_bc2 * x_ab) / denom_y
        
        valid_estimates.append((x, y))
            
    if not valid_estimates:
        return None
        
    avg_x = sum(e[0] for e in valid_estimates) / len(valid_estimates)
    avg_y = sum(e[1] for e in valid_estimates) / len(valid_estimates)
    
    return avg_x, avg_y

def update_plot(clients, estimated_locations, ax):
    ax.clear()
    ax.set_facecolor('#12121c')
    ax.grid(True, color='#2a2a3c', linestyle='--', linewidth=0.5)

    x = []
    y = []
    locator_x = []
    locator_y = []
    colors = []
    sizes = []
    labels = []

    beacon_color = '#00d2ff' # Cyan
    target_color = '#ff007f' # Neon Pink
    
    # Add beacons
    for c, client_info in clients.items():
        try:
            rx = float(client_info['x'])
            ry = float(client_info['y'])
            locator_x.append(rx)
            locator_y.append(ry)
            x.append(rx)
            y.append(ry)
            colors.append(beacon_color)
            sizes.append(150)
            pi_label = f"Pi {client_info['addr'][1]}"
            labels.append((rx, ry, pi_label, beacon_color))
        except ValueError:
            pass
            
    # Add targets
    for name, loc in estimated_locations.items():
        x.append(loc[0])
        y.append(loc[1])
        colors.append(target_color)
        sizes.append(300)
        labels.append((loc[0], loc[1], name, target_color))

    if x and y:
        ax.scatter(x, y, s=sizes, c=colors, edgecolor='white', linewidth=1.5, zorder=3)
        
    for lx, ly, text, color in labels:
        ax.text(lx, ly + 25, text, color=color, fontsize=12, ha='center', fontweight='bold')

    ax.set_title("Bluetooth Beacon Positioning System", color='white', fontsize=16, pad=20, fontweight='bold')
    if locator_x and locator_y:
        ax.set(xlim=(min(locator_x)-10, max(locator_x)+10), ylim=(min(locator_y)-10, max(locator_y)+10))
    else:
        ax.set(xlim=(-150, 150), ylim=(-150, 150))

    for spine in ax.spines.values():
        spine.set_visible(False)

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
    estimated_locations = {}
    for addr, data in devices_data.items():
        loc = estimate_location_4_devices(data['receivers'])
        if loc:
            print(f"Device: {data['name']} ({addr}) -> Estimated Location: x={loc[0]:.2f}, y={loc[1]:.2f}")
            estimated_locations[data['name']] = loc
        else:
            print(f"Device: {data['name']} ({addr}) -> Not enough receivers for estimation ({len(data['receivers'])}/3)")
    print("--------------------------------------")
    update_plot(clients, estimated_locations, ax)

except KeyboardInterrupt:
  print()
