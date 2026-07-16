import numpy as np

def trilateration_n_points(points):
    """
    Calcule la position (x, y) pour n points.
    points : liste de triplets (x_i, y_i, r_i)
    """
    n = len(points)
    if n < 3:
        raise ValueError("Il faut au moins 3 points pour la trilatération en 2D.")
        
    # Extraction du dernier point comme référence (point n)
    xn, yn, rn = points[-1]
    
    A = []
    B = []
    
    # Construction des matrices A et B pour les n-1 premiers points
    for i in range(n - 1):
        xi, yi, ri = points[i]
        
        # Ligne pour la matrice A
        A_row = [2 * (xi - xn), 2 * (yi - yn)]
        A.append(A_row)
        
        # Ligne pour le vecteur B
        B_row = (xi**2 - xn**2) + (yi**2 - yn**2) - (ri**2 - rn**2)
        B.append(B_row)
        
    A = np.array(A)
    B = np.array(B)
    
    # Résolution mathématique : X = (A^T * A)^(-1) * A^T * B
    # En Python, la fonction lstsq gère directement la pseudo-inverse de manière stable
    X, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)
    
    return X[0], X[1]

# --- EXEMPLE D'UTILISATION ---
# Format : (x, y, distance)
donnees_3_points = [(0, 0, 5), (10, 0, 5), (5, 8, 3)]
donnees_4_points = [(0, 400, 45), (400, 400, 35), (0, 0, 55), (400, 0, 50)]
donnees_5_points = [(0, 0, 5), (10, 0, 5), (5, 8, 3), (2, 4, 1.41), (8, 4, 4.24)]

print("Position avec 3 points :", trilateration_n_points(donnees_3_points))
print("Position avec 4 points :", trilateration_n_points(donnees_4_points))
print("Position avec 5 points :", trilateration_n_points(donnees_5_points))
######
# def estimate_location(receivers):
#     # Stop condition : if less than 3 receivers, return None -> trilateration needs 3 points
#     if len(receivers) < 3:
#         return None
    
#     # Extract points as (x, y, r)
#     points = [(r['x'], r['y'], r['r']) for r in receivers]
    
#     n = len(points)
    
#     # Extraction of the last point as reference (point n)
#     xn, yn, rn = points[-1]
    
#     # A is a matrix of size (n-1) x 2
#     A = []
#     # B is a vector of size (n-1) x 1
#     B = []
    
#     # Construction of matrices A and B for the first n-1 points
#     for i in range(n - 1):
#         xi, yi, ri = points[i]
        
#         # Row for matrix A
#         A_row = [2 * (xi - xn), 2 * (yi - yn)]
#         A.append(A_row)
        
#         # Row for vector B
#         B_row = (xi**2 - xn**2) + (yi**2 - yn**2) - (ri**2 - rn**2)
#         B.append(B_row)
        
#     A = np.array(A)
#     B = np.array(B)
    
#     # Mathematical resolution: X = (A^T * A)^(-1) * A^T * B
#     # In Python, the lstsq function directly handles the pseudo-inverse in a stable manner
#     try:
#         X, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)
#         return float(X[0]), float(X[1])
#     except Exception as e:
#         return None

# def parse_received_data(clients):
#     devices_data = {}
#     for c, client_info in clients.items():
#         rcv = client_info.get('rcv', '')
#         if not rcv:
#             continue
#         parts = rcv.split(',')
#         if len(parts) == 0:
#             continue
#         try:
#             rx = float(client_info['x'])
#             ry = float(client_info['y'])
#         except ValueError:
#             continue

#         for part in parts[1:]:
#             if not part.startswith('DEVICE:'):
#                 continue
#             fields = part.split('|')
#             device_info = {}
#             for field in fields:
#                 if ':' in field:
#                     k, v = field.split(':', 1)
#                     device_info[k] = v
#             addr = device_info.get('ADDR')
#             rssi_str = device_info.get('RSSI')
#             if addr and rssi_str:
#                 try:
#                     rssi = float(rssi_str)
#                     r = abs(rssi)
#                     if addr not in devices_data:
#                         devices_data[addr] = {'name': device_info.get('DEVICE', 'Unknown'), 'receivers': []}
#                     devices_data[addr]['receivers'].append({'x': rx, 'y': ry, 'r': r})
#                 except ValueError:
#                     continue
#     return devices_data