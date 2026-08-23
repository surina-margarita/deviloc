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
import itertools
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as patches
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
            return devices_data

def estimate_location_4_devices(receivers):
    if len(receivers) < 3:
        return None
    
    # Calculate distances
    points = []
    for r_data in receivers:
        rssi = r_data['rssi']
        tx_power = r_data['tx_power']
        
        calibrated_tx_power = tx_power
        if calibrated_tx_power > 100:
            corrected_tx_power = calibrated_tx_power - 256
            n = 5.8
            distance_meters = 10 ** ((corrected_tx_power - rssi) / (10 * n))
        elif calibrated_tx_power > 0:
            reference_rssi_1m = -65 
            n = 5.8
            distance_meters = 10 ** ((reference_rssi_1m - rssi) / (10 * n))
        else:
            n = 2.5
            distance_meters = 10 ** ((calibrated_tx_power - rssi) / (10 * n))
            
        r = distance_meters * 100 # Convert to cm for older logic or keep as meters
        # Actually in this version let's keep it as is (the old code used cm)
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

def update_plot(clients, room_counts, room_polygons, ax, bg_img):
    ax.clear()
    
    if bg_img is not None:
        ax.imshow(bg_img, extent=[-5, 15, -5, 15])
    else:
        ax.set_facecolor('#12121c')
        
    # Draw rooms
    for room_name, path in room_polygons.items():
        patch = patches.PathPatch(path, facecolor='cyan', alpha=0.2, lw=2, edgecolor='white')
        ax.add_patch(patch)
        
        # Center of polygon roughly
        cx = sum(p[0] for p in path.vertices) / len(path.vertices)
        cy = sum(p[1] for p in path.vertices) / len(path.vertices)
        
        count = room_counts.get(room_name, 0)
        
        bbox_props = dict(boxstyle="circle,pad=0.5", fc="white", ec="#00d2ff", lw=2, alpha=0.9)
        ax.text(cx, cy, str(count), fontsize=24, color='#ff007f', fontweight='bold', ha='center', va='center', bbox=bbox_props)
        ax.text(cx, cy-1.5, room_name, fontsize=10, color='white', ha='center', va='center')
        
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
      
  # Define some mock room polygons
  ROOM_POLYGONS = {
      'Room A': mpath.Path([(-5, -5), (15, -5), (15, 5), (-5, 5)]),
      'Room B': mpath.Path([(-5, 5), (15, 5), (15, 15), (-5, 15)])
  }

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
        loc = estimate_location_4_devices(data['receivers'])
        if loc:
            active_devices[addr] = {'time': current_time, 'loc': loc}
        
    # Prune old devices
    active_devices = {addr: info for addr, info in active_devices.items() if current_time - info['time'] <= TIME_WINDOW}
    
    room_counts = {room: 0 for room in ROOM_POLYGONS}
    
    for addr, info in active_devices.items():
        lx, ly = info['loc']
        for room_name, path in ROOM_POLYGONS.items():
            if path.contains_point((lx, ly)):
                room_counts[room_name] += 1
                break
    
    print("---------Room Counts-------------")
    for room, count in room_counts.items():
        print(f"{room}: {count} people")
    print("---------------------------------")
    
    update_plot(clients, room_counts, ROOM_POLYGONS, ax, bg_img)

except KeyboardInterrupt:
  print()
